# Feature Research

**Domain:** FMCW Phased Array Radar — Engineering Documentation & Improvement Research
**Researched:** 2026-03-13
**Confidence:** MEDIUM-HIGH (documentation structure: HIGH from IEEE/IET standards; improvement research: MEDIUM from current academic literature)

---

## Overview

This project has two parallel feature dimensions that must be treated separately:

1. **Documentation Features** — sections and depth required in the documentation package
2. **Improvement Research Features** — technical topics to survey for SW and HW improvement areas

Both dimensions have Table Stakes, Differentiators, and Anti-Features. The downstream consumer of FEATURES.md is requirements definition, so each item calls out complexity and dependencies clearly.

---

## Part 1: Documentation Package Features

### Table Stakes — Documentation (Engineers Expect These)

Missing any of these makes the documentation package feel incomplete to the engineering team.

| Documentation Section | Why Expected | Complexity | Notes |
|----------------------|--------------|------------|-------|
| FMCW Theory — radar equation, range/velocity derivations | Foundation for everything downstream; engineers need this to reason about detection limits | MEDIUM | Start from Maxwell's equations, derive beat frequency, range equation, velocity ambiguity, range-Doppler coupling |
| Waveform Model — LFM chirp math, time-bandwidth product, pulse compression gain | Engineers need this to tune chirp parameters (T1=30µs, T2=0.5µs) intelligently | MEDIUM | Derive matched filter SNR gain, ambiguity function, range/Doppler resolution formulas |
| Beamforming Theory — phased array steering, grating lobes, element spacing | 16-element array; engineers must understand beam pattern to debug or improve steering | MEDIUM | Derive array factor, phase shift per element for ADAR1000, grating lobe conditions for λ/2 spacing |
| Signal Processing Pipeline Documentation — DDC, CIC, matched filter, FFT, CFAR | The FPGA pipeline is the core of the system; must be documented module-by-module | HIGH | Document each Verilog module: `ddc_400m.v`, `cic_decimator_4x_enhanced.v`, `matched_filter_multi_segment.v`, `doppler_processor.v`, `fft_1024_forward.v` |
| RF Hardware Documentation — ADF4382, ADAR1000, ADTR1107, LT5552 mixer, AD9484 ADC | Engineers need component-level understanding for debugging and replacement decisions | HIGH | Include register maps, SPI configuration sequences, key performance specs (NF, IP3, phase noise) |
| FPGA Architecture Documentation — clock domains, CDC, resource utilization | Xilinx XC7A100T constraints; engineers need this to safely modify timing-critical HDL | HIGH | Document 100MHz/120MHz/400MHz domains, BUFG usage, CDC synchronizers, LUT/FF/BRAM utilization |
| STM32 Firmware Documentation — initialization sequence, peripheral configuration, power sequencing | Any firmware change without this causes hardware damage risk (power rail sequencing) | MEDIUM | Document GPIO states, SPI/I2C device addresses, power-on/off sequences, timing constraints |
| Python GUI Documentation — USB protocol, data structures, processing pipeline | GUI contains DBSCAN, Kalman tracking, map rendering — all undocumented tribal knowledge | MEDIUM | Document `RadarTarget` dataclass, USB packet format, DBSCAN parameters, Kalman state model |
| USB Interface Protocol — FT601 command/data format, packet structure | Interface between FPGA and Python host; critical for any host-side or FPGA-side changes | MEDIUM | Document `RadarSettings.parseFromUSB()`, command byte format, data streaming protocol |
| System Integration — how all layers connect | Engineers need end-to-end view for debugging failures that cross layer boundaries | MEDIUM | Document the full chain: GUI command → USB → FPGA → ADC → processing → USB → GUI |

### Differentiators — Documentation (Depth That Sets This Apart)

These are what make this documentation package genuinely valuable vs. a surface-level reference.

