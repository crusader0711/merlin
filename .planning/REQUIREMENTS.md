# Requirements: AERIS-10 PLFM Radar Documentation & Research

**Defined:** 2026-03-13
**Core Value:** Produce engineering-grade documentation capturing the complete radar system from first-principles physics through hardware to software, so the team can maintain and improve the radar without tribal knowledge.

## v1 Requirements

### Notation & Standards (NOTN)

- [x] **NOTN-01**: Project-wide symbol table following IEEE 686-2024 notation conventions
- [x] **NOTN-02**: Master system parameter table with canonical values for both AERIS-10 variants (Nexus/Extended)
- [x] **NOTN-03**: Equation numbering convention and cross-reference format established

### Physics Documentation (PHYS)

- [x] **PHYS-01**: FMCW theory — radar equation derivation from first principles, beat frequency, range equation, velocity measurement
- [x] **PHYS-02**: LFM waveform model — chirp signal math, time-bandwidth product, pulse compression gain, ambiguity function
- [x] **PHYS-03**: Beamforming theory — array factor derivation, phase shift per element for ADAR1000, grating lobe conditions, beam patterns
- [x] **PHYS-04**: Detection theory — CFAR derivation with Neyman-Pearson criterion, false alarm probability, detection probability curves
- [x] **PHYS-05**: Range-Doppler coupling analysis — full beat frequency with Doppler term, impact on 30us vs 0.5us chirps, compensation approaches
- [x] **PHYS-06**: Noise figure chain analysis — cascaded NF through LNA (ADTR1107), mixer (LT5552), ADC (AD9484), CIC filter
- [x] **PHYS-07**: Antenna array calibration theory — phase/amplitude error correction, ADAR1000 phase quantization effects, inter-element coupling

### Hardware Documentation (HDWR)

- [x] **HDWR-01**: System overview with master parameter table — center frequency, bandwidth, PRF, ADC rate, antenna gain, NF, FPGA resources
- [x] **HDWR-02**: RF front-end documentation — ADTR1107 LNA/PA, LT5552 mixer, AD9484 ADC with register maps, SPI sequences, key specs (NF, IP3)
- [x] **HDWR-03**: Frequency synthesis documentation — ADF4382 synthesizers, AD9523 clock generator, phase noise specifications, lock time
- [x] **HDWR-04**: Antenna array & beamforming documentation — ADAR1000 phase shifters, 16-element array geometry, beam steering tables
- [x] **HDWR-05**: FPGA board documentation — XC7A100T clock domains (100/120/400 MHz), CDC synchronizers, BUFG usage, LUT/FF/BRAM utilization
- [x] **HDWR-06**: Power management documentation — GPIO-controlled rail sequencing, voltage rails, thermal management, fan control
- [x] **HDWR-07**: Timing budget & latency analysis — ADC to DDC to CIC to matched filter to FFT to CFAR to USB end-to-end pipeline latency
- [x] **HDWR-08**: Power budget analysis — per-rail current draw, total power, thermal dissipation per subsystem
- [x] **HDWR-09**: GPS/IMU coordinate transform math — quaternion to Euler to target coordinate transformation documentation

### Software Documentation (SWDOC)

- [x] **SWDOC-01**: FPGA signal processing pipeline — DDC, CIC decimation, matched filter, 1024-pt FFT, CFAR documented by signal flow
- [ ] **SWDOC-02**: STM32 firmware documentation — initialization sequence, SPI/I2C device addresses, power-on/off sequences, peripheral config
- [x] **SWDOC-03**: Python GUI documentation — USB protocol, RadarTarget dataclass, DBSCAN parameters, Kalman state model, map rendering (V6 only)
- [x] **SWDOC-04**: USB interface protocol — FT601 command/data format, packet structure, RadarSettings.parseFromUSB(), streaming protocol

### SW Improvement Research (SWRES)

- [ ] **SWRES-01**: CFAR variants survey — CA-CFAR, OS-CFAR, GOCA-CFAR, SOCA-CFAR with false alarm rate, detection probability, computational cost comparison
- [ ] **SWRES-02**: Clutter rejection research — MTI filtering, Doppler notch filtering, recursive background subtraction, delay-line clutter rejection
- [ ] **SWRES-03**: Range extension via SNR optimization — coherent integration techniques, longer CPI, non-coherent integration, expected range improvement derivation
- [ ] **SWRES-04**: FPGA pipeline throughput optimization — HLS vs hand-coded Verilog, loop unrolling for FFT/matched filter, multi-bank memory, Artix-7 resource margins
- [ ] **SWRES-05**: ML-based detection alternatives to CFAR — autoencoder-based detection, CNN range-Doppler detectors, FPGA inference feasibility assessment
- [ ] **SWRES-06**: Pulse compression improvements — NLFM waveform optimization, sidelobe reduction without SNR loss, chirp memory/DAC feasibility
- [ ] **SWRES-07**: Target tracking improvements — IMM-Kalman filter, variational Bayesian IMM, adaptive Kalman for maneuvering targets
- [ ] **SWRES-08**: Adaptive beamforming research — MVDR/LCMV beamformers, hybrid robust beamforming, real-time FPGA weight computation feasibility

