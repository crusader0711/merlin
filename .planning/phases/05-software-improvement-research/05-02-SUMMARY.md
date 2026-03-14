---
phase: 05-software-improvement-research
plan: 02
subsystem: research
tags: [range-extension, pulse-compression, NLFM, coherent-integration, non-coherent-integration, range-migration, windowed-matched-filter, DAC-feasibility]

# Dependency graph
requires:
  - phase: 04-software-documentation
    provides: "FPGA pipeline documentation (matched filter stages, Doppler processor), noise figure chain, LFM waveform model"
provides:
  - "Range extension survey with coherent/non-coherent integration and range migration analysis"
  - "Pulse compression improvements survey with NLFM DAC feasibility and windowed matched filter options"
affects: [06-hardware-improvement-research]

# Tech tracking
tech-stack:
  added: []
  patterns: [five-section-research-structure, artix7-feasibility-tables, pitfall-6-range-migration-compliance]

key-files:
  created:
    - 04_research/03_range_extension.md
    - 04_research/06_pulse_compression.md
  modified: []

key-decisions:
  - "Windowed matched filter recommended as Priority 1 for pulse compression (lowest risk, 0.76 dB loss for 21.7 dB sidelobe improvement)"
  - "M=64 CPI extension recommended as Priority 1 for range extension (3 dB SNR, 1.19x range, 4-6 BRAMs)"
  - "NLFM achievable PSL limited to -35 to -40 dB by 8-bit DAC quantization (vs theoretical -45 to -50 dB)"
  - "Keystone range migration compensation infeasible on current BRAM budget (15-25 additional BRAMs needed)"
  - "Segmented integration proposed as BRAM-efficient alternative to Keystone for range migration"

patterns-established:
  - "Range migration analysis mandatory for all CPI extension proposals (Pitfall 6 compliance)"
  - "DAC precision constraint analysis for all waveform modification proposals"

requirements-completed: [SWRES-03, SWRES-06]

# Metrics
duration: 5min
completed: 2026-03-14
---

# Phase 5 Plan 02: Range Extension and Pulse Compression Research Summary

**Coherent/non-coherent integration survey with range migration analysis, and NLFM/windowed matched filter comparison with 8-bit DAC feasibility assessment**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-14T00:39:11Z
- **Completed:** 2026-03-14T00:44:22Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- Range extension survey covering M=64/128/256 CPI with SNR derivations and range extension factors, non-coherent post-Doppler integration, and Keystone range migration compensation
- Pulse compression survey covering NLFM (GA, spline, piecewise-linear), windowed matched filter (Taylor, Hamming, Chebyshev), and stretch processing optimization
- DAC feasibility analysis for NLFM showing 8-bit quantization limits practical PSL to -35 to -40 dB
- Artix-7 feasibility tables for every proposed algorithm, identifying BRAM as the binding constraint for range migration and zero-padded FFT proposals

## Task Commits

Each task was committed atomically:

1. **Task 1: Write range extension research survey** - `9d7240a` (feat)
2. **Task 2: Write pulse compression improvements research survey** - `a8daa36` (feat)

## Files Created/Modified
- `04_research/03_range_extension.md` -- Range extension via SNR optimization (SWRES-03): coherent/non-coherent integration, range migration analysis, Artix-7 feasibility
- `04_research/06_pulse_compression.md` -- Pulse compression improvements (SWRES-06): NLFM waveform optimization, windowed matched filter, stretch processing, DAC feasibility

## Decisions Made
- Windowed matched filter (Taylor, nbar=5, SLL=-35 dB) as Priority 1 for sidelobe reduction: only 0.76 dB processing loss for 21.7 dB sidelobe improvement, minimal FPGA resources
- M=64 CPI extension as Priority 1 for range extension: 3 dB SNR improvement, 1.19x range factor, 4-6 additional BRAMs within headroom
- NLFM practical PSL limited to -35 to -40 dB by 8-bit DAC quantization (theoretical -45 to -50 dB unachievable without DAC upgrade)
- Keystone transform infeasible on current BRAM budget (15-25 additional BRAMs); segmented integration proposed as alternative
- Non-coherent post-Doppler integration recommended as low-cost complement to coherent extension

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness
- Both research documents complete with all 5 mandatory sections
- Range extension document properly addresses Pitfall 6 (range migration analysis)
- Pulse compression document properly addresses Open Question 4 (NLFM DAC feasibility)
- BRAM-constrained proposals flagged appropriately in both documents
- Ready for 05-03-PLAN.md (FPGA optimization and ML detection research)

---
*Phase: 05-software-improvement-research*
*Completed: 2026-03-14*
