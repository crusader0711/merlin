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

*Requirement: HWRES-03*

### 3.1 Current State

The AERIS-10 antenna subsystem uses a **PCB-level integration** approach with discrete components at each array element. The current architecture from [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md):

| Component | Count | Function | Package Level |
|-----------|-------|----------|---------------|
| ADAR1000 beamformer IC | 4 units | 4-channel phase/gain control | Surface-mount IC |
| ADTR1107 T/R module | 16 units | PA + LNA + T/R switch per element | Surface-mount module |
| Antenna elements | 16 | Radiating elements | PCB patch (Nexus) / waveguide slot (Extended) |

Each element occupies a PCB footprint that includes the ADTR1107 module, associated bias components, and RF traces to the ADAR1000 beamformer. The inter-element spacing is $d = \lambda/2 = 14.3~\text{mm}$ at $f_c = 10.5~\text{GHz}$ (Eq. HW-ANT-6 in [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md)), yielding a total aperture length of:

$$
L_\text{aperture} = (N - 1) \times d = 15 \times 14.3~\text{mm} = 214.3~\text{mm} \tag{HW-ANT-7}
$$

The ADAR1000 devices are controlled via SPI1 on the STM32F746 with 2-bit DEV_ADDR addressing (0x00--0x03), as documented in [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#spi-interface) Section 2.2. The firmware bypasses the internal beam RAM and writes phase/gain settings directly via SPI for each of the 31 elevation beam positions.

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | Antenna type | 8x16 patch array (PCB-printed) | 32x16 slotted waveguide |
> | T/R module | ADTR1107 (integrated SiGe) | QPA2962 GaN PA + external LNA |
> | Element pitch constraint | 14.3 mm (set by $\lambda/2$) | 14.3 mm (same RF constraint) |
> | PCB area available | Compact platform, constrained | Larger platform, more available area |

### 3.2 Literature Survey

Antenna-in-Package (AiP) technology integrates the radiating antenna element, T/R module, and beamformer circuitry into a single multi-layer package, eliminating board-level RF interconnects and reducing per-element footprint.

#### LTCC X-Band AiP Implementations

| Implementation | Package Size | Technology | Performance | Source |
|---------------|-------------|------------|-------------|--------|
| Cadence X-band T/R AiP | 14.3 x 24.5 x 3.55 mm | LTCC with air cavities | RX gain >30 dB, TX EIRP 32--38.5 dBm | Cadence App Note |
| 3D X-band T/R module | ~20 x 20 x 3.7 mm | Anodized aluminum multilayer | 4-channel integrated T/R | IEICE 2020 |
| Miniaturized LTCC T/R | Various | LTCC 4-channel | 40% bandwidth at X-band | MDPI 2023 |

**LTCC (Low-Temperature Co-fired Ceramic)** is the dominant substrate technology for X-band AiP implementations. Key advantages:

- **Low dielectric loss** at X-band frequencies ($\tan\delta < 0.002$ for typical LTCC substrates)
- **Hermetic packaging** -- ceramic substrate provides environmental protection without additional encapsulation
- **Integrated air cavities** -- reduce dielectric loading on embedded patch antennas, improving radiation efficiency
- **Multi-layer interconnect** -- 10--20 ceramic layers allow 3D routing of RF, DC bias, and digital control signals
- **Thermal management** -- embedded thermal vias provide heat dissipation paths from active devices

#### Comparison: Current PCB-Level vs AiP Approaches

| Factor | Current PCB-Level | LTCC AiP | 3D-Stacked Module |
|--------|-------------------|----------|-------------------|
| Per-element footprint | ~20 x 25 mm (PCB area) | ~14 x 25 mm (Cadence ref) | ~20 x 20 mm |
| Height | ~5 mm (component + PCB) | 3.55 mm | 3.7 mm |
| RF interconnect loss | Board traces + connectors | Embedded stripline | Vertical transitions |
| Modularity | Individual T/R replacement | Entire AiP replacement | Module-level replacement |
| Element density | Limited by PCB routing | Higher (integrated routing) | Higher (vertical stacking) |
| Thermal path | Via PCB ground plane | Embedded thermal vias | Aluminum substrate |

#### Academic References

- Cadence, "LTCC Transmit-Receive X-Band Module with Phased Array Antenna," Application Note -- LTCC AiP dimensions, performance, and air cavity technique
- MDPI, "Design of X-Band TR Module Based on LTCC," *Electronics*, 2023 -- Miniaturized LTCC T/R module with 40% bandwidth
- IEICE, "Integrated X-band phased array antenna with LTCC 3D T/R module," *IEICE Electronics Express*, 2020 -- 3D integration approach with anodized aluminum multilayer

### 3.3 Gap Analysis

#### Size Reduction Quantification

The primary AiP benefit is per-element footprint reduction and the elimination of board-level RF routing:

| Metric | Current PCB-Level | LTCC AiP (projected) | Reduction |
|--------|-------------------|----------------------|-----------|
| Per-element area (footprint) | ~500 mm$^2$ (20 x 25 mm) | ~350 mm$^2$ (14 x 25 mm) | ~30% |
| Per-element height | ~5 mm | ~3.6 mm | ~28% |
| RF trace length (element to beamformer) | 15--30 mm (PCB trace) | <5 mm (embedded) | >60% |
| Interconnect insertion loss | 0.3--0.8 dB (PCB + connector) | <0.2 dB (embedded stripline) | ~0.5 dB |

The interconnect loss reduction of ~0.5 dB appears between the ADAR1000 output and the antenna element. This loss currently appears in the transmit and receive paths, affecting both transmit EIRP and receive noise figure. Per the Friis cascade Eq. (NF-8) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md), reducing the pre-LNA loss by 0.5 dB improves the system noise figure by approximately 0.5 dB (since pre-LNA losses add directly to $F_\text{sys}$).

#### What AiP Enables

1. **Higher element density** -- Reduced per-element footprint allows more elements in a given aperture, or the same element count in a smaller form factor
2. **Planar 2D arrays** -- Compact AiP modules facilitate dense 2D planar arrays with dual-plane electronic steering
3. **Reduced interconnect losses** -- Embedded RF routing eliminates PCB trace and connector losses
4. **Environmental robustness** -- LTCC hermetic packaging protects RF circuitry from moisture and contamination

#### What AiP Costs

1. **Significant NRE** -- Custom LTCC substrate design, fabrication, and qualification is a major non-recurring engineering investment ($100K--$500K range for prototype runs)
2. **Loss of modularity** -- Individual T/R module replacement is not possible; a failed element requires replacing the entire AiP module
3. **Custom package design** -- No commercial off-the-shelf AiP exists for the ADAR1000 + ADTR1107 combination
4. **Thermal constraints** -- LTCC thermal conductivity (~3 W/mK) is lower than aluminum PCB substrates (~200 W/mK), requiring careful thermal via design

#### ADAR1000 SPI Compatibility Concern

