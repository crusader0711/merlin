# Hardware Improvement Research

**Purpose:** Survey of hardware upgrade paths for the AERIS-10 radar system with quantified impact on detection range, noise figure, and signal quality. Each section evaluates a specific upgrade against the documented Phase 3 hardware baseline, substituting candidate component values into the existing Phase 2 physics equations to derive quantitative improvement estimates. This document is research and feasibility assessment only -- it does not contain implementation specifications.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [RF Front-End](../02_hardware/02_rf_frontend.md) -- ADTR1107 baseline, LT5552 mixer, AD9484 ADC
- [Frequency Synthesis](../02_hardware/03_frequency_synthesis.md) -- ADF4382A synthesizers, AD9523 clock tree
- [Noise Analysis](../01_physics/05_noise_analysis.md) -- cascaded noise figure derivation (Eq. NF-7 through NF-18)

---

## Introduction

### Scope

This document surveys six hardware upgrade paths for the AERIS-10 radar system, organized across three system layers:

1. **RF front-end** -- GaN vs SiGe front-end comparison (Section 1), frequency synthesizer phase noise improvements (Section 2)
2. **Antenna and packaging** -- Antenna-in-Package miniaturization (Section 3), antenna array expansion (Section 5)
3. **Digital back-end** -- Higher-resolution ADC options (Section 4), FPGA upgrade path (Section 6)

### Methodology

Each section follows a consistent structure:

1. **Current State** -- Quantitative baseline from the Phase 3 hardware documentation, with cross-references to the specific document and equation
2. **Literature Survey** -- Candidate components with specific part numbers and datasheet specifications, plus relevant academic references
3. **Gap Analysis** -- Quantitative improvement derived by substituting candidate values into existing Phase 2 equations (Friis cascade Eq. NF-8, radar range equation Eq. FMCW-6, SQNR Eq. NF-11, etc.) rather than re-deriving from first principles
4. **Feasibility Assessment** -- Integration complexity, cost, risk, and impact on the existing PCB/firmware/FPGA design
5. **Recommendations** -- Recommended investigation steps (not implementation specifications), with priority ranking relative to other topics

### Cross-Reference Framework

- All baseline values reference Phase 3 hardware documents ([`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md), [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md), [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md), [`05_fpga_board.md`](../02_hardware/05_fpga_board.md))
- All improvement calculations reference Phase 2 physics documents ([`01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md), [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md), [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md))
- Canonical numerical values come from the [Parameter Table](../00_notation/parameter_table.md)

### Research Scope Disclaimer

This document presents **research and feasibility assessments only**. It is not an implementation specification. Each section concludes with recommended investigation steps, not design specifications or schematics. Per the project scope defined in `PROJECT.md`, implementation of any improvements is out of scope for this documentation effort.

### AERIS-10 Variants

Both AERIS-10 variants are addressed throughout:

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | T/R module | ADTR1107 (SiGe, integrated) | QPA2962 GaN PA + external LNA |
> | $P_t$ per element | ~1 W (30 dBm) | 10 W (40 dBm) |
> | Detection range | 3 km | 20 km |
> | Antenna | 8x16 patch array | 32x16 slotted waveguide |

Where an upgrade path affects the two variants differently, variant-specific analysis is provided with callout blocks per [Conventions](../00_notation/conventions.md) Section 4.

---

## 1. GaN vs SiGe Front-End Comparison

*Requirement: HWRES-01*

### 1.1 Current State

