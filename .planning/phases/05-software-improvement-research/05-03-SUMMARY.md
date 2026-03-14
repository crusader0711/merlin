---
phase: 05-software-improvement-research
plan: 03
subsystem: research
tags: [fpga, optimization, hls, fft, ml, cnn, autoencoder, int8, artix-7]

# Dependency graph
requires:
  - phase: 03-hardware-documentation
    provides: FPGA resource capacity and module inventory (XC7A100T)
  - phase: 04-software-documentation
    provides: FPGA pipeline architecture and threshold detection baseline (SW-7)
provides:
  - FPGA pipeline optimization research survey (HLS, loop unrolling, multi-bank memory, parallelism)
  - ML-based detection alternatives survey (autoencoder, CNN, hybrid CFAR+ML)
affects: [06-hardware-improvement-research]

# Tech tracking
tech-stack:
  added: []
  patterns: [artix-7-feasibility-table, resource-margin-analysis, five-section-research-structure]

key-files:
  created:
    - 04_research/04_fpga_optimization.md
    - 04_research/05_ml_detection.md
  modified: []

key-decisions:
  - "Dual-port BRAM highest priority optimization (zero additional resources, immediate throughput gain)"
  - "Multi-bank BRAM interleaving infeasible for both FFT instances (~105% BRAM utilization)"
  - "Pipeline parallelism (2x/4x) BRAM-constrained on XC7A100T"
  - "Hybrid CFAR+ML recommended over on-FPGA ML (avoids resource constraint via host PC)"
  - "Tiny autoencoder MARGINAL on Artix-7; CNN detector MARGINAL for <10K params, INFEASIBLE for larger"
  - "8-bit ADC dynamic range flagged as fundamental ML input limitation"

patterns-established:
  - "Resource margin analysis: every optimization proposal includes delta table against current utilization"
  - "BRAM constraint gating: any proposal >20 additional BRAMs flagged as BRAM-constrained"

requirements-completed: [SWRES-04, SWRES-05]

# Metrics
duration: 6min
completed: 2026-03-14
---

# Phase 5 Plan 3: FPGA Optimization and ML Detection Research Summary

**FPGA pipeline optimization survey covering HLS/radix-4 FFT/dual-port BRAM with resource margin analysis, plus ML detection alternatives with INT8 quantization feasibility on Artix-7 XC7A100T**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-14T00:39:09Z
- **Completed:** 2026-03-14T00:45:08Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- FPGA optimization research survey with 5 optimization techniques analyzed against XC7A100T resource constraints, identifying dual-port BRAM and radix-4 FFT as feasible, multi-bank interleaving and pipeline parallelism as infeasible/marginal
- ML detection alternatives survey with autoencoder, CNN, and hybrid CFAR+ML approaches, each with INT8 quantization analysis and Artix-7 feasibility verdicts
- Both documents cross-reference Phase 1-4 baseline documentation with specific equation citations (SW-7, DET-17 through DET-24, HW-FPGA-1 through HW-FPGA-6)

## Task Commits

Each task was committed atomically:

1. **Task 1: Write FPGA pipeline optimization research survey** - `a0fa0fb` (feat)
2. **Task 2: Write ML-based detection research survey** - `0efb5bf` (feat)

## Files Created/Modified
- `04_research/04_fpga_optimization.md` - FPGA pipeline optimization research (HLS, radix-4 FFT, dual-port BRAM, parallelism)
- `04_research/05_ml_detection.md` - ML-based detection alternatives (autoencoder, CNN, hybrid CFAR+ML)

## Decisions Made
- Dual-port BRAM identified as Priority 1 optimization: no additional resources, up to 1.5x Doppler throughput
- Radix-4 FFT identified as Priority 2: trades ~32 additional DSPs for 2x FFT clock cycle reduction
- Multi-bank BRAM interleaving ruled infeasible: would push BRAM to ~105% for both FFT instances
- 2x/4x pipeline parallelism ruled marginal/infeasible: BRAM is the binding constraint
- Hybrid CFAR+ML recommended as Priority 1 ML approach: avoids FPGA resource constraint entirely
- On-FPGA autoencoder classified as MARGINAL: pushes BRAM to ~83%, competes for DSPs
- Training data collection identified as prerequisite for all ML approaches

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- FPGA optimization research (SWRES-04) and ML detection research (SWRES-05) complete
- Both documents ready for cross-referencing by remaining Phase 5 plans (SWRES-06 through SWRES-08)
- Resource margin analysis provides quantitative basis for evaluating any future FPGA algorithm proposals

## Self-Check: PASSED

All files exist, all commits verified.

---
*Phase: 05-software-improvement-research*
*Completed: 2026-03-14*
