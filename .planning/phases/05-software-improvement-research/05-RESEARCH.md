# Phase 5: Software Improvement Research - Research

**Researched:** 2026-03-14
**Domain:** Radar signal processing algorithms, CFAR detection, clutter rejection, FPGA optimization, ML-based detection, pulse compression, target tracking, adaptive beamforming
**Confidence:** MEDIUM-HIGH

## Summary

Phase 5 produces eight research documents (SWRES-01 through SWRES-08) surveying software improvements for the AERIS-10 FMCW phased array radar. Every research document is a Markdown file with the mandated structure: Current State / Literature Survey / Gap Analysis / Feasibility Assessment / Recommendations. The critical constraint is that every algorithm recommendation must include an Artix-7 XC7A100T resource estimate (63,400 LUTs, 240 DSP48E1s, 135 BRAMs, 126,800 FFs) and a feasibility verdict. The current system has approximately 26% LUT utilization, 37% DSP utilization, and 75% BRAM utilization based on Phase 3 theoretical estimates -- meaning LUT and DSP headroom exists but BRAM is tight.

The most important "current state" fact is that the system does NOT implement CFAR. Phase 4 documented that the threshold detector is a fixed magnitude comparator (|I|+|Q| > 10000), not an adaptive algorithm. All eight research documents must reference the completed Phase 1-4 documentation as their baseline, citing specific equations (DET-1 through DET-24 for detection theory, NF-1 through NF-18 for noise analysis, SW-1 through SW-7 for pipeline stages).

This phase is documentation and research ONLY -- no implementation. Each document ends with a feasibility assessment and recommended investigation steps, not implementation specifications. The output directory is `04_research/` (following the established numbering: `00_notation/`, `01_physics/`, `02_hardware/`, `03_software/`, `04_research/`).

**Primary recommendation:** Structure the eight SWRES documents as independent research surveys that share a common "Current State" baseline section referencing the Phase 1-4 documentation chain. Prioritize SWRES-01 (CFAR variants) and SWRES-04 (FPGA optimization) as the highest-impact deliverables, since the current system lacks true CFAR and FPGA resource margins constrain all other improvements.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SWRES-01 | CFAR variants survey (CA, OS, GOCA, SOCA) with Artix-7 resource estimates | Detection theory baseline (DET-1 through DET-24), current placeholder detector (SW-7), FPGA resource capacity (Section 2.2 of FPGA board doc), published CFAR FPGA implementations |
| SWRES-02 | Clutter rejection (MTI, background subtraction, Doppler notch) | Doppler processor documentation (SW-6), 32-chirp CPI, MTI/Doppler notch filter literature, FMCW-specific clutter models |
| SWRES-03 | Range extension via SNR optimization (coherent integration, longer CPI) | Noise figure chain (NF-1 through NF-18), radar range equation, current 32-chirp CPI and 1024-pt FFT, coherent/non-coherent integration theory |
| SWRES-04 | FPGA pipeline throughput optimization (HLS, pipelining, multi-bank memory) | FPGA module inventory (25+ modules), resource utilization estimates, clock domain architecture, pipeline data flow documentation |
| SWRES-05 | ML-based detection alternatives to CFAR (autoencoder, CNN, FPGA feasibility) | Current detection baseline, Artix-7 resource constraints (especially 240 DSP48E1s and 135 BRAMs), published FPGA CNN implementations |
| SWRES-06 | Pulse compression improvements (NLFM, sidelobe reduction) | LFM waveform model (LFM equations), matched filter documentation (SW-4), chirp memory architecture, DAC interface |
| SWRES-07 | Target tracking improvements (IMM-Kalman, adaptive Kalman) | Current Kalman filter in GUI_V6.py, RadarTarget dataclass, Python-side processing (no FPGA constraint) |
| SWRES-08 | Adaptive beamforming (MVDR/LCMV, real-time FPGA weight computation) | Beamforming theory (BF equations), ADAR1000 phase shifter architecture, 16-element array, current fixed beam steering |
</phase_requirements>

## Standard Stack

### Core -- Document Authoring
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| GitHub Markdown + MathJax | Current | Primary document format | Native GitHub rendering, equation support via `$$` blocks with `\tag{}` |
| Zotero | v7 | IEEE citation management | Free, BibTeX export, standard for academic literature surveys |
| Python + matplotlib | 3.x | Reproducible figures (detection curves, resource comparison charts) | Already used in project for documentation figures |

