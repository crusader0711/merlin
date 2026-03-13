# AERIS-10 Power Budget Analysis

**Purpose:** Provide a comprehensive power budget analysis covering per-rail current draw, per-subsystem power consumption, total system power for both variants, and thermal dissipation to ensure reliable system operation within thermal limits.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Power Management](06_power_management.md) -- rail definitions, sequencing, and monitoring

---

## 1. Overview

This document analyzes the power consumption of the AERIS-10 radar system by voltage rail and by functional subsystem. The analysis serves three purposes:

1. **Power supply sizing** -- ensure each voltage rail regulator can supply the required current with adequate margin
2. **Thermal management** -- determine per-subsystem heat dissipation for cooling system design
3. **Variant comparison** -- quantify the significant power difference between Nexus (ADTR1107, 1 W/element) and Extended (QPA2962, 10 W/element) configurations

Power values are derived from component datasheet typical specifications. For measured current values via the ADS7830 monitoring ADCs, see [`06_power_management.md`](06_power_management.md#6-current-and-temperature-monitoring). For voltage rail definitions and GPIO enable pins, see [`06_power_management.md`](06_power_management.md#2-voltage-rails).

---

## 2. Per-Rail Current Budget

The power consumed by each voltage rail is:

$$
P_\text{rail} = V_\text{rail} \times I_\text{rail} \tag{HW-PB-1}
$$

where $V_\text{rail}$ and $I_\text{rail}$ are defined in the [Symbol Table](../00_notation/symbol_table.md#hardware-and-power).

### 2.1 Clock Domain Rails

| Rail | Voltage | Components | Estimated Current | Power |
|------|---------|------------|-------------------|-------|
| 1.8V Clock | 1.8 V | AD9523-1 (1.8V domain) | ~0.15 A | 0.27 W |
| 3.3V Clock | 3.3 V | AD9523-1 (3.3V domain), OCXO | ~0.30 A | 0.99 W |

### 2.2 FPGA Rails

| Rail | Voltage | Components | Estimated Current | Power |
|------|---------|------------|-------------------|-------|
| 1.0V FPGA Core | 1.0 V | XC7A100T $V_\text{CCINT}$ | ~0.80 A | 0.80 W |
| 1.8V FPGA I/O | 1.8 V | XC7A100T $V_\text{CCAUX}$ | ~0.20 A | 0.36 W |
| 3.3V FPGA | 3.3 V | XC7A100T $V_\text{CCO}$, config, FT601 | ~0.50 A | 1.65 W |

Actual FPGA power consumption depends heavily on design utilization and toggle rates. The values above are representative estimates based on the Artix-7 power model for a design operating at 100--400 MHz with moderate resource utilization. Vivado power estimation reports would provide more precise values (see [STATE.md blocker](../.planning/STATE.md) regarding Vivado report availability).

### 2.3 Beamformer Rails

| Rail | Voltage | Components | Estimated Current | Power |
|------|---------|------------|-------------------|-------|
| 3.3V ADAR1000 (1-2) | 3.3 V | ADAR1000 #1, #2 (2 ICs) | ~0.30 A | 0.99 W |
| 3.3V ADAR1000 (3-4) | 3.3 V | ADAR1000 #3, #4 (2 ICs) | ~0.30 A | 0.99 W |
| 5.0V ADAR1000 | 5.0 V | ADAR1000 PA bias (x4 ICs) | ~0.40 A | 2.00 W |

Each ADAR1000 draws approximately 150 mA on its 3.3V supply (typical, all channels active in TX/RX mode).

### 2.4 RF Front-End Rails

| Rail | Voltage | Components | Estimated Current (Nexus) | Estimated Current (Extended) | Power (Nexus) | Power (Extended) |
|------|---------|------------|---------------------------|------------------------------|---------------|------------------|
| 3.3V ADTR1107 | 3.3 V | T/R modules (x16) | ~2.4 A | N/A | 7.92 W | N/A |
| PA VDD (22V) | 22 V | External PA drain | N/A | ~7.3 A | N/A | ~160 W |
| 5.0V PA banks | 5.0 V | PA bias supply | ~0.5 A | ~1.0 A | 2.5 W | 5.0 W |

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | PA type | ADTR1107 (integrated T/R) | QPA2962 (GaN MMIC) |
> | $P_t$ per element | 1 W | 10 W |
> | PA supply voltage | 3.3 V (integrated) | 22 V (external drain) |
> | Total PA power (16 elements) | ~16 W | ~160 W |
> | PA efficiency (typical) | ~25% | ~30% |

### 2.5 Control and Sensor Rails

| Rail | Voltage | Components | Estimated Current | Power |
|------|---------|------------|-------------------|-------|
| 3.3V Digital | 3.3 V | STM32F746, DAC5578 (x2), ADS7830 (x3), level shifters | ~0.25 A | 0.83 W |
| 5.0V Sensors | 5.0 V | TMP37 (x8), GY-85 IMU, BMP180, GPS module | ~0.10 A | 0.50 W |

---

## 3. Per-Subsystem Power

Grouping power by functional subsystem provides a clearer view of where energy is consumed:

$$
P_\text{subsystem} = \sum_{k} V_{\text{rail},k} \times I_{\text{rail},k} \tag{HW-PB-2}
$$

### 3.1 Subsystem Power Summary

| Subsystem | Rails Used | Power (Nexus) | Power (Extended) |
|-----------|-----------|---------------|------------------|
| Clock Distribution | 1.8V Clock, 3.3V Clock | 1.26 W | 1.26 W |
| FPGA | 1.0V Core, 1.8V I/O, 3.3V FPGA | 2.81 W | 2.81 W |
| Beamformer (ADAR1000 x4) | 3.3V ADAR (x2), 5.0V ADAR | 3.98 W | 3.98 W |
| RF Front-End / PA | 3.3V ADTR / 22V PA VDD, 5.0V PA | ~26.4 W | ~165 W |
| Digital Control | 3.3V Digital, 5.0V Sensors | 1.33 W | 1.33 W |
| ADF4382 (x2) | Fed from 3.3V rails | ~1.0 W | ~1.0 W |
| **Total** | | **~37 W** | **~175 W** |

### 3.2 Power Distribution

For the Nexus variant, the RF front-end consumes approximately 71% of total system power. For the Extended variant, the PA subsystem dominates at approximately 94% of total power. This has direct implications for cooling system design.

---

## 4. Total System Power

The total system power is the sum of all subsystem contributions:

$$
P_\text{total} = \sum_{i} P_{\text{subsystem},i} \tag{HW-PB-3}
$$

### 4.1 Variant Comparison

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | Total system power $P_\text{total}$ | ~37 W | ~175 W |
> | Total PA power (16 elements) | ~16 W | ~160 W |
> | Non-PA power | ~21 W | ~15 W |
> | Power supply recommendation | 50 W (35% margin) | 250 W (43% margin) |

The non-PA power differs slightly between variants because the Nexus uses the 3.3V-supplied ADTR1107 integrated T/R module while the Extended uses the 22V-supplied QPA2962 with a separate LNA, resulting in different loss distribution.

---

## 5. Thermal Dissipation Analysis

### 5.1 Power-to-Heat Conversion

For most components, nearly all consumed power is dissipated as heat. For power amplifiers, the dissipated power is the difference between DC input power and RF output power:

$$
P_\text{diss,PA} = P_\text{DC} - P_\text{RF} = P_\text{DC} \times (1 - \eta) \tag{HW-PB-4}
$$

where $\eta$ is the PA power-added efficiency (PAE).

### 5.2 Per-Subsystem Thermal Dissipation

| Subsystem | Power In | Efficiency | Heat Dissipated (Nexus) | Heat Dissipated (Extended) |
|-----------|----------|------------|-------------------------|----------------------------|
| Clock Distribution | 1.26 W | ~0% (all heat) | 1.26 W | 1.26 W |
| FPGA | 2.81 W | ~0% (all heat) | 2.81 W | 2.81 W |
| Beamformer | 3.98 W | ~0% (all heat) | 3.98 W | 3.98 W |
| PA (per element) | 1.65 W / 10 W | ~25% / ~30% | 1.24 W | 7.0 W |
| PA (16 elements total) | 26.4 W / 160 W | ~25% / ~30% | 19.8 W | 112 W |
| Digital Control | 1.33 W | ~0% (all heat) | 1.33 W | 1.33 W |
| **Total Heat** | | | **~29 W** | **~121 W** |

### 5.3 Thermal Thresholds

Cross-referencing the thermal management section in [`06_power_management.md`](06_power_management.md#7-thermal-management):

| Component | Max Operating Temp | Monitoring Method | Threshold Action |
|-----------|-------------------|-------------------|------------------|
| ADAR1000 | 85 C (junction) | On-chip SPI sensor | `ERROR_ADAR1000_TEMP` |
| QPA2962 | 85 C (base plate) | TMP37 via ADS7830 | Fan ON at 25 C, error at 75 C |
| FPGA (XC7A100T) | 100 C (junction) | Not directly monitored | -- |
| STM32F746 | 105 C (junction) | Not directly monitored | -- |

### 5.4 Cooling Requirements

The junction temperature of any component must satisfy Eq. (HW-PWR-5) from [`06_power_management.md`](06_power_management.md#74-thermal-dissipation):

$$
T_\text{junction} = T_\text{ambient} + P_\text{diss} \times \theta_{JA} < T_\text{max} \tag{HW-PB-5}
$$

For the Extended variant, the PA subsystem dissipates approximately 112 W across 16 elements (7 W per element). With a typical $\theta_{JA}$ of 10 C/W for a well-heatsinked GaN device, this requires:

$$
T_\text{ambient,max} = T_\text{max} - P_\text{diss} \times \theta_{JA} \tag{HW-PB-6}
$$

Active cooling (fan controlled by `EN_DIS_COOLING` GPIO) is mandatory for the Extended variant during TX operation. The Nexus variant generates approximately 29 W total heat, which may be manageable with passive cooling depending on enclosure design.

---

## 6. PA Power Analysis

### 6.1 Per-PA Power Consumption

Each PA element's power consumption is monitored in real time via the ADS7830 current sense ADCs. The per-element DC power is:

$$
P_\text{PA,element} = V_\text{DD} \times I_{dq} \tag{HW-PB-7}
$$

where $V_\text{DD}$ is the PA drain supply voltage and $I_{dq}$ is the quiescent drain current measured by the ADS7830 (see Eq. (HW-PWR-2) in [`06_power_management.md`](06_power_management.md#62-adc-to-current-conversion)).

The firmware targets a quiescent current of $I_{dq} \approx 1.680~\text{A}$ per element during the bias tuning procedure (`main.cpp`, lines 1640, 1655).

### 6.2 Total PA Power

For 16 active elements, the total PA power is:

$$
P_\text{PA,total} = \sum_{n=1}^{16} V_\text{DD} \times I_{dq,n} \tag{HW-PB-8}
$$

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | PA device | ADTR1107 | QPA2962 |
> | $V_\text{DD}$ | 3.3 V (integrated) | 22 V (external) |
> | Target $I_{dq}$ per element | ~1.68 A | ~1.68 A |
> | $P_t$ per element | 1 W | 10 W |
> | DC input per element | ~5.5 W | ~37 W |
> | PAE (typical) | ~25% | ~30% |
> | Heat per element | ~4.5 W | ~27 W |
> | Total PA DC power (16 elements) | ~88 W | ~592 W |
> | Total PA RF output | ~16 W | ~160 W |
> | Total PA heat (16 elements) | ~72 W | ~432 W |

**Note:** The $I_{dq}$ target of 1.68 A is from firmware. For the ADTR1107, the actual operating point at 3.3V supply with 1.68 A yields ~5.5 W DC per element, which is higher than the 1 W RF output, consistent with ~25% efficiency. For the QPA2962 at 22V supply, the same 1.68 A yields ~37 W DC per element. These values should be verified against the Power Management V6.xlsx spreadsheet for precise per-element budgets.

### 6.3 Overcurrent Protection

The firmware monitors each PA element against the 2.5 A overcurrent threshold (see [`06_power_management.md`](06_power_management.md#63-monitoring-thresholds)). At the maximum monitored current:

- **Nexus:** $P_\text{max} = 3.3 \times 2.5 = 8.25~\text{W}$ per element
- **Extended:** $P_\text{max} = 22 \times 2.5 = 55~\text{W}$ per element

These represent fault conditions that trigger emergency stop before thermal damage occurs.

---

## 7. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- symbols $V_\text{rail}$, $I_\text{rail}$, $P_\text{diss}$, $T_\text{junction}$, $\theta_{JA}$
- [Parameter Table](../00_notation/parameter_table.md) -- canonical system parameter values
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- [Power Management](06_power_management.md) -- rail definitions, sequencing, monitoring thresholds, emergency stop
- [System Overview](01_system_overview.md) -- system-level architecture and variant comparison

### Component Datasheets
- XC7A100T -- Xilinx Artix-7 FPGA power estimation (DS181)
- AD9523-1 -- Analog Devices clock distribution IC power consumption
- ADAR1000 -- Analog Devices beamformer power consumption per channel
- ADTR1107 -- Analog Devices integrated T/R module (Nexus variant)
- QPA2962 -- Qorvo GaN PA power consumption and thermal resistance (Extended variant)
- ADF4382 -- Analog Devices synthesizer power consumption
- TMP37 -- Analog Devices temperature sensor specifications
- INA241A3 -- Texas Instruments current sense amplifier

### Supplementary Data
- `3_Power Management/Power Management V6.xlsx` -- measured voltage rail specifications, current limits, and detailed power budget data
