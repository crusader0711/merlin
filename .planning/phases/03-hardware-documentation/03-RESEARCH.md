# Phase 3: Hardware Documentation - Research

**Researched:** 2026-03-14
**Domain:** Hardware subsystem documentation for FMCW phased array radar (AERIS-10)
**Confidence:** HIGH

## Summary

Phase 3 documents all hardware subsystems of the AERIS-10 radar. The codebase contains rich source material: Analog Devices no-OS drivers with full register maps (ADF4382, AD9523, ADAR1000), an STM32F746 firmware (`main.cpp`, ~2400 lines) with explicit power sequencing, clock configuration, and beam steering logic, and a Verilog FPGA design (~20 modules) with three clock domains. The component datasheets directory (`7_Components Datasheets and Application notes/`) contains PDFs for ADTR1107, LT5552, AD9484, ADF4382A, ADAR1000, ADS7830, DAC5578, and supporting components. Phase 2 physics documentation (6 completed docs in `01_physics/`) provides the mathematical foundation that hardware docs must reference.

The primary challenge is extracting hardware specifications from scattered sources (datasheets, firmware constants, FPGA parameters, README) and consolidating them into a coherent documentation set. The parameter table (`00_notation/parameter_table.md`) already resolves four key inconsistencies (center frequency, PRF, ADC resolution, steering range) and serves as the single source of truth. Hardware documentation must use the `HW` equation prefix with sub-prefixes (`HW-RF-1`, `HW-PWR-1`, etc.) per conventions.md.

**Primary recommendation:** Structure hardware docs by functional subsystem (not by component BOM), use draw.io SVG for block diagrams, extract register maps and SPI sequences directly from the no-OS driver headers, and cross-reference the parameter table for all numerical values.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| HDWR-01 | System overview with master parameter table | parameter_table.md exists; system-level specs from ARCHITECTURE.md, STACK.md, and main.cpp constants |
| HDWR-02 | RF front-end (ADTR1107, LT5552, AD9484) | Datasheets in `7_Components Datasheets/`, ADTR1107 init in ADAR1000_Manager, AD9484 FPGA interface in `ad9484_interface_400m.v` |
| HDWR-03 | Frequency synthesis (ADF4382, AD9523) | Full register maps in `adf4382.h` and `ad9523.h`, clock tree config in `configure_ad9523()`, LO frequencies in `adf4382a_manager.h` |
| HDWR-04 | Antenna array & beamforming (ADAR1000) | `ADAR1000_Manager.h/cpp`, `adar1000.h`, phase_differences[31] array, beam matrix init in main.cpp |
| HDWR-05 | FPGA board (XC7A100T) | `radar_system_top.v`, `cdc_modules.v`, constraint file `cntrt.xdc`, all Verilog modules in `9_Firmware/9_2_FPGA/` |
| HDWR-06 | Power management | GPIO sequencing in main.cpp (lines 1240-1500), `systemPowerUpSequence()`, `systemPowerDownSequence()`, DAC5578/ADS7830 drivers |
| HDWR-07 | Timing budget & latency analysis | Chirp timing from main.cpp (T1, PRI1, T2, PRI2, Guard), FPGA pipeline stages identifiable from Verilog modules |
| HDWR-08 | Power budget analysis | Power rail enables in main.cpp, ADS7830 current/temp monitoring, 8 temperature sensors, PA current monitoring |
| HDWR-09 | GPS/IMU coordinate transform math | GY_85_HAL driver, complementary filter in main.cpp (lines 1280-1385), GPS_Data_t struct, quaternion/Euler in main.cpp |
</phase_requirements>

## Standard Stack

### Core (Documentation Tooling)

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| GitHub Markdown + MathJax | N/A | Document format with `\tag{HW-*}` equations | Project convention, renders natively on GitHub |
| draw.io | v24+ | Hardware block diagrams, RF signal chain, clock tree | Version-controllable XML, SVG export for GitHub |
| WaveDrom | v3+ | SPI timing diagrams, clock domain waveforms | Digital timing standard; export to SVG |
| conventions.md | N/A | `HW-` prefix equations, variant callout blocks | Mandatory per project conventions |

