# RF Front-End Subsystem

**Purpose:** Document the AERIS-10 RF receive/transmit chain -- the ADTR1107 integrated T/R front-end module, LT5552 downconversion mixer, and AD9484 analog-to-digital converter -- with key specifications, interface details, and cross-references to the noise analysis and frequency synthesis subsystems.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules

---

## 1. Overview

The AERIS-10 RF front-end implements a superheterodyne architecture with an intermediate frequency $f_\text{IF}$ (see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga)). The signal path is:

1. **Antenna elements** (16-element phased array)
2. **ADAR1000** beamformer -- per-element phase and amplitude control, T/R switching (documented in [`04_antenna_beamforming.md`](04_antenna_beamforming.md))
3. **ADTR1107** T/R front-end module -- LNA (receive path) and PA (transmit path) per element
4. **LT5552** mixer -- downconversion from X-band RF to IF using ADF4382 RX LO
5. **AD9484** ADC -- 8-bit digitization of the IF signal at $f_s$ (see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga))

In the transmit path, the signal flows in reverse: the ADF4382 TX synthesizer generates the X-band carrier at $f_c$, which is amplified by the ADTR1107 PA and radiated through the array.

---

## 2. ADTR1107 T/R Front-End Module

The ADTR1107 (Analog Devices) is an integrated transmit/receive module covering 8 GHz to 16 GHz, combining a power amplifier (PA), low-noise amplifier (LNA), and T/R switch in a single package.

### 2.1 Key Specifications