| Documentation Section | Value Proposition | Complexity | Notes |
|----------------------|-------------------|------------|-------|
| Full Physics Derivations from First Principles | Engineers can derive system parameters from scratch, not just apply formulas blindly | HIGH | Derive from EM wave propagation through to SNR at detector; include noise figure chain analysis |
| CFAR Algorithm Deep Dive — mathematical derivation with false alarm/detection probability | Current system uses CFAR; engineers need to understand threshold setting and its tradeoffs | HIGH | Derive Neyman-Pearson criterion, CA-CFAR false alarm probability, window size vs. resolution tradeoff |
| Range-Doppler Coupling Analysis | FMCW-specific problem: fast targets shift range bin; critical for understanding detection errors | MEDIUM | Derive coupling equation, show impact on 30µs vs 0.5µs chirps, document compensation approach |
| Noise Figure Chain Analysis | End-to-end SNR budget explains detection range limits; directly drives improvement research | MEDIUM | Compute cascaded NF through LNA (ADTR1107), mixer (LT5552), ADC (AD9484), CIC filter |
| Antenna Array Calibration Procedure — phase/amplitude error correction | 16-element array performance degrades without calibration; procedure not documented | HIGH | Document ADAR1000 phase setting precision, inter-element phase error sources, calibration measurement method |
| Timing Budget and Latency Analysis — chirp to detection latency | Enables reasoning about max PRF, real-time processing headroom, and upgrade feasibility | MEDIUM | Document pipeline latency: ADC → DDC → CIC → matched filter → FFT → CFAR → USB |
| Coordinate System and GPS/IMU Integration Math | GPS-corrected target positions require quaternion transforms; math not documented anywhere | MEDIUM | Document the IMU quaternion → Euler → target coordinate transform in `GUI_V6.py` |
| Power Budget Analysis | Power consumption per subsystem enables platform integration decisions and thermal management | LOW | Compile per-rail current draw, total power, thermal dissipation for each subsystem |

### Anti-Features — Documentation (Deliberately Excluded)

| Anti-Feature | Why Requested | Why Problematic | Alternative |
|--------------|---------------|-----------------|-------------|
| Operator / User Manuals | Seems like natural documentation output | Audience is engineering team, not operators; different writing style, different content, different purpose — wastes scope | Explicitly stated out of scope in PROJECT.md; document engineering interfaces only |
| Regulatory / EMC / Safety Compliance Docs | Seems like completeness | Requires legal/regulatory expertise and certification knowledge outside engineering scope; creates liability if inaccurate | Reference applicable standards by number only in architecture doc; do not attempt compliance analysis |
| Marketing or Sales Materials | "Nice to have" for external presentations | Not engineering documentation; dilutes the technical depth of the package | Out of scope per PROJECT.md |
| Tutorial-Style Walkthroughs for Beginners | Makes docs "accessible" | Engineering audience already has deep RF/DSP background; simplification wastes space and condescends to the audience | Write at peer level; include references to standard texts (Skolnik, Richards) for foundational topics |
| GUI User Guide / Workflow Documentation | GUI exists and needs docs | Operator workflows are out of scope; document the engineering interfaces (USB protocol, data structures, processing parameters) not the click-by-click workflow | Document `GUI_V6.py` architecture and data processing, not button-press sequences |
| Implementation Guides for Improvements | Research output naturally leads to "how to implement X" | PROJECT.md explicitly excludes implementation — research only; attempting implementation guidance without actually doing the work produces unreliable guidance | End each improvement research section with "recommended next steps" framing, not implementation instructions |

---

## Part 2: Improvement Research Features

Subdivided into **Software (SW)** and **Hardware (HW)** improvement categories per PROJECT.md.

### SW Improvement Research — Table Stakes

Topics the engineering team will certainly expect to see surveyed.

