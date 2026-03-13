---
phase: 01-notation-parameter-standardization
plan: 02
subsystem: documentation
tags: [radar-parameters, aeris-10, notation, parameter-table, nexus, extended]

# Dependency graph
requires:
  - phase: 01-notation-parameter-standardization
    provides: "Research audit of all codebase parameters and inconsistencies"
provides:
  - "Master system parameter table with canonical values for both AERIS-10 variants"
  - "Inconsistency resolutions for center frequency, PRF, ADC bits, beam steering"
  - "Firmware/FPGA/GUI variable-to-symbol mapping"
  - "TBD tracking with downstream phase dependencies"
affects: [02-physics-derivations, 03-hardware-documentation, 04-software-documentation]

# Tech tracking
tech-stack:
  added: []
  patterns: [variant-column-parameter-table, inconsistency-resolution-section, tbd-tracking-with-phase-deps]

key-files:
  created:
    - 00_notation/parameter_table.md
  modified: []

key-decisions:
  - "Center frequency canonical at 10.5 GHz based on firmware wavelength constant; GUI default of 10.0 GHz flagged for correction"
  - "ADC canonical at 8-bit (AD9484) per datasheet; STACK.md 14-bit claim identified as incorrect"
  - "Firmware PRI1 is chirp-level repetition interval; GUI prf1 is display update rate -- distinct timing levels"
  - "Phase shift range -160 to +160 deg maps to ~33 deg steering, not 45 deg claimed in README"

patterns-established:
  - "Single source of truth: all parameter values live in parameter_table.md only"
  - "Variant columns: every parameter has explicit Nexus and Extended values"
  - "Variable traceability: firmware, FPGA, and GUI variable names mapped per parameter"

requirements-completed: [NOTN-02]

# Metrics
duration: 2min
completed: 2026-03-13
---

# Phase 1 Plan 2: Master System Parameter Table Summary

**Canonical parameter table with 40+ parameters for both AERIS-10 Nexus and Extended variants, resolving 4 codebase inconsistencies and mapping firmware/FPGA/GUI variables to standard symbols**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-13T22:15:20Z
- **Completed:** 2026-03-13T22:17:23Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Created master parameter table covering waveform/timing, antenna/beamforming, RF front-end, FPGA signal processing, frequency synthesis, clock domains, and system-level parameters
- Resolved all 4 codebase inconsistencies identified in research with documented rationale
- Mapped every parameter to its firmware variable, FPGA parameter, and/or GUI variable for full traceability
- Established TBD tracking section with explicit downstream phase dependencies

## Task Commits

Each task was committed atomically:

1. **Task 1: Create master system parameter table** - `93bc2a4` (feat)

## Files Created/Modified
- `00_notation/parameter_table.md` - Master system parameter table with canonical values for both AERIS-10 variants, inconsistency resolutions, variable mappings, and TBD tracking

## Decisions Made
- Center frequency set to 10.5 GHz as canonical (firmware wavelength constant is most authoritative; GUI default of 10.0 GHz flagged for codebase correction)
- ADC resolution confirmed as 8-bit (AD9484 per datasheet); STACK.md "14-bit" claim marked as incorrect
- Firmware PRI and GUI PRF documented as distinct timing levels (chirp interval vs. display rate)
- Beam steering phase shift range of +/-160 deg documented separately from steering angle (~+/-33 deg derived)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Parameter table ready for use by all downstream phases
- TBD values (chirp bandwidth, noise figures, antenna gains) flagged as required before Phase 2 physics derivations
- Symbol table (Plan 01-01) and conventions (Plan 01-03) still needed to complete Phase 1

---
*Phase: 01-notation-parameter-standardization*
*Completed: 2026-03-13*
