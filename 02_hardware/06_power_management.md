# AERIS-10 Power Management

**Purpose:** Document the complete power management subsystem including voltage rail sequencing, PA gate voltage control, current and temperature monitoring, thermal management, fan control, and emergency stop procedures.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [System Overview](01_system_overview.md) -- system-level power architecture reference

---

## 1. Overview

The AERIS-10 power management subsystem is orchestrated by the STM32F746 microcontroller through three control interfaces:

- **GPIO** -- controls power rail enable pins for sequenced power-up and power-down of all voltage domains
- **I2C (DAC5578)** -- two 8-channel DACs set the gate bias voltage $V_g$ for all 16 power amplifiers
- **I2C (ADS7830)** -- three 8-channel ADCs monitor PA drain current $I_{dq}$ and board temperatures

The power management architecture ensures safe startup through a defined sequencing order (core rails before I/O, clock before FPGA, analog before RF), continuous health monitoring during operation, and immediate shutdown via hardware emergency stop. The system supports autonomous thermal management through temperature-triggered fan control and overcurrent-triggered emergency stop.

---

## 2. Voltage Rails

The system uses ten independently controlled voltage rails, each enabled by a dedicated GPIO pin on the STM32F746. The sequencing order is defined by the firmware startup code (`main.cpp`).

| # | Rail | Voltage | GPIO Enable Pin | Purpose | Sequencing Group |
|---|------|---------|-----------------|---------|------------------|
| 1 | 1.8V Clock | 1.8 V | `EN_P_1V8_CLOCK` | AD9523-1 clock distribution IC (1.8V domain) | Clock |
| 2 | 3.3V Clock | 3.3 V | `EN_P_3V3_CLOCK` | AD9523-1 clock distribution IC (3.3V domain) | Clock |
| 3 | 1.0V FPGA Core | 1.0 V | `EN_P_1V0_FPGA` | XC7A100T Artix-7 core voltage | FPGA |
| 4 | 1.8V FPGA I/O | 1.8 V | `EN_P_1V8_FPGA` | XC7A100T I/O bank voltage | FPGA |
| 5 | 3.3V FPGA | 3.3 V | `EN_P_3V3_FPGA` | XC7A100T auxiliary and configuration | FPGA |
| 6 | 3.3V ADAR1000 (1-2) | 3.3 V | `EN_P_3V3_ADAR12` | ADAR1000 beamformer ICs #1 and #2 | Beamformer |
| 7 | 3.3V ADAR1000 (3-4) | 3.3 V | `EN_P_3V3_ADAR34` | ADAR1000 beamformer ICs #3 and #4 | Beamformer |
| 8 | 5.0V ADAR1000 | 5.0 V | `EN_P_5V0_ADAR` | ADAR1000 PA bias supply | Beamformer |
| 9 | 3.3V ADTR1107 | 3.3 V | `EN_P_3V3_ADTR` | ADTR1107 T/R module supply (Nexus) | RF Front-End |
| 10 | PA VDD | 22 V | `EN_DIS_RFPA_VDD` | External RF power amplifier drain supply | RF Front-End |

Additional GPIO-controlled power pins for the T/R module subsystem:

| Pin | Purpose |
|-----|---------|
| `EN_P_5V0_PA1` | PA bank 1 supply enable |
| `EN_P_5V0_PA2` | PA bank 2 supply enable |
| `EN_P_5V0_PA3` | PA bank 3 supply enable |
| `EN_P_3V3_VDD_SW` | T/R switch VDD supply |
| `EN_P_3V3_SW` | T/R switch control supply |

For canonical voltage and current specifications, see `3_Power Management/Power Management V6.xlsx`. The firmware (`main.cpp`) defines the sequencing order and delays; the spreadsheet contains the electrical specifications for each rail.

---

## 3. Power-On Sequence

The complete power-on sequence is implemented in `main.cpp` (lines 1237--1599) and the `systemPowerUpSequence()` function. The 17-step process proceeds as follows:

