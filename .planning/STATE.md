---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 05-01-PLAN.md (CFAR variants and clutter rejection research)
last_updated: "2026-03-14T00:46:22.820Z"
last_activity: 2026-03-14 — Completed 06-01-PLAN.md (GaN vs SiGe front-end and synthesizer phase noise research)
progress:
  total_phases: 6
  completed_phases: 5
  total_plans: 21
  completed_plans: 19
  percent: 86
---

---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 06-01-PLAN.md (GaN vs SiGe front-end and synthesizer phase noise research)
last_updated: "2026-03-14T00:45:23.670Z"
last_activity: 2026-03-14 — Completed 06-01-PLAN.md (GaN vs SiGe front-end and synthesizer phase noise research)
progress:
  [█████████░] 86%
  completed_phases: 4
  total_plans: 21
  completed_plans: 15
  percent: 76
---

---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 04-01-PLAN.md (FPGA signal processing pipeline)
last_updated: "2026-03-14T00:16:43.843Z"
last_activity: 2026-03-14 — Completed 03-05-PLAN.md (timing budget and GPS/IMU transforms)
progress:
  [█████████░] 93%
  completed_phases: 3
  total_plans: 14
  completed_plans: 12
---

---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 03-04-PLAN.md (power management and power budget)
last_updated: "2026-03-13T23:53:28.929Z"
last_activity: 2026-03-14 — Completed 03-03-PLAN.md (antenna/beamforming and FPGA board)
progress:
  total_phases: 6
  completed_phases: 3
  total_plans: 11
  completed_plans: 11
---

---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 03-03-PLAN.md (antenna/beamforming and FPGA board)
last_updated: "2026-03-13T23:45:45.761Z"
last_activity: 2026-03-14 — Completed 03-03-PLAN.md (antenna/beamforming and FPGA board)
progress:
  total_phases: 6
  completed_phases: 2
  total_plans: 11
  completed_plans: 10
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-13)

**Core value:** Produce engineering-grade documentation capturing the complete AERIS-10 radar system from first-principles physics through hardware to software, so the team can maintain and improve the radar without tribal knowledge.
**Current focus:** Phase 6 - Hardware Improvement Research (In Progress)

## Current Position

Phase: 6 of 6 (Hardware Improvement Research)
Plan: 2 of 3 in current phase (1 complete)
Status: Executing
Last activity: 2026-03-14 — Completed 06-01-PLAN.md (GaN vs SiGe front-end and synthesizer phase noise research)

Progress: [████████░░] 76%

## Performance Metrics

**Velocity:**
- Total plans completed: 10
- Average duration: 4 min
- Total execution time: 0.60 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 - Notation | 2/2 | 6 min | 3 min |
| 2 - Physics | 4/4 | 18 min | 4.5 min |
| 3 - Hardware | 3/5 | 12 min | 4 min |

**Recent Trend:**
- Last 5 plans: 02-04 (3 min), 02-03 (5 min), 02-01 (3 min), 02-02 (7 min), 03-01 (2 min)
- Trend: steady

