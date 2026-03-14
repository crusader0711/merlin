---
phase: 04-software-documentation
plan: 02
subsystem: firmware
tags: [stm32, embedded, spi, i2c, gpio, beamforming, radar-loop, power-amplifier]

# Dependency graph
requires:
  - phase: 01-notation-parameter-standardization
    provides: symbol table, parameter table, conventions for equation formatting
  - phase: 02-physics-documentation
    provides: FMCW theory, beamforming theory for cross-references
  - phase: 03-hardware-documentation
    provides: power management, frequency synthesis, antenna beamforming docs for cross-references
provides:
  - STM32 firmware documentation with 17-step init sequence
  - I2C/SPI peripheral address tables
  - Magic number derivations (SW-20 through SW-32)
  - Main radar loop control flow documentation
  - GPIO pin map grouped by subsystem
affects: [04-software-documentation, 05-software-research]

# Tech tracking
tech-stack:
  added: []
  patterns: [firmware-variable-to-symbol pairing per anti-pattern 5.4, chronological init sequence documentation]

key-files:
  created:
    - 03_software/02_stm32_firmware.md
  modified: []

key-decisions:
  - "SW-20 through SW-32 equation tags, starting at SW-20 to leave room for FPGA pipeline equations (SW-1 through SW-19)"
  - "Phase differences array documented as 160/n pattern for positive positions, symmetric negative mirror"
  - "PA Idq tuning loop documented with iterative DAC code adjustment and current sense amplifier parameters"

patterns-established:
  - "Firmware init sequences documented as numbered step tables with GPIO pins, functions, and delays"
  - "Magic numbers always derived from physics or component specs with SW-tagged equations"

requirements-completed: [SWDOC-02]

# Metrics
duration: 4min
completed: 2026-03-14
---

# Phase 4 Plan 2: STM32 Firmware Summary

**628-line firmware doc covering 17-step init sequence, I2C/SPI device tables, 13 SW-tagged magic number derivations, radar loop control flow with dual-chirp sequencing, and complete GPIO pin map**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-14T00:12:01Z
- **Completed:** 2026-03-14T00:16:55Z
- **Tasks:** 1
- **Files created:** 1

## Accomplishments
- Complete 17-step initialization sequence with exact GPIO pins, functions, delays, and cross-references to Phase 3 hardware docs
- I2C device address table (DAC5578 0x48/0x49, ADS7830 0x48/0x4A/0x49, GY-85, BMP180) and SPI device table (ADAR1000 SPI1, AD9523/ADF4382 SPI4) with CS pin names
- 13 SW-tagged equations (SW-20 through SW-32) deriving all magic numbers: PRI, Guard, phase_differences, ADAR1000 phase code, DAC gate voltage, Idq target, stepper steps
- Main radar loop documented with azimuth/elevation/chirp sequencing, FPGA handshake signals, and stepper motor control
- Complete GPIO pin map (57 pins) grouped by subsystem: power control, SPI CS, clock generator, LO, FPGA, sensors, PA DAC, indicators
- Error handling system with 16 error codes, emergency stop, and automatic recovery mechanisms

## Task Commits

Each task was committed atomically:

1. **Task 1: Write STM32 firmware documentation** - `075ea26` (feat)

**Plan metadata:** pending (docs: complete plan)

## Files Created/Modified
- `03_software/02_stm32_firmware.md` - STM32 firmware architecture documentation (628 lines)

## Decisions Made
- SW equation tags start at SW-20 to leave SW-1 through SW-19 for FPGA pipeline equations in Plan 01
- Phase differences array pattern documented as 160/n for indices 0-14, with symmetric negative mirror for indices 16-30
- PA Idq tuning documented with INA241A3 gain (50 V/V) and 5 mohm shunt resistor parameters extracted directly from firmware

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- STM32 firmware documentation complete, ready for Plans 03 (Python GUI) and 04 (USB protocol)
- FPGA pipeline documentation (Plan 01) can reference this document for STM32-FPGA handshake signal definitions

## Self-Check: PASSED

- FOUND: 03_software/02_stm32_firmware.md (628 lines, 13 SW-tagged equations)
- FOUND: commit 075ea26
- FOUND: 04-02-SUMMARY.md

---
*Phase: 04-software-documentation*
*Completed: 2026-03-14*
