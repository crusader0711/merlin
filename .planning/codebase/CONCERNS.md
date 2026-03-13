# Codebase Concerns

**Analysis Date:** 2026-03-13

## Tech Debt

### Multiple Obsolete GUI Versions
- Issue: 7 GUI versions co-exist in repository (GUI_V1.py through GUI_V6.py plus demo variants)
- Files:
  - `9_Firmware/9_3_GUI/GUI_V1.py`
  - `9_Firmware/9_3_GUI/GUI_V2.py`
  - `9_Firmware/9_3_GUI/GUI_V3.py`
  - `9_Firmware/9_3_GUI/GUI_V4.py`
  - `9_Firmware/9_3_GUI/GUI_V4_2_CSV.py`
  - `9_Firmware/9_3_GUI/GUI_V5.py`
  - `9_Firmware/9_3_GUI/GUI_V5_Demo.py`
  - `9_Firmware/9_3_GUI/GUI_V6.py`
  - `9_Firmware/9_3_GUI/GUI_V6_Demo.py`
- Impact:
  - Repository bloat with obsolete code paths
  - Uncertainty about which version is production vs experimental
  - Maintenance burden: any fix must potentially target multiple versions
  - Demo versions suggest incomplete or unstable implementations
- Fix approach:
  - Archive old versions (V1-V5) to separate branch
  - Mark GUI_V6_Demo.py status clearly (stable/experimental/deprecated)
  - Consolidate shared code into common module to reduce duplication

### Hardcoded Magic Numbers and Constants
- Issue: Numerous literal numeric values scattered throughout microcontroller code
- Files: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp`
- Examples from code:
  - `const int m_max = 32; const int n_max = 31;` (chirp parameters)
  - `const float T1 = 30.0f; const float PRI1 = 167.0f;` (timing in microseconds)
  - `const float Guard = 175.4f;` (guard time)
  - `const uint32_t sampleRate = 370;` (Hz)
  - Phase differences array with 31 hardcoded float values
  - IMU calibration biases: `float abias[3] = {-0.108, -0.038, -0.006}`
  - Magnetic declination: `float Mag_Declination = -0.61;`
- Impact:
  - Makes parameter tuning impossible without code recompilation
  - Hardware variations require code changes rather than configuration
  - No runtime flexibility for testing different radar configurations
  - Calibration values embed location-specific data (magnetic declination)
- Fix approach:
  - Extract all magic numbers to `#define` constants with descriptive names
  - Create configuration structure loaded from EEPROM or configuration partition
  - Document derivation/meaning of each constant
  - Implement runtime parameter adjustment via USB commands

