# Project Research Summary

**Project:** AERIS-10 PLFM Radar — Engineering Documentation & Improvement Research
**Domain:** Multi-layer engineering documentation set for a custom FMCW phased array radar system
**Researched:** 2026-03-13
**Confidence:** HIGH

## Executive Summary

The AERIS-10 is a fully built 10 GHz FMCW phased array radar with a 16-element antenna array (ADAR1000 beamformer), Xilinx Artix-7 XC7A100T FPGA signal processing pipeline, STM32F746 microcontroller, and a Python GUI with DBSCAN clustering and Kalman tracking. This project is not building software — it is building a structured engineering knowledge base for a complex, already-operational multi-domain system. The correct approach is a layered documentation architecture where physics derivations are written first, hardware documentation builds on them, software documentation builds on hardware, and improvement research surveys reference the complete system documentation as a baseline. This strict dependency order is not a stylistic preference; it is a technical requirement. Research surveys written before the baseline documentation exists will recommend improvements that are either already implemented, based on incorrect system parameters, or infeasible on the actual hardware.

The recommended toolchain is deliberately minimal: GitHub-native Markdown with MathJax for equations, draw.io SVG exports for hardware block diagrams, Mermaid for software flow diagrams, WaveDrom for FPGA timing diagrams, and Zotero for research citation management. All tooling is free and renders natively in GitHub, keeping the documentation inside the version-controlled repository where the engineering team already works. The most important documentation decision is establishing a project-wide notation table and a single system parameter table before writing a single physics derivation — inconsistent notation across physics, hardware, and software documents is the highest-probability failure mode for a project of this complexity.

The primary risk is scope creep and ordering violations. There is strong pressure to skip ahead to the research surveys (the most intellectually interesting deliverable) before the system documentation is solid enough to ground them. Improvement recommendations made without a documented noise figure chain, without a documented FPGA resource budget, and without a canonical software version designation will be academically interesting but operationally useless. The roadmap must enforce the dependency chain strictly and treat notation standardization as a zero-phase prerequisite, not as a Phase 1 deliverable.

## Key Findings

### Recommended Stack

The toolchain is GitHub-resident and zero-friction for an engineering team already using Git. GitHub natively renders MathJax math (since May 2022), Mermaid diagrams, and SVG images in all `.md` files, PRs, and Issues. No static site generator, documentation platform, or build step is required. draw.io exports version-controllable `.drawio` XML to the repository while SVG exports render as images. WaveDrom handles digital signal timing diagrams (not natively rendered on GitHub — export to SVG). Zotero manages the academic literature with IEEE citation style for the improvement research surveys. Python + matplotlib generates reproducible signal-model figures from the existing codebase. The full stack is already largely available in the repository context.

**Core technologies:**
- GitHub Markdown + MathJax: Primary document format with native equation rendering — eliminates compile step
- draw.io (v24+): Hardware block diagrams, RF signal chains, antenna geometry — version-controllable XML source
- Mermaid (v11+, GitHub-native): Software pipeline flowcharts, FPGA state machines — do NOT use for RF hardware layouts
- WaveDrom (v3+): FPGA/MCU timing diagrams — export to SVG for GitHub embedding
- Zotero (v7): IEEE citation management for improvement research surveys — free, BibTeX export
- Python + matplotlib: Reproducible documentation figures from existing codebase scripts
- markdownlint: Consistency enforcement across multi-author documentation

**Critical version notes:**
- GitHub MathJax `$...$` syntax requires `.md` file extension (does not render in `.txt`)
- `\tag{}` for equation numbering is confirmed supported in GitHub MathJax
- WaveDrom does not render natively on GitHub — always export to SVG

**What NOT to use:**
- Word/Google Docs, Confluence, Notion — breaks docs-as-code workflow
- Image-rendered LaTeX (codecogs.com) — dark mode breakage, not copy-pasteable, URL-dependent
- Sphinx+RST — unnecessary complexity for this use case

### Expected Features

The feature set spans two parallel dimensions: documentation sections (what the documentation package must contain) and improvement research topics (what literature must be surveyed). These dimensions have a strict dependency: research cannot be written credibly before documentation is complete.