### Reference Libraries (for research content, not implementation)
| Library | Purpose | When to Reference |
|---------|---------|-------------------|
| Skolnik, *Introduction to Radar Systems* 4th ed. | CFAR theory, detection performance, MTI | SWRES-01, SWRES-02, SWRES-03 |
| Richards, *Fundamentals of Radar Signal Processing* 2nd ed. | CFAR derivations, pulse compression, Doppler processing | SWRES-01, SWRES-06 |
| Mahafza, *Radar Systems Analysis and Design Using MATLAB* 3rd ed. | CFAR implementation, detection curves | SWRES-01, SWRES-03 |
| Xilinx UG479 (7 Series DSP48E1) | DSP slice architecture for resource estimates | SWRES-01, SWRES-04, SWRES-05, SWRES-08 |
| Xilinx DS181 (Artix-7 Data Sheet) | FPGA resource limits | All SWRES documents |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Zotero | BibTeX manual management | Zotero provides GUI + auto-import; manual BibTeX works but slower for 8 research docs |
| matplotlib figures | draw.io diagrams | matplotlib better for quantitative comparison charts; draw.io better for architecture diagrams |

## Architecture Patterns

### Recommended Document Structure
```
04_research/
    01_cfar_variants.md           # SWRES-01
    02_clutter_rejection.md       # SWRES-02
    03_range_extension.md         # SWRES-03
    04_fpga_optimization.md       # SWRES-04
    05_ml_detection.md            # SWRES-05
    06_pulse_compression.md       # SWRES-06
    07_target_tracking.md         # SWRES-07
    08_adaptive_beamforming.md    # SWRES-08
    figures/                      # Shared figures directory
```

### Pattern 1: Research Document Structure (Mandatory for All SWRES)
**What:** Every research document follows a five-section structure with standardized content.
**When to use:** All eight SWRES documents.
**Template:**

```markdown
# [Topic Title]

**Purpose:** [One sentence]
**Prerequisites:** [Links to Phase 1-4 documents this builds on]

## 1. Current State
[Reference specific equations, sections, and findings from Phase 1-4 docs]
[For SWRES-01: "The current system uses a fixed magnitude threshold |I|+|Q| > 10000
(Eq. SW-7), NOT a true CFAR algorithm. See Section 10 of 03_software/01_fpga_pipeline.md."]

## 2. Literature Survey
[Structured review of approaches with citations]
[Each approach: description, performance metrics, computational complexity]

## 3. Gap Analysis
[What the current system lacks vs. state of the art]
[Prioritized list of gaps]

## 4. Feasibility Assessment
[For EACH recommended improvement:]
### 4.N [Improvement Name]
| Property | Value |
|----------|-------|
| Algorithm complexity | O(N) / O(N log N) / O(N^2) |
| Estimated LUTs | X / 63,400 available |
| Estimated DSPs | X / 240 available |
| Estimated BRAMs | X / 135 available |
| Pipeline integration | [Where it fits in current pipeline] |
| Verdict | FEASIBLE / MARGINAL / INFEASIBLE on Artix-7 |

## 5. Recommendations
[Ranked list of recommended improvements]
[Each with: priority, expected performance gain, resource cost, risk]
[NO implementation specifications -- feasibility assessment and investigation steps only]

## References
[IEEE format citations]
```

### Pattern 2: Cross-Reference to Baseline Documentation
**What:** Every "Current State" section must cite specific Phase 1-4 documents and equations.
**When to use:** Opening section of every SWRES document.
**Example citations:**
- Detection theory: "See Eq. (DET-20) in `01_physics/04_detection_theory.md` for the CA-CFAR threshold multiplier derivation"
- Pipeline: "See Table 1.1 in `03_software/01_fpga_pipeline.md` for the 10-stage pipeline architecture"
- FPGA resources: "See Table 2.1 in `02_hardware/05_fpga_board.md` for XC7A100T resource capacity"

### Pattern 3: Artix-7 Feasibility Table (Mandatory)
**What:** Every algorithm recommendation includes a resource estimate table.
**When to use:** Section 4 of every SWRES document, for every algorithm discussed.
**Key constraint:** Current estimated utilization is ~26% LUT, ~37% DSP, ~75% BRAM. New algorithms must fit within remaining headroom (~46,900 LUTs, ~152 DSPs, ~34 BRAMs available).

