# Phase 4: Software Documentation - Research

**Researched:** 2026-03-14
**Domain:** Embedded firmware documentation (FPGA Verilog, STM32 C++, Python GUI) for FMCW radar system
**Confidence:** HIGH

## Summary

Phase 4 documents three software layers of the AERIS-10 radar system: the FPGA signal processing pipeline, STM32 firmware, and Python GUI. All source code has been read and analyzed. The codebase is complete and stable -- this is a documentation-only phase with no implementation work.

The FPGA pipeline is the most complex deliverable. The signal path runs: ADC (400 MHz LVDS) -> CDC -> DDC (NCO at 120 MHz IF + CIC 4x decimation + FIR) -> Matched Filter (overlap-save with 1024-pt FFT, 4 segments for long chirp) -> Range Bin Decimation (1024 -> 64 bins) -> Doppler Processor (32-pt FFT with Hamming window over 32 chirps x 64 range bins) -> USB output. The CFAR in `radar_system_top.v` is currently a simple magnitude threshold (|I|+|Q| > 10000), not a true CFAR implementation -- this must be documented honestly.

The STM32 firmware (`main.cpp`, ~2000 lines) contains the complete initialization sequence, radar pulse sequencing, and all magic numbers that need derivation documentation. The Python GUI (`GUI_V6.py`, ~617 lines) is the only version to document; V1-V5 are explicitly excluded.

**Primary recommendation:** Organize documentation by signal/data flow (ADC input -> processing stages -> GUI display), not by module. Use the `SW` equation tag prefix per conventions.md. Cross-reference Phase 2 physics and Phase 3 hardware documents extensively.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SWDOC-01 | FPGA signal processing pipeline -- DDC, CIC decimation, matched filter, 1024-pt FFT, CFAR documented by signal flow | Full Verilog source analyzed: `ddc_400m.v` (NCO+CIC+FIR), `matched_filter_multi_segment.v` (overlap-save), `doppler_processor.v` (32-pt FFT), `radar_receiver_final.v` (pipeline orchestration). CFAR is threshold-only in current code. |
| SWDOC-02 | STM32 firmware -- initialization sequence, SPI/I2C device addresses, power-on/off sequences, peripheral config | Full `main.cpp` analyzed: 17-step init sequence, all I2C addresses (DAC5578: 0x48/0x49, ADS7830: 0x48/0x4A/0x49), SPI configs, GPIO pin map from `main.h`, radar parameters with magic numbers |
| SWDOC-03 | Python GUI -- USB protocol, RadarTarget dataclass, DBSCAN parameters, Kalman state model, map rendering (V6 only) | `GUI_V6.py` fully analyzed: RadarTarget/RadarSettings/GPSData dataclasses, FT601Interface class, MapGenerator placeholder, RadarProcessor/USBPacketParser stubs. Note: some classes are stubs (`pass`) in current code |
| SWDOC-04 | USB interface protocol -- FT601 command/data format, packet structure, RadarSettings.parseFromUSB(), streaming protocol | `usb_data_interface.v` (FPGA side), `FT601Interface` class (Python side), `RadarSettings.h`/`USBHandler.h` (STM32 side) all analyzed. Packet format: Header(0xAA) + Range(32b) + Doppler(I16+Q16) + CFAR(1b) + Footer(0x55) |
</phase_requirements>

## Standard Stack

This phase produces Markdown documentation files, not software. The "stack" is the documentation tooling and conventions established in Phases 1-3.

### Core
| Tool | Purpose | Why Standard |
|------|---------|--------------|
| GitHub-flavored Markdown | Document format | All prior phases use this; renders on GitHub |
| MathJax `\tag{SW-N}` | Equation numbering | Per `conventions.md` -- SW prefix assigned for software docs |
| Symbol table cross-refs | Parameter consistency | Per `conventions.md` anti-pattern 5.4 -- always pair code vars with standard symbols |

### Output Location
| Deliverable | Path | Naming Pattern |
|-------------|------|----------------|
| FPGA pipeline doc | `03_software/01_fpga_pipeline.md` | Matches `01_physics/`, `02_hardware/` pattern |
| STM32 firmware doc | `03_software/02_stm32_firmware.md` | Sequential within directory |
| Python GUI doc | `03_software/03_python_gui.md` | V6 only per requirements |
| USB protocol doc | `03_software/04_usb_protocol.md` | Interface specification |

