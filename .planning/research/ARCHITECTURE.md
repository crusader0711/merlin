# Architecture Research

**Domain:** Multi-domain engineering documentation set — FMCW phased array radar (AERIS-10)
**Researched:** 2026-03-13
**Confidence:** HIGH (system is fully built and inspectable; architecture derived from direct analysis)

## Standard Architecture

### Documentation Hierarchy

The documentation set spans four knowledge layers. Each layer depends on the layer below it — software cannot be properly documented without hardware context, hardware cannot be properly documented without physics context, and research surveys cannot be properly written without system documentation as a baseline.

```
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 4: Research Surveys (improvement-oriented)                │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐  │
│  │  SW Improvement      │  │  HW Improvement                  │  │
│  │  (detection+proc.)   │  │  (RF/antenna/components)         │  │
│  └──────────┬───────────┘  └────────────────┬─────────────────┘  │
├─────────────┼────────────────────────────────┼────────────────────┤
│  LAYER 3: Software Documentation             │                    │
│  ┌──────────┴──────┐  ┌────────┐  ┌──────────┴──────────────┐    │
│  │  FPGA / Verilog │  │ STM32  │  │  Python GUI / Processing │    │
│  └──────────┬──────┘  └───┬────┘  └──────────┬──────────────┘    │
├─────────────┼─────────────┼───────────────────┼────────────────────┤
│  LAYER 2: Hardware Documentation                                  │
│  ┌──────────┴──┐  ┌───────┴────┐  ┌──────────┴──┐  ┌──────────┐  │
│  │  RF Front-  │  │  Frequency │  │  FPGA Board  │  │  Power   │  │
│  │  End/Array  │  │  Synthesis  │  │  & Interfaces│  │  Mgmt    │  │
│  └──────────┬──┘  └───────┬────┘  └──────────┬──┘  └────┬─────┘  │
├─────────────┼─────────────┼───────────────────┼──────────┼────────┤
│  LAYER 1: Physics Documentation (foundation)                      │
│  ┌──────────┴──┐  ┌───────┴────┐  ┌───────────┴─┐  ┌──────────┐  │
│  │  FMCW       │  │ Beamforming │  │  Signal     │  │Detection │  │
│  │  Theory     │  │ & Phased    │  │  Model &    │  │Theory    │  │
│  │  (LFM/      │  │ Arrays      │  │  Radar Eqn  │  │(CFAR etc)│  │
│  │  chirp)     │  │             │  │             │  │          │  │
│  └─────────────┘  └────────────┘  └─────────────┘  └──────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Document | Responsibility | Primary Audience Use |
|----------|----------------|----------------------|
| Physics / FMCW Theory | Beat frequency derivation, range/velocity equations, range-Doppler coupling, SNR from first principles | Referenced by SW docs for parameter justification; by research surveys for technique comparison |
| Physics / Beamforming | Array factor derivation, phase shift mathematics, ADAR1000 steering law, grating lobe conditions | Referenced by HW docs (antenna, ADAR1000); by SW docs (FPGA beamforming control) |
| Physics / Signal Model | Complete received signal model, I/Q decomposition, matched filter derivation, Doppler shift proof | Referenced by FPGA doc (pipeline stages); research surveys (proposed improvements start here) |
| Physics / Detection Theory | CFAR derivation (CA-CFAR, OS-CFAR), Pd/Pfa tradeoffs, Swerling models | Referenced by FPGA doc (CFAR stage); SW improvement survey (CFAR alternatives section) |
| HW / RF Front-End | ADTR1107 LNA/PA chain, LT5552 mixer, IF bandwidth, NF budget, gain chain | Referenced by Physics docs for gain values in radar equation; by SW docs for AGC parameters |
| HW / Frequency Synthesis | ADF4382 PLL config, AD9523 clock distribution, phase noise contribution, synthesizer timing | Referenced by FPGA doc (ADC/DAC clock domains); Physics doc (coherence requirements) |
| HW / FPGA Board | XC7A100T resources, clock architecture, DDR/BRAM usage, FT601 USB interface | Referenced by all FPGA SW docs; by power doc for power budget |
| HW / Power Management | Sequencing tables, rail voltages/currents, STM32 GPIO sequencing, thermal management | Referenced by HW docs for operating conditions; context for HW improvement survey |
| SW / FPGA (Verilog) | Pipeline stage-by-stage documentation: DDC → CIC → matched filter → FFT → CFAR → USB | References Physics docs for mathematical justification of each stage |
| SW / STM32 | Peripheral init, beamformer control sequences, GPS/IMU integration, power sequencing calls | References HW docs for register maps and timing; Physics doc for steering law implementation |
| SW / Python GUI | Signal processing chain (DBSCAN, Kalman), USB protocol, visualization architecture | References Physics docs for Doppler/range interpretation; SW FPGA doc for data format |
| Research / SW Improvement | CFAR alternatives, ML detection, clutter rejection, real-time optimization techniques | References SW docs as baseline; Physics detection theory for comparison metrics |
| Research / HW Improvement | Antenna miniaturization, range extension, component upgrades, power efficiency | References HW docs as baseline; Physics signal model for range budget analysis |

## Recommended Documentation Structure

```
docs/
├── physics/
│   ├── 01_fmcw_theory.md           # LFM chirp, beat frequency, range eq. derivation
│   ├── 02_signal_model.md          # Complete received signal, I/Q, matched filter
│   ├── 03_beamforming.md           # Array factor, phase steering, grating lobes
│   └── 04_detection_theory.md      # CFAR derivation, Pd/Pfa, Swerling models
├── hardware/
│   ├── 01_system_overview.md       # Block diagram, subsystem interfaces
│   ├── 02_rf_frontend.md           # ADTR1107, LT5552, gain/NF budget
│   ├── 03_frequency_synthesis.md   # ADF4382, AD9523, clock distribution
│   ├── 04_antenna_array.md         # Patch array (Nexus) and waveguide (Extended)
│   ├── 05_fpga_board.md            # XC7A100T resources, interfaces, constraints
│   └── 06_power_management.md      # Sequencing, rails, thermal
├── software/
│   ├── 01_fpga_pipeline.md         # Full Verilog pipeline documentation
│   ├── 02_stm32_firmware.md        # STM32 application, drivers, sequencing
│   └── 03_python_gui.md            # GUI architecture, signal processing, USB protocol
└── research/
    ├── 01_sw_target_detection.md   # CFAR alternatives, ML-based detection
    ├── 02_sw_signal_processing.md  # Pulse compression, Doppler, real-time
    └── 03_hw_improvements.md       # RF/antenna, range extension, miniaturization
