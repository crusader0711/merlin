# Master System Parameter Table -- AERIS-10

**Single source of truth for all numerical parameter values in the AERIS-10 radar system.**

This table provides canonical values for both the AERIS-10 Nexus (AERIS-10N, 3 km range, patch array) and AERIS-10 Extended (AERIS-10X, 20 km range, slotted waveguide with GaN PA) variants. No other document in this project may define canonical numerical values -- all derivations and analyses must reference this file.

**Related documents:**
- [Symbol Table](symbol_table.md) -- standard mathematical symbol definitions and units
- [Conventions](conventions.md) -- equation numbering, formatting rules, cross-reference format

---

## Inconsistency Resolutions

The codebase audit (see `.planning/phases/01-notation-parameter-standardization/01-RESEARCH.md`) identified four parameter inconsistencies across firmware, FPGA, GUI, and documentation sources. Each is resolved below with documented rationale.

### 1. Center Frequency: 10.5 GHz (canonical)

**Conflict:** README and the firmware wavelength constant (`wavelength = 0.02857` m, implying $f_c = c / \lambda = 3 \times 10^8 / 0.02857 \approx 10.5~\text{GHz}$) state 10.5 GHz. The GUI variable `system_frequency` defaults to `10e9` (10.0 GHz).

**Resolution:** $f_c = 10.5~\text{GHz}$ is canonical. The firmware wavelength constant is the most authoritative source because it directly affects beamforming calculations (element spacing = $\lambda/2$). The GUI default of 10.0 GHz appears to be an outdated or placeholder value.

**Action required:** Flag `system_frequency = 10e9` in `GUI_V6.py` for codebase correction to `10.5e9`.

### 2. PRF Discrepancy: Firmware PRI vs. GUI PRF

**Conflict:** Firmware defines `PRI1 = 167` $\mu\text{s}$ (implying chirp-level $f_{r,1} \approx 5988~\text{Hz}$). GUI defines `prf1 = 1000` Hz -- a factor of ~6 difference.

**Resolution:** These refer to different timing levels:
- **Firmware `PRI1 = 167` $\mu\text{s}$:** The chirp repetition interval -- the time between successive chirp transmissions within a coherent processing interval (CPI). This is the true radar PRF.
- **GUI `prf1 = 1000` Hz:** A display or processing update rate used for GUI rendering, NOT the chirp-level PRF.

Both values are documented in the parameter table below with clear labels to prevent confusion.

### 3. ADC Resolution: 8-bit (AD9484)

**Conflict:** The FPGA Verilog parameter `ADC_WIDTH = 8` in `ddc_400m.v` indicates an 8-bit data path. `STACK.md` claims "14-bit ADC."

**Resolution:** The AD9484 is an 8-bit, 500 MSPS ADC per its datasheet. The FPGA data path width (`ADC_WIDTH = 8`) confirms this. The "14-bit" claim in STACK.md is incorrect -- likely a confusion with a different ADC part number or a planned upgrade that was never implemented.

**Canonical value:** 8-bit ADC (AD9484, 500 MSPS rated, operated at 400 MSPS).

### 4. Beam Steering Range: Phase Shift vs. Steering Angle

**Conflict:** README states "+/-45 degrees" steering range. The firmware array `phase_differences[31]` contains inter-element phase shifts from $-160^\circ$ to $+160^\circ$.

**Resolution:** These describe different quantities:
- **$\Delta\phi_n$: $-160^\circ$ to $+160^\circ$** -- the inter-element phase shift applied by the ADAR1000 beamformer ICs.
- **Steering angle $\theta$** -- derived from the phase shift via $\theta = \arcsin\!\left(\frac{\Delta\phi \cdot \lambda}{2\pi d}\right)$. With $d = \lambda/2$, this gives $\theta = \arcsin\!\left(\frac{\Delta\phi}{\pi}\right)$, yielding a maximum steering angle of approximately $\pm 33^\circ$ at $\Delta\phi = \pm 160^\circ$.

The README's "+/-45 degrees" may refer to a design goal or a different calculation basis. The parameter table records the firmware phase shift range; the actual steering angle is a derived quantity documented in the antenna/beamforming section.

---

## System Parameters

### Waveform and Timing

