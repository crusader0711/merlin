# Pitfalls Research

**Domain:** FMCW radar system documentation & improvement research (embedded: FPGA + MCU + desktop SW)
**Researched:** 2026-03-13
**Confidence:** HIGH (physics/signal-processing pitfalls) / MEDIUM (documentation process pitfalls)

---

## Critical Pitfalls

### Pitfall 1: Range-Doppler Coupling Undocumented or Incorrectly Derived

**What goes wrong:**
Derivations present beat frequency as a pure range measurement without clearly stating the Doppler-coupling assumption. Readers (and future implementers) believe range is unambiguous when in reality the beat frequency `f_b = (2·S·R)/c ± f_d` conflates range and radial velocity. Documentation that omits the coupling term causes incorrect range estimates for moving targets and makes the CFAR threshold logic inexplicable without tribal knowledge.

**Why it happens:**
Most textbook FMCW derivations assume a stationary target to simplify the math. Writers copy the simplified result into system documentation without restating the assumption, leaving the Doppler term implicit and invisible.

**How to avoid:**
Derive the full beat-frequency expression including the Doppler term before introducing the stationary-target simplification. Annotate every formula that uses the simplified form with an explicit assumption box: "Valid only for |v_r| << c·B/(2·f_c·T)". Show the triangle-sweep (up/down chirp) decoupling technique and document whether the AERIS-10 implements it or ignores it.

**Warning signs:**
- Beat-frequency derivation shows only one term (`f_b = 2SR/c`) with no mention of velocity
- CFAR documentation says "range bin" without explaining what happens when a target moves
- MATLAB code uses only a single-slope chirp with no velocity correction

**Phase to address:**
Physics documentation phase (earliest phase). All downstream signal-processing and CFAR docs depend on this derivation being correct.

---

### Pitfall 2: Inconsistent Variable Notation Across Physics, Hardware, and Software Docs

**What goes wrong:**
The FPGA doc calls the chirp bandwidth `B`, the physics doc calls it `Δf`, and the MATLAB doc calls it `sweep_bw`. Readers cannot trace a parameter from first-principles formula to register value without manually reconciling notation. Cross-referencing breaks silently — a reader following "see equation (3)" lands in a document using completely different symbols.

**Why it happens:**
Physics, hardware, and software documents are written independently by (or for) different domains. Each domain uses its own conventional notation. Without a master symbol table defined at the start, each doc drifts toward its own convention.

**How to avoid:**
Define a project-wide notation table before writing any physics derivation. Enforce it: every document opens with a "Notation" section that maps its local symbols to the master table. For hardware parameters (e.g., chirp slope, ADC sample rate), anchor the notation to the actual hardware register names used in the STM32 code and FPGA constraints file so software and physics derivations share the same identifiers.

**Warning signs:**
- A parameter (e.g., carrier frequency) has three different names across three docs
- "See the hardware documentation" cross-references resolve to docs that use different units (MHz vs GHz, µs vs samples)
- Magic numbers in `main.cpp` (like `const float PRI1 = 167.0f`) are never mapped back to a derived equation

**Phase to address:**
First physics documentation phase, as a prerequisite. Must be established before any other doc is written, or every subsequent document will need a full revision pass.

---

### Pitfall 3: CFAR Documentation That Omits Clutter Model Assumptions

**What goes wrong:**
The CA-CFAR (Cell-Averaging CFAR) implemented in the FPGA is documented as "the CFAR stage" without stating which clutter distribution it assumes (Rayleigh/Gaussian). Readers attempting to evaluate improvements (CFAR variants, ML-based detection) cannot compare alternatives without knowing what model the current implementation uses. Research survey sections end up recommending algorithms that are not meaningfully better for the actual clutter environment this radar operates in.

**Why it happens:**
CA-CFAR is the default starting point taught in textbooks and is sometimes implemented without consciously choosing a clutter model. Whoever built the FPGA pipeline chose it because it is standard; the documentation inherits this lack of explicit rationale.

**How to avoid:**
Document the CFAR stage with three items: (1) which CFAR variant is implemented (CA, OS, GOCA, SOCA), (2) the assumed clutter distribution and why it was chosen, (3) the guard cells and reference window size with a derivation showing how those values were set for the AERIS-10's specific range resolution and operating environment. In the improvement research, always evaluate candidate algorithms against the same clutter model before recommending them.

