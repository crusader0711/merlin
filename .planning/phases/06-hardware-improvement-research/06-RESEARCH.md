# Phase 6: Hardware Improvement Research - Research

**Researched:** 2026-03-14
**Domain:** RF/Antenna/ADC/FPGA hardware upgrade paths for X-band FMCW phased array radar
**Confidence:** MEDIUM-HIGH

## Summary

Phase 6 produces a single research document (`research/03_hw_improvements.md`) surveying six hardware upgrade paths for the AERIS-10 radar system. Every recommendation must trace its impact through the documented noise figure chain (Eq. NF-8 in `01_physics/05_noise_analysis.md`) and address both AERIS-10 variants (Nexus 3 km / Extended 20 km). This is a documentation-only phase -- no implementation specifications, only feasibility assessments and recommended investigation steps.

The six research topics span three system layers: RF front-end (HWRES-01 GaN vs SiGe, HWRES-02 synthesizer phase noise), antenna/packaging (HWRES-03 AiP miniaturization, HWRES-05 array expansion), and digital back-end (HWRES-04 ADC resolution, HWRES-06 FPGA upgrade). Each topic follows the mandated structure: Current State / Literature Survey / Gap Analysis / Feasibility / Recommendations. The existing hardware documentation (Phase 3) provides all the baseline parameters needed -- component specs, noise chain, clock tree, FPGA resources -- so each research section can open with a precise current-state summary referencing those documents.

**Primary recommendation:** Structure the research document as six self-contained sections within a single file, each opening with a quantitative current-state baseline from Phase 3 documentation, followed by a literature survey with specific part numbers and specifications, gap analysis against system requirements, and a feasibility verdict with noise figure impact.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| HWRES-01 | GaN vs SiGe front-end comparison (output power, NF, die size at X-band vs ADTR1107) | ADTR1107 baseline specs now confirmed (2.5 dB NF, 18 dB RX gain, 25 dBm Psat); GaN alternatives identified with X-band specs; noise figure chain impact quantifiable via Eq. NF-8 |
| HWRES-02 | Frequency synthesizer phase noise improvements (fractional-N PLL, Doppler floor) | ADF4382A FOM -239 dBc/Hz documented; competing LMX2820 FOM -236 dBc/Hz identified; Doppler floor derivation from phase noise requires existing physics docs |
| HWRES-03 | Antenna-in-Package (AiP) miniaturization (3D-stacked T/R, LTCC, ADAR1000+ADTR1107 compatibility) | LTCC X-band AiP implementations found (14.3x24.5x3.55 mm); compatibility with ADAR1000 4-channel architecture researchable from beamformer docs |
| HWRES-04 | Higher-resolution ADC options (14-to-16-bit, FPGA interface impact, SNR improvement) | AD9484 8-bit baseline documented; AD9680 14-bit 500 MSPS identified (SNR 65.3 dBFS, JESD204B); SNR improvement calculable from Eq. NF-11 |
| HWRES-05 | Antenna array expansion (16-to-32/64, ADAR1000 cascading, PCB constraints, grating lobes) | Current 16-element ULA with d=lambda/2 documented; ADAR1000 2-bit address supports 4 devices per SPI bus; grating lobe analysis in Eq. BF-10 |
| HWRES-06 | FPGA upgrade path (Artix UltraScale+, resource comparison, PCB migration, USB 3.0 compatibility) | XC7A100T baseline documented (63,400 LUTs, 240 DSPs, 135 BRAMs); AU25P specs found (141,000 LUTs, 1,200 DSPs, 300 BRAMs); FT601 compatible with AU+ family |
</phase_requirements>

## Standard Stack

This phase produces Markdown documentation, not code. The "stack" is the documentation toolchain established in earlier phases plus the research methodology.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| GitHub Markdown + MathJax | N/A | Primary document format | Consistent with all prior phases; equations render natively |
| Zotero | v7 | IEEE citation management | Research phase requires academic references; BibTeX export for consistency |
| Parameter Table | N/A | Single source of truth for numerical values | All current-state baselines reference `parameter_table.md` |

