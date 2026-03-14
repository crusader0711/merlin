---
phase: 04-software-documentation
plan: 01
subsystem: fpga-signal-processing
tags: [fpga, verilog, ddc, nco, cic, matched-filter, doppler, fft, overlap-save, usb]

# Dependency graph
requires:
  - phase: 03-hardware-documentation
    provides: FPGA board clock domains, timing budget, module inventory
  - phase: 02-physics-foundation
    provides: FMCW theory equations (FMCW-1 through FMCW-30), LFM pulse compression, CFAR detection theory
  - phase: 01-notation-parameter-standardization
    provides: Symbol table, parameter table, equation conventions
provides:
  - FPGA signal processing pipeline documentation (03_software/01_fpga_pipeline.md)
  - Software signal processing symbols in symbol table (Section 6)
  - 7 SW-tagged equations deriving all FPGA magic numbers
affects: [04-02, 04-03, 05-01, 05-02, 05-03]

# Tech tracking
tech-stack:
  added: []
  patterns: [signal-flow documentation, magic number derivation with numerical verification]

key-files:
  created:
    - 03_software/01_fpga_pipeline.md
  modified:
    - 00_notation/symbol_table.md

key-decisions:
  - "Threshold detection documented honestly as placeholder (|I|+|Q| > 10000), not true CFAR, despite CFAR variable names in source"
  - "Signal-flow organization (ADC to USB) rather than module-by-module, per research recommendation"
  - "Magic number derivations include numerical verification as exception to anti-pattern 5.1 (needed to show where hex constants originate)"

patterns-established:
  - "SW-N equation tag prefix for all software documentation equations"
  - "Verilog variable names always paired with standard symbols per anti-pattern 5.4"

requirements-completed: [SWDOC-01]

# Metrics
duration: 4min
completed: 2026-03-14
---

# Phase 4 Plan 01: FPGA Signal Processing Pipeline Summary

**10-stage receive pipeline documented from ADC input to USB output with 7 SW-tagged equations deriving NCO phase increment (0x4CCCCCCD), CIC gain shift (10), latency buffer (3187 cycles), and overlap-save segmentation**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-14T00:11:46Z
- **Completed:** 2026-03-14T00:15:46Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Added Section 6 (Software Signal Processing) to symbol table with 7 new symbols for NCO, CIC gain, overlap-save, and range bin decimation
- Created 541-line FPGA pipeline document covering all 10 processing stages by signal flow with clock domains specified per stage
- Derived all magic numbers from physics: NCO phase increment 0x4CCCCCCD from f_IF/f_s ratio, CIC right-shift 10 from 4^5=1024=2^10, latency buffer 3187 from FFT pipeline delay
- Documented threshold detection honestly as placeholder, not true CFAR, with cross-reference to Phase 5 SWRES-01 for future improvement

## Task Commits

Each task was committed atomically:

1. **Task 1: Add software signal processing symbols to symbol table** - `e892b30` (feat)
2. **Task 2: Write FPGA signal processing pipeline document** - `4bdc2dc` (feat)

## Files Created/Modified
- `00_notation/symbol_table.md` - Added Section 6 with 7 new SW-domain symbols; renumbered Sections 7->8, 8->9
- `03_software/01_fpga_pipeline.md` - Complete FPGA pipeline documentation (541 lines, 7 SW-tagged equations)

## Decisions Made
- Threshold detection documented honestly as placeholder fixed threshold (|I|+|Q| > 10000), not true CFAR, despite source code variable names using CFAR terminology
- Signal-flow organization chosen over module-by-module per Phase 4 research recommendation
- Magic number derivations include numerical verification (exception to anti-pattern 5.1) to show where hex/decimal constants originate

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- 03_software/ directory created and first document established
- SW equation tag prefix (SW-1 through SW-7) in use; subsequent plans continue from SW-8
- Phase 4 plans 04-02 (STM32 firmware) and 04-03 (USB protocol + GUI) can proceed

---
*Phase: 04-software-documentation*
*Completed: 2026-03-14*