```

### Structure Rationale

- **physics/**: Numbered 01-04 to enforce reading order. FMCW theory must come before signal model; signal model must come before detection theory. These are foundation documents — they never reference hardware or software, only mathematics and physics.
- **hardware/**: System overview first so any hardware sub-doc can reference back to it for context. Each subsystem doc is self-contained but cross-links to neighboring subsystems via interface specifications.
- **software/**: FPGA pipeline first because it is the most complex and most frequently referenced. STM32 and GUI docs reference FPGA data formats and interfaces.
- **research/**: Written last. Each research doc opens with a "Current State" section that links to the corresponding system documentation, then surveys the literature for improvements.

## Architectural Patterns

### Pattern 1: Foundation-First Build Order

**What:** Write physics docs before hardware docs, hardware docs before software docs, and system docs before research surveys. No document references a document written "above" it in the hierarchy.

**When to use:** Always for this project. The dependency chain is strict: range equation parameters come from hardware (noise figure, gain), which come from physics (radar equation). If a software doc is written before the hardware doc, the author will either skip justifications or embed hardware facts in the wrong layer.

**Trade-offs:** Slower start — the visible deliverable (SW doc) comes after invisible groundwork. Payoff is a consistent, trustworthy reference where every number is traceable.

### Pattern 2: Interface-Contract Cross-References

**What:** When document A depends on document B, reference the specific section of B rather than the document as a whole. Use explicit anchor links in Markdown.

**When to use:** Everywhere a number or claim is borrowed from another layer. Example: the FPGA pipeline doc states the matched filter reference chirp length as 30 µs for the long chirp and 0.5 µs for the short chirp. That fact is owned by the Physics / Signal Model doc (waveform parameters section) and the FPGA pipeline doc links to it.

**Trade-offs:** Requires section anchors to be stable across edits. Establish anchor conventions early (e.g., `#range-equation`, `#cfar-threshold`) and do not rename them.