| Research Topic | Why Expected | Complexity | Notes |
|----------------|--------------|------------|-------|
| CFAR Variants Survey — CA-CFAR, OS-CFAR, GOCA-CFAR, SOCA-CFAR | Current system uses basic CFAR; non-homogeneous environments degrade it significantly | MEDIUM | Compare false alarm rate, detection probability, computational cost; identify which variants suit the system's clutter environment |
| ML-Based Detection Alternatives to CFAR | Active 2025 research area; autoencoder and CNN approaches demonstrate CFAR-level performance with better clutter adaptability | HIGH | Survey: autoencoder-based detection (correlation 0.73+ vs CFAR), CNN range-Doppler detectors, data-driven approaches; assess FPGA feasibility |
| Clutter Rejection — MTI, Doppler notch filtering, background subtraction | Clutter rejection is a stated pain point; engineers need systematic survey of what works | MEDIUM | Survey MTI filtering, recursive background subtraction (10-15 dB SNR improvement reported), delay-line FMCW clutter rejection; assess applicability to current FPGA pipeline |
| Pulse Compression Improvements — NLFM waveforms, sidelobe reduction | Current system uses LFM chirp; NLFM can reduce range sidelobes without SNR loss | HIGH | Survey NLFM optimization methods (genetic algorithm, iterative design), MMSE adaptive matched filter; assess chirp memory/DAC feasibility |
| Doppler Processing Improvements — 2D FFT optimization, zero-padding, windowing | Current 1024-pt FFT is fixed; windowing choice directly affects Doppler sidelobe level and velocity resolution | LOW | Survey window function tradeoffs (Hamming, Chebyshev, DPSS) for range-Doppler maps; assess impact on current 1024-pt FFT implementation |
| Target Tracking Improvements — IMM filter, adaptive Kalman | Current system uses fixed-parameter Kalman filter in GUI; maneuvering targets degrade performance | MEDIUM | Survey IMM-Kalman (outperforms EKF for maneuvering targets), variational Bayesian IMM (2025 research); assess Python implementation feasibility |

### SW Improvement Research — Differentiators

Deeper topics that make the survey genuinely actionable for improvement decisions.

| Research Topic | Value Proposition | Complexity | Notes |
|----------------|-------------------|------------|-------|
| Micro-Doppler Feature Extraction | Enables target classification (drone vs. vehicle vs. person) beyond just detection | HIGH | Survey STFT-based micro-Doppler extraction, CNN classification on range-Doppler maps, lightweight CNN for embedded use; assess compute requirements vs. current Python/FPGA budget |
| Two-Stage CFAR for 3D Radar | Current system has 3D spatial coverage (azimuth scan + elevation); two-stage CFAR approaches designed for 3D environments | HIGH | 2025 paper (Frontiers Signal Processing): two-stage CFAR with adaptive clutter distribution estimation; direct applicability to this system's scan geometry |
| FPGA Pipeline Throughput Optimization — HLS, pipelining, parallelization | Processing speed is a stated pain point; systematic optimization of Verilog pipeline can recover headroom | HIGH | Survey HLS vs. hand-coded Verilog tradeoffs, loop unrolling strategies for FFT/matched filter, multi-bank memory for parallel processing; assess Artix-7 resource margins |
| DBSCAN Parameter Optimization for Radar | Current GUI uses DBSCAN for clustering; epsilon/min_samples defaults may not be optimal for radar target density | MEDIUM | Survey density-based clustering parameter selection methods, adaptive DBSCAN variants; specific to radar point cloud characteristics |
| Adaptive Beamforming — MVDR/LCMV replacing fixed phase steering | Current system uses pre-computed phase tables in ADAR1000; adaptive beamforming rejects interference in real-time | HIGH | Survey MVDR/LCMV beamformers (99.29% detection accuracy reported 2025), hybrid robust beamforming; assess FPGA compute requirements for real-time weight computation |
| Range Extension via SNR Optimization — coherent integration, longer CPI | Detection range scales as SNR^0.25; coherent processing gain is the primary lever | MEDIUM | Survey coherent integration techniques, longer coherent processing intervals, non-coherent integration fallback; derive expected range improvement for current system parameters |

### HW Improvement Research — Table Stakes