### Anti-Patterns to Avoid
- **Academic benchmark without FPGA translation:** Never cite GPU or Zynq UltraScale+ benchmarks as evidence of Artix-7 feasibility. Always translate to XC7A100T resource estimates.
- **Implementation specifications:** End with "recommended investigation steps," never with design specs or Verilog code. PROJECT.md explicitly excludes implementation.
- **Ignoring current baseline:** Every recommendation must state improvement over the CURRENT system (e.g., "vs. the fixed threshold detector"), not over a theoretical ideal.
- **BRAM-heavy proposals without accounting for current usage:** Current BRAM utilization is ~75%. Any proposal requiring >34 additional BRAMs is infeasible without redesigning existing modules.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CFAR resource estimates | Custom gate-level analysis | Published FPGA implementation papers + scaling from known implementations | Multiple peer-reviewed CFAR FPGA papers provide verified resource numbers |
| Detection probability curves | Manual Marcum Q-function tables | matplotlib with scipy.special or numerical quadrature (already in project) | Numerical computation is faster and more accurate than hand-tabulation |
| FPGA resource scaling | Guessing from algorithm description | Xilinx IP core datasheets + published synthesis reports | Actual synthesis reports are the only reliable source for resource estimates |
| Literature survey structure | Ad-hoc format per document | IEEE/IET research survey conventions | Consistent structure across 8 documents improves readability and cross-referencing |

**Key insight:** This phase is research documentation, not implementation. The "don't hand-roll" principle applies to research methodology: use published implementation data rather than speculative resource estimates.

## Common Pitfalls

### Pitfall 1: Proposing BRAM-Heavy Algorithms Without Checking Headroom
**What goes wrong:** Algorithms like large FFTs, deep FIR filters, or ML weight storage consume BRAM. The current system is at ~75% BRAM utilization (101/135 blocks estimated). Proposals that need >34 additional BRAMs are infeasible.
**Why it happens:** Researchers focus on algorithm performance without checking the specific FPGA resource that is most constrained.
**How to avoid:** Every feasibility table must include BRAM estimate. Flag any proposal requiring >20 BRAMs as "BRAM-constrained" with a mitigation note.
**Warning signs:** Proposals involving lookup tables, coefficient storage, or data buffers larger than a few KB.

### Pitfall 2: GPU/Cloud Benchmarks Presented as FPGA-Feasible
**What goes wrong:** ML detection papers report accuracy on GPU/cloud platforms. These results do not transfer to Artix-7 with 240 DSP48E1s and no floating-point hardware.
**Why it happens:** Academic literature benchmarks on powerful platforms; translating to resource-constrained FPGAs requires separate analysis.
**How to avoid:** For every ML/CNN proposal, include: (a) model size in parameters, (b) INT8 quantization impact on accuracy, (c) DSP/LUT estimate for inference engine, (d) whether it fits in XC7A100T.
**Warning signs:** Papers citing TensorFlow/PyTorch accuracy without FPGA synthesis results.

### Pitfall 3: Ignoring the Placeholder Detection Baseline
**What goes wrong:** Research compares proposed improvements against "ideal CFAR" instead of the actual system (|I|+|Q| > 10000 threshold).
**Why it happens:** The Verilog uses CFAR variable names, creating a false impression that CFAR is implemented.
**How to avoid:** Every "Current State" section must explicitly state that the current detector is a fixed threshold, citing Eq. (SW-7) and Section 10 of `03_software/01_fpga_pipeline.md`.
**Warning signs:** Phrases like "improving the current CFAR" -- there is no current CFAR.

### Pitfall 4: Scope Creep Into Implementation
**What goes wrong:** Research documents begin including Verilog code, timing diagrams, or register maps for proposed improvements.
**Why it happens:** Natural tendency when researchers understand the implementation well enough to write specs.
**How to avoid:** End each document with "Recommended Investigation Steps" (bullet points), not "Implementation Plan." PROJECT.md explicitly excludes implementation.
**Warning signs:** Documents exceeding research scope with RTL-level details.

### Pitfall 5: CFAR Variants Without Clutter Distribution Assumptions
**What goes wrong:** CFAR variant recommendations without specifying which clutter distribution they assume (Rayleigh, K-distribution, Weibull, log-normal).
**Why it happens:** Academic papers often assume a specific clutter model without stating it prominently.
**How to avoid:** For each CFAR variant, explicitly state: assumed noise distribution, breakdown conditions, and how it relates to the AERIS-10 operating environment.
**Warning signs:** CFAR recommendations that only cite false alarm rate without specifying the clutter model.