**Must have — Documentation (Phase 1 foundation):**
- Physics documentation: FMCW theory, LFM waveform model, beamforming derivations, detection theory with full first-principles derivations — foundation for all downstream documents
- Signal processing pipeline documentation: per-module documentation of the full FPGA Verilog pipeline (DDC → CIC → matched filter → 1024-pt FFT → CFAR) — required before software improvement research is credible
- RF hardware documentation: ADTR1107, LT5552, ADF4382, AD9484, ADAR1000 component specs, register maps, SPI sequences — required before hardware improvement research is credible
- FPGA architecture documentation: clock domains (100/120/400 MHz), CDC synchronizers, resource utilization — safety-critical for HDL changes
- STM32 firmware documentation: power sequencing, peripheral initialization — hardware damage risk without this

**Must have — Documentation (Phase 2 completeness):**
- Python GUI documentation: USB protocol, DBSCAN parameters, Kalman state model, architecture (GUI_V6.py only — V1-V5 explicitly excluded)
- Noise figure chain analysis: cascaded NF through full receive chain — directly answers detection range limits
- Timing budget and latency analysis: ADC to detection pipeline latency
- Antenna calibration procedure: ADAR1000 phase error correction

**Must have — Improvement Research (Phase 3):**
- SW: CFAR variants survey (CA-CFAR, OS-CFAR, GOCA-CFAR, SOCA-CFAR), clutter rejection (MTI, background subtraction), range extension via SNR optimization, FPGA pipeline throughput optimization
- HW: GaN vs SiGe front-end comparison, frequency synthesizer phase noise, antenna-in-package miniaturization

**Should have — Improvement Research:**
- SW: ML-based detection (autoencoder/CNN alternatives to CFAR), NLFM pulse compression, IMM target tracking, adaptive beamforming (MVDR/LCMV)
- HW: Higher-resolution ADC, antenna array expansion (16→32 elements), Artix UltraScale+ upgrade path

**Defer to future consideration (v2+):**
- MIMO upgrade path (high architectural cost, low near-term impact)
- Digital beamforming (DBF) architecture (very high complexity, far-horizon upgrade)
- Micro-Doppler classification (not tied to stated pain points)
- Dual-band coherent operation
- DBSCAN parameter optimization (empirically tunable, low research value)

**Deliberate anti-features (out of scope):**
- Operator/user manuals — wrong audience
- Regulatory/EMC/safety compliance analysis — requires legal expertise
- Implementation specifications for improvements — PROJECT.md explicitly excludes implementation
- Tutorial-style walkthroughs — wrong audience depth
- Exhaustive CFAR literature survey — focus on FPGA-implementable variants only

### Architecture Approach

The documentation architecture is a strict four-layer hierarchy: Layer 1 (Physics) → Layer 2 (Hardware) → Layer 3 (Software) → Layer 4 (Research Surveys). No document may reference a document in a higher layer. Physics documents provide mathematical foundations; hardware documents assign actual component values to those equations; software documents show how hardware is controlled and data processed; research surveys take the complete system documentation as their baseline and evaluate improvements against it. The critical path through this hierarchy runs: `physics/01_fmcw_theory.md` → `physics/02_signal_model.md` → `software/01_fpga_pipeline.md`, because the FPGA pipeline is the most complex and most-referenced document in the set, and everything flows through it.

**Major documentation components:**
1. `physics/` (4 docs) — FMCW theory, signal model, beamforming, detection theory — pure mathematics, no component model numbers
2. `hardware/` (6 docs) — system overview (master parameter table), RF front-end, frequency synthesis, antenna array, FPGA board, power management
3. `software/` (3 docs) — FPGA pipeline (by signal flow, not by module), STM32 firmware, Python GUI
4. `research/` (3 docs) — SW target detection, SW signal processing, HW improvements — each opens with current-state section before literature survey

**Key patterns to follow:**
- Single source of truth: All numerical system parameters live in `hardware/01_system_overview.md`; all other documents link to it
- Interface-contract cross-references: Reference specific anchored sections, not entire documents
- Research survey structure: "Current State / Literature / Gap Analysis" in every research document
- Variant callout blocks: AERIS-10 Nexus (3 km) vs. Extended (20 km) differences marked explicitly

### Critical Pitfalls

1. **Inconsistent notation across physics/hardware/software** — Create a project-wide symbol table as the first deliverable before writing a single equation. Define the master symbol set in `hardware/01_system_overview.md` and enforce it across all documents. Recovery mid-project is HIGH cost.

2. **Range-Doppler coupling omitted from physics derivation** — The beat frequency `f_b = (2SR)/c ± f_d` is frequently documented without the Doppler term. Derive the full expression first; introduce the stationary-target simplification explicitly as an annotated assumption. All CFAR documentation downstream depends on this being correct.