**Warning signs:**
- FPGA CFAR documentation describes only the threshold formula, not the assumptions behind it
- Improvement research recommends CFAR variants without stating operating environment (land, sea, weather)
- Guard cell count and reference window size appear as magic numbers with no derivation

**Phase to address:**
FPGA signal-processing documentation phase. The improvement research survey for software depends on this being correct.

---

### Pitfall 4: Beamforming Doc That Skips the Array Factor Derivation

**What goes wrong:**
Beamforming is documented as "the ADAR1000 applies phase shifts to steer the beam." This tells the reader nothing about grating lobes, scan blindness, half-wavelength element spacing constraints, or the relationship between phase quantization (the ADAR1000 provides 2.8° resolution) and beam-pointing error. When the hardware improvement research evaluates miniaturization or array reconfiguration options, the team has no analytical basis for predicting beam quality degradation.

**Why it happens:**
Beamforming documentation tends to be written from the hardware configuration perspective ("here is how to program the ADAR1000") rather than from the signal-processing perspective ("here is why the array is designed the way it is"). The chip datasheet covers register-level programming; nobody writes the physics layer.

**How to avoid:**
Derive the array factor for a uniform linear array (ULA) from first principles. Show explicitly: element spacing d = λ/2 at 10 GHz, the steering vector `a(θ) = [1, e^{j2πd sinθ/λ}, ..., e^{j2π(N-1)d sinθ/λ}]^T`, the grating lobe condition, and the mapping from ADAR1000 6-bit phase word to actual phase shift to beam-pointing error. Document the 16-element array geometry (4 ADAR1000 chips × 4 channels each).

**Warning signs:**
- Hardware doc describes ADAR1000 SPI register writes without explaining which phase values are loaded and why
- Phase differences array in `main.cpp` (31 hardcoded floats) is never traced back to an array geometry derivation
- No mention of grating lobes or scan range limits in any document

**Phase to address:**
Physics documentation phase. Hardware documentation for the RF front-end depends on it.

---

### Pitfall 5: Software Improvement Research That Proposes Changes Incompatible With Fixed Hardware

**What goes wrong:**
The improvement research recommends algorithms (e.g., 2D-FFT Doppler processing, STAP, deep-learning-based detection) without stating their computational requirements against the existing FPGA (Xilinx Artix-7 XC7A100T) and USB pipeline constraints. The team reads the survey and cannot determine what is actually implementable on this hardware without doing their own analysis.

**Why it happens:**
Research surveys draw from academic literature that typically benchmarks on high-end platforms (Zynq UltraScale+, GPU clusters). Authors copy algorithm descriptions from papers without translating resource requirements to the actual target platform.

**How to avoid:**
For every algorithm improvement recommended in the software research survey, include a hardware feasibility annotation: (a) estimated FPGA LUT/DSP usage relative to XC7A100T resources (269,200 LUTs, 240 DSP48E1s), (b) whether it fits the existing 1024-pt FFT pipeline or requires architectural changes, (c) whether USB 3.0 bandwidth (FT601) is a bottleneck for the data rates it requires. Clearly separate "feasible on current AERIS-10" from "requires hardware upgrade."

**Warning signs:**
- Research survey uses phrases like "high computational efficiency" without citing clock cycles or resource counts
- Recommended algorithms are benchmarked only on MATLAB/Python simulations, not on Artix-7 class devices
- No section in the research maps recommendations back to existing hardware constraints

**Phase to address:**
Software improvement research phase. Must check FPGA constraints before finalizing any recommendation.

---

### Pitfall 6: Hardware Improvement Research That Ignores RF System Budget

**What goes wrong:**
Hardware improvement research recommends component swaps (better ADC, different LNA, updated synthesizer) without tracing the impact through the full RF chain: noise figure, dynamic range, and SNR budget. A recommended component change that improves one stage but degrades another goes undetected because the system link budget is never computed in the documentation.

**Why it happens:**
Component-level documentation focuses on individual specs (ADC ENOB, LNA noise figure) without integrating them into a radar range equation analysis. The radar range equation is the tool that connects all hardware parameters to detection range, but it is often presented only in the physics section and never linked back to hardware choices.