**Example reference pattern:**
```markdown
The matched filter applies pulse compression using the stored reference chirp
(long: 30 µs, short: 0.5 µs). See [Signal Model — Waveform Parameters](../physics/02_signal_model.md#waveform-parameters)
for the derivation of these values from bandwidth and time-bandwidth product requirements.
```

### Pattern 3: "Current State / Literature / Gap" Research Survey Structure

**What:** Each research document follows a fixed three-part structure: (1) document the current system implementation in detail, (2) survey the literature for state-of-the-art alternatives, (3) identify gaps as actionable recommendations.

**When to use:** All four research documents. This structure makes the research immediately actionable — the team can read Part 1 alone if they only need a system refresher, or jump to Part 3 for recommendations.

**Trade-offs:** Part 1 is redundant with the system documentation, but this redundancy is intentional. Research surveys should be self-contained so they can be shared with external collaborators who do not have the full doc set.

### Pattern 4: Parametric Consistency via a Single Source of Truth Table

**What:** Create one master table in `hardware/01_system_overview.md` listing all system parameters (center frequency, chirp bandwidth, pulse width, PRF, ADC sample rate, antenna gain, noise figure, etc.). Every other document that uses these numbers links to this table rather than re-stating them.

**When to use:** Any time a numerical system parameter appears in more than one document.

**Why this matters:** The AERIS-10 has two versions (Nexus 3 km / Extended 20 km) with different antenna arrays and power stages. Without a single source of truth, inconsistency between SW and HW documents is inevitable.

## Data Flow

### Signal Processing Chain (documentation follows this flow)

```
[Antenna Array]
     |  (physics/03_beamforming.md owns the math)
     v
[ADTR1107 LNA → LT5552 Mixer → IF chain]
     |  (hardware/02_rf_frontend.md owns this)
     v
[AD9484 ADC @ 400 MHz, 14-bit]
     |  (hardware/05_fpga_board.md owns ADC interface)
     v
[FPGA: DDC → CIC 4x → Matched Filter → 1024-pt FFT → CFAR]
     |  (software/01_fpga_pipeline.md owns this; physics/02+04 justify it)
     v
[FT601 USB 3.0 → Python GUI]
     |  (software/03_python_gui.md owns this)
     v
[DBSCAN clustering → Kalman tracking → Map display]
     |  (software/03_python_gui.md owns this)
```

### Documentation Cross-Reference Flow

```
physics/01_fmcw_theory.md
    ↓ (beat freq. derivation consumed by)
physics/02_signal_model.md
    ↓ (I/Q model, matched filter consumed by)
software/01_fpga_pipeline.md      hardware/02_rf_frontend.md
    ↓                                    ↓
research/01_sw_target_detection.md  research/03_hw_improvements.md

physics/04_detection_theory.md
    ↓ (CFAR math consumed by)
software/01_fpga_pipeline.md (CFAR stage)
    ↓
research/01_sw_target_detection.md (CFAR alternatives section)

physics/03_beamforming.md
    ↓ (consumed by)
hardware/04_antenna_array.md    software/02_stm32_firmware.md (ADAR1000 steering)
    ↓
research/03_hw_improvements.md (antenna section)
```

### Key Data Flows to Document

