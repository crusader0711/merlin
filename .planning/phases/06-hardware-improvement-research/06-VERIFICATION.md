---
phase: 06-hardware-improvement-research
verified: 2026-03-14T00:00:00Z
status: passed
score: 4/4 must-haves verified
re_verification: false
human_verification:
  - test: "Read research/03_hw_improvements.md end-to-end as a radar engineer unfamiliar with AERIS-10"
    expected: "Can understand all six upgrade paths, follow quantified improvement claims back to cited equations, and use the priority table to decide which upgrade to pursue first"
    why_human: "Document coherence, readability, and whether the narrative logic holds for a domain expert cannot be verified programmatically"
  - test: "Verify FMCW-6 citation label in Sections 1.3 and 5.2"
    expected: "The cited FMCW-6 equation is P_refl at target; the full range equation is FMCW-11. The derived proportionalities (HW-IMP-1 and HW-IMP-12) are physically correct but the citation label is wrong."
    why_human: "Physics accuracy of the cross-reference label needs human review; it is a labeling issue rather than a broken link, and the actual derived equations are correct"
---

# Phase 6: Hardware Improvement Research Verification Report

**Phase Goal:** Engineers have a grounded survey of hardware upgrade paths with impact traced through the documented noise figure chain and RF link budget
**Verified:** 2026-03-14
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | GaN vs SiGe front-end comparison quantifies output power, noise figure, and die size impact on detection range relative to ADTR1107 baseline | VERIFIED | Section 1 contains PA/LNA comparison tables, HW-IMP-1 range factor calculation (1.6–2.4x), and Friis cascade NF impact table via Eq. NF-8 |
| 2 | Synthesizer phase noise section derives Doppler floor improvement from ADF4382A phase noise profile using system chirp parameters | VERIFIED | Section 2.3 derives $\Delta f_d$ from actual $T_r$ and $M=32$ values, computes SPNR = 170+ dB at 1 kHz offset, and states minimum detectable velocity ≈ 2.67 m/s |
| 3 | AiP miniaturization section addresses LTCC implementations at X-band with compatibility assessment against current ADAR1000+ADTR1107 architecture | VERIFIED | Section 3.2 surveys Cadence/MDPI/IEICE LTCC references with dimensions; Section 3.3 explicitly documents the ADAR1000 SPI DEV_ADDR compatibility constraint |
| 4 | Array expansion section quantifies gain improvement and range multiplier for 32 and 64 elements with SPI bus scaling constraints documented | VERIFIED | Section 5.2 scaling table (16/32/64 elements), HW-IMP-11/12 for array gain and range, 2-bit DEV_ADDR limit documented with max 4 devices per bus |
| 5 | ADC upgrade section correctly bases improvement on 8-bit AD9484 baseline and quantifies 36 dB SQNR improvement for 14-bit upgrade | VERIFIED | Section 4.1 states "8-bit" with two independent sources (02_rf_frontend.md + `ADC_WIDTH=8` in `ddc_400m.v`); HW-IMP-15 gives +36.1 dB for 8-to-14-bit using Eq. NF-11 |
| 6 | ADC section explicitly documents JESD204B interface dependency on FPGA upgrade | VERIFIED | Section 4.4 blockquote: "HWRES-04 (ADC upgrade) is DEPENDENT on HWRES-06 (FPGA upgrade). The ADC cannot be upgraded to a 14-bit JESD204B device without simultaneously upgrading the FPGA." |
| 7 | FPGA upgrade section compares XC7A100T against AU15P and AU25P with resource tables, and documents PCB migration as HIGH complexity | VERIFIED | Section 6.2 resource comparison table; AU10P flagged NOT viable (fewer LUTs); Section 6.4 "PCB Migration Complexity: HIGH (Pitfall 5)" with full voltage-rail breakdown |
| 8 | Cross-topic dependency between HWRES-04 and HWRES-06 is explicitly documented | VERIFIED | Section 7.1 dependency map with "ENABLES" notation and "KEY COUPLING" callout; priority table ranks ADC+FPGA as #1 paired upgrade |
| 9 | Document concludes with cross-topic priority ranking and recommended investigation roadmap | VERIFIED | Section 7.2 priority table (5 entries ranked by impact/complexity/timeline); Section 7.3 three-phase investigation roadmap (near-term/medium-term/next-generation) |
| 10 | Both AERIS-10 variants addressed throughout | VERIFIED | 42 mentions of "Nexus" and "Extended"; 6 variant callout blocks; intro table distinguishes variant specs |
| 11 | Every section traces improvement through documented Phase 2/3 equations | VERIFIED | Friis cascade NF-8 (12+ references), SQNR NF-11 (8+ references), NF-12 (3 references), BF-10/BF-16/BF-3, FMCW-6/FMCW-11, 16 cross-references to 05_fpga_board.md, 9 to 02_rf_frontend.md |