**How to avoid:**
In the hardware documentation, build a complete noise/link budget table that includes: TX power → antenna gain → free-space loss → target RCS → receive antenna gain → LNA noise figure → ADC noise floor → SNR at CFAR input. Every hardware improvement recommendation must state where in this chain it acts and what delta-SNR it achieves.

**Warning signs:**
- Hardware docs discuss ADC sample rate and bit depth without computing ENOB contribution to noise floor
- Improvement research recommends a "higher-performance ADC" without quantifying the SNR improvement
- Radar range equation appears only in the physics section, never referenced in hardware documentation

**Phase to address:**
Hardware documentation phase, before hardware improvement research is written.

---

### Pitfall 7: Multi-Version Code Confusion in Software Documentation

**What goes wrong:**
The repository contains 9 GUI versions (V1 through V6 plus demo variants). Documentation that describes "the GUI" without specifying which version creates an ambiguity that compounds over time. Documenting an obsolete version wastes effort; documenting all versions is impossible; documenting only V6 while old versions remain in the repo leaves readers wondering whether the old code is authoritative.

**Why it happens:**
This is already present in the AERIS-10 codebase (see CONCERNS.md). Documentation projects typically begin by reading the code — if the canonical version is not clearly designated before documentation starts, the writer documents whatever version they read first.

**How to avoid:**
Designate the canonical version (GUI_V6.py) explicitly in a documentation scope decision at the start of the software documentation phase. Add a note in the docs that V1–V5 are historical and not documented. Do not document known bugs in obsolete versions (like the V4 CSV variant) — document only the current canonical implementation, while noting where V6 still has known issues (e.g., the hardcoded 64-byte packet stub, the bare `except: pass` blocks).

**Warning signs:**
- Software documentation section headers say "the GUI" without a version number
- Bug descriptions reference line numbers that don't exist in V6 (because they're from V5)
- "Known issues" section lists problems that were already fixed in a newer version

**Phase to address:**
Software documentation phase, as a setup step before any code reading begins.

---

## Technical Debt Patterns

Shortcuts in documentation that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skipping derivation steps ("it can be shown that...") | Faster writing | Reader cannot verify or extend; errors propagate | Never — this project requires full derivations |
| Documenting intended behavior instead of actual behavior | Cleaner docs | Misrepresents the system; engineers debug against wrong model | Never for this project scope |
| Copying parameter values from datasheets without tracing to code | Fast hardware coverage | Hardcoded magic numbers (like in `main.cpp`) remain unexplained | Never — every constant needs a derivation anchor |
| Writing research survey without implementation feasibility check | Broad coverage | Recommendations are not actionable for the actual platform | Never — annotate all recommendations with hardware feasibility |
| Documenting only the happy path in firmware state machines | Simpler flow diagrams | Error conditions (like the `Error_Handler` infinite loop) appear intentional | Never for safety-critical paths |
| Using informal units in derivations (e.g., "frequency in MHz") | Faster writing | Unit errors cascade; SI units with explicit conversion required | Never in physics derivations |

---

## Integration Gotchas

Common mistakes when documenting the boundaries between system components.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| FPGA ↔ STM32 interface | Document only the SPI register map, omit timing diagrams | Include setup/hold timing, GPIO trigger timing, and the GPIO-to-FPGA sync that currently runs in the main control loop (fragile per CONCERNS.md) |
| STM32 ↔ Python GUI via FT601 USB | Document the API as if the packet format is stable | Document the actual packet format including the hardcoded 64-byte stub in `get_packet_length()` and the buffer overflow condition in `USBHandler.cpp` as known limitations |
| Python GUI ↔ display/visualization | Document DBSCAN and Kalman as if they are independent modules | Document the actual thread architecture including the race condition in the target list and the fixed 100-target ceiling |
| MATLAB processing ↔ FPGA pipeline | Document MATLAB scripts as standalone | Explicitly tie each MATLAB processing step to the corresponding FPGA pipeline stage (DDC → CIC → matched filter → FFT → CFAR) so the docs are a unified signal-flow reference |
| IMU/GPS ↔ coordinate transforms | Document the transform math without the calibration context | The 3×3 calibration matrix and magnetic declination value (-0.61 rad) are hardcoded with no derivation; document both the math and the per-unit calibration dependency |

---

## Performance Traps