### Supporting
| Tool | Purpose | When to Use |
|------|---------|-------------|
| Component datasheets (PDF) | Primary specs for current and candidate components | Every comparison table must cite datasheet values |
| Noise figure chain (Eq. NF-8) | Quantitative impact assessment | Every recommendation must show NF delta |

## Architecture Patterns

### Document Structure (Single File)
```
research/
  03_hw_improvements.md      # All 6 HWRES topics in one file
```

### Section Pattern (Repeated 6 Times)
Each HWRES section follows this structure:

```markdown
## N. [Topic Title]

### N.1 Current State
- Baseline specs from Phase 3 hardware docs (with cross-references)
- Current noise figure contribution (reference Eq. NF-8)
- Variant differences (Nexus vs Extended)

### N.2 Literature Survey
- Candidate components with specific part numbers and specs
- Academic references for advanced techniques
- Comparison tables: current vs candidates

### N.3 Gap Analysis
- What the current system cannot do
- What the upgrade enables
- Quantitative improvement (dB, range, resolution)

### N.4 Feasibility Assessment
- Integration complexity (PCB, firmware, FPGA changes)
- Cost and availability considerations
- Risk factors

### N.5 Recommendations
- Recommended next investigation steps (NOT implementation specs)
- Priority ranking relative to other HWRES topics
```

### Cross-Reference Pattern
Every section must reference:
1. The relevant Phase 3 hardware document for baseline values
2. The noise analysis document (`01_physics/05_noise_analysis.md`) for NF impact
3. The parameter table for canonical system values
4. At least one primary source (datasheet or peer-reviewed paper)

### Anti-Patterns to Avoid
- **Writing implementation specifications:** PROJECT.md explicitly excludes implementation. End with "feasibility assessment" and "recommended investigation steps," not design specs or schematics.
- **Unsourced performance claims:** Every numerical spec must cite a datasheet, paper, or documented measurement. No "approximately" without a source.
- **Ignoring variant differences:** Both Nexus (ADTR1107, 1W, 3km) and Extended (QPA2962, 10W, 20km) must be addressed. Some upgrades affect one variant more than the other.
- **Comparing against wrong ADC baseline:** The AD9484 is 8-bit, NOT 14-bit. The project documentation explicitly corrects this common confusion (see `02_rf_frontend.md` Section 4 pitfall reminder).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Noise figure impact calculation | Custom derivation | Eq. NF-8 from `05_noise_analysis.md` with substituted values | Already derived and validated in Phase 2 |
| Grating lobe analysis for expanded array | New derivation | Eq. BF-10 from `03_beamforming_theory.md` with updated N and d | Already derived with ADAR1000 quantization effects |
| SNR improvement from ADC upgrade | Ad-hoc formula | Eq. NF-11 (SQNR = 6.02b + 1.76 dB) | Standard formula already documented |
| Range improvement estimate | Independent derivation | Radar range equation Eq. FMCW-6 with updated parameters | R_max proportional to (P_t G^2)^(1/4), already documented |

**Key insight:** Phase 2 and Phase 3 have already established all the mathematical framework needed to quantify improvements. The research document should substitute candidate component values into existing equations, not re-derive them.

## Common Pitfalls

### Pitfall 1: ADC Bit Width Confusion
**What goes wrong:** The AD9484 is frequently cited as "14-bit" in casual references. The AERIS-10 uses it as an 8-bit ADC at 400 MSPS. HWRES-04 compares upgrades to 14-bit and 16-bit, which means the actual improvement is from 8 bits (not 14 bits).
**Why it happens:** Multiple sources list the AD9484 as supporting 14-bit mode; the system uses 8-bit mode.
**How to avoid:** Always reference `02_rf_frontend.md` Section 4 and `ddc_400m.v` ADC_WIDTH = 8 as the ground truth.
**Warning signs:** If the "improvement" from 14-to-16-bit shows only 12 dB gain, someone is using the wrong baseline. The actual improvement from 8-to-14-bit is 36 dB of SQNR.

