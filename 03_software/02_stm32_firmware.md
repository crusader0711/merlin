# STM32 Firmware Architecture

**Purpose:** Documents the STM32F7 microcontroller firmware (`main.cpp`, ~2000 lines; `main.h`, GPIO pin map) covering the complete 17-step initialization sequence, SPI/I2C peripheral configuration, magic number derivations from physics and component specifications, and the main radar loop control flow for azimuth/elevation scanning with dual-chirp sequencing.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Power Management](../02_hardware/06_power_management.md) -- power-on sequencing and GPIO rail control
- [Frequency Synthesis](../02_hardware/03_frequency_synthesis.md) -- AD9523 clock tree and ADF4382 LO
- [Antenna and Beamforming](../02_hardware/04_antenna_beamforming.md) -- ADAR1000 beam steering and phase calculation
- [Timing Budget](../02_hardware/07_timing_budget.md) -- pipeline latency and chirp timing

---

## 1. Firmware Architecture Overview

The STM32F7 firmware operates as the central controller for the AERIS-10 radar system. It manages three distinct phases of operation:

1. **Initialization** (Steps 1--17): Power sequencing of all subsystems, sensor calibration, clock configuration, beamformer setup, and GUI synchronization. Total duration ranges from approximately 200 seconds (dominated by the 180-second OCXO warm-up) to several minutes depending on GPS acquisition and user start command.

2. **Main Radar Loop**: Continuous azimuth/elevation scanning with dual-chirp sequencing, FPGA handshake signaling, and stepper motor control. Each full revolution covers $N_\text{az}$ (`y_max` in `main.cpp`) azimuth positions with $N_\text{el}$ (`n_max`) elevation beam positions per azimuth.

3. **Error Handling and Monitoring**: Periodic health checks of all subsystems (clock lock, IMU, barometer, GPS, PA current, temperature) with automatic recovery for non-critical faults and emergency shutdown for critical faults.

### Firmware Block Diagram

| Phase | Subsystems | Duration |
|-------|-----------|----------|
| Initialization (Steps 1--3) | MCU core, HAL, GPIO, SPI, I2C, UART, USB, Timer | ~ms |
| Initialization (Step 4) | OCXO warm-up wait | 180 s |
| Initialization (Steps 5--7) | Clock tree (AD9523), FPGA power | ~1 s |
| Initialization (Steps 8--9) | IMU (GY-85), Barometer (BMP180) | ~4 s |
| Initialization (Steps 10--12) | LO (ADF4382), Beamformer (ADAR1000) | 2--11 s |
| Initialization (Steps 13--15) | GPS, Stepper, GUI sync | 10 s + user |
| Initialization (Steps 16--17) | PA bias (if enabled), FPGA reset | ~2 s |
| Main Loop | Radar pulse sequence + health monitoring | Continuous |

---

## 2. Initialization Sequence

The complete 17-step power-up and initialization sequence executes in `main()` (lines 1189--1699 of `main.cpp`). Each step is documented with the exact GPIO pins toggled, the function called, the purpose of any delay, and cross-references to the relevant hardware documentation.

### 2.1 Initialization Sequence Table

| Step | Action | Code Location | Duration |
|------|--------|---------------|----------|
| 1 | MPU / HAL / Clock config | `MPU_Config()`, `HAL_Init()`, `SystemClock_Config()`, `PeriphCommonClock_Config()` | ~ms |
| 2 | Peripheral initialization | `MX_GPIO_Init()` through `MX_USB_DEVICE_Init()` | ~ms |
| 3 | Start TIM1 + DWT | `HAL_TIM_Base_Start(&htim1)`, `DWT_Init()` | ~ms |
| 4 | OCXO warm-up wait | `HAL_Delay(180000)` | 180 s |
| 5 | AD9523 power sequence | 1V8_CLOCK, 3V3_CLOCK, release reset | 300 ms |
| 6 | AD9523 clock configuration | `configure_ad9523()` -- 12 channel outputs | ~100 ms |
| 7 | FPGA power sequence | 1V0, 1V8, 3V3 (100 ms each) | 300 ms |
| 8 | IMU initialization | `GY85_Init()` + 10 iterations with complementary filter | ~3 s |
| 9 | Barometer calibration | `myBMP.getPressure()` x 5 iterations | ~500 ms |
| 10 | ADF4382 LO initialization | `ADF4382A_Manager_Init()` + lock wait (up to 10 s) | 1--10 s |
| 11 | ADAR1000 power + init | 3V3_ADAR12/34, 5V0_ADAR, `systemPowerUpSequence()` | ~1 s |
| 12 | Beam matrix initialization | `initializeBeamMatrices()` -- 31 positions x 16 elements | ~ms |
| 13 | GPS acquisition | `smartDelay(1000)` x 10 iterations | 10 s |
| 14 | Point stepper to North | Stepper motor rotation based on IMU yaw | variable |
| 15 | Send GPS to GUI + wait for start | `GPS_SendBinaryToGUI()` + poll `isStartFlagReceived()` | user-dependent |
| 16 | PA power-up (if enabled) | DAC5578 init, set Vg, enable VDD, Idq tuning | ~2 s |
| 17 | FPGA reset + enable mixers | GPIO toggle PD12 + PD11 | ~10 ms |

### 2.2 Step Details

#### Step 1: MPU / HAL / System Clock Configuration

The STM32F7 Memory Protection Unit (MPU) is configured first via `MPU_Config()`, followed by `HAL_Init()` which resets all peripherals and initializes the Flash interface and SysTick timer. `SystemClock_Config()` sets up the PLL chain: HSE (25 MHz external crystal) with PLLM=25, PLLN=144, PLLP=2 yields a system clock of 72 MHz. APB1 is divided by 2 (36 MHz), APB2 runs at full speed (72 MHz). `PeriphCommonClock_Config()` activates the TIM prescaler to double the timer clock frequency.