Patterns that appear correct in documentation but mask real-world performance constraints.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Documenting FFT resolution without windowing | Stated range resolution looks better than reality | Always state window function used (Hann, Blackman, etc.) and include the scalloping loss and resolution degradation factor | Any time someone computes expected resolution from the docs and then measures it |
| Quoting ADC sample rate (370 Hz) without aliasing analysis | Documented Nyquist bandwidth is wrong | Derive the effective IF bandwidth from the chirp parameters, not just the ADC rate, and verify anti-aliasing filter cutoff | When a reader tries to set chirp parameters for a new range |
| Stating CFAR probability of false alarm without guard cell analysis | PFA appears constant; in practice it varies with clutter density | Document the guard cell + reference window configuration and derive PFA analytically, noting that CA-CFAR PFA degrades in multi-target environments | In clutter-dense environments or when targets are closely spaced |
| Documenting Python GUI throughput at low data rates | GUI appears responsive in testing; locks up in field | Document the O(n) buffer-shift bottleneck and the single-threaded architecture; include measured CPU load at max data rate | At high target counts or sustained 4096+ byte/read data rates |

---

## Documentation-Specific Mistakes

Domain-specific issues in writing engineering documentation for multi-layer radar systems.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Deriving the radar range equation but not connecting it to actual system parameters | Range equation is decorative; engineers cannot compute expected detection range | Plug in actual AERIS-10 values (TX power, antenna gain, ADC noise floor, CFAR threshold) to produce a concrete maximum range estimate |
| Writing FPGA documentation from the Vivado project structure (by module) instead of signal flow (by processing stage) | Readers understand individual modules but not the pipeline | Structure FPGA docs by pipeline stage: DDC → CIC decimation → matched filter → 1024-pt FFT → CFAR, then describe each stage's module |
| Omitting clock domain crossing documentation in FPGA docs | Silent data corruption risks appear undocumented | Document every clock domain (ADC clock, FPGA processing clock, USB clock) and each crossing point and synchronization method |
| Writing improvement research that conflates algorithm and implementation complexity | "Easy to implement" algorithms require FPGA rewrites | For every recommendation, separately rate: algorithmic complexity (math) vs. implementation complexity (FPGA/firmware changes required) |
| Documenting hardware by BOM entry rather than by functional block | Readers cannot understand system behaviour from a parts list | Organize hardware documentation around functional blocks (RF front-end, LO chain, ADC path, power management) with BOM references as secondary annotation |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces in radar system documentation.

- [ ] **Physics derivation:** Signal model appears complete — verify it includes the moving-target Doppler term, not just the stationary approximation
- [ ] **Beamforming documentation:** Phase shift calculation appears complete — verify it derives the expected beam width, sidelobe level, and grating lobe condition for the 16-element array at 10 GHz
- [ ] **CFAR documentation:** CFAR stage appears documented — verify it states the clutter distribution assumption, guard cell count, reference window size, and design PFA
- [ ] **FPGA pipeline documentation:** Each stage appears described — verify the full data flow including bit width, sample rate, and latency (clock cycles) at each stage boundary
- [ ] **Software documentation:** GUI appears documented — verify it specifies which version (V6) and explicitly excludes V1–V5
- [ ] **Magic numbers documented:** Constants in `main.cpp` appear explained — verify every constant is traced to either a hardware spec, a derivation, or a calibration measurement (especially the 31-element phase differences array, PRI1 = 167 µs, Guard = 175.4 µs)
- [ ] **Improvement research:** Algorithms appear recommended — verify each recommendation includes an AERIS-10 hardware feasibility assessment (Artix-7 resources, USB bandwidth, pipeline compatibility)
- [ ] **Cross-references verified:** Section references appear correct — verify that notation is consistent across physics, hardware, and software docs (same symbol for carrier frequency, bandwidth, chirp slope, etc.)

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Inconsistent notation discovered mid-project | HIGH | Halt new writing; create master symbol table from existing docs; do a full find-and-replace pass across all documents before resuming |
| Physics derivation found to have a sign error or missing term | MEDIUM | Correct in physics doc first; then audit all downstream docs (CFAR doc, MATLAB doc, improvement research) that cite the affected equation |
| Software docs written against wrong GUI version | MEDIUM | Identify which version was documented; diff V5 vs V6; annotate sections that changed with "as of V6" and flag sections that describe behavior only present in V5 |
| Improvement research recommendations found to be FPGA-infeasible | LOW | Add an explicit "Implementation Feasibility" subsection to each recommendation rather than removing it; infeasible recommendations are still valuable as "requires hardware upgrade" category |
| FPGA pipeline docs written by module (not by signal flow) | HIGH | Rewrite the FPGA section with a signal-flow outline; existing module descriptions can be reorganized as subsections rather than discarded |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Range-Doppler coupling undocumented | Physics documentation phase | Review derivation includes the Doppler term and the decoupling condition |
| Inconsistent notation | Before any writing begins (notation table as first deliverable) | Cross-check: same symbol for the same quantity in all docs written so far |
| CFAR clutter model assumption missing | FPGA/signal-processing documentation phase | CFAR section states clutter distribution, guard cells, reference window, and design PFA |
| Beamforming skips array factor | Physics documentation phase | Derivation includes steering vector, grating lobe condition, and 6-bit phase quantization error |
| Software research incompatible with hardware | Software improvement research phase | Every recommendation has a hardware feasibility tag relative to Artix-7 + FT601 constraints |
| Hardware research missing RF link budget | Hardware documentation phase (before hardware research) | Link budget table in hardware docs; each hardware recommendation references it |
| Multi-version code confusion | Software documentation phase setup | Canonical version declared in documentation scope; V1–V5 explicitly excluded |
| Magic numbers untraced | Software documentation phase | Every constant in `main.cpp` has a documentation anchor (equation number, spec sheet reference, or calibration procedure) |
| FPGA docs written by module not signal flow | FPGA documentation phase | Table of contents follows DDC → CIC → matched filter → FFT → CFAR signal flow |

