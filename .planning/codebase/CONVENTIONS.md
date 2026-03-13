# Coding Conventions

**Analysis Date:** 2026-03-13

## Naming Patterns

**Files:**
- C++ implementation files: `ClassName.cpp` - PascalCase for class-based files
- C++ header files: `ClassName.h` - PascalCase matching implementation
- Python scripts: `script_name.py` or `GUI_VX.py` - snake_case for utility scripts, versioned naming for GUI applications
- Examples: `ADAR1000_Manager.cpp/.h`, `BMP180.cpp`, `GUI_V6.py`, `CSV_radar.py`, `LUT.py`

**Functions:**
- C++: camelCase for class methods, snake_case for C-style functions
  - Public methods: `powerUpSystem()`, `setBeamAngle()`, `switchToTXMode()`
  - Private helpers: `initializeSingleDevice()`, `calculatePhaseSettings()`
  - Low-level register ops: `adarWrite()`, `adarRead()`, `adarSetBit()`
- Python: snake_case for all functions
  - Examples: `generate_radar_csv()`, `create_input_fields()`, `create_results_display()`

**Variables:**
- C++:
  - Member variables with trailing underscore: `current_mode_`, `beam_sweeping_active_`, `devices_`, `last_switch_time_us_`
  - Local variables: camelCase: `deviceIndex`, `phase_settings`, `rxBuffer`, `temp`
  - Constants: UPPER_CASE: `GPIO_IDX_TX_CS`, `BROADCAST_OFF`, `REG_INTERFACE_CONFIG_A`
- Python:
  - Constants: UPPER_CASE: `DARK_BG`, `DARK_FG`, `DARK_ACCENT`, `USB_AVAILABLE`
  - Instance variables: snake_case: `system_frequency`, `chirp_duration_1`, `noise_std`
  - Local variables: snake_case: `num_samples`, `target_list`, `timestamp_ns`

**Types:**
- C++:
  - Classes: PascalCase: `ADAR1000Manager`, `ADAR1000Device`, `BeamConfig`
  - Enums: PascalCase with descriptive values: `BeamDirection::TX`, `BeamDirection::RX`
  - Structs: PascalCase: `BeamConfig`, `ADAR1000Device`, `GPSData`
- Python:
  - Dataclasses: PascalCase: `RadarTarget`, `RadarSettings`, `GPSData`
  - Internal type hints: `Dict`, `List`, `Tuple`, `Optional`

## Code Style

**Formatting:**
- No automated formatter detected. Formatting varies between files.
- C++ files use 4-space indentation (observed in ADAR1000_Manager.cpp)
- Python files use 4-space indentation (PEP 8 style)
- Line length: varies, no strict limit enforced

**Linting:**
- No ESLint, Prettier, or Python linting configuration found
- Code style is manual/self-enforced

## Import Organization

**Order:**
1. Standard library headers (C++): `#include <vector>`, `#include <memory>`, `#include <cmath>`
2. HAL/Platform specific: `#include "stm32f7xx_hal.h"`, `#include "main.h"`
3. Project-specific headers: `#include "ADAR1000_Manager.h"`, `#include "adar1000.h"`
4. C/C++ mixed headers wrapped with `extern "C"` when needed

**Path Aliases:**
- No path aliases detected
- Full relative paths used throughout

**Python Imports:**
Order observed in GUI files (`GUI_V6.py`, `GUI_V5.py`):
1. Standard library: `import tkinter`, `import threading`, `import time`
2. Third-party scientific: `import numpy`, `import matplotlib`, `from scipy import signal`
3. Third-party utility: `import logging`, `import struct`, `import crcmod`
4. USB/Hardware: `import usb.core`, `from pyftdi.ftdi import Ftdi` (wrapped in try/except with feature flags)
5. Project utilities: Custom classes defined inline or imported

## Error Handling

**Patterns:**
- C++: Boolean return values indicate success/failure (`bool powerUpSystem()`, `bool setBeamAngle()`)
  - Returns `true` on success, `false` on failure
  - Functions that query state return data directly (`float readTemperature()`, `uint8_t readRegister()`)
  - No exception throwing observed; uses HAL status checks: `HAL_StatusTypeDef status`