*Updated after each plan completion*
| Phase 03 P05 | 5 | 2 tasks | 2 files |
| Phase 04 P01 | 4min | 2 tasks | 2 files |
| Phase 04 P03 | 5 | 2 tasks | 2 files |
| Phase 04 P02 | 4 | 1 tasks | 1 files |
| Phase 05 P02 | 5 | 2 tasks | 2 files |
| Phase 06 P01 | 5 | 2 tasks | 1 files |
| Phase 05 P03 | 6 | 2 tasks | 2 files |
| Phase 05 P01 | 6 | 2 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Strict dependency chain: Notation -> Physics -> Hardware -> Software -> Research (no skipping ahead)
- [Roadmap]: Phases 5 and 6 (SW/HW research) can execute in parallel after Phase 4 completes
- [Roadmap]: GUI_V6.py is the canonical software version; V1-V5 explicitly excluded from documentation
- [01-01]: Document-prefix equation numbering (FMCW-N, LFM-N, BF-N) chosen over section-based numbering for cross-document uniqueness
- [01-01]: Plain-text cross-references because GitHub MathJax does not support \ref{}/\eqref{}
- [01-01]: IEEE 686-2024 as notation authority with Skolnik/Richards as secondary references
- [01-01]: Physical constants in symbol table; all system parameter values deferred to parameter_table.md
- [02-01]: Derived full beat frequency with Doppler term first (FMCW-16), then stationary-target approximation as labeled special case
- [02-01]: 30 tagged equations (FMCW-1 through FMCW-30) to avoid skipping intermediate algebraic steps
- [02-01]: Range-Doppler coupling analyzed symbolically with T_c1/T_c2 = 60 ratio; numerical eval deferred pending bandwidth B
- [02-02]: 33 LFM equations covering full chirp-to-ambiguity derivation chain
- [02-02]: 24 DET equations covering hypothesis testing through CFAR loss
- [02-02]: CA-CFAR uses standard Skolnik/Richards formula; ambiguity function interpreted for four system properties
- [02-02]: Marcum Q-function computed via numerical quadrature (no scipy dependency)
- [02-03]: 19 BF-tagged equations (vs plan's ~15) to avoid skipping intermediate steps, consistent with 02-01 approach
- [02-03]: ADAR1000 phase quantization modeled as deterministic error with specific sidelobe prediction (~-29 dB for N=16)
- [02-03]: Grating lobe analysis shows d/lambda < 0.649 is safe for +/-33 deg scan range (30% margin beyond lambda/2)
- [02-03]: Taylor taper nbar=5 SLL=-30dB as reference design point for beam pattern comparison figures
- [02-04]: ADC effective noise figure modeled as signal-level-dependent (not fixed) due to 8-bit quantization constraint
- [02-04]: CIC filter noise analysis extends chain past ADC with bit growth, passband droop, and truncation noise
- [02-04]: Representative placeholder values clearly labeled for numerical examples (per research recommendation)
- [Phase 03]: HW-SYS equation prefix for system overview; 12 hardware symbols in new Section 7 of symbol table
- [Phase 03]: ADAR1000 beam RAM bypassed; firmware writes phase settings directly via SPI per beam position
- [Phase 03]: FPGA resource utilization documented as theoretical estimates pending Vivado reports
- [Phase 03]: FT601 100 MHz clock treated as asynchronous to system 100 MHz (separate oscillator)
- [Phase 03]: Detailed FPGA signal processing deferred to Phase 4 SWDOC-01; FPGA doc covers structural inventory only
- [Phase 03]: LT5552 mixer NF approximated as reciprocal of conversion loss (standard passive mixer treatment)
- [Phase 03]: AD9523 clock tree table documents all 14 channels (12 active + 2 disabled) for completeness
- [Phase 03]: OCXO warm-up (180s) documented as critical startup timing constraint
- [Phase 03-04]: 17-step power-on sequence documented from firmware main.cpp with exact delays and GPIO pin names
- [Phase 03-04]: PA bias tuning documented with Idq target 1.680A; power budget uses datasheet typical values (xlsx not text-readable)
- [Phase 03]: FPGA pipeline latency values are theoretical estimates pending Vivado timing reports
- [Phase 03]: Complementary filter uses Euler angles (not quaternions) despite q[4] array being initialized in firmware
- [Phase 03]: Flat-Earth approximation valid for GPS coordinate transform at AERIS-10 detection ranges (< 20 km)
- [Phase 04]: Threshold detection documented honestly as placeholder, not true CFAR, despite CFAR variable names in source
- [Phase 04]: Signal-flow documentation organization (ADC to USB) chosen over module-by-module per research recommendation
- [Phase 04]: Magic number derivations include numerical verification as exception to anti-pattern 5.1
- [Phase 04]: FT601 packet: 11 transfers (1 header + 4 range + 4 Doppler + 1 detection + 1 footer) per usb_data_interface.v
- [Phase 04]: GUI system_frequency default 10e9 flagged as known discrepancy vs canonical 10.5 GHz
- [Phase 04-02]: SW equation tags start at SW-20, reserving SW-1 through SW-19 for FPGA pipeline (Plan 01)
- [Phase 05]: Windowed matched filter (Taylor nbar=5) as Priority 1 for pulse compression (0.76 dB loss for 21.7 dB sidelobe improvement)
- [Phase 05]: M=64 CPI as Priority 1 for range extension (3 dB SNR, 1.19x range, 4-6 BRAMs)
- [Phase 05]: NLFM PSL limited to -35 to -40 dB by 8-bit DAC (vs theoretical -45 to -50 dB)
- [Phase 05]: Keystone range migration compensation infeasible on current BRAM budget; segmented integration as alternative
- [Phase 06]: HW-IMP equation prefix for hardware improvement research; GaN PA advantage is transmit power not NF; ADF4382A is best-in-class synthesizer; ADC quantization floor is Doppler bottleneck
- [Phase 05-03]: Dual-port BRAM highest priority optimization (zero cost, immediate throughput gain)
- [Phase 05-03]: Hybrid CFAR+ML recommended over on-FPGA ML (avoids resource constraint via host PC)
- [Phase 05-03]: Multi-bank BRAM interleaving and 2x/4x parallelism infeasible/marginal due to BRAM constraint
- [Phase 05]: CA-CFAR ranked Priority 1; GOCA-CFAR Priority 2 for clutter edges; 2-pulse canceller Priority 1 for clutter rejection
- [Phase 05]: Clutter measurement campaign prerequisite for both CFAR variant selection and clutter rejection tuning
- [Phase 05]: Multi-mode CFAR rated MARGINAL (49-66% of available LUT headroom); all other CFAR variants FEASIBLE

### Pending Todos

None yet.

### Blockers/Concerns

- Clarify which AERIS-10 variant (Nexus vs Extended) is primary for physics derivations before Phase 2
- Confirm FPGA Vivado implementation reports are accessible for Phase 3 and Phase 5 feasibility assessments
- Identify which CFAR variant is implemented in Verilog before Phase 4 FPGA pipeline documentation

## Session Continuity

Last session: 2026-03-14T00:46:22.818Z
Stopped at: Completed 05-01-PLAN.md (CFAR variants and clutter rejection research)
Resume file: None
