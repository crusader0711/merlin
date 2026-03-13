# Codebase Structure

**Analysis Date:** 2026-03-13

## Directory Layout

```
PLFM_RADAR/
├── 1_Project_Description/           # Project overview and requirements
├── 2_Functional Diagram & Interconnection Matrices/  # System block diagrams
├── 3_Power Management/               # Power sequencing documentation
├── 4_Schematics and Boards Layout/   # PCB schematics, Gerber files
│   ├── 4_4_Board Stack-up/
│   ├── 4_6_Schematics/
│   └── 4_7_Production Files/         # BOM, assembly guides
├── 5_Simulations/                    # RF/Antenna simulation projects
│   ├── Antenna/                      # EM simulations (OpenEMS)
│   ├── DAC_ReconstructionFilter/
│   ├── Fencing/
│   ├── IF_BPF/
│   ├── Stub_BPF/
│   └── sim_wg_alumina_*/
├── 6_Application Notes/              # Design reference documents
├── 7_Components Datasheets and Application notes/  # IC documentation
│   ├── AD9484/
│   ├── ADF4382A/
│   └── QPA2962/
├── 8_Utils/                          # Utilities and signal processing
│   └── Python/                       # Python analysis scripts
│       ├── CSV_radar.py              # Radar data processing
│       ├── RADAR_eq.py               # Radar equations
│       ├── patch_antenna.py          # Antenna calculations
│       ├── LUT.py                    # Lookup table generation
│       └── test_radar_data.csv       # Sample output data
├── 9_Firmware/                       # Embedded and FPGA firmware
│   ├── 9_1_Microcontroller/          # STM32F746 firmware
│   │   ├── 9_1_1_C_Cpp_Libraries/    # Device drivers and HAL
│   │   ├── 9_1_2_C_Cpp_Algorithms/   # Algorithm specifications
│   │   └── 9_1_3_C_Cpp_Code/         # Application code
│   ├── 9_2_FPGA/                     # Xilinx XC7A100T Verilog
│   │   ├── radar_system_top.v        # Top-level module
│   │   ├── radar_transmitter.v       # TX path
│   │   ├── radar_receiver_final.v    # RX path
│   │   ├── plfm_chirp_controller.v   # Chirp sequencing
│   │   ├── ddc_400m.v                # Digital down-converter
│   │   ├── matched_filter_multi_segment.v  # Pulse compression
│   │   ├── doppler_processor.v       # Doppler FFT
│   │   ├── usb_data_interface.v      # FT601 USB 3.0
│   │   ├── *_*.mem                   # Chirp memory initialization files
│   │   ├── cdc_modules.v             # Clock domain crossing
│   │   ├── cntrt.xdc                 # Vivado constraints
│   │   └── radar_system_tb.v         # Testbench
│   └── 9_3_GUI/                      # Python GUI application
│       ├── GUI_V6.py                 # Latest GUI (production)
│       ├── GUI_V5.py                 # Previous version
│       ├── GUI_V6_Demo.py            # Demo mode
│       ├── test_radar_data.csv       # Test data for demo
│       └── GUI_versions.txt          # Version history
├── .planning/codebase/               # GSD planning documents
├── README.md                         # Project overview
└── [image files]                     # System photos, diagrams
```

## Directory Purposes

**9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries:**
- Purpose: Embedded device drivers and hardware abstraction
- Contains: No-OS framework, STM32 HAL wrappers, component drivers
- Key files:
  - `stm32f7xx_hal.h`: STM32F746xx HAL header
  - `no_os_*.c/h`: No-OS Linux framework (generic drivers)
  - `stm32_*.c/h`: STM32-specific implementations (GPIO, SPI, I2C, UART, DMA, PWM, timer)
  - `ADAR1000_Manager.h/cpp`: Beamformer control (4 × ADAR1000 phase shifters)
  - `adf4382a_manager.c/h`: Frequency synthesizer control
  - `ADS7830.c/h`: ADC driver for temperature/current sensing
  - `DAC5578.h`: DAC driver for power amp gate voltage control
  - `BMP180.h/cpp`: Barometer driver
  - `GY_85_HAL.h/c`: IMU (accelerometer, gyroscope, magnetometer) driver
  - `TinyGPSPlus.h/cpp`: GPS parsing library
  - `gps_handler.h`: GPS data structure
  - `USBHandler.h/cpp`: USB CDC interface handling
  - `iio*.c/h`: IIO (Industrial I/O) interface framework
  - `platform_noos_stm32.h/c`: STM32 platform abstraction for no-OS

**9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code:**
- Purpose: Main STM32 application firmware
- Contains: Initialization, event loop, system orchestration
- Key files:
  - `main.cpp`: Main application entry point (~2000+ lines)
    - Peripheral initialization (SPI, I2C, UART, timers)
    - GPS/IMU data acquisition
    - Component manager instances
    - Radar sequencing control
    - Power management GPIO toggling
  - `main.h`: GPIO pin definitions for all hardware interfaces