3. **CFAR documentation missing clutter model assumptions** — Document which CFAR variant (CA/OS/GOCA/SOCA) is implemented, the assumed clutter distribution, and the guard cell/reference window derivation. Research survey CFAR alternatives cannot be meaningfully evaluated without this baseline.

4. **Software improvement research proposing hardware-incompatible algorithms** — Every algorithm recommendation must include a hardware feasibility annotation: Artix-7 XC7A100T resource estimate (269,200 LUTs, 240 DSP48E1s), USB 3.0 bandwidth compatibility, and pipeline integration complexity. Academic benchmarks on Zynq UltraScale+ or GPU are not transferable without this translation.

5. **Multi-version code confusion in software documentation** — The repository contains 9 GUI versions. Designate GUI_V6.py as canonical before any software documentation begins. Document only V6; explicitly note that V1–V5 are historical and undocumented. Magic numbers in `main.cpp` (PRI1 = 167 µs, Guard = 175.4 µs, 31-element phase differences array) must be traced to derivations or calibration procedures — not left as unexplained constants.

## Implications for Roadmap

Based on research, the documentation project has a strict 8-phase build order driven by the dependency graph. Phases 2 and 3 can be partially parallelized internally; Phases 4 and 5 can be parallelized within their groups. The critical path is physics/01 → physics/02 → software/01_fpga_pipeline.

### Phase 0: Notation and Parameter Standardization

**Rationale:** Establishing the notation table and master system parameter table before any physics writing begins eliminates the highest-probability failure mode. Recovery from notation inconsistency mid-project is HIGH cost — this cannot be treated as a Phase 1 deliverable.
**Delivers:** Project-wide symbol table (IEEE 686-2024 compliant), master system parameter table in `hardware/01_system_overview.md` (center frequency, chirp bandwidth, PRF, ADC rate, antenna gain, noise figure, XC7A100T resources)
**Avoids:** Inconsistent notation pitfall (Pitfall 2), hardware facts embedded in software docs anti-pattern

### Phase 1: Physics Foundation

**Rationale:** All hardware, software, and research documents ultimately reference physics derivations. FMCW theory must precede signal model; signal model must precede detection theory. No downstream document can be written correctly without this layer.
**Delivers:** `physics/01_fmcw_theory.md`, `physics/02_signal_model.md`, `physics/03_beamforming.md`, `physics/04_detection_theory.md`
**Addresses:** FMCW theory, waveform model, beamforming theory, CFAR derivation (all P1 documentation table stakes)
**Avoids:** Range-Doppler coupling omission (Pitfall 1), beamforming array factor gap (Pitfall 4), physics derivations mixed into hardware/software docs (Anti-Pattern 3)
**Uses:** GitHub MathJax `$$` blocks with `\tag{}` equation numbering, IEEE 686-2024 notation

### Phase 2: Hardware Documentation

**Rationale:** Hardware parameters (noise figure, gain, component specs) are inputs to the physics radar equation and are required before the FPGA pipeline doc can reference actual signal levels. The system overview must be written first to anchor all subsystem cross-references.
**Delivers:** `hardware/01_system_overview.md` (master parameter table), `hardware/02_rf_frontend.md`, `hardware/03_frequency_synthesis.md`, `hardware/04_antenna_array.md`, `hardware/05_fpga_board.md`, `hardware/06_power_management.md`
**Addresses:** RF hardware table stakes, FPGA architecture, STM32 power sequencing (hardware-damage risk)
**Avoids:** Hardware research without RF link budget (Pitfall 6), hardware docs by BOM not by functional block (documentation mistake)
**Uses:** draw.io SVG for block diagrams, WaveDrom for timing diagrams, direct datasheet cross-references

### Phase 3: Software Documentation

**Rationale:** The FPGA pipeline document is the most complex single deliverable and the most referenced document in the set — it must be written before the GUI or STM32 docs (which reference its data formats). STM32 and GUI docs can be parallelized after FPGA pipeline is complete.
**Delivers:** `software/01_fpga_pipeline.md` (DDC → CIC → matched filter → 1024-pt FFT → CFAR by signal flow), `software/02_stm32_firmware.md`, `software/03_python_gui.md`
**Addresses:** Signal processing pipeline, FPGA architecture, USB protocol, DBSCAN/Kalman tracking (all table stakes)
**Avoids:** FPGA docs written by module not signal flow (documentation mistake), multi-version code confusion (Pitfall 7), CFAR clutter model assumption missing (Pitfall 3)
**Uses:** Mermaid for pipeline flowcharts, WaveDrom for timing, canonical version = GUI_V6.py