The ADAR1000 SPI control interface (3-byte transaction, 2-bit DEV_ADDR, documented in [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#spi-interface) Section 2.2) must be preserved in any AiP solution. Specifically:

- **SPI signal routing:** The ADAR1000 requires SPI clock, MOSI, MISO, and per-device chip select signals routed through the AiP substrate to the embedded beamformer IC
- **Level shifting:** The current system uses an FPGA-based level shifter (`level_shifter_interface.v`) to translate STM32 3.3V SPI to ADAR1000 1.8V I/O; this function must be preserved or integrated
- **Firmware impact:** If the AiP uses a different control interface (e.g., I2C, proprietary serial), the entire STM32 firmware driver (`ADAR1000_Manager.cpp`) and FPGA level-shifter interface require redesign

An AiP solution that preserves the ADAR1000 SPI interface requires no firmware changes. An AiP solution using a different beamformer IC or custom ASIC would require complete firmware and FPGA interface redesign.

### 3.4 Feasibility Assessment

| Factor | Assessment | Rating |
|--------|------------|--------|
| Integration complexity | Fundamental PCB redesign, custom LTCC substrate, new thermal management | **HIGH** |
| NRE cost | LTCC packaging is a specialized process; prototype costs $100K--$500K | **HIGH** |
| Component availability | ADAR1000 and ADTR1107 are commercially available; LTCC fabrication is specialty | **MODERATE** |
| Technical risk | ADAR1000 + ADTR1107 specific AiP integration has NOT been demonstrated in literature | **HIGH** |
| Timeline | 12--18 months for design, fabrication, and characterization of prototype AiP | **LONG** |
| Firmware impact | None if ADAR1000 SPI preserved; complete redesign if different beamformer IC used | **VARIABLE** |

> **Variant Note: AiP Impact by Platform**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | Miniaturization benefit | **HIGH** -- compact platform benefits most from size reduction | **LOW** -- Extended platform has ample space |
> | Thermal challenge | **MODERATE** -- ADTR1107 at 1W per element | **HIGH** -- QPA2962 at 10W per element exceeds LTCC thermal limits |
> | PCB redesign scope | Entire antenna PCB | Slotted waveguide array incompatible with AiP (different antenna technology) |
> | Recommendation | Primary AiP candidate | AiP not applicable to waveguide array; focus on PA module miniaturization instead |

The Extended variant's slotted waveguide antenna is structurally incompatible with AiP technology (waveguide slots are machined, not printed). AiP miniaturization is therefore primarily relevant to the **Nexus variant** with its PCB-printed patch array.

### 3.5 Recommendations

**Priority ranking:** LOW relative to ADC upgrade (HWRES-04) and array expansion (HWRES-05), which offer more immediate and quantifiable performance gains.

**Key findings:**

1. LTCC-based AiP at X-band is **technically mature** for generic T/R modules, but the specific ADAR1000 + ADTR1107 combination has not been demonstrated in an AiP package
2. The primary benefit is **form factor reduction** (~30% area, ~28% height), not RF performance improvement. The ~0.5 dB interconnect loss reduction is modest compared to the 8--15 dB transmit power gain from GaN PA upgrade (HWRES-01) or the 36 dB SQNR gain from ADC upgrade (HWRES-04)
3. AiP is primarily relevant to the **Nexus variant** -- the Extended variant's waveguide antenna is incompatible with AiP technology
4. **ADAR1000 SPI compatibility** is a critical constraint -- any AiP solution must preserve the existing SPI control interface to avoid firmware and FPGA redesign

**Recommended investigation steps (not implementation specifications):**

1. Contact LTCC fabricators (e.g., Kyocera, TDK, VIA Electronic) for feasibility study with ADAR1000 + ADTR1107 die stack at $\lambda/2 = 14.3~\text{mm}$ element pitch
2. Evaluate whether commercial beamformer-integrated AiP solutions (e.g., future Analog Devices or Qorvo products) could replace the ADAR1000 + ADTR1107 combination without SPI interface changes
3. Assess thermal viability: can LTCC thermal vias dissipate 1W (ADTR1107) per element at 14.3 mm pitch without exceeding junction temperature limits?
4. As a **near-term alternative**, optimize the current PCB layout for element density without full AiP transition -- this may recover 10--15% of the AiP size benefit with minimal NRE

**Position as next-generation option:** AiP miniaturization should be considered for a future AERIS-10 revision (v2.0+) after the higher-priority upgrades (ADC, array expansion, GaN PA) have been evaluated and potentially implemented.

---

## 4. Higher-Resolution ADC Options

*Requirement: HWRES-04*

### 4.1 Current State

The AERIS-10 digitizes the IF signal using the **AD9484** (Analog Devices), an **8-bit** 500 MSPS ADC operated at $f_s = 400~\text{MSPS}$. The 8-bit resolution is confirmed by two independent sources:

- **Hardware documentation:** [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md#ad9484-adc) Section 4 explicitly states "8-bit" with a pitfall reminder
- **FPGA source code:** `ADC_WIDTH = 8` in `ddc_400m.v` (the DDC module that receives ADC samples)

> **Pitfall 1 (from research): ADC Bit Width Confusion.** The AD9484 is frequently cited as "14-bit" in casual references. The AERIS-10 uses it as an **8-bit** ADC at 400 MSPS. All improvement calculations in this section use the 8-bit baseline. If an "improvement" from 14-to-16-bit shows only 12 dB gain, the wrong baseline has been used. The actual improvement from 8-to-14-bit is **36 dB of SQNR**.

| Parameter | Symbol | Value | Source |
|-----------|--------|-------|--------|
| Resolution | $b$ | 8 bits | [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md#ad9484-adc) Section 4; `ddc_400m.v` `ADC_WIDTH = 8` |
| Maximum sample rate | -- | 500 MSPS | AD9484 datasheet |
| Operating sample rate | $f_s$ | 400 MSPS | AD9523 OUT4/OUT5 clock; [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#400-mhz-adc-domain) Eq. (HW-FPGA-1) |
| ENOB | -- | ~7.5 bits typical | AD9484 datasheet at Nyquist input |
| Theoretical SQNR | -- | 49.9 dB | Eq. (NF-11) with $b = 8$ |
| SFDR | -- | ~48 dBFS typical | AD9484 datasheet at Nyquist input |
| Interface | -- | 8-bit parallel LVDS DDR | [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md#lvds-interface) Section 4.3 |
| FPGA interface module | -- | `ad9484_interface_400m.v` | IBUFDS + IDDR primitives; [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#fpga-module-inventory) Section 5 |

The theoretical SQNR for the 8-bit AD9484 follows from Eq. (NF-11) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#signal-to-quantization-noise-ratio):

$$
\text{SQNR}_\text{dB} = 6.02 \, b + 1.76~\text{dB} \tag{NF-11}
$$

For $b = 8$: $\text{SQNR} = 6.02 \times 8 + 1.76 = 49.9~\text{dB}$. This quantization noise floor at $-49.9~\text{dBFS}$ is documented as a "dominant constraint" on the AERIS-10 digital noise floor in both [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md#dynamic-range) Section 4.4 and [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#signal-to-quantization-noise-ratio) Section 5.2.

The ADC's effective noise figure $F_\text{ADC}$ is signal-level-dependent per Eq. (NF-12) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#effective-noise-figure-of-the-adc):

$$
F_\text{ADC} = 1 + \frac{\sigma_q^2}{k_B T_0 B_n G_\text{chain}} \tag{NF-12}
$$

where $G_\text{chain} = G_\text{LNA} \, G_\text{mix} \, G_\text{IF}$ is the total analog chain gain preceding the ADC. When $G_\text{chain}$ is insufficient to raise thermal noise above the quantization floor, $F_\text{ADC}$ becomes large and dominates the system noise figure.

### 4.2 Literature Survey

#### Candidate ADC Comparison

| Parameter | AD9484 (current) | AD9680 | AD9208 |
|-----------|-------------------|--------|--------|
| Resolution | 8 bits | **14 bits** | **14 bits** |
| Sample rate | 500 MSPS (rated) | 500 MSPS / 1 GSPS | 3 GSPS |
| SNR | ~48 dBFS | 65.3 dBFS | ~65 dBFS |
| ENOB | ~7.5 bits | 10.8 bits | ~10.5 bits |
| SFDR | ~48 dBFS | 82 dBFS | ~80 dBFS |
| Noise density | -- | $-154~\text{dBFS/Hz}$ | Similar |
| Interface | **LVDS parallel (8-bit DDR)** | **JESD204B** | **JESD204B** |
| JESD204B lanes | N/A | Up to 4 lanes per channel | Up to 8 lanes per channel |
| Channels | Single | Dual | Dual |
| Power consumption | ~0.5 W | ~1.5 W | ~2.5 W |
| Package | 32-lead LFCSP | 64-lead LFCSP | 196-ball BGA |

**Critical observation:** The AD9680 and AD9208 use **JESD204B serial interfaces**, NOT parallel LVDS. This is a fundamental interface change with major FPGA implications (see Section 4.4 below and Section 6 for the coupled FPGA upgrade analysis).

#### AD9680 as Primary Candidate

The AD9680 is the most suitable upgrade candidate for the AERIS-10:

- **500 MSPS per channel** at 14-bit resolution matches the current 400 MSPS operating rate
- **Dual channel** allows potential future dual-receiver architectures (e.g., sum/difference beamforming)
- **65.3 dBFS SNR** represents a substantial improvement over the AD9484's ~48 dBFS
- **JESD204B interface** at up to 10 Gbps per lane supports the full 14-bit data rate
- **Widely adopted** in radar and communications systems, with mature Xilinx IP support for JESD204B PHY

#### AD9208 as Future Option

The AD9208 targets higher-bandwidth applications (3 GSPS) and is relevant only if the AERIS-10 migrates to direct RF sampling (eliminating the mixer stage). At the current IF-based architecture with $f_s = 400~\text{MSPS}$, the AD9208 is significantly over-specified.

#### Academic and Datasheet References

- Analog Devices, "AD9680 Datasheet," 14-bit, 500 MSPS / 1 GSPS JESD204B dual ADC -- primary specification source
- Analog Devices, "AD9208 Datasheet," 14-bit, 3 GSPS JESD204B dual ADC -- future option reference
- Xilinx/AMD, "JESD204B Interface for UltraScale+ FPGAs," User Guide UG578 -- FPGA-side JESD204B implementation
- W. Kester, *The Data Conversion Handbook*, Analog Devices / Newnes, 2005, Chapter 3 -- ADC noise analysis and SQNR derivation

### 4.3 Gap Analysis

#### SQNR Improvement Calculation

Using Eq. (NF-11) to compute the SQNR improvement from higher-resolution ADCs:

$$
\Delta\text{SQNR} = 6.02 \times (b_\text{new} - b_\text{current})~\text{dB} \tag{HW-IMP-15}
$$

| ADC Resolution | $b$ | SQNR (Eq. NF-11) | $\Delta$SQNR vs 8-bit | Assessment |
|----------------|-----|-------------------|----------------------|------------|
| AD9484 (current) | 8 | 49.9 dB | 0 dB | Baseline |
| 14-bit (AD9680) | 14 | 86.0 dB | **+36.1 dB** | Primary candidate |
| 16-bit (hypothetical) | 16 | 98.1 dB | **+48.2 dB** | Future reference |

**This is the single largest potential improvement in the entire AERIS-10 system.** The 36.1 dB SQNR improvement from an 8-to-14-bit upgrade exceeds the impact of all other HWRES improvements combined:

- GaN PA upgrade (HWRES-01): +8--15 dB transmit power
- Array expansion (HWRES-05): +3--6 dB array gain
- Synthesizer improvement (HWRES-02): negligible (already best-in-class)
- AiP miniaturization (HWRES-03): ~0.5 dB interconnect loss reduction

#### Quantization Floor Impact on Doppler Detection

The connection between ADC resolution and Doppler detection was established in Section 2. The phase noise analysis showed SPNR values of 170+ dB at relevant Doppler offsets, while the 8-bit ADC quantization floor sits at only ~50 dB. The ADC quantization noise is the dominant limitation on Doppler detection sensitivity, exceeding the phase noise floor by more than **120 dB**.

A 14-bit ADC would lower the quantization floor to $-86~\text{dBFS}$, which remains well above the thermal noise floor for most operating conditions. This means the 36.1 dB improvement in quantization floor translates to a genuine 36.1 dB improvement in dynamic range, not merely a theoretical advantage masked by other noise sources.

#### Critical Caveat: Analog Chain Gain Requirement (Eq. NF-12)

The full SQNR improvement is realized **only if the analog chain gain $G_\text{chain}$ is sufficient to keep thermal noise above the new (much lower) quantization floor**. Per Eq. (NF-12) in [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md#effective-noise-figure-of-the-adc):

$$
F_\text{ADC} = 1 + \frac{\sigma_q^2}{k_B T_0 B_n G_\text{chain}}
$$

For the ADC noise figure to approach unity (quantization noise negligible), the thermal noise at the ADC input must dominate:

$$
k_B T_0 B_n G_\text{chain} \gg \sigma_q^2 \tag{HW-IMP-16}
$$

With a 14-bit ADC, $\sigma_q^2$ decreases by a factor of $2^{2(14-8)} = 4096$ (36 dB) compared to the 8-bit ADC. This dramatically relaxes the gain requirement -- the analog chain gain that was previously just sufficient to keep thermal noise above the 8-bit quantization floor now provides 36 dB of margin above the 14-bit floor.

However, a higher-resolution ADC also **exposes the analog chain noise that was previously masked by quantization**. If the analog chain has gain/noise characteristics that produce a noise floor between $-50~\text{dBFS}$ and $-86~\text{dBFS}$, a 14-bit ADC will faithfully digitize this noise rather than hiding it in the quantization floor. This is not a disadvantage -- it reveals the true analog chain performance and enables the system to benefit from future analog chain improvements.

> **Warning sign from research (Pitfall 1):** If someone claims the "improvement" from a 14-to-16-bit upgrade is 12 dB, they have used the wrong baseline. Starting from the actual 8-bit AD9484, the improvement is 36.1 dB (8-to-14-bit) or 48.2 dB (8-to-16-bit). The 12 dB figure would only be correct if the current ADC were already 14-bit, which it is not.

### 4.4 Feasibility Assessment

#### Interface Change: JESD204B (Pitfall 2)

This is the critical constraint that couples HWRES-04 to HWRES-06 (FPGA upgrade).

**Current interface:** The AD9484 uses an 8-bit parallel LVDS DDR interface, captured by the FPGA via `IBUFDS` + `IDDR` primitives in `ad9484_interface_400m.v` (documented in [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md#lvds-interface) Section 4.3 and [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#fpga-module-inventory) Section 5).

**Required interface:** The AD9680 uses JESD204B serial interface requiring high-speed serial transceivers (GTH or GTY) on the FPGA.

**Artix-7 XC7A100T transceiver status:** The XC7A100T has **zero** GTH or GTY transceivers (confirmed in [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#device-resources) Section 2.1 resource table). The FPGA **cannot natively support JESD204B**.

> **HWRES-04 (ADC upgrade) is DEPENDENT on HWRES-06 (FPGA upgrade).** The ADC cannot be upgraded to a 14-bit JESD204B device without simultaneously upgrading the FPGA to a device with GTH/GTY transceivers. See Section 6 for the FPGA upgrade analysis.

**Alternative: LVDS-interfaced high-resolution ADCs.** A few ADCs offer higher resolution with parallel LVDS interfaces (e.g., AD9265, 16-bit, 125 MSPS), but these do not meet the 400 MSPS sample rate requirement. At 400+ MSPS with 14-bit resolution, JESD204B is the industry-standard interface. No commercially available 14-bit, 400+ MSPS ADC offers a parallel LVDS interface.

#### Firmware and FPGA Impact

If the FPGA is upgraded to support JESD204B (see Section 6):

| Component | Current (AD9484) | Upgraded (AD9680) | Change Scope |
|-----------|------------------|-------------------|--------------|
| ADC interface module | `ad9484_interface_400m.v` (IBUFDS + IDDR) | JESD204B PHY + link layer IP | **Complete rewrite** |
| Data width | 8-bit | 14-bit | Entire pipeline width change |
| DDC module | `ddc_400m.v` (`ADC_WIDTH = 8`) | `ADC_WIDTH = 14` | Parameter change + multiplier resizing |
| CIC decimator | 8-bit input, 18-bit output (Eq. NF-15) | 14-bit input, 24-bit output | Wider accumulators |
| Matched filter | 18-bit data path | 24-bit data path | Wider multipliers, more BRAM |
| Doppler processor | 16-bit I/Q | 24-bit I/Q | Wider FFT butterfly |
| BRAM usage | ~101 BRAMs (current estimate) | Higher (wider data paths) | Increased utilization |
| DSP usage | ~88 DSPs (current estimate) | Higher (wider multipliers) | Increased utilization |

The pipeline data width change from 8-bit to 14-bit input propagates through all processing stages, increasing resource utilization. This is another reason the FPGA upgrade (HWRES-06) is required -- not only for JESD204B transceivers but also for the additional LUT, DSP, and BRAM resources needed for wider data paths.

#### Analog Chain Re-optimization

A 14-bit ADC with $-86~\text{dBFS}$ quantization floor will reveal analog chain imperfections (spurs, intermodulation products, thermal noise) that were previously hidden by the $-50~\text{dBFS}$ quantization floor of the 8-bit ADC. This may require:

- Anti-aliasing filter redesign (sharper transition band, lower passband ripple)
- IF amplifier gain optimization to position the thermal noise floor optimally within the ADC's dynamic range
- LO isolation improvement if synthesizer spurs fall within the ADC's expanded dynamic range
- PCB layout optimization to reduce coupling from digital noise into the analog signal path

These are standard engineering tasks for ADC upgrade projects, not fundamental obstacles.

### 4.5 Recommendations

**Priority ranking:** **HIGHEST** when combined with HWRES-06 (FPGA upgrade). The ADC upgrade cannot be pursued independently due to the JESD204B interface dependency.

**Key findings:**

1. The 8-to-14-bit ADC upgrade provides **36.1 dB SQNR improvement** -- the single largest potential improvement in the AERIS-10 system
2. The ADC quantization floor ($-49.9~\text{dBFS}$) is the dominant noise limitation, exceeding the phase noise floor by 120+ dB (Section 2 analysis)
3. The AD9680 (14-bit, 500 MSPS, JESD204B) is the primary candidate, with mature Xilinx JESD204B IP support
4. **CRITICAL: HWRES-04 depends on HWRES-06** -- the Artix-7 XC7A100T lacks the GTH transceivers required for JESD204B (Pitfall 2). ADC and FPGA must be upgraded as a **paired upgrade**
5. The wider data path (14-bit vs 8-bit) increases FPGA resource utilization, further necessitating the FPGA upgrade

**Recommended investigation steps (not implementation specifications):**

1. **Evaluate AD9680 + AU15P as a paired upgrade path** -- confirm JESD204B lane rate compatibility, verify Xilinx JESD204B PHY IP configuration for 14-bit, 400 MSPS operation
2. **Prototype on Opal Kelly XEM8305** (AU15P development board) with AD9680 evaluation board connected via FMC -- validate JESD204B link establishment and data integrity
3. **Characterize the analog chain noise floor** at the ADC input to determine the actual dynamic range improvement (vs theoretical 36.1 dB) -- if analog chain noise exceeds $-86~\text{dBFS}$, the realized improvement is less than the theoretical maximum
4. **Estimate updated FPGA resource utilization** with 14-bit data paths through the entire signal processing pipeline -- verify AU15P resources are sufficient or AU25P is required
5. **Assess IF amplifier gain requirements** -- ensure the analog chain gain positions the thermal noise floor optimally within the AD9680's 86 dB dynamic range

---

## 5. Antenna Array Expansion

*Requirement: HWRES-05*

### 5.1 Current State

The AERIS-10 uses a **16-element uniform linear array (ULA)** with half-wavelength spacing, controlled by four ADAR1000 beamformer ICs. The baseline array parameters from [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md):

| Parameter | Symbol | Value | Source |
|-----------|--------|-------|--------|
| Element count | $N$ | 16 | [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#16-element-array-geometry) Section 4 |
| Inter-element spacing | $d$ | $\lambda/2 = 14.3~\text{mm}$ at 10.5 GHz | Eq. (HW-ANT-6) |
| Total aperture | $L_\text{aperture}$ | 214.3 mm | Eq. (HW-ANT-7) |
| Beamwidth (broadside) | $\theta_{3\text{dB}}$ | ~6.3 deg | Eq. (HW-ANT-10) |
| Scan range (mechanical) | $\theta_\text{max}$ | $\pm 62.7°$ | Eq. (HW-ANT-3) |
| Scan range (practical) | -- | $\pm 33°$ (acceptable sidelobes) | Eq. (BF-16) in [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md) |
| Array gain | $G_\text{array}$ | $10\log_{10}(16) = 12.0~\text{dB}$ | Array factor theory |

**ADAR1000 SPI Topology** (from [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#spi-interface) Section 2.2):

| ADAR1000 Unit | DEV_ADDR | Elements | CS GPIO |
|---------------|----------|----------|---------|
| #1 | 0x00 | 0--3 | GPIOA Pin 0 |
| #2 | 0x01 | 4--7 | GPIOA Pin 1 |
| #3 | 0x02 | 8--11 | GPIOA Pin 2 |
| #4 | 0x03 | 12--15 | GPIOA Pin 3 |

The ADAR1000 DEV_ADDR field is **2 bits** (addresses 0x00--0x03), supporting a maximum of **4 devices per SPI bus**. The current system uses SPI1 on the STM32F746 with 4 individual chip selects. SPI4 is used for the AD9523 clock distribution and ADF4382A synthesizers. SPI2, SPI3, SPI5, and SPI6 are available on the STM32F746.

### 5.2 Literature Survey

#### Array Gain Scaling

Array gain for a uniformly weighted $N$-element ULA scales as $10\log_{10}(N)$ (from the array factor peak of Eq. (BF-3) in [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md)):

$$
G_\text{array}(N) = 10\log_{10}(N) \tag{HW-IMP-11}
$$

The radar range equation (Eq. FMCW-6 in [`01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md)) shows that maximum detection range scales with the square root of antenna gain (since the same antenna is used for transmit and receive, $G$ appears twice in the range equation, giving $R_\text{max} \propto G^{1/2}$):

$$
R_\text{max} \propto G_\text{array}^{1/2} \propto N^{1/2} \tag{HW-IMP-12}
$$

#### Beamwidth Scaling

From the half-power beamwidth expression Eq. (BF-10) in [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md):

$$
\theta_{3\text{dB}} \approx \frac{0.886\lambda}{Nd} \tag{BF-10}
$$

With $d = \lambda/2$ maintained for all array sizes, the beamwidth scales inversely with element count:

$$
\theta_{3\text{dB}} \approx \frac{0.886}{N \times 0.5} = \frac{1.772}{N} \quad \text{radians} \tag{HW-IMP-13}
$$

#### Scaling Analysis Table

| Parameter | 16 elements (current) | 32 elements | 64 elements |
|-----------|----------------------|-------------|-------------|
| ADAR1000 count | 4 | 8 | 16 |
| SPI buses required | 1 | 2 | 4 |
| Array gain $G_\text{array}$ | 12.0 dB | 15.1 dB (+3.0 dB) | 18.1 dB (+6.0 dB) |
| Beamwidth $\theta_{3\text{dB}}$ (broadside) | 6.3 deg | 3.2 deg | 1.6 deg |
| Aperture length $L_\text{aperture}$ | 214 mm (8.4 in) | 443 mm (17.4 in) | 900 mm (35.4 in) |
| Range multiplier ($N^{1/2}$) | 1.0x | 1.41x | 2.0x |
| ADTR1107 T/R modules | 16 | 32 | 64 |
| Total PA power (ADTR1107 at 316 mW) | 5.1 W | 10.1 W | 20.2 W |

#### Grating Lobe Analysis

With $d = \lambda/2$ maintained for all array sizes, the grating lobe condition Eq. (BF-16) in [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md) remains satisfied:

$$
\frac{d}{\lambda} = 0.5 < \frac{1}{1 + \sin\theta_\text{max}} \tag{BF-16}
$$

For the practical scan range of $\pm 33°$, the grating-lobe-free limit is $d/\lambda < 0.649$, providing **30% margin** above the half-wavelength spacing. Expanding the array to 32 or 64 elements at $d = \lambda/2$ does **not** introduce grating lobes -- the grating lobe condition depends only on $d/\lambda$ and the scan range, not on the number of elements.

The increased element count does, however, produce **narrower grating lobes** (proportional to $1/N$) if element spacing were to exceed $\lambda/2$, making proper spacing more critical for larger arrays.

### 5.3 Gap Analysis

#### SPI Bus Scaling Constraint (Pitfall 4)

The ADAR1000 DEV_ADDR is a **2-bit** hardware address field (bits [6:5] of the SPI transaction byte 0, documented in [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#spi-interface) Section 2.2). This limits addressing to a maximum of **4 ADAR1000 devices per SPI bus**.

**32-element expansion (8 ADAR1000 devices):**
- Requires **2 SPI buses** (4 devices per bus)
- SPI1 retains current 4 devices (elements 0--15)
- SPI2 or SPI3 added for new 4 devices (elements 16--31)
- STM32F746 SPI2 (PB10/PB14/PB15) or SPI3 (PB3/PB4/PB5) available
- Firmware change: `ADAR1000_Manager` extended to support dual-bus operation with bus selection per device group

**64-element expansion (16 ADAR1000 devices):**
- Requires **4 SPI buses** (4 devices per bus)
- SPI1 + SPI2 + SPI3 + SPI5 (or SPI6) allocated to ADAR1000 control
- STM32F746 has SPI1--SPI6 (6 total); SPI1 (ADAR1000) and SPI4 (AD9523/ADF4382A) currently used, leaving SPI2, SPI3, SPI5, SPI6 available -- sufficient for 64-element expansion
- Firmware change: significant -- quad-bus management, parallel SPI transfers, modified beam matrix structure

#### Physical Aperture Constraints

| Array Size | Aperture Length | Physical Assessment |
|------------|----------------|---------------------|
| 16 elements | 214 mm (8.4 in) | Fits both variants |
| 32 elements | 443 mm (17.4 in) | Fits Extended; tight for Nexus |
| 64 elements | 900 mm (35.4 in) | Requires platform redesign |

> **Variant Note: Physical Constraints**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | 32-element feasibility | **TIGHT** -- 443 mm linear aperture may exceed Nexus platform width; mechanical redesign likely required | **FEASIBLE** -- Extended platform has sufficient space for 443 mm aperture |
> | 64-element feasibility | **NOT FEASIBLE** -- 900 mm exceeds any reasonable compact platform dimension | **CHALLENGING** -- 900 mm aperture requires dedicated mounting structure |
> | Array configuration | Linear ULA (1D steering) | Could consider 2D subarray for elevation + azimuth |

#### Beam Steering Time Impact

The beam steering sequence (documented in [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#beam-steering-sequence) Section 3.6) programs all ADAR1000 devices sequentially before each chirp burst. The SPI programming time per beam position scales linearly with the number of ADAR1000 devices:

$$
T_\text{SPI}(N_\text{dev}) = N_\text{dev} \times T_\text{SPI,1} \tag{HW-IMP-14}
$$

where $T_\text{SPI,1}$ is the time to program a single ADAR1000 (4 channels x 2 registers/channel x 3 bytes/transaction at SPI clock rate). At the current SPI1 clock rate, programming 4 ADAR1000 devices is fast relative to the chirp timing. However:

- **32 elements (8 devices, 2 buses):** SPI buses can operate in parallel, so the effective programming time is $\max(T_\text{bus1}, T_\text{bus2})$, approximately equal to the current 4-device time if firmware uses DMA on both buses
- **64 elements (16 devices, 4 buses):** Four parallel SPI buses, each programming 4 devices -- effective time remains comparable to current if all buses operate concurrently

With 31 elevation positions and $M = 32$ chirps per position (16 long + 16 short), the total scan cycle includes $31 \times T_\text{SPI}$ SPI programming intervals. Parallel SPI operation is critical for maintaining scan cycle time as the array expands.

#### Power Budget Scaling

Each additional element requires one ADTR1107 T/R module (Nexus variant), scaling the PA power budget linearly:

| Array Size | ADTR1107 Count | Total PA Power | DC Power (est. 50% PAE) |
|------------|---------------|----------------|------------------------|
| 16 elements | 16 | 5.1 W | ~10 W |
| 32 elements | 32 | 10.1 W | ~20 W |
| 64 elements | 64 | 20.2 W | ~40 W |

The power management subsystem (documented in [`06_power_management.md`](../02_hardware/06_power_management.md)) would require higher-capacity voltage regulators and wider PCB power planes for the 5V PA supply rail.

### 5.4 Feasibility Assessment

| Factor | 32-Element Expansion | 64-Element Expansion |
|--------|---------------------|---------------------|
| SPI complexity | **MODERATE** -- 1 additional SPI bus | **HIGH** -- 3 additional SPI buses |
| PCB redesign | **MODERATE** -- extended antenna PCB, new SPI routing | **HIGH** -- entirely new PCB, potential multi-board |
| Firmware changes | **MODERATE** -- dual-bus SPI control, extended beam matrices ($31 \times 32$ per matrix) | **HIGH** -- quad-bus SPI, DMA parallelism, 4x beam matrix memory |
| Mechanical impact | **MODERATE** -- 2x aperture length (443 mm) | **HIGH** -- 4x aperture length (900 mm), platform redesign |
| Power budget | **MODERATE** -- 2x PA power (10 W total) | **HIGH** -- 4x PA power (20 W total), thermal management redesign |
| Component cost | **MODERATE** -- 16 additional ADTR1107 + 4 additional ADAR1000 | **HIGH** -- 48 additional ADTR1107 + 12 additional ADAR1000 |
| Performance gain | +3.0 dB array gain, 1.41x range | +6.0 dB array gain, 2.0x range |

> **Variant Note: Expansion Feasibility**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | 32-element | **FEASIBLE with mechanical redesign** -- compact platform needs wider enclosure for 443 mm aperture | **FEASIBLE** -- Extended platform accommodates 443 mm aperture |
> | 64-element | **NOT RECOMMENDED** -- 900 mm aperture incompatible with compact form factor; conflicts with Nexus design philosophy | **FEASIBLE with dedicated mount** -- Extended platform could support 900 mm with structural modifications |
> | Recommended path | 32-element maximum for Nexus | 32-element near-term; 64-element as future option |

### 5.5 Recommendations

**Priority ranking:** MEDIUM-HIGH -- Array expansion provides guaranteed, well-understood performance improvement with mature physics (all equations already derived in Phase 2).

**Key findings:**

1. **32-element expansion is the practical near-term upgrade path** -- moderate complexity, meaningful +3.0 dB array gain, and 1.41x range improvement with well-characterized SPI scaling
2. **64-element expansion is viable but requires platform redesign** -- the 900 mm aperture and quad-SPI bus architecture represent a significant engineering effort
3. **SPI bus scaling is the primary firmware constraint** -- the 2-bit ADAR1000 DEV_ADDR limits 4 devices per bus, requiring multi-bus SPI management for arrays beyond 16 elements
4. **Grating lobes are not a concern** -- with $d = \lambda/2$ maintained, grating lobes remain outside visible space for all scan angles within the $\pm 33°$ practical range (30% margin per Eq. BF-16)
5. **Power budget scales linearly** -- 32-element array requires ~20 W DC for PA supply, within typical platform power budgets

**Recommended investigation steps (not implementation specifications):**

1. **Prototype 32-element array on Extended platform** -- measure actual beam pattern, sidelobe levels, and scan performance vs theoretical predictions from Eq. (BF-8) and Eq. (BF-9)
2. **Implement dual-SPI firmware** -- extend `ADAR1000_Manager` to support SPI1 + SPI2 with DMA for parallel bus operation; verify beam steering time overhead is acceptable
3. **Evaluate mechanical mounting** -- assess whether the Nexus platform can accommodate a 443 mm aperture with acceptable structural rigidity and pointing stability
4. **Characterize mutual coupling** -- a 32-element array has different edge-element coupling patterns than a 16-element array; measure active element patterns and assess calibration requirements (reference [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md#element-pattern-and-mutual-coupling) Section 7)
5. **Cost-benefit analysis** -- compare the 1.41x range improvement from 32-element expansion against the 1.6--2.4x range improvement from GaN PA upgrade (HWRES-01) at equivalent cost

---

## 6. FPGA Upgrade Path

*Requirement: HWRES-06*

### 6.1 Current State

The AERIS-10 digital processing platform is the **Xilinx Artix-7 XC7A100T** FPGA (28 nm process), documented in [`05_fpga_board.md`](../02_hardware/05_fpga_board.md). The device resources from [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#device-resources) Section 2.1:

| Resource | Available | Symbol | Source |
|----------|-----------|--------|--------|
| Look-Up Tables (LUTs) | 63,400 | $N_\text{LUT}$ | [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#device-resources) Table 2.1 |
| Flip-Flops (FFs) | 126,800 | $N_\text{FF}$ | [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#device-resources) Table 2.1 |
| Block RAM (36 Kb each) | 135 | $N_\text{BRAM}$ | [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#device-resources) Table 2.1 |
| DSP48E1 Slices | 240 | $N_\text{DSP}$ | [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#device-resources) Table 2.1 |
| GTH/GTY Transceivers | **0** | -- | XC7A100T datasheet |
| Global Clock Buffers (BUFG) | 32 | -- | [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#device-resources) Table 2.1 |
| MMCM/PLL (CMTs) | 6 | -- | [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#device-resources) Table 2.1 |
| Process node | 28 nm | -- | Artix-7 DS181 |

**Estimated resource utilization** from [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#resource-utilization) Section 2.2 (theoretical estimates pending Vivado reports -- Open Question 3 from research):

| Resource | Estimated Used | Available | Utilization |
|----------|---------------|-----------|-------------|
| LUTs | ~16,500 | 63,400 | ~26% |
| DSP48E1 | ~88 | 240 | ~37% |
| BRAMs | ~101 | 135 | **~75%** |

> BRAM utilization is the most likely bottleneck due to FFT twiddle factor storage and chirp reference memories, as noted in [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#resource-utilization) Section 2.2.

**Clock domains** from [`05_fpga_board.md`](../02_hardware/05_fpga_board.md#clock-domains) Section 3:

| Domain | Frequency | Source | Key Modules |
|--------|-----------|--------|-------------|
| ADC | 400 MHz | AD9523 OUT4/5 (LVDS) | ADC interface, DDC front-end |
| DAC | 120 MHz | AD9523 OUT10/11 (LVCMOS) | Chirp TX, DAC interface |
| System | 100 MHz | AD9523 OUT6 (LVCMOS) | CIC, matched filter, FFT, Doppler |
| FT601 | 100 MHz | FT601 IC (external) | USB data, packet analyzer |

The critical architectural limitation is the **absence of high-speed serial transceivers** (GTH/GTY). The XC7A100T is a fabric-only FPGA with no multi-gigabit serial I/O capability, which prevents native support for JESD204B (required by all modern 14-bit, 400+ MSPS ADCs) and other high-speed serial protocols.

### 6.2 Literature Survey

#### Artix UltraScale+ Resource Comparison

| Resource | XC7A100T (current) | AU10P | AU15P | AU25P |
|----------|-------------------|-------|-------|-------|
| System Logic Cells | 101,440 | 96,250 | 170,100 | 308,437 |
| CLB LUTs | 63,400 | **44,000** | 77,760 | 141,000 |
| CLB Flip-Flops | 126,800 | 88,000 | 155,520 | 282,000 |
| Block RAM (36 Kb) | 135 | 100 | 144 | 300 |
| DSP Slices | 240 (DSP48E1) | 400 (DSP48E2) | 576 (DSP48E2) | 1,200 (DSP48E2) |
| Transceivers | **0** | **12 GTH** | **12 GTH** | **12 GTY** |
| CMTs | 6 | 3 | 3 | 4 |
| Max transceiver rate | N/A | 12.5 Gbps (GTH) | 12.5 Gbps (GTH) | 16.3 Gbps (GTY) |
| Process node | 28 nm | 16 nm | 16 nm | 16 nm |
| Core voltage | 1.0 V | 0.85 V | 0.85 V | 0.85 V |

Source: AMD/Xilinx Artix-7 DS181 and Artix UltraScale+ product selection guide.

**Critical observations:**

1. **AU10P has FEWER LUTs than XC7A100T** (44,000 vs 63,400). Despite being marketed as the "entry" Artix UltraScale+, the AU10P would reduce LUT headroom. It is **NOT a viable migration target** for the AERIS-10 unless the design can be significantly optimized to fit in fewer LUTs.

2. **AU15P is the minimum viable upgrade:** 77,760 LUTs (22% more than XC7A100T), 576 DSP slices (2.4x), 144 BRAMs (slightly more), and -- critically -- **12 GTH transceivers** enabling JESD204B for the ADC upgrade (HWRES-04).

3. **AU25P is the future-proof option:** 141,000 LUTs (2.2x), 1,200 DSPs (5x), 300 BRAMs (2.2x), and **GTY transceivers** at 16.3 Gbps. This provides substantial headroom for:
   - 14-bit ADC data paths (wider multipliers, deeper buffers)
   - Phase 5 software improvements: larger FFTs, more complex matched filters, potential ML inference (per research in `research/01_sw_algorithm_improvements.md` and `research/02_sw_pipeline_improvements.md`)
   - Array expansion (HWRES-05): more SPI controller instances for multi-bus operation

4. **DSP48E2 vs DSP48E1:** UltraScale+ DSP slices feature **27x18 multipliers** (vs 25x18 for Artix-7 DSP48E1), providing wider multiply operations. For a 14-bit ADC data path, the 27-bit input accommodates 24-bit processed data (14-bit ADC + CIC bit growth per Eq. NF-15) without requiring multi-DSP cascading.

5. **FT601 USB 3.0 compatibility:** The FT601's 32-bit FIFO interface operates at 100 MHz with LVCMOS33 I/O standard. Artix UltraScale+ HP (High-Performance) I/O banks support LVCMOS33, confirming compatibility. The **Opal Kelly XEM8305** development board demonstrates FT601 + AU15P integration, providing independent verification of this compatibility.

#### DSP Slice Architecture Comparison

| Feature | DSP48E1 (Artix-7) | DSP48E2 (UltraScale+) |
|---------|-------------------|-----------------------|
| Pre-adder | 25-bit | **27-bit** |
| Multiplier | 25 x 18 | **27 x 18** |
| Accumulator | 48-bit | 48-bit |
| Pre-adder mode | Add only | Add/subtract |
| Wide XOR | No | Yes (96-bit) |
| Cascade | 48-bit PCOUT | 48-bit PCOUT |

The wider pre-adder and multiplier in DSP48E2 directly benefit the signal processing pipeline when moving from 8-bit to 14-bit ADC data, as the intermediate products grow wider through the processing chain.

### 6.3 Gap Analysis

#### What the Current FPGA Cannot Do

1. **Support any ADC with JESD204B interface** -- zero transceivers means no high-speed serial interface. This directly blocks HWRES-04 (ADC upgrade), the single highest-impact improvement identified in this document.

2. **Run multiple FFT pipelines simultaneously** -- the current BRAM utilization of ~75% leaves insufficient room for parallel processing paths. A second 1024-point FFT requires approximately 20 additional BRAMs, exceeding the 34-BRAM remaining headroom.

3. **Support wider data paths** -- a 14-bit ADC with CIC bit growth produces 24-bit outputs (Eq. NF-15 with $b_\text{in} = 14$: $b_\text{out} = 14 + 5 \times 2 = 24~\text{bits}$). The wider data paths require more DSP slices for each multiply-accumulate operation and more BRAMs for each buffer.

4. **Implement advanced algorithms** -- Phase 5 software improvement research identified several high-impact algorithms (CFAR variants, Kalman filtering, MVDR beamforming) that are resource-limited on the current platform (per `research/02_sw_pipeline_improvements.md`).

#### What FPGA Upgrade Enables

1. **GTH/GTY transceivers unlock JESD204B** -- the key enabler for HWRES-04 (ADC upgrade). With 12 GTH lanes on AU15P, the FPGA can support multiple JESD204B links simultaneously.

2. **More DSP slices enable advanced processing:**
   - AU15P (576 DSPs): 2.4x current capacity -- supports 14-bit data paths, larger matched filters
   - AU25P (1,200 DSPs): 5x current capacity -- supports simultaneous FFT/CFAR processing, potential ML inference on processed data

3. **More BRAMs enable deeper buffers:**
   - AU15P (144 BRAMs): slight increase, adequate for 14-bit upgrade
   - AU25P (300 BRAMs): 2.2x current capacity -- enables larger range/Doppler maps, longer CPI integration, multi-bank interleaving

4. **16 nm process advantages:** Lower power consumption per logic cell, higher maximum clock frequencies, and UltraRAM (AU25P only) for large on-chip memory.

### 6.4 Feasibility Assessment

#### PCB Migration Complexity: HIGH (Pitfall 5)

> **Pitfall 5 (from research): FPGA Upgrade Without Clock Domain Migration Analysis.** If this analysis describes the FPGA upgrade as "straightforward" or "drop-in," the hardware integration has not been considered. The FPGA upgrade implies a new PCB, new constraint file, re-verified clock tree, and potentially new AD9523 clock outputs for JESD204B reference clocks.

The migration from Artix-7 to Artix UltraScale+ is **NOT a drop-in upgrade**. The following subsystems must be redesigned:

| Subsystem | Migration Impact | Effort |
|-----------|-----------------|--------|
| **PCB layout** | Different BGA package, different pin assignments, different I/O bank arrangement | Full PCB redesign |
| **Power management** | Core voltage changes from 1.0 V (Artix-7) to 0.85 V (UltraScale+); additional voltage rails for GTH transceivers (MGTAVCC 1.0V, MGTAVTT 1.2V) | New power tree design |
| **Constraint file** | Different BUFG architecture, different I/O standards for HP banks, new transceiver pin locations | Complete `.xdc` rewrite |
| **Clock tree** | Different MMCM/PLL architecture; JESD204B requires dedicated reference clocks (typically 125 MHz or device clock) from AD9523 | AD9523 reconfiguration, potential new clock outputs |
| **Configuration** | Different bitstream format, different JTAG chain, different SPI flash requirements | New configuration circuit |
| **I/O standards** | UltraScale+ HP I/O banks support different voltage levels; current LVCMOS33 interfaces must be mapped to compatible banks | I/O planning redesign |

**Voltage rail differences:**

| Rail | Artix-7 XC7A100T | UltraScale+ AU15P/AU25P |
|------|-------------------|-------------------------|
| Core (VCCINT) | 1.0 V | 0.85 V |
| Auxiliary (VCCAUX) | 1.8 V | 1.8 V |
| Block RAM (VCCBRAM) | 1.0 V | 0.85 V |
| I/O (VCCO) | 1.8 / 2.5 / 3.3 V (bank-dependent) | 1.0 -- 3.3 V (HP/HD banks) |
| GTH analog (MGTAVCC) | N/A | 1.0 V |
| GTH termination (MGTAVTT) | N/A | 1.2 V |

The GTH transceiver power rails (MGTAVCC, MGTAVTT) are new requirements that do not exist on the current Artix-7 board.

#### Clock Tree Redesign

The current AD9523 clock tree (documented in [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md#complete-clock-tree-table)) uses 12 of 14 available output channels. For JESD204B operation, additional clocks are needed:

- **Device clock** for JESD204B link: typically the ADC sample clock (400 MHz), already available from AD9523 OUT4/OUT5
- **Reference clock** for GTH transceiver PLL: may require a dedicated AD9523 output or a recovered clock from the JESD204B link
- **SYSREF clock** for JESD204B deterministic latency: requires a new low-frequency clock output (typically sample clock / N) from AD9523

The AD9523 has 2 unused outputs (OUT8, OUT12) that could potentially serve these roles, but the divider ratios and output formats must be verified against JESD204B timing requirements.

#### FT601 USB 3.0 Compatibility

The FT601 FIFO interface is architecture-agnostic:

| Parameter | Current (Artix-7) | Upgraded (AU15P/AU25P) | Compatibility |
|-----------|-------------------|------------------------|---------------|
| Data bus width | 32-bit | 32-bit | Compatible |
| Clock | 100 MHz (external) | 100 MHz (external) | Compatible |
| I/O standard | LVCMOS33 | LVCMOS33 (HD I/O bank) | Compatible |
| Interface protocol | FIFO read/write | FIFO read/write | Compatible |

The Opal Kelly XEM8305 (AU15P + FT601) confirms this compatibility in a production development board.

#### Firmware (Verilog) Migration

| Module Category | Migration Effort | Notes |
|-----------------|-----------------|-------|
| Processing pipeline (CIC, FFT, matched filter, Doppler) | **MODERATE** -- synthesizable RTL, mostly portable | May need DSP48E2 instantiation changes; parameterized designs adapt with updated constraints |
| ADC interface (`ad9484_interface_400m.v`) | **COMPLETE REWRITE** -- replaced by JESD204B PHY + link layer | New module using Xilinx JESD204B IP core |
| CDC modules (`cdc_modules.v`) | **LOW** -- standard synchronizer patterns are portable | Verify MTBF calculation (Eq. HW-FPGA-4) at UltraScale+ timing characteristics |
| USB interface (`usb_data_interface.v`) | **LOW** -- FIFO interface is architecture-independent | Verify timing constraints against AU15P I/O timing |
| Clock infrastructure (BUFGs, MMCMs) | **MODERATE** -- different buffer primitives | Replace `BUFG` instantiations with UltraScale+ equivalents (`BUFGCE`, `BUFGCTRL`) |
| Constraint file (`cntrt.xdc`) | **COMPLETE REWRITE** -- different pin assignments, I/O banks, timing models | New `.xdc` required for the target AU15P/AU25P package |

### 6.5 Recommendations

**Priority ranking:** **HIGH** -- the FPGA upgrade enables the highest-impact improvement in the system (HWRES-04, ADC upgrade with 36 dB SQNR improvement). Without the FPGA upgrade, the ADC cannot be changed.

**Key findings:**

1. **AU15P is the recommended minimum migration target:** 22% more LUTs than XC7A100T, 2.4x DSPs, comparable BRAMs, and -- critically -- **12 GTH transceivers** enabling JESD204B for HWRES-04
2. **AU25P is recommended if Phase 5 software improvements require significant additional resources:** 2.2x LUTs, 5x DSPs, 2.2x BRAMs provide substantial headroom for advanced processing
3. **AU10P is NOT viable** -- fewer LUTs (44K vs 63K) than the current XC7A100T, despite having GTH transceivers
4. **PCB migration complexity is HIGH** (Pitfall 5) -- different package, voltage rails, I/O banks, and configuration. This is NOT a drop-in upgrade; the entire board must be redesigned
5. **HWRES-06 should be paired with HWRES-04** for maximum system improvement -- upgrading the FPGA without upgrading the ADC wastes the GTH transceivers; upgrading the ADC is impossible without the FPGA upgrade
6. **Prototype before custom PCB** -- the Opal Kelly XEM8305 (AU15P + FT601) provides a validated development platform for JESD204B evaluation before committing to a custom board design

**Recommended investigation steps (not implementation specifications):**

1. **Prototype with Opal Kelly XEM8305** -- port the current signal processing pipeline to AU15P, verify functionality with the existing AD9484 (via LVDS), then connect AD9680 evaluation board via FMC for JESD204B validation
2. **Estimate AU15P resource utilization** -- resynthesize the current design for AU15P to establish actual (not theoretical) resource baseline, then estimate the additional resources for 14-bit data paths
3. **Evaluate AD9523 clock tree reconfiguration** -- determine JESD204B reference clock and SYSREF requirements, verify that OUT8 and OUT12 (currently unused) can serve these roles
4. **Assess AU15P vs AU25P** -- if estimated AU15P utilization with 14-bit data paths exceeds 70%, recommend AU25P for design margin
5. **Power budget analysis** -- estimate total power for AU15P/AU25P including GTH transceivers; verify compatibility with existing power supply architecture or identify required changes
6. **Clock tree verification** -- confirm that the existing 100/120/400 MHz clock domains can be reproduced on UltraScale+ with equivalent or better jitter performance

---

## 7. Cross-Topic Summary and Recommendations

### 7.1 Dependency Map

The six hardware upgrade topics are not independent. The following dependency relationships determine which upgrades can be pursued alone and which must be paired:

```
HWRES-06 (FPGA Upgrade)
    |
    |--- ENABLES ---> HWRES-04 (ADC Upgrade)
    |                     [JESD204B transceivers required]
    |
    +--- ENABLES ---> Phase 5 SW improvements
                          [More DSPs, BRAMs, LUTs]

HWRES-04 (ADC Upgrade) + HWRES-06 (FPGA Upgrade)
    = HIGHEST-IMPACT PAIRED UPGRADE (36 dB SQNR)

HWRES-01 (GaN Front-End)     --- INDEPENDENT ---
    [Nexus PA upgrade; Extended already has GaN PA]

HWRES-05 (Array Expansion)   --- INDEPENDENT ---
    [32-element: MODERATE complexity, no other upgrade needed]
    [64-element: may benefit from FPGA upgrade for more SPI controllers]

HWRES-02 (Synthesizer)       --- DIMINISHING RETURNS ---
    [ADF4382A already best-in-class; no replacement improves performance]

HWRES-03 (AiP Miniaturization) --- NEXT-GENERATION ---
    [Fundamental PCB redesign; Nexus-only; HIGH NRE cost]
```

**Key coupling:** HWRES-04 (ADC upgrade) **cannot** be pursued without HWRES-06 (FPGA upgrade) because the Artix-7 XC7A100T lacks GTH transceivers for JESD204B. Conversely, upgrading only the FPGA without the ADC wastes the new transceiver capability. These two upgrades deliver maximum value only as a **paired investment**.

**Independent upgrades:** HWRES-01 (GaN PA for Nexus) and HWRES-05 (array expansion) can each be pursued independently of the digital back-end upgrades. They affect the analog/RF domain and do not require FPGA or ADC changes.

### 7.2 Priority Ranking

| Rank | HWRES Topic | Impact | Complexity | Dependencies | Timeline | Rationale |
|------|-------------|--------|------------|-------------|----------|-----------|
| **1** | **HWRES-04 + HWRES-06** (ADC + FPGA) | **+36.1 dB SQNR** (highest in system) | **HIGH** (new PCB, FPGA, ADC, firmware) | Paired -- must be done together | Medium-term | Single largest improvement; addresses the dominant noise limitation (8-bit quantization floor) |
| **2** | **HWRES-05** (Array expansion to 32) | **+3.0 dB gain**, 1.41x range | **MODERATE** (2nd SPI bus, wider aperture, more T/R modules) | Independent | Near-term | Well-understood physics, mature components, guaranteed improvement |
| **3** | **HWRES-01** (GaN front-end for Nexus) | **+8--15 dB** transmit power, 1.6--2.4x range | **MODERATE** (hybrid PA+LNA, 28V supply, thermal management) | Independent (Nexus only; Extended already has GaN) | Near-term | Significant range improvement for Nexus variant; Extended variant architecture provides reference design |
| **4** | **HWRES-02** (Synthesizer phase noise) | **Negligible** (ADF4382A already best-in-class) | **LOW** (OCXO swap or loop filter tuning) | Independent | Near-term | Phase noise SPNR exceeds ADC quantization floor by 120+ dB; no synthesizer replacement improves system |
| **5** | **HWRES-03** (AiP miniaturization) | **~0.5 dB** interconnect loss, ~30% area reduction | **HIGH** (custom LTCC, $100K+ NRE) | Independent (Nexus only) | Next-generation | Form factor benefit only; Extended variant waveguide incompatible with AiP |

**Impact quantification summary:**

| Upgrade | Metric | Improvement | vs ADC Upgrade (36 dB) |
|---------|--------|-------------|----------------------|
| ADC 8-to-14-bit (HWRES-04) | SQNR | +36.1 dB | Baseline |
| GaN PA (HWRES-01, Nexus) | Transmit power | +8--15 dB | 22--42% of ADC impact |
| 32-element array (HWRES-05) | Array gain | +3.0 dB | 8% of ADC impact |
| Synthesizer (HWRES-02) | Phase noise | ~0 dB net improvement | 0% |
| AiP (HWRES-03) | Interconnect loss | ~0.5 dB | 1.4% of ADC impact |

### 7.3 Recommended Investigation Roadmap

#### Phase A: Near-Term Investigations

**Timeline:** 0--6 months. Can be pursued with current hardware plus evaluation boards.

1. **Prototype 32-element array on Extended platform** (HWRES-05)
   - Minimal risk: well-understood scaling, mature ADAR1000 components
   - Validates dual-SPI bus firmware, measures actual beam pattern vs theoretical
   - Provides immediate +3 dB gain and 1.41x range improvement
   - **Deliverable:** Measured beam patterns, SPI timing verification, range improvement validation

2. **Evaluate AD9680 + AU15P on Opal Kelly XEM8305** (HWRES-04 + HWRES-06)
   - XEM8305 provides pre-validated AU15P + FT601 platform
   - Connect AD9680 evaluation board via FMC for JESD204B link testing
   - Port signal processing pipeline to AU15P, verify resource utilization
   - **Deliverable:** JESD204B link status, resource utilization report, data integrity verification

3. **Characterize analog chain noise floor** (supports HWRES-04 assessment)
   - Measure actual noise floor at ADC input to determine realized dynamic range improvement
   - If analog noise exceeds $-86~\text{dBFS}$, the ADC upgrade's realized improvement is less than 36 dB
   - **Deliverable:** Measured noise floor spectrum, comparison against 8-bit and 14-bit quantization floors

#### Phase B: Medium-Term Development

**Timeline:** 6--18 months. Requires custom PCB design and fabrication.

1. **Custom PCB with AU15P + AD9680** (HWRES-04 + HWRES-06)
   - Full PCB redesign incorporating UltraScale+ power management, JESD204B reference clocks, and 14-bit data paths
   - Leverage Phase A evaluation results for resource estimation and clock tree configuration
   - **Deliverable:** Production-ready PCB design, verified JESD204B operation, validated signal processing pipeline with 14-bit data

2. **32-element array integration** (HWRES-05)
   - Integrate validated 32-element array (from Phase A prototype) with production radar system
   - Mechanical and thermal qualification
   - **Deliverable:** 32-element production array, calibration procedures, validated performance

3. **GaN PA evaluation for Nexus** (HWRES-01)
   - If Phase A results confirm Nexus range improvement is needed beyond array expansion
   - Leverage Extended variant's QPA2962 + bias circuitry as reference design
   - **Deliverable:** Nexus variant with hybrid GaN PA, thermal management solution

#### Phase C: Next-Generation Options

**Timeline:** 18+ months. Requires fundamental platform redesign.

1. **AiP evaluation with LTCC fabricator** (HWRES-03)
   - Only pursue after higher-priority upgrades (ADC, FPGA, array) have been implemented
   - Contact Kyocera, TDK, or VIA Electronic for ADAR1000 + ADTR1107 feasibility study
   - **Deliverable:** LTCC prototype modules, measured RF performance, cost assessment

2. **64-element array feasibility** (HWRES-05 extension)
   - Requires platform redesign for 900 mm aperture
   - Quad-SPI bus architecture (4 buses x 4 ADAR1000 devices)
   - Only relevant for Extended variant (Nexus platform too compact)
   - **Deliverable:** Mechanical design, SPI firmware architecture, cost-benefit analysis

### 7.4 Open Questions

The following open questions from the Phase 6 research remain unresolved and affect specific upgrade paths:

| # | Question | Affects | Blocking? | Resolution Path |
|---|----------|---------|-----------|-----------------|
| 1 | ADTR1107 full specs at 10.5 GHz (PA P1dB, LNA IP3, switching time) | HWRES-01 (GaN comparison baseline) | No -- qualitative conclusions hold | Extract from datasheet PDF in repository |
| 2 | ADF4382A phase noise at exact offsets from 10.5 GHz carrier | HWRES-02 (Doppler floor validation) | No -- FOM-based estimates show >120 dB margin | Extract from datasheet phase noise plots |
| 3 | Vivado actual resource utilization vs theoretical estimates | HWRES-06 (AU15P vs AU25P sizing) | Partially -- affects AU15P adequacy determination | Run Vivado synthesis on current design; or use Phase A XEM8305 evaluation |
| 4 | IF amplifier presence/absence in receive chain | HWRES-04 (analog chain gain assessment) | No -- analog chain re-optimization needed regardless | Board schematic review |
| 5 | GaN vs SiGe per-element cost at relevant quantities (16--64 units) | HWRES-01 (cost-benefit) | No -- qualitative assessment sufficient for research phase | Vendor quotes (not in scope for documentation) |

**Questions 1 and 2** are documentation-level questions resolvable by extracting datasheet data. They do not block any upgrade decision because the qualitative conclusions (GaN advantage is PA power, not NF; phase noise is not the Doppler bottleneck) hold regardless of the precise numerical values.

**Question 3** partially blocks the AU15P vs AU25P selection. Phase A evaluation on the XEM8305 will resolve this by providing actual synthesis results.

---

## References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- symbol definitions for $F$, $G$, $P_t$, $\mathcal{L}(f_m)$
- [Parameter Table](../00_notation/parameter_table.md) -- canonical numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Phase 2 Physics Cross-References
- [`01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md) -- radar range equation Eq. (FMCW-6), $R_\text{max} \propto P_t^{1/4}$
- [`05_noise_analysis.md`](../01_physics/05_noise_analysis.md) -- Friis cascade Eq. (NF-7), AERIS-10 chain Eq. (NF-8), SQNR Eq. (NF-11)
- [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md) -- array factor Eq. (BF-3), beamwidth Eq. (BF-10), grating lobe analysis Eq. (BF-16), element pattern Eq. (BF-17)

### Phase 3 Hardware Cross-References
- [`02_rf_frontend.md`](../02_hardware/02_rf_frontend.md) -- ADTR1107 baseline, LT5552 mixer, AD9484 ADC, cascaded NF reference Eq. (HW-RF-4)
- [`03_frequency_synthesis.md`](../02_hardware/03_frequency_synthesis.md) -- ADF4382A synthesizers, AD9523 clock tree, phase noise Eq. (HW-FS-7) through Eq. (HW-FS-8)
- [`04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md) -- ADAR1000 beamformer, 16-element array geometry, SPI topology Section 2.2, beam steering Section 3
- [`05_fpga_board.md`](../02_hardware/05_fpga_board.md) -- XC7A100T resources, clock domains

### Component Datasheets and Product Pages
- ADTR1107 -- 8--16 GHz integrated T/R front-end module ([Analog Devices product page](https://www.analog.com/en/products/adtr1107.html))
- QPA2962 -- 6--18 GHz 10 W GaN MMIC power amplifier ([Qorvo](https://www.qorvo.com))
- ADF4382A -- 62.5 MHz to 21 GHz microwave wideband synthesizer ([Analog Devices product page](https://www.analog.com/en/products/adf4382a.html))
- LMX2820 -- 45 MHz to 22.6 GHz wideband synthesizer, FOM $-236~\text{dBc/Hz}$ ([Texas Instruments product page](https://www.ti.com/product/LMX2820))
- AD9484 -- 8-bit, 500 MSPS ADC ([Analog Devices product page](https://www.analog.com/en/products/ad9484.html))
- AD9680 -- 14-bit, 500 MSPS / 1 GSPS dual ADC, JESD204B interface ([Analog Devices product page](https://www.analog.com/en/products/ad9680.html))
- AD9208 -- 14-bit, 3 GSPS dual ADC, JESD204B interface ([Analog Devices product page](https://www.analog.com/en/products/ad9208.html))
- AD9523-1 -- Dual-PLL 12-output clock distribution IC ([Analog Devices](https://www.analog.com/en/products/ad9523-1.html))
- XC7A100T -- Artix-7 FPGA (DS181: Artix-7 Data Sheet, [AMD/Xilinx](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/artix-7.html))
- Artix UltraScale+ -- AU10P, AU15P, AU25P FPGA family ([AMD product selection guide](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/artix-ultrascale-plus.html))
- Opal Kelly XEM8305 -- AU15P + FT601 USB 3.0 development board ([Opal Kelly](https://www.opalkelly.com/products/fpga-integration/xem8305))
- ADAR1000 Datasheet -- X/Ku-band 4-channel analog beamformer, 2-bit DEV_ADDR, 7-bit phase resolution ([Analog Devices](https://www.analog.com/media/en/technical-documentation/data-sheets/adar1000.pdf))

### Industry and Academic References
- Altum RF, "Front-End Components for X/Ku Band Phased Array Radar," Nov 2025 -- GaN/SiGe comparison landscape
- Cadence, "LTCC Transmit-Receive X-Band Module with Phased Array Antenna," Application Note -- AiP dimensions and performance
- ResearchGate, "X-Band Transmit/Receive Module MMIC Chip-Set Based on Emerging GaN and SiGe Technologies" -- GaN vs SiGe comparison
- Qorvo, "X-Band Radar: Driving Defense Applications with Beamforming, GaN, and GaAs Technology" -- Industry perspective
- R. E. Best, *Phase-Locked Loops: Design, Simulation, and Applications*, 6th ed., McGraw-Hill, 2007 -- PLL phase noise theory
- D. B. Leeson, "A Simple Model of Feedback Oscillator Noise Spectrum," *Proceedings of the IEEE*, vol. 54, no. 2, 1966 -- Leeson's oscillator noise model
- B. Razavi, "A Study of Phase Noise in CMOS Oscillators," *IEEE JSSC*, vol. 31, no. 3, 1996 -- Oscillator phase noise analysis
- W. Kester, *The Data Conversion Handbook*, Analog Devices / Newnes, 2005 -- ADC noise analysis, SQNR derivation, converter interface design
- Xilinx/AMD, "JESD204B Interface for UltraScale+ FPGAs," User Guide UG578 -- JESD204B PHY and link layer implementation
- Xilinx/AMD, "UltraScale Architecture DSP Slice," User Guide UG579 -- DSP48E2 architecture and capabilities
- MDPI, "Design of X-Band TR Module Based on LTCC," *Electronics*, vol. 12, 2023 -- LTCC miniaturization for X-band T/R modules
- IEICE, "Integrated X-band phased array antenna with LTCC 3D T/R module," *IEICE Electronics Express*, vol. 17, no. 4, 2020 -- 3D LTCC integration with anodized aluminum multilayer
- Mailloux, R.J., *Phased Array Antenna Handbook*, 3rd ed., Artech House, 2018 -- Array scaling, grating lobes, mutual coupling