### Pitfall 6: Coherent Integration Proposals Ignoring Range Migration
**What goes wrong:** Longer CPI proposals assume targets remain in the same range bin throughout integration, which fails for fast-moving targets.
**Why it happens:** Range migration becomes significant when target velocity causes range change exceeding one range bin during the CPI.
**How to avoid:** Calculate maximum unambiguous velocity for proposed CPI durations and flag range migration compensation requirements.
**Warning signs:** CPI extension proposals without a range migration analysis.

## Code Examples

This phase produces documentation (Markdown research surveys), not code. The following are content patterns rather than code examples.

### Example: Feasibility Assessment Table (for every algorithm)
```markdown
### 4.1 CA-CFAR with 32 Reference Cells, 4 Guard Cells

| Property | Value |
|----------|-------|
| Algorithm complexity | O(N_ref) per cell under test |
| Estimated LUTs | ~2,000--4,000 (sliding window + comparator) |
| Estimated DSPs | 2--4 (magnitude computation, threshold multiply) |
| Estimated BRAMs | 2--4 (reference cell buffer for 2D window) |
| Clock cycles per detection | ~N_ref + N_guard + 1 = 37 |
| Pipeline integration | Replaces inline threshold in `radar_system_top.v` (Stage 9) |
| Published reference | PMC 9861839: 8,260 LUTs for 16-cell CA-CFAR on Stratix II |
| Verdict | **FEASIBLE** -- well within Artix-7 headroom |
```

### Example: Current State Section Opening
```markdown
## 1. Current State

The AERIS-10 radar currently uses a **fixed magnitude threshold** for target
detection, NOT a true CFAR algorithm. The detection logic in
`radar_system_top.v` computes the L1 norm of the Doppler output and compares
against a hardcoded constant (see Eq. (SW-7) in
[`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md#10-stage-8-threshold-detection)):

$$|I| + |Q| > 10{,}000$$

This results in an **uncontrolled false alarm rate** that varies with noise
level. The detection theory foundation for proper CFAR implementation is
derived in [`01_physics/04_detection_theory.md`](../01_physics/04_detection_theory.md),
Eqs. (DET-17) through (DET-24).
```

### Example: Recommendation Format
```markdown
## 5. Recommendations

### Priority 1: CA-CFAR (Immediate Feasibility)
- **Expected improvement:** Controlled P_fa (e.g., 10^-6) regardless of noise level
- **Resource cost:** ~3,000 LUTs, 2 DSPs, 3 BRAMs (< 5% of available)
- **Risk:** LOW -- well-understood algorithm, multiple published FPGA implementations
- **Investigation steps:**
  1. Determine reference cell count based on range-Doppler map dimensions (64 range bins x 32 Doppler bins)
  2. Evaluate 1D vs. 2D CFAR based on clutter environment characterization
  3. Simulate CA-CFAR performance against measured noise data from current system
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fixed threshold detection | Adaptive CFAR (CA, OS, GOCA variants) | Mature since 1990s, FPGA implementations since ~2010 | AERIS-10 still uses fixed threshold -- this is the primary gap |
| LFM chirp only | NLFM waveform optimization (genetic algorithm, spline methods) | Active research 2020-2025 | -40 to -50 dB sidelobes achievable without SNR loss |
| Fixed-parameter Kalman | IMM-Kalman with variational Bayesian adaptation | Active research 2024-2025 | Significant RMSE improvement for maneuvering targets |
| Fixed beam steering tables | MVDR/LCMV adaptive beamforming | Mature algorithm, FPGA implementations emerging 2020-2025 | Requires matrix inversion -- resource-intensive on Artix-7 |
| Hand-coded Verilog only | Vitis HLS (formerly Vivado HLS) for algorithm acceleration | Mature since ~2018, continuous improvement | Up to 4x faster IP creation but 15-30% resource overhead vs. hand-coded |
| Separate CA/OS/GO detection | Parallel multi-mode CFAR (CA + OS + GO simultaneously) | Published FPGA implementations 2023 | Better detection across mixed environments |
| CPU-based CNN inference | FPGA-based quantized CNN (INT8) | Active research 2023-2025 | Feasible on larger FPGAs (Kintex/Zynq); marginal on Artix-7 due to DSP/BRAM limits |