| Parameter | Symbol | Nexus (AERIS-10N) | Extended (AERIS-10X) | Firmware Var | FPGA Param | GUI Var | Source |
|-----------|--------|-------------------|----------------------|--------------|------------|---------|--------|
| Center frequency | $f_c$ | 10.5 GHz | 10.5 GHz | -- | -- | `system_frequency` | README, firmware $\lambda$ |
| Chirp bandwidth | $B$ | TBD | TBD | -- | -- | -- | Requires ADF4382 config |
| Wavelength | $\lambda$ | 0.02857 m | 0.02857 m | `wavelength` | -- | -- | main.cpp:L1133 |
| Long chirp duration | $T_{c,1}$ | 30 $\mu\text{s}$ | 30 $\mu\text{s}$ | `T1` | `USE_LONG_CHIRP` | `chirp_duration_1` | main.cpp:L~200 |
| Short chirp duration | $T_{c,2}$ | 0.5 $\mu\text{s}$ | 0.5 $\mu\text{s}$ | `T2` | -- | `chirp_duration_2` | main.cpp:L~201 |
| Long chirp PRI | $T_{r,1}$ | 167 $\mu\text{s}$ | 167 $\mu\text{s}$ | `PRI1` | -- | -- | main.cpp:L~202 |
| Short chirp PRI | $T_{r,2}$ | 175 $\mu\text{s}$ | 175 $\mu\text{s}$ | `PRI2` | -- | -- | main.cpp:L~203 |
| Guard time | $T_\text{guard}$ | 175.4 $\mu\text{s}$ | 175.4 $\mu\text{s}$ | `Guard` | -- | -- | main.cpp:L~204 |
| Chirps per position | $M$ | 32 | 32 | `m_max` | `CHIRPS_PER_FRAME` | `chirps_per_position` | main.cpp, doppler_processor.v |
| Elevation positions | $N_\text{el}$ | 31 | 31 | `n_max` | -- | -- | main.cpp |
| Azimuth positions | $N_\text{az}$ | 50 | 50 | `y_max` | -- | -- | main.cpp |

### Antenna and Beamforming

| Parameter | Symbol | Nexus (AERIS-10N) | Extended (AERIS-10X) | Firmware Var | FPGA Param | GUI Var | Source |
|-----------|--------|-------------------|----------------------|--------------|------------|---------|--------|
| Array elements | $N$ | 16 (8x2 subarrays) | 16 (cascaded) | -- | -- | -- | README |
| Element spacing | $d$ | $\lambda/2$ (~14.3 mm) | $\lambda/2$ | `element_spacing` | -- | -- | main.cpp:L1134 |
| Antenna type | -- | 8x16 patch array | 32x16 slotted waveguide | -- | -- | -- | README |
| Phase shift range | $\Delta\phi_n$ | $-160^\circ$ to $+160^\circ$ | $-160^\circ$ to $+160^\circ$ | `phase_differences[31]` | -- | -- | main.cpp |
| ADAR1000 units | -- | 4 | 4 | -- | -- | -- | README |

### RF Front-End

| Parameter | Symbol | Nexus (AERIS-10N) | Extended (AERIS-10X) | Firmware Var | FPGA Param | GUI Var | Source |
|-----------|--------|-------------------|----------------------|--------------|------------|---------|--------|
| Output power/element | $P_t$ | ~1 W (ADTR1107) | 10 W (QPA2962 GaN) | -- | -- | -- | README |
| LNA noise figure | $F_\text{LNA}$ | TBD (ADTR1107 datasheet) | TBD | -- | -- | -- | Datasheet needed |
| Mixer | -- | LT5552 | LT5552 | -- | -- | -- | README |
| ADC | -- | AD9484 (8-bit, 500 MSPS) | AD9484 (8-bit, 500 MSPS) | -- | -- | -- | Datasheet |

### Signal Processing (FPGA)

| Parameter | Symbol | Nexus (AERIS-10N) | Extended (AERIS-10X) | Firmware Var | FPGA Param | GUI Var | Source |
|-----------|--------|-------------------|----------------------|--------------|------------|---------|--------|
| ADC sample rate | $f_s$ | 400 MHz | 400 MHz | -- | `FS` | -- | ddc_400m.v |
| IF frequency | $f_\text{IF}$ | 120 MHz | 120 MHz | `IF_freq` | `IF_FREQ` | -- | main.cpp, ddc_400m.v |
| ADC data width | -- | 8 bits | 8 bits | -- | `ADC_WIDTH` | -- | ddc_400m.v |
| NCO width | -- | 16 bits | 16 bits | -- | `NCO_WIDTH` | -- | ddc_400m.v |
| CIC stages | $N_\text{CIC}$ | 5 | 5 | -- | `STAGES` | -- | cic_decimator.v |
| CIC decimation | $D_\text{CIC}$ | 4 | 4 | -- | `DECIMATION` | -- | cic_decimator.v |
| FFT/buffer size | $N_\text{FFT}$ | 1024 | 1024 | -- | `BUFFER_SIZE` | -- | matched_filter.v |
| Doppler FFT size | $N_\text{Doppler}$ | 32 | 32 | -- | `DOPPLER_FFT_SIZE` | -- | doppler_processor.v |
| Range bins | $N_R$ | 64 | 64 | -- | `RANGE_BINS` | -- | doppler_processor.v |
| Long chirp samples | -- | 3000 | 3000 | -- | `LONG_CHIRP_SAMPLES` | -- | matched_filter.v |
| Short chirp samples | -- | 50 | 50 | -- | `SHORT_CHIRP_SAMPLES` | -- | matched_filter.v |