### Phase 4: Supporting Analysis

**Rationale:** Noise figure chain and timing budget analyses are high-value additions that require Phase 2 hardware documentation and Phase 3 software documentation to be complete. These analyses answer "why is range limited?" and "how much processing headroom do we have?" directly.
**Delivers:** Noise figure chain analysis (embedded in RF front-end or system overview), timing budget and pipeline latency analysis, antenna calibration procedure, GPS/IMU coordinate transform documentation
**Addresses:** P2 documentation features that depend on earlier phases
**Avoids:** Improvement research referencing undocumented range limits, hardware research without RF link budget (Pitfall 6 reinforcement)

### Phase 5: Software Improvement Research

**Rationale:** Research cannot start until Phase 1-3 system documentation provides the baseline to evaluate improvements against. Each research doc must open with a current-state section before surveying the literature.
**Delivers:** `research/01_sw_target_detection.md` (CFAR variants, ML detection), `research/02_sw_signal_processing.md` (clutter rejection, NLFM, Doppler processing, tracking)
**Addresses:** All P1 SW improvement research topics (CFAR variants, clutter rejection, range extension, FPGA throughput), P2 topics (ML detection, NLFM, IMM tracking)
**Avoids:** Software research incompatible with hardware (Pitfall 5) — every recommendation tagged with Artix-7 feasibility assessment
**Uses:** Zotero for IEEE citation management, structure: Current State / Literature / Gap Analysis

### Phase 6: Hardware Improvement Research

**Rationale:** Hardware improvement research can run in parallel with Phase 5 software research, but requires Phase 2 hardware documentation (particularly the RF link budget) to be complete. Every recommendation must trace its impact through the noise figure chain.
**Delivers:** `research/03_hw_improvements.md` (GaN front-end, ADC upgrade, antenna expansion, AiP miniaturization, synthesizer phase noise, FPGA upgrade path)
**Addresses:** All P1 HW improvement topics (GaN comparison, synthesizer phase noise, AiP miniaturization), P2 topics (ADC upgrade, array expansion, Artix UltraScale+)
**Avoids:** Hardware research without RF link budget (Pitfall 6) — every recommendation references noise figure delta

### Phase Ordering Rationale

- Phases 0-1-2-3 are strictly sequential: dependency chain from notation → physics → hardware → software is absolute
- Phase 4 supporting analysis can overlap with the tail of Phase 3 (once hardware docs are complete)
- Phases 5 and 6 can run in parallel after Phase 3 is complete
- The 8-phase architecture build order from ARCHITECTURE.md maps directly onto phases 1-3, with research in phases 5-6

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (FPGA Pipeline Documentation):** Highest complexity single deliverable; 10+ Verilog modules, 3 clock domains, known CDC issues documented in CONCERNS.md. Recommend dedicated planning session to define module-by-module documentation scope before writing begins.
- **Phase 5 (SW Improvement Research):** ML-based detection and FPGA throughput optimization are rapidly evolving areas (2024-2025 literature). Feasibility assessments against Artix-7 constraints require careful resource modeling — these will likely surface tradeoffs not obvious from academic benchmarks.
- **Phase 6 (HW Improvement Research):** GaN front-end and AiP miniaturization research requires careful RF link budget grounding. The two AERIS-10 variants (Nexus vs. Extended) have different power budgets; research must address both.

Phases with standard patterns (can proceed without additional research):
- **Phase 0 (Notation):** IEEE 686-2024 notation is authoritative; symbol conventions are well-established
- **Phase 1 (Physics):** FMCW theory is mature; derivation structure follows standard Skolnik/Richards/Mahafza conventions
- **Phase 2 (Hardware):** Component datasheets are available; draw.io + WaveDrom documentation patterns are well-defined
- **Phase 4 (Supporting Analysis):** Noise figure chain and latency analysis are standard engineering calculations

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All tools verified against official documentation sources; GitHub MathJax confirmed with release notes; tooling is mature and widely adopted |
| Features | HIGH (documentation) / MEDIUM (research topics) | Documentation sections derived from direct codebase analysis; improvement research topics grounded in 2024-2025 academic literature with MEDIUM confidence on ML/advanced techniques |
| Architecture | HIGH | Architecture derived from direct codebase inspection of all Verilog modules, Python files, and firmware — primary source, highest confidence |
| Pitfalls | HIGH (physics/signal-processing) / MEDIUM (process) | Physics pitfalls backed by IEEE sources and direct codebase analysis; documentation process pitfalls based on engineering project patterns |