**Deprecated/outdated:**
- Vivado HLS: Now called Vitis HLS (rebranded in 2020). Research documents should reference "Vitis HLS" for current tool name.
- Single-pulse detection analysis only: Modern radar systems analyze detection across multiple pulses; single-pulse Pd curves (DET-21, DET-22) are baseline only.

## Open Questions

1. **Actual FPGA resource utilization (Vivado reports)**
   - What we know: Theoretical estimates from Phase 3 (~26% LUT, ~37% DSP, ~75% BRAM)
   - What's unclear: Actual post-implementation utilization may differ significantly
   - Recommendation: Flag all feasibility assessments as "based on theoretical estimates pending Vivado reports." Use conservative margins (assume 30% overhead on theoretical estimates).

2. **Clutter environment characterization**
   - What we know: The system operates at X-band (10.5 GHz) with ground clutter, but no measured clutter statistics are available
   - What's unclear: Whether ground clutter follows Rayleigh, K-distribution, or Weibull -- this determines optimal CFAR variant
   - Recommendation: Present CFAR variant analysis parametrically across clutter models. Recommend clutter measurement campaign as first investigation step.

3. **ADC dynamic range impact on ML detection**
   - What we know: AD9484 is 8-bit (49.9 dB SQNR), which limits the dynamic range of range-Doppler maps
   - What's unclear: Whether 8-bit quantized range-Doppler maps provide sufficient resolution for CNN/autoencoder-based detection
   - Recommendation: Flag this as a key feasibility question for SWRES-05. ML approaches may be more sensitive to ADC bit depth than traditional CFAR.

4. **NLFM waveform DAC feasibility**
   - What we know: Current chirp waveforms are stored in `.mem` files and output via the 120 MHz DAC interface
   - What's unclear: Whether NLFM waveform coefficients can be generated with sufficient precision using the current 8-bit DAC at 120 MHz
   - Recommendation: Calculate NLFM coefficient precision requirements in SWRES-06 and compare against DAC specifications.

5. **ADAR1000 update rate for adaptive beamforming**
   - What we know: ADAR1000 phase settings are written via SPI; firmware bypasses beam RAM
   - What's unclear: Maximum SPI update rate for real-time weight adaptation (MVDR/LCMV require per-CPI weight updates)
   - Recommendation: Quantify SPI transaction time for full 16-element weight update in SWRES-08 feasibility section.

## SWRES-Specific Research Findings

### SWRES-01: CFAR Variants

**CA-CFAR on FPGA:** Published implementations show 2,000-8,260 LUTs for 16-reference-cell CA-CFAR (varies by implementation complexity and target FPGA). A CM-CM CFAR processor required 23,741 LUTs on an Artix-7 XC7A100T -- this is a more complex multi-mode variant. Simple CA-CFAR is well within resource budget.

**OS-CFAR complexity:** OS-CFAR requires sorting the reference cells, which adds O(N_ref * log(N_ref)) complexity vs. O(N_ref) for CA-CFAR. FPGA implementations use sorting networks (bitonic sort) or insertion sort, adding ~2x-3x the LUT count of CA-CFAR for equivalent reference window sizes.

**GOCA/SOCA-CFAR:** Greatest-Of and Smallest-Of variants compute two half-window averages and select max/min. Resource overhead vs. CA-CFAR is minimal (~10-20% more LUTs for the comparison logic). GOCA prevents false alarms at clutter edges; SOCA reduces target masking.

**Confidence:** HIGH -- multiple published FPGA implementations with verified resource numbers.

### SWRES-02: Clutter Rejection

**MTI for FMCW:** Three primary approaches: (1) background subtraction (subtract mean across chirps), (2) FIR high-pass filter (1st or 2nd order), (3) IIR notch filter at zero Doppler. All are low-resource on FPGA. Background subtraction requires one BRAM per range bin for the running average.

**Doppler notch filter:** Digital notch filter with complex coefficients can reject clutter at any Doppler frequency, not just zero. Useful for platform motion compensation. Resource cost: ~200-500 LUTs for a 2nd-order IIR filter.

**Integration with current pipeline:** MTI/clutter rejection would be inserted between the matched filter output (Stage 6) and the Doppler processor (Stage 7), or equivalently between range bin decimation and Doppler FFT.

**Confidence:** HIGH -- MTI is mature, well-documented in Skolnik Ch. 15 and MathWorks reference implementations.

### SWRES-03: Range Extension via SNR

