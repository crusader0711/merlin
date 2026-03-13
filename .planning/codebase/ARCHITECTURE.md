# Architecture

**Analysis Date:** 2026-03-13

## Pattern Overview

**Overall:** Layered Embedded Systems Architecture with Hardware-Software Co-Design

**Key Characteristics:**
- Three-layer system: **Microcontroller (STM32F746) → FPGA (Xilinx XC7A100T) → Python GUI**
- Signal processing pipeline with real-time constraints
- Hardware abstraction layers for device communication
- Modular component managers for RF/beamforming control
- High-speed USB 3.0 interface (FT601) for data streaming

## Layers

**Hardware Abstraction Layer (HAL):**
- Purpose: Encapsulates low-level hardware communication primitives
- Location: `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/`
- Contains: No-OS drivers (GPIO, SPI, I2C, UART, DMA), STM32F7xx HAL bindings
- Depends on: STM32F7xx MCU hardware
- Used by: Device managers, main application

**Device Manager Layer:**
- Purpose: Manages individual RF/beamforming components with higher-level abstractions
- Location: `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/`
- Contains: `ADAR1000_Manager.h/cpp` (4-channel beamformers), `adf4382a_manager.c` (frequency synthesizers), component drivers
- Depends on: HAL layer, specific device datasheets
- Used by: Main firmware, system control logic

**FPGA Signal Processing Layer:**
- Purpose: Performs real-time radar signal processing on XC7A100T
- Location: `9_Firmware/9_2_FPGA/`
- Contains: Verilog modules for waveform generation, ADC interfacing, DDC, pulse compression, Doppler FFT, CFAR detection
- Depends on: System clocks (100MHz, 120MHz, 400MHz ADC), external ADC/DAC interfaces
- Used by: USB data interface, STM32 control signals

**System Control Layer:**
- Purpose: Orchestrates radar operation, peripheral sequencing, sensor integration
- Location: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp`
- Contains: Initialization, event loop, GPS/IMU integration, power sequencing
- Depends on: Device managers, FPGA control signals
- Used by: USB interface, external commands

**Application Layer:**
- Purpose: User interaction and visualization
- Location: `9_Firmware/9_3_GUI/`
- Contains: Python GUI with tkinter, USB communication, map rendering, target tracking
- Depends on: USB interface, PyUSB/PyFTDI drivers
- Used by: End users

## Data Flow

**Transmit Path:**

1. **Waveform Generation** (`plfm_chirp_controller.v`, `radar_transmitter.v`)
   - STM32 sends chirp command to FPGA via control signals (`stm32_new_chirp`)
   - FPGA chirp controller generates LFM chirp envelope (long: 30µs, short: 0.5µs)
   - Chirp lookup tables in memory (`long_chirp_*.mem`, `short_chirp_*.mem`) feed DAC

2. **DAC Output** (`dac_interface_single.v`)
   - 8-bit chirp data output at 120MHz (`clk_120m_dac`)
   - DAC physical output feeds RF up-conversion mixer (LT5552)

3. **Frequency Up-Conversion**
   - Mixer combines IF chirp with TX LO from ADF4382 (Frequency Synthesizer)
   - RF output power amplified via ADTR1107 front-end chips (×16 elements)
   - Beamforming via ADAR1000 phase shifters (4 units, 4 elements each)

**Receive Path:**

1. **RF Reception**
   - 16 antenna elements receive reflected signals
   - Beamforming controlled by ADAR1000 (RX mode)
   - Down-conversion mixer (LT5552) produces IF output

2. **ADC Acquisition** (`ad9484_interface_400m.v`, `lvds_to_cmos_400m.v`)
   - AD9484 14-bit ADC samples at 400MHz
   - LVDS interface converted to CMOS via `lvds_to_cmos_400m.v`
   - Raw I/Q data captured in frame buffers

3. **Signal Processing Pipeline** (`radar_receiver_final.v`)
   - **DDC (Digital Down Converter)** `ddc_400m.v`:
     - Produces baseband I/Q at 400MHz → decimated output
     - Uses NCO for frequency translation

   - **Decimation** `cic_decimator_4x_enhanced.v`:
     - CIC filter for anti-aliasing, rate reduction
     - Output rate: ~100MHz

   - **Matched Filtering** `matched_filter_multi_segment.v`:
     - Pulse compression via reference chirp correlation
     - Produces range profile (range dimension extraction)

   - **Doppler Processing** `doppler_processor.v`, `fft_1024_forward.v`:
     - Forward FFT (1024-point) on pulse train
     - Extracts velocity/Doppler dimension
     - Output: 2D range-Doppler map

   - **CFAR Detection**:
     - Constant False Alarm Rate thresholding
     - Identifies target candidates

4. **USB Data Transfer** (`usb_data_interface.v`)
   - Packed detection results → FT601 USB 3.0 interface
   - 32-bit data path with flow control
   - Handshake signals: `ft601_txe_n` (empty), `ft601_rxf_n` (full)

**State Management:**

- **Beam Position**: Controlled by STM32 via `stm32_new_elevation`, `stm32_new_azimuth` signals
  - FPGA maintains `current_elevation`, `current_azimuth`, `current_chirp` registers
  - STM32 manages stepper motor for mechanical rotation

- **Chirp Sequencing**:
  - m ∈ [1,32] chirps per beam position
  - n ∈ [1,31] elevation positions
  - y ∈ [1,50] azimuth rotations (360° mechanical scan)
  - Guard time between sequences: 175.4µs

- **GPS/IMU Data**: Captured in `main.cpp` globals
  - `current_gps_data`: Latitude, longitude, altitude
  - IMU quaternion (`q[4]`) for pitch/roll corrections
  - Integrated into target coordinate transformation in GUI

## Key Abstractions

**BeamConfig Structure:**
- Purpose: Encapsulates phase/gain settings for a single beam direction
- Location: `ADAR1000_Manager.h`
- Pattern: Configuration struct with validation
- Usage: Sets 4-element phase patterns, dwell time, beam steering angle

**RadarSettings:**
- Purpose: Centralized radar parameter container
- Location: `RadarSettings.h`
- Pattern: Value object parsed from USB commands
- Manages: Chirp durations, PRF, frequency range, detection thresholds

**RadarTarget:**
- Purpose: Single target detection result
- Location: `GUI_V6.py` (dataclass)
- Fields: Range, velocity, azimuth, elevation, SNR, position (GPS-corrected), track ID
- Pattern: Data transfer object between FPGA processing and Python visualization

**Signal Processing Stages:**
Each stage is a separate Verilog module with clear input/output interfaces:
- Input: Clock domain, valid signal, data
- Output: Valid signal, processed data
- Error handling: Underflow/overflow flags

## Entry Points

**STM32 Main Loop:**
- Location: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` (main function after initialization)
- Triggers: Power-up, USB host command, periodic scanning
- Responsibilities:
  - Initialize AD9523 (clock generator), ADF4382 (RX/TX LOs), ADAR1000 (beamformers)
  - Configure STM32 peripherals (SPI, I2C, UART, timers)
  - Enable power rails via GPIO sequencing
  - Process GPS/IMU data
  - Monitor thermal sensors (ADS7830) for fan control
  - Relay USB commands to FPGA