### Pitfall 2: Ignoring JESD204B Interface Change
**What goes wrong:** Higher-resolution ADCs (14-bit+) at 500 MSPS use JESD204B serial interfaces, not parallel LVDS. This requires FPGA transceivers (GTH/GTY), which Artix-7 XC7A100T does not have.
**Why it happens:** Researchers compare ADC specs without checking the digital interface.
**How to avoid:** HWRES-04 (ADC upgrade) and HWRES-06 (FPGA upgrade) are tightly coupled. Document the interface dependency explicitly.
**Warning signs:** If the ADC upgrade is presented as "drop-in," the interface has been overlooked.

### Pitfall 3: GaN Noise Figure Assumption
**What goes wrong:** GaN PAs have excellent output power but GaN LNAs typically have higher noise figures than SiGe or GaAs LNAs. Recommending GaN for the entire T/R module without separating PA and LNA analysis leads to incorrect NF predictions.
**Why it happens:** "GaN is better" oversimplifies the technology tradeoff.
**How to avoid:** Analyze PA path (where GaN excels in Pout) separately from LNA path (where SiGe/GaAs may retain NF advantage). The ADTR1107 already achieves 2.5 dB NF -- verify any GaN LNA alternative matches this.
**Warning signs:** If a GaN T/R module shows worse NF than the ADTR1107, the LNA stage needs separate evaluation.

### Pitfall 4: Array Expansion Without SPI Bandwidth Check
**What goes wrong:** Doubling the array to 32 elements means 8 ADAR1000 devices. The ADAR1000 2-bit DEV_ADDR field supports only 4 devices per SPI bus. Expanding to 32 elements requires a second SPI bus or SPI multiplexing.
**Why it happens:** Element count focus neglects control path scaling.
**How to avoid:** Document SPI bus topology changes alongside antenna element count. Reference `04_antenna_beamforming.md` Section 2.2 for the current 4-device SPI mapping.
**Warning signs:** If 32/64 element expansion discusses only RF performance without addressing SPI control, the analysis is incomplete.

### Pitfall 5: FPGA Upgrade Without Clock Domain Migration Analysis
**What goes wrong:** Artix UltraScale+ uses different I/O banks, clock routing, and BUFG architectures than Artix-7. Direct pin-for-pin migration is not possible.
**Why it happens:** Resource count comparison (more LUTs, more DSPs) overshadows the PCB and clock tree redesign required.
**How to avoid:** Document that FPGA upgrade implies new PCB, new constraint file, re-verified clock tree, and potentially new AD9523 clock outputs for JESD204B reference clocks.
**Warning signs:** If FPGA upgrade is described as "straightforward" or "drop-in," the analysis has not considered the hardware integration.

### Pitfall 6: Phase Noise Impact Without Doppler Floor Derivation
**What goes wrong:** Citing synthesizer phase noise specs without computing the actual Doppler detection floor improvement provides no actionable insight.
**Why it happens:** Phase noise is specified at fixed offsets (100 kHz, 1 MHz) but Doppler floor depends on integration time, PRF, and chirp parameters.
**How to avoid:** Derive the Doppler floor from phase noise using the system's actual chirp parameters (T_c1 = 30 us, T_c2 = 0.5 us, M = 32 chirps/position).
**Warning signs:** If phase noise improvement is stated as "X dB better" without translating to minimum detectable velocity, the analysis stops short.

## Code Examples

This phase produces documentation, not code. However, the following equation substitution patterns are critical:

### Noise Figure Impact of LNA Upgrade
```
Source: 01_physics/05_noise_analysis.md Eq. NF-8

Current ADTR1107 baseline:
  F_LNA = 2.5 dB => F_LNA_lin = 10^(2.5/10) = 1.778
  G_LNA = 18 dB  => G_LNA_lin = 10^(18/10)  = 63.1

For any candidate LNA with F_new, G_new:
  Delta_F_sys = (F_new_lin - F_LNA_lin)
              + (F_mix - 1)(1/G_new_lin - 1/G_LNA_lin)
              + ...

Positive Delta_F = degradation; Negative = improvement
```

