# Testing Patterns

**Analysis Date:** 2026-03-13

## Test Framework

**Runner:**
- No test framework detected
- No pytest, unittest, Jest, or other test runner configuration found
- No test configuration files: `pytest.ini`, `conftest.py`, `setup.py`, `tox.ini`

**Assertion Library:**
- Not applicable - no automated testing framework in use

**Run Commands:**
- No standardized test execution scripts found
- C++ firmware built via STM32CubeIDE (HAL-based)
- Python scripts run directly: `python script_name.py`
- No `make test`, `npm test`, `pytest` or similar commands configured

## Test File Organization

**Location:**
- Test data files exist but are data fixtures, not tests:
  - `/8_Utils/Python/test_radar_data.csv` - Sample radar data for GUI testing
  - `/8_Utils/Python/small_test_radar_data.csv` - Reduced dataset variant
  - `/9_Firmware/9_3_GUI/test_radar_data.csv` - GUI test data

**Naming:**
- No standardized test file naming pattern (e.g., no `test_*.py` or `*_test.cpp` files)
- Data fixtures prefixed with `test_` but not actual test code

**Structure:**
- No dedicated test directory
- Test data colocated with utilities and applications

## Test Structure

**Suite Organization:**
- No test suites found

**Patterns:**
- Manual testing through GUI applications
- Data validation through CSV comparison
- Hardware testing likely performed on physical radar hardware

## Mocking

**Framework:**
- Not applicable; no unit testing framework in use

**Patterns:**
- No mock objects or stubbing detected
- Full integration testing implied by architecture

**What to Mock:**
- N/A

**What NOT to Mock:**
- N/A

## Fixtures and Factories

**Test Data:**
- CSV-based radar data fixtures in `/8_Utils/Python/`
  - `CSV_radar.py` - Generates synthetic radar data with realistic targets
  - `CSV_radar_2.py` - Reduced-size variant of radar data generator
  - These scripts create test datasets programmatically

Example fixture generation from `CSV_radar.py`:
```python
def generate_radar_csv(filename="pulse_compression_output.csv"):
    """Generate realistic radar CSV data for testing the Python GUI"""

    targets = [
        {'range': 3000, 'velocity': 25, 'snr': 30, 'azimuth': 10, 'elevation': 5},
        {'range': 5000, 'velocity': -15, 'snr': 25, 'azimuth': 20, 'elevation': 2},
        {'range': 8000, 'velocity': 5, 'snr': 20, 'azimuth': 30, 'elevation': 8},
        {'range': 12000, 'velocity': -8, 'snr': 18, 'azimuth': 45, 'elevation': 3},
    ]

    data = []
    for chirp in range(num_long_chirps):
        for sample in range(samples_per_chirp):
            # Accumulate target signatures with noise
            i_val = np.random.normal(0, noise_std)
            q_val = np.random.normal(0, noise_std)
            # ... add targets and generate entry
```

**Location:**
- `/8_Utils/Python/` - Utility scripts that generate test data
- Data stored as CSV files for manual verification and GUI testing

## Coverage

**Requirements:**
- No coverage requirements enforced
- No `.coveragerc` or similar configuration

**View Coverage:**
- Not applicable

## Test Types

**Unit Tests:**
- Not implemented
- Individual functions tested informally through hardware operation
- Firmware validation occurs through STM32 debugging and UART output

**Integration Tests:**
- Implicit through operation:
  - Power sequencing: `powerUpSystem()` → `initializeAllDevices()` → `setBeamAngle()`
  - Mode transitions: `switchToTXMode()` → peripheral configuration chain
  - Data acquisition: ADC reads → signal processing → CSV output

- GUI integration:
  - USB communication tested manually through pyusb/FTDI interfaces
  - Data visualization validated visually with test CSV data
  - Map rendering tested with synthetic GPS coordinates

**E2E Tests:**
- Not formalized
- Real radar hardware testing is the primary validation
- GUI-to-firmware integration tested through:
  - USB command sequencing
  - Live radar data capture to CSV
  - Beam steering angle verification

## Common Patterns

**Async Testing:**
- C++: No async testing; firmware is event-driven via interrupts
  - Delays used for settling times: `HAL_Delay(10)`, `delayUs(50)`
  - Timing critical operations hardcoded with specific delays
  - No async test harness

- Python: Threading used in GUI but not tested
  - Queue-based communication between threads
  - Manual verification through GUI responsiveness

**Error Testing:**
- Limited error path testing observed
- Hardware communication failures detected through return codes:
  ```cpp
  if (!initializeSingleDevice(i)) {
      return false;  // Propagates initialization failure
  }
  ```

- No explicit error injection or fault injection testing framework
- Verification through boolean success indicators

## Manual Testing Patterns

**Firmware Validation:**
- UART output for debugging: messages logged to serial console
- Register readback verification: `verifyDeviceCommunication()` writes test value 0xA5 to scratchpad
- Temperature sensor validation: `readTemperature()` samples ADC
- Beam angle verification through RF measurement (off-system)

**GUI Testing:**
- Visual inspection of plotted targets on radar screen
- CSV data comparison for signal processing correctness
- USB communication logs for protocol verification
- Interactive testing with test data CSV files

**Hardware Testing:**
- Power sequencing verified with multimeter/scope
- Frequency stability checked with spectrum analyzer
- Beam patterns measured with horn antenna sweep
- Target detection validated with RCS calibration targets

## Data Generation for Testing

**Radar Simulation:**
Location: `/8_Utils/Python/CSV_radar.py`

Generates realistic I/Q radar data with:
- Multiple moving targets with specified Doppler shifts
- Noise modeling (Gaussian)
- Clutter simulation (stationary targets)
- Long and short chirp sequences

Parameters configurable:
- Number of chirps, samples per chirp
- Target range, velocity, SNR, azimuth/elevation
- Noise standard deviation
- ADC sampling frequency

Output: CSV file with columns:
- `timestamp_ns`, `chirp_number`, `chirp_type`, `sample_index`, `I_value`, `Q_value`, `magnitude_squared`

**Frequency Generation:**
Location: `/8_Utils/Python/LUT.py`, `/8_Utils/Python/Generic_Ramp_Frequency.py`

Scripts generate waveform lookup tables and frequency ramps for:
- DAC programming
- Verilog simulation data
- Signal validation

---

*Testing analysis: 2026-03-13*
