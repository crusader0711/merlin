---
phase: 02-physics-foundation
plan: 01
subsystem: physics
tags: [fmcw, radar-equation, beat-frequency, doppler, range-doppler-coupling, lfm]

# Dependency graph
requires:
  - phase: 01-notation-parameter-standardization
    provides: symbol table, parameter table, equation conventions
provides:
  - "FMCW theory document with 30 tagged equations (FMCW-1 through FMCW-30)"
  - "Updated symbol table with 15 Phase 2 symbols across 4 sections"
  - "Root dependency for all other Phase 2 physics documents"
affects: [02-02-PLAN, 02-03-PLAN, 02-04-PLAN, hardware-documentation, software-documentation]

# Tech tracking
tech-stack:
  added: []
  patterns: [first-principles-derivation-flow, symbolic-only-derivations, variant-callout-blocks]

key-files:
  created: [01_physics/01_fmcw_theory.md]
  modified: [00_notation/symbol_table.md]

key-decisions:
  - "Derived full beat frequency with Doppler term first (FMCW-16), then introduced stationary-target approximation as explicitly labeled special case"
  - "Used 30 tagged equations (FMCW-1 through FMCW-30) exceeding the planned ~20, to avoid skipping intermediate algebraic steps"
  - "Range-Doppler coupling analyzed symbolically with chirp duration ratio T_c1/T_c2 = 60, deferring numerical evaluation until bandwidth B is resolved"

patterns-established:
  - "First-principles derivation flow: fundamental principle -> step-by-step algebra -> final result -> variant callout"
  - "Symbol-first-use linking: link to symbol_table.md section on first use of each symbol"
  - "TBD parameter handling: keep derivations symbolic, note TBD status in callout blocks referencing parameter_table.md"

requirements-completed: [PHYS-01, PHYS-05]

# Metrics
duration: 3min
completed: 2026-03-13
---

# Phase 2 Plan 01: FMCW Theory Summary

**First-principles FMCW radar theory with full beat frequency Doppler coupling, 30 tagged equations from EM propagation through range-Doppler analysis, plus 15 new Phase 2 symbols**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-13T22:46:09Z
- **Completed:** 2026-03-13T22:49:32Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Added 15 Phase 2 symbols to symbol table (8 antenna/beamforming, 5 detection/signal, 1 waveform/timing, 1 signal processing)
- Wrote comprehensive FMCW theory document covering EM propagation, radar range equation, FMCW modulation, beat frequency with full Doppler term, range/velocity measurement, max unambiguous range/velocity, and range-Doppler coupling
- All 30 equations are purely symbolic with no inline numerical values, following conventions.md exactly

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Phase 2 symbols to symbol table** - `b89aa54` (feat)
2. **Task 2: Write FMCW theory document** - `218a25b` (feat)

## Files Created/Modified
- `00_notation/symbol_table.md` - Added 15 new symbols: k, psi, theta_0, theta_3dB, w_n, a_n, delta_phi_n, delta_a_n, alpha, N_ref, N_guard, T_e, B_n, tau, chi
- `01_physics/01_fmcw_theory.md` - Complete FMCW theory from first principles (9 sections, 30 tagged equations, ~430 lines)

## Decisions Made
- Derived full beat frequency with Doppler term first (Eq. FMCW-16), then introduced stationary-target approximation as an explicitly labeled special case -- following research anti-pattern guidance
- Used 30 tagged equations exceeding the planned ~20 to ensure no intermediate algebraic steps are skipped per research anti-pattern guidance
- Range-Doppler coupling analyzed symbolically with ratio T_c1/T_c2 = 60; deferred numerical evaluation pending bandwidth B resolution in parameter table
- w_n (element weight) added with explicit note linking it to w[n] (window function), resolving the disambiguation question from research

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- FMCW theory document is the root dependency for all other Phase 2 physics documents
- 02-02-PLAN (LFM waveform + detection theory) can now reference beat frequency (FMCW-16), range equation (FMCW-18), radar equation SNR (FMCW-11)
- 02-03-PLAN (beamforming + calibration) can reference wavelength and frequency definitions
- 02-04-PLAN (noise analysis) can reference radar equation SNR form
- Chirp bandwidth B remains TBD -- downstream documents must continue using symbolic derivations

---
*Phase: 02-physics-foundation*
*Completed: 2026-03-13*
