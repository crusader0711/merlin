---
phase: 05-software-improvement-research
plan: 01
subsystem: research
tags: [cfar, clutter-rejection, fpga, artix-7, detection, mti, doppler]

# Dependency graph
requires:
  - phase: 04-software-documentation
    provides: "FPGA pipeline documentation (SW-7 threshold baseline), detection theory (DET-17 through DET-24)"
provides:
  - "CFAR variant comparison with Artix-7 resource feasibility (CA, OS, GOCA, SOCA, multi-mode)"
  - "Clutter rejection survey with pipeline integration analysis (MTI, Doppler notch, background subtraction)"
affects: [05-02, 05-03, 06-software-improvement-research]

# Tech tracking
tech-stack:
  added: []
  patterns: [five-section-research-structure, artix7-feasibility-table, current-state-baseline-reference]

key-files:
  created:
    - 04_research/01_cfar_variants.md
    - 04_research/02_clutter_rejection.md
  modified: []

key-decisions:
  - "CA-CFAR ranked Priority 1 for CFAR (lowest resource cost, well-published FPGA implementations)"
  - "GOCA-CFAR ranked Priority 2 for clutter-edge robustness over OS-CFAR"
  - "2-pulse delay-line canceller ranked Priority 1 for clutter rejection (trivial resource cost, 25-35 dB improvement)"
  - "Clutter measurement campaign identified as prerequisite before any clutter rejection implementation"
  - "Multi-mode CFAR rated MARGINAL (49-66% of available LUT headroom consumed)"
  - "All clutter rejection approaches rated FEASIBLE (<2% of available LUTs each)"

patterns-established:
  - "Five-section research document structure: Current State, Literature Survey, Gap Analysis, Feasibility Assessment, Recommendations"
  - "Current State sections explicitly reference Phase 1-4 baseline with equation numbers"
  - "CFAR-N and CR-N equation tag prefixes for research documents"

requirements-completed: [SWRES-01, SWRES-02]

# Metrics
duration: 6min
completed: 2026-03-14
---

# Phase 5 Plan 01: CFAR Variants and Clutter Rejection Research Summary

**CA/OS/GOCA/SOCA CFAR comparison and MTI/Doppler-notch/background-subtraction clutter rejection survey with Artix-7 XC7A100T feasibility tables for all algorithms**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-14T00:39:03Z
- **Completed:** 2026-03-14T00:45:22Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- CFAR variants document covers CA, OS, GOCA, SOCA, and multi-mode CFAR with detection performance, clutter distribution assumptions, and Artix-7 resource feasibility tables; all single-mode variants rated FEASIBLE, multi-mode rated MARGINAL
- Clutter rejection document covers delay-line cancellation, MTI FIR filter, IIR notch filter, adaptive Doppler notch, and recursive background subtraction with pipeline insertion points between Stages 6-8
- Both documents open with Current State sections referencing the fixed threshold baseline (Eq. SW-7) and absence of clutter rejection, cross-referencing detection theory (DET-17 through DET-24) and pipeline documentation

## Task Commits

Each task was committed atomically:

1. **Task 1: Write CFAR variants research survey** - `ef901ae` (feat)
2. **Task 2: Write clutter rejection research survey** - `01693af` (feat)

## Files Created/Modified
- `04_research/01_cfar_variants.md` - CFAR variant comparison with 5 mandatory sections, 7 feasibility tables, 4 ranked recommendations
- `04_research/02_clutter_rejection.md` - Clutter rejection survey with 5 mandatory sections, 5 feasibility tables, 4 ranked recommendations plus clutter measurement campaign

## Decisions Made
- CA-CFAR recommended as Priority 1 over OS-CFAR because it achieves optimal detection in homogeneous environments at ~3,000-4,000 LUTs vs. ~8,000-12,000 for OS-CFAR
- GOCA-CFAR ranked Priority 2 (over OS-CFAR at Priority 3) because clutter-edge handling is more critical for ground-based X-band operation than multi-target robustness
- 2-pulse delay-line canceller ranked Priority 1 for clutter rejection due to trivial resource cost (~50-100 LUTs) and 25-35 dB improvement factor
- Clutter measurement campaign identified as the essential first investigation step for both CFAR variant selection and clutter rejection parameter tuning

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- 04_research/ directory now contains the two highest-priority research documents (SWRES-01, SWRES-02)
- Plan 05-02 (range extension and pulse compression) can proceed; these documents provide the detection and clutter baseline it references
- BRAM constraint tracking established: CA-CFAR (2-4) + clutter rejection (0-6) = 2-10 additional BRAMs of 34 available

---
*Phase: 05-software-improvement-research*
*Completed: 2026-03-14*