The Nexus variant uses the **ADTR1107** (Analog Devices) as an integrated transmit/receive front-end module. Key baseline specifications from [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md#adtr1107-tr-front-end-module):

| Parameter | Symbol | Value | Source |
|-----------|--------|-------|--------|
| Technology | -- | SiGe BiCMOS | ADTR1107 datasheet |
| Frequency range | -- | 8--16 GHz | ADTR1107 datasheet |
| LNA noise figure | $F_\text{LNA}$ | 2.5 dB | ADTR1107 product page |
| LNA gain | $G_\text{LNA}$ | 18 dB (small signal) | ADTR1107 product page |
| PA saturated output power | $P_t$ | 25 dBm (~316 mW) | ADTR1107 product page |
| Integration | -- | PA + LNA + SPDT switch in single package | ADTR1107 datasheet |
| Supply voltage | -- | 5 V | ADTR1107 datasheet |

The ADTR1107 LNA is the first active stage in the receive chain. Per the Friis cascade formula Eq. (NF-8) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#aeris-10-receive-chain-stages):

$$
F_\text{sys} = F_\text{LNA} + \frac{F_\text{mix} - 1}{G_\text{LNA}} + \frac{F_\text{IF} - 1}{G_\text{LNA} \, G_\text{mix}} + \frac{F_\text{ADC} - 1}{G_\text{LNA} \, G_\text{mix} \, G_\text{IF}} \tag{NF-8}
$$

The first-stage noise figure $F_\text{LNA}$ appears directly in the cascade, while all subsequent stage contributions are divided by the cumulative gain of preceding stages. With $G_\text{LNA} = 18~\text{dB}$ (linear: $10^{18/10} \approx 63.1$), downstream noise contributions are suppressed by a factor of 63.

The Extended variant already implements a **hybrid GaN PA + separate LNA** approach using the **QPA2962** (Qorvo) GaN MMIC power amplifier (6--18 GHz, 10 W) paired with an external LNA, as documented in [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md#variant-differences) Section 2.4. This provides a direct reference point for the hybrid architecture's feasibility.

### 1.2 Literature Survey

#### PA Path: GaN Advantage

GaN-on-SiC power amplifiers at X-band deliver substantially higher output power than SiGe PAs, owing to GaN's wider bandgap (3.4 eV vs 1.1 eV for Si), higher breakdown voltage, and superior thermal conductivity of the SiC substrate.

| Parameter | ADTR1107 PA (SiGe) | Typical GaN PA (X-band) | Specific Candidates |
|-----------|--------------------|-----------------------|---------------------|
| $P_\text{sat}$ | 25 dBm (316 mW) | 33--40 dBm (2--10 W) | QPA2962: 40 dBm (10 W) |
| PA gain | TBD (ADTR1107 datasheet) | 20--25 dB typical | QPA2962: ~20 dB |
| Supply voltage | 5 V | 24--28 V | QPA2962: 28 V |
| Frequency range | 8--16 GHz | 6--18 GHz typical | QPA2962: 6--18 GHz |
| Technology | SiGe BiCMOS | GaN on SiC | -- |

**Candidate GaN PA devices at X-band:**

- **Qorvo QPA2962** -- 6--18 GHz, 10 W saturated output power. Already used in the Extended variant, confirming integration feasibility with the AERIS-10 system architecture.
- **Wolfspeed CGHV1J070D** -- GaN HEMT, 70 W CW at X-band (significantly oversized for per-element use; relevant only for centralized PA architectures).
- **Altum RF ALT-8025-CE** -- X-band GaN T/R module targeting phased array applications (application-specific, limited public datasheet availability).

#### LNA Path: SiGe/GaAs Advantage

GaN LNAs at X-band typically exhibit **higher noise figures** than SiGe or GaAs LNAs. This is a critical distinction from the PA path.

| Parameter | ADTR1107 LNA (SiGe) | Typical GaN LNA (X-band) | Typical GaAs pHEMT LNA |
|-----------|---------------------|--------------------------|------------------------|
| Noise figure | 2.5 dB | 1.5--3.0 dB | 1.0--2.0 dB |
| Gain | 18 dB | 15--25 dB | 15--25 dB |
| IP3 (output) | TBD | Higher than SiGe | Moderate |
| Survivability | Moderate | High (high breakdown) | Low |

**Key observation (Pitfall 3 from research):** GaN LNAs can have noise figures **worse** than the ADTR1107's 2.5 dB. The 1.5--3.0 dB range for GaN LNAs means some candidates would *degrade* the receive chain noise figure. The GaN LNA advantage lies in survivability (high power handling without damage) and linearity, not in noise figure.

GaAs pHEMT LNAs offer the lowest noise figures at X-band (1.0--2.0 dB) but lack the power handling capability of GaN. For a hybrid approach, a GaAs LNA on the receive path combined with a GaN PA on the transmit path yields the best of both technologies.

### 1.3 Gap Analysis

#### Transmit Power Improvement (PA Path)

The radar range equation (Eq. FMCW-6 in [`01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md)) shows that maximum detection range scales with the fourth root of transmit power:

$$
R_\text{max} \propto P_t^{1/4} \tag{HW-IMP-1}
$$

For the Nexus variant, replacing the ADTR1107 PA (25 dBm) with a GaN PA:

> **Variant Note: Nexus PA Upgrade Analysis**
> | | Current (ADTR1107) | GaN PA (2W) | GaN PA (5W) | GaN PA (10W, QPA2962) |
> |--|-------|----------|----------|----------|
> | $P_t$ per element | 25 dBm (316 mW) | 33 dBm (2 W) | 37 dBm (5 W) | 40 dBm (10 W) |
> | Power increase | -- | +8 dB | +12 dB | +15 dB |
> | Range factor ($P_t^{1/4}$) | 1.0x | 1.58x | 2.00x | 2.37x |
> | Estimated $R_\text{max}$ | 3 km | 4.7 km | 6.0 km | 7.1 km |

The range estimates assume all other parameters remain constant (antenna gain, noise figure, losses). The Extended variant already uses the QPA2962 at 10 W per element, so its transmit power upgrade path would require even higher power devices (20--50 W class), which introduces substantially more thermal management complexity.

#### Noise Figure Impact (LNA Path)

Substituting candidate LNA noise figures into Eq. (NF-8) to assess the impact on system noise figure:

**Step 1 -- Convert baseline to linear:**
- ADTR1107: $F_\text{LNA} = 2.5~\text{dB} \Rightarrow F_\text{LNA,lin} = 10^{2.5/10} = 1.778$
- ADTR1107: $G_\text{LNA} = 18~\text{dB} \Rightarrow G_\text{LNA,lin} = 10^{18/10} = 63.1$

**Step 2 -- Evaluate delta for candidate LNAs:**

Using the Friis cascade Eq. (NF-8), the system noise figure change when replacing the LNA is:

$$
\Delta F_\text{sys} = (F_\text{new,lin} - F_\text{LNA,lin}) + (F_\text{mix,lin} - 1)\left(\frac{1}{G_\text{new,lin}} - \frac{1}{G_\text{LNA,lin}}\right) + \cdots \tag{HW-IMP-2}
$$

where higher-order terms follow the same pattern. The first term dominates when gain values are similar.

| Candidate LNA | $\text{NF}_\text{dB}$ | $F_\text{lin}$ | $G_\text{dB}$ | $G_\text{lin}$ | $\Delta F_\text{sys}$ (first-order) | Assessment |
|---------------|----------------------|----------------|---------------|----------------|-------------------------------------|------------|
| ADTR1107 (baseline) | 2.5 | 1.778 | 18 | 63.1 | 0 | Baseline |
| GaN LNA (worst) | 3.0 | 2.000 | 20 | 100 | +0.222 (+0.5 dB degradation) | **Worse NF** |
| GaN LNA (best) | 1.5 | 1.413 | 15 | 31.6 | -0.365 but higher downstream contribution | **Mixed** |
| GaAs pHEMT LNA | 1.5 | 1.413 | 20 | 100 | -0.365 (-1.0 dB improvement) | **Best NF** |
| GaAs pHEMT LNA | 1.0 | 1.259 | 22 | 158 | -0.519 (-1.5 dB improvement) | **Best NF** |

**Key finding:** A GaN LNA at 3.0 dB NF would **degrade** the system noise figure by approximately 0.5 dB compared to the ADTR1107 baseline. Only GaN LNAs achieving better than 2.5 dB NF at 10.5 GHz would improve the receive path. A GaAs pHEMT LNA at 1.0--1.5 dB NF would improve the system noise figure by 1.0--1.5 dB.

The noise figure improvement translates to detection range via the radar range equation:

$$
R_\text{max} \propto F_\text{sys}^{-1/4} \tag{HW-IMP-3}
$$

A 1.5 dB NF improvement corresponds to approximately 9% range increase (all else equal). Compared to the 58--137% range increase from the PA power upgrade, the LNA NF improvement is **secondary**.

### 1.4 Feasibility Assessment

#### Integration Complexity

| Factor | ADTR1107 (current) | Hybrid GaN PA + Separate LNA |
|--------|-------------------|------------------------------|
| Component count per element | 1 (integrated T/R) | 2+ (PA + LNA + T/R switch) |
| PCB area per element | Minimal (single package) | 2--3x larger footprint |
| Bias circuits | Single 5V supply | 28V PA supply + separate LNA bias |
| T/R switching | Internal SPDT | External switch required |
| Firmware changes | None (ADTR1107 control via ADAR1000) | PA bias DAC, LNA bias, T/R switch timing |

The Extended variant already implements this hybrid approach, demonstrating that firmware support for separate PA bias control (via `DAC5578`) and current monitoring (via `ADS7830`) exists. Migration of the Nexus variant to a hybrid architecture could leverage the Extended variant's firmware infrastructure.

#### Power Management

GaN PAs require 24--28V drain supply, compared to the ADTR1107's 5V. This necessitates:
- Additional DC-DC converter stage (5V or 12V input to 28V output)
- Higher current capacity on the PA supply rail
- Gate bias sequencing to prevent damage (negative gate voltage applied before drain voltage)
- Per the power management documentation in [`06_power_management.md`](../02_hardware/06_power_management.md), the 17-step power-on sequence would require additional steps for GaN PA bias

#### Cost

- GaN PA devices (e.g., QPA2962) are significantly more expensive per unit than the ADTR1107 integrated module
- At 16-element quantities, the cost differential is substantial but not prohibitive for a development/research platform
- At 64-element quantities (array expansion scenario), cost becomes a major factor
- Separate LNA + PA + switch also increases assembly and testing cost

#### Thermal Risk

- GaN PA at 10W per element with 16 elements: $16 \times 10~\text{W} = 160~\text{W}$ total PA power dissipation (assuming ~50% PAE)
- Current ADTR1107 at 316 mW per element: ~5W total PA power
- 30x increase in thermal dissipation requires active cooling redesign
- Extended variant's thermal management approach provides a reference design

### 1.5 Recommendations

**Priority ranking:** HIGH for Nexus variant PA upgrade; LOW for LNA-only upgrade.

**Key findings:**
1. GaN's advantage is **primarily in transmit power**, not receive noise figure. The ADTR1107's 2.5 dB NF is competitive with or better than most GaN LNAs at X-band.
2. The **hybrid GaN PA + SiGe/GaAs LNA** approach is the recommended architecture, which the Extended variant already demonstrates with the QPA2962.
3. PA power upgrade provides **1.6--2.4x range improvement** for Nexus (from 3 km to 4.7--7.1 km).
4. LNA NF upgrade provides **~9% range improvement** at best -- a secondary benefit.

**Recommended investigation steps (not implementation specifications):**
1. Characterize the ADTR1107 PA P1dB and gain at 10.5 GHz specifically (Open Question 1 from research) to establish precise baseline
2. Evaluate QPA2962 integration with the Nexus variant PCB -- leverage Extended variant firmware and bias circuitry as reference
3. Survey GaAs pHEMT LNAs at X-band with NF < 2.0 dB for potential receive path improvement
4. Perform thermal simulation for 16-element GaN PA array at target power levels
5. Assess whether the Extended variant's existing hybrid approach meets Nexus detection range requirements (potentially avoiding a dedicated Nexus GaN redesign)

---

## 2. Frequency Synthesizer Phase Noise Improvements

*Requirement: HWRES-02*

### 2.1 Current State

The AERIS-10 uses two **ADF4382A** (Analog Devices) microwave wideband synthesizers to generate the TX and RX local oscillator signals, as documented in [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md#adf4382-synthesizers):

| Parameter | Value | Source |
|-----------|-------|--------|
| PLL figure of merit (FOM) | $-239~\text{dBc/Hz}$ | ADF4382A product page |
| VCO range | 11.5--21.0 GHz (fundamental) | `adf4382.h:468--469` |
| TX output frequency | $f_\text{TX} = 10.5~\text{GHz}$ | `TX_FREQ_HZ` in `adf4382a_manager.h` |
| RX output frequency | $f_\text{RX} = 10.38~\text{GHz}$ | `RX_FREQ_HZ` in `adf4382a_manager.h` |
| Reference frequency | 300 MHz from AD9523 (OUT0/OUT1) | [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md#complete-clock-tree-table) |
| Architecture | Fractional-N with FRAC1/FRAC2/MOD2 | Eq. (HW-FS-8) in [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md#pll-frequency-synthesis) |
| Master reference | 100 MHz OCXO (180 s warm-up) | [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md#ocxo-warm-up-requirement) |

The VCO output frequency is synthesized per Eq. (HW-FS-8):

$$
f_\text{VCO,ADF} = f_\text{ref} \times \left( N_\text{INT} + \frac{\text{FRAC1}}{2^{25}} + \frac{\text{FRAC2}}{\text{MOD2} \times 2^{25}} \right) \tag{HW-FS-8}
$$

Phase noise of the synthesizer is critical because it sets the **Doppler detection floor** -- the minimum Doppler frequency shift (and therefore minimum target velocity) that can be distinguished from the oscillator's own phase noise. As noted in [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md#phase-noise) Section 3.8, close-in phase noise limits the minimum detectable velocity $v$.

### 2.2 Literature Survey

#### Synthesizer Comparison

| Parameter | ADF4382A (Analog Devices) | LMX2820 (Texas Instruments) |
|-----------|--------------------------|----------------------------|
| PLL FOM | $-239~\text{dBc/Hz}$ | $-236~\text{dBc/Hz}$ |
| Frequency range | 62.5 MHz -- 21 GHz | 45 MHz -- 22.6 GHz |
| VCO range | 11.5--21 GHz (fundamental) | Wide (integrated VCO) |
| Fractional-N | FRAC1/FRAC2/MOD2, 25-bit modulus | Fractional-N with delta-sigma |
| Max PFD frequency | 625 MHz (integer mode) | Competitive |
| Integrated jitter | Ultra-low (datasheet) | Competitive |
| FOM advantage | **Baseline (best-in-class)** | 3 dB worse |

The ADF4382A's $-239~\text{dBc/Hz}$ FOM represents **best-in-class** performance among commercially available wideband synthesizers at X-band. The LMX2820's $-236~\text{dBc/Hz}$ FOM is 3 dB worse, which translates directly to 3 dB higher phase noise floor at the same offset frequency and output frequency.

#### Alternative Improvement Paths

Since the ADF4382A is already best-in-class, phase noise improvements are more likely to come from other system elements:

1. **OCXO reference upgrade** -- The 100 MHz OCXO provides the master reference. A higher-stability OCXO with lower close-in phase noise would improve the reference contribution to the synthesized output. Ultra-low phase noise OCXOs (e.g., Wenzel Sprinter series) achieve $\mathcal{L}(100~\text{Hz}) < -155~\text{dBc/Hz}$ at 100 MHz.

2. **Clean-up PLL loop filter optimization** -- The ADF4382A PLL2 loop bandwidth determines the crossover frequency between reference noise (dominant inside the loop bandwidth) and VCO noise (dominant outside). Optimizing the loop filter components can minimize the integrated phase noise.

3. **Reference frequency increase** -- Using a higher reference frequency (e.g., 500 MHz or 1 GHz) reduces the PLL multiplication factor $N$, which directly reduces the $20\log_{10}(N)$ phase noise contribution from the reference path. However, the AD9523 clock tree is currently configured for 300 MHz reference (Eq. HW-FS-5 with $D_k = 12$).

4. **Fractional-N spur reduction** -- Advanced delta-sigma modulator techniques and spur cancellation (ADF4382A supports bleed current via `EN_BLEED` in REG001F) can reduce fractional spurs that contribute to the phase noise floor near Doppler offsets of interest.

#### Academic References

- R. E. Best, *Phase-Locked Loops: Design, Simulation, and Applications*, 6th ed., McGraw-Hill, 2007 -- PLL phase noise theory
- B. Razavi, "A Study of Phase Noise in CMOS Oscillators," *IEEE JSSC*, vol. 31, no. 3, 1996 -- Foundational oscillator phase noise analysis
- D. B. Leeson, "A Simple Model of Feedback Oscillator Noise Spectrum," *Proceedings of the IEEE*, vol. 54, no. 2, 1966 -- Leeson's oscillator noise model

### 2.3 Gap Analysis

#### Doppler Floor from Phase Noise

The Doppler detection floor is determined by the synthesizer's phase noise at the Doppler offset frequency. For an FMCW radar, the relevant offset frequency is the Doppler shift $f_d$ corresponding to the target velocity of interest.

The minimum detectable Doppler shift $f_{d,\text{min}}$ is limited by the phase noise spectral density $\mathcal{L}(f_d)$ integrated over the Doppler resolution bandwidth $\Delta f_d$, relative to the coherent integration gain from $M$ chirps.

For the AERIS-10 system, the Doppler resolution bandwidth is determined by the coherent processing interval (CPI). With $M$ chirps at pulse repetition interval $T_r$:

$$
\Delta f_d = \frac{1}{M \cdot T_r} \tag{HW-IMP-4}
$$

For the long-chirp mode ($T_{r,1} = 167~\mu\text{s}$, $M = 32$):

$$
\Delta f_{d,1} = \frac{1}{32 \times 167 \times 10^{-6}} \approx 187~\text{Hz}
$$

For the short-chirp mode ($T_{r,2} = 175~\mu\text{s}$, $M = 32$):

$$
\Delta f_{d,2} = \frac{1}{32 \times 175 \times 10^{-6}} \approx 179~\text{Hz}
$$

#### Phase Noise to Doppler Floor Derivation

The phase noise power in the Doppler resolution cell at offset $f_d$ from the carrier is:

$$
P_{\text{PN}}(f_d) = \mathcal{L}(f_d) \cdot \Delta f_d \tag{HW-IMP-5}
$$

where $\mathcal{L}(f_d)$ is the single-sideband phase noise spectral density in dBc/Hz at offset $f_d$, and $\Delta f_d$ is the Doppler resolution bandwidth.

Coherent integration of $M$ chirps improves the signal-to-phase-noise ratio by:

$$
G_\text{coh} = 10 \log_{10}(M) = 10 \log_{10}(32) \approx 15.1~\text{dB} \tag{HW-IMP-6}
$$

The effective phase noise floor after coherent integration, expressed as a signal-to-phase-noise ratio (in dB) at Doppler offset $f_d$, is:

$$
\text{SPNR}(f_d) = -\mathcal{L}(f_d) - 10\log_{10}(\Delta f_d) + G_\text{coh} \tag{HW-IMP-7}
$$

For detection, the SPNR must exceed the minimum detectable SNR ($\text{SNR}_\text{min}$, see [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)). The minimum detectable Doppler shift $f_{d,\text{min}}$ is the offset at which $\text{SPNR}(f_{d,\text{min}}) = \text{SNR}_\text{min}$.

#### Translating to Minimum Detectable Velocity

The Doppler shift relates to radial velocity via:

$$
f_d = \frac{2 v}{\lambda} \tag{HW-IMP-8}
$$

where $\lambda = c / f_c$ (see [Symbol Table](../00_notation/symbol_table.md#range-and-velocity)). At $f_c = 10.5~\text{GHz}$, $\lambda \approx 0.02857~\text{m}$ (see [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing)). Therefore the minimum detectable velocity corresponding to the Doppler resolution is:

$$
v_\text{min} = \frac{f_{d,\text{min}} \cdot \lambda}{2} = \frac{\Delta f_d \cdot \lambda}{2} \tag{HW-IMP-9}
$$

For the long-chirp mode:

$$
v_{\text{min},1} = \frac{187 \times 0.02857}{2} \approx 2.67~\text{m/s} \approx 9.6~\text{km/h}
$$

For the short-chirp mode:

$$
v_{\text{min},2} = \frac{179 \times 0.02857}{2} \approx 2.56~\text{m/s} \approx 9.2~\text{km/h}
$$

These are the **velocity resolution limits** set by the CPI length. The phase noise floor sets a separate limit: if $\mathcal{L}(f_d)$ at a particular offset is too high, the phase noise power exceeds the target return even for velocities above the resolution limit.

#### Phase Noise Impact Estimation

To estimate the actual Doppler floor from the ADF4382A, we need $\mathcal{L}(f_m)$ at the relevant offset frequencies. Using the FOM to estimate phase noise at offset $f_m$ from a carrier at $f_\text{out}$ with PFD frequency $f_\text{PFD}$:

$$
\mathcal{L}(f_m) \approx \text{FOM} + 20\log_{10}\left(\frac{f_\text{out}}{f_\text{PFD}}\right) + 10\log_{10}(f_m) \tag{HW-IMP-10}
$$

This is an approximation valid inside the PLL loop bandwidth where reference noise dominates. For the ADF4382A at $f_\text{out} = 10.5~\text{GHz}$, $f_\text{PFD} = 300~\text{MHz}$ (assuming $R = 1$):

$$
\mathcal{L}(f_m) \approx -239 + 20\log_{10}\left(\frac{10.5 \times 10^9}{300 \times 10^6}\right) + 10\log_{10}(f_m)
$$

$$
= -239 + 20\log_{10}(35) + 10\log_{10}(f_m)
$$

$$
= -239 + 30.9 + 10\log_{10}(f_m)
$$

$$
= -208.1 + 10\log_{10}(f_m) \quad \text{dBc/Hz}
$$

At representative offsets:

| Offset $f_m$ | $\mathcal{L}(f_m)$ (ADF4382A est.) | $\mathcal{L}(f_m)$ (LMX2820 est., +3 dB) |
|--------------|-------------------------------------|------------------------------------------|
| 1 kHz | $-178~\text{dBc/Hz}$ | $-175~\text{dBc/Hz}$ |
| 10 kHz | $-168~\text{dBc/Hz}$ | $-165~\text{dBc/Hz}$ |
| 100 kHz | $-158~\text{dBc/Hz}$ | $-155~\text{dBc/Hz}$ |
| 1 MHz | $-148~\text{dBc/Hz}$ | $-145~\text{dBc/Hz}$ |

> **Caution:** These are approximate values derived from the FOM figure and the PLL noise transfer function model. Actual phase noise at specific offsets depends on VCO noise, loop bandwidth, charge pump noise, and reference oscillator noise. The ADF4382A datasheet phase noise plots at 10.5 GHz should be consulted for authoritative values (Open Question 2 from research).

Applying Eq. (HW-IMP-7) at $f_m = 1~\text{kHz}$ offset for the long-chirp mode:

$$
\text{SPNR}(1~\text{kHz}) = 178 - 10\log_{10}(187) + 15.1 = 178 - 22.7 + 15.1 = 170.4~\text{dB}
$$

This SPNR is far above any practical $\text{SNR}_\text{min}$ threshold, indicating that the ADF4382A phase noise does **not** limit Doppler detection at the velocities of interest. The 1 kHz Doppler offset corresponds to a velocity of:

$$
v = \frac{1000 \times 0.02857}{2} \approx 14.3~\text{m/s} \approx 51~\text{km/h}
$$

Even at very low Doppler offsets (e.g., 100 Hz, corresponding to $v \approx 1.4~\text{m/s} \approx 5.1~\text{km/h}$):

$$
\text{SPNR}(100~\text{Hz}) \approx 188 - 22.7 + 15.1 = 180.4~\text{dB}
$$

The phase noise floor remains far below the thermal noise floor for any practical target scenario.

#### Synthesizer Replacement Assessment

Replacing the ADF4382A with the LMX2820 would **worsen** the phase noise by 3 dB across all offsets. No currently available commercial synthesizer improves upon the ADF4382A's FOM of $-239~\text{dBc/Hz}$. The synthesizer is already the **strongest link** in the phase noise chain.

### 2.4 Feasibility Assessment

#### Synthesizer Replacement

| Factor | Assessment |
|--------|------------|
| Benefit | Negative -- LMX2820 is 3 dB worse than ADF4382A |
| Complexity | Low if pin-compatible; moderate otherwise (PCB redesign, firmware driver) |
| Recommendation | **Not recommended** -- ADF4382A is already best-in-class |

#### OCXO Reference Upgrade

| Factor | Assessment |
|--------|------------|
| Benefit | Moderate -- improves close-in phase noise (< 1 kHz offsets) |
| Complexity | Low -- OCXO is a discrete module on the PCB; replacement requires only matching the 100 MHz output and the VCXO input specifications of the AD9523 |
| Cost | Moderate -- ultra-low phase noise OCXOs (Wenzel, Pascall) cost significantly more than standard OCXOs |
| Risk | Low -- OCXO interface is well-defined; warm-up time may differ |

#### Loop Filter Optimization

| Factor | Assessment |
|--------|------------|
| Benefit | Low to moderate -- optimizing loop bandwidth can reduce integrated jitter |
| Complexity | Low -- passive component changes on existing PCB; no firmware changes |
| Cost | Minimal -- resistor and capacitor changes |
| Risk | Low -- but requires careful simulation to avoid loop stability issues |

#### Phase Noise vs. Other Noise Sources

A critical consideration: even with perfect phase noise, the AERIS-10 Doppler detection performance may be limited by **other noise sources**:

- **ADC quantization noise** -- The 8-bit AD9484 has a quantization floor at $-49.9~\text{dBFS}$ (Eq. NF-11 in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#signal-to-quantization-noise-ratio)). This is likely the dominant noise floor for Doppler detection, not phase noise.
- **Thermal noise** -- The system thermal noise floor (set by $F_\text{sys}$ per Eq. NF-8) competes with phase noise at all offsets.
- **Platform vibration** -- Mechanical vibration of the antenna platform can introduce Doppler modulation that mimics phase noise, potentially dominating at low offset frequencies.

The estimated SPNR values (170+ dB) are far above the ADC quantization floor (~50 dB), confirming that **ADC resolution, not phase noise, is the dominant limitation** on Doppler detection sensitivity.

### 2.5 Recommendations

**Priority ranking:** LOW -- The ADF4382A is already best-in-class; the largest gains come from addressing other noise sources (ADC upgrade per HWRES-04).

**Key findings:**
1. The ADF4382A at $-239~\text{dBc/Hz}$ FOM is the **best commercially available** synthesizer for this application. No replacement improves performance.
2. The estimated SPNR at relevant Doppler offsets exceeds 170 dB, far above the 8-bit ADC quantization floor of ~50 dB. **Phase noise is not the Doppler detection bottleneck.**
3. The Doppler velocity resolution is limited by CPI length ($\Delta v \approx 2.6~\text{m/s}$ for the long-chirp mode), not by phase noise.
4. OCXO reference upgrade provides marginal improvement at close-in offsets; loop filter optimization provides marginal improvement at the loop bandwidth crossover.

**Recommended investigation steps (not implementation specifications):**
1. **Characterize actual ADF4382A phase noise** at 10.5 GHz from datasheet plots at 100 Hz, 1 kHz, 10 kHz, 100 kHz, and 1 MHz offsets (Open Question 2 from research) to validate the FOM-based estimates above
2. **Measure the system Doppler floor** empirically -- compare against the theoretical phase noise floor to determine whether phase noise, ADC quantization, or platform vibration is the actual limiting factor
3. **Evaluate OCXO upgrade options** -- relevant only if empirical measurements show the reference oscillator contribution is significant at offsets below 1 kHz
4. **Prioritize HWRES-04 (ADC upgrade)** over synthesizer improvements -- the 36 dB SQNR improvement from an 8-to-14-bit ADC upgrade would have far greater impact on Doppler detection sensitivity than any achievable phase noise improvement

---

## 3. Antenna-in-Package Miniaturization

*To be completed in Plan 06-02.*

---

## 4. Higher-Resolution ADC Options

*To be completed in Plan 06-03.*

---

## 5. Antenna Array Expansion

*To be completed in Plan 06-02.*

---

## 6. FPGA Upgrade Path

*To be completed in Plan 06-03.*

---

## References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- symbol definitions for $F$, $G$, $P_t$, $\mathcal{L}(f_m)$
- [Parameter Table](../00_notation/parameter_table.md) -- canonical numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Phase 2 Physics Cross-References
- [`01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md) -- radar range equation Eq. (FMCW-6), $R_\text{max} \propto P_t^{1/4}$
- [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md) -- Friis cascade Eq. (NF-7), AERIS-10 chain Eq. (NF-8), SQNR Eq. (NF-11)
- [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md) -- array factor, grating lobe analysis Eq. (BF-10)

### Phase 3 Hardware Cross-References
- [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md) -- ADTR1107 baseline, LT5552 mixer, AD9484 ADC, cascaded NF reference Eq. (HW-RF-4)
- [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md) -- ADF4382A synthesizers, AD9523 clock tree, phase noise Eq. (HW-FS-7) through Eq. (HW-FS-8)
- [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md) -- ADAR1000 beamformer, 16-element array geometry
- [`05_fpga_board.md`](../02_hardware/05_fpga_board.md) -- XC7A100T resources, clock domains

### Component Datasheets and Product Pages
- ADTR1107 -- 8--16 GHz integrated T/R front-end module ([Analog Devices product page](https://www.analog.com/en/products/adtr1107.html))
- QPA2962 -- 6--18 GHz 10 W GaN MMIC power amplifier ([Qorvo](https://www.qorvo.com))
- ADF4382A -- 62.5 MHz to 21 GHz microwave wideband synthesizer ([Analog Devices product page](https://www.analog.com/en/products/adf4382a.html))
- LMX2820 -- 45 MHz to 22.6 GHz wideband synthesizer, FOM $-236~\text{dBc/Hz}$ ([Texas Instruments product page](https://www.ti.com/product/LMX2820))
- AD9680 -- 14-bit, 500 MSPS / 1 GSPS dual ADC ([Analog Devices product page](https://www.analog.com/en/products/ad9680.html))
- AD9523-1 -- Dual-PLL 12-output clock distribution IC ([Analog Devices](https://www.analog.com/en/products/ad9523-1.html))

### Industry and Academic References
- Altum RF, "Front-End Components for X/Ku Band Phased Array Radar," Nov 2025 -- GaN/SiGe comparison landscape
- Cadence, "LTCC Transmit-Receive X-Band Module with Phased Array Antenna," Application Note -- AiP dimensions and performance
- ResearchGate, "X-Band Transmit/Receive Module MMIC Chip-Set Based on Emerging GaN and SiGe Technologies" -- GaN vs SiGe comparison
- Qorvo, "X-Band Radar: Driving Defense Applications with Beamforming, GaN, and GaAs Technology" -- Industry perspective
- R. E. Best, *Phase-Locked Loops: Design, Simulation, and Applications*, 6th ed., McGraw-Hill, 2007 -- PLL phase noise theory
- D. B. Leeson, "A Simple Model of Feedback Oscillator Noise Spectrum," *Proceedings of the IEEE*, vol. 54, no. 2, 1966 -- Leeson's oscillator noise model
- B. Razavi, "A Study of Phase Noise in CMOS Oscillators," *IEEE JSSC*, vol. 31, no. 3, 1996 -- Oscillator phase noise analysis
