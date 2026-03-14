# Roadmap: AERIS-10 PLFM Radar Documentation & Research

## Overview

This project produces engineering-grade documentation for the AERIS-10 FMCW phased array radar system, followed by improvement research surveys. The build order is strictly layered: notation standardization first (prevents the highest-probability failure mode), then physics derivations (foundation for everything), then hardware documentation (assigns real component values to physics equations), then software documentation (shows how hardware is controlled and data processed), and finally parallel research surveys that evaluate improvements against the documented baseline. No research document can be written credibly before the system documentation it references is complete.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Notation & Parameter Standardization** - Establish project-wide symbol table, master parameter table, and cross-reference conventions before any derivations begin (completed 2026-03-13)
- [x] **Phase 2: Physics Foundation** - Derive FMCW theory, signal models, beamforming, and detection theory from first principles (completed 2026-03-13)
- [x] **Phase 3: Hardware Documentation** - Document all hardware subsystems with component specs, register maps, and analysis (completed 2026-03-13)
- [x] **Phase 4: Software Documentation** - Document FPGA pipeline, STM32 firmware, and Python GUI by signal/data flow (completed 2026-03-14)
- [ ] **Phase 5: Software Improvement Research** - Survey target detection, signal processing, and FPGA optimization advances with feasibility assessments
- [ ] **Phase 6: Hardware Improvement Research** - Survey RF, antenna, ADC, and FPGA upgrade paths with noise figure impact analysis

## Phase Details

### Phase 1: Notation & Parameter Standardization
**Goal**: Engineers opening any document in the set encounter consistent notation and can look up any system parameter in one canonical location
**Depends on**: Nothing (first phase)
**Requirements**: NOTN-01, NOTN-02, NOTN-03
**Success Criteria** (what must be TRUE):
  1. A project-wide symbol table exists following IEEE 686-2024 conventions, and every symbol used in later documents is defined there
  2. A master system parameter table exists with canonical values for both AERIS-10 variants (Nexus and Extended), covering center frequency, bandwidth, PRF, ADC rate, antenna gain, noise figure, and FPGA resources
  3. An equation numbering convention and cross-reference format is established and documented so all subsequent physics/hardware/software documents can reference equations consistently
**Plans**: 2 plans

Plans:
- [x] 01-01-PLAN.md — Equation/formatting conventions and project-wide symbol table (NOTN-01, NOTN-03)
- [ ] 01-02-PLAN.md — Master system parameter table for both AERIS-10 variants (NOTN-02)

### Phase 2: Physics Foundation
**Goal**: Engineers can trace any signal processing operation in the radar back to a first-principles physics derivation
**Depends on**: Phase 1
**Requirements**: PHYS-01, PHYS-02, PHYS-03, PHYS-04, PHYS-05, PHYS-06, PHYS-07
**Success Criteria** (what must be TRUE):
  1. FMCW radar equation is derived from first principles through beat frequency to range/velocity measurement, with the full Range-Doppler coupling term included (not simplified away)
  2. LFM waveform model documents chirp signal mathematics, time-bandwidth product, pulse compression gain, and ambiguity function with derivations an engineer can follow step-by-step
  3. Beamforming array factor is derived for the 16-element geometry with ADAR1000 phase shift per element, grating lobe conditions, and beam pattern plots
  4. CFAR detection theory is derived from Neyman-Pearson criterion through false alarm probability to detection probability curves, with the clutter distribution assumption made explicit
  5. Noise figure chain analysis traces cascaded NF through the full receive path (ADTR1107 LNA, LT5552 mixer, AD9484 ADC, CIC filter) and antenna calibration theory covers ADAR1000 phase/amplitude error correction
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md — Symbol table additions and FMCW theory from first principles with range-Doppler coupling (PHYS-01, PHYS-05)
- [ ] 02-02-PLAN.md — LFM waveform model and detection theory (PHYS-02, PHYS-04)
- [ ] 02-03-PLAN.md — Beamforming theory and antenna calibration theory (PHYS-03, PHYS-07)
- [ ] 02-04-PLAN.md — Cascaded noise figure chain analysis (PHYS-06)

### Phase 3: Hardware Documentation
**Goal**: Engineers can locate any hardware subsystem's specifications, register maps, interface details, and operational constraints in one place
**Depends on**: Phase 2
**Requirements**: HDWR-01, HDWR-02, HDWR-03, HDWR-04, HDWR-05, HDWR-06, HDWR-07, HDWR-08, HDWR-09
**Success Criteria** (what must be TRUE):
  1. System overview document anchors all subsystem cross-references with a master parameter table that is the single source of truth for every numerical value in the documentation set
  2. RF front-end (ADTR1107, LT5552, AD9484), frequency synthesis (ADF4382, AD9523), and antenna array (ADAR1000, 16-element geometry) are documented with register maps, SPI sequences, and key specs (NF, IP3, phase noise, lock time)
  3. FPGA board documentation covers XC7A100T clock domains (100/120/400 MHz), CDC synchronizers, BUFG usage, and LUT/FF/BRAM utilization
  4. Power management documents GPIO-controlled rail sequencing, voltage rails, thermal management, and fan control; power budget analysis covers per-rail current draw and thermal dissipation per subsystem
  5. End-to-end timing budget traces latency from ADC through DDC, CIC, matched filter, FFT, CFAR to USB output; GPS/IMU coordinate transform math is documented with quaternion-to-Euler-to-target transformations
**Plans**: 5 plans