**9_Firmware/9_2_FPGA:**
- Purpose: FPGA RTL for real-time signal processing
- Contains: Verilog modules, memory initialization files, simulation
- Key files by function:
  - **System Top-Level:**
    - `radar_system_top.v` (436 lines): Top module, instantiates TX/RX/USB submodules, clock distribution
  - **Transmitter:**
    - `radar_transmitter.v`: TX control sequencing
    - `plfm_chirp_controller.v` (800 lines): Chirp memory sequencing, LFM envelope generation
    - `dac_interface_single.v`: DAC output interface (8-bit @ 120MHz)
  - **Receiver:**
    - `radar_receiver_final.v` (352 lines): RX pipeline orchestration
    - `ad9484_interface_400m.v`: ADC LVDS interface (14-bit @ 400MHz)
    - `lvds_to_cmos_400m.v`: Level conversion
    - `ddc_400m.v` (425 lines): Digital down-converter (NCO + mixer)
    - `cic_decimator_4x_enhanced.v` (299 lines): Rate reduction (400MHz → ~100MHz)
    - `matched_filter_multi_segment.v` (409 lines): Pulse compression via stored reference
    - `doppler_processor.v` (304 lines): Doppler FFT (1024-point forward transform)
    - `fft_1024_forward.v` (123 lines): FFT core module
  - **Detection/Output:**
    - `usb_data_interface.v` (183 lines): FT601 USB 3.0 handshaking, data packing
  - **Support Modules:**
    - `cdc_modules.v` (236 lines): Clock domain crossing for synchronization
    - `edge_detector.v`: Event detection
    - `level_shifter_interface.v`: 3V3↔1V8 level shifting for ADAR1000 SPI
  - **Memory Files:**
    - `long_chirp_seg0_i.mem`, `long_chirp_seg0_q.mem`: Long chirp (30µs) reference I/Q
    - `short_chirp_i.mem`, `short_chirp_q.mem`: Short chirp (0.5µs) reference I/Q
    - 3 segments for long chirp handle frequency sweep coverage
  - **Simulation:**
    - `radar_system_tb.v` (559 lines): Testbench with stimulus generation
  - **Constraints:**
    - `cntrt.xdc`: Vivado timing/physical constraints

**9_Firmware/9_3_GUI:**
- Purpose: User-facing Python GUI for radar control and visualization
- Contains: Tkinter-based interface, signal processing, USB communication
- Key files:
  - `GUI_V6.py` (~1000+ lines): Production GUI
    - `RadarTarget`: Dataclass for detections (range, velocity, azimuth, elevation, GPS coordinates, SNR, track ID)
    - `RadarSettings`: Dataclass for system parameters
    - `GPSData`: GPS-derived location/altitude
    - `FT601Interface`: PyFTDI USB 3.0 device enumeration and communication
    - `RadarProcessor`: Signal processing (clustering, tracking)
    - `RadarGUI`: Main tkinter application with real-time matplotlib plots
    - Features: Range-Doppler map, target tracking, map generation with GPS overlay, DBSCAN clustering, Kalman filtering
  - `GUI_V5.py`: Previous stable version
  - `GUI_V6_Demo.py`: Demo mode (file-based data)
  - `test_radar_data.csv`: Sample radar output for testing

**8_Utils/Python:**
- Purpose: Signal processing and analysis utilities
- Contains: Radar equation calculator, antenna analysis, waveform generation
- Key files:
  - `RADAR_eq.py`: Radar range/SNR equations
  - `CSV_radar.py`: Radar data processing from CSV
  - `patch_antenna.py`: Patch antenna gain/pattern calculations
  - `LUT.py`: Lookup table generation for FPGA chirp memory
  - `FFT_Ramp_Frequency.py`: FFT analysis of frequency-modulated signals
  - `Gen_Triangular.py`: Triangular waveform generation

## Key File Locations

**Entry Points:**

- `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp`: STM32 firmware entry point
  - Initializes all peripherals
  - Starts main event loop
  - Handles USB commands and sensor data

- `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.h`: Hardware pin definitions
  - GPIO mapping for all RF/control signals
  - Clock/power rail enables
  - ADAR1000 control signals

- `9_Firmware/9_2_FPGA/radar_system_top.v`: FPGA top module entry point
  - Connects all signal processing pipelines
  - Manages clock distribution

- `9_Firmware/9_3_GUI/GUI_V6.py`: Python GUI entry point
  - Tkinter main window
  - USB device discovery
  - Real-time plotting

**Configuration:**

- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/RadarSettings.h`: Radar system parameters (read-only during runtime)
- `9_Firmware/9_3_GUI/GUI_V6.py`: Hard-coded system frequency, chirp durations, PRF values in dataclasses

**Core Logic:**

- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADAR1000_Manager.h/cpp`: Beamforming control
  - Phase/gain steering algorithms
  - Beam sequence management

- `9_Firmware/9_2_FPGA/radar_receiver_final.v`: RX signal processing pipeline
  - Instantiates DDC, decimator, matched filter, Doppler processor
  - Coordinates data flow between stages

