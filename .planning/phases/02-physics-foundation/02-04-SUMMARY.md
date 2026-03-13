---
phase: 02-physics-foundation
plan: 04
subsystem: physics
tags: [noise-figure, friis, adc, cic, quantization, thermal-noise]

# Dependency graph
requires:
  - phase: 01-notation-parameter-standardization
    provides: Symbol table, parameter table, equation conventions
provides:
  - Cascaded noise figure chain analysis from antenna through digital output (NF-1 to NF-18)
  - ADC quantization noise model for 8-bit AD9484
  - CIC filter noise growth and truncation analysis
  - System noise budget table with substitution procedure for TBD parameters
affects: [03-hardware-documentation, 06-hardware-improvement-research]

# Tech tracking
tech-stack:
  added: []
  patterns: [symbolic-derivation-with-pending-numerical-evaluation, dB-linear-conversion-reminder-box]

key-files:
  created: [01_physics/05_noise_analysis.md]
  modified: []

key-decisions:
  - "18 tagged equations (NF-1 through NF-18) covering thermal noise through digital processing"
  - "ADC noise figure modeled as signal-level-dependent rather than fixed, reflecting 8-bit constraint"
  - "CIC noise analysis includes bit growth formula, passband droop, and truncation noise -- not just processing gain"
  - "Representative placeholder values clearly labeled for numerical example (F_LNA=3dB, G_LNA=20dB)"

patterns-established:
  - "Conversion reminder box pattern: table showing dB vs linear with bold warning about mixing units"
  - "Pending numerical evaluation pattern: explicit step-by-step substitution procedure with placeholder example"

requirements-completed: [PHYS-06]

# Metrics
duration: 3min
completed: 2026-03-13
---

# Phase 2 Plan 4: Noise Figure Chain Analysis Summary

**Cascaded noise figure from Friis formula through analog chain (LNA, mixer, IF amp), 8-bit AD9484 quantization noise, and 5-stage CIC filter noise growth with complete system budget**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-13T22:46:13Z
- **Completed:** 2026-03-13T22:49:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Complete noise analysis document with 18 tagged equations (NF-1 through NF-18) tracing noise from antenna thermal noise through digital output
- Friis cascaded noise figure with explicit dB-to-linear conversion reminder and derivation from two-stage induction
- 8-bit AD9484 quantization noise analysis: SQNR of 49.9 dB, effective noise figure as function of analog chain gain, ENOB relationship
- CIC filter noise analysis: bit growth formula (8-bit input to 18-bit output), passband droop via sinc response, truncation noise model
- System noise budget table with symbolic cumulative noise figure at each stage
- Numerical evaluation section with representative placeholder values and step-by-step substitution procedure

## Task Commits

Each task was committed atomically:

1. **Task 1: Write noise analysis document** - `ae97e95` (feat)

## Files Created/Modified
- `01_physics/05_noise_analysis.md` - Cascaded noise figure chain analysis from antenna to digital output

## Decisions Made
- Modeled ADC effective noise figure as signal-level-dependent (Eq. NF-12) rather than a fixed value, because for 8-bit ADC the quantization noise contribution depends on analog chain gain
- Included ENOB discussion (Eq. NF-13) to bridge theoretical 49.9 dB SQNR to practical performance
- Extended noise chain past ADC to include CIC filter (addressing Pitfall 4 from research), with both beneficial (processing gain) and detrimental (truncation noise, passband droop) contributions
- Used representative placeholder values (F_LNA=3dB, G_LNA=20dB, etc.) clearly labeled as unconfirmed, per research recommendation

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Noise analysis document complete and ready for cross-referencing by hardware documentation (Phase 3)
- TBD parameters (F_LNA, G_LNA, F_mix, G_mix) must be resolved from component datasheets before numerical evaluation section can be finalized
- Document references 01_fmcw_theory.md which is planned in 02-01-PLAN.md; links will resolve when that document is created

---
*Phase: 02-physics-foundation*
*Completed: 2026-03-13*