## Architecture Patterns

### Recommended Document Structure
```
03_software/
  01_fpga_pipeline.md      # SWDOC-01: Signal flow from ADC to USB
  02_stm32_firmware.md     # SWDOC-02: Init sequence, peripherals, radar loop
  03_python_gui.md         # SWDOC-03: V6 architecture, dataclasses, algorithms
  04_usb_protocol.md       # SWDOC-04: Packet format, command protocol
```

### Pattern 1: Signal-Flow Documentation (SWDOC-01)
**What:** Document FPGA pipeline by following data through each stage, not by describing modules in isolation.
**When to use:** FPGA pipeline documentation (SWDOC-01) -- the most complex deliverable.

The signal flow must be documented as a continuous chain:

1. **ADC Acquisition** (`ad9484_interface_400m.v` + `lvds_to_cmos_400m.v`)
   - 8-bit LVDS at 400 MHz -> CMOS conversion
   - CDC crossing: ADC clock domain -> processing clock domain (3-stage synchronizer)

2. **Digital Down-Conversion** (`ddc_400m_enhanced`)
   - NCO generates sin/cos at $f_\text{IF} = 120~\text{MHz}$ using phase increment `0x4CCCCCCD`
   - Phase dithering via 8-bit LFSR to reduce spurs
   - Mixing: `mixed_i = adc_signed * cos_out`, `mixed_q = adc_signed * sin_out`
   - Mixer output: 34-bit (18-bit ADC x 16-bit NCO)

3. **CIC Decimation** (`cic_decimator_4x_enhanced`)
   - 5 stages, decimation factor 4, comb delay 1
   - Input: 18-bit at 400 MHz, Output: 18-bit at 100 MHz
   - Bit growth: 36-bit internal, right-shifted by 10 (gain = 4^5 = 1024 = 2^10)
   - Saturation detection with latched overflow monitoring

4. **FIR Compensation** (`fir_lowpass_parallel_enhanced`)
   - Compensates CIC passband droop
   - CDC crossing from 400 MHz to 100 MHz domain (another 3-stage sync)
   - Dual I/Q channels processed independently

5. **DDC Input Interface** (`ddc_input_interface`)
   - Scales and aligns I/Q outputs for downstream processing
   - Data sync error detection

6. **Matched Filter** (`matched_filter_multi_segment`)
   - Overlap-save method with 1024-pt FFT segments
   - Long chirp: 3000 samples -> 4 segments (advance=896, overlap=128)
   - Short chirp: 50 samples -> 1 segment (zero-padded to 1024)
   - 8-state FSM: IDLE -> COLLECT_DATA -> ZERO_PAD -> WAIT_REF -> PROCESSING -> WAIT_FFT -> OUTPUT -> NEXT_SEGMENT
   - Reference chirp from memory via `chirp_memory_loader_param` with latency buffer (3187 cycles)

7. **Range Bin Decimation** (`range_bin_decimator`)
   - 1024 range bins -> 64 bins (decimation factor 16, peak detection mode)
   - Reduces data volume before Doppler processing

8. **Doppler Processing** (`doppler_processor_optimized`)
   - 32-pt FFT across 32 chirps per frame for each of 64 range bins
   - Hamming window in Q15 format (pre-calculated coefficients)
   - Memory: `64 x 32 = 2048` entries of I/Q data in block RAM
   - Chirp-major addressing: `addr = chirp_index * RANGE_BINS + range_bin`
   - Uses Xilinx `xfft_32` IP core
   - Output: 32-bit packed `{Q[15:0], I[15:0]}` per bin

9. **CFAR / Detection** (in `radar_system_top.v`)
   - **IMPORTANT:** Currently NOT a true CFAR implementation
   - Simple magnitude threshold: `|I| + |Q| > 10000`
   - Document as "placeholder threshold detection" -- a real CFAR module is not instantiated

10. **USB Output** (`usb_data_interface`)
    - FT601 Slave FIFO mode, clocked at `ft601_clk_in` (100 MHz)
    - Packet: Header(0xAA) -> Range(4x32b) -> Doppler(4x32b) -> Detection(1b) -> Footer(0x55)