### SNR Improvement from ADC Upgrade
```
Source: 01_physics/05_noise_analysis.md Eq. NF-11

Current AD9484 (8-bit):  SQNR = 6.02*8  + 1.76 = 49.9 dB
14-bit ADC:               SQNR = 6.02*14 + 1.76 = 86.0 dB
16-bit ADC:               SQNR = 6.02*16 + 1.76 = 98.1 dB

Improvement: 36.1 dB (8->14) or 48.2 dB (8->16)
```

### Array Gain from Element Expansion
```
Source: 01_physics/03_beamforming_theory.md

Array gain scales as 10*log10(N):
  16 elements: 12.0 dB
  32 elements: 15.1 dB  (+3.0 dB)
  64 elements: 18.1 dB  (+6.0 dB)

Range improvement (R_max proportional to G^(1/2)):
  32 elements: 1.41x range increase
  64 elements: 2.0x range increase
```

## State of the Art

### HWRES-01: GaN vs SiGe Front-End

**Current component:** ADTR1107 (Analog Devices)
- Technology: SiGe BiCMOS
- Frequency: 6-18 GHz
- LNA noise figure: 2.5 dB (confirmed from datasheet)
- LNA gain: 18 dB (small signal)
- PA saturated output power: 25 dBm (~316 mW) per element
- Package: Compact integrated T/R module with SPDT switch

**GaN landscape at X-band (2025):**

| Parameter | ADTR1107 (SiGe) | GaN T/R (typical) | Impact |
|-----------|------------------|--------------------|--------|
| PA Psat | 25 dBm (316 mW) | 33-40 dBm (2-10 W) | +8-15 dB transmit power |
| LNA NF | 2.5 dB | 1.5-3.0 dB (GaN LNA) | Marginal NF change |
| LNA Gain | 18 dB | 15-25 dB | Comparable |
| Integration | Single IC (PA+LNA+SW) | Separate PA + LNA ICs typical | Higher component count |
| Die size | Small (SiGe process) | Larger (GaN on SiC) | PCB area increase |
| Supply voltage | 5V | 24-28V (GaN PA) | Power management redesign |

**Key finding:** GaN's advantage is primarily in transmit power, not receive NF. The ADTR1107's 2.5 dB NF is competitive with GaN LNAs. A hybrid approach (GaN PA + SiGe/GaAs LNA) preserves the NF advantage while gaining transmit power -- this is exactly what the Extended variant already does with the QPA2962 GaN PA.

**Industry trend (2025-2026):** Hybrid GaN PA + SiGe beamformer architectures are the dominant approach for new X-band phased arrays. Pure GaN T/R modules exist but cost significantly more per element.

**Confidence:** MEDIUM-HIGH (ADTR1107 specs confirmed from product page; GaN specs are typical ranges from multiple sources, not single-device datasheets)

### HWRES-02: Frequency Synthesizer Phase Noise

**Current component:** ADF4382A (Analog Devices)
- Reference: 300 MHz from AD9523
- Output: 10.5 GHz (TX) / 10.38 GHz (RX)
- PLL figure of merit: -239 dBc/Hz
- VCO range: 11.5-21 GHz (fundamental)
- Fractional-N with FRAC1/FRAC2/MOD2

**Competing synthesizers:**

| Parameter | ADF4382A | LMX2820 (TI) |
|-----------|----------|---------------|
| FOM | -239 dBc/Hz | -236 dBc/Hz |
| Frequency range | 62.5 MHz - 21 GHz | 45 MHz - 22.6 GHz |
| Integrated jitter | Ultra-low (spec TBD from datasheet) | Competitive |
| Max PFD freq | 625 MHz (integer mode) | High (TBD) |

**Key finding:** The ADF4382A already represents best-in-class phase noise performance. The 3 dB FOM advantage over LMX2820 translates to meaningfully lower Doppler floor. Phase noise improvements are more likely to come from better reference oscillator (OCXO upgrade) or clean-up PLL loop filter optimization than from synthesizer replacement.