#### Step 2: Peripheral Initialization

All STM32 peripherals are initialized in sequence via STM32CubeMX-generated functions:

| Function | Peripheral | Purpose |
|----------|-----------|---------|
| `MX_GPIO_Init()` | GPIO ports A--G | All power enables, SPI CS, LED, stepper, FPGA control |
| `MX_TIM1_Init()` | TIM1 | Microsecond counter (72 MHz / prescaler 71 = 1 MHz) |
| `MX_I2C1_Init()` | I2C1 | DAC5578 gate voltage control |
| `MX_I2C2_Init()` | I2C2 | ADS7830 current/temperature monitoring |
| `MX_I2C3_Init()` | I2C3 | GY-85 IMU |
| `MX_SPI1_Init()` | SPI1 | ADAR1000 beamformer ICs |
| `MX_SPI4_Init()` | SPI4 | AD9523 clock generator, ADF4382 TX/RX LOs |
| `MX_UART5_Init()` | UART5 | GPS receiver (NMEA input) |
| `MX_USART3_UART_Init()` | USART3 | Debug console output |
| `MX_USB_DEVICE_Init()` | USB OTG FS | USB CDC interface to host GUI |

#### Step 3: Timer and Cycle Counter Start

`HAL_TIM_Base_Start(&htim1)` starts the microsecond timer used by `delay_us()` and `micros()`. `DWT_Init()` enables the ARM Data Watchpoint and Trace unit cycle counter (`DWT->CYCCNT`) for nanosecond-resolution delays used during the short chirp $T_{c,2}$ (`T2` in `main.cpp`) timing via `delay_ns()`.

#### Step 4: OCXO Warm-Up Wait

`HAL_Delay(180000)` pauses for 180 seconds (3 minutes) to allow the oven-controlled crystal oscillator (OCXO) to reach thermal equilibrium. The OCXO provides the 100 MHz reference input to the AD9523-1 clock generator. Frequency stability requires the crystal oven to reach its set-point temperature before the clock tree can generate phase-coherent outputs. See [Power Management](../02_hardware/06_power_management.md) for the OCXO thermal specifications.

During this wait, the AD9523 reset pin is held low (`AD9523_RESET_Pin` = PF6, asserted via `GPIO_PIN_RESET`), preventing the clock generator from attempting to lock to an unstable reference.

#### Step 5: AD9523 Power Sequence

The AD9523-1 clock generator is powered in the correct rail order to prevent latch-up:

1. Enable 1.8 V clock supply: `EN_P_1V8_CLOCK_Pin` (PG4) set HIGH, wait 100 ms
2. Enable 3.3 V clock supply: `EN_P_3V3_CLOCK_Pin` (PG5) set HIGH, wait 100 ms
3. Release reset: `AD9523_RESET_Pin` (PF6) set HIGH, wait 100 ms

Total step duration: 300 ms. Cross-reference: [Power Management](../02_hardware/06_power_management.md) for rail sequencing constraints and [Frequency Synthesis](../02_hardware/03_frequency_synthesis.md) for the AD9523-1 PLL architecture.

#### Step 6: AD9523 Clock Configuration

`configure_ad9523()` programs the AD9523-1 via SPI4 (CS on PF7, 10 MHz SPI clock, Mode 0). The PLL2 is configured with N=36 (VCO at 3.6 GHz from 100 MHz reference) and the following output channels are enabled:

| Channel | Output | Divider | Frequency | Driver | Purpose |
|---------|--------|---------|-----------|--------|---------|
| OUT0 | ADF4382 TX ref | /12 | 300 MHz | LVDS 7 mA | TX LO reference clock |
| OUT1 | ADF4382 RX ref | /12 | 300 MHz | LVDS 7 mA | RX LO reference clock (phase-aligned with OUT0) |
| OUT4 | ADC clock | /9 | 400 MHz | LVDS 7 mA | AD9484 sampling clock |
| OUT5 | FPGA ADC clock | /9 | 400 MHz | LVDS 7 mA | FPGA ADC data capture (phase-aligned with OUT4) |
| OUT6 | FPGA system clock | /36 | 100 MHz | LVCMOS | FPGA processing clock domain |
| OUT7 | FPGA test clock | /180 | 20 MHz | LVCMOS | FPGA debug/test |
| OUT8 | Sync TX | /60 | 60 MHz | LVDS 4 mA | ADF4382 TX synchronization |
| OUT9 | Sync RX | /60 | 60 MHz | LVDS 4 mA | ADF4382 RX synchronization (phase-aligned with OUT8) |
| OUT10 | DAC clock | /30 | 120 MHz | LVCMOS | DAC interface clock |
| OUT11 | FPGA DAC clock | /30 | 120 MHz | LVCMOS | FPGA DAC domain (phase-aligned with OUT10) |

Channels 2, 3, 12, and 13 are disabled (tri-state). After programming, `ad9523_sync()` issues a synchronization pulse to align all divider outputs. Cross-reference: [Frequency Synthesis](../02_hardware/03_frequency_synthesis.md) for the complete AD9523-1 clock tree.

#### Step 7: FPGA Power Sequence

The FPGA is powered in ascending voltage order to prevent core damage:

1. Enable 1.0 V core: `EN_P_1V0_FPGA_Pin` (PE7) set HIGH, wait 100 ms
2. Enable 1.8 V auxiliary: `EN_P_1V8_FPGA_Pin` (PE8) set HIGH, wait 100 ms
3. Enable 3.3 V I/O: `EN_P_3V3_FPGA_Pin` (PE9) set HIGH, wait 100 ms

Total step duration: 300 ms. Cross-reference: [Power Management](../02_hardware/06_power_management.md) for FPGA power sequencing requirements.

#### Step 8: IMU Initialization