### Inadequate Error Handling in Critical Firmware
- Issue: Error_Handler() enters infinite loop without recovery mechanism
- Files: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` (line 2385-2394)
- Code:
  ```cpp
  void Error_Handler(void)
  {
    __disable_irq();
    while (1) { }
  }
  ```
- Impact:
  - System hangs silently on any unrecoverable error
  - No error reporting to host computer
  - No logging of error condition
  - Renders hardware unresponsive without debugger
  - Critical for field deployment reliability
- Fix approach:
  - Implement error code transmission to host via USB before halt
  - Add watchdog timer to force reset if system hangs
  - Log error codes to persistent storage
  - Implement graceful degradation for non-critical failures

### Empty Exception Handlers in Python GUI
- Issue: Generic empty `except` blocks that silently swallow exceptions
- Files: `9_Firmware/9_3_GUI/GUI_V6.py` (multiple locations), `9_Firmware/9_3_GUI/GUI_V5.py`
- Examples:
  - Line 92: `except: pass`
  - Line 367: `except: pass`
  - Line 371: `except: pass`
  - Line 375: `except: pass`
  - Line 421: `except: pass`
  - Line 425: `except: pass`
- Impact:
  - Errors go unreported - UI may appear frozen or unresponsive
  - Difficult to diagnose runtime issues
  - USB disconnects or device failures silently ignored
  - Makes debugging field issues nearly impossible
- Fix approach:
  - Replace all bare `except: pass` with specific exception types
  - Log all exceptions at minimum
  - Provide user feedback for critical failures
  - Implement telemetry collection for errors

## Known Bugs

### Buffer Overflow Risk in USBHandler
- Symptoms: System crash or data corruption if malformed USB packet received
- Files: `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp` (line 64)
- Code:
  ```cpp
  uint32_t bytes_to_copy = (length < (MAX_BUFFER_SIZE - buffer_index)) ?
                           length : (MAX_BUFFER_SIZE - buffer_index);
  memcpy(usb_buffer + buffer_index, data, bytes_to_copy);
  ```
- Trigger: Send USB packet with `length > MAX_BUFFER_SIZE` before buffer is cleared
- Issue: Buffer is truncated silently but index isn't reset when buffer fills, causing data loss or misalignment on next packet
- Workaround: Ensure host only sends packets smaller than MAX_BUFFER_SIZE

### Packet Length Hardcoded to 64 Bytes
- Symptoms: Incorrect data parsing if actual packet size differs
- Files: `9_Firmware/9_3_GUI/GUI_V6.py` (line 600)
- Code:
  ```python
  def get_packet_length(self, packet):
      """Calculate packet length including header and footer"""
      return 64  # Example: 64-byte packets
  ```
- Impact: Function is marked as stub ("Example:") but used in production parsing loop, leading to misalignment
- Trigger: Any deviation from 64-byte packets causes frame synchronization loss
- Workaround: Ensure all packets are exactly 64 bytes

## Security Considerations

### Hardcoded USB Start Flag
- Risk: Any USB device sending bytes [23, 46, 158, 237] can trigger radar startup
- Files: `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp` (line 38)
- Current mitigation: None - no authentication or host verification
- Recommendations:
  - Implement USB device class authentication (vendor/product ID verification)
  - Add timeout-based session management
  - Require multi-step handshake instead of single magic bytes
  - Rate-limit start flag acceptance

### Unencrypted USB Communication
- Risk: Settings and radar data traverse USB without encryption or integrity checking
- Files: `9_Firmware/9_3_GUI/GUI_V6.py`, `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp`
- Current mitigation: Basic CRC available but not consistently used
- Recommendations:
  - Implement USB packet signing with CRC
  - Add checksum verification in parser
  - Consider encryption for calibration/settings data if deployed in secure context

### Missing Input Validation
- Risk: Malformed settings packets could cause undefined behavior in firmware
- Files: `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp` (parseFromUSB function)
- Current mitigation: Checks for "SET" and "END" markers but no range validation
- Recommendations:
  - Validate all numeric parameters against hardware limits
  - Add bounds checking for frequency, power, timing values
  - Implement firmware version negotiation

## Performance Bottlenecks

### Blocking GPIO Toggle in Signal Processing
- Problem: Tight timing loop contains blocking operations
- Files: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` (line 514)
- Impact: GPIO toggle to signal FPGA happens in main control flow, may miss timing windows
- Current timing: No interrupt-driven alternative, relies on synchronous execution
- Improvement path:
  - Move GPIO toggle to DMA or timer interrupt
  - Use hardware SPI with automatic chip select instead of manual GPIO
  - Measure actual timing jitter with oscilloscope

### Inefficient Buffer Shifting in Packet Parser
- Problem: Byte-by-byte buffer shift in parser loop causes O(n) overhead per packet
- Files: `9_Firmware/9_3_GUI/GUI_V6.py` (line 587)
- Code:
  ```python
  if len(buffer) > 4:
      buffer = buffer[1:]  # Inefficient - creates new bytes object
  ```
- Impact: At high data rates (4096+ bytes/read), repeated shifting causes CPU spikes
- Improvement path:
  - Use circular buffer or index pointers instead of slicing
  - Implement hardware frame synchronization to reduce searching
  - Pre-allocate fixed-size buffer

### Python GUI Thread Synchronization
- Problem: Multiple threads compete for UI updates without synchronization
- Files: `9_Firmware/9_3_GUI/GUI_V6.py`
- Current approach: Queues for some data but direct list access for target tracking
- Impact: Potential race conditions in target list updates
- Improvement path:
  - Standardize on queue-based communication between threads
  - Use lock-based protection for shared data structures
  - Add thread safety assertions in debug builds

## Fragile Areas

### IMU Calibration Matrix Hardcoded
- Files: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` (lines 139-142)
- Why fragile:
  - 3x3 calibration matrix is sensor-specific but embedded as literals
  - Any sensor replacement requires code modification and recompilation
  - No mechanism to load per-unit calibration data
  - Biases are location-specific (magnetic declination = -0.61)
- Safe modification:
  - Store calibration in EEPROM with version/serial number
  - Implement factory calibration procedure
  - Add runtime calibration UI in Python GUI
- Test coverage: No test for incorrect calibration values

### USB State Machine Without Timeout
- Files: `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp`
- Why fragile:
  - State machine can get stuck in RECEIVING_SETTINGS indefinitely if partial packet received
  - No timeout to return to WAITING_FOR_START
  - Slow/buggy USB host could hang firmware
- Safe modification:
  - Add timeout counter that resets state after 100ms without data
  - Implement keep-alive/heartbeat messages
  - Add watchdog to force state reset
- Test coverage: No test for disconnected/stalled USB hosts

### Stepper Motor Control via GPIO Without Feedback
- Files: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` (line 195)
- Why fragile:
  - Stepper position calculated by counting pulses but no encoder feedback
  - If stepper misses steps or stalls, antenna position diverges from assumption
  - No stall detection mechanism
