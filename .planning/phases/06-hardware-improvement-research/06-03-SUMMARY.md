---
phase: 06-hardware-improvement-research
plan: 03
subsystem: research
tags: [adc, fpga, jesd204b, ad9680, au15p, au25p, xc7a100t, sqnr, digital-backend, x-band]

# Dependency graph
requires:
  - phase: 02-physics-foundation
    provides: "SQNR equation Eq. NF-11, quantization noise Eq. NF-12, Friis cascade Eq. NF-8"
  - phase: 03-hardware-documentation
    provides: "AD9484 8-bit baseline, XC7A100T resource table, clock domain architecture"
  - phase: 06-hardware-improvement-research
    provides: "Document scaffold and Sections 1-3, 5 from Plans 06-01 and 06-02; HW-IMP equation prefix through HW-IMP-14"
provides:
  - "Higher-resolution ADC research section (Section 4 of research/03_hw_improvements.md)"
  - "FPGA upgrade path research section (Section 6 of research/03_hw_improvements.md)"
  - "Cross-topic summary with priority ranking and investigation roadmap (Section 7)"
  - "HW-IMP equations 15-16 for SQNR improvement and analog chain gain requirement"
  - "Complete hardware improvement research document (all 7 sections finalized)"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: [hw-research-section-pattern, paired-upgrade-dependency-analysis, phased-investigation-roadmap]

key-files:
  created: []
  modified: [research/03_hw_improvements.md]

key-decisions:
  - "ADC+FPGA (HWRES-04+06) ranked #1 priority -- 36.1 dB SQNR is the single largest improvement; must be paired due to JESD204B dependency"
  - "AU15P is minimum viable FPGA migration target (77K LUTs, 12 GTH); AU10P rejected (fewer LUTs than XC7A100T)"
  - "AD9680 (14-bit, 500 MSPS, JESD204B) selected as primary ADC upgrade candidate"
  - "PCB migration rated HIGH complexity -- different voltage rails, I/O banks, transceiver power requirements; NOT a drop-in upgrade"
  - "Investigation roadmap phased as: near-term prototyping (XEM8305+AD9680, 32-element array), medium-term custom PCB, next-generation AiP"

patterns-established:
  - "Paired upgrade dependency: HWRES-04 (ADC) cannot proceed without HWRES-06 (FPGA) and vice versa for maximum value"
  - "Cross-topic dependency mapping: text-based dependency graph showing ENABLES/INDEPENDENT/DIMINISHING relationships"
  - "Phased investigation roadmap: Phase A (near-term eval boards), Phase B (custom PCB), Phase C (next-gen)"

requirements-completed: [HWRES-04, HWRES-06]

# Metrics
duration: 5min
completed: 2026-03-14
---

# Phase 6 Plan 03: Digital Back-End Research Summary

**ADC upgrade from 8-bit AD9484 to 14-bit AD9680 quantified as 36.1 dB SQNR improvement (largest single improvement in system), coupled with AU15P FPGA upgrade for JESD204B support, plus cross-topic priority ranking establishing ADC+FPGA as the highest-priority paired investment across all six HWRES topics**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-14T00:53:21Z
- **Completed:** 2026-03-14T00:59:04Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Completed Section 4 (Higher-Resolution ADC Options) with 8-bit baseline confirmation, 36.1 dB SQNR improvement calculation from Eq. NF-11, JESD204B interface dependency on FPGA upgrade explicitly documented (Pitfall 2), and analog chain gain requirement analysis via Eq. NF-12
- Completed Section 6 (FPGA Upgrade Path) with XC7A100T vs AU10P/AU15P/AU25P resource comparison, AU10P flagged as NOT viable (fewer LUTs), AU15P as minimum migration target, PCB migration rated HIGH complexity (Pitfall 5), and FT601 USB 3.0 compatibility confirmed via Opal Kelly XEM8305
- Added Section 7 (Cross-Topic Summary) with dependency map, priority ranking table across all 6 HWRES topics, phased investigation roadmap (near-term/medium-term/next-generation), and consolidated open questions
- Document is now complete with all 7 research sections, introduction, and references -- an engineer can read it end-to-end and prioritize hardware upgrade investments

## Task Commits

Each task was committed atomically:

1. **Task 1: Complete ADC upgrade and FPGA upgrade sections (HWRES-04, HWRES-06)** - `33347f9` (feat)
2. **Task 2: Add cross-topic summary and finalize document** - `6de2a91` (feat)

## Files Created/Modified
- `research/03_hw_improvements.md` - Sections 4, 6, and 7 completed; References section updated with ADC, FPGA, and JESD204B sources

## Decisions Made
- **ADC+FPGA as paired #1 priority:** The 36.1 dB SQNR improvement from an 8-to-14-bit ADC upgrade is the single largest improvement available, but requires FPGA upgrade for JESD204B transceivers. These must be pursued together.
- **AU15P over AU10P:** AU10P has fewer LUTs (44K) than the current XC7A100T (63.4K), making it a regression. AU15P provides 77.8K LUTs (22% more) plus 12 GTH transceivers.
- **AD9680 as primary candidate:** 14-bit, 500 MSPS, JESD204B interface matches the current 400 MSPS operating rate with mature Xilinx IP support.
- **PCB migration is HIGH complexity:** Different BGA package, 0.85V core (vs 1.0V), new GTH power rails (MGTAVCC, MGTAVTT), different I/O banks -- entire board must be redesigned.
- **Phased investigation roadmap:** Phase A uses evaluation boards (XEM8305, AD9680 FMC) for risk reduction before committing to custom PCB in Phase B.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Hardware improvement research document (`research/03_hw_improvements.md`) is complete with all 7 sections
- All 6 HWRES requirements (HWRES-01 through HWRES-06) have been addressed across Plans 06-01, 06-02, and 06-03
- Phase 6 is complete -- no remaining plans
- Cross-topic priority ranking provides actionable guidance for future hardware investment decisions
- Investigation roadmap provides concrete next steps organized by timeline and risk

---
*Phase: 06-hardware-improvement-research*
*Completed: 2026-03-14*
