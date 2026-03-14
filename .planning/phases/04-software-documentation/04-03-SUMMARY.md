---
phase: 04-software-documentation
plan: 03
subsystem: documentation
tags: [usb, ft601, python, gui, tkinter, protocol, dataclass]

# Dependency graph
requires:
  - phase: 01-notation-parameter-standardization
    provides: Symbol table, parameter table, conventions for document formatting
  - phase: 03-hardware-documentation
    provides: FPGA board docs for FT601 clock domain, GPS/IMU transforms for coordinate chain
provides:
  - USB interface protocol specification (FT601 packet format, STM32 CDC, host commands)
  - Python GUI V6 architecture documentation with complete/stub status tracking
  - RadarSettings field-to-symbol mapping
affects: [05-software-research, 06-hardware-research]

# Tech tracking
tech-stack:
  added: []
  patterns: [stub-status-tracking, code-variable-to-symbol-mapping, binary-protocol-specification]

key-files:
  created:
    - 03_software/04_usb_protocol.md
    - 03_software/03_python_gui.md
  modified: []

key-decisions:
  - "Documented FT601 packet as 11 transfers (1 header + 4 range + 4 Doppler + 1 detection + 1 footer) based on usb_data_interface.v state machine"
  - "Flagged system_frequency default 10e9 vs canonical 10.5 GHz as known issue in GUI doc"
  - "STM32USBInterface noted as referenced-but-not-defined in GUI_V6.py"

patterns-established:
  - "Stub-vs-complete status table: every class explicitly marked with implementation status"
  - "Binary protocol byte-map tables: offset, size, type, byte order, content columns"

requirements-completed: [SWDOC-03, SWDOC-04]

# Metrics
duration: 5min
completed: 2026-03-14
---

# Phase 4 Plan 3: USB Protocol and Python GUI Summary

**FT601 USB 3.0 packet protocol fully specified (0xAA/0x55 framing, range/Doppler/detection fields) with STM32 CDC GPS binary format and Python GUI V6 architecture documenting 4 complete + 5 stub classes**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-14T00:12:07Z
- **Completed:** 2026-03-14T00:16:38Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- Complete USB protocol specification enabling new client implementation without reading source code
- Python GUI V6 architecture documented with explicit stub-vs-complete status for every class
- All dataclass fields mapped to standard symbols per anti-pattern 5.4
- Cross-references established between USB protocol doc, GUI doc, and Phase 2/3 docs

## Task Commits

Each task was committed atomically:

1. **Task 1: Write USB interface protocol document** - `02e1d52` (feat)
2. **Task 2: Write Python GUI V6 documentation** - `2428311` (feat)

## Files Created/Modified
- `03_software/04_usb_protocol.md` - Complete USB interface protocol: FT601 physical layer, packet format, STM32 GPS/settings protocol, streaming protocol, new client guide (371 lines)
- `03_software/03_python_gui.md` - Python GUI V6 architecture: class hierarchy, implementation status, dataclasses, FT601Interface, designed interfaces for stubs (419 lines)

## Decisions Made
- Documented FT601 packet structure as 11 transfers based on the `usb_data_interface.v` state machine analysis (1 header + 4 range + 4 Doppler + 1 detection + 1 footer)
- Flagged `system_frequency` default of `10e9` in GUI as known discrepancy vs canonical `10.5 GHz` from parameter table
- Noted `STM32USBInterface` is referenced in `RadarGUI.__init__()` but not defined in `GUI_V6.py` -- documented as "Not defined" status
- Included SW-1 through SW-3 equation tags for data rate calculation and designed DBSCAN/Kalman formulations

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `03_software/` directory established with USB protocol and GUI docs
- Cross-references to `01_fpga_pipeline.md` and `02_stm32_firmware.md` are forward-looking (those docs created by plans 04-01 and 04-02)
- Phase 4 plans 01 and 02 can reference these docs for USB data output and GUI integration context

---
*Phase: 04-software-documentation*
*Completed: 2026-03-14*