**Coherent integration gain:** SNR improves by factor M for M coherently integrated pulses. Current system: M=32 chirps per CPI. Doubling to M=64 gives 3 dB improvement, which extends range by factor 2^(3/40) = 1.19x (range scales as SNR^0.25).

**Non-coherent integration:** When coherent integration is limited by target motion, non-coherent integration of magnitude-squared values provides reduced but still useful gain of approximately sqrt(M).

**Range migration constraint:** For CPI duration T_CPI, range migration exceeds one range bin when target velocity > (range resolution) / T_CPI. Must be analyzed for any CPI extension proposal.

**Confidence:** HIGH -- coherent integration theory is well-established; quantitative analysis straightforward from existing system parameters.

### SWRES-04: FPGA Pipeline Optimization

**Vitis HLS vs. hand-coded Verilog:** HLS provides 4x faster development but typically 15-30% resource overhead. For a resource-constrained Artix-7, hand-coded Verilog remains preferred for performance-critical modules (FFT, matched filter). HLS may be appropriate for less critical modules (USB interface, control logic).

**Multi-bank memory:** Current Doppler processor uses single-port BRAM. Dual-port BRAM would allow simultaneous read/write, reducing processing time. Artix-7 BRAMs are natively dual-port.

**Loop unrolling for FFT:** The 1024-pt FFT uses radix-2 DIT architecture. Partial unrolling (radix-4 or split-radix) can reduce clock cycles by 2x but increases DSP usage by 2x. Current DSP headroom (~152 available) supports this.

**Confidence:** MEDIUM -- optimization tradeoffs depend on actual utilization numbers from Vivado reports.

### SWRES-05: ML-Based Detection

**Artix-7 CNN feasibility:** The XC7A100T can support small INT8-quantized CNNs with ~10K-50K parameters using available DSP/BRAM resources. Larger models (>100K parameters) are infeasible without external memory.

**Autoencoder approach:** A small autoencoder (encoder: 64->32->16, decoder: 16->32->64) operating on range-Doppler patches would require ~2,000-4,000 LUTs, 20-40 DSPs, and 5-10 BRAMs for INT8 inference. This is potentially feasible but would compete with existing FFT modules for DSP slices.

**Practical concern:** Training data requirements are significant -- the system would need labeled range-Doppler maps with known targets, which requires field data collection.

**Confidence:** LOW-MEDIUM -- feasibility estimates are extrapolated from published FPGA CNN implementations on similar-class devices; no direct Artix-7 radar detection implementation found.

### SWRES-06: Pulse Compression (NLFM)

**NLFM sidelobe reduction:** NLFM achieves -40 to -50 dB sidelobes without the SNR loss of windowed LFM. The 2025 Scientific Reports paper demonstrates optimization methods achieving high Doppler tolerance.

**DAC constraint:** Current 8-bit DAC at 120 MHz limits waveform fidelity. NLFM requires higher precision than LFM due to nonlinear phase modulation. Quantization effects on NLFM sidelobes must be analyzed.

**Memory impact:** NLFM reference chirp coefficients would replace the current LFM `.mem` files. Storage requirement is identical (same number of samples), but matched filter reference must also be updated.

**Confidence:** MEDIUM -- NLFM theory is solid; DAC precision impact on practical sidelobe performance needs analysis specific to the 8-bit/120 MHz constraint.

### SWRES-07: Target Tracking (IMM-Kalman)

**Current baseline:** GUI_V6.py uses a fixed-parameter Kalman filter in Python. IMM-Kalman runs on the host PC (Python), NOT on the FPGA -- no FPGA resource constraint applies.

**IMM architecture:** Typically 2-3 models (constant velocity, constant acceleration, coordinated turn) with model probability updates. Computational overhead is 2-3x a single Kalman filter -- trivial in Python.

**2025 advances:** Variational Bayesian IMM improves maneuver detection responsiveness and reduces RMSE by adapting change-point statistics in real-time. Published in MDPI Electronics 2025.

**Confidence:** HIGH -- Python implementation is straightforward; no FPGA constraints; well-established algorithm.

### SWRES-08: Adaptive Beamforming

**MVDR on FPGA:** Published implementations require XCKU060/XCKU085-class FPGAs (4000+ DSP slices) for real-time MVDR with matrix inversion. The Artix-7 XC7A100T with 240 DSPs is significantly resource-constrained for full MVDR.

**LCMV alternative:** Similar computational requirements to MVDR; both require covariance matrix inversion (O(N^3) for N=16 elements).