Plans:
- [ ] 03-01-PLAN.md — System overview with hardware symbol table additions and subsystem index (HDWR-01)
- [ ] 03-02-PLAN.md — RF front-end and frequency synthesis documentation (HDWR-02, HDWR-03)
- [ ] 03-03-PLAN.md — Antenna/beamforming hardware and FPGA board documentation (HDWR-04, HDWR-05)
- [ ] 03-04-PLAN.md — Power management and power budget analysis (HDWR-06, HDWR-08)
- [ ] 03-05-PLAN.md — End-to-end timing budget and GPS/IMU coordinate transforms (HDWR-07, HDWR-09)

### Phase 4: Software Documentation
**Goal**: Engineers can follow any data path from ADC input through FPGA processing to GUI display without undocumented gaps
**Depends on**: Phase 3
**Requirements**: SWDOC-01, SWDOC-02, SWDOC-03, SWDOC-04
**Success Criteria** (what must be TRUE):
  1. FPGA signal processing pipeline is documented by signal flow (DDC to CIC decimation to matched filter to 1024-pt FFT to CFAR), not by Verilog module, with each stage's input/output formats and the implemented CFAR variant explicitly identified
  2. STM32 firmware documentation covers initialization sequence, SPI/I2C device addresses, power-on/off sequences, and peripheral configuration including derivation of magic numbers (PRI1=167us, Guard=175.4us, phase differences array)
  3. Python GUI documentation covers USB protocol, RadarTarget dataclass, DBSCAN clustering parameters, Kalman state model, and map rendering for canonical version GUI_V6.py only (V1-V5 explicitly excluded)
  4. USB interface protocol documents FT601 command/data format, packet structure, RadarSettings.parseFromUSB(), and streaming protocol completely enough to implement a new client
**Plans**: 3 plans

Plans:
- [ ] 04-01-PLAN.md — FPGA signal processing pipeline by signal flow with magic number derivations (SWDOC-01)
- [ ] 04-02-PLAN.md — STM32 firmware initialization, peripherals, and radar loop documentation (SWDOC-02)
- [ ] 04-03-PLAN.md — USB interface protocol and Python GUI V6 architecture documentation (SWDOC-03, SWDOC-04)

### Phase 5: Software Improvement Research
**Goal**: Engineers have a grounded survey of software improvement options with feasibility assessments against the actual Artix-7 XC7A100T hardware
**Depends on**: Phase 4 (Phases 5 and 6 can execute in parallel)
**Requirements**: SWRES-01, SWRES-02, SWRES-03, SWRES-04, SWRES-05, SWRES-06, SWRES-07, SWRES-08
**Success Criteria** (what must be TRUE):
  1. CFAR variants (CA, OS, GOCA, SOCA) are compared on false alarm rate, detection probability, and computational cost, with each variant's Artix-7 resource estimate (LUT/DSP48E1/BRAM)
  2. Clutter rejection approaches (MTI, Doppler notch, background subtraction) and range extension techniques (coherent/non-coherent integration) are surveyed with expected range improvement derivations referenced to the documented noise figure chain
  3. FPGA pipeline optimization research (HLS vs hand-coded Verilog, loop unrolling, multi-bank memory) includes resource margin analysis against documented XC7A100T utilization
  4. ML-based detection alternatives, pulse compression improvements (NLFM), target tracking advances (IMM-Kalman), and adaptive beamforming (MVDR/LCMV) each include an FPGA inference feasibility assessment grounded in actual hardware constraints
  5. Every research document opens with a "Current State" section that references the system documentation baseline before surveying the literature
**Plans**: 4 plans

Plans:
- [ ] 05-01-PLAN.md — CFAR variants survey and clutter rejection research (SWRES-01, SWRES-02)
- [ ] 05-02-PLAN.md — Range extension via SNR optimization and pulse compression improvements (SWRES-03, SWRES-06)
- [ ] 05-03-PLAN.md — FPGA pipeline optimization and ML-based detection alternatives (SWRES-04, SWRES-05)
- [ ] 05-04-PLAN.md — Target tracking improvements and adaptive beamforming research (SWRES-07, SWRES-08)

### Phase 6: Hardware Improvement Research
**Goal**: Engineers have a grounded survey of hardware upgrade paths with impact traced through the documented noise figure chain and RF link budget
**Depends on**: Phase 3 (Phases 5 and 6 can execute in parallel after Phase 4)
**Requirements**: HWRES-01, HWRES-02, HWRES-03, HWRES-04, HWRES-05, HWRES-06
**Success Criteria** (what must be TRUE):
  1. GaN vs SiGe front-end comparison covers output power, noise figure, and die size at X-band with quantified impact on detection range relative to current ADTR1107 baseline
  2. Frequency synthesizer phase noise improvements and higher-resolution ADC options each include calculated impact on Doppler floor and SNR respectively, with FPGA interface compatibility assessed
  3. Antenna-in-Package miniaturization and antenna array expansion (16 to 32/64 elements) research addresses both AERIS-10 variants (Nexus and Extended) with PCB constraints and grating lobe implications
  4. FPGA upgrade path (Artix UltraScale+) includes resource comparison, PCB migration complexity, and USB 3.0 compatibility assessment
**Plans**: TBD

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD

## Progress

**Execution Order:**
Phases 1 through 4 execute sequentially. Phases 5 and 6 can execute in parallel after Phase 4 completes.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Notation & Parameter Standardization | 1/2 | Executing | - |
| 2. Physics Foundation | 4/4 | Complete   | 2026-03-13 |
| 3. Hardware Documentation | 5/5 | Complete   | 2026-03-13 |
| 4. Software Documentation | 3/3 | Complete   | 2026-03-14 |
| 5. Software Improvement Research | 0/4 | Not started | - |
| 6. Hardware Improvement Research | 0/TBD | Not started | - |
