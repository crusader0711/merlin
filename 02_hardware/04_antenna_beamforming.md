# Antenna Array and Beamforming Hardware

**Purpose:** Document the ADAR1000-based 16-element phased array beamforming subsystem, including register-level control, beam steering tables extracted from firmware, and array geometry for both AERIS-10 variants.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Beamforming Theory](../01_physics/03_beamforming_theory.md) -- array factor derivation, grating lobe analysis

---

## 1. Overview

The AERIS-10 antenna subsystem is a 16-element linear phased array controlled by four ADAR1000 beamformer ICs, each managing 4 channels. The STM32F746 microcontroller configures all four ADAR1000 devices via SPI1 to steer the beam across $N_\text{el} = 31$ elevation positions per azimuth step. The system supports both transmit and receive beam steering with independent phase and gain control per element.

The beamforming architecture implements the array factor $AF(\theta)$ derived in Eq. (BF-3) of [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md#array-factor) through per-element phase control on the ADAR1000 vector modulators, with quantization effects analyzed in Eq. (BF-14) of the same document.

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | Antenna type | 8x16 patch array | 32x16 slotted waveguide |
> | Antenna gain $G$ | ~20 dBi (TBD) | ~30 dBi (TBD) |
> | T/R module | ADTR1107 (integrated) | QPA2962 GaN PA + external LNA |
> | $P_t$ per element | 1 W | 10 W |

---

## 2. ADAR1000 Beamformer IC

### 2.1 Function

The ADAR1000 is an Analog Devices 4-channel X/Ku-band analog beamformer providing independent phase and gain control per channel in both transmit and receive modes. Each IC includes:

- **4 receive channels:** LNA, vector modulator (phase + gain), VGA
- **4 transmit channels:** VGA, vector modulator, PA driver
- **T/R switch control** per channel with configurable polarity
- **On-chip ADC** for temperature monitoring
- **Beam RAM** for storing up to 121 beam states (bypassable via `MEM_CTRL` register)

Four ADAR1000 units provide 16 total channels mapped to the 16 array elements. The firmware bypasses the internal beam RAM (`MEM_CTRL_BIAS_RAM_BYPASS | MEM_CTRL_BEAM_RAM_BYPASS` in `ADAR1000_Manager.cpp`) and writes phase/gain settings directly via SPI for each beam position.

### 2.2 SPI Interface

The ADAR1000 uses a 3-byte SPI transaction format on STM32 SPI1:

| Byte | Bits | Field | Description |
|------|------|-------|-------------|
| 0 | [7] | R/W | `1` = read, `0` = write |
| 0 | [6:5] | DEV_ADDR | 2-bit device hardware address (0x00--0x03) |
| 0 | [4:0] | ADDR[12:8] | Register address high bits |
| 1 | [7:0] | ADDR[7:0] | Register address low bits |
| 2 | [7:0] | DATA | Read/write data byte |

**Broadcast mode:** Setting byte 0 to `0x08` (bit [3] = 1) addresses all ADAR1000 devices on the bus simultaneously.

**Chip select mapping** (from `ADAR1000_Manager.cpp`):

| ADAR1000 Unit | CS GPIO | Elements | DEV_ADDR |
|---------------|---------|----------|----------|
| #1 | GPIOA Pin 0 | 0--3 | 0x00 |
| #2 | GPIOA Pin 1 | 4--7 | 0x01 |
| #3 | GPIOA Pin 2 | 8--11 | 0x02 |
| #4 | GPIOA Pin 3 | 12--15 | 0x03 |

The FPGA provides a level-shifter interface (`level_shifter_interface` module in `level_shifter_interface.v`) to translate the STM32 3.3 V SPI signals to the ADAR1000's 1.8 V I/O domain.

### 2.3 Key Register Map

Registers extracted from `adar1000.h`. All addresses are 13-bit; only the lower byte is shown for registers below 0x100.

#### Interface and Control Registers

| Register | Address | Description |
|----------|---------|-------------|
| `INTERFACE_CONFIG_A` | 0x000 | Soft reset (`[7]\|[0]`), LSB-first (`[6]\|[1]`), SDO active (`[4]\|[3]`) |
| `INTERFACE_CONFIG_B` | 0x001 | Interface configuration B |
| `DEV_CONFIG` | 0x002 | Device configuration |
| `SCRATCHPAD` | 0x00A | Read/write test register for SPI verification |
| `TRANSFER` | 0x00F | Transfer control |

#### Receive Channel Registers (per channel 1--4)

| Register | Addr (CH1) | Addr (CH2) | Addr (CH3) | Addr (CH4) | Description |
|----------|------------|------------|------------|------------|-------------|
| `CHx_RX_GAIN` | 0x010 | 0x011 | 0x012 | 0x013 | RX VGA gain (8-bit) |
| `CHx_RX_PHS_I` | 0x014 | 0x016 | 0x018 | 0x01A | RX phase I component (VM_I lookup) |
| `CHx_RX_PHS_Q` | 0x015 | 0x017 | 0x019 | 0x01B | RX phase Q component (VM_Q lookup) |

#### Transmit Channel Registers (per channel 1--4)

| Register | Addr (CH1) | Addr (CH2) | Addr (CH3) | Addr (CH4) | Description |
|----------|------------|------------|------------|------------|-------------|
| `CHx_TX_GAIN` | 0x01C | 0x01D | 0x01E | 0x01F | TX VGA gain (8-bit) |
| `CHx_TX_PHS_I` | 0x020 | 0x022 | 0x024 | 0x026 | TX phase I component |
| `CHx_TX_PHS_Q` | 0x021 | 0x023 | 0x025 | 0x027 | TX phase Q component |

#### Bias and Enable Registers

| Register | Address | Description |
|----------|---------|-------------|
| `LOAD_WORKING` | 0x028 | Transfer working regs to active: bit [0] = LDRX, bit [1] = LDTX |
| `PA_CH1..4_BIAS_ON` | 0x029--0x02C | PA bias voltage (on-state): 0x00 = 0 V, 0xFF = -4.8 V |
| `LNA_BIAS_ON` | 0x02D | LNA bias voltage (on-state) |
| `RX_ENABLES` | 0x02E | RX channel enables (bits [6:3] = CH1--4 enable) |
| `TX_ENABLES` | 0x02F | TX channel enables (bits [6:3] = CH1--4 enable) |
| `MISC_ENABLES` | 0x030 | Detector, bias, and T/R mode enables |
| `SW_CONTROL` | 0x031 | T/R switch: `TR_SOURCE` [2], `TX_EN` [6], `RX_EN` [5] |
| `PA_CH1..4_BIAS_OFF` | 0x046--0x049 | PA bias voltage (off-state) |
| `LNA_BIAS_OFF` | 0x04A | LNA bias voltage (off-state) |

#### ADC and Memory Registers

| Register | Address | Description |
|----------|---------|-------------|
| `ADC_CONTROL` | 0x032 | ADC clock select, enable (`0x60`), start conversion (`0x70`) |
| `ADC_OUT` | 0x033 | ADC result (temperature: $T = 0.5 \times \text{raw} - 50$ deg C) |
| `MEM_CTL` | 0x038 | RAM bypass (`[6]` beam, `[5]` bias), scan mode (`[7]`) |
| `BIAS_CURRENT_RX_LNA` | 0x034 | RX LNA bias current (nominal: 8) |
| `BIAS_CURRENT_RX` | 0x035 | RX VM+VGA bias current (nominal: VM=5, VGA=10) |
| `BIAS_CURRENT_TX` | 0x036 | TX VM+VGA bias current (firmware sets 0x2D) |
| `BIAS_CURRENT_TX_DRV` | 0x037 | TX driver bias current (firmware sets 0x06) |

#### Beam Step Registers

| Register | Address | Description |
|----------|---------|-------------|
| `TX_BEAM_STEP_START` | 0x04D | TX beam step start index |
| `TX_BEAM_STEP_STOP` | 0x04E | TX beam step stop index |
| `RX_BEAM_STEP_START` | 0x04F | RX beam step start index |
| `RX_BEAM_STEP_STOP` | 0x050 | RX beam step stop index |

### 2.4 Phase Control

The ADAR1000 uses a vector modulator with 7-bit phase resolution. Phase is set by writing I and Q components to the `CHx_PHS_I` and `CHx_PHS_Q` registers, using 128-entry lookup tables:

- **`VM_I[128]`:** In-phase component for each of 128 phase steps
- **`VM_Q[128]`:** Quadrature component for each of 128 phase steps
- **`VM_GAIN[128]`:** Gain correction per phase step

The phase step size is:

$$
\Delta\phi_\text{step} = \frac{360°}{128} = 2.8125° \tag{HW-ANT-1}
$$

To set a desired phase $\phi$ on a channel, the firmware computes the 7-bit index and writes the corresponding I/Q values from the lookup tables (`adarSetRxPhase()` / `adarSetTxPhase()` in `ADAR1000_Manager.cpp`):

```
index = phi % 128
I_reg = VM_I[index]
Q_reg = VM_Q[index]
```

After writing phase or gain registers, the `LOAD_WORKING` register must be written to transfer working registers to the active set.

### 2.5 Gain Control

Each channel has a VGA (variable gain amplifier) with 8-bit gain control. The firmware sets:
- **RX gain:** 30 (via `adarSetRxVgaGain`, `ADAR1000_Manager.cpp`)
- **TX gain:** 0x7F (maximum, via `adarSetTxVgaGain`, `ADAR1000_Manager.cpp`)

### 2.6 Fast Switch Mode

The ADAR1000Manager supports fast TX/RX switching for FMCW pulsed operation. In fast switch mode (`setFastSwitchMode(true)` in `ADAR1000_Manager.cpp`):

- Both PA and LNA supplies remain energized
- Both PA and LNA bias are held active
- Switching settling time is reduced from 50 us to 10 us
- Only the T/R switch position and ADTR1107 control signal are toggled

The `pulseTXMode()` and `pulseRXMode()` methods perform minimal-latency switching by toggling only the ADTR1107 control line, used during `executeChirpSequence()` in `main.cpp`.

---

## 3. Beam Steering Implementation

### 3.1 Phase Differences Array

The firmware defines 31 inter-element phase differences $\Delta\phi_n$ (`phase_differences[31]` in `main.cpp`) that map to 31 elevation beam positions. These values are the per-element phase increment in degrees:

| Index | $\Delta\phi_n$ (deg) | Index | $\Delta\phi_n$ (deg) | Index | $\Delta\phi_n$ (deg) |
|-------|---------------------|-------|---------------------|-------|---------------------|
| 0 | +160.000 | 11 | +13.333 | 22 | -17.778 |
| 1 | +80.000 | 12 | +12.308 | 23 | -20.000 |
| 2 | +53.333 | 13 | +11.429 | 24 | -22.857 |
| 3 | +40.000 | 14 | +10.667 | 25 | -26.667 |
| 4 | +32.000 | 15 | 0.000 | 26 | -32.000 |
| 5 | +26.667 | 16 | -10.667 | 27 | -40.000 |
| 6 | +22.857 | 17 | -11.429 | 28 | -53.333 |
| 7 | +20.000 | 18 | -12.308 | 29 | -80.000 |
| 8 | +17.778 | 19 | -13.333 | 30 | -160.000 |
| 9 | +16.000 | 20 | -14.545 | | |
| 10 | +14.545 | 21 | -16.000 | | |

Position 15 ($\Delta\phi = 0°$) is the broadside beam. The array is symmetric: positions 0--14 steer in one direction, positions 16--30 steer in the opposite direction with mirrored phase values.

### 3.2 Steering Angle Derivation

The steering angle $\theta_0$ corresponding to each inter-element phase difference $\Delta\phi_n$ is derived from the array factor steering condition Eq. (BF-5) in [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md):

$$
\theta_0 = \arcsin\!\left(\frac{\Delta\phi_n \cdot \lambda}{360° \cdot d}\right) \tag{HW-ANT-2}
$$

With $d = \lambda/2$ (see [Parameter Table](../00_notation/parameter_table.md#antenna-and-beamforming)):

$$
\theta_0 = \arcsin\!\left(\frac{\Delta\phi_n}{180°}\right) \tag{HW-ANT-3}
$$

For the extreme positions: $|\Delta\phi_n| = 160°$ yields $|\theta_0| = \arcsin(160/180) \approx \pm 62.7°$. However, the grating lobe analysis in Eq. (BF-10) of the beamforming theory shows that with $d = \lambda/2$ the safe scan range extends to approximately $\pm 33°$ before grating lobes appear (with $d/\lambda < 0.649$ providing 30% margin). The extreme steering positions approach the physical limits of the array and exhibit significant beam broadening.

### 3.3 Per-Element Phase Computation

For a given beam position with inter-element phase difference $\Delta\phi_\text{pos}$ (from `phase_differences[]`), the phase applied to element $n$ ($n = 0, 1, \ldots, 15$) is:

$$
\phi_n = n \times \Delta\phi_\text{pos} \tag{HW-ANT-4}
$$

This implements the progressive phase shift of Eq. (BF-5) in the beamforming theory. The firmware computes this in `initializeBeamMatrices()` (`main.cpp`):

```c
cumulative_phase_degrees = element * phase_diff_degrees;
```

### 3.4 Conversion to 7-Bit ADAR1000 Register Value

The per-element phase $\phi_n$ in degrees is converted to a 7-bit register value (0--127) for the ADAR1000:

$$
\text{reg}_n = \left\lfloor \frac{\phi_n \bmod 360°}{360°} \times 128 \right\rfloor \bmod 128 \tag{HW-ANT-5}
$$

This quantization introduces a maximum phase error of $\Delta\phi_\text{step}/2 = 1.40625°$ per element. The effect on sidelobe levels is analyzed in Eq. (BF-14) of [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md), which predicts worst-case sidelobe degradation to approximately -29 dB for $N = 16$ elements.

The firmware implements this conversion in `degreesTo7BitPhase()` (`main.cpp`):

```c
uint8_t phase_7bit = (uint8_t)((degrees / 360.0f) * 128.0f);
return phase_7bit % 128;
```

### 3.5 Beam Matrices

The firmware pre-computes all per-element phase settings into three data structures (`main.cpp`):

| Structure | Dimensions | Beam Positions | Phase Direction |
|-----------|------------|----------------|-----------------|
| `matrix1[15][16]` | 15 beams x 16 elements | Positions 0--14 | Positive $\Delta\phi$ |
| `vector_0[16]` | 1 beam x 16 elements | Position 15 | Broadside (all zeros) |
| `matrix2[15][16]` | 15 beams x 16 elements | Positions 16--30 | Negative $\Delta\phi$ |

Each entry is the 7-bit phase value for that element at that beam position, computed by `initializeBeamMatrices()`. During radar operation, `runRadarPulseSequence()` sends the pre-computed phase patterns to all four ADAR1000 devices via `setCustomBeamPattern16()`, which distributes 16 phase values across 4 devices x 4 channels.

### 3.6 Beam Steering Sequence

During each azimuth position, the firmware executes the following elevation scan (from `runRadarPulseSequence()` in `main.cpp`):

1. For each of the 15 positive-steering beam positions (from `matrix1`):
   - Load phase pattern to all ADAR1000 devices (TX and RX)
   - Execute chirp sequence: $M/2$ long chirps at $T_{r,1}$, guard time $T_\text{guard}$, then $M/2$ short chirps at $T_{r,2}$
   - Toggle FPGA elevation signal (`GPIOD Pin 9`)
2. Load broadside pattern (`vector_0`) and execute chirps
3. For each of the 15 negative-steering beam positions (from `matrix2`):
   - Load phase pattern and execute chirps

The chirp execution uses fast switch mode, toggling between `pulseTXMode()` and `pulseRXMode()` within each PRI.

---

## 4. 16-Element Array Geometry

### 4.1 Physical Layout

The array consists of $N = 16$ elements (see [Parameter Table](../00_notation/parameter_table.md#antenna-and-beamforming)) arranged as a uniform linear array (ULA) with inter-element spacing:

$$
d = \frac{\lambda}{2} \approx \frac{0.02857~\text{m}}{2} = 14.3~\text{mm} \tag{HW-ANT-6}
$$

where $\lambda$ is the wavelength at $f_c$ (see [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing)).

The total aperture length is:

$$
L_\text{aperture} = (N - 1) \times d = 15 \times 14.3~\text{mm} = 214.3~\text{mm} \tag{HW-ANT-7}
$$

> **Variant Note:**
> | | Nexus (AERIS-10N) | Extended (AERIS-10X) |
> |--|-------|----------|
> | Array configuration | 8x16 patch array (8x2 subarrays) | 32x16 slotted waveguide (cascaded) |
> | Element type | Printed patch | Slotted waveguide |
> | Antenna gain $G$ | ~20 dBi (TBD) | ~30 dBi (TBD) |

### 4.2 Grating Lobe Conditions

From the grating lobe analysis in Eq. (BF-10) of [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md), a grating lobe appears when:

$$
\frac{d}{\lambda} \geq \frac{1}{1 + |\sin\theta_0|} \tag{HW-ANT-8}
$$

With $d/\lambda = 0.5$, the maximum scan angle before a grating lobe enters visible space is $\theta_\text{max} = 90°$ (the first grating lobe appears at the endfire direction). More practically, for acceptable performance with controlled sidelobes, the recommended scan range from the beamforming theory is $d/\lambda < 0.649$ for the system's $\pm 33°$ scan range, providing approximately 30% margin above the half-wavelength spacing.

### 4.3 Half-Power Beamwidth

The approximate half-power beamwidth $\theta_{3\text{dB}}$ for a uniform-weighted $N$-element ULA (from Eq. (BF-8) in the beamforming theory) is:

$$
\theta_{3\text{dB}} \approx \frac{0.886 \lambda}{N d \cos\theta_0} \tag{HW-ANT-9}
$$

At broadside ($\theta_0 = 0$) with $N = 16$ and $d = \lambda/2$:

$$
\theta_{3\text{dB}} \approx \frac{0.886}{16 \times 0.5} \approx 0.111~\text{rad} \approx 6.3° \tag{HW-ANT-10}
$$

---

## 5. ADTR1107 T/R Module Integration

The ADTR1107 is an Analog Devices integrated transmit/receive front-end module (Nexus variant) that combines PA, LNA, and T/R switch in a single package. The ADAR1000Manager controls the ADTR1107 power sequencing and mode switching.

### 5.1 Power Sequence

The ADTR1107 initialization (`initializeADTR1107Sequence()` in `ADAR1000_Manager.cpp`) follows a strict sequence:

1. Enable VDD_SW (3.3 V) via `EN_P_3V3_VDD_SW` GPIO
2. Enable VSS_SW (-3.3 V) via `EN_P_3V3_SW` GPIO
3. Set CTRL_SW to RX mode initially
4. Set VGG_LNA bias to 0 V
5. Disable VDD_LNA (0 V for initial TX mode)
6. Set VGG_PA to safe negative voltage (-1.75 V, register 0x5D)
7. Enable VDD_PA (5.0 V) via three PA enable GPIOs
8. Adjust VGG_PA to operational bias (-0.245 V, register 0x0D) for target $I_{DQ,PA} = 220~\text{mA}$

### 5.2 TX/RX Mode Switching

Mode switching (`setADTR1107Mode()` in `ADAR1000_Manager.cpp`) follows safe sequencing:

**TX mode:**
1. Disable LNA power
2. Set LNA bias to off (0x00)
3. Enable PA power (5.0 V, three GPIO enables)
4. Set PA bias to operational (0x7F)
5. Set T/R switch to TX via `SW_CONTROL` register bit [2]

**RX mode:**
1. Disable PA power
2. Set PA bias to safe value (0x20)
3. Enable LNA power (3.3 V)
4. Set LNA bias to operational (0x30)
5. Set T/R switch to RX via `SW_CONTROL` register bit [2]

---

## 6. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- authoritative symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- canonical numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Physics Foundation (Phase 2)
- [`03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md) -- array factor Eq. (BF-3), steering Eq. (BF-5), grating lobes Eq. (BF-10), phase quantization Eq. (BF-14)

### Hardware References
- [`01_system_overview.md`](01_system_overview.md) -- system-level block diagram and clock domain overview
- [`03_frequency_synthesis.md`](03_frequency_synthesis.md) -- AD9523 clock distribution to ADAR1000 SPI

### Firmware Source
- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adar1000.h` -- ADAR1000 register definitions
- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADAR1000_Manager.h` -- beamformer management API
- `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADAR1000_Manager.cpp` -- beamformer implementation (SPI, phase/gain, T/R switching)
- `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` -- `phase_differences[31]`, `initializeBeamMatrices()`, `executeChirpSequence()`

### Component Datasheets
- ADAR1000 -- X/Ku-band 4-channel analog beamformer (Analog Devices)
- ADTR1107 -- 8 GHz to 16 GHz front-end T/R module (Analog Devices, Nexus variant)
- QPA2962 -- 6 GHz to 18 GHz 10 W GaN MMIC power amplifier (Qorvo, Extended variant)
