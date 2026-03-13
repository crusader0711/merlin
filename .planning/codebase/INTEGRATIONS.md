# External Integrations

**Analysis Date:** 2026-03-13

## APIs & External Services

**Mapping:**
- **Google Maps** - Web-based map visualization for radar overlay
  - SDK/Client: Embedded HTML/JavaScript in Python-generated map template
  - Auth: `GOOGLE_MAPS_API_KEY` environment variable placeholder in `9_Firmware/9_3_GUI/GUI_V6.py:414`
  - Usage: Map generation via `MapGenerator` class, opens in system browser via `webbrowser` module
  - Location: `9_Firmware/9_3_GUI/GUI_V*.py` (all GUI versions)

## Data Storage

**Databases:**
- **None detected** - No persistent database backend
- CSV data used for test/demo purposes only:
  - `8_Utils/Python/test_radar_data.csv` (476 KB)
  - `8_Utils/Python/small_test_radar_data.csv` (56 KB)
  - `9_Firmware/9_3_GUI/test_radar_data.csv` (476 KB)

**File Storage:**
- **Local filesystem only** - Radar data and generated maps stored locally
  - Temporary directory: Used via `tempfile.mktemp()` in `GUI_V6.py`
  - Generated HTML maps: Created as temporary files with map overlay
  - CSV export capability implied (no integration file format, local save)

**Caching:**
- **None** - No caching layer detected

## Sensors & Hardware Interfaces

**Position/Navigation:**
- **GPS Module** - Real-time positioning
  - Driver: `TinyGPSPlus.h` at `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/`
  - Communication: UART interface from STM32F746
  - Data: Latitude, longitude, altitude
  - Integration: `GPSData` dataclass with `latitude`, `longitude`, `altitude` fields

**Inertial Measurement:**
- **GY-85 IMU** - 9-DOF (accelerometer, gyroscope, magnetometer)
  - Driver: `GY_85_HAL.h` at `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/`
  - Communication: I2C from STM32F746
  - Data: Pitch/roll/yaw for target coordinate correction
  - Integration: Pitch angle used to correct radar target elevations in GUI

**Environmental:**
- **BMP180 Barometer** - Altitude/pressure measurement
  - Communication: I2C from STM32F746
  - Driver: Referenced in README but no dedicated header file found

## Microcontroller Communication

**STM32F746 USB Interface:**
- **Protocol**: USB CDC (Communications Device Class)
- **Purpose**: Control and configuration of radar system
- **Data Exchange**: Radar settings, start/stop flags, power sequencing
- **Implementation**: `STM32USBInterface` class in GUI (not fully shown but referenced)
- **Baud Rate**: USB (480 Mbps FS)

**Configuration Commands:**
- Start flag transmission: `send_start_flag()` method
- Settings application: `apply_settings()` method
- Device enumeration via `list_devices()` method

## FPGA Data Interface

**FT601 USB 3.0 SuperSpeed:**
- **Vendor/Product IDs**:
  - FT601: 0x0403:0x6030
  - FT601Q: 0x0403:0x6031
- **Data Rate**: USB 3.0 (400 MB/s+ theoretical)
- **Configuration**: 32-bit word aligned transfers, FIFO mode
- **Buffer Size**: 512 bytes optimal for FT601
- **Burst Mode**: Configurable for maximum throughput (4KB chunks when enabled)
- **Implementation**: `FT601Interface` class in `9_Firmware/9_3_GUI/GUI_V6.py:94-363`
- **Features**:
  - Dual-mode open: pyftdi (preferred) or direct USB access (fallback)
  - Latency timer: 2ms
  - Frequency: 100 MHz clock
  - Packet parsing with CRC validation

**Data Packets:**
- **Format**: 32-bit aligned, minimum 8 bytes
- **Content**: Raw radar signal data from FPGA ADC interface
- **Validation**: CRC24 checking via `crcmod` library

## Signal Processing Pipeline

**On-Device (FPGA XC7A100T):**
- **ADC Interface**: AD9484 400 MHz ADC acquisition
  - Driver: `ad9484_interface_400m.v` at `9_Firmware/9_2_FPGA/`
- **Signal Processing Blocks**:
  - DDC (Digital Down Converter): `ddc_400m.v`
  - CIC Decimator: `cic_decimator_4x_enhanced.v`
  - FIR Lowpass Filter: `fir_lowpass.v`
  - NCO (Numerically Controlled Oscillator): `nco_400m_enhanced.v`
  - FFT 1024-point: `fft_1024_forward.v`, `fft_1024_inverse.v`
  - Matched Filter: `matched_filter_multi_segment.v`
  - Doppler Processor: `doppler_processor.v`
  - CFAR Detection: Implied (mentioned in README but no separate module)