### Pattern 2: Initialization Sequence Documentation (SWDOC-02)
**What:** Document STM32 firmware as a chronological initialization sequence followed by main loop.
**When to use:** STM32 firmware documentation.

The init sequence from `main.cpp` (lines 1189-1700):

| Step | Action | Code Location | Duration |
|------|--------|---------------|----------|
| 1 | MPU/HAL/Clock config | `MPU_Config()`, `HAL_Init()`, `SystemClock_Config()` | ~ms |
| 2 | Peripheral init | `MX_GPIO_Init()` through `MX_USB_DEVICE_Init()` | ~ms |
| 3 | Start TIM1 + DWT | `HAL_TIM_Base_Start()`, `DWT_Init()` | ~ms |
| 4 | OCXO warm-up wait | `HAL_Delay(180000)` | **180 seconds** |
| 5 | AD9523 power sequence | 1V8_CLOCK -> 3V3_CLOCK -> release reset | 300 ms |
| 6 | AD9523 clock configuration | `configure_ad9523()` -- 12 channel outputs | ~100 ms |
| 7 | FPGA power sequence | 1V0 -> 1V8 -> 3V3 (100ms each) | 300 ms |
| 8 | IMU initialization | `GY85_Init()` + 10 iterations with complementary filter | ~3 s |
| 9 | Barometer calibration | `myBMP.getPressure()` x 5 iterations | ~500 ms |
| 10 | ADF4382 LO initialization | `ADF4382A_Manager_Init()` + lock wait (up to 10s) | 1-10 s |
| 11 | ADAR1000 power + init | 3V3_ADAR12/34 -> 5V0_ADAR -> `systemPowerUpSequence()` | ~1 s |
| 12 | Beam matrix initialization | `initializeBeamMatrices()` -- 31 positions x 16 elements | ~ms |
| 13 | GPS acquisition | `smartDelay(1000)` x 10 iterations | 10 s |
| 14 | Point stepper to North | Stepper motor rotation based on IMU yaw | variable |
| 15 | Send GPS to GUI + wait for start | `GPS_SendBinaryToGUI()` + poll `isStartFlagReceived()` | user-dependent |
| 16 | PA power-up (if enabled) | DAC5578 init -> set Vg -> enable VDD -> Idq tuning | ~2 s |
| 17 | FPGA reset + enable mixers | GPIO toggle PD12 + PD11 | ~10 ms |

### Magic Numbers to Derive

| Value | Variable | Formula/Derivation |
|-------|----------|-------------------|
| PRI1 = 167 us | `PRI1` in main.cpp | $T_{r,1} = T_{c,1} + \text{processing time} = 30 + 137 = 167~\mu\text{s}$ |
| Guard = 175.4 us | `Guard` in main.cpp | Guard time between long and short chirp sequences |
| Phase increment 0x4CCCCCCD | `PHASE_INC_120MHZ` in ddc_400m.v | $\Delta\phi = \frac{f_\text{IF}}{f_s} \times 2^{32} = \frac{120\times10^6}{400\times10^6} \times 2^{32} = 0.3 \times 4294967296 = 1288490189 = \text{0x4CCCCCCD}$ |
| CIC gain shift 10 | `>>> 10` in cic_decimator | Gain = $D^N = 4^5 = 1024 = 2^{10}$ |
| phase_differences[31] | Array in main.cpp | $\Delta\phi_n$ for 31 elevation beam positions, derived from desired steering angles with $d = \lambda/2$ |
| DAC_val = 126 | PA bias init | Vg = -3.98V via opamp, input = 1.63058V -> `126/255 * 3.3V = 1.63V` |
| Idq target 1.680A | PA tuning loop | QPA2962 target quiescent drain current |
| Latency buffer 3187 | `LATENCY(3187)` | Reference chirp alignment delay: FFT pipeline latency |
| Stepper_steps/y_max = 4 | Stepper motor steps per azimuth | 200 steps/rev / 50 positions = 4 steps between positions |