| Research Topic | Why Expected | Complexity | Notes |
|----------------|--------------|------------|-------|
| GaN vs GaAs vs SiGe Front-End Comparison for X-Band | Current ADTR1107 is SiGe-based; GaN offers higher output power for range extension | MEDIUM | Survey GaN T/R module specifications at X-band: output power (>1W/channel reported), noise figure (≤5.5 dB), die size; compare to ADTR1107 specs |
| Higher-Resolution ADC Options | Current AD9484 is 14-bit at 400 MHz; increased ADC dynamic range directly improves clutter rejection and sensitivity | MEDIUM | Survey 14→16-bit upgrade options in same speed class, assess impact on FPGA input interface (LVDS lane count), SNR improvement calculation |
| Antenna Array Expansion — 16→32 or 64 elements | More elements = higher gain, narrower beam, better angular resolution | HIGH | Survey element count vs. array gain tradeoffs, ADAR1000 cascading (current 4 chips → 8 chips), PCB real-estate constraints, grating lobe implications |
| Improved Frequency Synthesizer Phase Noise | ADF4382 phase noise limits close-in Doppler resolution; lower phase noise LO improves slow-target detection | MEDIUM | Survey fractional-N PLL advances, compare ADF4382 phase noise spec vs. competing synthesizers; derive Doppler detection floor improvement |
| Power Management Improvements — lower idle power, more efficient PA supply | Platform power budget is a consideration; PA supply dominates at 5V rails | LOW | Survey efficient PA bias sequencing, dynamic power control per beam position, power amplifier efficiency at X-band |

### HW Improvement Research — Differentiators

| Research Topic | Value Proposition | Complexity | Notes |
|----------------|-------------------|------------|-------|
| Antenna-in-Package (AiP) / System-in-Package (SiP) Miniaturization | Hardware miniaturization is a stated pain point; AiP reduces RF board area significantly | HIGH | Survey X-band AiP implementations: 3D-stacked T/R modules at 20×20×3.7mm, LTCC antenna-on-package; assess integration compatibility with current ADAR1000+ADTR1107 architecture |
| MIMO Radar Upgrade Path — virtual aperture extension | MIMO with 16 physical elements can synthesize much larger virtual apertures without adding hardware | HIGH | Survey FMCW-MIMO waveform orthogonality requirements, virtual aperture gain derivation, FPGA processing load increase; assess feasibility as future upgrade to current 16-element array |
| Higher-Speed FPGA — Artix-7 successor (Artix UltraScale+) | XC7A100T resource and speed constraints limit pipeline improvements; newer FPGAs unblock multiple SW improvements | HIGH | Survey Artix UltraScale+ equivalents, resource comparison (LUT, DSP48, BRAM), PCB migration complexity, USB 3.0 interface compatibility |
| Digital Beamforming (DBF) — replace analog ADAR1000 with per-element ADC | True DBF enables simultaneous multi-beam, adaptive nulling, and MIMO in hardware | HIGH | Survey per-element digitization architectures, required ADC count and data rate (16× current), FPGA input bandwidth requirements; position as far-future upgrade path |
| Coherent Multi-Band Operation — X + Ku dual-band | ADAR1000 supports 8-16 GHz; coherent dual-band improves target ID and clutter rejection | HIGH | Survey dual-band coherent radar architectures, shared aperture implementations; assess ADF4382 multi-band synthesizer capability |

### Anti-Features — Improvement Research (Deliberately Out of Scope)

| Anti-Feature | Why Requested | Why Problematic | Alternative |
|--------------|---------------|-----------------|-------------|
| Implementation Specifications for Improvements | Research naturally leads to wanting to build things | PROJECT.md explicitly excludes implementation; writing implementation specs without validation produces unreliable guidance and scope creep | Close each research section with "feasibility assessment" and "recommended investigation steps" — not design specifications |
| Exhaustive Literature Review of Every CFAR Variant | Completeness instinct | Academic literature has dozens of CFAR variants; surveying all equally produces an unactionable bibliography | Focus on variants with demonstrated FPGA implementation and non-homogeneous environment performance — the system's actual constraints |
| Commercial Off-the-Shelf System Comparison | "How do we compare to X?" | Competitor analysis is marketing content, not engineering research; COTS systems use different architectures and their specs are not directly comparable | Stick to component-level and algorithm-level comparisons grounded in the actual system constraints |
| Safety / EMI / RF Exposure Research | Seems relevant to HW improvements | Regulatory and safety research requires legal expertise and type-specific measurements; not an engineering documentation task | Document RF output power levels factually in hardware docs; explicitly exclude compliance analysis |