**Doppler floor connection:** Phase noise at offset f_m from carrier directly sets the minimum detectable Doppler shift. With M=32 coherent integrations at each beam position, the effective phase noise floor improves by ~15 dB (10*log10(32)). The research document must derive the actual minimum detectable velocity from the ADF4382A phase noise profile at the system's offset frequencies.

**Confidence:** MEDIUM (FOM values confirmed; detailed phase noise at specific offsets requires full datasheet graphs which were not extractable)

### HWRES-03: Antenna-in-Package (AiP) Miniaturization

**Current architecture:**
- ADAR1000 beamformer ICs (4 units x 4 channels = 16 elements)
- ADTR1107 T/R modules (16 units, separate packages)
- PCB-level integration with discrete components
- Current aperture: ~214 mm linear (16 elements at 14.3 mm spacing)

**AiP landscape at X-band:**

| Implementation | Package Size | Technology | Performance |
|---------------|-------------|------------|-------------|
| LTCC X-band AiP (Cadence ref) | 14.3 x 24.5 x 3.55 mm | LTCC with air cavities | RX gain >30 dB, TX EIRP 32-38.5 dBm |
| 3D X-band T/R module | ~20 x 20 x 3.7 mm | Anodized aluminum multilayer | 4-channel integrated |
| Miniaturized LTCC T/R | Various | LTCC 4-channel | 40% bandwidth at X-band |

**Key finding:** LTCC-based AiP at X-band is technically mature but requires fundamental PCB redesign. The ADAR1000 + ADTR1107 combination is already a relatively integrated solution at the board level. True AiP miniaturization would integrate the beamformer, T/R module, and antenna element into a single package -- this is a significant NRE investment. The research document should position this as a "next-generation" option with cost/benefit analysis, not a near-term upgrade.

**Compatibility concern:** The ADAR1000's SPI control interface and phase/gain setting architecture would need to be preserved in any AiP solution, or the firmware and FPGA level-shifter interface would require redesign.

**Confidence:** MEDIUM (LTCC AiP dimensions and performance from peer-reviewed papers; specific ADAR1000+ADTR1107 AiP integration has not been reported in literature)

### HWRES-04: Higher-Resolution ADC Options

**Current component:** AD9484 (Analog Devices)
- Resolution: 8-bit (NOT 14-bit -- see pitfall)
- Sample rate: 400 MSPS (operated), 500 MSPS rated
- ENOB: ~7.5 bits typical
- SQNR: 49.9 dB theoretical
- Interface: 8-bit parallel LVDS DDR
- FPGA interface: `ad9484_interface_400m.v` with IBUFDS + IDDR primitives

**Candidate ADCs:**

| Parameter | AD9484 (current) | AD9680 (14-bit) | AD9208 (14-bit) |
|-----------|-------------------|-----------------|-----------------|
| Resolution | 8 bits | 14 bits | 14 bits |
| Sample rate | 500 MSPS | 500 MSPS / 1 GSPS | 3 GSPS |
| SNR | ~48 dBFS | 65.3 dBFS | ~65 dBFS |
| ENOB | 7.5 bits | 10.8 bits | ~10.5 bits |
| Interface | LVDS parallel | JESD204B | JESD204B |
| Noise density | N/A | -154 dBFS/Hz | Similar |
| Channels | Single | Dual | Dual |

**Critical interface change:** The AD9680 and AD9208 use JESD204B serial interfaces, NOT parallel LVDS. The Artix-7 XC7A100T has no GTH/GTY transceivers and cannot natively support JESD204B. This makes HWRES-04 dependent on HWRES-06 (FPGA upgrade). Artix UltraScale+ devices include GTH transceivers that support JESD204B.

**SNR improvement:**
- 8-bit to 14-bit: +36.1 dB SQNR (from 49.9 to 86.0 dB)
- 8-bit to 16-bit: +48.2 dB SQNR (from 49.9 to 98.1 dB)