### HW Improvement Research (HWRES)

- [ ] **HWRES-01**: GaN vs SiGe front-end comparison — output power, noise figure, die size at X-band, comparison to current ADTR1107
- [ ] **HWRES-02**: Frequency synthesizer phase noise improvements — fractional-N PLL advances, ADF4382 vs competing synthesizers, Doppler floor improvement
- [ ] **HWRES-03**: Antenna-in-Package (AiP) miniaturization — 3D-stacked T/R modules, LTCC implementations, compatibility with ADAR1000+ADTR1107
- [ ] **HWRES-04**: Higher-resolution ADC options — 14 to 16-bit upgrade, FPGA interface impact, SNR improvement calculation
- [ ] **HWRES-05**: Antenna array expansion — 16 to 32/64 elements, ADAR1000 cascading, PCB constraints, grating lobe implications
- [ ] **HWRES-06**: FPGA upgrade path — Artix UltraScale+ resource comparison, PCB migration complexity, USB 3.0 compatibility

## v2 Requirements

### Future Research Topics

- **FRES-01**: MIMO radar upgrade path — virtual aperture extension, waveform orthogonality, FPGA processing load
- **FRES-02**: Digital beamforming (DBF) — per-element ADC architecture, data rate requirements, multi-beam capability
- **FRES-03**: Micro-Doppler feature extraction — target classification (drone/vehicle/person), lightweight CNN for embedded use
- **FRES-04**: Dual-band coherent operation — X + Ku band, shared aperture, ADF4382 multi-band capability
- **FRES-05**: Two-stage CFAR for 3D radar — adaptive clutter distribution estimation for azimuth/elevation scan geometry

## Out of Scope

| Feature | Reason |
|---------|--------|
| Implementation of any improvements | Documentation and research only per PROJECT.md |
| Operator/user manuals | Engineering team audience, not operators |
| Regulatory/EMC/safety compliance docs | Requires legal/regulatory expertise |
| Tutorial-style walkthroughs | Engineering audience has RF/DSP background |
| GUI user workflow guides | Document architecture, not click-by-click |
| Implementation specs for improvements | End with feasibility assessment, not design specs |
| Exhaustive CFAR literature review | Focus on FPGA-implementable variants only |
| Commercial system comparison | Engineering research, not competitive analysis |
| DBSCAN parameter optimization | Empirically tunable, low research value |
| Marketing/sales materials | Out of scope per PROJECT.md |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| NOTN-01 | Phase 1 | Complete |
| NOTN-02 | Phase 1 | Complete |
| NOTN-03 | Phase 1 | Complete |
| PHYS-01 | Phase 2 | Complete |
| PHYS-02 | Phase 2 | Complete |
| PHYS-03 | Phase 2 | Complete |
| PHYS-04 | Phase 2 | Complete |
| PHYS-05 | Phase 2 | Complete |
| PHYS-06 | Phase 2 | Complete |
| PHYS-07 | Phase 2 | Complete |
| HDWR-01 | Phase 3 | Complete |
| HDWR-02 | Phase 3 | Complete |
| HDWR-03 | Phase 3 | Complete |
| HDWR-04 | Phase 3 | Complete |
| HDWR-05 | Phase 3 | Complete |
| HDWR-06 | Phase 3 | Complete |
| HDWR-07 | Phase 3 | Complete |
| HDWR-08 | Phase 3 | Complete |
| HDWR-09 | Phase 3 | Complete |
| SWDOC-01 | Phase 4 | Complete |
| SWDOC-02 | Phase 4 | Pending |
| SWDOC-03 | Phase 4 | Complete |
| SWDOC-04 | Phase 4 | Complete |
| SWRES-01 | Phase 5 | Pending |
| SWRES-02 | Phase 5 | Pending |
| SWRES-03 | Phase 5 | Pending |
| SWRES-04 | Phase 5 | Pending |
| SWRES-05 | Phase 5 | Pending |
| SWRES-06 | Phase 5 | Pending |
| SWRES-07 | Phase 5 | Pending |
| SWRES-08 | Phase 5 | Pending |
| HWRES-01 | Phase 6 | Pending |
| HWRES-02 | Phase 6 | Pending |
| HWRES-03 | Phase 6 | Pending |
| HWRES-04 | Phase 6 | Pending |
| HWRES-05 | Phase 6 | Pending |
| HWRES-06 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 37 total
- Mapped to phases: 37
- Unmapped: 0

---
*Requirements defined: 2026-03-13*
*Last updated: 2026-03-13 after roadmap creation*