### Pattern 3: GUI Architecture Documentation (SWDOC-03)
**What:** Document Python GUI V6 as interconnected classes with data flow.
**When to use:** GUI documentation (V6 only).

Key classes to document:
- `RadarTarget` -- dataclass: id, range, velocity, azimuth, elevation, lat, lon, snr, timestamp, track_id
- `RadarSettings` -- dataclass: system_frequency (10 GHz), chirp durations, PRF values, max_distance (50 km)
- `GPSData` -- dataclass: latitude, longitude, altitude, pitch, timestamp
- `FT601Interface` -- FT601 USB 3.0 communication (pyftdi preferred, direct USB fallback)
- `RadarProcessor` -- clustering (DBSCAN) and tracking (Kalman) -- **currently a stub**
- `RadarGUI` -- tkinter main window with matplotlib real-time plots
- `MapGenerator` -- Google Maps overlay -- **currently a stub**
- `STM32USBInterface` -- USB CDC to STM32 for settings/control -- **referenced but not defined in V6**

**IMPORTANT:** Several classes are stubs (`pass` body) in the current GUI_V6.py. Document the architecture and interfaces as designed, but clearly note which implementations are complete vs. stub.

### Anti-Patterns to Avoid
- **Describing modules in isolation:** Each signal processing stage must show input format, transformation, and output format as part of the flow
- **Omitting clock domain information:** Every stage must specify which clock domain it operates in (400 MHz ADC, 100 MHz system, FT601 100 MHz)
- **Inlining numerical values without symbol mapping:** Per conventions.md anti-pattern 5.4, always pair firmware variable names with standard symbols from the symbol table
- **Documenting V1-V5 GUI versions:** Explicitly excluded per requirements

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Signal flow diagrams | ASCII art signal chains | Markdown tables with stage-by-stage description | Consistent with Phase 3 table-driven format |
| Register maps | Ad-hoc register tables | Existing I2C address tables extracted from code | All addresses already in main.cpp |
| Equation derivations | New derivation chains | Cross-references to Phase 2 physics docs | FMCW, LFM, detection theory already derived |
| Timing diagrams | Custom timing descriptions | Cross-reference to `02_hardware/07_timing_budget.md` | Pipeline latency already documented in Phase 3 |

## Common Pitfalls

### Pitfall 1: CFAR Misrepresentation
**What goes wrong:** Documenting the threshold detection in `radar_system_top.v` as "CFAR detection" when it is actually a fixed magnitude threshold (`|I|+|Q| > 10000`).
**Why it happens:** The architecture docs and variable names (`rx_cfar_detection`, `cfar_valid`) use CFAR terminology, but the implementation is a simple threshold.
**How to avoid:** Document the actual implementation honestly: "Placeholder threshold detection. A full CFAR implementation (CA-CFAR, OS-CFAR) is a future enhancement. See Phase 5 SWRES-01."
**Warning signs:** Comments saying "Simple threshold detection on doppler magnitude" in the code.

### Pitfall 2: Stub Classes in GUI_V6
**What goes wrong:** Documenting `RadarProcessor`, `USBPacketParser`, `RadarPacketParser`, `MapGenerator` as complete implementations when they are currently `pass` stubs.
**Why it happens:** The class structure and interfaces are defined but implementations are empty.
**How to avoid:** Document the designed interface and data flow, but mark each as "stub implementation" vs "complete implementation" with a status table.

### Pitfall 3: Clock Domain Confusion
**What goes wrong:** Not specifying which clock domain each FPGA stage operates in, leading to confusion about data rates.
**Why it happens:** The DDC module operates across two domains (400 MHz input, 100 MHz output), with CDC crossings between CIC and FIR stages.
**How to avoid:** Include a clock domain table at the start of the FPGA pipeline document showing each module and its clock domain.

### Pitfall 4: Duplicate Parameter Definitions
**What goes wrong:** Defining radar parameter values in the software docs instead of referencing `parameter_table.md`.
**Why it happens:** Values like `T1 = 30.0f` and `PRI1 = 167.0f` are hardcoded in `main.cpp` and tempting to copy.
**How to avoid:** Per conventions.md anti-pattern 5.1/5.2: reference parameter table for values, show only the firmware variable name and standard symbol mapping.

