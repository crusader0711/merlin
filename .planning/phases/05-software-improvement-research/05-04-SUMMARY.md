---
phase: 05-software-improvement-research
plan: 04
subsystem: research
tags: [kalman, imm, mvdr, lcmv, beamforming, tracking, adaptive, adar1000]

# Dependency graph
requires:
  - phase: 04-software-documentation
    provides: "Python GUI Kalman baseline (SW-3), FPGA pipeline, USB protocol"
  - phase: 03-hardware-documentation
    provides: "ADAR1000 phase control (HW-ANT-1), Artix-7 resource capacity, beamforming hardware"
  - phase: 02-physics-foundation
    provides: "Array factor theory (BF-3 through BF-19), beam steering equations"
provides:
  - "Target tracking improvements survey (IMM-Kalman, VB-IMM, adaptive Kalman, EKF/UKF)"
  - "Adaptive beamforming research survey (MVDR, LCMV, hybrid, robust beamforming)"
  - "ADAR1000 quantization impact analysis on adaptive null depth"
  - "Artix-7 MVDR feasibility verdict (INFEASIBLE on-FPGA, FEASIBLE hybrid)"
affects: [06-hardware-improvement-research]

# Tech tracking
tech-stack:
  added: []
  patterns: [research-survey-5-section, feasibility-table-per-algorithm]

key-files:
  created:
    - 04_research/07_target_tracking.md
    - 04_research/08_adaptive_beamforming.md
  modified: []

key-decisions:
  - "Target tracking scoped to Python host (no FPGA constraint); IMM-Kalman ranked Priority 1"
  - "MVDR/LCMV on Artix-7 INFEASIBLE (needs 2000+ DSPs vs 151 available); hybrid host-computed FEASIBLE"
  - "ADAR1000 quantization limits adaptive null depth to ~-29 dB regardless of algorithm"

patterns-established:
  - "Python-side algorithms need no FPGA feasibility table (explain why instead)"
  - "Hardware quantization constraints documented as hard floors on algorithm performance"

requirements-completed: [SWRES-07, SWRES-08]

# Metrics
duration: 6min
completed: 2026-03-14
---

# Phase 5 Plan 4: Target Tracking & Adaptive Beamforming Summary

**IMM-Kalman tracking survey for Python host and MVDR/LCMV adaptive beamforming research with ADAR1000 quantization and Artix-7 feasibility analysis**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-14T00:39:16Z
- **Completed:** 2026-03-14T00:45:30Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Target tracking survey covering IMM-Kalman, variational Bayesian IMM, adaptive Kalman (IAE), and EKF/UKF -- all correctly scoped to Python host processing with no FPGA resource constraint
- Adaptive beamforming survey covering MVDR, LCMV, hybrid host-computed, and robust beamforming -- with Artix-7 resource tables proving real-time MVDR infeasible (10x-25x DSP gap)
- ADAR1000 phase quantization impact quantified: 7-bit resolution limits adaptive null depth to ~-29 dB, establishing a hardware precision floor for all adaptive beamforming approaches

## Task Commits

Each task was committed atomically:

1. **Task 1: Write target tracking improvements research survey** - `230257a` (feat)
2. **Task 2: Write adaptive beamforming research survey** - `364b3b7` (feat)

## Files Created/Modified
- `04_research/07_target_tracking.md` - IMM-Kalman, VB-IMM, adaptive Kalman, EKF/UKF survey with Python feasibility assessment
- `04_research/08_adaptive_beamforming.md` - MVDR/LCMV/hybrid/robust beamforming survey with Artix-7 resource analysis and ADAR1000 quantization impact

## Decisions Made
- Target tracking correctly scoped to Python host processing -- no FPGA feasibility table needed (explained why: all tracking runs post-detection in Python)
- MVDR/LCMV on Artix-7 rated INFEASIBLE: published implementations require 2,000-4,000 DSP slices vs. 151 remaining on XC7A100T
- Hybrid host-computed MVDR rated FEASIBLE: moves matrix inversion to Python/NumPy, with ~1.2-2.6 ms round-trip latency fitting within per-CPI timing
- ADAR1000 7-bit phase quantization documented as hard precision floor (~-29 dB) that no algorithm can overcome without hardware modification
- Fixed amplitude tapering (Taylor weights) recommended as zero-cost immediate improvement from -13.3 dB to -30 dB sidelobes

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 4 Phase 5 plans (SWRES-01 through SWRES-08) now have research surveys complete
- Phase 6 (Hardware Improvement Research) can proceed -- HWRES-06 (FPGA upgrade path) is cross-referenced by the adaptive beamforming Priority 3 recommendation
- The hybrid host-computed MVDR approach depends on per-element data streaming which would require FPGA pipeline modification (documented as investigation step, not implementation)

## Self-Check: PASSED

- FOUND: 04_research/07_target_tracking.md
- FOUND: 04_research/08_adaptive_beamforming.md
- FOUND: commit 230257a
- FOUND: commit 364b3b7
- All 5 mandatory sections present in both documents
- Target tracking correctly scoped to Python (23 Python references)
- ADAR1000 quantization addressed (24 references)
- MVDR INFEASIBLE verdict present (6 occurrences)

---
*Phase: 05-software-improvement-research*
*Completed: 2026-03-14*