**On-Host (Python GUI):**
- **Target Clustering**: DBSCAN (scikit-learn) for detection grouping
- **Target Tracking**: Kalman filter (filterpy) for multi-target tracking
- **Signal Analysis**: SciPy signal processing for verification/analysis
- **Visualization**: Matplotlib real-time plotting with tkinter backend

## Waveform Generation

**Chirp Waveforms:**
- **Storage**: Memory files for LUT (Look-Up Table)
  - Long chirp segments (3x I/Q pairs): 6 KB each = 18 KB total
  - Short chirp segments (I/Q pair): 300 bytes each = 600 bytes total
  - Files located at `9_Firmware/9_2_FPGA/`
- **Generation**: PLFM (Pulse Linear Frequency Modulated)
- **Controller**: `plfm_chirp_controller.v` (125 KB, complex controller module)
- **Characteristics**:
  - Long chirp: 30 microseconds
  - Short chirp: 0.5 microseconds
  - RF Frequency: 10.5 GHz
  - Chirp rate: 1-2 MHz/microsecond (estimated from component specs)

## Beam Steering Interface

**Phase Shifter Control (ADAR1000):**
- **Quantity**: 4x ADAR1000 (each 4-channel = 16 channels total)
- **Communication**: SPI from STM32F746
- **Purpose**: Electronic beam steering (±45° azimuth/elevation)
- **Control Method**: Phase value programming per TX/RX element
- **Implementation**: `adar1000.h` driver in microcontroller firmware
- **Manager**: `ADAR1000_Manager.h` higher-level interface

**Frequency Synthesizer Control (ADF4382):**
- **Quantity**: 2x (RX and TX paths)
- **Communication**: SPI from STM32F746
- **Purpose**: LO generation for up/down conversion
- **Implementation**: `adf4382.c/h` drivers with manager layer `adf4382a_manager.c`

## Clock Distribution

**AD9523-1 Clock Generator:**
- **Reference**: 100 MHz external oscillator
- **Outputs**: Provides synchronized clocks to:
  - DAC (chirp generation)
  - ADC (signal acquisition)
  - FPGA (all signal processing)
  - RX/TX Synthesizers (LO generation)
- **Control**: SPI from STM32F746
- **Driver**: `ad9523.h` with status monitoring

## Temperature & Monitoring

**Temperature Sensors:**
- **Quantity**: 8x ADS7830 ADCs with thermistors
- **Purpose**: Cooling fan feedback and PA thermal management
- **Communication**: I2C from STM32F746
- **Implementation**: `ADS7830.c` driver

**Current Monitoring:**
- **Power Amplifier Current**: 2x ADS7830 ADCs
- **Purpose**: PA output monitoring, power sequencing feedback
- **Communication**: I2C from STM32F746

**Gate Voltage Control:**
- **DAC Interface**: 2x DAC5578 (8-channel DACs)
- **Purpose**: Programmable gate voltage for GaN power amplifiers
- **Communication**: I2C from STM32F746

## Power Management Integration

**Sequencing:**
- **Microcontroller Role**: STM32F746 manages power-up/power-down sequence
- **Voltage Rails**:
  - 5V (general digital, PA bias)
  - 1.8V (FPGA I/O)
  - 3.3V (FPGA core, ADAR, clock, switches, ADCs)
  - 1.0V (FPGA core)
  - 5.5V (PA supply boost)
- **Enable Control**: GPIO-controlled enable pins for each rail
  - Sequence defined in Power Management spreadsheet (not in codebase)

## Mechanical Control

**Stepper Motor:**
- **Purpose**: 360° mechanical antenna rotation
- **Control**: Step/direction signals from STM32F746
- **GPIO Pins**: `STEPPER_CW_P` and `STEPPER_CLK_P`
- **Driver**: Stepper driver chip (not explicitly named, likely DRV series)

**Cooling System:**
- **Control**: On/off GPIO enable for cooling fans
- **Pin**: `EN_DIS_COOLING`
- **Feedback**: Temperature sensors (8x) for automatic control

## Test Data & Simulation

**Python Simulation Tools:**
- **CSV Radar Generator**: `CSV_radar.py`, `CSV_radar_2.py` at `8_Utils/Python/`
- **Chirp Generators**: `Gen_Triangular.py`, `Generic_Ramp_Frequency.py`
- **Antenna Pattern Analysis**: `patch_antenna.py`
- **Radar Equation Calculator**: `RADAR_eq.py` with tkinter GUI
- **FFT Analysis**: `FFT_Ramp_Frequency.py`

**Location**: `8_Utils/Python/` directory

## Logging & Diagnostics

**Logging Framework:**
- Python logging module (standard library)
- Level: INFO
- Format: `%(asctime)s - %(levelname)s - %(message)s`
- Configured in `GUI_V*.py` files

**Log Points:**
- USB device enumeration
- Device open/close operations
- Radar start/stop operations
- FT601 burst mode configuration
- Error conditions (USB errors, parsing errors, timeout conditions)

---

*Integration audit: 2026-03-13*