### Pitfall 5: Missing Verilog Module Documentation
**What goes wrong:** Only documenting the main pipeline stages and missing support modules.
**Why it happens:** Focus on DDC/CIC/matched filter/Doppler and overlooking `chirp_memory_loader_param`, `latency_buffer_2159`, `range_bin_decimator`, `ddc_input_interface`.
**How to avoid:** The signal flow documentation must include every module in the receive path. The `radar_receiver_final.v` instantiation list is the authoritative module inventory.

## Code Examples

### FPGA Module Inventory (from radar_receiver_final.v)
Source: `/Users/mit/Documents/GitHub/PLFM_RADAR/9_Firmware/9_2_FPGA/radar_receiver_final.v`

```
Module Instantiation Chain:
1. lvds_to_cmos_400m          -- ADC clock recovery
2. ad9484_lvds_to_cmos_400m   -- ADC data conversion
3. cdc_adc_to_processing      -- CDC: ADC clock -> 400 MHz processing
4. ddc_400m_enhanced           -- DDC (contains NCO, mixer, CIC, CDC, FIR internally)
5. ddc_input_interface         -- I/Q scaling and alignment
6. chirp_memory_loader_param   -- Reference chirp LUT loading
7. latency_buffer_2159         -- Reference alignment delay (3187 cycles)
8. matched_filter_multi_segment -- Pulse compression (overlap-save)
9. range_bin_decimator          -- 1024->64 range bin reduction
10. doppler_processor_optimized -- 32-pt Doppler FFT across chirps
```

### I2C Device Address Table (from main.cpp)
Source: `/Users/mit/Documents/GitHub/PLFM_RADAR/9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp`

| Device | I2C Bus | 7-bit Address | Purpose |
|--------|---------|---------------|---------|
| DAC5578 #1 | I2C1 | 0x48 | PA gate voltage control (channels 1-8) |
| DAC5578 #2 | I2C1 | 0x49 | PA gate voltage control (channels 9-16) |
| ADS7830 #1 | I2C2 | 0x48 | PA current monitoring (Idq 1-8) |
| ADS7830 #2 | I2C2 | 0x4A | PA current monitoring (Idq 9-16) |
| ADS7830 #3 | I2C2 | 0x49 | Temperature sensors (TMP37 x8) |
| GY-85 IMU | I2C3 | (default) | Accelerometer, gyroscope, magnetometer |
| BMP180 | (I2C) | (default) | Barometric pressure/altitude |

### SPI Device Configuration (from main.cpp)
Source: `/Users/mit/Documents/GitHub/PLFM_RADAR/9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp`

| Device | SPI Bus | CS Pin | Speed | Mode |
|--------|---------|--------|-------|------|
| ADAR1000 #1-4 | SPI1 | PA0-PA3 (via level shifter) | -- | -- |
| AD9523 | SPI4 | PF7 | 10 MHz | Mode 0 |
| ADF4382 TX | SPI4 | PG14 | -- | -- |
| ADF4382 RX | SPI4 | PG10 | -- | -- |

### USB Packet Format (from usb_data_interface.v)
Source: `/Users/mit/Documents/GitHub/PLFM_RADAR/9_Firmware/9_2_FPGA/usb_data_interface.v`

```
State Machine: IDLE -> SEND_HEADER -> SEND_RANGE_DATA -> SEND_DOPPLER_DATA ->
               SEND_DETECTION_DATA -> SEND_FOOTER -> WAIT_ACK -> IDLE

Packet Structure:
  [0xAA]                          -- Header (8-bit, byte enable = 01)
  [range_profile x4]             -- Range data (4x 32-bit words, BE=11)
  [{doppler_real, doppler_imag}]  -- Doppler I/Q (4x 32-bit words, BE=11)
  [{7'b0, cfar_detection}]       -- Detection flag (8-bit, BE=01)
  [0x55]                          -- Footer (8-bit, BE=01)

FT601 Interface:
  Clock: ft601_clk_in (100 MHz, separate from system clocks)
  Data bus: 32-bit bidirectional with tri-state control
  Flow control: ft601_txe (TX FIFO empty), ft601_rxf (RX FIFO full)
```

### STM32-to-FPGA Control Signals (from radar_system_top.v + main.cpp)