| Step | Action | Delay After | Firmware Reference |
|------|--------|-------------|-------------------|
| 1 | Wait for OCXO warm-up | 180 s | `HAL_Delay(180000)` -- L1237 |
| 2 | Assert AD9523 reset (active low) | -- | `AD9523_RESET` -> `GPIO_PIN_RESET` -- L1238 |
| 3 | Enable 1.8V clock rail | 100 ms | `EN_P_1V8_CLOCK` -> SET -- L1241 |
| 4 | Enable 3.3V clock rail | 100 ms | `EN_P_3V3_CLOCK` -> SET -- L1243 |
| 5 | Release AD9523 reset | 100 ms | `AD9523_RESET` -> SET -- L1245 |
| 6 | Configure AD9523 via SPI | -- | `configure_ad9523()` -- L1265 |
| 7 | Enable 1.0V FPGA core | 100 ms | `EN_P_1V0_FPGA` -> SET -- L1271 |
| 8 | Enable 1.8V FPGA I/O | 100 ms | `EN_P_1V8_FPGA` -> SET -- L1273 |
| 9 | Enable 3.3V FPGA | 100 ms | `EN_P_3V3_FPGA` -> SET -- L1275 |
| 10 | Initialize IMU (GY-85 via I2C3) | ~3 s (10 iterations x 300 ms) | `GY85_Init()` + complementary filter -- L1280 |
| 11 | Initialize barometer (BMP180) | ~500 ms (5 iterations x 100 ms) | `myBMP.getPressure()` -- L1391 |
| 12 | Initialize ADF4382 TX/RX LOs, wait for lock | up to 10 s (100 x 100 ms timeout) | `ADF4382A_Manager_Init()` -- L1404 |
| 13 | Enable ADAR1000 3.3V (pairs 1-2 and 3-4) | 500 ms | `EN_P_3V3_ADAR12/34` -> SET -- L1485 |
| 14 | Enable ADAR1000 5.0V | 500 ms | `EN_P_5V0_ADAR` -> SET -- L1488 |
| 15 | ADTR1107 power sequence + ADAR1000 init + calibration | -- | `systemPowerUpSequence()` -- L1496 |
| 16 | Initialize DAC5578 (PA gate bias) + set initial $V_g$ | -- | `DAC5578_Init()` -- L1563 |
| 17 | Initialize ADS7830 (PA current monitoring) + PA bias tuning | -- | `ADS7830_Init()` + Idq loop -- L1603 |

### 3.1 Sequencing Rationale

The sequencing order follows standard FPGA and mixed-signal power-up practice:

1. **OCXO first** (Step 1): The oven-controlled crystal oscillator requires 180 seconds to stabilize frequency. All downstream clocks depend on this reference.
2. **Clock rails before clock IC** (Steps 2--5): The AD9523-1 requires stable 1.8V and 3.3V supplies before reset release.
3. **Clock IC before FPGA** (Step 6): The FPGA requires valid clock signals before configuration.
4. **FPGA core before I/O** (Steps 7--9): Xilinx Artix-7 requires $V_\text{CCINT}$ (1.0V) before $V_\text{CCAUX}$ (1.8V) before $V_\text{CCO}$ (3.3V) per datasheet sequencing requirements.
5. **Sensors before RF** (Steps 10--11): IMU and barometer initialization must complete before the main radar loop begins.
6. **LO lock before beamformer** (Step 12): Frequency synthesizers must achieve phase lock before RF signal path is activated.
7. **Beamformer before PA** (Steps 13--17): ADAR1000 analog supplies must be stable before enabling the power amplifiers to prevent uncontrolled RF emission.

### 3.2 Clock Tree Setup (Step 6)

