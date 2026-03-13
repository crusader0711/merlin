# PLFM RADAR Documentation & Research

## What This Is

A comprehensive documentation and research initiative for the AERIS-10 PLFM Radar System — a fully operational FMCW X-band (10 GHz) phased array radar with 16-element beamforming. The project produces three deliverables: detailed system documentation (software, hardware, physics with full derivations), a software improvement research survey (target detection & signal processing), and a hardware improvement research survey — all written for the engineering team that maintains and extends the system.

## Core Value

Produce engineering-grade documentation that captures the complete system — from first-principles physics through hardware design to software implementation — so the team can maintain, debug, and improve the radar without tribal knowledge.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(None yet — ship to validate)

### Active

<!-- Current scope. Building toward these. -->

- [ ] Complete software documentation (MATLAB processing, Python GUI/control, FPGA Verilog signal processing)
- [ ] Complete hardware documentation (RF front-end, FPGA, STM32, power management, antenna array)
- [ ] Physics documentation with full derivations (FMCW theory, beamforming, signal models, detection theory)
- [ ] Software improvement research: target detection advances (CFAR alternatives, ML-based detection, clutter rejection)
- [ ] Software improvement research: signal processing advances (pulse compression, Doppler processing, real-time optimization)
- [ ] Hardware improvement research: RF/antenna improvements (miniaturization, range extension, component upgrades)
- [ ] All documents cross-referenced and internally consistent

### Out of Scope

- Implementation of any improvements — this project is documentation and research only
- User manuals or operator guides — audience is engineering team, not end users
- Marketing or sales materials
- Regulatory/compliance documentation (EMC, safety)

## Context

The AERIS-10 is a fully operational FMCW phased array radar system built around:
- **STM32F746** microcontroller (system control, peripheral management, GPS/IMU)
- **Xilinx XC7A100T Artix-7 FPGA** (real-time signal processing pipeline: DDC → CIC decimation → matched filter → 1024-pt FFT → CFAR)
- **Python/Tkinter GUI** (visualization, DBSCAN clustering, Kalman tracking, map rendering)
- **16-element phased array** with ADAR1000 beamformers and ADTR1107 front-ends
- **ADF4382 frequency synthesizers**, AD9523 clock generator, AD9484 14-bit 400MHz ADC
- **FT601 USB 3.0** high-speed data interface

Key pain points driving the improvement research:
1. **Detection range** — want to detect targets at greater distances
2. **Clutter rejection** — better filtering of ground/weather clutter
3. **Processing speed** — faster real-time signal processing
4. **Hardware miniaturization** — smaller/lighter components for the platform

## Constraints

- **Audience**: Engineering team — full technical depth expected, no dumbing down
- **Physics depth**: Full derivations from first principles, not just applied formulas
- **Format**: Markdown files in repository, cross-referenced
- **Scope**: Documentation and research only — no code changes

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Equal depth across all domains (SW/HW/Physics) | Team needs complete reference, not just one layer | — Pending |
| Full physics derivations | Engineers need to understand signal models to make improvements | — Pending |
| Separate research docs for SW and HW improvements | Different expertise needed, clearer organization | — Pending |
| Survey + actionable recommendations | Team wants both state-of-the-art awareness and concrete next steps | — Pending |

---
*Last updated: 2026-03-13 after initialization*