| Parameter | Symbol | Value | Notes |
|-----------|--------|-------|-------|
| Frequency range | -- | 8--16 GHz | Covers full X-band |
| Output power (PA, P1dB) | $P_t$ | ~1 W (30 dBm) | Per element, Nexus variant |
| LNA noise figure | $F_\text{LNA}$ | TBD | See [Parameter Table](../00_notation/parameter_table.md#tbd-tracking) |
| LNA gain | $G_\text{LNA}$ | TBD | Datasheet value pending extraction |
| IP3 (LNA, output) | -- | TBD | Datasheet value pending extraction |
| PA gain | -- | TBD | Datasheet value pending extraction |

The ADTR1107 noise figure $F_\text{LNA}$ is a critical parameter because the first-stage noise figure dominates the system noise budget per the Friis formula Eq. (NF-7) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#friis-cascaded-noise-figure). Once confirmed from the datasheet, this value must be updated in the [Parameter Table](../00_notation/parameter_table.md#tbd-tracking).

### 2.2 TX/RX Switching

T/R switching is controlled by the ADAR1000 beamformer via the `setADTR1107Control()` method in the firmware (`ADAR1000_Manager.cpp`). The control signal sets the ADTR1107's internal switch position:

- **TX mode:** PA active, LNA disabled. The `CTRL_SW` pin is driven HIGH.
- **RX mode:** LNA active, PA disabled. The `CTRL_SW` pin is driven LOW.

Fast switching between TX and RX modes is supported via `fastTXMode()` and `fastRXMode()` in the ADAR1000 manager, enabling rapid T/R toggling during the chirp cycle.

### 2.3 Power Sequencing

The ADTR1107 requires a specific power-up sequence to prevent damage, implemented in `ADAR1000_Manager::initializeADTR1107Sequence()` (`ADAR1000_Manager.cpp`):

1. Connect all GND pins to ground (hardware)
2. Set `VDD_SW` to 3.3 V via GPIO enable (`EN_P_3V3_ADTR`)
3. Set `VSS_SW` to $-3.3~\text{V}$ via GPIO enable (`EN_P_3V3_SW`)
4. Set `CTRL_SW` to RX mode initially
5. Set LNA gate voltage `VGG_LNA` to 0 V (via ADAR1000 bias DAC)
6. Apply `VDD_LNA` at 5.0 V
7. Set `VGG_LNA` to operating bias
8. Set PA gate voltage `VGG_PA` and drain voltage `VDD_PA`
9. Ramp PA drain current $I_{dq}$ (`Idq_pa_bias`) to operating point

Each step includes settling delays to ensure safe power rail transitions.

### 2.4 Variant Differences

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | T/R module | ADTR1107 (integrated) | QPA2962 GaN PA + external LNA |
> | $P_t$ per element | ~1 W (30 dBm) | 10 W (40 dBm) |
> | Noise figure $F_\text{LNA}$ | TBD (ADTR1107 datasheet) | TBD (external LNA datasheet) |
> | Package | Single integrated module | Separate PA and LNA components |

The Extended variant replaces the ADTR1107 with a Qorvo QPA2962 GaN MMIC power amplifier (6--18 GHz, 10 W) paired with a separate external LNA. This provides 10x transmit power but requires independent bias control for the PA and LNA stages. The firmware PA bias control via `DAC5578` and current monitoring via `ADS7830` supports both configurations.

---

## 3. LT5552 Mixer

The LT5552 (Analog Devices / Linear Technology) is a high-linearity double-balanced mixer covering 3 GHz to 20 GHz.

### 3.1 Key Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| RF/LO frequency range | 3--20 GHz | Covers X-band operation |
| Conversion loss | ~7 dB typical | Passive mixer: $G_\text{mix} < 1$ |
| Input IP3 (IIP3) | +23.8 dBm typical | High linearity for strong signal handling |
| LO drive level | 13--18 dBm | Required for specified performance |
| IF bandwidth | DC to 6 GHz | Supports $f_\text{IF}$ operation |

### 3.2 Downconversion

The LT5552 performs RF-to-IF downconversion using the RX local oscillator generated by the ADF4382 (documented in [`03_frequency_synthesis.md`](03_frequency_synthesis.md#adf4382-synthesizers)). The IF frequency is the difference between the TX and RX synthesizer frequencies:

$$
f_\text{IF} = f_\text{TX} - f_\text{RX} \tag{HW-RF-1}
$$

where $f_\text{TX}$ (`TX_FREQ_HZ` in `adf4382a_manager.h`) and $f_\text{RX}$ (`RX_FREQ_HZ` in `adf4382a_manager.h`) are the TX and RX local oscillator frequencies, respectively (see [Parameter Table](../00_notation/parameter_table.md#frequency-synthesis) for values).

### 3.3 Noise Figure Impact

As a passive mixer, the LT5552 has conversion *loss* rather than gain ($G_\text{mix} < 1$, i.e., $G_{\text{mix,dB}} < 0~\text{dB}$). The mixer's noise figure $F_\text{mix}$ and the noise of all downstream stages are divided by $G_\text{LNA}$ in the Friis cascade Eq. (NF-8) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#aeris-10-receive-chain-stages), making the LNA gain critical for suppressing these contributions.

The equivalent noise figure for a passive mixer approximates its conversion loss:

$$
F_\text{mix} \approx \frac{1}{G_\text{mix}} \tag{HW-RF-2}
$$

---

## 4. AD9484 ADC

The AD9484 (Analog Devices) is an 8-bit, 500 MSPS analog-to-digital converter. In the AERIS-10, it is operated at $f_s$ (see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga)) to digitize the IF signal.

> **Pitfall Reminder:** The AD9484 is an **8-bit** ADC, NOT 14-bit. See [Parameter Table -- Inconsistency Resolution #3](../00_notation/parameter_table.md#3-adc-resolution-8-bit-ad9484). The FPGA data path width `ADC_WIDTH = 8` in `ddc_400m.v` confirms this.

### 4.1 Key Specifications

| Parameter | Symbol | Value | Notes |
|-----------|--------|-------|-------|
| Resolution | $b$ | 8 bits | FPGA `ADC_WIDTH = 8` |
| Maximum sample rate | -- | 500 MSPS | Datasheet rated maximum |
| Operating sample rate | $f_s$ | 400 MSPS | Clocked from AD9523 OUT4/OUT5 |
| ENOB | -- | ~7.5 bits typical | At Nyquist input frequency |
| SFDR | -- | ~48 dBFS typical | At Nyquist input frequency |
| Input bandwidth | -- | 650 MHz | Full-power analog bandwidth |
| Interface | -- | LVDS DDR | 8-bit parallel, differential |
| Power supply | -- | 1.8 V / 3.3 V | Analog and digital supply rails |

### 4.2 Clock Source

The ADC clock is provided by the AD9523-1 clock distribution IC via outputs OUT4 and OUT5 at 400 MHz LVDS (see [`03_frequency_synthesis.md`](03_frequency_synthesis.md#ad9523-1-clock-generator) and the clock tree table therein). OUT4 drives the AD9484 directly; OUT5 provides a phase-aligned copy to the FPGA for data capture synchronization.

### 4.3 LVDS Interface

The AD9484 outputs 8-bit data via an LVDS DDR (double data rate) interface, captured by the FPGA using Xilinx IDDR primitives. The interface is implemented in two Verilog modules:

**`ad9484_interface_400m.v`** -- Primary ADC data capture:

| Signal | Width | Direction | Description |
|--------|-------|-----------|-------------|
| `adc_d_p[7:0]` / `adc_d_n[7:0]` | 8-bit differential | Input | LVDS data pairs |
| `adc_dco_p` / `adc_dco_n` | 1-bit differential | Input | Data clock output (400 MHz LVDS) |
| `adc_data_400m[7:0]` | 8-bit | Output | Captured data in 400 MHz domain |
| `adc_data_valid_400m` | 1-bit | Output | Data valid flag |

The module uses:
- `IBUFDS` primitives with `DIFF_TERM = "TRUE"` and `IOSTANDARD = "LVDS_25"` for LVDS-to-single-ended conversion on each data bit and the DCO clock
- `IDDR` primitives in `SAME_EDGE_PIPELINED` mode for DDR data capture, producing rising-edge and falling-edge samples
- A phase toggle register to interleave rising and falling edge data into the 400 MSPS output stream

**`lvds_to_cmos_400m.v`** -- Clock domain conversion:

| Signal | Width | Direction | Description |
|--------|-------|-----------|-------------|
| `clk_400m_p` / `clk_400m_n` | 1-bit differential | Input | 400 MHz LVDS clock |
| `clk_400m_cmos` | 1-bit | Output | 400 MHz CMOS clock |

This module converts the LVDS DCO clock to a CMOS-level clock using `IBUFDS` (with `DIFF_TERM = "FALSE"`, using external 100 Ohm termination) and a `BUFG` global clock buffer for distribution across the FPGA fabric.

### 4.4 Dynamic Range

The theoretical signal-to-quantization-noise ratio for an 8-bit ADC is given by Eq. (NF-11) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#signal-to-quantization-noise-ratio):

$$
\text{SQNR}_\text{dB} = 6.02 \, b + 1.76~\text{dB} \tag{HW-RF-3}
$$

For $b = 8$, this yields a theoretical SQNR of approximately 49.9 dB. In practice, the AD9484 achieves an ENOB of approximately 7.5 bits (see Eq. (NF-13)), further reducing the effective dynamic range. The ADC effective noise figure $F_\text{ADC}$ depends on the signal level and analog chain gain, as analyzed in Eq. (NF-12) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#effective-noise-figure-of-the-adc).

The 8-bit quantization noise floor is a **dominant constraint** on the AERIS-10 digital noise floor. The CIC decimation filter (5 stages, $D_\text{CIC} = 4$) provides processing gain that partially compensates for the limited ADC resolution (see Eq. (NF-14) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#cic-processing-gain)).

---

## 5. Cascaded Noise Figure Reference

The AERIS-10 receive chain noise figure is analyzed in detail in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md). The cascade order and cross-references are:

| Stage | Component | Noise Figure Symbol | Gain Symbol | Reference |
|-------|-----------|-------------------|-------------|-----------|
| 1 | ADTR1107 LNA | $F_\text{LNA}$ (TBD) | $G_\text{LNA}$ (TBD) | [Parameter Table](../00_notation/parameter_table.md#tbd-tracking) |
| 2 | LT5552 mixer | $F_\text{mix}$ | $G_\text{mix}$ | Eq. (HW-RF-2) above |
| 3 | IF amplifier (if present) | $F_\text{IF}$ | $G_\text{IF}$ | TBD |
| 4 | AD9484 ADC | $F_\text{ADC}$ | $G_\text{ADC}$ | Eq. (NF-12) in noise analysis |

The system noise figure follows the Friis formula, Eq. (NF-8) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#aeris-10-receive-chain-stages):

$$
F_\text{sys} = F_\text{LNA} + \frac{F_\text{mix} - 1}{G_\text{LNA}} + \frac{F_\text{IF} - 1}{G_\text{LNA} \, G_\text{mix}} + \frac{F_\text{ADC} - 1}{G_\text{LNA} \, G_\text{mix} \, G_\text{IF}} \tag{HW-RF-4}
$$

The first-stage noise figure $F_\text{LNA}$ dominates provided the LNA gain $G_\text{LNA}$ is sufficient to suppress downstream contributions. The representative numerical evaluation in Section 7.3 of [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#numerical-evaluation-pending-parameter-resolution) illustrates this relationship using placeholder values.

**TBD parameters affecting noise budget:**
- $F_\text{LNA}$ -- ADTR1107 datasheet extraction required (Nexus variant)
- $G_\text{LNA}$ -- ADTR1107 datasheet extraction required
- Extended variant noise figure chain -- QPA2962 + external LNA analysis required

---

## 6. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- symbol definitions for $F$, $G$, $P_t$, $f_\text{IF}$, $f_s$, $b$
- [Parameter Table](../00_notation/parameter_table.md) -- canonical numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Hardware Cross-References
- [`01_system_overview.md`](01_system_overview.md) -- system block diagram and variant comparison
- [`03_frequency_synthesis.md`](03_frequency_synthesis.md) -- ADF4382 LO frequencies (mixer LO source), AD9523 clock tree (ADC clock source)
- [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md) -- Friis cascaded noise figure derivation, ADC noise contribution, CIC processing gain

### Firmware Sources
- `ADAR1000_Manager.cpp` / `ADAR1000_Manager.h` -- ADTR1107 power sequencing (`initializeADTR1107Sequence()`), T/R switching (`setADTR1107Control()`)
- `adf4382a_manager.h` -- LO frequency definitions (`TX_FREQ_HZ`, `RX_FREQ_HZ`)

### FPGA Sources
- `ad9484_interface_400m.v` -- LVDS DDR data capture interface
- `lvds_to_cmos_400m.v` -- LVDS-to-CMOS clock conversion

### Component Datasheets
- ADTR1107 -- 8--16 GHz integrated T/R front-end module ([`7_Components Datasheets and Application notes/adtr1107.pdf`](../7_Components%20Datasheets%20and%20Application%20notes/adtr1107.pdf))
- LT5552 -- 3--20 GHz high-linearity double-balanced mixer ([`7_Components Datasheets and Application notes/LTC5552f.pdf`](../7_Components%20Datasheets%20and%20Application%20notes/LTC5552f.pdf))
- AD9484 -- 8-bit, 500 MSPS ADC ([`7_Components Datasheets and Application notes/`](../7_Components%20Datasheets%20and%20Application%20notes/))
- QPA2962 -- 6--18 GHz 10 W GaN MMIC power amplifier (Extended variant)