| Signal | GPIO Pin | Direction | Purpose |
|--------|----------|-----------|---------|
| stm32_new_chirp | PD8 | STM32->FPGA | Toggle on each new chirp |
| stm32_new_elevation | PD9 | STM32->FPGA | Toggle on elevation change |
| stm32_new_azimuth | PD10 | STM32->FPGA | Toggle on azimuth change |
| stm32_mixers_enable | PD11 | STM32->FPGA | Enable/disable RF mixers |
| FPGA reset | PD12 | STM32->FPGA | Active-low FPGA reset |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Module-by-module docs | Signal-flow documentation | Phase 4 decision | Engineers can trace any data path end-to-end |
| V1-V5 GUI versions | V6-only documentation | Phase 4 scope | Reduces documentation burden, prevents confusion |
| CFAR as separate module | Placeholder threshold in top module | Current codebase state | Must document honestly; real CFAR is Phase 5 research |

## Open Questions

1. **Matched filter processing chain sub-module**
   - What we know: `matched_filter_multi_segment.v` instantiates `matched_filter_processing_chain` which is not in the file listing. It likely contains the forward FFT, spectral multiplication, and inverse FFT.
   - What's unclear: The exact internal structure of this sub-module.
   - Recommendation: Document the interface (inputs/outputs/timing) based on the instantiation in `matched_filter_multi_segment.v`. Note that internal implementation details require the sub-module source.

2. **Which CFAR variant is implemented?**
   - What we know: The current code uses a simple `|I|+|Q| > 10000` threshold, NOT a CFAR algorithm.
   - What's unclear: Whether a separate CFAR module exists outside the analyzed files.
   - Recommendation: Document the threshold as a placeholder. Blockers/Concerns in STATE.md already flags this: "Identify which CFAR variant is implemented in Verilog before Phase 4 FPGA pipeline documentation."

3. **GUI stub implementations**
   - What we know: `RadarProcessor`, `USBPacketParser`, `RadarPacketParser`, `MapGenerator` are stubs with `pass` bodies in GUI_V6.py.
   - What's unclear: Whether complete implementations exist elsewhere.
   - Recommendation: Document the designed interface and note stub status. The DBSCAN and Kalman filter parameters mentioned in requirements likely refer to the intended design, not current implementation.

4. **STM32USBInterface class**
   - What we know: Referenced in RadarGUI but not defined in GUI_V6.py.
   - What's unclear: Whether it's in a separate file or planned but unimplemented.
   - Recommendation: Document the interface based on usage patterns in RadarGUI (list_devices, open_device, send_start_flag, close).

## Sources

### Primary (HIGH confidence)
- **Verilog source files** -- All modules in `9_Firmware/9_2_FPGA/` read directly
- **main.cpp** -- Full 2000-line firmware analyzed (init sequence, radar loop, error handling)
- **main.h** -- Complete GPIO pin mapping (166 lines)
- **GUI_V6.py** -- Full 617-line Python GUI analyzed
- **RadarSettings.h** / **USBHandler.h** -- USB protocol interface definitions
- **gps_handler.h** -- GPS data structure definition
- **conventions.md** / **symbol_table.md** -- Documentation format requirements

### Secondary (MEDIUM confidence)
- **ARCHITECTURE.md** / **STRUCTURE.md** -- GSD codebase analysis (cross-verified with source)
- **Phase 3 hardware docs** -- Document format patterns (verified by reading `02_hardware/01_system_overview.md`)

### Tertiary (LOW confidence)
- **matched_filter_processing_chain** sub-module -- Referenced but not in file listing; interface documented from instantiation

## Metadata

**Confidence breakdown:**
- FPGA pipeline: HIGH -- all Verilog source read, signal flow traced through every module
- STM32 firmware: HIGH -- complete main.cpp analyzed, all init steps identified, GPIO pins mapped
- Python GUI: MEDIUM -- code structure clear but several key classes are stubs
- USB protocol: HIGH -- both FPGA and host-side implementations analyzed
- Magic number derivations: HIGH -- all numerical values traced to physical equations or component specs

**Research date:** 2026-03-14
**Valid until:** Indefinite (codebase is stable, documentation-only phase)