**Overall confidence:** HIGH

### Gaps to Address

- **Canonical chirp parameters for Extended vs. Nexus variant:** The documentation must specify which variant's parameters are used in physics derivations; both variants should be addressed with callout blocks. Clarify with the engineering team which variant is primary before Phase 1 begins.
- **FPGA resource utilization baseline:** Current Vivado implementation reports are needed before Phase 3 FPGA pipeline documentation and Phase 5 feasibility assessments can be written accurately. Confirm these reports are accessible in the repository.
- **CFAR variant actually implemented:** PITFALLS.md identifies the need to document which CFAR variant (CA/OS/GOCA/SOCA) is implemented in the Verilog. Inspect `doppler_processor.v` / CFAR module source before beginning Phase 3.
- **Magic numbers in main.cpp:** PRI1 = 167 µs, Guard = 175.4 µs, and the 31-element phase differences array require derivation traces. These must be resolved during Phase 2-3 (hardware/software documentation), not deferred to research phases.

## Sources

### Primary (HIGH confidence)
- PLFM_RADAR codebase direct analysis (Verilog modules, Python GUI, STM32 firmware) — system architecture and pitfall identification
- PLFM_RADAR CONCERNS.md — known bugs, tech debt, fragile implementation areas
- PLFM_RADAR PROJECT.md — system architecture and project constraints
- [GitHub Writing Mathematical Expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions) — MathJax support confirmed
- [IEEE 686-2024 Standard for Radar Definitions](https://standards.ieee.org/ieee/686/10853/) — notation authority
- [IEEE 521-2019 Letter Designations for Radar-Frequency Bands](https://ieeexplore.ieee.org/document/8999849/) — X-band definition
- [Infineon FMCW Radar DSP Handout](https://www.infineon.com/dgdl/Infineon-FMCW_RADAR_Digital_Signal_Processing_Handout-Training-v01_00-EN.pdf) — pipeline structure and pitfall patterns
- [NATO RTO EN-SET-086bis: Signal Processing for Phased Array Radar](https://publications.sto.nato.int/publications/STO%20Educational%20Notes/RTO-EN-SET-086bis/EN-SET-086bis-01.pdf) — beamforming notation conventions
- [NAVAIR Electronic Warfare and Radar Systems Engineering Handbook](https://apps.dtic.mil/sti/tr/pdf/ADA617071.pdf) — documentation structure reference
- Analog Devices ADAR1000, ADTR1107 datasheets — component baseline

### Secondary (MEDIUM confidence)
- [Two-Stage CFAR for 3D Radar — Frontiers Signal Processing 2025](https://www.frontiersin.org/journals/signal-processing/articles/10.3389/frsip.2025.1688944/full) — CFAR improvements
- [Advancements in mmWave Radar Signal Processing — MDPI Electronics 2025](https://www.mdpi.com/2079-9292/14/7/1436) — SW improvement landscape
- [Autoencoder-Based Target Detection in MIMO FMCW — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9370841/) — ML detection alternatives
- [Hybrid Robust Beamforming for Phased Array — PMC 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12706067/) — adaptive beamforming
- [NLFM Waveform Optimization — Scientific Reports 2025](https://www.nature.com/articles/s41598-025-23766-6) — pulse compression
- [Variational Bayesian IMM for Maneuvering Target Tracking — MDPI 2025](https://www.mdpi.com/2079-9292/14/10/1908) — tracking improvements
- [Altum RF Front-End Components for X/Ku Band — Nov 2025](https://www.altumrf.com/app/uploads/2025/12/Altum-RF-Front-end-Components-for-X-Ku-Band-Phased-Array-radar-Nov-2025.pdf) — HW improvement landscape
- [FPGA Parallel Processing for Radar — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11723343/) — throughput optimization
- [CFAR Performance Analysis — Taylor & Francis 2024](https://www.tandfonline.com/doi/full/10.1080/01431161.2024.2408494) — clutter distribution assumptions

---
*Research completed: 2026-03-13*
*Ready for roadmap: yes*