`GY85_Init()` initializes the GY-85 9-DOF IMU module (ADXL345 accelerometer, ITG-3200 gyroscope, HMC5883L magnetometer) on I2C3. The firmware then runs 10 iterations of a complementary filter to establish a stable orientation estimate before using the yaw angle to point the stepper motor to North (Step 14).

Each iteration reads accelerometer, gyroscope, and magnetometer data, applies bias corrections (`abias[]`, `gbias[]`, `mbias[]`), normalizes the magnetometer vector, and fuses the data using a complementary filter with equal weights (0.5 accelerometer, 0.5 gyroscope). The filter computes pitch $\theta_\text{pitch}$ (`Pitch_Sensor`), roll $\theta_\text{roll}$ (`Roll_Sensor`), and tilt-compensated yaw $\psi_\text{yaw}$ (`Yaw_Sensor`) using Euler angles. A 300 ms delay between iterations allows sensor settling.

Cross-reference: [GPS/IMU Transforms](../02_hardware/09_gps_imu_transforms.md) for the complementary filter equations and coordinate frame definitions.

#### Step 9: Barometer Calibration

Five iterations of `myBMP.getPressure()` read the BMP180 barometric pressure sensor. Each reading computes the radar altitude $h_\text{radar}$ (`RADAR_Altitude`) using the barometric formula. A 100 ms delay between readings allows ADC settling. The BMP180 is configured in ultra-high-resolution mode (`BMP180_ULTRAHIGHRES`, 8x oversampling, 12 uA power consumption).

#### Step 10: ADF4382 LO Initialization

`ADF4382A_Manager_Init(&lo_manager, SYNC_METHOD_TIMED)` initializes both TX and RX local oscillator synthesizers (ADF4382A) on SPI4. After initialization, phase shifts are applied (500 ps for both TX and RX) and strobed to take effect. The firmware then polls the lock detect pins (`ADF4382_TX_LKDET_Pin` = PG11, `ADF4382_RX_LKDET_Pin` = PG6) with 100 ms intervals, up to 100 attempts (10 seconds maximum). Once both LOs achieve lock, `ADF4382A_TriggerTimedSync()` issues a synchronization pulse using the phase-aligned 60 MHz clocks from AD9523 channels OUT8/OUT9. LED1 (PF12) and LED2 (PF13) indicate TX and RX lock status respectively.

Cross-reference: [Frequency Synthesis](../02_hardware/03_frequency_synthesis.md) for the ADF4382A PLL architecture and phase noise specifications.

#### Step 11: ADAR1000 Power and Initialization

The ADAR1000 beamformer power-up sequence:

1. Disable RF mixers: PD11 set LOW (prevents RF transmission during ADAR1000 init)
2. Enable 3.3 V for ADAR1000 #1--2: `EN_P_3V3_ADAR12_Pin` (PE11) set HIGH
3. Enable 3.3 V for ADAR1000 #3--4: `EN_P_3V3_ADAR34_Pin` (PE12) set HIGH
4. Wait 500 ms for supply stabilization
5. Enable 5.0 V for all ADAR1000: `EN_P_5V0_ADAR_Pin` (PE10) set HIGH
6. Wait 500 ms for supply stabilization
7. `systemPowerUpSequence()` executes:
   - `initializeADTR1107Sequence()` -- ADTR1107 T/R module power-up
   - `initializeAllDevices()` -- all 4 ADAR1000 devices initialized via SPI1
   - `performSystemCalibration()` -- system-level calibration
   - `setAllDevicesTXMode()` -- set to safe TX mode

Cross-reference: [Antenna and Beamforming](../02_hardware/04_antenna_beamforming.md) for the ADAR1000 register map and SPI protocol.

#### Step 12: Beam Matrix Initialization

`initializeBeamMatrices()` pre-computes the phase settings for all $N_\text{el} = 31$ (`n_max`) elevation beam positions across all $N = 16$ antenna elements. The phase difference array $\Delta\phi_n$ (`phase_differences[31]` in `main.cpp`) stores the inter-element phase shift in degrees for each beam position. The function computes three data structures:

- **`matrix1[15][16]`**: Positions 1--15 (positive phase shifts, $\Delta\phi > 0$). Each entry is a 7-bit phase code for the ADAR1000 phase register.
- **`vector_0[16]`**: Position 16 (broadside, $\Delta\phi = 0$). All elements set to zero phase.
- **`matrix2[15][16]`**: Positions 17--31 (negative phase shifts, $\Delta\phi < 0$).

The conversion from degrees to 7-bit phase code is performed by `degreesTo7BitPhase()`: the input angle is normalized to $[0, 360)$ degrees, then mapped to a 7-bit integer $[0, 127]$ via $\text{code} = \lfloor(\phi / 360) \times 128\rfloor \bmod 128$. See Section 5 for the derivation of the `phase_differences` array.

#### Step 13: GPS Acquisition

Ten iterations of `smartDelay(1000)` feed the TinyGPS++ parser with NMEA data from UART5 for 1 second each. After the loop, `RADAR_Longitude` and `RADAR_Latitude` store the averaged GPS fix. `smartDelay()` is a non-blocking delay that continuously reads UART5 bytes and passes them to `gps.encode()` during the wait period.

#### Step 14: Point Stepper to North

The stepper motor is rotated to align the antenna array with magnetic North, corrected by the magnetic declination $\delta_\text{mag}$ (`Mag_Declination` in `main.cpp`). The rotation direction is set to counter-clockwise (CCW) via `STEPPER_CW_P_Pin` (PD4) = LOW. The number of steps is calculated from the current IMU yaw angle:

$$
n_\text{steps} = \left\lfloor \frac{\psi_\text{yaw} \times S_\text{rev}}{360} \right\rfloor \tag{SW-20}
$$

