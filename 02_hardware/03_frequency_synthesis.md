# Frequency Synthesis Subsystem

**Purpose:** Document the AERIS-10 frequency synthesis architecture -- the AD9523-1 clock distribution IC (complete 12-output clock tree), the ADF4382 TX/RX local oscillator synthesizers, and the OCXO warm-up requirement -- with register maps, initialization sequences, and cross-references to the RF front-end and system overview.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules

---

## 1. Overview

The AERIS-10 frequency synthesis architecture generates all system clocks and local oscillator signals from a single 100 MHz oven-controlled crystal oscillator (OCXO). The signal chain is:

1. **100 MHz OCXO** -- precision frequency reference (VCXO input to AD9523)
2. **AD9523-1** -- dual-PLL clock distribution IC with internal VCO at 3.6 GHz, providing 12 output channels through programmable integer dividers
3. **ADF4382 (x2)** -- microwave wideband synthesizers generating TX LO at $f_\text{TX}$ and RX LO at $f_\text{RX}$ (see [Parameter Table](../00_notation/parameter_table.md#frequency-synthesis) for values)

The AD9523 is the clock backbone of the entire system: it provides reference clocks to both ADF4382 synthesizers, ADC/DAC clocks to the FPGA, the system processing clock, and synchronization signals.

---

## 2. AD9523-1 Clock Generator

The AD9523-1 (Analog Devices) is a dual-PLL clock generator with 12 LVDS/LVCMOS outputs. In the AERIS-10, PLL1 is configured in bypass mode; PLL2 multiplies the 100 MHz VCXO to produce a 3.6 GHz VCO, from which all output clocks are derived via integer dividers.

### 2.1 VCO Frequency

The AD9523 PLL2 multiplies the VCXO reference to produce the internal VCO frequency:

$$
f_\text{VCO} = f_\text{VCXO} \times N_\text{PLL2} \tag{HW-FS-1}
$$

where $f_\text{VCXO}$ is the VCXO frequency and $N_\text{PLL2}$ is the PLL2 feedback divider. The PLL2 feedback divider is computed from the A and B counters:

$$
N_\text{PLL2} = 4 \times B_\text{cnt} + A_\text{cnt} \tag{HW-FS-2}
$$

From the firmware configuration in `configure_ad9523()` (`main.cpp:924--1076`):
- `pll2_ndiv_b_cnt` $= B_\text{cnt} = 9$
- `pll2_ndiv_a_cnt` $= A_\text{cnt} = 0$
- `pll2_r2_div` $= 0$ (R2 divider = 1, so PFD frequency equals VCXO frequency)

Therefore:

$$
N_\text{PLL2} = 4 \times 9 + 0 = 36 \tag{HW-FS-3}
$$

$$
f_\text{VCO} = 100~\text{MHz} \times 36 = 3.6~\text{GHz} \tag{HW-FS-4}
$$

### 2.2 Output Clock Derivation

Each AD9523 output clock is derived from the VCO by an integer channel divider $D_k$:

$$
f_{\text{out},k} = \frac{f_\text{VCO}}{D_k} \tag{HW-FS-5}
$$

### 2.3 Complete Clock Tree Table

The following table documents all 12 AD9523 output channels as configured in `configure_ad9523()` (`main.cpp:970--1029`). Channels not listed (OUT2, OUT3, OUT12, OUT13) are disabled (`output_dis = 1`, `driver_mode = TRISTATE`).

| AD9523 Output | Frequency | Divider $D_k$ | Format | Destination | FPGA Signal | Firmware Line |
|---------------|-----------|----------------|--------|-------------|-------------|---------------|
| OUT0 | 300 MHz | 12 | LVDS 7 mA | ADF4382 TX reference | -- | `main.cpp:972` |
| OUT1 | 300 MHz | 12 | LVDS 7 mA | ADF4382 RX reference | -- | `main.cpp:978` |
| OUT2 | -- | -- | Disabled | -- | -- | -- |
| OUT3 | -- | -- | Disabled | -- | -- | -- |
| OUT4 | 400 MHz | 9 | LVDS 7 mA | AD9484 ADC clock | `adc_dco_p/n` | `main.cpp:984` |
| OUT5 | 400 MHz | 9 | LVDS 7 mA | FPGA ADC clock (phase-aligned with OUT4) | `adc_dco_p/n` | `main.cpp:990` |
| OUT6 | 100 MHz | 36 | LVCMOS | FPGA system clock | `clk_100m` | `main.cpp:996` |
| OUT7 | 20 MHz | 180 | LVCMOS | FPGA test/debug clock | -- | `main.cpp:1002` |
| OUT8 | 60 MHz | 60 | LVDS 4 mA | ADF4382 TX sync (SYNCP/SYNCN) | -- | `main.cpp:1008` |
| OUT9 | 60 MHz | 60 | LVDS 4 mA | ADF4382 RX sync (SYNCP/SYNCN) | -- | `main.cpp:1014` |
| OUT10 | 120 MHz | 30 | LVCMOS | DAC clock | `clk_120m_dac` | `main.cpp:1020` |
| OUT11 | 120 MHz | 30 | LVCMOS | FPGA DAC clock (phase-aligned with OUT10) | `clk_120m_dac` | `main.cpp:1026` |
| OUT12 | -- | -- | Disabled | -- | -- | -- |
| OUT13 | -- | -- | Disabled | -- | -- | -- |

Verification: each frequency satisfies Eq. (HW-FS-5). For example, OUT4: $3600~\text{MHz} / 9 = 400~\text{MHz}$.

### 2.4 Key Register Map

The following registers are the most important for AD9523 configuration. Register definitions are from the Analog Devices no-OS driver header `ad9523.h`.

| Register | Address | Field | Description |
|----------|---------|-------|-------------|
| `SERIAL_PORT_CONFIG` | 0x000 | `SDO_ACTIVE`, `SOFT_RESET` | SPI mode and soft reset control |
| `PLL2_FEEDBACK_DIVIDER_AB` | 0x0F1 | `NDIV_A_CNT[1:0]`, `NDIV_B_CNT[5:0]` | PLL2 N divider: $N = 4B + A$ |
| `PLL2_R2_DIVIDER` | 0x0F7 | `R2_DIVIDER_VAL[4:0]` | PLL2 R2 divider (0 = divide-by-1) |
| `PLL2_CHARGE_PUMP` | 0x0F0 | `CP_CURRENT` | PLL2 charge pump current |
| `PLL2_VCO_CTRL` | 0x0F3 | `VCO_CALIBRATE`, `FORCE_VCO_MIDSCALE` | VCO calibration and control |
| `PLL2_LOOP_FILTER_CTRL` | 0x0F6 | `CPOLE1`, `RZERO`, `RPOLE2` | PLL2 loop filter component selection |
| `CHANNEL_CLOCK_DIST(ch)` | 0x192 + 3*ch | `DIV[9:0]`, `DRIVER_MODE[3:0]`, `PWR_DOWN` | Per-channel divider, output format, enable |
| `STATUS_SIGNALS` | 0x232 | `SYNC_MAN_CTRL` | Manual sync trigger |
| `READBACK_0` | 0x22C | `PLL2_LD`, `PLL1_LD` | PLL lock detect status |
| `IO_UPDATE` | 0x234 | `IO_UPDATE_EN` | Latch register writes to active config |
| `POWER_DOWN_CTRL` | 0x233 | `PLL1_PWR_DOWN`, `PLL2_PWR_DOWN`, `DIST_PWR_DOWN` | Power-down control |

### 2.5 SPI Interface

The AD9523 uses a 3-wire or 4-wire SPI interface:

| Parameter | Value | Source |
|-----------|-------|--------|
| SPI clock speed | 10 MHz | `main.cpp:1036` (`max_speed_hz`) |
| SPI mode | Mode 0 (CPOL=0, CPHA=0) | `main.cpp:1038` |
| Address width | 13 bits (12-bit address + R/W bit at bit 15) | `ad9523.h:43--46` |
| Data width | 8, 16, or 24 bits (register-dependent) | `ad9523.h:48--51` |
| R/W bit | Bit 15: 1 = read, 0 = write | `ad9523.h:43--44` |
| Multi-byte | Byte count in bits [14:13] | `ad9523.h:45` |
| STM32 peripheral | SPI4 | `main.cpp:1040` |

Register writes are buffered and take effect only after an `IO_UPDATE` strobe (register 0x234, bit 0).

### 2.6 Lock Detection and Status

PLL lock status is read from the `READBACK_0` register (0x22C):

| Bit | Field | Description |
|-----|-------|-------------|
| [0] | `PLL1_LD` | PLL1 lock detect |
| [1] | `PLL2_LD` | PLL2 lock detect |
| [5] | `STAT_VCXO` | VCXO status |
| [6] | `PLL2_FB_CLK` | PLL2 feedback clock present |
| [7] | `PLL2_REF_CLK` | PLL2 reference clock present |

VCO calibration status is available in `READBACK_1` (0x22D), bit [0] (`VCO_CALIB_IN_PROGRESS`).

The firmware calls `ad9523_status()` after setup to verify lock (`main.cpp:1065`).

### 2.7 Firmware Initialization Flow

The `configure_ad9523()` function (`main.cpp:924--1076`) follows this sequence:

1. **Initialize platform data** -- set VCXO frequency (100 MHz), PLL2 dividers ($N = 36$, $R2 = 1$), charge pump current (3500 nA), loop filter components
2. **Configure channel array** -- set divider, output format, and enable for each of the 14 channels (12 used, 2 disabled)
3. **Set SPI parameters** -- 10 MHz clock, Mode 0, STM32 SPI4
4. **Call `ad9523_init()`** -- fill default platform data values
5. **Release hardware reset** -- `AD9523_RESET_RELEASE()`, 5 ms delay
6. **Select reference** -- `AD9523_REF_SEL(true)` selects REFB (100 MHz VCXO)
7. **Call `ad9523_setup()`** -- writes all registers via SPI, performs IO update, VCO calibration, and sync
8. **Verify lock** -- `ad9523_status()` checks PLL lock indicators
9. **Manual sync** -- `ad9523_sync()` aligns all output phases

---

## 3. ADF4382 Synthesizers

The AERIS-10 uses two ADF4382A microwave wideband synthesizers (Analog Devices) to generate the TX and RX local oscillator signals. Both are configured identically except for their output frequency.

### 3.1 Frequency Configuration

| Parameter | TX Synthesizer | RX Synthesizer | Firmware Source |
|-----------|---------------|----------------|-----------------|
| Output frequency | $f_\text{TX}$ | $f_\text{RX}$ | `TX_FREQ_HZ`, `RX_FREQ_HZ` in `adf4382a_manager.h` |
| Reference clock | 300 MHz (AD9523 OUT0) | 300 MHz (AD9523 OUT1) | `REF_FREQ_HZ` in `adf4382a_manager.h` |
| Sync clock | 60 MHz (AD9523 OUT8) | 60 MHz (AD9523 OUT9) | `SYNC_CLOCK_FREQ` in `adf4382a_manager.h` |

The TX and RX LO frequencies are defined in `adf4382a_manager.h`:

```
REF_FREQ_HZ   = 300,000,000 Hz    (300 MHz from AD9523)
TX_FREQ_HZ    = 10,500,000,000 Hz (10.5 GHz)
RX_FREQ_HZ    = 10,380,000,000 Hz (10.38 GHz)
SYNC_CLOCK_FREQ = 60,000,000 Hz   (60 MHz sync clock)
```

### 3.2 IF Derivation

The intermediate frequency results from the difference between TX and RX synthesizer frequencies:

$$
f_\text{IF} = f_\text{TX} - f_\text{RX} \tag{HW-FS-6}
$$

This equation is equivalent to Eq. (HW-RF-1) in [`02_rf_frontend.md`](02_rf_frontend.md#downconversion), establishing the connection between the frequency synthesis and RF front-end subsystems. The IF frequency value is documented in the [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga) and confirmed in the firmware as `IF_freq` and in the FPGA as `IF_FREQ` in `ddc_400m.v`.

### 3.3 PLL Frequency Synthesis

The ADF4382 VCO operates in the 11.5--21.0 GHz range (ADF4382A variant, per `adf4382.h:468--469`). The output frequency is derived from the VCO via a programmable output divider:

$$
f_\text{out} = \frac{f_\text{VCO,ADF}}{2^{D_\text{clkout}}} \tag{HW-FS-7}
$$

where $D_\text{clkout}$ is the CLKOUT divider register value (0--4 for ADF4382, 0--2 for ADF4382A). The VCO frequency is set by the N divider and the reference frequency:

$$
f_\text{VCO,ADF} = f_\text{ref} \times \left( N_\text{INT} + \frac{\text{FRAC1}}{2^{25}} + \frac{\text{FRAC2}}{\text{MOD2} \times 2^{25}} \right) \tag{HW-FS-8}
$$

where $f_\text{ref}$ is the PFD frequency (reference clock after the R divider and optional doubler), $N_\text{INT}$ is the integer divider, and FRAC1/FRAC2/MOD2 provide fractional-N operation.

### 3.4 Key Register Map

The following registers control the ADF4382 frequency synthesis and are the most important for understanding the system configuration. Register definitions from `adf4382.h`.

| Register | Address | Key Fields | Bits | Description |
|----------|---------|-----------|------|-------------|
| REG0000 | 0x0000 | `SOFT_RESET`, `SDO_ACTIVE` | [0], [3] | Reset (write 0x81) and SPI 3/4-wire mode |
| REG0010 | 0x0010 | `N_INT_LSB` | [7:0] | Integer N divider, LSB |
| REG0011 | 0x0011 | `N_INT_MSB`, `CLKOUT_DIV` | [3:0], [7:5] | Integer N divider MSB, output divider |
| REG0012--0014 | 0x0012--0x0014 | `FRAC1WORD` | 24-bit | Fractional-N numerator word 1 |
| REG0015 | 0x0015 | `INT_MODE`, `PFD_POL` | [2], [1] | Integer/fractional mode, PFD polarity |
| REG001F | 0x001F | `CP_I`, `EN_BLEED` | [3:0], [4] | Charge pump current, bleed enable |
| REG0020 | 0x0020 | `R_DIV`, `EN_RDBLR`, `EN_AUTOCAL` | [5:0], [6], [7] | R divider (max 63), ref doubler, auto-cal |
| REG002B | 0x002B | `PD_ALL`, `PD_VCO`, `PD_LD` | [7], [4], [3] | Power-down controls |
| REG002D | 0x002D | `EN_LOL`, `EN_LDWIN`, `LD_O_CTRL` | [5], [4], [1:0] | Lock detect configuration |
| REG0058 | 0x0058 | `LOCKED`, `FSM_BUSY` | [0], [1] | PLL lock status (read-only) |

### 3.5 SPI Interface

| Parameter | Value | Source |
|-----------|-------|--------|
| SPI clock speed | 10 MHz | `ADF4382A_SPI_SPEED_HZ` in `adf4382a_manager.h` |
| SPI peripheral | SPI4 | `ADF4382A_SPI_DEVICE_ID = 4` |
| Transaction format | 16-bit address (MSB = R/W) + 8-bit data | `adf4382.h:460--463` |
| R/W bit | Bit 15: 1 = read, 0 = write | `ADF4382_SPI_READ_CMD = 0x8000` |
| Buffer size | 3 bytes per transaction | `ADF4382_BUFF_SIZE_BYTES = 3` |

### 3.6 Synchronization Mechanism

The two ADF4382 synthesizers must maintain a fixed phase relationship for coherent operation. Synchronization is achieved using the **timed sync** mechanism via dedicated 60 MHz sync clocks:

- **AD9523 OUT8** provides the 60 MHz sync clock to the TX ADF4382 via SYNCP/SYNCN pins
- **AD9523 OUT9** provides the 60 MHz sync clock to the RX ADF4382 via SYNCP/SYNCN pins

The firmware supports two synchronization methods (defined in `adf4382a_manager.h`):

| Method | Enum Value | Description |
|--------|-----------|-------------|
| EZ-Sync | `SYNC_METHOD_EZSYNC` | Software synchronization via SPI `SW_SYNC` bit (REG001F[7]) |
| Timed Sync | `SYNC_METHOD_TIMED` | Hardware synchronization using SYNCP/SYNCN pins with `TIMED_SYNC` bit (REG001E[5]) |

The timed sync method is preferred for production use as it provides deterministic phase alignment. The sync delay is configurable via `SYNC_DEL` (REG0031[7:5]).

### 3.7 Lock Detection

Each ADF4382 provides a lock detect output on a dedicated GPIO pin:

| Synthesizer | Lock Detect GPIO | Firmware Pin | Port |
|-------------|-----------------|--------------|------|
| TX LO | `TX_LKDET_Pin` | GPIO_PIN_4 | GPIOG |
| RX LO | `RX_LKDET_Pin` | GPIO_PIN_9 | GPIOG |

Lock status can also be read via SPI from REG0058, bit [0] (`LOCKED`). The firmware function `ADF4382A_CheckLockStatus()` reads both GPIO pins and returns the lock state of each synthesizer.

The lock detect window and count are configured via REG002C (`LDWIN_PW` and `LD_COUNT_OPWR`).

### 3.8 Phase Noise

Phase noise of the ADF4382 is critical for the AERIS-10 Doppler processing performance. Close-in phase noise sets the minimum detectable Doppler frequency shift $f_d$ and therefore the minimum detectable velocity $v$.

The phase noise power spectral density $\mathcal{L}(f_m)$ at offset $f_m$ from the carrier (defined in the [Symbol Table](../00_notation/symbol_table.md#hardware-and-power)) determines the noise floor against which Doppler returns must be detected. Datasheet specifications for the ADF4382A at 10.5 GHz output should be consulted for the actual phase noise profile.

### 3.9 Chip Enable and Phase Adjustment

Each ADF4382 has dedicated GPIO control lines:

| Function | TX GPIO | RX GPIO | Description |
|----------|---------|---------|-------------|
| Chip Enable | `TX_CE_Pin` (PG0) | `RX_CE_Pin` (PG5) | Power enable |
| Chip Select | `TX_CS_Pin` (PG1) | `RX_CS_Pin` (PG6) | SPI chip select |
| Delay Adjust | `TX_DELADJ_Pin` (PG2) | `RX_DELADJ_Pin` (PG7) | Fine phase delay PWM |
| Delay Strobe | `TX_DELSTR_Pin` (PG3) | `RX_DELSTR_Pin` (PG8) | Latch phase delay |
| Lock Detect | `TX_LKDET_Pin` (PG4) | `RX_LKDET_Pin` (PG9) | PLL lock status |

Fine phase adjustment is supported via the DELADJ/DELSTR pins with configurable duty cycle (`DELADJ_MAX_DUTY_CYCLE = 1000`) and pulse width (`DELADJ_PULSE_WIDTH_US = 10` microseconds). Maximum phase shift is `PHASE_SHIFT_MAX_PS = 10000` picoseconds.

---

## 4. OCXO Warm-Up Requirement

The AERIS-10 uses an oven-controlled crystal oscillator (OCXO) as the master frequency reference. The OCXO requires a **180-second warm-up period** before reaching frequency stability sufficient for clock synthesis.

This warm-up delay is implemented in the firmware as:

```
HAL_Delay(180000);   // main.cpp:L1237 -- 180 seconds = 3 minutes
```

This delay occurs at the beginning of the power-up sequence, **before** any clock configuration (AD9523 setup) or synthesizer initialization (ADF4382 setup). Attempting to configure the AD9523 or ADF4382 before the OCXO has stabilized will result in unreliable PLL lock and incorrect output frequencies.

> **Pitfall Warning:** This 3-minute warm-up delay is easy to overlook when analyzing system startup time. The total power-on to operational time is approximately 185--190 seconds: 180 seconds OCXO warm-up + 5--10 seconds for clock configuration, synthesizer lock, FPGA initialization, and beam calibration.

The warm-up timeline integrates into the overall power sequencing documented in [`06_power_management.md`](06_power_management.md):

$$
t_\text{startup} = t_\text{OCXO} + t_\text{clock} + t_\text{synth} + t_\text{init} \tag{HW-FS-9}
$$

where $t_\text{OCXO} = 180~\text{s}$ is the OCXO warm-up time, $t_\text{clock}$ is the AD9523 configuration time, $t_\text{synth}$ is the ADF4382 lock acquisition time (including VCO calibration), and $t_\text{init}$ covers FPGA, ADAR1000, and beam matrix initialization.

---

## 5. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- symbol definitions for $f_\text{VCO}$, $f_\text{IF}$, $\mathcal{L}(f_m)$, $t_\text{lock}$
- [Parameter Table](../00_notation/parameter_table.md) -- canonical frequency values, clock domain specifications
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Hardware Cross-References
- [`01_system_overview.md`](01_system_overview.md) -- system-level clock domain overview (Section 4), VCO frequency derivation Eq. (HW-SYS-1) through Eq. (HW-SYS-3)
- [`02_rf_frontend.md`](02_rf_frontend.md) -- LT5552 mixer LO connection, AD9484 clock source, IF frequency cross-reference Eq. (HW-RF-1)

### Firmware Sources
- `main.cpp:924--1076` -- `configure_ad9523()` function: complete AD9523 clock tree configuration
- `main.cpp:1237` -- `HAL_Delay(180000)`: OCXO warm-up delay
- `adf4382a_manager.h` -- ADF4382A frequency definitions, GPIO pin assignments, SPI configuration, sync methods
- `adf4382.h` -- ADF4382 register map (Analog Devices no-OS driver), VCO frequency ranges, PLL specifications
- `ad9523.h` -- AD9523 register map (Analog Devices no-OS driver), channel configuration structures

### Component Datasheets
- AD9523-1 -- Dual-PLL 12-output clock distribution IC ([`7_Components Datasheets and Application notes/`](../7_Components%20Datasheets%20and%20Application%20notes/))
- ADF4382A -- 62.5 MHz to 21 GHz microwave wideband synthesizer ([`7_Components Datasheets and Application notes/`](../7_Components%20Datasheets%20and%20Application%20notes/))
