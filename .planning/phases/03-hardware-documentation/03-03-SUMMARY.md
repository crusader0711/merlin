---
phase: 03-hardware-documentation
plan: 03
subsystem: hardware
tags: [adar1000, beamforming, fpga, xc7a100t, artix-7, cdc, phased-array, verilog]

# Dependency graph
requires:
  - phase: 03-01
    provides: "System overview with clock domain summary and hardware symbols"
  - phase: 02-03
    provides: "Beamforming theory (array factor, grating lobes, phase quantization)"
provides:
  - "ADAR1000 register map and SPI protocol documentation"
  - "31-position beam steering table with phase_differences array"
  - "XC7A100T clock domain architecture (4 domains)"
  - "CDC synchronizer implementation documentation"
  - "Complete FPGA Verilog module inventory (25 modules)"
affects: [04-software-documentation, 05-sw-research]

# Tech tracking
tech-stack:
  added: []
  patterns: ["HW-ANT-N equation prefix for antenna/beamforming", "HW-FPGA-N equation prefix for FPGA board"]

key-files:
  created:
    - 02_hardware/04_antenna_beamforming.md
    - 02_hardware/05_fpga_board.md
  modified: []

key-decisions:
  - "ADAR1000 beam RAM bypassed in firmware; phase settings written directly via SPI for each position"
  - "FPGA resource utilization documented as theoretical estimates pending Vivado reports"
  - "FT601 100 MHz clock treated as asynchronous to system 100 MHz despite same frequency (separate oscillator)"
  - "Detailed signal processing pipeline deferred to Phase 4 SWDOC-01; FPGA doc covers structural inventory only"

patterns-established:
  - "Register map tables extracted from driver headers with SPI transaction format context"
  - "Firmware variable to standard symbol mapping (per conventions.md anti-pattern 5.4)"

requirements-completed: [HDWR-04, HDWR-05]

# Metrics
duration: 5min
completed: 2026-03-14
---

# Phase 3 Plan 03: Antenna/Beamforming and FPGA Board Summary

**ADAR1000 beamformer register map with 31-position beam steering tables and XC7A100T FPGA platform with 4 clock domains, 3 CDC synchronizer types, and 25-module Verilog inventory**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-13T23:38:14Z
- **Completed:** 2026-03-13T23:43:21Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- ADAR1000 register map extracted from adar1000.h with full SPI protocol documentation, including 3-byte transaction format, broadcast mode, and chip select mapping
- Complete 31-position beam steering table documenting all phase_differences values, per-element phase computation, 7-bit quantization conversion, and pre-computed beam matrix structure (matrix1, matrix2, vector_0)
- FPGA clock domain architecture with 4 domains (400/120/100/100 MHz) traced to AD9523 divider equations and constraint file definitions
- CDC synchronizer documentation covering 3 module types from cdc_modules.v: Gray-coded multi-bit, single-bit, and handshake-based
- Complete 25-module Verilog inventory with clock domains, key parameters, and function descriptions
- 10 HW-ANT equations and 6 HW-FPGA equations following conventions.md

## Task Commits

Each task was committed atomically:

1. **Task 1: Document antenna array and beamforming hardware** - `b30ad33` (feat)
2. **Task 2: Document FPGA board subsystem** - `5fcae00` (feat)

## Files Created/Modified
- `02_hardware/04_antenna_beamforming.md` -- ADAR1000 beamformer register map, beam steering tables, array geometry, ADTR1107 integration
- `02_hardware/05_fpga_board.md` -- XC7A100T resource capacity, clock domains, CDC synchronizers, module inventory, constraint summary

## Decisions Made
- ADAR1000 beam RAM bypass documented as the firmware implementation pattern (direct SPI writes for each beam position rather than using internal beam RAM)
- FPGA resource utilization presented as theoretical per-module estimates with clear caveat that actual numbers require Vivado implementation reports (known blocker)
- FT601 clock documented as asynchronous to system clock despite both being 100 MHz, because they originate from different oscillators (FT601 IC vs AD9523)
- Signal processing pipeline details (DDC algorithms, matched filter design, Doppler processing) explicitly deferred to Phase 4 SWDOC-01; FPGA document covers structural inventory and platform architecture only

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Both antenna/beamforming and FPGA board documents complete, providing the hardware platform context needed for Phase 4 signal processing documentation
- FPGA module inventory serves as the structural reference for Phase 4's detailed pipeline analysis
- Beam steering tables and ADAR1000 register map support Phase 5 (SW/HW research) feasibility assessments
- Known blocker remains: Vivado implementation reports needed for actual FPGA utilization numbers

---
*Phase: 03-hardware-documentation*
*Completed: 2026-03-14*