### Reference Sources

| Source | Location | Content |
|--------|----------|---------|
| parameter_table.md | `00_notation/parameter_table.md` | Canonical numerical values for both variants |
| symbol_table.md | `00_notation/symbol_table.md` | Authoritative symbol definitions |
| Component datasheets | `7_Components Datasheets and Application notes/` | ADTR1107, LT5552, AD9484, ADF4382A, ADAR1000, ADS7830, DAC5578 |
| No-OS driver headers | `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/` | Register maps, SPI protocols, init sequences |
| FPGA Verilog | `9_Firmware/9_2_FPGA/` | Clock domains, interface modules, CDC synchronizers |
| Firmware main.cpp | `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` | Power sequencing, initialization, beam steering |
| Existing block diagram | `2_Functional Diagram & Interconnection Matrices/RADAR_V6.drawio` | System-level block diagram (draw.io source) |
| Power management | `3_Power Management/Power Management V6.xlsx` | Voltage rails, current budgets |

## Architecture Patterns

### Recommended Document Structure

```
02_hardware/
  01_system_overview.md          # HDWR-01: Master parameter table, system block diagram
  02_rf_frontend.md              # HDWR-02: ADTR1107, LT5552, AD9484
  03_frequency_synthesis.md      # HDWR-03: ADF4382, AD9523 clock tree
  04_antenna_beamforming.md      # HDWR-04: ADAR1000, 16-element array, steering tables
  05_fpga_board.md               # HDWR-05: XC7A100T clock domains, CDC, resources
  06_power_management.md         # HDWR-06: Rail sequencing, thermal management
  07_timing_budget.md            # HDWR-07: End-to-end pipeline latency
  08_power_budget.md             # HDWR-08: Per-rail current, thermal dissipation
  09_gps_imu_transforms.md       # HDWR-09: Coordinate transform math
  figures/                       # SVG exports from draw.io and WaveDrom
```

### Pattern 1: Document Template (per conventions.md)

Every hardware document follows the project template:

```markdown
# [Subsystem Name]

**Purpose:** [One sentence]

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md)
- [Parameter Table](../00_notation/parameter_table.md)
- [Conventions](../00_notation/conventions.md)

---

## 1. Overview
[Block diagram, functional description]

## 2. Key Specifications
[Table referencing parameter_table.md for values]

## 3. Register Map / SPI Sequences
[Extracted from driver headers]

## 4. Interface Details
[Pin assignments, clock domains, voltage levels]

> **Variant Note:**
> | | Nexus | Extended |
> |--|-------|----------|
> | [differing parameter] | [value] | [value] |

---

## References
- [Symbol Table](../00_notation/symbol_table.md)
- [Parameter Table](../00_notation/parameter_table.md)
- [Datasheet name and URL/path]
```

### Pattern 2: Register Map Documentation

Extract register definitions directly from the no-OS driver headers. Present as structured tables.

```markdown
### ADF4382 Key Registers

| Register | Address | Field | Bits | Description | Default |
|----------|---------|-------|------|-------------|---------|
| REG0000 | 0x0000 | SOFT_RESET | [0] | Software reset (write 0x81) | 0 |
| REG0000 | 0x0000 | SDO_ACTIVE | [3] | SPI 3-wire/4-wire mode | 0 |
| REG0010 | 0x0010 | N_INT_LSB | [7:0] | Integer divider LSB | -- |
```

### Pattern 3: Firmware Variable to Standard Symbol Mapping

Per conventions.md anti-pattern 5.4, always map firmware variable names to standard symbols:

```markdown
The long chirp duration $T_{c,1}$ (`T1` in `main.cpp:L180`) is set to $30~\mu\text{s}$
(see [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing)).
```

### Pattern 4: Clock Tree Documentation

The AD9523 clock distribution is central. Document as a structured table extracted from `configure_ad9523()` (main.cpp lines 924-1076):