where $S_\text{rev}$ (`Stepper_steps` in `main.cpp`) is the number of steps per revolution (see [Parameter Table](../00_notation/parameter_table.md#system-level-derivedtbd)). Each step generates a 500 us HIGH / 500 us LOW pulse on `STEPPER_CLK_P_Pin` (PD5).

#### Step 15: GPS Data to GUI and Wait for Start

`GPS_SendBinaryToGUI(&gps_data)` transmits a binary packet containing latitude, longitude, altitude, pitch, and timestamp over USB CDC to the host GUI application. The firmware then enters a polling loop on `usbHandler.isStartFlagReceived()`, waiting for the operator to press the start button in the GUI. The `RadarSettings` structure received from the GUI contains system frequency, chirp durations, PRF values, and maximum distance parameters.

#### Step 16: PA Power-Up (Conditional)

When the `PowerAmplifier` flag is set (compiled as `#define PowerAmplifier 1`), the QPA2962 GaN power amplifier bias sequence executes:

1. **DAC initialization**: Two DAC5578 8-bit DACs on I2C1 (addresses 0x48 and 0x49) are initialized with clear-to-zero behavior and simultaneous LDAC update mode.
2. **Set gate voltage**: All 16 PA channels are set to the initial DAC code $N_\text{DAC}$ (`DAC_val` in `main.cpp`). See Section 5 for the derivation of $N_\text{DAC} = 126$.
3. **Enable drain supply**: `EN_DIS_RFPA_VDD_Pin` (PD6) set HIGH, enabling the 22 V drain supply.
4. **Initialize current monitors**: Two ADS7830 8-bit ADCs on I2C2 (addresses 0x48 and 0x4A) are initialized for single-ended measurement with internal reference.
5. **Idq tuning loop**: For each of the 16 PA channels, the firmware iteratively reduces the DAC code in steps of 4 (increasing the negative gate voltage) while monitoring the drain quiescent current $I_{dq}$ (`Idq_reading[]`) until it reaches the target value. See Section 5 for the $I_{dq}$ derivation.

Cross-reference: [Power Management](../02_hardware/06_power_management.md) for the PA bias circuit topology and [Power Budget](../02_hardware/08_power_budget.md) for PA power dissipation.

#### Step 17: FPGA Reset and Enable Mixers

1. **FPGA reset**: PD12 toggled LOW for 10 ms then HIGH, issuing an active-low reset to the FPGA to clear all internal state and synchronize with the newly configured clock tree.
2. **Enable mixers**: PD11 (`stm32_mixers_enable`) set HIGH, commanding the FPGA to enable the LT5552 RF mixers for signal transmission and reception.

After Step 17, the firmware enters the main radar loop.

---

## 3. Peripheral Configuration Tables

### 3.1 I2C Device Address Table

| Device | I2C Bus | 7-bit Address | GPIO (LDAC/CLR) | Purpose |
|--------|---------|---------------|-----------------|---------|
| DAC5578 #1 | I2C1 | 0x48 | PB5 (LDAC), PB4 (CLR) | PA gate voltage $V_g$ control, channels 1--8 |
| DAC5578 #2 | I2C1 | 0x49 | PB9 (LDAC), PB8 (CLR) | PA gate voltage $V_g$ control, channels 9--16 |
| ADS7830 #1 | I2C2 | 0x48 | -- | PA drain current $I_{dq}$ monitoring, channels 1--8 |
| ADS7830 #2 | I2C2 | 0x4A | -- | PA drain current $I_{dq}$ monitoring, channels 9--16 |
| ADS7830 #3 | I2C2 | 0x49 | -- | Temperature sensors (TMP37 x 8) |
| GY-85 IMU | I2C3 | default | PC6 (MAG_DRDY), PC7 (ACC_INT), PC8 (GYR_INT) | Accelerometer, gyroscope, magnetometer |
| BMP180 | I2C3 | default (0x77) | -- | Barometric pressure / altitude |

### 3.2 SPI Device Configuration Table

| Device | SPI Bus | CS Pin | Port | Speed | Mode | Purpose |
|--------|---------|--------|------|-------|------|---------|
| ADAR1000 #1 | SPI1 | `ADAR_1_CS_3V3_Pin` | PA0 | -- | -- | Beamformer IC #1 (elements 1--4) |
| ADAR1000 #2 | SPI1 | `ADAR_2_CS_3V3_Pin` | PA1 | -- | -- | Beamformer IC #2 (elements 5--8) |
| ADAR1000 #3 | SPI1 | `ADAR_3_CS_3V3_Pin` | PA2 | -- | -- | Beamformer IC #3 (elements 9--12) |
| ADAR1000 #4 | SPI1 | `ADAR_4_CS_3V3_Pin` | PA3 | -- | -- | Beamformer IC #4 (elements 13--16) |
| AD9523-1 | SPI4 | `AD9523_CS_Pin` | PF7 | 10 MHz | Mode 0 | Clock generator |
| ADF4382 TX | SPI4 | `ADF4382_TX_CS_Pin` | PG14 | -- | -- | TX local oscillator synthesizer |
| ADF4382 RX | SPI4 | `ADF4382_RX_CS_Pin` | PG10 | -- | -- | RX local oscillator synthesizer |

### 3.3 UART Configuration

| Peripheral | Instance | Purpose |
|-----------|----------|---------|
| UART5 | `huart5` | GPS receiver NMEA input (TinyGPS++ parser) |
| USART3 | `huart3` | Debug console output (status messages, error reports) |

---

## 4. Main Radar Loop

After initialization, the firmware enters an infinite `while(1)` loop (line 1705) that alternates between system health monitoring and radar pulse sequencing.

### 4.1 Loop Structure

```
while(1) {
    1. System health check (checkSystemHealthStatus)
    2. LO lock status monitor (every 5 s)
    3. Temperature sensor monitor (every 5 s)
    4. Radar pulse sequence (runRadarPulseSequence)
}
```

### 4.2 System Health Check

`checkSystemHealthStatus()` runs `checkSystemHealth()` which polls nine subsystem health indicators:

| Check | Interval | Condition | Error Code |
|-------|----------|-----------|------------|
| AD9523 clock status | 5 s | STATUS0 or STATUS1 pin LOW | `ERROR_AD9523_CLOCK` |
| ADF4382 lock detect | Each call | TX or RX lock lost | `ERROR_ADF4382_TX/RX_UNLOCK` |
| ADAR1000 communication | Each call | SPI verify fails for any of 4 devices | `ERROR_ADAR1000_COMM` |
| ADAR1000 temperature | Each call | Any device > 85 C | `ERROR_ADAR1000_TEMP` |
| IMU data validity | 10 s | NaN in accelerometer readings | `ERROR_IMU_COMM` |
| BMP180 pressure range | 15 s | Pressure outside 30--110 kPa or NaN | `ERROR_BMP180_COMM` |
| GPS fix age | 30 s | No GPS update in 30 s | `ERROR_GPS_COMM` |
| PA drain current | Each call | Any $I_{dq} > 2.5$ A (overcurrent) or $I_{dq} < 0.1$ A (bias fault) | `ERROR_RF_PA_OVERCURRENT/BIAS` |
| System temperature | Each call | Temperature > 75 C | `ERROR_TEMPERATURE_HIGH` |

**Critical errors** (`ERROR_RF_PA_OVERCURRENT` through `ERROR_POWER_SUPPLY`) trigger `Emergency_Stop()`, which activates the DAC5578 hardware CLR pins to immediately zero all PA gate voltages, then enters an infinite halt loop. **Non-critical errors** trigger `attemptErrorRecovery()` which re-initializes the failed subsystem. After 10 cumulative errors, the system enters safe mode (mixers disabled, power-down sequence, LED blink pattern).

### 4.3 Temperature Monitoring

Every 5 seconds, the firmware reads 8 TMP37 analog temperature sensors via ADS7830 #3 (I2C2, address 0x49). The temperature conversion uses the TMP37 transfer function:

$$
T_\text{sensor} = \frac{N_\text{ADC} \times 165}{255} \tag{SW-21}
$$

where $N_\text{ADC}$ is the 8-bit ADC reading and the factor 165/255 = 0.64705 accounts for the TMP37 output range (3.3 V full scale corresponds to 165 C). If any sensor exceeds 25 C (the `Max_Temp` threshold), the cooling system is enabled via `EN_DIS_COOLING_Pin` (PD7).

### 4.4 Radar Pulse Sequence

`runRadarPulseSequence()` executes one complete azimuth position, consisting of elevation beam sweeps and stepper motor advancement.

#### 4.4.1 Elevation Sweep

For each of $N_\text{el} = 31$ beam elevation positions, the firmware:

1. **Toggles `stm32_new_elevation`** (PD9) to notify the FPGA of an elevation change
2. **Sets beam phase pattern** via SPI1 to all 4 ADAR1000 devices for both TX and RX paths
3. **Executes chirp sequence** (`executeChirpSequence()`)

The beam steering pattern cycles through three sub-patterns per elevation step:
- **Positive steering** (from `matrix1`): $m_\text{max}/2 = 16$ chirps
- **Broadside** (from `vector_0`): $m_\text{max}/2 = 16$ chirps
- **Negative steering** (from `matrix2`): $m_\text{max}/2 = 16$ chirps

#### 4.4.2 Chirp Sequencing

`executeChirpSequence()` generates the dual-chirp waveform for each beam position. Each call produces two chirp bursts separated by a guard interval:

**Long chirp burst** ($M/2$ chirps at microsecond timing):
- For each chirp: toggle `stm32_new_chirp` (PD8), pulse TX mode, wait $T_{c,1}$ (`T1`), pulse RX mode, wait $T_{r,1} - T_{c,1}$ (`PRI1 - T1`)
- Uses `delay_us()` (TIM1-based, 1 us resolution)

**Guard interval**: wait $T_\text{guard}$ (`Guard`) via `delay_us()`

**Short chirp burst** ($M/2$ chirps at nanosecond timing):
- For each chirp: toggle `stm32_new_chirp` (PD8), pulse TX mode, wait $T_{c,2}$ (`T2`), pulse RX mode, wait $T_{r,2} - T_{c,2}$ (`PRI2 - T2`)
- Uses `delay_ns()` (DWT cycle counter, sub-microsecond resolution)

#### 4.4.3 FPGA Handshake Signals

| Signal | GPIO Pin | Direction | Trigger |
|--------|----------|-----------|---------|
| `stm32_new_chirp` | PD8 | STM32 to FPGA | Toggled at the start of each chirp (both long and short) |
| `stm32_new_elevation` | PD9 | STM32 to FPGA | Toggled on each elevation beam position change |
| `stm32_new_azimuth` | PD10 | STM32 to FPGA | Toggled after completing all elevation positions at one azimuth |
| `stm32_mixers_enable` | PD11 | STM32 to FPGA | HIGH = mixers enabled, LOW = mixers disabled (safe mode) |
| FPGA reset | PD12 | STM32 to FPGA | Active-low reset pulse during initialization |

#### 4.4.4 Azimuth Advancement

After completing all elevation positions, the firmware:

1. Toggles `stm32_new_azimuth` (PD10) to notify the FPGA
2. Increments the azimuth counter $y$ (wraps at $N_\text{az}$)
3. Steps the stepper motor to the next azimuth position by generating $S_\text{rev}/N_\text{az}$ step pulses (see Eq. (SW-24) in Section 5)

Each stepper step is a 500 us HIGH / 500 us LOW pulse on `STEPPER_CLK_P_Pin` (PD5), giving a step period of 1 ms.

---

## 5. Magic Number Derivations

Every hardcoded numerical constant in the firmware is derived below from physics principles or component specifications. Per [conventions.md anti-pattern 5.4](../00_notation/conventions.md), each firmware variable name is paired with its standard symbol.

### 5.1 Long Chirp PRI

The long chirp PRI $T_{r,1}$ (`PRI1` in `main.cpp`) is the sum of the long chirp duration $T_{c,1}$ and the processing/settling time between chirps:

$$
T_{r,1} = T_{c,1} + t_\text{processing} = 30 + 137 = 167~\mu\text{s} \tag{SW-22}
$$

where $T_{c,1}$ (`T1` in `main.cpp`) is the long chirp duration and $t_\text{processing} = 137~\mu\text{s}$ is the time allocated for FPGA data acquisition, ADC settling, and SPI beam updates between chirps. Cross-reference: [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing) for canonical timing values and [FMCW Theory Eq. (FMCW-5)](../01_physics/01_fmcw_theory.md) for the PRI definition.

### 5.2 Guard Time

The guard time $T_\text{guard}$ (`Guard` in `main.cpp`) separates the long chirp burst from the short chirp burst within a single beam position dwell:

$$
T_\text{guard} = 175.4~\mu\text{s} \tag{SW-23}
$$

This value provides sufficient time for the FPGA matched filter pipeline to flush the long chirp data and reconfigure for the short chirp processing mode. The guard must exceed the matched filter pipeline latency to prevent inter-burst interference. Cross-reference: [Timing Budget](../02_hardware/07_timing_budget.md) for FPGA pipeline latency analysis.

### 5.3 Phase Differences Array

The inter-element phase shift array $\Delta\phi_n$ (`phase_differences[31]` in `main.cpp`) defines 31 elevation beam positions. Each value is the phase difference in degrees applied between adjacent antenna elements to steer the beam to elevation angle $\theta_n$.

The fundamental beam steering equation with half-wavelength element spacing $d = \lambda/2$ simplifies to:

$$
\Delta\phi = \frac{2\pi d \sin\theta}{\lambda} = \frac{2\pi \cdot (\lambda/2) \cdot \sin\theta}{\lambda} = \pi \sin\theta \tag{SW-24}
$$

Converting to degrees:

$$
\Delta\phi_\text{deg} = 180 \sin\theta \tag{SW-25}
$$

The inverse relation gives the steering angle from the phase difference:

$$
\theta = \arcsin\!\left(\frac{\Delta\phi_\text{deg}}{180}\right) \tag{SW-26}
$$

The 31 values in `phase_differences[]` are arranged symmetrically around broadside ($\Delta\phi = 0$ at index 15), with positive values (indices 0--14) steering to one side and negative values (indices 16--30) steering to the other:

| Index | $\Delta\phi_n$ (deg) | Steering angle $\theta$ (deg) |
|-------|---------------------|-------------------------------|
| 0 | +160.0 | +62.7 |
| 1 | +80.0 | +26.4 |
| 2 | +53.333 | +17.2 |
| 3 | +40.0 | +12.8 |
| ... | ... | ... |
| 14 | +10.667 | +3.4 |
| 15 | 0.0 | 0.0 (broadside) |
| 16 | -10.667 | -3.4 |
| ... | ... | ... |
| 29 | -80.0 | -26.4 |
| 30 | -160.0 | -62.7 |

The pattern follows $\Delta\phi_n = 160/n$ for positions 1--15 (e.g., 160, 80, 53.33, 40, 32, ...) and the negative mirror for positions 17--31. This provides finer angular resolution near broadside and coarser resolution at extreme scan angles.

The 7-bit phase code written to the ADAR1000 phase register is computed by `degreesTo7BitPhase()`:

$$
\text{code}_n = \left\lfloor \frac{\phi_\text{cumulative}}{360} \times 128 \right\rfloor \bmod 128 \tag{SW-27}
$$

where $\phi_\text{cumulative} = k \times \Delta\phi_n$ is the cumulative phase for element $k$ at beam position $n$. The ADAR1000 phase register has 7-bit resolution (2.8125 degrees per step). Cross-reference: [Beamforming Theory Eq. (BF-1)](../01_physics/03_beamforming_theory.md) for the array factor phase term and [Antenna and Beamforming](../02_hardware/04_antenna_beamforming.md) for the ADAR1000 phase register format.

### 5.4 DAC Gate Voltage Code

The PA gate voltage DAC code $N_\text{DAC}$ (`DAC_val` in `main.cpp`) sets the quiescent gate voltage $V_g$ for the QPA2962 GaN power amplifiers via a DAC5578 driving an inverting op-amp:

The DAC output voltage is:

$$
V_\text{DAC} = \frac{N_\text{DAC}}{255} \times V_\text{ref} = \frac{126}{255} \times 3.3 \approx 1.631~\text{V} \tag{SW-28}
$$

The inverting op-amp converts this to a negative gate voltage:

$$
V_g \approx -3.98~\text{V} \tag{SW-29}
$$

This initial gate voltage biases the QPA2962 near pinch-off. The Idq tuning loop (Step 16) then adjusts $N_\text{DAC}$ downward in steps of 4 (making $V_g$ more negative) until the measured drain current converges to the target.

### 5.5 Quiescent Drain Current Target

The target quiescent drain current $I_{dq,\text{target}}$ (`1.680` in the Idq tuning loop) is the recommended Class AB bias point for the QPA2962 GaN MMIC power amplifier:

$$
I_{dq,\text{target}} = 1.680~\text{A} \tag{SW-30}
$$

This value is sourced from the QPA2962 datasheet typical operating conditions. The drain current is measured by the ADS7830 ADC through an INA241A3 current sense amplifier ($G = 50$ V/V) and a 5 mohm shunt resistor:

$$
I_{dq} = \frac{V_\text{ADC}}{G \times R_\text{shunt}} = \frac{(3.3/255) \times N_\text{ADC}}{50 \times 0.005} \tag{SW-31}
$$

Cross-reference: [Power Budget](../02_hardware/08_power_budget.md) for PA power dissipation calculations.

### 5.6 Stepper Steps per Azimuth Position

The number of stepper motor steps between adjacent azimuth positions is derived from the motor steps per revolution $S_\text{rev}$ (`Stepper_steps` in `main.cpp`) and the number of azimuth positions $N_\text{az}$ (`y_max`):

$$
n_\text{step/az} = \frac{S_\text{rev}}{N_\text{az}} = \frac{200}{50} = 4~\text{steps per position} \tag{SW-32}
$$

Each step rotates the antenna array by $360/200 = 1.8$ degrees. Four steps yield $7.2$ degrees of azimuth rotation per position, giving full 360-degree coverage over $N_\text{az} = 50$ positions. See [Parameter Table](../00_notation/parameter_table.md#system-level-derivedtbd) for the canonical stepper motor specifications.

---

## 6. GPIO Pin Map

The complete GPIO pin map from `main.h`, grouped by subsystem.

### 6.1 Power Control

| Pin | Port | Define Name | Purpose |
|-----|------|-------------|---------|
| PE7 | GPIOE | `EN_P_1V0_FPGA_Pin` | FPGA 1.0 V core supply enable |
| PE8 | GPIOE | `EN_P_1V8_FPGA_Pin` | FPGA 1.8 V auxiliary supply enable |
| PE9 | GPIOE | `EN_P_3V3_FPGA_Pin` | FPGA 3.3 V I/O supply enable |
| PE10 | GPIOE | `EN_P_5V0_ADAR_Pin` | ADAR1000 5.0 V supply enable |
| PE11 | GPIOE | `EN_P_3V3_ADAR12_Pin` | ADAR1000 #1--2 3.3 V supply enable |
| PE12 | GPIOE | `EN_P_3V3_ADAR34_Pin` | ADAR1000 #3--4 3.3 V supply enable |
| PE13 | GPIOE | `EN_P_3V3_ADTR_Pin` | ADTR1107 T/R module 3.3 V supply enable |
| PE14 | GPIOE | `EN_P_3V3_SW_Pin` | RF switch 3.3 V supply enable |
| PE15 | GPIOE | `EN_P_3V3_VDD_SW_Pin` | RF switch VDD supply enable |
| PG0 | GPIOG | `EN_P_5V0_PA1_Pin` | PA bank 1 5.0 V supply enable |
| PG1 | GPIOG | `EN_P_5V0_PA2_Pin` | PA bank 2 5.0 V supply enable |
| PG2 | GPIOG | `EN_P_5V0_PA3_Pin` | PA bank 3 5.0 V supply enable |
| PG3 | GPIOG | `EN_P_5V5_PA_Pin` | PA 5.5 V supply enable |
| PG4 | GPIOG | `EN_P_1V8_CLOCK_Pin` | Clock generator 1.8 V supply enable |
| PG5 | GPIOG | `EN_P_3V3_CLOCK_Pin` | Clock generator 3.3 V supply enable |
| PD6 | GPIOD | `EN_DIS_RFPA_VDD_Pin` | RF PA drain supply (22 V) enable |
| PD7 | GPIOD | `EN_DIS_COOLING_Pin` | Cooling system enable |

### 6.2 SPI Chip Select

| Pin | Port | Define Name | Purpose |
|-----|------|-------------|---------|
| PA0 | GPIOA | `ADAR_1_CS_3V3_Pin` | ADAR1000 #1 chip select |
| PA1 | GPIOA | `ADAR_2_CS_3V3_Pin` | ADAR1000 #2 chip select |
| PA2 | GPIOA | `ADAR_3_CS_3V3_Pin` | ADAR1000 #3 chip select |
| PA3 | GPIOA | `ADAR_4_CS_3V3_Pin` | ADAR1000 #4 chip select |
| PF7 | GPIOF | `AD9523_CS_Pin` | AD9523-1 clock generator chip select |
| PG10 | GPIOG | `ADF4382_RX_CS_Pin` | ADF4382 RX LO chip select |
| PG14 | GPIOG | `ADF4382_TX_CS_Pin` | ADF4382 TX LO chip select |

### 6.3 AD9523 Clock Generator Control

| Pin | Port | Define Name | Purpose |
|-----|------|-------------|---------|
| PF3 | GPIOF | `AD9523_PD_Pin` | Power-down control |
| PF4 | GPIOF | `AD9523_REF_SEL_Pin` | Reference select (REFA/REFB) |
| PF5 | GPIOF | `AD9523_SYNC_Pin` | Synchronization pulse output |
| PF6 | GPIOF | `AD9523_RESET_Pin` | Active-low reset |
| PF8 | GPIOF | `AD9523_STATUS0_Pin` | Lock/status indicator 0 (input) |
| PF9 | GPIOF | `AD9523_STATUS1_Pin` | Lock/status indicator 1 (input) |
| PF10 | GPIOF | `AD9523_EEPROM_SEL_Pin` | EEPROM access select |

### 6.4 ADF4382 LO Control

| Pin | Port | Define Name | Purpose |
|-----|------|-------------|---------|
| PG6 | GPIOG | `ADF4382_RX_LKDET_Pin` | RX LO lock detect (input) |
| PG7 | GPIOG | `ADF4382_RX_DELADJ_Pin` | RX delay adjust |
| PG8 | GPIOG | `ADF4382_RX_DELSTR_Pin` | RX delay strobe |
| PG9 | GPIOG | `ADF4382_RX_CE_Pin` | RX chip enable |
| PG11 | GPIOG | `ADF4382_TX_LKDET_Pin` | TX LO lock detect (input) |
| PG12 | GPIOG | `ADF4382_TX_DELSTR_Pin` | TX delay strobe |
| PG13 | GPIOG | `ADF4382_TX_DELADJ_Pin` | TX delay adjust |
| PG15 | GPIOG | `ADF4382_TX_CE_Pin` | TX chip enable |

### 6.5 FPGA Control

| Pin | Port | Signal Name | Purpose |
|-----|------|-------------|---------|
| PD8 | GPIOD | `stm32_new_chirp` | New chirp edge signal to FPGA |
| PD9 | GPIOD | `stm32_new_elevation` | New elevation position signal |
| PD10 | GPIOD | `stm32_new_azimuth` | New azimuth position signal |
| PD11 | GPIOD | `stm32_mixers_enable` | RF mixer enable/disable |
| PD12 | GPIOD | FPGA reset | Active-low FPGA reset |

### 6.6 Sensors and Peripherals

| Pin | Port | Define Name | Purpose |
|-----|------|-------------|---------|
| PC6 | GPIOC | `MAG_DRDY_Pin` | Magnetometer data ready (input) |
| PC7 | GPIOC | `ACC_INT_Pin` | Accelerometer interrupt (input) |
| PC8 | GPIOC | `GYR_INT_Pin` | Gyroscope interrupt (input) |
| PD4 | GPIOD | `STEPPER_CW_P_Pin` | Stepper motor direction (CW/CCW) |
| PD5 | GPIOD | `STEPPER_CLK_P_Pin` | Stepper motor step clock |

### 6.7 PA DAC Control

| Pin | Port | Define Name | Purpose |
|-----|------|-------------|---------|
| PB4 | GPIOB | `DAC_1_VG_CLR_Pin` | DAC #1 hardware clear (zero all outputs) |
| PB5 | GPIOB | `DAC_1_VG_LDAC_Pin` | DAC #1 load DAC (simultaneous update) |
| PB8 | GPIOB | `DAC_2_VG_CLR_Pin` | DAC #2 hardware clear |
| PB9 | GPIOB | `DAC_2_VG_LDAC_Pin` | DAC #2 load DAC |

### 6.8 Indicators

| Pin | Port | Define Name | Purpose |
|-----|------|-------------|---------|
| PF12 | GPIOF | `LED_1_Pin` | TX LO lock indicator |
| PF13 | GPIOF | `LED_2_Pin` | RX LO lock indicator |
| PF14 | GPIOF | `LED_3_Pin` | Error code blink indicator |
| PF15 | GPIOF | `LED_4_Pin` | General status indicator |

---

## 7. Error Handling

### 7.1 Error Classification

The firmware defines 16 error codes in `SystemError_t`, classified into critical and non-critical categories:

**Critical errors** (trigger emergency shutdown via `Emergency_Stop()`):
- `ERROR_RF_PA_OVERCURRENT` -- any $I_{dq} > 2.5$ A
- `ERROR_RF_PA_BIAS` -- any $I_{dq} < 0.1$ A (channel not biased)
- `ERROR_STEPPER_MOTOR` -- stepper motor fault
- `ERROR_FPGA_COMM` -- FPGA communication failure
- `ERROR_POWER_SUPPLY` -- power supply fault

**Non-critical errors** (trigger recovery attempt):
- `ERROR_AD9523_CLOCK` -- clock generator status pin indicates fault
- `ERROR_ADF4382_TX_UNLOCK` / `ERROR_ADF4382_RX_UNLOCK` -- LO lock lost (recovery: re-init)
- `ERROR_ADAR1000_COMM` -- SPI communication failure (recovery: re-init all devices)
- `ERROR_ADAR1000_TEMP` -- device temperature > 85 C
- `ERROR_IMU_COMM` -- NaN readings (recovery: re-init IMU)
- `ERROR_BMP180_COMM` -- pressure out of range
- `ERROR_GPS_COMM` -- no fix update in 30 s (auto-recovery when signal returns)
- `ERROR_TEMPERATURE_HIGH` -- system temperature > 75 C
- `ERROR_MEMORY_ALLOC` -- memory allocation failure
- `ERROR_WATCHDOG_TIMEOUT` -- software watchdog (60 s timeout)

### 7.2 Emergency Stop

`Emergency_Stop()` is the last line of defense for PA protection. It activates the DAC5578 hardware CLR pins (`DAC_1_VG_CLR_Pin` = PB4, `DAC_2_VG_CLR_Pin` = PB8), which are wired to immediately zero all DAC outputs (gate voltage goes to 0 V, pinching off all PA transistors). The function then enters an infinite loop -- recovery requires a hardware reset.

### 7.3 Safe Mode

If `checkSystemHealthStatus()` returns `false` (emergency state or > 10 cumulative errors), the main loop:
1. Disables mixers (PD11 LOW)
2. Executes `systemPowerDownSequence()` (reverse power-down: RX mode, disable PA supplies, safe bias, disable LNA, disable switches)
3. Enters LED blink loop (all 4 LEDs toggling) indicating safe mode

---

## 8. References

- [Symbol Table](../00_notation/symbol_table.md) -- standard mathematical symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- canonical numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- [FMCW Theory](../01_physics/01_fmcw_theory.md) -- chirp timing and PRI derivations
- [Beamforming Theory](../01_physics/03_beamforming_theory.md) -- array factor and phase steering equations
- [System Overview](../02_hardware/01_system_overview.md) -- AERIS-10 system architecture
- [RF Front-End](../02_hardware/02_rf_frontend.md) -- mixer and PA specifications
- [Frequency Synthesis](../02_hardware/03_frequency_synthesis.md) -- AD9523 and ADF4382 configuration
- [Antenna and Beamforming](../02_hardware/04_antenna_beamforming.md) -- ADAR1000 register map and beam steering
- [Power Management](../02_hardware/06_power_management.md) -- power sequencing and GPIO rail control
- [Timing Budget](../02_hardware/07_timing_budget.md) -- pipeline latency analysis
- [Power Budget](../02_hardware/08_power_budget.md) -- PA power dissipation
- [GPS/IMU Transforms](../02_hardware/09_gps_imu_transforms.md) -- complementary filter and coordinate transforms
