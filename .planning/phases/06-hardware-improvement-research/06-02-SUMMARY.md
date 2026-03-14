---
phase: 06-hardware-improvement-research
plan: 02
subsystem: research
tags: [aip, ltcc, antenna, array-expansion, adar1000, spi, beamforming, x-band, ula]

# Dependency graph
requires:
  - phase: 02-physics-foundation
    provides: "Beamforming theory Eq. BF-3/BF-10/BF-16, radar range equation Eq. FMCW-6"
  - phase: 03-hardware-documentation
    provides: "ADAR1000 SPI topology, 16-element array geometry, ADTR1107 baseline"
  - phase: 06-hardware-improvement-research
    provides: "Document scaffold and HW-IMP equation prefix from Plan 06-01"
provides:
  - "Antenna-in-Package miniaturization research section (Section 3 of research/03_hw_improvements.md)"
  - "Antenna array expansion research section (Section 5 of research/03_hw_improvements.md)"
  - "HW-IMP equations 11-14 for array gain scaling, range improvement, beamwidth scaling, SPI programming time"
affects: [06-03-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns: [hw-research-section-pattern, array-scaling-analysis, spi-bus-topology-scaling]

key-files:
  created: []
  modified: [research/03_hw_improvements.md]

key-decisions:
  - "AiP miniaturization rated LOW priority -- form factor benefit (~30% area reduction) is modest compared to ADC upgrade (36 dB SQNR) and GaN PA (1.6-2.4x range)"
  - "AiP primarily relevant to Nexus variant; Extended variant waveguide antenna incompatible with AiP technology"
  - "ADAR1000 SPI compatibility identified as critical AiP constraint -- must preserve SPI interface or redesign firmware+FPGA"
  - "32-element array expansion is practical near-term upgrade (MODERATE complexity, +3 dB gain, 1.41x range)"
  - "64-element expansion viable but requires platform redesign (900 mm aperture, quad-SPI bus)"
  - "SPI bus scaling follows ADAR1000 2-bit DEV_ADDR limit: max 4 devices per bus, requiring multi-bus architecture for >16 elements"

patterns-established:
  - "Array scaling analysis: tabulate element count vs ADAR1000 count, SPI buses, gain, beamwidth, aperture, range multiplier"
  - "SPI topology scaling: document bus count, available STM32 SPI peripherals, firmware changes per expansion level"

requirements-completed: [HWRES-03, HWRES-05]

# Metrics
duration: 5min
completed: 2026-03-14
---

# Phase 6 Plan 02: Antenna and Packaging Research Summary

**LTCC-based AiP miniaturization assessed as next-generation option (LOW priority, Nexus-only), and 32-element array expansion identified as practical near-term upgrade path with +3 dB gain and 1.41x range improvement constrained by ADAR1000 2-bit SPI addressing**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-14T00:46:33Z
- **Completed:** 2026-03-14T00:51:15Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Completed Section 3 (Antenna-in-Package Miniaturization) with LTCC X-band survey, ADAR1000 SPI compatibility analysis, and variant-specific feasibility assessment
- Completed Section 5 (Antenna Array Expansion) with full scaling analysis table (16/32/64 elements), SPI bus topology scaling, grating lobe verification, and power budget projections
- Added 4 new HW-IMP equations (HW-IMP-11 through HW-IMP-14) for array gain, range improvement, beamwidth scaling, and SPI programming time
- Updated References section with HWRES-03 and HWRES-05 academic and datasheet sources

## Task Commits

Each task was committed atomically:

1. **Task 1: Complete Antenna-in-Package miniaturization section (HWRES-03)** - `c8a35b6` (feat)
2. **Task 2: Complete antenna array expansion section (HWRES-05)** - `0be1662` (feat)

## Files Created/Modified
- `research/03_hw_improvements.md` - Sections 3 and 5 completed (AiP miniaturization and array expansion), References section updated

## Decisions Made
- **AiP priority ranking:** LOW -- the ~30% footprint reduction and ~0.5 dB interconnect loss improvement are modest compared to the 36 dB SQNR from ADC upgrade or 8-15 dB from GaN PA upgrade
- **AiP variant applicability:** Nexus only -- Extended variant's slotted waveguide antenna is structurally incompatible with AiP technology
- **ADAR1000 SPI as critical constraint:** Any AiP solution must preserve the 3-byte SPI transaction format and 2-bit DEV_ADDR addressing, or the entire firmware driver and FPGA level-shifter require redesign
- **32-element as recommended expansion:** MODERATE complexity with meaningful +3.0 dB gain and 1.41x range; 64-element deferred to future platform redesign
- **Parallel SPI for scan time:** Multi-bus SPI with DMA can maintain current scan cycle time for expanded arrays by programming buses concurrently

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Document scaffold ready for Plan 06-03 (Sections 4 and 6: ADC upgrade and FPGA upgrade) to fill remaining stubs
- HW-IMP equation numbering continues from HW-IMP-15 for Plan 06-03 sections
- Key cross-reference: Section 5 (array expansion) documents SPI scaling that affects Section 6 (FPGA upgrade) if larger arrays need more SPI peripherals
- Priority ranking across all HWRES topics now established: ADC upgrade (HWRES-04) > GaN PA (HWRES-01) > Array expansion (HWRES-05) > AiP (HWRES-03) for near-term impact

---
*Phase: 06-hardware-improvement-research*
*Completed: 2026-03-14*