- `9_Firmware/9_3_GUI/GUI_V6.py`: Target detection and visualization
  - DBSCAN clustering for target grouping
  - Kalman filtering for tracking
  - Map rendering with Folium/matplotlib

**Testing:**

- `9_Firmware/9_2_FPGA/radar_system_tb.v`: FPGA testbench
  - Stimulus generation for TX/RX paths
  - Output verification

- `8_Utils/Python/test_radar_data.csv`: Test dataset for GUI
  - Contains synthetic radar detections for demo mode

## Naming Conventions

**Files:**

- C/C++ source: snake_case with `.c` or `.cpp` extension
  - Example: `adf4382a_manager.c`, `ADAR1000_Manager.cpp`

- C/C++ headers: snake_case with `.h` extension, guards use UPPER_CASE
  - Example: `USBHandler.h` with guard `#ifndef USBHANDLER_H`

- Verilog: snake_case with `.v` extension
  - Example: `ddc_400m.v`, `radar_system_top.v`

- Memory initialization: snake_case with segment/domain suffix
  - Example: `long_chirp_seg0_i.mem` (segment 0, I-channel), `short_chirp_q.mem` (Q-channel)

- Python: snake_case for modules, CamelCase for classes
  - Example: `GUI_V6.py`, `class RadarTarget`, `class FT601Interface`

**Directories:**

- Numbered hierarchies for organization: `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries`
- Descriptive names with underscores: `Power_Management`, `Board_Stack-up`
- Tool-specific: `9_2_FPGA` (Xilinx RTL), `9_3_GUI` (Python)

**C/C++ Identifiers:**

- Types/Classes: CamelCase (e.g., `ADAR1000Manager`, `RadarSettings`, `BeamConfig`)
- Functions: camelCase (e.g., `setBeamAngle()`, `getSystemFrequency()`)
- Constants/Macros: UPPER_CASE (e.g., `GPIO_IDX_TX_CS`, `USE_LONG_CHIRP`)
- Variables: snake_case (e.g., `phase_dac1`, `chirp_duration_1`)

**Verilog Identifiers:**

- Ports: snake_case (e.g., `dac_data`, `adc_dco_p`, `ft601_txe_n`)
- Internal signals: snake_case with domain prefix (e.g., `clk_100m_buf`, `rx_doppler_valid`)
- Parameters: UPPER_CASE (e.g., `USE_LONG_CHIRP`, `DOPPLER_ENABLE`)

**Signal Names Convention:**

- Active-low signals: `_n` suffix (e.g., `ft601_txe_n`, `reset_n`, `adc_pwdn`)
- Directional: `tx_*` for transmitter, `rx_*` for receiver
- Clock domain: `clk_120m_dac` indicates 120MHz DAC clock domain

## Where to Add New Code

**New Feature - Signal Processing Algorithm:**
- **Implementation:** `9_Firmware/9_2_FPGA/` as new Verilog module
  - Follows input/output port naming convention
  - Implements CDC if crossing clock domains
  - Register outputs with pipeline stage naming
- **Integration:** Instantiate in `radar_receiver_final.v` or `radar_system_top.v`
- **Tests:** Add stimulus in `radar_system_tb.v`

**New Component/Module - RF Hardware Interface:**
- **Implementation:** `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/` as pair:
  - `component_name.h`: Interface header with struct definitions
  - `component_name.c` or `.cpp`: Implementation using no-OS HAL primitives
- **Manager Class:** Create `ComponentNameManager.h/cpp` if complex (≥5 control functions)
- **Integration:** Instantiate in `main.cpp`, call init/control from event loop

**New Utility - Python Analysis:**
- **Implementation:** `8_Utils/Python/script_name.py`
  - Follow module organization pattern
  - Include docstrings and type hints
- **Integration:** Import in `GUI_V6.py` or standalone for analysis

**New Test/Demo:**
- **GUI Demo:** Copy `GUI_V6_Demo.py`, modify CSV loading logic
- **FPGA Simulation:** Extend `radar_system_tb.v` with new test vectors

## Special Directories

**4_Schematics and Boards Layout/4_7_Production Files:**
- Purpose: Gerber files, BOM, manufacturing documentation
- Generated: Yes (from Altium design files)
- Committed: Yes (for reproducibility)

**9_Firmware/9_2_FPGA/ (*.mem files):**
- Purpose: Pre-computed chirp reference signals for matched filtering
- Generated: Yes (computed via Python scripts in `8_Utils/Python/`)
- Committed: Yes (required at compile-time)

**5_Simulations/ (subdirectories):**
- Purpose: Electromagnetic and circuit simulations (RF filters, antennas)
- Generated: Yes (OpenEMS, HFSS, LTspice outputs)
- Committed: Selectively (project files yes, large mesh outputs no)

**.planning/codebase/**
- Purpose: GSD planning documents generated from codebase analysis
- Generated: Yes (by Claude mapper tools)
- Committed: Yes (living documentation)

---

*Structure analysis: 2026-03-13*