This is the single largest potential improvement in the entire AERIS-10 system. The 8-bit ADC quantization floor is documented as a "dominant constraint" in `02_rf_frontend.md` Section 4.4 and `05_noise_analysis.md` Section 5.2. However, this improvement is only realized if the analog chain gain is sufficient to keep thermal noise above the new (much lower) quantization floor -- see Eq. NF-12.

**Confidence:** HIGH (AD9484 baseline confirmed from FPGA source code; AD9680 specs from official datasheet; JESD204B interface requirement verified)

### HWRES-05: Antenna Array Expansion

**Current array:**
- 16 elements, uniform linear array (ULA)
- Spacing: d = lambda/2 = 14.3 mm at 10.5 GHz
- ADAR1000: 4 devices (2-bit DEV_ADDR, 4 channels each)
- SPI bus: SPI1 on STM32, single bus with 4 chip selects
- Beamwidth: ~6.3 degrees at broadside
- Scan range: +/- 62.7 degrees (mechanically limited to +/-33 degrees for acceptable sidelobes)

**Scaling analysis:**

| Parameter | 16 elements | 32 elements | 64 elements |
|-----------|-------------|-------------|-------------|
| ADAR1000 count | 4 | 8 | 16 |
| SPI buses required | 1 | 2 | 4 |
| Array gain | 12.0 dB | 15.1 dB | 18.1 dB |
| Beamwidth (broadside) | 6.3 deg | 3.2 deg | 1.6 deg |
| Aperture length | 214 mm | 443 mm | 900 mm |
| Range multiplier | 1.0x | 1.41x | 2.0x |

**SPI scaling constraint:** The ADAR1000 DEV_ADDR is 2 bits (addresses 0x00-0x03), supporting max 4 devices per SPI bus. Expanding to 32 elements requires 8 ADAR1000 devices on 2 SPI buses. Expanding to 64 elements requires 16 devices on 4 SPI buses. The STM32F746 has 6 SPI peripherals total (SPI1-SPI6), of which SPI1 (ADAR1000) and SPI4 (AD9523, ADF4382) are currently used. SPI2, SPI3, SPI5, SPI6 are available for expansion.

**Grating lobe analysis:** With d = lambda/2 maintained, grating lobes remain outside visible space for all scan angles (Eq. BF-10). The critical constraint is physical: a 64-element array at lambda/2 spacing spans 900 mm (~35 inches), which may exceed mechanical platform constraints.

**Beam steering time impact:** With 31 elevation positions and M=32 chirps per position, the current scan cycle time is already substantial. Doubling elements does not change scan time (all elements are steered simultaneously via ADAR1000), but the SPI programming time per beam position increases linearly with ADAR1000 count.

**Confidence:** HIGH (all scaling analysis derived from documented system parameters and ADAR1000 datasheet; SPI constraint verified from firmware)

### HWRES-06: FPGA Upgrade Path

**Current FPGA:** Xilinx Artix-7 XC7A100T

**Resource comparison:**

| Resource | XC7A100T | AU10P | AU15P | AU25P |
|----------|----------|-------|-------|-------|
| System Logic Cells | 101,440 | 96,250 | 170,100 | 308,437 |
| CLB LUTs | 63,400 | 44,000 | 77,760 | 141,000 |
| CLB Flip-Flops | 126,800 | 88,000 | 155,520 | 282,000 |
| Block RAM (36Kb) | 135 | 100 | 144 | 300 |
| DSP Slices | 240 (DSP48E1) | 400 (DSP48E2) | 576 (DSP48E2) | 1,200 (DSP48E2) |
| Transceivers | 0 | 12 GTH | 12 GTH | 12 GTY |
| CMTs | 6 | 3 | 3 | 4 |
| Process node | 28 nm | 16 nm | 16 nm | 16 nm |

**Key observations:**

1. **AU10P is NOT a drop-in upgrade:** Despite being the "entry" Artix UltraScale+, the AU10P has fewer LUTs (44K vs 63K) than the XC7A100T. It does have more DSP slices (400 vs 240) and GTH transceivers (12 vs 0), but the LUT reduction could be problematic for the current design.