**FPGA Top Module:**
- Location: `9_Firmware/9_2_FPGA/radar_system_top.v` (module `radar_system_top`)
- Triggers: Clock edges, external control signals
- Responsibilities:
  - Instantiate and connect transmitter, receiver, USB interface submodules
  - Manage clock distribution via BUFG primitives
  - Synchronize reset across clock domains (CDC)
  - Expose status outputs for debugging

**Python GUI:**
- Location: `9_Firmware/9_3_GUI/GUI_V6.py` (main() function)
- Triggers: User interaction, USB data arrival, timer events
- Responsibilities:
  - USB device enumeration and connection
  - Real-time plotting of range-Doppler maps
  - Target clustering via DBSCAN
  - Kalman filter tracking
  - Map rendering with GPS integration

## Error Handling

**Strategy:** Defensive design with fallback modes and diagnostic registers

**Patterns:**

**Hardware Communication:**
- I2C/SPI transactions include ACK/NACK verification
- Register reads verified against expected values
- Device initialization checks communication before proceeding
- Timeouts on blocking operations (e.g., `verifyDeviceCommunication()` in `ADAR1000_Manager.h`)

**Signal Integrity:**
- ADC clock loss detection via `adc_dco_p/n` LVDS signals
- DAC underflow protection via latency buffers
- USB flow control: respect `ft601_txe_n` (transmit FIFO empty) and `ft601_rxf_n` (receive FIFO full)

**Firmware:**
- `GUI_V6.py` catches USB communication errors, logs, and offers device re-enumeration
- Missing target detections logged but don't halt operation
- Python exception handlers in threading loops prevent GUI crashes

**Typical Failure Modes:**
- Clock synchronization failure → System halt (reset required)
- ADC dropout → Range profile set to zeros, operation continues with reduced data
- USB disconnection → GUI offers reconnect dialog
- Temperature sensor read failure → Fan control defaults to "always on"

## Cross-Cutting Concerns

**Logging:**
- Approach: Printf-style via `no_os_print_log.h` on STM32, Python `logging` module in GUI
- STM32: Via UART/USB CDC (routed to terminal)
- Python: File and console logging with timestamp

**Validation:**
- Input validation: All USB commands parsed by `RadarSettings.parseFromUSB()` with bounds checking
- Chirp parameters (`T1`, `T2`, `PRI1`, `PRI2`) compile-time constants in `main.cpp`
- GUI radar target clustering uses DBSCAN with epsilon/min_samples validation

**Authentication:**
- Not implemented (closed system, USB requires physical access)
- No security-critical operations exposed

**Power Sequencing:**
- GPIO-controlled via `main.cpp` globals:
  - `EN_P_5V0_PA1`, `EN_P_5V0_PA2` (Power Amplifier supply)
  - `EN_P_1V0_FPGA`, `EN_P_1V8_FPGA`, `EN_P_3V3_FPGA` (FPGA rails)
  - `EN_P_5V0_ADAR` (Beamformer supply)
  - `EN_P_3V3_ADTR` (Front-end supply)
  - `EN_P_3V3_SW` (RF switch supply)
- Sequencing order enforced by delays and startup routines
- Cooling fans controlled via DAC voltage output to thermal load resistors

---

*Architecture analysis: 2026-03-13*