### Frequency Synthesis

| Parameter | Symbol | Nexus (AERIS-10N) | Extended (AERIS-10X) | Firmware Var | FPGA Param | GUI Var | Source |
|-----------|--------|-------------------|----------------------|--------------|------------|---------|--------|
| Clock reference | -- | 100 MHz (AD9523-1) | 100 MHz (AD9523-1) | -- | -- | -- | README |
| Synthesizers | -- | 2x ADF4382 (TX/RX LO) | 2x ADF4382 | -- | -- | -- | README |

### FPGA Clock Domains

| Parameter | Symbol | Nexus (AERIS-10N) | Extended (AERIS-10X) | Firmware Var | FPGA Param | GUI Var | Source |
|-----------|--------|-------------------|----------------------|--------------|------------|---------|--------|
| ADC clock | -- | 400 MHz | 400 MHz | -- | -- | -- | ARCHITECTURE.md |
| DAC clock | -- | 120 MHz | 120 MHz | -- | `clk_120m_dac` | -- | dac_interface_single.v |
| System clock | -- | 100 MHz | 100 MHz | -- | -- | -- | ARCHITECTURE.md |

### System-Level (Derived/TBD)

| Parameter | Symbol | Nexus (AERIS-10N) | Extended (AERIS-10X) | Firmware Var | FPGA Param | GUI Var | Source |
|-----------|--------|-------------------|----------------------|--------------|------------|---------|--------|
| Max detection range | $R_\text{max}$ | 3 km | 20 km | -- | -- | `max_distance` (50 km display) | README |
| Stepper steps/rev | -- | 200 | 200 | `Stepper_steps` | -- | -- | main.cpp |
| Magnetic declination | -- | $-0.61^\circ$ | $-0.61^\circ$ | `Mag_Declination` | -- | -- | main.cpp |
| GUI PRF long | -- | -- | -- | -- | -- | `prf1` = 1000 Hz | GUI_V6.py (display rate, NOT chirp PRF) |
| GUI PRF short | -- | -- | -- | -- | -- | `prf2` = 2000 Hz | GUI_V6.py (display rate) |

---

## TBD Tracking

The following parameters have unknown or unverified values. Each is annotated with the downstream phase that requires its resolution.

| Parameter | Symbol | What Is Needed | Required Before |
|-----------|--------|----------------|-----------------|
| Chirp bandwidth | $B$ | ADF4382 configuration analysis or chirp LUT examination to determine sweep range | Phase 2 (Physics derivations need $B$ for range resolution $\Delta R = c / 2B$) |
| LNA noise figure (Nexus) | $F_\text{LNA}$ | ADTR1107 datasheet lookup (integrated T/R module NF) | Phase 2 (Radar range equation requires noise figure chain) |
| LNA noise figure (Extended) | $F_\text{LNA}$ | QPA2962 + external LNA datasheet analysis | Phase 2 (Radar range equation) |
| Nexus antenna gain | $G$ | 8x16 patch array gain calculation or measurement data | Phase 2 (Link budget requires antenna gain) |
| Extended antenna gain | $G$ | 32x16 slotted waveguide array analysis or measurement data | Phase 2 (Link budget) |
| Extended noise figure chain | $F$ | Full receive chain NF analysis for GaN variant | Phase 3 (Hardware documentation of RF chain) |

---

## Footer

All parameter values must be updated in THIS file only. No other document may define canonical numerical values. If a discrepancy is found between this table and a source file (firmware, FPGA, GUI, or datasheet), update this table with the corrected value and document the resolution in the Inconsistency Resolutions section above.

When referencing parameter values in derivations or analysis documents, use symbolic notation (e.g., $f_c$, $T_{c,1}$, $M$) and link to this file for the numerical value. Keep derivations general; substitute specific numbers only in worked examples that explicitly reference this table.
