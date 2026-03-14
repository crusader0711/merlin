---
phase: 06-hardware-improvement-research
plan: 01
subsystem: research
tags: [gan, sige, phase-noise, adf4382a, adtr1107, x-band, doppler, noise-figure]

# Dependency graph
requires:
  - phase: 02-physics-foundation
    provides: "Noise figure chain (Eq. NF-8), radar range equation (Eq. FMCW-6), SQNR (Eq. NF-11)"
  - phase: 03-hardware-documentation
    provides: "ADTR1107 baseline specs, ADF4382A synthesizer specs, AD9523 clock tree"
provides:
  - "Hardware improvement research document scaffold (research/03_hw_improvements.md)"
  - "GaN vs SiGe front-end comparison with quantified range impact (Section 1)"
  - "Frequency synthesizer phase noise analysis with Doppler floor derivation (Section 2)"
  - "HW-IMP equation prefix with 10 tagged equations (HW-IMP-1 through HW-IMP-10)"
affects: [06-02-PLAN, 06-03-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns: [hw-research-section-pattern, friis-substitution-pattern, fom-to-phase-noise-estimation]

key-files:
  created: [research/03_hw_improvements.md]
  modified: []

key-decisions:
  - "HW-IMP equation prefix for hardware improvement research equations (HW-IMP-1 through HW-IMP-10)"
  - "GaN PA advantage is primarily transmit power (1.6-2.4x range), not receive NF; hybrid GaN PA + SiGe/GaAs LNA recommended"
  - "ADF4382A is best-in-class (-239 dBc/Hz FOM); no synthesizer replacement improves phase noise"
  - "Phase noise SPNR (170+ dB) far exceeds ADC quantization floor (~50 dB); ADC is the Doppler detection bottleneck"
  - "FOM-based phase noise estimation used for ADF4382A (actual datasheet extraction flagged as Open Question)"

patterns-established:
  - "Section pattern: Current State / Literature Survey / Gap Analysis / Feasibility / Recommendations for each HWRES topic"
  - "Substitution pattern: substitute candidate values into existing Phase 2 equations rather than re-deriving"
  - "Variant callout blocks wherever Nexus and Extended differ"

requirements-completed: [HWRES-01, HWRES-02]

# Metrics
duration: 5min
completed: 2026-03-14
---

# Phase 6 Plan 01: RF Front-End Research Summary

**GaN vs SiGe front-end comparison showing 1.6-2.4x range improvement from PA power upgrade, and Doppler floor analysis proving ADF4382A phase noise is not the detection bottleneck (ADC quantization floor dominates by 120+ dB)**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-14T00:39:27Z
- **Completed:** 2026-03-14T00:44:24Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Created hardware improvement research document scaffold with introduction, methodology, and cross-reference framework supporting all six HWRES sections
- Completed Section 1 (GaN vs SiGe) with separate PA and LNA path analysis, quantified range improvement tables, and Friis cascade NF impact assessment
- Completed Section 2 (Frequency Synthesizer Phase Noise) with full Doppler floor derivation from system chirp parameters, minimum detectable velocity calculation, and ADF4382A vs LMX2820 comparison
- Established 10 tagged equations (HW-IMP-1 through HW-IMP-10) for hardware improvement analysis

## Task Commits

Each task was committed atomically:

1. **Task 1: Create document scaffold and GaN vs SiGe front-end section** - `7960953` (feat)
2. **Task 2: Complete frequency synthesizer phase noise section** - `dba5637` (feat)

## Files Created/Modified
- `research/03_hw_improvements.md` - Hardware improvement research document with scaffold, introduction, Sections 1-2 complete, and placeholder stubs for Sections 3-6

## Decisions Made
- **HW-IMP equation prefix:** Assigned HW-IMP prefix for all new equations in this research document, consistent with conventions.md Section 1 pattern
- **GaN PA vs LNA separation:** Analyzed PA path (where GaN excels: +8-15 dB power) separately from LNA path (where SiGe retains NF advantage at 2.5 dB), per Pitfall 3 from research
- **Phase noise estimation method:** Used FOM-based estimation ($\mathcal{L}(f_m) \approx \text{FOM} + 20\log_{10}(f_\text{out}/f_\text{PFD}) + 10\log_{10}(f_m)$) since exact datasheet plots were not extractable; flagged as requiring validation
- **Doppler bottleneck identification:** Phase noise SPNR of 170+ dB vs ADC quantization floor of ~50 dB conclusively shows ADC resolution is the limiting factor, not phase noise
- **Extended variant as hybrid reference:** Used the Extended variant's existing QPA2962 + external LNA architecture as feasibility evidence for the hybrid GaN PA + SiGe LNA approach

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Document scaffold ready for Plans 06-02 (Sections 3, 5: antenna topics) and 06-03 (Sections 4, 6: digital back-end topics) to fill remaining stubs
- HW-IMP equation numbering continues from HW-IMP-11 for subsequent sections
- References section organized by topic, ready for additions from Plans 02 and 03
- Key finding propagated: ADC upgrade (HWRES-04 in Plan 06-03) should be prioritized over synthesizer improvements based on the Doppler floor analysis

---
*Phase: 06-hardware-improvement-research*
*Completed: 2026-03-14*