---

## Feature Dependencies

```
Physics Documentation
    └──required by──> Signal Processing Pipeline Documentation
    └──required by──> CFAR Deep Dive
    └──required by──> Noise Figure Chain Analysis

Signal Processing Pipeline Documentation
    └──required by──> FPGA Pipeline Throughput Optimization Research
    └──required by──> CFAR Variants Survey
    └──required by──> Pulse Compression Improvements Research

RF Hardware Documentation
    └──required by──> Noise Figure Chain Analysis
    └──required by──> GaN vs SiGe Front-End Comparison
    └──required by──> Frequency Synthesizer Phase Noise Research

Antenna Array Documentation (Beamforming Theory)
    └──required by──> Antenna Calibration Procedure
    └──required by──> Adaptive Beamforming Research
    └──required by──> MIMO Upgrade Path Research

FPGA Architecture Documentation
    └──required by──> FPGA Pipeline Throughput Optimization Research
    └──required by──> Higher-Speed FPGA Research (need baseline to compare)

USB Interface Protocol Documentation
    └──required by──> Python GUI Documentation (GUI uses USB protocol)

STM32 Firmware Documentation
    └──enhances──> FPGA Architecture Documentation (control signals cross boundary)

CFAR Variants Survey (SW Research)
    └──enhances──> ML-Based Detection Research (need CFAR baseline to evaluate alternatives)

Noise Figure Chain Analysis
    └──enhances──> Range Extension Research (SNR budget defines range ceiling)
    └──enhances──> GaN Front-End Comparison (quantifies benefit of NF improvement)

Range Extension Research (SW)
    └──complements──> Antenna Array Expansion Research (HW)
    (both address range; SW via SNR, HW via gain — results must be read together)
```

### Dependency Notes

- **Physics Documentation must precede all research sections**: The CFAR derivations, waveform optimization, and noise figure analysis all require the reader to have the physics foundations. Write physics docs in Phase 1.
- **RF Hardware Documentation must precede HW improvement research**: Cannot evaluate GaN alternatives without knowing current ADTR1107 performance baseline.
- **FPGA Architecture Documentation must precede SW processing improvement research**: Pipeline optimization requires knowing current resource utilization and timing margins.
- **SW and HW range extension research are complementary, not competing**: FPGA-side coherent integration improvements and HW-side GaN power amplifier improvements address the same pain point from different angles. Both must be surveyed to give a complete picture.

---

## MVP Definition (Phased Delivery)

### Phase 1 — Foundation Documentation (v1)

The minimum that makes the rest possible. Without these, improvement research has no grounding.

- [ ] Physics Documentation — FMCW theory, LFM waveform model, beamforming theory, detection theory with full derivations — **required foundation for everything downstream**
- [ ] Signal Processing Pipeline Documentation — per-module documentation of all FPGA Verilog stages — **required before SW improvement research is credible**
- [ ] RF Hardware Documentation — component specs, register maps, signal chain — **required before HW improvement research is credible**

### Phase 2 — Complete System Documentation (v1.x)

Fills out the documentation package once the foundation is solid.

- [ ] FPGA Architecture Documentation — clock domains, CDC, resource utilization — **add once pipeline docs expose the gaps**
- [ ] STM32 Firmware Documentation — initialization, power sequencing, peripheral config — **add after FPGA docs; cross-references needed**
- [ ] Python GUI Documentation — USB protocol, DBSCAN, Kalman, map rendering — **add after firmware docs; protocol spec must come from firmware side first**
- [ ] Noise Figure Chain Analysis — cascaded NF budget — **add after hardware docs are complete; depends on component specs**
- [ ] Timing Budget and Latency Analysis — **add after pipeline docs; depends on per-stage latency data**