2. **AU15P is the natural migration target:** With 77,760 LUTs (22% more than XC7A100T), 576 DSP slices (2.4x), 144 BRAMs (slightly more), and 12 GTH transceivers enabling JESD204B, the AU15P is the minimum viable upgrade for supporting a 14-bit ADC.

3. **AU25P is the "future-proof" option:** With 141K LUTs (2.2x), 1,200 DSPs (5x), 300 BRAMs (2.2x), and GTY transceivers, the AU25P provides substantial headroom for both HWRES-04 (ADC upgrade) and Phase 5 software improvements (larger FFTs, more complex matched filters, ML inference).

4. **DSP48E2 vs DSP48E1:** UltraScale+ DSP slices are 27x18 multipliers (vs 25x18 for Artix-7), providing wider multiply operations useful for higher-precision signal processing.

5. **GTH transceivers enable JESD204B:** This is the key enabler for HWRES-04 (ADC upgrade). Without transceivers, no high-speed serial ADC interface is possible.

**PCB migration complexity:** HIGH. Different packages, different I/O banks, different pin assignments, different voltage rails (UltraScale+ uses 0.85V core vs 1.0V for Artix-7), different configuration modes. The entire PCB layout, constraint file, and power management subsystem must be redesigned.

**FT601 USB 3.0 compatibility:** The FT601's 32-bit FIFO interface at 100 MHz (LVCMOS33) is compatible with Artix UltraScale+ HP I/O banks. Opal Kelly's XEM8305 board demonstrates FT601 + AU15P integration, confirming compatibility.

**Confidence:** HIGH (XC7A100T baseline from project documentation; AU-series specs from AMD product pages and selection guides; FT601 compatibility confirmed from development board)

## Open Questions

1. **ADTR1107 full phase noise profile**
   - What we know: NF = 2.5 dB, LNA gain = 18 dB, PA Psat = 25 dBm
   - What's unclear: PA P1dB, LNA IP3, switching time, and full S-parameter data at 10.5 GHz specifically
   - Recommendation: Reference datasheet PDF in repository (`7_Components Datasheets and Application notes/adtr1107.pdf`) for frequency-specific performance

2. **ADF4382A phase noise at exact operating frequency**
   - What we know: FOM = -239 dBc/Hz; output is 10.5 GHz via VCO division
   - What's unclear: Exact phase noise at 100 kHz and 1 MHz offsets at 10.5 GHz (requires reading datasheet graphs)
   - Recommendation: Extract values from datasheet phase noise plots for quantitative Doppler floor calculation

3. **Vivado resource utilization actuals**
   - What we know: Theoretical estimates (~16,500 LUTs, ~88 DSPs, ~101 BRAMs used)
   - What's unclear: Actual post-implementation utilization (Vivado reports not in repository)
   - Recommendation: Flag as TBD; FPGA upgrade analysis should use theoretical estimates with margin

4. **IF amplifier presence and specifications**
   - What we know: Noise chain includes an IF amp stage (Stage 3 in Eq. NF-8)
   - What's unclear: Whether an IF amplifier actually exists in the signal chain, or if the mixer drives the ADC directly
   - Recommendation: Research document should note this ambiguity and analyze both cases

5. **Cost comparison for GaN vs SiGe at volume**
   - What we know: GaN is more expensive per device; SiGe excels at volume pricing
   - What's unclear: Actual per-element cost differential at relevant quantities (16-64 units)
   - Recommendation: Note cost as a qualitative factor; do not attempt specific pricing

## Sources