---

## Sources

- [FMCW Radar Part 1 - Ranging (WirelessPi)](https://wirelesspi.com/fmcw-radar-part-1-ranging/) — range-Doppler coupling discussion
- [FMCW Radar Part 2 - Velocity, Angle and Radar Data Cube (WirelessPi)](https://wirelesspi.com/fmcw-radar-part-2-velocity-angle-and-radar-data-cube/) — Doppler decoupling
- [Decoupling the Doppler Ambiguity Interval From Maximum Range in FMCW Radars (IEEE)](https://ieeexplore.ieee.org/document/8988231/) — coupling analysis
- [Infineon FMCW Radar Digital Signal Processing Handout](https://www.infineon.com/dgdl/Infineon-FMCW_RADAR_Digital_Signal_Processing_Handout-Training-v01_00-EN.pdf?fileId=8ac78c8c8929aa4d018a178075b06be9) — DSP pipeline patterns
- [NATO RTO: Fundamentals of Signal Processing for Phased Array Radar](https://publications.sto.nato.int/publications/STO%20Educational%20Notes/RTO-EN-SET-086bis/EN-SET-086bis-01.pdf) — notation, beamforming pitfalls
- [Analog Devices Phased Array Antenna Patterns Part 1](https://www.analog.com/en/resources/analog-dialogue/articles/phased-array-antenna-patterns-part1.html) — array factor, element spacing
- [Analog Devices ADAR1000 Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/adar1000.pdf) — 6-bit phase resolution (2.8°), calibration procedure
- [CFAR Performance Analysis (2024, Taylor & Francis)](https://www.tandfonline.com/doi/full/10.1080/01431161.2024.2408494) — clutter distribution assumptions
- [An improved CFAR algorithm for multiple environmental conditions (Springer, 2024)](https://link.springer.com/article/10.1007/s11760-024-03001-x) — CFAR variant comparison
- [Overview of Radar Clutter — William Melvin, ISART 2024](https://its.ntia.gov/media/zj0fjkfi/isart2024_melvin.pdf) — clutter modeling state of the art
- [PySDR: Beamforming & DOA](https://pysdr.org/content/doa.html) — steering vector notation
- PLFM_RADAR CONCERNS.md — known bugs, tech debt, fragile areas (first-party source, HIGH confidence)
- PLFM_RADAR PROJECT.md — system architecture and constraints (first-party source, HIGH confidence)

---

*Pitfalls research for: FMCW radar system documentation and improvement research (AERIS-10 PLFM Radar)*
*Researched: 2026-03-13*