| AD9523 Output | Frequency | Format | Divider | Destination | FPGA Signal |
|---------------|-----------|--------|---------|-------------|-------------|
| OUT0 | 300 MHz | LVDS 7mA | /12 | ADF4382 TX REF | -- |
| OUT1 | 300 MHz | LVDS 7mA | /12 | ADF4382 RX REF | -- |
| OUT4 | 400 MHz | LVDS 7mA | /9 | AD9484 ADC CLK | `adc_dco_p/n` |
| OUT5 | 400 MHz | LVDS 7mA | /9 | FPGA ADC CLK | `adc_dco_p/n` |
| OUT6 | 100 MHz | LVCMOS | /36 | FPGA System | `clk_100m` |
| OUT7 | 20 MHz | LVCMOS | /180 | FPGA Test | -- |
| OUT8 | 60 MHz | LVDS 4mA | /60 | ADF4382 TX SYNC | -- |
| OUT9 | 60 MHz | LVDS 4mA | /60 | ADF4382 RX SYNC | -- |
| OUT10 | 120 MHz | LVCMOS | /30 | DAC | `clk_120m_dac` |
| OUT11 | 120 MHz | LVCMOS | /30 | FPGA DAC | `clk_120m_dac` |

VCO frequency: 3.6 GHz (PLL2: 100 MHz PFD x N=36).

### Anti-Patterns to Avoid

- **Organizing by BOM instead of function:** Document by functional subsystem (RF front-end, frequency synthesis, beamforming), not by component part number list. Components appear in the subsystem where they are most relevant.
- **Inlining numerical values in derivations:** All numerical values must reference parameter_table.md. Hardware docs should use symbolic notation with the `HW-` equation prefix.
- **Duplicating physics derivations:** Hardware docs reference Eq. (FMCW-N), Eq. (BF-N) etc. from `01_physics/` -- never re-derive.
- **Presenting register maps without SPI context:** Always show the SPI transaction format (address width, data width, R/W bit position) alongside register tables.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Register map extraction | Manual transcription from datasheets | Extract from `adf4382.h`, `ad9523.h`, `adar1000.h` driver headers | Headers are structured, authoritative, and already in the repo |
| Clock tree calculation | Manual frequency math | Document from `configure_ad9523()` function in main.cpp | Actual firmware config is ground truth |
| Power sequencing order | Infer from schematic | Document from `systemPowerUpSequence()` and GPIO init in main.cpp | Firmware defines the actual sequence |
| Beam steering tables | Recalculate from theory | Document `phase_differences[31]` array and `initializeBeamMatrices()` | Firmware values are what the hardware actually uses |
| Block diagrams | Build from scratch | Start from `RADAR_V6.drawio` in `2_Functional Diagram/` | Existing draw.io source is a starting point |

## Common Pitfalls

### Pitfall 1: AD9484 Resolution Confusion
**What goes wrong:** Documentation states "14-bit ADC" based on stale STACK.md entry.
**Why it happens:** STACK.md originally listed 14-bit; actual part is AD9484 (8-bit, 500 MSPS).
**How to avoid:** parameter_table.md already resolves this -- use it as source of truth. ADC_WIDTH=8 in FPGA confirms.
**Warning signs:** Any document claiming 14-bit ADC resolution.

### Pitfall 2: Confusing Phase Shift with Steering Angle
**What goes wrong:** Conflating the ADAR1000 inter-element phase shift range ($\pm 160^\circ$) with the antenna beam steering angle range.
**Why it happens:** README says "+/-45 degrees" but firmware uses phase shifts up to $\pm 160^\circ$.
**How to avoid:** parameter_table.md resolves this. Phase shift $\Delta\phi_n$ and steering angle $\theta$ are different quantities related by $\theta = \arcsin(\Delta\phi \lambda / 2\pi d)$. Maximum steering angle is approximately $\pm 33^\circ$.
**Warning signs:** Stating "+/-45 deg steering range" without derivation.

### Pitfall 3: Missing OCXO Warm-Up Requirement
**What goes wrong:** Timing documentation omits the 3-minute OCXO warm-up delay.
**Why it happens:** `HAL_Delay(180000)` at main.cpp line 1237 is easy to miss.
**How to avoid:** Document the full power-on timeline including the 180-second warm-up before any clock configuration.