1. **Chirp generation path:** Python LUT generation (`LUT.py`) → `.mem` files → FPGA `plfm_chirp_controller.v` → DAC → RF. This crosses all three SW layers and requires both SW and HW docs to agree on chirp parameters.
2. **Receive pipeline:** ADC LVDS → `ddc_400m.v` → `cic_decimator_4x_enhanced.v` → `matched_filter_multi_segment.v` → `doppler_processor.v` → `usb_data_interface.v`. Each stage is a documentation unit in `software/01_fpga_pipeline.md`.
3. **Beam steering path:** ADAR1000 phase codes in `ADAR1000_Manager.cpp` → SPI via STM32 → ADAR1000 registers → antenna phase shifts. Physics beamforming doc derives the steering law; HW doc specifies the ADAR1000 register map; SW STM32 doc shows the implementation.
4. **GPS/IMU correction path:** GPS/IMU data acquired by STM32 → sent over USB → GUI applies coordinate correction to `RadarTarget` objects. Documented in STM32 doc (acquisition) and GUI doc (application).

## Build Order for Documentation Phases

The dependency graph imposes a strict build order. Phases that can be parallelized are grouped.

| Phase | Documents | Dependencies | Can Parallelize With |
|-------|-----------|--------------|----------------------|
| 1 | `physics/01_fmcw_theory.md` | None (start here) | — |
| 2 | `physics/02_signal_model.md`, `physics/03_beamforming.md` | Phase 1 | Each other |
| 3 | `physics/04_detection_theory.md`, `hardware/01_system_overview.md` | Phase 2 | Each other |
| 4 | `hardware/02_rf_frontend.md`, `hardware/03_frequency_synthesis.md`, `hardware/04_antenna_array.md` | Phase 3 | All three |
| 5 | `hardware/05_fpga_board.md`, `hardware/06_power_management.md` | Phase 4 | Each other |
| 6 | `software/01_fpga_pipeline.md` | Phases 3, 5 (physics + HW) | — |
| 7 | `software/02_stm32_firmware.md`, `software/03_python_gui.md` | Phase 6 | Each other |
| 8 | `research/01_sw_target_detection.md`, `research/02_sw_signal_processing.md`, `research/03_hw_improvements.md` | Phase 7 | All three |

**Critical path:** physics/01 → physics/02 → software/01_fpga_pipeline.md. Everything flows through the FPGA pipeline doc, which is the most complex and most central document in the set.

## Anti-Patterns

### Anti-Pattern 1: Hardware Facts Embedded in Software Documentation

**What people do:** Document the chirp bandwidth (500 MHz) inside the FPGA pipeline doc, the ADC sample rate inside the Python GUI doc, etc.

**Why it's wrong:** When a parameter changes or is corrected, it must be updated in every document it appears in. With a system this complex, parameters will inevitably fall out of sync.

**Do this instead:** All numerical parameters live in `hardware/01_system_overview.md`. All other documents reference that table with an explicit anchor link.

### Anti-Pattern 2: Writing Research Surveys Without a Documented Baseline

**What people do:** Jump straight to surveying CFAR alternatives without first documenting what the AERIS-10 currently implements.

**Why it's wrong:** The research survey becomes disconnected from the actual system. Recommendations may duplicate existing functionality, or assume different parameters than what the system uses. The team cannot evaluate whether a proposed improvement actually helps.

**Do this instead:** Each research document opens with a "Current System" section (2-3 pages minimum) that describes the existing implementation in the context of this research topic. Write this before touching the literature.

### Anti-Pattern 3: Physics Derivations Mixed Into Hardware or Software Docs

**What people do:** Derive the CFAR threshold equation inside the FPGA pipeline document because "that's where CFAR is implemented."

**Why it's wrong:** The same derivation is needed by the research survey. Duplicating it creates inconsistency risk. The software doc author may also simplify the derivation, losing the rigor the research author needs.

**Do this instead:** Physics derivations live in the physics layer only. Software and hardware docs cite the result and link to the derivation.