### Phase 3 — Improvement Research (v2)

Research only starts after documentation provides the baseline to evaluate improvements against.

- [ ] SW Improvement Research — CFAR variants, ML detection, clutter rejection, pulse compression, Doppler processing, tracking — **depends on Phase 1+2 docs for grounding**
- [ ] HW Improvement Research — GaN front-end, ADC upgrade, antenna expansion, synthesizer, miniaturization — **depends on Phase 1+2 hardware docs for baseline**

### Future Consideration (v2+)

Deeper dives warranted only if Phase 3 research identifies these as high-impact.

- [ ] MIMO Upgrade Path Research — high complexity, requires significant FPGA and antenna changes; survey only if Phase 3 identifies range extension as the top priority
- [ ] Digital Beamforming (DBF) Architecture — very high complexity; survey as long-horizon research after analog beamforming improvements are exhausted
- [ ] Micro-Doppler Classification Research — valuable but not directly tied to the four stated pain points; add if classification capability is identified as a team need

---

## Feature Prioritization Matrix

### Documentation Sections

| Section | Engineering Value | Writing Cost | Priority |
|---------|-------------------|--------------|----------|
| Physics Documentation (FMCW, waveform, beamforming) | HIGH — foundation for all reasoning | HIGH | P1 |
| Signal Processing Pipeline (FPGA modules) | HIGH — core of system, all improvement research depends on it | HIGH | P1 |
| RF Hardware Documentation | HIGH — required for HW research and debugging | HIGH | P1 |
| FPGA Architecture (clock domains, CDC) | HIGH — safety-critical for HDL changes | MEDIUM | P1 |
| STM32 Firmware Documentation | HIGH — power sequencing is hardware-damage risk | MEDIUM | P1 |
| Python GUI Documentation | MEDIUM — useful but not blocking | MEDIUM | P2 |
| Noise Figure Chain Analysis | HIGH — directly answers "why is range limited?" | MEDIUM | P2 |
| Timing Budget and Latency Analysis | MEDIUM — useful for optimization, not blocking | MEDIUM | P2 |
| Antenna Calibration Procedure | MEDIUM — important for array performance | HIGH | P2 |
| GPS/IMU Coordinate Transform Math | MEDIUM — documents existing behavior | LOW | P2 |
| Power Budget Analysis | LOW — informational | LOW | P3 |

### SW Improvement Research Topics

| Topic | Impact on Pain Points | Research Cost | Priority |
|-------|----------------------|---------------|----------|
| CFAR Variants Survey | HIGH — directly addresses clutter rejection and detection | MEDIUM | P1 |
| Clutter Rejection (MTI, background subtraction) | HIGH — stated pain point | MEDIUM | P1 |
| Range Extension via SNR Optimization | HIGH — stated pain point | MEDIUM | P1 |
| FPGA Pipeline Throughput Optimization | HIGH — stated pain point (processing speed) | HIGH | P1 |
| ML-Based Detection (CFAR alternative) | MEDIUM-HIGH — active research, strong results reported | HIGH | P2 |
| Pulse Compression Improvements (NLFM) | MEDIUM — improves sidelobes, indirect range benefit | HIGH | P2 |
| Target Tracking Improvements (IMM) | MEDIUM — improves track quality on maneuvering targets | MEDIUM | P2 |
| Doppler Processing Improvements (windowing) | LOW-MEDIUM — incremental improvement | LOW | P3 |
| Adaptive Beamforming (MVDR/LCMV) | MEDIUM — interference rejection benefit | HIGH | P3 |
| Micro-Doppler Classification | LOW for stated pain points — classification not a stated need | HIGH | P3 |
| DBSCAN Parameter Optimization | LOW — incremental, easy to tune empirically | LOW | P3 |

### HW Improvement Research Topics