The AD9523-1 clock tree configuration establishes all system clocks from the 3.6 GHz VCO. See [System Overview -- Clock Domain Overview](01_system_overview.md#4-clock-domain-overview) for the complete clock tree, including Eq. (HW-SYS-1) through Eq. (HW-SYS-3).

For frequency synthesis (ADF4382 TX/RX LO) details initiated in Step 12, see [`03_frequency_synthesis.md`](03_frequency_synthesis.md).

---

## 4. Power-Down Sequence

The power-down sequence is implemented in `systemPowerDownSequence()` (`main.cpp`, lines 372--410). It reverses the power-on order, disabling RF stages first for safety:

| Step | Action | Delay After | Firmware Reference |
|------|--------|-------------|-------------------|
| 1 | Set all ADAR1000 devices to RX mode (safe state) | 10 ms | `setAllDevicesRXMode()` -- L377 |
| 2 | Disable PA power supplies (all three banks) | 10 ms | `EN_P_5V0_PA1/2/3` -> RESET -- L381 |
| 3 | Set PA biases to safe values (0x20 on all channels) | 10 ms | `REG_PA_CHx_BIAS_ON` = 0x20 -- L385 |
| 4 | Disable LNA power supply | 10 ms | `EN_P_3V3_ADTR` -> RESET -- L394 |
| 5 | Set LNA bias to zero | 10 ms | `REG_LNA_BIAS_ON` = 0x00 -- L398 |
| 6 | Disable switch power supplies | 10 ms | `EN_P_3V3_VDD_SW`, `EN_P_3V3_SW` -> RESET -- L404 |

The power-down sequence is automatically triggered when the system health monitor detects a critical fault (error count exceeds 10 or emergency state is set). Before power-down, the firmware disables the RF mixer path by resetting GPIO PD11, preventing any RF transmission during shutdown.

---

## 5. PA Gate Voltage Control

### 5.1 DAC5578 Configuration

Two Texas Instruments DAC5578 8-bit, 8-channel DACs control the gate bias voltage $V_g$ for all 16 power amplifiers. Each DAC channel drives one PA element through an inverting op-amp circuit.

| DAC | I2C Bus | I2C Address | Channels | PA Elements |
|-----|---------|-------------|----------|-------------|
| `hdac1` | I2C1 | 0x48 | 0--7 | PA 1--8 |
| `hdac2` | I2C1 | 0x49 | 0--7 | PA 9--16 |

**Key features used:**
- `DAC5578_CMD_WRITE_UPDATE` (0x20): Write and immediately update output
- Hardware LDAC pins for simultaneous multi-channel update
- Hardware CLR pins for emergency stop (see Section 8)
- Clear code configured to zero-scale (`DAC5578_CLR_CODE_ZERO`): CLR pin activation drives all outputs to 0V

### 5.2 Voltage-to-Code Conversion

The DAC5578 output voltage is:

$$
V_\text{DAC} = \frac{D}{2^8 - 1} \times V_\text{ref} \tag{HW-PWR-1}
$$

where $D$ is the 8-bit digital code (0--255) and $V_\text{ref}$ is the DAC reference voltage.

The op-amp inverting stage converts $V_\text{DAC}$ to the PA gate voltage $V_g$. The firmware comment indicates that a DAC code of 126 corresponds to a gate voltage of $V_g = -3.98~\text{V}$ (op-amp input $= 1.63058~\text{V}$), establishing the initial bias point.

### 5.3 PA Bias Tuning Procedure

After initial DAC setup, the firmware performs an automated bias tuning loop for each PA element (`main.cpp`, lines 1628--1656):

1. Start at DAC code 126 (most negative $V_g$, PA pinched off)
2. Decrease DAC code by 4 per iteration (increasing $V_g$ toward zero, opening the PA)
3. Read drain current $I_{dq}$ via ADS7830
4. Continue until $I_{dq}$ deviates from the target quiescent point ($1.680~\text{A}$) by more than $0.2~\text{A}$, or DAC code reaches minimum (38)
5. Safety counter limits to 50 iterations maximum

This procedure sets each PA to its optimal quiescent operating point, compensating for device-to-device variation.

---

## 6. Current and Temperature Monitoring

### 6.1 ADS7830 ADC Configuration

Three Texas Instruments ADS7830 8-bit, 8-channel ADCs provide continuous monitoring of PA drain current and board temperatures.

| ADC | I2C Bus | I2C Address | Mode | Function |
|-----|---------|-------------|------|----------|
| `hadc1` | I2C2 | 0x48 | Single-ended, internal ref ON | PA 1--8 drain current ($I_{dq}$) |
| `hadc2` | I2C2 | 0x4A | Single-ended, internal ref ON | PA 9--16 drain current ($I_{dq}$) |
| `hadc3` | I2C2 | 0x49 | Single-ended, internal ref ON | 8 temperature sensors (TMP37) |

### 6.2 ADC-to-Current Conversion

The PA drain current $I_{dq}$ is measured through a current sense resistor with an INA241A3 current sense amplifier. The ADC reading maps to current by:

$$
I_{dq} = \frac{V_\text{ADC}}{G \times R_\text{shunt}} = \frac{\displaystyle\frac{3.3}{255} \times D_\text{ADC}}{50 \times 0.005} \tag{HW-PWR-2}
$$

where:
- $D_\text{ADC}$ is the 8-bit ADC reading (0--255)
- $V_\text{ref} = 3.3~\text{V}$ is the ADC reference voltage
- $G = 50~\text{V/V}$ is the INA241A3 gain (`G_INA241A3=50` in firmware)
- $R_\text{shunt} = 5~\text{m}\Omega$ is the current sense resistor (`Rshunt=5mOhms` in firmware)

Simplifying:

$$
I_{dq} = \frac{3.3 \times D_\text{ADC}}{255 \times 0.25} = \frac{D_\text{ADC}}{19.318} \tag{HW-PWR-3}
$$

### 6.3 Monitoring Thresholds

The firmware (`checkSystemHealth()` in `main.cpp`, lines 650--661) checks each PA element against the following thresholds:

| Condition | Threshold | Error Code | Severity |
|-----------|-----------|------------|----------|
| Overcurrent | $I_{dq} > 2.5~\text{A}$ | `ERROR_RF_PA_OVERCURRENT` | Critical -- triggers `Emergency_Stop()` |
| Under-bias (bias fault) | $I_{dq} < 0.1~\text{A}$ | `ERROR_RF_PA_BIAS` | Critical -- triggers `Emergency_Stop()` |

Both conditions trigger the emergency stop procedure (Section 8) via the `handleSystemError()` function, which calls `Emergency_Stop()` for any error code in the range `ERROR_RF_PA_OVERCURRENT` through `ERROR_POWER_SUPPLY`.

---

## 7. Thermal Management

### 7.1 Temperature Monitoring

Eight TMP37 analog temperature sensors are read via `hadc3` (ADS7830 at I2C address 0x49). The TMP37 has a linear output of 20 mV/C with a 3.3V supply range corresponding to 165C full-scale.

The ADC-to-temperature conversion is:

$$
T = D_\text{ADC} \times \frac{165}{255} \approx D_\text{ADC} \times 0.64705 \tag{HW-PWR-4}
$$

where $T$ is temperature in degrees Celsius and $D_\text{ADC}$ is the 8-bit ADC reading. The firmware reads all 8 sensors every 5 seconds (`main.cpp`, lines 1751--1775).

### 7.2 Temperature Thresholds

| Component | Threshold | Action | Firmware Reference |
|-----------|-----------|--------|-------------------|
| ADAR1000 (on-chip sensor) | $> 85~\text{C}$ | Error: `ERROR_ADAR1000_TEMP` | `readTemperature()` -- L614 |
| System board (TMP37) | $> 25~\text{C}$ (active cooling threshold) | Fan ON | Temperature loop -- L1764 |
| System (general) | $> 75~\text{C}$ | Error: `ERROR_TEMPERATURE_HIGH` | `checkSystemHealth()` -- L664 |

The ADAR1000 has an internal temperature sensor read via SPI (`readTemperature()` in `ADAR1000_Manager`). The QPA2962 operating temperature range is specified as $-40~\text{C}$ to $+85~\text{C}$ (base plate).

### 7.3 Fan Control

Active cooling is controlled by the `EN_DIS_COOLING` GPIO pin:

- **Fan ON:** `EN_DIS_COOLING` -> `GPIO_PIN_SET` when any TMP37 sensor exceeds the active cooling threshold
- **Fan OFF:** `EN_DIS_COOLING` -> `GPIO_PIN_RESET` when all sensors are below threshold

The fan control operates on the same 5-second polling cycle as the temperature monitoring.

### 7.4 Thermal Dissipation

The junction temperature of a power-dissipating component is estimated by:

$$
T_\text{junction} = T_\text{ambient} + P_\text{diss} \times \theta_{JA} \tag{HW-PWR-5}
$$

where $P_\text{diss}$ is the component power dissipation (defined in the [Symbol Table](../00_notation/symbol_table.md#hardware-and-power)) and $\theta_{JA}$ is the junction-to-ambient thermal resistance. For per-subsystem power dissipation values, see [`08_power_budget.md`](08_power_budget.md).

---

## 8. Emergency Stop

The `Emergency_Stop()` function (`main.cpp`, lines 722--731) provides an immediate hardware-level shutdown of all PA gate voltages.

### 8.1 Procedure

1. **Activate CLR pin on DAC1:** `DAC5578_ActivateClearPin(&hdac1)` -- drives the hardware clear pin low, forcing all 8 DAC outputs to zero-scale (0V) per the pre-configured `DAC5578_CLR_CODE_ZERO` setting
2. **Activate CLR pin on DAC2:** `DAC5578_ActivateClearPin(&hdac2)` -- same for PA elements 9--16
3. **Hold state:** The function enters an infinite loop, keeping outputs cleared until manual power cycle

### 8.2 Trigger Conditions

The emergency stop is triggered by `handleSystemError()` (`main.cpp`, lines 773--779) when any of the following critical errors is detected:

| Error | Code | Description |
|-------|------|-------------|
| `ERROR_RF_PA_OVERCURRENT` | 9 | Any PA element $I_{dq} > 2.5~\text{A}$ |
| `ERROR_RF_PA_BIAS` | 10 | Any PA element $I_{dq} < 0.1~\text{A}$ |
| `ERROR_STEPPER_MOTOR` | 11 | Stepper motor fault |
| `ERROR_FPGA_COMM` | 12 | FPGA communication failure |
| `ERROR_POWER_SUPPLY` | 13 | Power supply fault |

### 8.3 Hardware Mechanism

The DAC5578 CLR pin provides a hardware-level safety path independent of I2C communication. When the CLR pin is driven active:

- All DAC output registers are immediately loaded with the pre-configured clear code (zero-scale in this system)
- The PA gate voltage is driven to maximum negative bias, pinching off all PAs
- No I2C transaction is required -- the clear is purely hardware-driven
- Response time is limited only by the DAC settling time and CLR pin propagation delay

This ensures PA shutdown even if the I2C bus is faulted or the STM32 is in an error state.

---

## 9. System Health Monitoring

The `checkSystemHealth()` function (`main.cpp`, lines 586--676) performs comprehensive system monitoring on each main loop iteration. The health checks cover:

| Check | Interval | Condition | Error Code |
|-------|----------|-----------|------------|
| AD9523 clock status | 5 s | STATUS0 or STATUS1 pin low | `ERROR_AD9523_CLOCK` |
| ADF4382 TX lock | Every loop | Lock detect pin low | `ERROR_ADF4382_TX_UNLOCK` |
| ADF4382 RX lock | Every loop | Lock detect pin low | `ERROR_ADF4382_RX_UNLOCK` |
| ADAR1000 communication | Every loop | SPI verify fails | `ERROR_ADAR1000_COMM` |
| ADAR1000 temperature | Every loop | $T > 85~\text{C}$ | `ERROR_ADAR1000_TEMP` |
| IMU communication | 10 s | NaN readings | `ERROR_IMU_COMM` |
| BMP180 communication | 15 s | Pressure out of range | `ERROR_BMP180_COMM` |
| GPS communication | 30 s | No fix update | `ERROR_GPS_COMM` |
| PA overcurrent | Every loop | $I_{dq} > 2.5~\text{A}$ | `ERROR_RF_PA_OVERCURRENT` |
| PA bias fault | Every loop | $I_{dq} < 0.1~\text{A}$ | `ERROR_RF_PA_BIAS` |
| System temperature | Every loop | $T > 75~\text{C}$ | `ERROR_TEMPERATURE_HIGH` |
| Watchdog | 60 s | No health check update | `ERROR_WATCHDOG_TIMEOUT` |

Non-critical errors trigger automatic recovery attempts. Critical errors (PA overcurrent, PA bias, stepper, FPGA, power supply) trigger emergency stop. If the error count exceeds 10, the system enters safe mode with full power-down.

---

## 10. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- symbols $V_\text{rail}$, $I_\text{rail}$, $P_\text{diss}$, $T_\text{junction}$, $\theta_{JA}$
- [Parameter Table](../00_notation/parameter_table.md) -- canonical system parameter values
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- [System Overview](01_system_overview.md) -- system-level block diagram and control path description
- [Power Budget](08_power_budget.md) -- per-rail current draw and thermal dissipation analysis

### Firmware Source
- `main.cpp` -- power sequencing (L1237--1599), `systemPowerUpSequence()` (L341), `systemPowerDownSequence()` (L372), `Emergency_Stop()` (L722), `checkSystemHealth()` (L586)

### Component Datasheets
- DAC5578 -- Texas Instruments 8-bit, 8-channel DAC with hardware CLR and LDAC
- ADS7830 -- Texas Instruments 8-bit, 8-channel ADC with I2C interface
- INA241A3 -- Texas Instruments high-side current sense amplifier ($G = 50~\text{V/V}$)
- TMP37 -- Analog Devices low-voltage temperature sensor (20 mV/C)
- ADAR1000 -- Analog Devices X/Ku-band analog beamformer (internal temperature sensor)
- QPA2962 -- Qorvo 6--18 GHz 10 W GaN MMIC PA (Extended variant, $T_\text{base}$ max 85C)

### Supplementary Data
- `3_Power Management/Power Management V6.xlsx` -- voltage rail specifications, current limits, and power budget data
