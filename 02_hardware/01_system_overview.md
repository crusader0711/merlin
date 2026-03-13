# AERIS-10 Hardware System Overview

**Purpose:** Provide the organizational anchor for all hardware subsystem documentation, including the functional block diagram description, two-variant summary, clock domain overview, and cross-references to every subsequent hardware document.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules

---

## 1. Overview

The AERIS-10 is a fully operational FMCW X-band phased array radar system. It transmits frequency-modulated continuous-wave chirps through a 16-element antenna array and processes the received echoes to produce range-Doppler detection maps with target tracking.

### 1.1 Functional Block Diagram

The system-level block diagram is maintained in [`RADAR_V6.drawio`](../2_Functional%20Diagram%20%26%20Interconnection%20Matrices/RADAR_V6.drawio). The signal path proceeds through the following functional stages:

1. **Antenna Elements** -- 16-element phased array (8x2 subarrays on Nexus, cascaded on Extended)
2. **ADAR1000 Beamformer** -- four ADAR1000 ICs providing per-element phase and amplitude control for beam steering across 31 elevation positions
3. **ADTR1107 T/R Module** (Nexus) / **QPA2962 GaN PA** (Extended) -- integrated transmit/receive front-end with power amplifier and low-noise amplifier
4. **LT5552 Mixer** -- down-conversion from X-band to IF using separate TX and RX local oscillators (ADF4382), yielding $f_\text{IF}$ (see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga))
5. **AD9484 ADC** -- 8-bit, 500 MSPS rated (operated at $f_s$), digitizing the IF signal with LVDS interface to FPGA
6. **FPGA Signal Processing Pipeline (XC7A100T):**
   - **DDC** -- digital down-conversion from IF to baseband using a numerically controlled oscillator
   - **CIC Decimator** -- $N_\text{CIC}$-stage cascaded integrator-comb filter with decimation factor $D_\text{CIC}$
   - **Matched Filter** -- pulse compression via frequency-domain convolution using $N_\text{FFT}$-point FFT
   - **Range FFT** -- $N_\text{FFT}$-point forward FFT for range bin extraction
   - **Doppler FFT** -- $N_\text{Doppler}$-point FFT across $M$ chirps per beam position for velocity estimation
   - **CFAR Detector** -- constant false alarm rate detection with adaptive threshold
7. **FT601 USB 3.0** -- high-speed data transfer from FPGA to host PC at 100 MHz interface clock
8. **Host PC (Python GUI)** -- visualization, DBSCAN clustering, Kalman tracking, and map rendering (GUI_V6.py)

### 1.2 Control Path

An **STM32F746** microcontroller orchestrates system operation:
- SPI bus to ADF4382 (TX/RX LO configuration), AD9523 (clock tree), and ADAR1000 (beam steering)
- I2C bus to DAC5578 (PA gate bias), ADS7830 (current/temperature monitoring), GY-85 IMU, and BMP180 barometer
- UART to GPS module (TinyGPS++)
- GPIO for power rail sequencing, fan control, and emergency stop

---

## 2. System Parameter Quick Reference

The [Parameter Table](../00_notation/parameter_table.md) is the single source of truth for all numerical values. The table below lists key system parameters by symbol for quick lookup -- consult the parameter table for actual values and firmware/FPGA variable mappings.