| Topic | Impact on Pain Points | Research Cost | Priority |
|-------|----------------------|---------------|----------|
| GaN vs SiGe Front-End Comparison | HIGH — range extension (higher Tx power) | MEDIUM | P1 |
| Improved Frequency Synthesizer Phase Noise | MEDIUM-HIGH — slow-target detection, Doppler floor | MEDIUM | P1 |
| Antenna-in-Package Miniaturization | HIGH — stated pain point (miniaturization) | MEDIUM | P1 |
| Higher-Resolution ADC | MEDIUM — dynamic range improvement | MEDIUM | P2 |
| Antenna Array Expansion (16→32 elements) | MEDIUM — range and angular resolution | HIGH | P2 |
| Higher-Speed FPGA (Artix UltraScale+) | MEDIUM — enables SW improvements that hit current resource limits | HIGH | P2 |
| MIMO Upgrade Path | LOW-MEDIUM for near-term — architectural change | HIGH | P3 |
| Dual-Band Operation | LOW for stated pain points | HIGH | P3 |
| Digital Beamforming (DBF) | LOW for near-term — very high architectural cost | HIGH | P3 |

**Priority key:**
- P1: Address in Phase 3 research as core deliverables
- P2: Include in Phase 3 research as supporting sections
- P3: Survey briefly or defer; not directly tied to stated pain points

---

## Sources

- [FPGA Parallel Processing for Radar — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11723343/) — FPGA throughput optimization (HIGH confidence)
- [Two-Stage CFAR for 3D Radar — Frontiers Signal Processing 2025](https://www.frontiersin.org/journals/signal-processing/articles/10.3389/frsip.2025.1688944/full) — CFAR improvements (MEDIUM confidence)
- [Advancements in mmWave Radar Signal Processing — MDPI Electronics 2025](https://www.mdpi.com/2079-9292/14/7/1436) — SW improvement landscape (MEDIUM confidence)
- [Autoencoder-Based Target Detection in MIMO FMCW — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9370841/) — ML-based CFAR alternative (MEDIUM confidence)
- [Hybrid Robust Beamforming for Phased Array — PMC 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12706067/) — Adaptive beamforming (MEDIUM confidence)
- [Sparse Phased Array Optimization Using Deep Learning — arXiv 2025](https://arxiv.org/html/2504.17073v1) — DL beamforming (MEDIUM confidence)
- [Altum RF Front-End Components for X/Ku Band Phased Array — Nov 2025](https://www.altumrf.com/app/uploads/2025/12/Altum-RF-Front-end-Components-for-X-Ku-Band-Phased-Array-radar-Nov-2025.pdf) — HW improvement landscape (MEDIUM confidence)
- [CFAR Algorithm FPGA Implementation — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9861839/) — CFAR FPGA feasibility (HIGH confidence)
- [Ground Clutter Mitigation with MTI — MathWorks](https://www.mathworks.com/help/radar/ug/ground-clutter-mitigation-with-moving-target-indication-mti-radar.html) — clutter rejection techniques (HIGH confidence)
- [NLFM Waveform Optimization — Scientific Reports 2025](https://www.nature.com/articles/s41598-025-23766-6) — pulse compression improvements (MEDIUM confidence)
- [Variational Bayesian IMM for Maneuvering Target Tracking — MDPI 2025](https://www.mdpi.com/2079-9292/14/10/1908) — tracking improvements (MEDIUM confidence)
- [Electronic Warfare and Radar Systems Engineering Handbook — NAVAIR](https://apps.dtic.mil/sti/tr/pdf/ADA617071.pdf) — documentation structure reference (HIGH confidence)
- [Principles of Modern Radar — IET Digital Library](https://digital-library.theiet.org/doi/book/10.1049/sbra021e) — standard documentation structure (HIGH confidence)
- ADAR1000, ADTR1107 datasheets — Analog Devices (component documentation baseline, HIGH confidence)

---

*Feature research for: AERIS-10 PLFM Radar System documentation and improvement research*
*Researched: 2026-03-13*
