# Technology Stack

**Analysis Date:** 2026-03-13

## Languages

**Primary:**
- **C/C++** - Microcontroller firmware (STM32F746 HAL and no-OS libraries)
- **Verilog** - FPGA signal processing implementation (XC7A100T Artix-7)
- **Python** 3.8+ - GUI application and signal processing utilities

**Secondary:**
- **VHDL** - Potential FPGA simulation/testbench (references in file structure)

## Runtime

**Environment:**
- **STM32 Microcontroller** - STM32F746 (ARM Cortex-M7 @ ~216 MHz, 340KB RAM, 1MB Flash)
- **Xilinx FPGA** - XC7A100T Artix-7 (on-board signal processing)
- **Desktop/Linux** - Python GUI runtime for visualization

**Package Manager:**
- **Python pip** - Used for Python dependencies
- No detected package.json or requirements.txt (Python dependencies hard-coded in imports)
- STM32CubeIDE / ARM GCC for microcontroller compilation

## Frameworks

**Core:**
- **Tkinter** - Python GUI framework (dark-themed desktop application)
- **Matplotlib** - Real-time radar plotting with FigureCanvasTkAgg backend
- **NumPy/SciPy** - Signal processing arrays and operations
- **STM32Cube HAL** - Hardware abstraction layer for STM32F746
- **Xilinx Vivado** (inferred) - FPGA design and synthesis framework

**Testing:**
- No dedicated test framework detected in codebase
- FPGA testbenches present: `radar_system_tb.v` at `9_Firmware/9_2_FPGA/radar_system_tb.v`

**Build/Dev:**
- **STM32CubeIDE** - Microcontroller development (HAL files present)
- **Xilinx Vivado** - FPGA synthesis and implementation
- **xdc constraint files** - Present at `9_Firmware/9_2_FPGA/cntrt.xdc`

## Key Dependencies

**Critical:**
- **scikit-learn** (v? unspecified) - DBSCAN clustering for target detection
  - `from sklearn.cluster import DBSCAN` in `9_Firmware/9_3_GUI/GUI_V6.py:16`
- **filterpy** (v? unspecified) - Kalman filtering for target tracking
  - `from filterpy.kalman import KalmanFilter` in `9_Firmware/9_3_GUI/GUI_V6.py:17`
- **scipy** (v? unspecified) - Signal processing (scipy.signal)
  - `from scipy import signal` in `9_Firmware/9_3_GUI/GUI_V6.py:15`

**Infrastructure:**
- **pyusb** - USB device communication (optional, graceful fallback)
  - `import usb.core`, `import usb.util` in `9_Firmware/9_3_GUI/GUI_V6.py:25-26`
  - Used for STM32 USB CDC communication
- **pyftdi** - FTDI USB FIFO interface (optional, graceful fallback)
  - `from pyftdi.ftdi import Ftdi` in `9_Firmware/9_3_GUI/GUI_V6.py:33`
  - Supports FT601 USB 3.0 SuperSpeed controller for high-speed radar data streaming
- **crcmod** - CRC computation for packet validation
  - `import crcmod` in `9_Firmware/9_3_GUI/GUI_V6.py:18`
- **TinyGPSPlus** - GPS data parsing (C++ library ported to C)
  - `TinyGPSPlus.h` at `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/TinyGPSPlus.h`
- **Analog Devices no-OS libraries** - Core device drivers
  - Multiple AD drivers: `adf4382.h`, `adar1000.h`, `ad9523.h`
  - Located at `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/`

## Configuration

**Environment:**
- GUI API Key: `GOOGLE_MAPS_API_KEY` placeholder in `9_Firmware/9_3_GUI/GUI_V6.py:414`
- System parameters defined in `RadarSettings` dataclass:
  - `system_frequency: 10e9` (10.5 GHz)
  - `chirp_duration_1: 30e-6` and `chirp_duration_2: 0.5e-6`
  - `chirps_per_position: 32`
  - `max_distance: 50000` meters

**Build:**
- **STM32CubeIDE project** - Uses `.ioc` project files (not present, likely generated)
- **Xilinx TCL scripts** - FPGA automation scripts expected
- **Verilog constraints** - `cntrt.xdc` at `9_Firmware/9_2_FPGA/cntrt.xdc` (16.6 KB, Artix-7 specific)
- **Memory initialization files** - `.mem` files for chirp LUTs:
  - Long chirp segments: `long_chirp_seg{0,1,2}_{i,q}.mem`
  - Short chirp segments: `short_chirp_{i,q}.mem`

## Platform Requirements

**Development:**
- **STM32CubeIDE** or GCC ARM toolchain for microcontroller compilation
- **Xilinx Vivado 2021.x or later** for FPGA synthesis (inferred from XC7A100T device)
- **Python 3.8+** with pip for GUI runtime
- **Linux/macOS/Windows** host for GUI application

**Production:**
- **STM32F746** microcontroller with programmed firmware
- **XC7A100T Artix-7 FPGA** with configured bitstream
- **FT601 USB 3.0 SuperSpeed controller** for high-speed data (primary interface)
- **USB CDC communication** via STM32 for control/configuration (fallback)
- **GPS module** (GY-85 IMU) optional for position correction
- **Power management** board for voltage sequencing to subsystems

## Special Components

**RF/Analog:**
- **AD9523-1** - Low-jitter clock generator (100 MHz reference)
- **ADF4382** - Frequency synthesizers (2x for RX/TX paths)
- **ADAR1000** - 4-channel phase shifters (4x for beamforming, 16 elements total)
- **ADTR1107** - Front-end ICs for LNA/PA stages (16x)
- **LT5552** - Microwave mixers (2x for up/down-conversion)
- **DAC5578** - Power amplifier gate voltage control
- **ADS7830** - ADC for temperature/current sensing (8x temperature, 2x current)

**Connectivity:**
- **USB 3.0 (FT601)** - Primary high-speed data interface (up to 400 MB/s raw)
- **USB CDC (STM32)** - Control and configuration interface
- **UART** - GPS module communication
- **I2C/SPI** - Peripheral communication (clock gen, synthesizers, phase shifters, ADCs)
- **GPIO** - RF switches, stepper motor, cooling fan control

---

*Stack analysis: 2026-03-13*