| Parameter | Symbol | Description |
|-----------|--------|-------------|
| Center frequency | $f_c$ | Carrier frequency (X-band) |
| Chirp bandwidth | $B$ | Frequency sweep range (TBD -- see [Parameter Table](../00_notation/parameter_table.md#tbd-tracking)) |
| Long chirp duration | $T_{c,1}$ | Pulse width for long-range mode |
| Short chirp duration | $T_{c,2}$ | Pulse width for short-range mode |
| Long chirp PRI | $T_{r,1}$ | Pulse repetition interval (long) |
| Short chirp PRI | $T_{r,2}$ | Pulse repetition interval (short) |
| Guard time | $T_\text{guard}$ | Interval between chirp sequences |
| Chirps per position | $M$ | Coherent processing interval length |
| ADC sample rate | $f_s$ | Digitizer clock rate |
| IF frequency | $f_\text{IF}$ | Intermediate frequency after mixing |
| FFT size | $N_\text{FFT}$ | Range processing FFT length |
| Doppler FFT size | $N_\text{Doppler}$ | Velocity processing FFT length |
| Array elements | $N$ | Number of antenna elements |
| Elevation positions | $N_\text{el}$ | Beam positions per azimuth |
| Azimuth positions | $N_\text{az}$ | Steps per mechanical revolution |

### 2.1 Variant Comparison -- Key Differences

The AERIS-10 is produced in two variants. Parameters not listed below are shared between variants. See the [Parameter Table](../00_notation/parameter_table.md) for complete values.

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | Transmit power $P_t$ per element | 1 W (ADTR1107) | 10 W (QPA2962 GaN) |
> | Antenna type | 8x16 patch array | 32x16 slotted waveguide |
> | Antenna gain $G$ | ~20 dBi (patch, TBD) | ~30 dBi (waveguide, TBD) |
> | Detection range $R_\text{max}$ | 3 km | 20 km |

---

## 3. Subsystem Index

The following documents cover each hardware subsystem in detail. All documents reside in [`02_hardware/`](./) and follow the conventions in [`conventions.md`](../00_notation/conventions.md).

| Doc | Filename | Subsystem | Key Components | Requirement |
|-----|----------|-----------|----------------|-------------|
| 02 | [`02_rf_frontend.md`](02_rf_frontend.md) | RF Front-End | ADTR1107, LT5552, AD9484 | HDWR-02 |
| 03 | [`03_frequency_synthesis.md`](03_frequency_synthesis.md) | Frequency Synthesis | ADF4382 (x2), AD9523-1 | HDWR-03 |
| 04 | [`04_antenna_beamforming.md`](04_antenna_beamforming.md) | Antenna Array & Beamforming | ADAR1000 (x4), 16-element array | HDWR-04 |
| 05 | [`05_fpga_board.md`](05_fpga_board.md) | FPGA Board | XC7A100T Artix-7 | HDWR-05 |
| 06 | [`06_power_management.md`](06_power_management.md) | Power Management | DAC5578, ADS7830, GPIO sequencing | HDWR-06 |
| 07 | [`07_timing_budget.md`](07_timing_budget.md) | Timing Budget & Latency | End-to-end pipeline analysis | HDWR-07 |
| 08 | [`08_power_budget.md`](08_power_budget.md) | Power Budget | Per-rail current, thermal dissipation | HDWR-08 |
| 09 | [`09_gps_imu_transforms.md`](09_gps_imu_transforms.md) | GPS/IMU Coordinate Transforms | GY-85 IMU, GPS, BMP180 | HDWR-09 |

---

## 4. Clock Domain Overview

The AERIS-10 clock architecture is anchored by an **AD9523-1** clock distribution IC driven by a 100 MHz oven-controlled crystal oscillator (OCXO). The AD9523 internal VCO generates all system clocks through programmable integer dividers.

### 4.1 VCO Frequency

The AD9523 PLL2 multiplies the VCXO reference to produce the VCO frequency:

$$
f_\text{VCO} = f_\text{VCXO} \times N_\text{PLL2} \tag{HW-SYS-1}
$$

where $f_\text{VCXO}$ is the 100 MHz VCXO frequency and $N_\text{PLL2} = 4 \times B_\text{cnt} + A_\text{cnt}$ is the PLL2 feedback divider. With $B_\text{cnt} = 9$ and $A_\text{cnt} = 0$, the divider is $N_\text{PLL2} = 36$, giving:

$$
f_\text{VCO} = 100~\text{MHz} \times 36 = 3.6~\text{GHz} \tag{HW-SYS-2}
$$

### 4.2 Clock Domain Summary

Each output clock is derived from the VCO by an integer divider $D_k$:

$$
f_{\text{out},k} = \frac{f_\text{VCO}}{D_k} \tag{HW-SYS-3}
$$

The system operates in four clock domains:

| Clock Domain | Frequency | AD9523 Output | Divider $D_k$ | Destination |
|-------------|-----------|---------------|----------------|-------------|
| ADC acquisition | 400 MHz | OUT4, OUT5 | 9 | AD9484, FPGA ADC interface |
| DAC output | 120 MHz | OUT10, OUT11 | 30 | DAC, FPGA DAC interface |
| System/processing | 100 MHz | OUT6 | 36 | FPGA main processing |
| FT601 interface | 100 MHz | External (FT601 IC) | -- | USB 3.0 data transfer |

Additional AD9523 outputs provide reference clocks for the frequency synthesizers:

| Output | Frequency | Divider | Destination |
|--------|-----------|---------|-------------|
| OUT0, OUT1 | 300 MHz | 12 | ADF4382 TX/RX reference |
| OUT8, OUT9 | 60 MHz | 60 | ADF4382 TX/RX SYNC |
| OUT7 | 20 MHz | 180 | Test/debug |

Cross-domain data transfer between the 400 MHz ADC domain and the 100 MHz processing domain uses 3-stage Gray-coded CDC synchronizers (documented in [`05_fpga_board.md`](05_fpga_board.md)).

### 4.3 System Noise Temperature Reference

The system equivalent noise temperature $T_e$ (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)) relates to the system noise figure $F$ (linear) by:

$$
T_e = T_0 (F - 1) \tag{HW-SYS-4}
$$

where $T_0$ is the standard reference noise temperature (see [Symbol Table -- Physical Constants](../00_notation/symbol_table.md#physical-constants)). The full cascaded noise figure analysis is derived in [`01_physics/05_noise_analysis.md`](../01_physics/05_noise_analysis.md) using the Friis formula, with hardware component values documented in [`02_rf_frontend.md`](02_rf_frontend.md).

---

## 5. Variant Comparison

The AERIS-10 system is produced in two variants optimized for different operational ranges. All shared parameters (waveform timing, signal processing pipeline, FPGA configuration, clock architecture) are identical between variants.

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | Power amplifier | ADTR1107 (integrated T/R module) | QPA2962 (GaN PA, external LNA) |
> | $P_t$ per element | 1 W | 10 W |
> | Antenna | 8x16 patch array | 32x16 slotted waveguide |
> | Antenna gain $G$ | ~20 dBi (TBD) | ~30 dBi (TBD) |
> | Detection range $R_\text{max}$ | 3 km | 20 km |

### 5.1 Architectural Differences

**RF Front-End:** The Nexus variant uses the ADTR1107, an Analog Devices integrated transmit/receive module that combines PA, LNA, and T/R switch in a single package. The Extended variant replaces this with a Qorvo QPA2962 GaN power amplifier providing 10x the transmit power, paired with a separate external LNA.

**Antenna:** The Nexus uses a compact 8x16 printed patch array. The Extended uses a 32x16 slotted waveguide array with higher directivity, yielding approximately 10 dB additional antenna gain.

**Detection Range:** The combined effect of higher transmit power (+10 dB) and higher antenna gain (~10 dB each way) extends the detection range from 3 km (Nexus) to 20 km (Extended). The range improvement follows from the radar range equation Eq. (FMCW-6) in [`01_physics/01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md), where $R_\text{max} \propto (P_t G^2)^{1/4}$.

**Firmware:** The STM32 firmware codebase is shared between both variants. The power sequencing differs slightly for the PA subsystem (ADTR1107 vs QPA2962 bias control), but all other initialization, beam steering, and data acquisition code is identical.

---

## 6. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- authoritative symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- canonical numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Physics Foundation (Phase 2)
- [`01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md) -- FMCW radar equation, beat frequency, range-Doppler coupling
- [`02_lfm_waveform_model.md`](../01_physics/02_lfm_waveform_model.md) -- LFM chirp signal model, pulse compression
- [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md) -- Array factor, ADAR1000 phase quantization, grating lobes
- [`04_detection_theory.md`](../01_physics/04_detection_theory.md) -- CFAR detection, Neyman-Pearson criterion
- [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md) -- Cascaded noise figure, system noise temperature
- [`06_calibration_theory.md`](../01_physics/06_calibration_theory.md) -- ADAR1000 phase/amplitude calibration

### Block Diagram
- [`RADAR_V6.drawio`](../2_Functional%20Diagram%20%26%20Interconnection%20Matrices/RADAR_V6.drawio) -- System-level functional block diagram (draw.io source)

### Key Component Datasheets
- AD9523-1 -- Clock distribution IC (12-output, dual PLL)
- ADF4382 -- Microwave wideband synthesizer (x2: TX and RX LO)
- ADAR1000 -- X/Ku-band 4-channel analog beamformer (x4)
- ADTR1107 -- 8 GHz to 16 GHz front-end T/R module (Nexus)
- QPA2962 -- 6 GHz to 18 GHz 10 W GaN MMIC power amplifier (Extended)
- LT5552 -- 3 GHz to 20 GHz high-linearity mixer
- AD9484 -- 8-bit, 500 MSPS ADC
- XC7A100T -- Artix-7 FPGA (101,440 LUTs, 126,800 FFs, 135 BRAMs, 240 DSP48E1s)