- Safe modification:
  - Add optional absolute position sensor (home switch + encoder)
  - Implement stall current monitoring
  - Add periodic homing routine
- Test coverage: No test for lost steps or jamming

## Scaling Limits

### Fixed-Size Target List
- Current capacity: 100 targets max (hard limit in GUI_V5.py line 1401)
- Limit: Very-high-density scenarios (dense urban/traffic) may exceed capacity
- Scaling path:
  - Implement circular buffer with configurable size
  - Add priority/scoring to keep only most-important targets
  - Stream excess targets to disk for post-processing

### USB3 FT601 Bandwidth Underutilized
- Current capacity: 4096-byte read chunks, variable rate
- Limit: FT601 theoretical max ~400 MB/s, actual usage unclear
- Scaling path:
  - Measure actual data rate with profiling
  - Optimize packet format to reduce overhead
  - Consider raw streaming mode if latency-critical

### Single-Threaded Python GUI
- Current architecture: Main thread handles UI + data processing in main loop
- Limit: GUI responsiveness degrades with high data rates
- Scaling path:
  - Move packet parsing to dedicated thread
  - Batch UI updates to fixed interval (50ms)
  - Use multiprocessing for heavy signal processing (FFT, clustering)

## Dependencies at Risk

### Old-style Python Imports with Limited Error Handling
- Risk: pyusb or pyftdi installation missing silently disables functionality
- Files: `9_Firmware/9_3_GUI/GUI_V6.py` (lines 24-39)
- Current mitigation: Warnings logged but no fail-safe
- Migration plan:
  - Add requirements.txt or setup.py with explicit versions
  - Implement fallback implementations for critical USB interfaces
  - Create integration test that fails if USB unavailable

### Hardcoded Reference to AD9523 Control Pins
- Risk: STM32 HAL GPIO configuration could change with next CubeMX regeneration
- Files: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` (lines 247-253)
- Current mitigation: Wrapper functions provide abstraction but underlying pins hardcoded
- Migration plan:
  - Move pin definitions to generated config files
  - Add compile-time checks for pin availability
  - Implement pin validation at startup

## Missing Critical Features

### No System Diagnostics or Self-Test
- Problem: No mechanism to verify hardware health before operation
- Blocks: Cannot ensure radar is operational before deployment
- Missing diagnostics:
  - Frequency synthesizer lock detection
  - DAC/ADC functional test
  - FPGA communication verification
  - Antenna element continuity check
  - Temperature sensor validation

### No Persistent Logging to Device
- Problem: Error logs only exist in RAM, lost on reboot
- Blocks: Cannot diagnose field failures after the fact
- Missing capability:
  - Circular flash log buffer
  - Error event timestamps
  - System restart reason detection

### No Firmware Version Management
- Problem: No way to identify firmware version or detect compatibility
- Blocks: Host GUI cannot verify microcontroller firmware version
- Missing implementation:
  - Version string in firmware
  - Version query command over USB
  - Compatibility check in host software

## Test Coverage Gaps

### No USB Communication Unit Tests
- What's not tested: USBHandler state machine transitions, buffer overflow cases, malformed packet rejection
- Files: `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp`
- Risk: State machine bugs reach field deployment
- Priority: High - affects system reliability and security

### No Radar Signal Processing Integration Tests
- What's not tested: Packet parsing correctness, frame synchronization recovery, handling of corrupted data
- Files: `9_Firmware/9_3_GUI/GUI_V6.py` (packet parser methods)
- Risk: Incorrect target detection or coordinate transforms undetected
- Priority: High - directly impacts mission performance

### No IMU/GPS Integration Tests
- What's not tested: Coordinate transformation correctness, pitch correction math, GPS to terrain fusion
- Files: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` (lines 148-151 orientation calculations)
- Risk: Incorrect target geolocation deployed to field
- Priority: Medium - affects feature quality not core safety

### No USB Stress Testing
- What's not tested: Sustained high-bandwidth operation, rapid connect/disconnect, recovery from USB errors
- Risk: System hangs or crashes under real-world deployment conditions
- Priority: Medium-High - affects availability

---

*Concerns audit: 2026-03-13*