### Pitfall 4: Clock Domain Mismatch in Documentation
**What goes wrong:** Stating wrong clock frequencies for FPGA domains.
**Why it happens:** Multiple clock signals with similar names.
**How to avoid:** Use the AD9523 configuration in firmware as ground truth:
- 400 MHz: ADC acquisition domain (OUT4/OUT5)
- 120 MHz: DAC output domain (OUT10/OUT11)
- 100 MHz: System/processing domain (OUT6)
- FT601 clock: 100 MHz (external from FT601 IC)

### Pitfall 5: Incomplete Power Rail Documentation
**What goes wrong:** Documenting only the enable sequence without voltage values or current limits.
**Why it happens:** main.cpp has GPIO enables but not voltage/current specs.
**How to avoid:** Cross-reference `3_Power Management/Power Management V6.xlsx` for voltage values and current limits. The firmware shows sequencing order; the spreadsheet has electrical specs.

### Pitfall 6: Variant Differences Not Called Out
**What goes wrong:** Writing as if only one variant exists.
**Why it happens:** Most firmware code is shared between Nexus and Extended.
**How to avoid:** Use the variant callout block format from conventions.md. Key differences:
- Power amplifier: ADTR1107 (1W, Nexus) vs QPA2962 GaN (10W, Extended)
- Antenna: 8x16 patch (Nexus) vs 32x16 slotted waveguide (Extended)

### Pitfall 7: Timing Budget Without Guard Time
**What goes wrong:** Computing CPI duration from chirp counts alone.
**Why it happens:** Guard time ($T_\text{guard} = 175.4~\mu\text{s}$) between long and short chirp sequences is easily overlooked.
**How to avoid:** Full chirp sequence per beam position: 32 long chirps at PRI1=167us + Guard=175.4us + 32 short chirps at PRI2=175us. Document from `executeChirpSequence()` in main.cpp.

## Code Examples

### AD9523 Clock Configuration (from main.cpp:924-1076)

Key configuration parameters extracted from firmware:

```c
// VCO = 3.6 GHz (PLL2: 100 MHz x N=36)
pdata.vcxo_freq = 100000000;     // 100 MHz VCXO
pdata.pll2_ndiv_b_cnt = 9;       // N = 4*9 + 0 = 36
pdata.pll2_r2_div = 0;           // R2 = 1

// Channel allocations (VCO / divider):
channels[0].channel_divider = 12;  // 300 MHz -> ADF4382 TX
channels[4].channel_divider = 9;   // 400 MHz -> ADC
channels[6].channel_divider = 36;  // 100 MHz -> FPGA system
channels[10].channel_divider = 30; // 120 MHz -> DAC
```

### ADF4382 Frequency Configuration (from adf4382a_manager.h)

```c
#define REF_FREQ_HZ      300000000ULL   // 300 MHz from AD9523
#define TX_FREQ_HZ       10500000000ULL // 10.5 GHz TX LO
#define RX_FREQ_HZ       10380000000ULL // 10.38 GHz RX LO
#define SYNC_CLOCK_FREQ  60000000ULL    // 60 MHz sync clock
// IF = TX - RX = 10.5 GHz - 10.38 GHz = 120 MHz (matches firmware IF_freq)
```

### Power Sequencing Order (from main.cpp:1237-1500)

```
1. Wait 180s for OCXO warm-up
2. Enable 1.8V clock rail -> 100ms delay
3. Enable 3.3V clock rail -> 100ms delay
4. Release AD9523 reset -> 100ms delay
5. Configure AD9523 via SPI (clock tree setup)
6. Enable FPGA 1.0V core -> 100ms delay
7. Enable FPGA 1.8V I/O -> 100ms delay
8. Enable FPGA 3.3V -> 100ms delay
9. Initialize IMU (GY-85 via I2C3)
10. Initialize barometer (BMP180)
11. Initialize ADF4382 TX+RX LOs, wait for lock
12. Enable ADAR1000 3.3V (pairs 1-2 and 3-4)
13. Enable ADAR1000 5.0V -> 500ms delay
14. ADTR1107 power sequence
15. Initialize all 4 ADAR1000 devices via SPI
16. System calibration
17. Initialize beam matrices (31 positions)
```