**Score:** 11/11 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `research/03_hw_improvements.md` | Complete 7-section hardware improvement research document | VERIFIED | 1,399 lines; all 7 section headers confirmed (## 1 through ## 7) |
| `research/03_hw_improvements.md` § 1 | GaN vs SiGe front-end section (HWRES-01) | VERIFIED | Full 5-subsection structure; PA and LNA paths analyzed separately; range improvement table |
| `research/03_hw_improvements.md` § 2 | Frequency synthesizer phase noise section (HWRES-02) | VERIFIED | Doppler resolution derived from actual chirp parameters; minimum detectable velocity stated |
| `research/03_hw_improvements.md` § 3 | Antenna-in-Package miniaturization section (HWRES-03) | VERIFIED | LTCC survey with specific dimensions; ADAR1000 SPI compatibility constraint explicitly documented |
| `research/03_hw_improvements.md` § 4 | Higher-resolution ADC section (HWRES-04) | VERIFIED | 8-bit baseline confirmed via two sources; +36.1 dB SQNR calculated; JESD204B dependency blockquoted |
| `research/03_hw_improvements.md` § 5 | Antenna array expansion section (HWRES-05) | VERIFIED | 16/32/64 scaling table; SPI DEV_ADDR constraint documented; grating lobe analysis via Eq. BF-16 |
| `research/03_hw_improvements.md` § 6 | FPGA upgrade path section (HWRES-06) | VERIFIED | Resource comparison table; AU10P rejected; AU15P as minimum viable; PCB migration rated HIGH |
| `research/03_hw_improvements.md` § 7 | Cross-topic summary (dependency map, priority ranking, roadmap) | VERIFIED | Text dependency graph; 5-entry priority table with quantified impact; 3-phase investigation roadmap |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `research/03_hw_improvements.md` | `01_physics/05_noise_analysis.md` | Eq. NF-8 for cascaded NF impact | WIRED | NF-8 cited 12+ times by equation number; formula reproduced in Section 1.1 |
| `research/03_hw_improvements.md` | `01_physics/05_noise_analysis.md` | Eq. NF-11 for SQNR, NF-12 for quantization floor | WIRED | NF-11 cited 8+ times; NF-12 cited 3 times; both applied with substitutions |
| `research/03_hw_improvements.md` | `02_hardware/02_rf_frontend.md` | ADTR1107 baseline specs cross-reference | WIRED | 9 inline cross-references with section anchors; 8-bit ADC confirmed from this doc |
| `research/03_hw_improvements.md` | `02_hardware/03_frequency_synthesis.md` | ADF4382A baseline cross-reference | WIRED | ADF4382A FOM, VCO range, reference freq, fractional-N equation HW-FS-8 all cited |
| `research/03_hw_improvements.md` | `02_hardware/04_antenna_beamforming.md` | ADAR1000 baseline and SPI topology cross-reference | WIRED | SPI topology table reproduced; DEV_ADDR constraint cited to Section 2.2 of this doc |
| `research/03_hw_improvements.md` | `01_physics/03_beamforming_theory.md` | Grating lobe analysis Eq. BF-10 and array gain BF-3 | WIRED | BF-10 cited 3 times; BF-3 used for array gain scaling; BF-16 for grating lobe condition |
| `research/03_hw_improvements.md` | `02_hardware/05_fpga_board.md` | XC7A100T baseline resource utilization | WIRED | 16 cross-references; resource table reproduced in Section 6.1; zero-transceivers statement cited |
| `research/03_hw_improvements.md` | `01_physics/01_fmcw_theory.md` | Range equation Eq. FMCW-6 | PARTIAL | Link exists and HW-IMP-1/HW-IMP-12 derivations are physically correct. Minor labeling issue: FMCW-6 is the reflected power at target ($P_\text{refl}$); the full two-way range equation is FMCW-11. The $R_\text{max} \propto P_t^{1/4}$ proportionality is correct and derivable from FMCW-11. The wrong equation tag is cited but the physics and calculation are correct. |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| HWRES-01 | 06-01-PLAN.md | GaN vs SiGe front-end comparison — output power, NF, die size at X-band, comparison to ADTR1107 | SATISFIED | Section 1: PA and LNA paths analyzed separately; range improvement quantified 1.6–2.4x; NF impact via Eq. NF-8 |
| HWRES-02 | 06-01-PLAN.md | Frequency synthesizer phase noise improvements — ADF4382A vs competitors, Doppler floor improvement | SATISFIED | Section 2: ADF4382A vs LMX2820 comparison; Doppler floor derived from chirp parameters; min velocity 2.67 m/s stated |
| HWRES-03 | 06-02-PLAN.md | Antenna-in-Package (AiP) miniaturization — 3D-stacked T/R modules, LTCC implementations, ADAR1000+ADTR1107 compatibility | SATISFIED | Section 3: LTCC survey with dimensions; ADAR1000 SPI compatibility constraint; variant applicability (Nexus-only) |
| HWRES-04 | 06-03-PLAN.md | Higher-resolution ADC options — 14 to 16-bit upgrade, FPGA interface impact, SNR improvement calculation | SATISFIED | Section 4: 8-bit baseline confirmed; +36.1 dB SQNR for 14-bit; JESD204B dependency explicitly documented as blocker |
| HWRES-05 | 06-02-PLAN.md | Antenna array expansion — 16 to 32/64 elements, ADAR1000 cascading, PCB constraints, grating lobe implications | SATISFIED | Section 5: scaling table; DEV_ADDR SPI constraint; grating lobe analysis; physical aperture constraints per variant |
| HWRES-06 | 06-03-PLAN.md | FPGA upgrade path — Artix UltraScale+ resource comparison, PCB migration complexity, USB 3.0 compatibility | SATISFIED | Section 6: resource comparison; AU10P NOT viable; AU15P minimum target; PCB migration HIGH; FT601 compatibility confirmed |

**All 6 HWRES requirements satisfied.** No orphaned requirements found: REQUIREMENTS.md maps exactly HWRES-01 through HWRES-06 to Phase 6, all covered by the three plans as declared.

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `research/03_hw_improvements.md` line 128, 876 | FMCW-6 cited as "the radar range equation" but FMCW-6 is $P_\text{refl}$ at target; the full range SNR equation is FMCW-11 | Info | The HW-IMP-1 and HW-IMP-12 proportionalities derived from it are physically correct. The cross-reference label is inaccurate but the math is sound. |
| `research/03_hw_improvements.md` line 98 | "PA gain | TBD (ADTR1107 datasheet)" — TBD value in a data table | Info | Flagged as an open question in Section 7.4 item 1; does not affect any quantitative conclusion |

No blockers. No placeholder stubs. No empty implementations. All seven sections are substantive with complete Current State / Literature Survey / Gap Analysis / Feasibility / Recommendations subsections.

---

### Human Verification Required

#### 1. FMCW Equation Label Review

**Test:** Open `01_physics/01_fmcw_theory.md` and note that FMCW-6 is the reflected power density at the target ($P_\text{refl}$), while FMCW-11 is the full two-way received SNR equation from which $R_\text{max} \propto P_t^{1/4}$ is derived. Then review lines 128 and 876 of `research/03_hw_improvements.md` where the document says "radar range equation (Eq. FMCW-6)."
**Expected:** Decide whether to update the citation to FMCW-11, or to note in the physics document that $R_\text{max}$ scaling follows from FMCW-6 through FMCW-11. The derived proportionalities (HW-IMP-1 and HW-IMP-12) are correct in either case.
**Why human:** This is a citation label accuracy judgment that requires physics review, not a broken link or wrong calculation.

#### 2. End-to-End Document Coherence

**Test:** Read `research/03_hw_improvements.md` as a radar engineer unfamiliar with AERIS-10. Verify that the Section 7 priority ranking follows logically from the per-section analyses, and that the phased roadmap (Phase A/B/C) would make sense to a hardware team planning upgrade investments.
**Expected:** Priority ranking and roadmap are internally consistent with the individual section conclusions and variant constraints.
**Why human:** Document narrative coherence and domain logic cannot be verified by grep.

---

### Gaps Summary

No gaps. All must-haves from all three PLANs are verified against the actual document:

- All 7 sections exist and are substantive (not stubs)
- All 6 HWRES requirements (HWRES-01 through HWRES-06) are addressed
- All key cross-references to Phase 2 physics (NF-8, NF-11, NF-12, BF-10, BF-16, FMCW equations) are present and cite by equation number
- All key cross-references to Phase 3 hardware (02_rf_frontend.md, 03_frequency_synthesis.md, 04_antenna_beamforming.md, 05_fpga_board.md) are present with section anchors
- Variant-specific analysis (Nexus vs Extended) appears throughout with callout blocks
- Critical pitfalls documented: 8-bit ADC baseline (Pitfall 1), JESD204B dependency (Pitfall 2), GaN PA vs LNA separation (Pitfall 3), SPI DEV_ADDR constraint (Pitfall 4), PCB migration complexity (Pitfall 5), Doppler floor from chirp parameters (Pitfall 6)
- All 6 task commits documented in summaries exist in git history (7960953, dba5637, c8a35b6, 0be1662, 33347f9, 6de2a91)

The phase goal is achieved: engineers have a grounded survey of hardware upgrade paths with impact traced through the documented noise figure chain and RF link budget.

---

*Verified: 2026-03-14*
*Verifier: Claude (gsd-verifier)*
