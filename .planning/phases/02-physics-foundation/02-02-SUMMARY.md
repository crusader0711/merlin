---
phase: 02-physics-foundation
plan: 02
subsystem: physics
tags: [lfm, chirp, pulse-compression, ambiguity-function, detection-theory, cfar, neyman-pearson, swerling, marcum-q]

# Dependency graph
requires:
  - phase: 01-notation-parameter-standardization
    provides: Symbol table, parameter table, equation conventions
  - phase: 02-physics-foundation (plan 01)
    provides: FMCW theory with beat frequency, range equation, range-Doppler coupling
provides:
  - LFM waveform model with chirp signal, matched filter, pulse compression, ambiguity function (33 tagged equations)
  - Detection theory from Neyman-Pearson through CA-CFAR (24 tagged equations)
  - Detection probability curve SVG figures for Swerling Cases 0 and I
affects: [02-03 beamforming, 02-04 noise figure, phase-3 hardware, phase-4 software CFAR, phase-5 CFAR research]

# Tech tracking
tech-stack:
  added: [matplotlib (SVG generation), numpy (numerical Marcum Q-function)]
  patterns: [numerical quadrature for Marcum Q-function without scipy, I_0 Bessel via power series]

key-files:
  created:
    - 01_physics/02_lfm_waveform_model.md
    - 01_physics/04_detection_theory.md
    - 01_physics/figures/detection_curves_swerling0.svg
    - 01_physics/figures/detection_curves_swerling1.svg
    - 01_physics/figures/gen_detection_curves.py
  modified: []

key-decisions:
  - "33 LFM equations (LFM-1 through LFM-33) covering full chirp-to-ambiguity derivation chain"
  - "24 DET equations (DET-1 through DET-24) covering hypothesis testing through CFAR loss"
  - "Marcum Q-function computed via numerical quadrature with I_0 power series (no scipy dependency)"
  - "Swerling I closed-form P_d = P_fa^(1/(1+SNR)) used for single-pulse detection curves"
  - "CA-CFAR threshold multiplier uses standard Skolnik/Richards formula, not hand-rolled"
  - "Ambiguity function interpreted for four system properties: range resolution, velocity resolution, coupling slope, sidelobe level"

patterns-established:
  - "SVG figure generation with Python script in figures/ directory for reproducibility"
  - "Cross-document equation referencing pattern: Eq. (PREFIX-N) in [filename](path)"

requirements-completed: [PHYS-02, PHYS-04]

# Metrics
duration: 7min
completed: 2026-03-13
---

# Phase 2 Plan 2: LFM Waveform Model and Detection Theory Summary

**LFM chirp signal through ambiguity function (33 equations) and Neyman-Pearson through CA-CFAR detection (24 equations) with Swerling Case 0/I detection probability curve SVGs**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-13T22:52:07Z
- **Completed:** 2026-03-13T22:59:47Z
- **Tasks:** 3
- **Files created:** 5

## Accomplishments
- LFM waveform model document with complete derivation chain: chirp signal, instantaneous frequency, time-bandwidth product, matched filter theory with SNR maximization, pulse compression, sidelobe structure with windowing tradeoffs, and fully interpreted ambiguity function
- Detection theory document with complete derivation chain: binary hypothesis testing, Neyman-Pearson lemma, Gaussian noise model, square-law detector, five Swerling target models, CA-CFAR threshold multiplier derivation, detection probability curves, CFAR loss analysis, and non-homogeneous environment overview
- Two publication-quality SVG detection probability curve figures generated with Python/matplotlib, showing P_d vs SNR for four P_fa values across Swerling Cases 0 and I

## Task Commits

Each task was committed atomically:

1. **Task 1: Write LFM waveform model document** - `ded56bb` (feat)
2. **Task 2: Write detection theory document** - `acb3c2c` (feat)
3. **Task 3: Generate detection probability curve figures** - `f6fbfaa` (feat)

## Files Created/Modified
- `01_physics/02_lfm_waveform_model.md` - LFM chirp signal, matched filter, pulse compression, ambiguity function (33 tagged equations)
- `01_physics/04_detection_theory.md` - Neyman-Pearson, Swerling models, CA-CFAR, detection curves (24 tagged equations)
- `01_physics/figures/detection_curves_swerling0.svg` - P_d vs SNR for non-fluctuating target
- `01_physics/figures/detection_curves_swerling1.svg` - P_d vs SNR for Swerling Case I
- `01_physics/figures/gen_detection_curves.py` - Python script to regenerate figures

## Decisions Made
- Used 33 LFM equations to cover full derivation without gaps, matching the 30-equation depth of the FMCW theory document
- Implemented Marcum Q-function via numerical quadrature with I_0 power series to avoid scipy dependency
- Used standard CA-CFAR threshold multiplier formula from Skolnik/Richards per plan guidance
- Ambiguity function section includes four explicit system-specific interpretations (range resolution, velocity resolution, coupling slope, sidelobe level) rather than just the derivation
- Detection theory motivates OS-CFAR/GO-CFAR/SO-CFAR without deriving them, setting up Phase 5 SWRES-01

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- NumPy 2.x removed `numpy.trapz` in favor of `numpy.trapezoid` -- fixed in generation script (auto-fix during Task 3, Rule 3 blocking issue)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- LFM waveform model and detection theory complete the waveform-to-detection vertical slice
- Beamforming theory (02-03) can now reference matched filter SNR gain from LFM document
- Noise figure chain analysis (02-04, already completed) references radar equation SNR from FMCW theory
- Phase 4 CFAR documentation can reference the CA-CFAR derivation and detection curves
- Phase 5 CFAR research (SWRES-01) has the CA-CFAR baseline and non-homogeneous environment motivation

## Self-Check: PASSED

All 5 created files verified present. All 3 task commits verified in git log.

---
*Phase: 02-physics-foundation*
*Completed: 2026-03-13*