- Python:
  - Try/except blocks for optional dependencies: Lines 24-38 in GUI_V6.py show feature flag pattern
  - Logging used for warnings: `logging.warning("pyusb not available...")`
  - GUI uses `messagebox` for user-facing errors

**No defensive null checks observed** - assumes pointer/reference validity after construction

## Logging

**Framework:**
- C++: UART-based logging using HAL: `HAL_UART_Transmit(&huart3, msg, size, timeout)`
- Python: Python's `logging` module configured with INFO level
  - `logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')`

**Patterns:**
- C++: String constants transmitted over UART: `const uint8_t msg[] = "Starting System Power-Up Sequence...\r\n";`
- Python: Standard logger calls with timestamps automatically added
- Both systems log major system transitions (power-up/down, mode switches)

## Comments

**When to Comment:**
- Register address definitions have brief inline comments: `#define BROADCAST_OFF  0  // No broadcast`
- GPIO mappings documented: `{GPIOA, GPIO_PIN_0}, // ADAR1000 #1`
- Complex calculations occasionally have explanatory text (e.g., phase calculation formulas)
- System initialization steps frequently documented inline

**JSDoc/TSDoc:**
- Not used; C++ uses simple block comments for file headers
- Python files have minimal docstrings; some methods have brief descriptions in quotes
- Example from RADAR_eq.py: `"""Create all input fields with labels and units"""`

**Comment Style:**
- C++: `// Single line` and `/* Multi-line */`
- Python: `# Single line` and `"""Docstrings"""`

## Function Design

**Size:**
- Range: 5-50 lines typically, max observed ~100 lines
- Longer functions: `main()` in main.cpp (2411 lines total file), `setADTR1107Mode()` (~70 lines)
- Short helper functions common: `enablePASupplies()` (4 lines), `disableLNASupplies()` (2 lines)

**Parameters:**
- C++: Typically 1-3 parameters per function
  - Uses uint8_t device indices for hardware selection
  - Boolean flags for mode control
  - Const references for large data: `const uint8_t phase_settings[4]`
  - Example: `void adarSetRxPhase(uint8_t deviceIndex, uint8_t channel, uint8_t phase, uint8_t broadcast)`

- Python: Often 1-2 parameters for methods, more for initialization
  - Heavy use of self for instance methods
  - Default parameters common: `def setBeamDwellTime(self, ms=100)`

**Return Values:**
- C++:
  - Status methods return `bool` (success indicator)
  - Data queries return specific types: `float`, `uint8_t`, `uint32_t`
  - Some functions return void and modify state through member variables

- Python:
  - Methods often return None (modify instance state)
  - Generator functions in utility scripts return computed results
  - GUI update methods typically void

## Module Design

**Exports:**
- C++: Classes defined in headers expose all public methods; no interface/implementation separation beyond class definitions
- Python: Scripts are typically run directly; no structured module exports observed

**Barrel Files:**
- Not used in this codebase
- Each file has specific responsibility (ADAR1000_Manager handles ADAR device, GUI_V6 is complete app)

**Public/Private Boundaries:**
- C++: Clear public/private sections in class definitions
  - ADAR1000Manager.h shows full public API (lines 42-83) and private implementations (lines 124-157)
  - Sensitive low-level SPI operations (adarWrite, adarRead) marked private but implemented in .cpp

- Python: Convention-based (leading underscore not used; class methods are all public by design)

**Initialization Patterns:**
- C++:
  - Constructor initializes member vectors: `for (int i = 0; i < 4; ++i) { devices_.push_back(...) }`
  - Explicit initialization required: `bool powerUpSystem()` must be called
  - Default member values in class: `bool fast_switch_mode_ = false;`

- Python:
  - Dataclass decorators for simple data: `@dataclass` with type hints
  - Class __init__ methods for complex initialization

---

*Convention analysis: 2026-03-13*