### Primary (HIGH confidence)
- [ADTR1107 Product Page -- Analog Devices](https://www.analog.com/en/products/adtr1107.html) -- NF 2.5 dB, LNA gain 18 dB, PA Psat 25 dBm confirmed
- [ADF4382A Product Page -- Analog Devices](https://www.analog.com/en/products/adf4382a.html) -- FOM -239 dBc/Hz, 11.5-21 GHz VCO range
- [AD9680 Product Page -- Analog Devices](https://www.analog.com/en/products/ad9680.html) -- 14-bit, 500 MSPS, SNR 65.3 dBFS, JESD204B interface
- [AD9208 Product Page -- Analog Devices](https://www.analog.com/en/products/ad9208.html) -- 14-bit, 3 GSPS, JESD204B
- [ADAR1000 Datasheet -- Analog Devices](https://www.analog.com/media/en/technical-documentation/data-sheets/adar1000.pdf) -- 4-channel, 2-bit DEV_ADDR, 7-bit phase resolution
- [Artix UltraScale+ Product Page -- AMD](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/artix-ultrascale-plus.html) -- AU7P/AU10P/AU15P/AU25P resource tables
- [XEM8305 (Opal Kelly) -- AU15P + USB 3.0 dev board](https://www.opalkelly.com/products/fpga-integration/xem8305) -- FT601 + AU15P compatibility confirmed
- AERIS-10 Phase 2/3 documentation -- noise analysis, hardware docs (project internal, HIGH confidence)

### Secondary (MEDIUM confidence)
- [Altum RF Front-End Components for X/Ku Band -- Nov 2025](https://www.altumrf.com/app/uploads/2025/12/Altum-RF-Front-end-Components-for-X-Ku-Band-Phased-Array-radar-Nov-2025.pdf) -- GaN/SiGe comparison landscape
- [LTCC X-Band T/R Module with Phased Array -- Cadence App Note](https://www.cadence.com/en_US/home/resources/application-notes/ltcc-transmit-receive-x-band-module-with-a-phased-array-antenna-an.html) -- AiP dimensions and performance
- [X-band T/R module in GaN technology -- ResearchGate](https://www.researchgate.net/publication/224186342_X-Band_transmitreceive_module_MMIC_chip-set_based_on_emerging_GaN_and_SiGe_technologies) -- GaN vs SiGe comparison
- [LMX2820 Product Page -- Texas Instruments](https://www.ti.com/product/LMX2820) -- FOM -236 dBc/Hz competing synthesizer
- [Design of X-Band TR Module Based on LTCC -- MDPI 2023](https://www.mdpi.com/2673-4591/118/1/29) -- LTCC miniaturization reference
- [Qorvo X-Band Radar Beamforming](https://www.qorvo.com/design-hub/blog/x-band-radar-driving-defense-applications-with-beamforming-gan-and-gaas-technology) -- Industry perspective on GaN for X-band
- [Integrated X-band phased array antenna with LTCC 3D T/R module -- IEICE](https://www.jstage.jst.go.jp/article/elex/17/4/17_17.20190714/_article) -- 3D LTCC integration reference

### Tertiary (LOW confidence -- needs validation)
- GaN LNA noise figure range (1.5-3.0 dB) -- aggregated from multiple web sources, not from single authoritative datasheet
- Cost comparisons between GaN and SiGe -- qualitative industry consensus, no specific pricing data

## Metadata

**Confidence breakdown:**
- HWRES-01 (GaN vs SiGe): MEDIUM-HIGH -- ADTR1107 specs confirmed; GaN specs are typical ranges, not device-specific
- HWRES-02 (Synthesizer): MEDIUM -- ADF4382A FOM confirmed; phase noise at specific offsets requires datasheet extraction
- HWRES-03 (AiP): MEDIUM -- LTCC technology proven at X-band; ADAR1000+ADTR1107 specific integration not demonstrated
- HWRES-04 (ADC): HIGH -- All specs from official Analog Devices product pages; interface change well-documented
- HWRES-05 (Array expansion): HIGH -- Derived from documented system parameters and ADAR1000 datasheet
- HWRES-06 (FPGA upgrade): HIGH -- Resource tables from AMD product pages; FT601 compatibility from dev board product

**Research date:** 2026-03-14
**Valid until:** 2026-06-14 (component specs are stable; AiP/integration research may evolve faster)
