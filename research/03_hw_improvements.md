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

*Placeholder -- to be completed in Task 2.*

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
- LMX2820 -- 45 MHz to 22.6 GHz wideband synthesizer ([Texas Instruments product page](https://www.ti.com/product/LMX2820))
- AD9680 -- 14-bit, 500 MSPS / 1 GSPS dual ADC ([Analog Devices product page](https://www.analog.com/en/products/ad9680.html))

### Industry and Academic References
- Altum RF, "Front-End Components for X/Ku Band Phased Array Radar," Nov 2025 -- GaN/SiGe comparison landscape
- Cadence, "LTCC Transmit-Receive X-Band Module with Phased Array Antenna," Application Note -- AiP dimensions and performance
- ResearchGate, "X-Band Transmit/Receive Module MMIC Chip-Set Based on Emerging GaN and SiGe Technologies" -- GaN vs SiGe comparison
- Qorvo, "X-Band Radar: Driving Defense Applications with Beamforming, GaN, and GaAs Technology" -- Industry perspective