### Beam Steering Implementation (from main.cpp:238-435)

```c
// 31 elevation positions with inter-element phase shifts
const float phase_differences[31] = {
    160.0, 80.0, 53.333, 40.0, 32.0, 26.667, 22.857, 20.0,
    17.778, 16.0, 14.545, 13.333, 12.308, 11.429, 10.667, 0.0,
    -10.667, -11.429, -12.308, -13.333, -14.545, -16.0, -17.778,
    -20.0, -22.857, -26.667, -32.0, -40.0, -53.333, -80.0, -160.0
};

// Per-element phase = element_index * phase_differences[beam_pos]
// Converted to 7-bit (0-127) for ADAR1000: (degrees / 360) * 128
```

### FPGA Clock Domains (from radar_system_top.v)

```verilog
module radar_system_top (
    input wire clk_100m,          // System clock (100 MHz)
    input wire clk_120m_dac,      // DAC clock (120 MHz)
    input wire ft601_clk_in,      // FT601 interface clock (100 MHz)
    // ADC clock is implicit via adc_dco_p/n (400 MHz LVDS)
);
```

### CDC Synchronizer Pattern (from cdc_modules.v)

```verilog
module cdc_adc_to_processing #(
    parameter WIDTH = 8,
    parameter STAGES = 3    // 3-stage synchronizer for metastability
)(
    input wire src_clk,     // 400 MHz ADC domain
    input wire dst_clk,     // 100 MHz processing domain
    ...
);
// Uses Gray encoding for multi-bit CDC crossing
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 14-bit ADC assumption | 8-bit AD9484 confirmed | Phase 1 (parameter audit) | All SNR/dynamic range calculations use 8-bit |
| $f_c = 10.0$ GHz (GUI default) | $f_c = 10.5$ GHz (firmware canonical) | Phase 1 (parameter audit) | Wavelength, element spacing, all beamforming calculations |
| "+/-45 deg" steering | $\pm 33^\circ$ actual (from $\pm 160^\circ$ phase) | Phase 1 (parameter audit) | Grating lobe analysis references BF equations |

## Key Data to Extract for Each Requirement

### HDWR-01: System Overview
- Master parameter table already exists in `00_notation/parameter_table.md`
- System block diagram from `RADAR_V6.drawio`
- Two-variant summary table (Nexus vs Extended)
- Cross-reference to all subsequent hardware docs

### HDWR-02: RF Front-End
- **ADTR1107:** Integrated T/R module (LNA+PA), datasheet at `7_Components Datasheets/adtr1107.pdf`, init via `ADAR1000_Manager::initializeADTR1107Sequence()`
- **LT5552:** Mixer, datasheet at `7_Components Datasheets/LTC5552f.pdf`, up/down conversion
- **AD9484:** 8-bit 500 MSPS ADC (operated at 400 MSPS), LVDS interface in `ad9484_interface_400m.v` and `lvds_to_cmos_400m.v`
- Key specs to document: NF (from ADTR1107 datasheet -- TBD in parameter table), IP3, gain, conversion loss

### HDWR-03: Frequency Synthesis
- **AD9523-1:** Full clock tree from `configure_ad9523()` (12 outputs, VCO=3.6 GHz)
- **ADF4382:** Two instances (TX: 10.5 GHz, RX: 10.38 GHz), IF=120 MHz, REF=300 MHz
- Register maps in `adf4382.h` (extensive bit-field definitions)
- Lock detection: GPIO pins `ADF4382_TX_LKDET`, `ADF4382_RX_LKDET`
- Phase noise: requires ADF4382 datasheet analysis
- Sync mechanism: timed sync via 60 MHz clocks on SYNCP/SYNCN

### HDWR-04: Antenna Array & Beamforming
- **ADAR1000:** 4 units x 4 channels = 16 elements, SPI via STM32 SPI1
- Register map in `adar1000.h`, manager in `ADAR1000_Manager.h/cpp`
- 128-entry VM lookup tables (VM_I, VM_Q, VM_GAIN) for vector modulator
- 7-bit phase resolution (2.8125 deg/step), 128 gain levels
- Beam steering: 31 positions from `phase_differences[31]`
- Beam matrices: matrix1[15][16], matrix2[15][16], vector_0[16] (broadside)
- Fast switch mode for rapid TX/RX toggling

### HDWR-05: FPGA Board
- **XC7A100T:** 3 explicit clock domains (100/120/400 MHz) + FT601 100 MHz
- CDC: `cdc_modules.v` with Gray-coded multi-bit synchronizers, 3-stage metastability protection
- Modules: DDC, CIC decimator (5-stage, 4x), matched filter (multi-segment), 1024-pt FFT (forward+inverse), Doppler processor (32-pt FFT, 64 range bins), USB interface
- Constraint file: `cntrt.xdc` (16.6 KB -- contains pin assignments and clock constraints)
- Resource utilization: requires Vivado reports (flagged as potentially unavailable in STATE.md blockers)

### HDWR-06: Power Management
- Rail sequencing from main.cpp with explicit GPIO enables and delays
- Rails: 1.0V FPGA core, 1.8V FPGA I/O, 1.8V clock, 3.3V clock, 3.3V FPGA, 3.3V ADAR, 3.3V ADTR, 3.3V switches, 5.0V ADAR, 5.0V PA
- DAC5578: PA gate voltage control (2x 8-channel DACs via I2C)
- ADS7830: Temperature (8x on hadc3) and current monitoring (hadc1, hadc2)
- Emergency stop: `Emergency_Stop()` clears DAC outputs via hardware CLR pin
- Fan control via `EN_DIS_COOLING` GPIO
- Thermal limits: ADAR1000 temp > 85C triggers error, system temp > 75C triggers warning

### HDWR-07: Timing Budget
- Per-position chirp sequence: 16 long + 16 short chirps (m_max/2 each pattern)
- Long chirp: $T_{c,1} = 30~\mu\text{s}$, $T_{r,1} = 167~\mu\text{s}$
- Short chirp: $T_{c,2} = 0.5~\mu\text{s}$, $T_{r,2} = 175~\mu\text{s}$
- Guard: $T_\text{guard} = 175.4~\mu\text{s}$
- Total per beam position: 16 * 167 + 175.4 + 16 * 175 = 2672 + 175.4 + 2800 = 5647.4 us
- 31 elevation positions per azimuth, 50 azimuth positions per revolution
- FPGA pipeline latency: ADC -> DDC -> CIC -> matched filter -> FFT -> Doppler -> CFAR -> USB
- Stepper motor: 200 steps/rev, 50 azimuth positions = 4 steps per position, 1ms per step (500us high + 500us low)

### HDWR-08: Power Budget
- Cross-reference `3_Power Management/Power Management V6.xlsx`
- PA current monitoring via ADS7830 (16 channels for Idq)
- Temperature monitoring: 8 channels on ADS7830 (hadc3)
- Overcurrent threshold: Idq > 2.5A per PA
- Under-bias threshold: Idq < 0.1A per PA

### HDWR-09: GPS/IMU Coordinate Transform
- **GY-85 IMU:** ADXL345 accelerometer (I2C 0x53), ITG3200 gyroscope (I2C 0x68), HMC5883 magnetometer (I2C 0x1E)
- Complementary filter in main.cpp: 50/50 accel/gyro weighting
- Magnetometer calibration: 3x3 rotation matrix (M11-M33) and bias correction
- Pitch/Roll from fused accel+gyro, Yaw from tilt-compensated magnetometer with magnetic declination correction
- GPS: TinyGPS++ via UART5, provides lat/lon/alt
- Barometer: BMP180 for altitude (hypsometric formula)
- Target coordinate transform: radar-relative (range, azimuth, elevation) -> GPS-absolute coordinates using pitch/roll/yaw corrections
- Quaternion representation: `q[4]` array initialized but complementary filter uses Euler angles

## Open Questions

1. **Chirp bandwidth $B$ is TBD**
   - What we know: ADF4382 TX=10.5 GHz, RX=10.38 GHz, IF=120 MHz. Chirp LUT files exist in FPGA directory.
   - What's unclear: The actual frequency sweep range (bandwidth) applied during the chirp. It is embedded in the chirp LUT memory files and/or ADF4382 modulation configuration.
   - Recommendation: Analyze chirp LUT `.mem` files to extract the frequency sweep, or document as TBD with downstream impact noted (range resolution $\Delta R = c/2B$ depends on this).

2. **FPGA resource utilization**
   - What we know: XC7A100T has 63,400 LUTs, 126,800 FFs, 135 BRAMs, 240 DSP48E1s.
   - What's unclear: Actual utilization percentages. STATE.md flags this: "Confirm FPGA Vivado implementation reports are accessible."
   - Recommendation: If Vivado reports are not available, document the theoretical resource requirements per module and note that actual utilization is unverified.

3. **ADTR1107 noise figure**
   - What we know: ADTR1107 is an integrated T/R front-end. Datasheet is at `7_Components Datasheets/adtr1107.pdf`.
   - What's unclear: Exact NF value is listed as TBD in parameter_table.md.
   - Recommendation: Extract from datasheet during documentation. This feeds into the noise figure chain analysis (Eq. NF-* from `01_physics/05_noise_analysis.md`).

4. **Extended variant QPA2962 GaN PA details**
   - What we know: README states 10W per element with QPA2962 for Extended variant.
   - What's unclear: Firmware appears to support only ADTR1107 (Nexus). QPA2962 may be a design-stage component.
   - Recommendation: Document QPA2962 as the Extended variant specification. Use variant callout blocks throughout. Flag any firmware support gaps.

5. **CFAR variant implemented**
   - What we know: STATE.md blocker: "Identify which CFAR variant is implemented in Verilog before Phase 4."
   - What's unclear: The doppler_processor.v contains detection logic but the CFAR module structure is not yet fully examined.
   - Recommendation: Note this as relevant context for HDWR-05 FPGA documentation. Detailed CFAR analysis belongs in Phase 4 (software documentation), but the FPGA module structure should be documented here.

## Sources

### Primary (HIGH confidence)
- `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` -- power sequencing, initialization, clock config, beam steering, timing parameters
- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adf4382.h` -- ADF4382 register map (Analog Devices no-OS driver)
- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ad9523.h` -- AD9523 register map (Analog Devices no-OS driver)
- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adar1000.h` -- ADAR1000 register map
- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADAR1000_Manager.h` -- beamformer management API
- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adf4382a_manager.h` -- LO frequencies, sync configuration
- `9_Firmware/9_2_FPGA/radar_system_top.v` -- FPGA clock domains, interface signals
- `9_Firmware/9_2_FPGA/cdc_modules.v` -- CDC synchronizer implementation
- `9_Firmware/9_2_FPGA/doppler_processor.v` -- DSP parameters (FFT size, range bins)
- `00_notation/parameter_table.md` -- canonical parameter values with inconsistency resolutions
- `00_notation/conventions.md` -- equation numbering, formatting, anti-patterns
- `00_notation/symbol_table.md` -- authoritative symbol definitions
- `.planning/codebase/ARCHITECTURE.md` -- system data flow, layer descriptions
- `.planning/codebase/STACK.md` -- component inventory
- `.planning/codebase/CONCERNS.md` -- known issues, fragile areas

### Secondary (MEDIUM confidence)
- `7_Components Datasheets and Application notes/` -- component datasheets (not yet read in detail)
- `3_Power Management/Power Management V6.xlsx` -- power budget data (not yet read)
- `2_Functional Diagram & Interconnection Matrices/RADAR_V6.drawio` -- existing block diagram

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all tooling verified in Phase 1-2, project conventions established
- Architecture: HIGH -- document structure follows project patterns, source material locations confirmed
- Pitfalls: HIGH -- derived from direct codebase inspection and parameter_table.md inconsistency resolutions
- Content sources: HIGH for firmware/FPGA (direct code inspection), MEDIUM for datasheet specs (not yet extracted)

**Research date:** 2026-03-14
**Valid until:** No expiry -- hardware documentation of an existing system; source material is stable