### Anti-Pattern 4: One Monolithic Document Per Domain

**What people do:** Write one large "Software Documentation" PDF covering FPGA + STM32 + GUI.

**Why it's wrong:** The FPGA pipeline is 2000+ lines of Verilog across 10+ modules. The GUI is 1000+ lines of Python with clustering, tracking, and visualization. These are distinct systems with different audiences (RTL engineers vs. Python developers). A monolithic doc becomes unnavigable and unmaintainable.

**Do this instead:** One document per major subsystem, with explicit interface documents at the boundaries.

## Integration Points

### External References (into the docs)

| Source | Integration Pattern | Notes |
|--------|---------------------|-------|
| Component datasheets (`7_Components Datasheets/`) | Link to specific section/page in datasheet | Never copy register tables — link. Datasheets may be revised. |
| Simulation results (`5_Simulations/`) | Embed key figures with reference to simulation project | State tool version (OpenEMS, LTspice) and date of simulation |
| `8_Utils/Python/*.py` equations | Quote the equation, link to script | `RADAR_eq.py` and `patch_antenna.py` are documentation-adjacent — reference them |
| Existing README | `hardware/01_system_overview.md` supersedes README technical content | README stays as quick-start; full detail lives in docs |

### Internal Boundaries

| Boundary | Communication Pattern | Notes |
|-----------|-----------------------|-------|
| Physics → Hardware | Physics provides equations; HW provides component values that satisfy those equations | Physics doc should not know component model numbers; HW doc should not re-derive equations |
| Physics → Software | Physics provides mathematical models for each pipeline stage | FPGA doc cites physics result, not re-derives it |
| Hardware → Software | HW doc provides register maps, timing diagrams, electrical specs | SW doc references HW doc for all configuration values |
| System Docs → Research | Research doc Section 1 summarizes current system (sourced from system docs); Section 2 surveys literature; Section 3 provides gap analysis | Research docs are allowed to synthesize across multiple system docs |
| FPGA SW → GUI SW | FT601 USB data format is the interface contract | This interface must be documented explicitly in both `software/01_fpga_pipeline.md` (producer) and `software/03_python_gui.md` (consumer) |

## Versioning and Dual-Version Handling

The AERIS-10 exists in two variants: Nexus (3 km, patch array) and Extended (20 km, waveguide array, GaN PAs). Documentation must be explicit about which variant is being described.

**Recommended convention:** Use callout blocks for variant-specific content:

```markdown
> **AERIS-10X (Extended) only:** The QPA2962 GaN power amplifiers require
> additional power sequencing. See [Power Management](../hardware/06_power_management.md#extended-variant).
```

Physics and most FPGA documents apply to both variants. RF front-end, antenna, and power management documents have significant variant-specific sections.

## Sources

- Direct codebase analysis: `9_Firmware/` directory, all Verilog modules and Python files (HIGH confidence — primary source)
- [Documenting Software Architectures: Views and Beyond](https://ptgmedia.pearsoncmg.com/images/9780321552686/samplepages/0321552687.pdf) — layered documentation and interface-contract patterns (MEDIUM confidence)
- [NASA Systems Engineering Handbook](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) — hierarchical decomposition and requirements traceability in multi-domain engineering systems (MEDIUM confidence)
- [FMCW Radar DSP — Infineon application note](https://www.infineon.com/dgdl/Infineon-FMCW_RADAR_Digital_Signal_Processing_Handout-Training-v01_00-EN.pdf?fileId=8ac78c8c8929aa4d018a178075b06be9) — radar data cube model, signal processing chain structure (HIGH confidence — official documentation)
- [FPGA Implementation of CFAR for Radar Systems (MDPI Sensors 2023)](https://www.mdpi.com/1424-8220/23/2/954) — FPGA CFAR documentation conventions (MEDIUM confidence)

---
*Architecture research for: AERIS-10 PLFM Radar documentation set*
*Researched: 2026-03-13*