**Hybrid approach:** Pre-computed weight tables with periodic MVDR updates on the host PC, downloaded to ADAR1000 via SPI. This moves the computation off-FPGA but introduces latency.

**ADAR1000 constraint:** The ADAR1000 has 7-bit phase resolution (2.8 deg steps) and 0.5 dB gain resolution. Adaptive beamforming precision is limited by this quantization.

**Confidence:** MEDIUM -- MVDR/LCMV theory well-understood; FPGA feasibility on Artix-7 is LOW for real-time implementation, but hybrid approach (host-computed weights) is feasible.

## Sources

### Primary (HIGH confidence)
- `03_software/01_fpga_pipeline.md` -- Current pipeline architecture, threshold detector documentation (Eq. SW-7)
- `01_physics/04_detection_theory.md` -- CA-CFAR derivation (Eqs. DET-17 through DET-24), Swerling models
- `01_physics/05_noise_analysis.md` -- Noise figure chain (Eqs. NF-1 through NF-18), ADC quantization analysis
- `02_hardware/05_fpga_board.md` -- XC7A100T resource capacity, clock domains, module inventory
- [FPGA Implementation of Efficient CFAR Algorithm for Radar Systems -- PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9861839/) -- CA-CFAR FPGA resource data
- [Ground Clutter Mitigation with MTI -- MathWorks](https://www.mathworks.com/help/radar/ug/ground-clutter-mitigation-with-moving-target-indication-mti-radar.html) -- MTI techniques
- [FPGA-Based Uniform Linear Array MVDR Beamformer -- MathWorks](https://www.mathworks.com/help/phased/ug/fixed-point-hdl-optimized-mvdr-beamformer.html) -- MVDR FPGA reference implementation

### Secondary (MEDIUM confidence)
- [Improved CFAR algorithm for multiple environmental conditions -- Springer 2024](https://link.springer.com/article/10.1007/s11760-024-03001-x) -- Multi-mode CFAR on Artix-7 (23,741 LUTs)
- [NLFM Waveform Optimization -- Scientific Reports 2025](https://www.nature.com/articles/s41598-025-23766-6) -- NLFM sidelobe reduction methods
- [Model Adaptive Kalman Filter -- MDPI Electronics 2025](https://www.mdpi.com/2079-9292/14/10/1908) -- Variational Bayesian IMM
- [MVDR Algorithm and FPGA Integration -- ScienceDirect 2024](https://www.sciencedirect.com/science/article/pii/S1051200424003579) -- MVDR on XCKU085 FPGA
- [MVDR and LCMV Beamformers FPGA Comparison -- Springer](https://link.springer.com/article/10.1007/s11277-017-4953-1) -- MVDR/LCMV resource comparison
- [Real-Time FPGA-Based CNNs -- arXiv 2509.04153](https://arxiv.org/abs/2509.04153) -- CNN FPGA implementation survey
- [Efficient FPGA CNN+LSTM for Radar -- PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10857097/) -- Radar signal recognition on FPGA
- [Coherent Integration for High-Speed Targets -- MDPI Remote Sensing](https://www.mdpi.com/2072-4292/16/12/2139) -- Long-time integration methods
- [Autoencoder-Based Target Detection in MIMO FMCW -- PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9370841/) -- ML detection alternative to CFAR
- [Robust Peak Detection Techniques for FMCW Radar -- MDPI](https://www.mdpi.com/2624-6120/6/3/36) -- CFAR comparison and FPGA feasibility

### Tertiary (LOW confidence -- needs validation)
- Artix-7 CNN inference capability estimates -- extrapolated from general FPGA CNN literature, no direct radar detection implementation found on XC7A100T
- Vitis HLS 15-30% resource overhead estimate -- from general FPGA design literature, not radar-specific benchmarking

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- tooling is identical to Phases 1-4 (Markdown + MathJax + Zotero)
- Architecture: HIGH -- research document structure follows established project patterns
- CFAR/MTI research: HIGH -- mature algorithms with published FPGA implementations
- ML detection research: LOW-MEDIUM -- feasibility on Artix-7 specifically is uncertain
- FPGA optimization: MEDIUM -- depends on unavailable Vivado implementation reports
- Beamforming research: MEDIUM -- MVDR/LCMV well-understood but FPGA feasibility on Artix-7 is questionable

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (30 days -- stable domain, but FPGA tool capabilities evolve)
