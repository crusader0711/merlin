---
phase: 03-hardware-documentation
plan: 05
subsystem: hardware
tags: [timing-budget, gps, imu, coordinate-transforms, complementary-filter, magnetometer, barometer, fpga-pipeline]

# Dependency graph
requires:
  - phase: 03-hardware-documentation (plans 02, 03, 04)
    provides: FPGA module inventory, clock domains, antenna beamforming positions, frequency synthesis clocks
provides:
  - End-to-end timing budget with chirp sequence, scan timing, and FPGA pipeline latency
  - GPS/IMU coordinate transform documentation for radar-to-world conversion
affects: [04-software-documentation, 05-research]

# Tech tracking
tech-stack:
  added: []
  patterns: [HW-TIM equation prefix for timing, HW-NAV equation prefix for navigation]

key-files:
  created:
    - 02_hardware/07_timing_budget.md
    - 02_hardware/09_gps_imu_transforms.md
  modified: []

key-decisions:
  - "FPGA pipeline latency values are theoretical estimates pending Vivado timing reports"
  - "Complementary filter uses Euler angles (not quaternions) despite q[4] array being initialized"
  - "Magnetometer calibration matrix is identity (uncalibrated default) in current firmware"
  - "Flat-Earth approximation valid for GPS coordinate transform at AERIS-10 detection ranges"

patterns-established:
  - "HW-TIM-N: Timing budget equations (25 equations)"
  - "HW-NAV-N: Navigation/coordinate transform equations (26 equations)"

requirements-completed: [HDWR-07, HDWR-09]

# Metrics
duration: 5min
completed: 2026-03-14
---

# Phase 3 Plan 5: Timing Budget & GPS/IMU Transforms Summary

**End-to-end timing budget tracing chirp sequence through FPGA pipeline (~266 us estimated), plus GPS/IMU coordinate transform chain with complementary filter attitude estimation and radar-to-world rotation matrices**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-13T23:47:46Z
- **Completed:** 2026-03-13T23:52:50Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Complete timing budget: chirp sequence timing with guard time (Pitfall 7), full scan timing (~8.96s/revolution), stage-by-stage FPGA pipeline latency, and end-to-end summary showing CPI dominates at 93.4%
- GPS/IMU coordinate transforms: GY-85 sensor suite, complementary filter with 50/50 weighting, magnetometer calibration, tilt-compensated yaw, barometric altitude, complete rotation matrix chain (Tait-Bryan ZYX), and GPS integration
- 51 total tagged equations (25 HW-TIM + 26 HW-NAV) with complete firmware variable mappings

## Task Commits

Each task was committed atomically:

1. **Task 1: Create end-to-end timing budget document** - `c13cc21` (feat)
2. **Task 2: Document GPS/IMU coordinate transforms** - `9179432` (feat)

## Files Created/Modified
- `02_hardware/07_timing_budget.md` - End-to-end timing budget with chirp sequence, scan timing, FPGA pipeline latency, and system responsiveness analysis
- `02_hardware/09_gps_imu_transforms.md` - GPS/IMU coordinate transform documentation covering sensor suite, attitude estimation, calibration, and radar-to-world transform

## Decisions Made
- FPGA pipeline latency values documented as theoretical estimates (actual values require Vivado timing reports, a known blocker)
- Quaternion array `q[4]` documented as initialized but unused; firmware uses Euler-angle complementary filter instead
- Magnetometer calibration matrix noted as identity default (uncalibrated); proper calibration procedure described
- Flat-Earth approximation used for GPS coordinate conversion, valid at AERIS-10 detection ranges (< 20 km)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 (Hardware Documentation) is now complete with all 5 plans executed
- All 8 hardware subsystem documents are created (01-09, with 07 and 09 completed in this plan)
- Ready to proceed to Phase 4 (Software Documentation)

---
*Phase: 03-hardware-documentation*
*Completed: 2026-03-14*
