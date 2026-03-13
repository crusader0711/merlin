# FPGA Board -- Xilinx Artix-7 XC7A100T

**Purpose:** Document the FPGA digital processing platform, including clock domain architecture, CDC synchronizers, resource capacity, Verilog module inventory, and constraint file summary.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [System Overview](01_system_overview.md) -- clock domain overview and system block diagram

---

## 1. Overview

The Xilinx Artix-7 XC7A100T FPGA is the central digital processing platform for the AERIS-10 radar system. It receives 8-bit digitized IF samples from the AD9484 ADC at $f_s$ (see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga)) via an LVDS interface and processes them through the following pipeline:

1. **LVDS-to-CMOS conversion** at 400 MHz (ADC clock domain)
2. **Digital Down-Conversion (DDC)** -- NCO-based mixing from $f_\text{IF}$ to baseband
3. **CIC Decimation** -- $N_\text{CIC}$-stage CIC filter with decimation factor $D_\text{CIC}$
4. **Matched Filtering** -- multi-segment frequency-domain pulse compression using $N_\text{FFT}$-point forward and inverse FFTs
5. **Doppler Processing** -- $N_\text{Doppler}$-point FFT across $M$ chirps per beam position, applied to $N_R$ range bins
6. **USB 3.0 Output** -- FT601 interface for high-speed data transfer to the host PC

The FPGA also generates the transmit chirp waveform via a DAC interface at 120 MHz, manages the level-shifter SPI bridge between the STM32 (3.3 V) and the ADAR1000 beamformers (1.8 V), and tracks beam position state (elevation, azimuth, chirp index).

> **Note:** Detailed signal processing pipeline documentation (DDC algorithms, CIC filter analysis, matched filter design, Doppler processing) is deferred to Phase 4 (SWDOC-01). This document covers the FPGA platform architecture and structural inventory.

---

## 2. XC7A100T Resource Capacity

### 2.1 Device Resources

The Artix-7 XC7A100T provides the following on-chip resources:

| Resource | Available | Symbol |
|----------|-----------|--------|
| Look-Up Tables (LUTs) | 63,400 | $N_\text{LUT}$ |
| Flip-Flops (FFs) | 126,800 | $N_\text{FF}$ |
| Block RAM (36 Kb each) | 135 | $N_\text{BRAM}$ |
| DSP48E1 Slices | 240 | $N_\text{DSP}$ |
| Global Clock Buffers (BUFG) | 32 | -- |
| MMCM/PLL | 6 | -- |
| I/O Pins | 300 | -- |

Symbols are defined in the [Symbol Table -- Hardware and Power](../00_notation/symbol_table.md#hardware-and-power).

### 2.2 Resource Utilization

**Status:** Actual FPGA resource utilization requires Vivado implementation reports, which are not currently available in the repository. This is a known blocker documented in [STATE.md](../.planning/STATE.md).

Theoretical per-module estimates based on Verilog module parameters:

| Module | Est. LUTs | Est. DSPs | Est. BRAMs | Notes |
|--------|-----------|-----------|------------|-------|
| DDC (NCO + mixer) | ~500 | 4 | 0 | 16-bit NCO, 8x16 multiply |
| CIC decimator (5-stage, 4x) | ~200 | 0 | 0 | Integrators + combs |
| FIR lowpass (32-tap) | ~300 | 32 | 0 | Parallel multiply-accumulate |
| FFT 1024-pt forward | ~4,000 | 16 | 20 | Radix-2 butterfly, twiddle ROM |
| FFT 1024-pt inverse | ~4,000 | 16 | 20 | Same architecture |
| Matched filter (multi-segment) | ~2,000 | 8 | 30 | Chirp reference storage |
| Doppler processor (32-pt FFT) | ~2,000 | 8 | 10 | 64 range bins, windowing |
| USB data interface | ~1,000 | 0 | 4 | FIFO buffering |
| Chirp controller + transmitter | ~1,500 | 4 | 15 | Chirp LUT memory |
| Other (ADC, DAC, CDC, level shifter) | ~1,000 | 0 | 2 | Interfaces |
| **Estimated Total** | **~16,500** | **~88** | **~101** | |
| **Utilization %** | **~26%** | **~37%** | **~75%** | |

> These estimates are approximate. Actual utilization will differ based on synthesis optimizations, routing congestion, and Vivado tool decisions. BRAM usage is the most likely bottleneck due to FFT twiddle factor storage and chirp reference memories.

### 2.3 BUFG Usage

The constraint file and top module instantiate three global clock buffers:

| BUFG Instance | Clock Signal | Frequency | Source |
|---------------|-------------|-----------|--------|
| `bufg_100m` | `clk_100m` | 100 MHz | AD9523 OUT6 |
| `bufg_120m` | `clk_120m_dac` | 120 MHz | AD9523 OUT10/OUT11 |
| `bufg_ft601` | `ft601_clk_in` | 100 MHz | FT601 IC (external) |

The 400 MHz ADC clock (`adc_dco_p/n`) enters the FPGA via dedicated LVDS input buffers and is handled within the ADC interface module rather than through a BUFG.

---

## 3. Clock Domains

The FPGA operates in four clock domains, all derived from the AD9523 clock distribution IC except the FT601 interface clock. See [`01_system_overview.md` Section 4](01_system_overview.md#4-clock-domain-overview) for the clock generation equations Eq. (HW-SYS-1) through Eq. (HW-SYS-3).

### 3.1 400 MHz ADC Domain

$$
f_\text{ADC} = \frac{f_\text{VCO}}{D_\text{ADC}} = \frac{3.6~\text{GHz}}{9} = 400~\text{MHz} \tag{HW-FPGA-1}
$$

- **Source:** AD9523 OUT4/OUT5 (LVDS, 7 mA drive)
- **FPGA entry:** Differential LVDS input `adc_dco_p` / `adc_dco_n`
- **I/O standard:** LVDS_25 with on-chip differential termination (`DIFF_TERM TRUE`)
- **Modules:** `ad9484_interface_400m`, `lvds_to_cmos_400m`, `ddc_400m_enhanced` (front-end mixer at 400 MHz)
- **Constraint:** `create_clock -name adc_dco_p -period 2.5 [get_ports {adc_dco_p}]`

### 3.2 120 MHz DAC Domain

$$
f_\text{DAC} = \frac{f_\text{VCO}}{D_\text{DAC}} = \frac{3.6~\text{GHz}}{30} = 120~\text{MHz} \tag{HW-FPGA-2}
$$

- **Source:** AD9523 OUT10/OUT11 (LVCMOS)
- **FPGA entry:** Single-ended LVCMOS33 input `clk_120m_dac`
- **Modules:** `radar_transmitter` (DAC output path), `dac_interface_single`
- **Constraint:** `create_clock -name clk_120m_dac -period 8.333 [get_ports {clk_120m_dac}]`

### 3.3 100 MHz System/Processing Domain

$$
f_\text{sys} = \frac{f_\text{VCO}}{D_\text{sys}} = \frac{3.6~\text{GHz}}{36} = 100~\text{MHz} \tag{HW-FPGA-3}
$$

- **Source:** AD9523 OUT6 (LVCMOS)
- **FPGA entry:** Single-ended LVCMOS input `clk_100m`
- **Modules:** All signal processing after CDC (CIC, matched filter, FFT, Doppler, CFAR), USB data interface, system status monitoring
- **Constraint:** `create_clock -name clk_100m -period 10.0 [get_ports {clk_100m}]`

This is the primary processing domain. The DDC module (`ddc_400m_enhanced`) bridges between the 400 MHz ADC domain and the 100 MHz processing domain internally, outputting 18-bit baseband I/Q samples at the decimated rate.

### 3.4 100 MHz FT601 Domain

- **Source:** FT601 USB 3.0 IC (external oscillator, not from AD9523)
- **FPGA entry:** Single-ended input `ft601_clk_in`
- **Modules:** `usb_data_interface`, `usb_packet_analyzer`
- **Constraint:** `create_clock -name ft601_clk_in -period 10.0 [get_ports {ft601_clk_in}]`

Although nominally 100 MHz (same as the system clock), this clock is asynchronous to `clk_100m` because it originates from a separate oscillator on the FT601 IC. The constraint file defines a multicycle path exception between these domains:

```
set_multicycle_path -setup 2 -from [get_clocks clk_100m] -to [get_clocks ft601_clk_in]
set_multicycle_path -hold 1 -from [get_clocks clk_100m] -to [get_clocks ft601_clk_in]
```

### 3.5 Clock Domain Summary

| Domain | Frequency | Source | I/O Standard | FPGA Signal | Key Modules |
|--------|-----------|--------|-------------|-------------|-------------|
| ADC | 400 MHz | AD9523 OUT4/5 | LVDS_25 | `adc_dco_p/n` | ADC interface, DDC front-end |
| DAC | 120 MHz | AD9523 OUT10/11 | LVCMOS33 | `clk_120m_dac` | Chirp TX, DAC interface |
| System | 100 MHz | AD9523 OUT6 | LVCMOS | `clk_100m` | CIC, matched filter, FFT, Doppler |
| FT601 | 100 MHz | FT601 IC | LVCMOS33 | `ft601_clk_in` | USB data, packet analyzer |

---

## 4. CDC Synchronizers

Cross-domain data transfer between asynchronous clock domains requires clock domain crossing (CDC) synchronizers to prevent metastability. The design implements three CDC module types in `cdc_modules.v`.

### 4.1 Multi-Bit CDC with Gray Encoding

**Module:** `cdc_adc_to_processing`
**Parameters:** `WIDTH = 8`, `STAGES = 3`
**Used for:** ADC data transfer from 400 MHz to 100 MHz domain

This module implements a Gray-coded multi-bit synchronizer:

1. **Source domain (400 MHz):** Data is registered and a 2-bit toggle counter increments on each valid sample
2. **Gray encoding:** Binary data is converted to Gray code at the domain boundary via $G = B \oplus (B \gg 1)$
3. **Synchronization chain:** 3-stage flip-flop chain in the destination domain for both data and toggle signals
4. **Destination domain (100 MHz):** Gray-to-binary conversion, new-data detection via toggle change

The 3-stage synchronizer provides metastability protection. The mean time between failures (MTBF) due to metastability for a synchronizer with $S$ stages is approximately:

$$
\text{MTBF} = \frac{e^{S \cdot t_\text{res} / \tau}}{f_\text{dst} \cdot f_\text{src} \cdot T_w} \tag{HW-FPGA-4}
$$

where $f_\text{dst}$ is the destination clock frequency, $f_\text{src}$ is the source clock frequency, $T_w$ is the metastability window, $t_\text{res}$ is the resolution time per stage, and $\tau$ is the metastability time constant. For Artix-7 with $S = 3$ stages, the MTBF is typically on the order of thousands of years at these clock frequencies.

### 4.2 Single-Bit CDC

**Module:** `cdc_single_bit`
**Parameters:** `STAGES = 3`
**Used for:** Control signals crossing between clock domains

A simple shift-register synchronizer: the source signal is clocked through a 3-stage flip-flop chain in the destination domain. The output is the delayed, metastability-safe version of the input.

### 4.3 Handshake-Based CDC

**Module:** `cdc_handshake`
**Parameters:** `WIDTH = 32`
**Used for:** Wide data transfers with flow control (e.g., system-to-FT601 domain)

This module implements a full request/acknowledge handshake protocol:

1. **Source** registers data and asserts `src_busy`
2. **Destination** synchronizes the busy signal (2-stage chain), captures data, asserts `dst_ack`
3. **Source** synchronizes the ack signal (2-stage chain), clears busy
4. **Destination** clears ack when busy deasserts

This provides reliable multi-bit transfer with backpressure via `src_ready` and `dst_ready` signals, at the cost of reduced throughput (one transfer per ~4 destination clock cycles).

### 4.4 CDC Crossing Points

| Crossing | From | To | Module | Width |
|----------|------|----|--------|-------|
| ADC data | 400 MHz ADC | 100 MHz system | `cdc_adc_to_processing` | 8-bit |
| STM32 control signals | Asynchronous GPIO | 100 MHz system | `cdc_single_bit` | 1-bit each |
| Processing to USB | 100 MHz system | 100 MHz FT601 | `cdc_handshake` | 32-bit |

The STM32 control signals (`stm32_new_chirp`, `stm32_new_elevation`, `stm32_new_azimuth`, `stm32_mixers_enable`) are declared as false paths in the constraint file (`set_false_path -from [get_ports {stm32_new_*}]`) since they are toggle-based signals synchronized by edge detectors in the FPGA.

---

## 5. FPGA Module Inventory

The following table lists all synthesizable Verilog modules in `9_Firmware/9_2_FPGA/`. This is a structural inventory; detailed signal processing documentation is in Phase 4 (SWDOC-01).

| Module | File | Clock Domain | Function | Key Parameters |
|--------|------|-------------|----------|----------------|
| `radar_system_top` | `radar_system_top.v` | All | Top-level integration: TX, RX, USB | `USE_LONG_CHIRP`, `DOPPLER_ENABLE`, `USB_ENABLE` |
| `radar_transmitter` | `radar_transmitter.v` | 100 MHz, 120 MHz | Chirp waveform generation and TX control | -- |
| `radar_receiver_final` | `radar_receiver_final.v` | 100 MHz | Receiver pipeline integration | -- |
| `plfm_chirp_controller_enhanced` | `plfm_chirp_controller.v` | 100 MHz | PLFM chirp sequence state machine | -- |
| `chirp_memory_loader_param` | `chirp_memory_loader_param.v` | 100 MHz | Loads chirp I/Q from `.mem` files | Long: 3 segments, Short: 1 segment |
| `dac_interface_single` | `dac_interface_single.v` | 120 MHz | 8-bit DAC output with clock forwarding | -- |
| `ad9484_interface_400m` | `ad9484_interface_400m.v` | 400 MHz | ADC LVDS deserializer | 8-bit data width |
| `lvds_to_cmos_400m` | `lvds_to_cmos_400m.v` | 400 MHz | LVDS-to-single-ended conversion | 8-bit |
| `ddc_400m_enhanced` | `ddc_400m.v` | 400 MHz, 100 MHz | DDC: NCO mixing + filtering | `NCO_WIDTH = 16`, `ADC_WIDTH = 8` |
| `ddc_input_interface` | `ddc_input_interface.v` | 400 MHz | ADC data routing to DDC | -- |
| `nco_400m_enhanced` | `nco_400m_enhanced.v` | 400 MHz | Numerically controlled oscillator | 16-bit phase accumulator |
| `cic_decimator_4x_enhanced` | `cic_decimator_4x_enhanced.v` | 100 MHz | CIC decimation filter | `STAGES = 5`, `DECIMATION = 4`, `COMB_DELAY = 1` |
| `fir_lowpass_parallel_enhanced` | `fir_lowpass.v` | 100 MHz | FIR lowpass (CIC droop compensation) | `TAPS = 32`, `COEFF_WIDTH = 18` |
| `matched_filter_multi_segment` | `matched_filter_multi_segment.v` | 100 MHz | Multi-segment matched filter | Long: 3000 samples, Short: 50 samples |
| `frequency_matched_filter` | `frequency_matched_filter.v` | 100 MHz | Frequency-domain matched filter core | -- |
| `fft_1024_forward_enhanced` | `fft_1024_forward.v` | 100 MHz | 1024-point forward FFT | Radix-2 DIT |
| `fft_1024_inverse_enhanced` | `fft_1024_inverse.v` | 100 MHz | 1024-point inverse FFT | Radix-2 DIT |
| `doppler_processor_optimized` | `doppler_processor.v` | 100 MHz | Doppler FFT + range-Doppler map | `DOPPLER_FFT_SIZE = 32`, `RANGE_BINS = 64`, `CHIRPS_PER_FRAME = 32` |
| `latency_buffer_2159` | `latency_buffer_2159.v` | 100 MHz | Pipeline delay buffer | `LATENCY = 3187`, `DATA_WIDTH = 32` |
| `edge_detector_enhanced` | `edge_detector.v` | 100 MHz | Toggle-to-pulse edge detector | -- |
| `level_shifter_interface` | `level_shifter_interface.v` | 100 MHz | SPI level shifting (3.3 V to 1.8 V) | STM32 to ADAR1000 |
| `usb_data_interface` | `usb_data_interface.v` | 100 MHz, FT601 | FT601 USB 3.0 data transfer | 32-bit data bus |
| `usb_packet_analyzer` | `usb_packet_analyzer.v` | FT601 | USB packet framing and analysis | -- |
| `cdc_adc_to_processing` | `cdc_modules.v` | 400 MHz -> 100 MHz | Multi-bit Gray-coded CDC | `WIDTH = 8`, `STAGES = 3` |
| `cdc_single_bit` | `cdc_modules.v` | Any -> Any | Single-bit synchronizer | `STAGES = 3` |
| `cdc_handshake` | `cdc_modules.v` | Any -> Any | Handshake-based wide CDC | `WIDTH = 32` |

**Testbench (not synthesized):**

| Module | File | Description |
|--------|------|-------------|
| `radar_system_tb` | `radar_system_tb.v` | System-level simulation testbench |

**Memory initialization files** (loaded by `chirp_memory_loader_param`):

| File | Content |
|------|---------|
| `long_chirp_seg0_i.mem`, `long_chirp_seg0_q.mem` | Long chirp segment 0 (I/Q) |
| `long_chirp_seg1_i.mem`, `long_chirp_seg1_q.mem` | Long chirp segment 1 (I/Q) |
| `long_chirp_seg2_i.mem`, `long_chirp_seg2_q.mem` | Long chirp segment 2 (I/Q) |
| `short_chirp_i.mem`, `short_chirp_q.mem` | Short chirp (I/Q) |

---

## 6. Constraint File Summary

The constraint file `cntrt.xdc` defines timing, I/O standards, and pin assignments for the XC7A100T.

### 6.1 Clock Definitions

| Clock Name | Period | Frequency | Port | Jitter |
|------------|--------|-----------|------|--------|
| `clk_100m` | 10.0 ns | 100 MHz | `clk_100m` | 0.1 ns |
| `clk_120m_dac` | 8.333 ns | 120 MHz | `clk_120m_dac` | 0.1 ns |
| `ft601_clk_in` | 10.0 ns | 100 MHz | `ft601_clk_in` | 0.1 ns |
| `adc_dco_p` | 2.5 ns | 400 MHz | `adc_dco_p` | 0.05 ns |

### 6.2 I/O Standards

| Interface | I/O Standard | Notes |
|-----------|-------------|-------|
| ADC data (`adc_d_p/n`) | LVDS_25 | With on-chip differential termination |
| ADC clock (`adc_dco_p/n`) | LVDS_25 | With on-chip differential termination |
| DAC data/control | LVCMOS33 | Fast slew rate, 8 mA drive |
| ADAR1000 (3.3 V side) | LVCMOS33 | STM32 SPI signals |
| ADAR1000 (1.8 V side) | LVCMOS18 | ADAR1000 SPI signals |
| FT601 data/control | LVCMOS33 | 32-bit bidirectional data bus |
| STM32 control signals | LVCMOS33 | `stm32_new_*`, `stm32_mixers_enable` |
| Status/debug outputs | LVCMOS33 | System status, Doppler debug |
| Reset | LVCMOS33 | Active-low with internal pull-up |

### 6.3 Key Timing Constraints

**ADC input delay:**
- Max input delay: 1.0 ns relative to `adc_dco_p`
- Min input delay: 0.2 ns relative to `adc_dco_p`

**FT601 output delay:**
- Max output delay: 2.0 ns relative to `ft601_clk_in`
- Min output delay: 0.5 ns relative to `ft601_clk_in`

**False paths:** STM32 toggle-based control signals (`stm32_new_chirp`, `stm32_new_elevation`, `stm32_new_azimuth`, `stm32_mixers_enable`) are declared as false paths since they are asynchronous inputs synchronized by edge detectors.

### 6.4 Physical Constraints

- Unused pins are configured with pull-up resistors (`BITSTREAM.CONFIG.UNUSEDPIN Pullup`)
- FT601 interface pins are grouped in the same I/O bank for signal integrity
- Pin numbers are parameterized as `[PIN_NUMBER]` placeholders in the constraint template

---

## 7. Signal Processing Pipeline Data Flow

The complete data path through the FPGA can be expressed as a cascade of processing stages with associated data widths and rates. The decimated output rate after CIC filtering is:

$$
f_\text{out} = \frac{f_s}{D_\text{CIC}} \tag{HW-FPGA-5}
$$

The total pipeline depth from ADC input to Doppler output involves:

$$
N_\text{pipeline} = N_\text{CDC} + N_\text{DDC} + N_\text{CIC} + N_\text{MF} + N_\text{Doppler} \tag{HW-FPGA-6}
$$

where each term represents the latency contribution of that processing stage in clock cycles. Detailed latency analysis is deferred to [`07_timing_budget.md`](07_timing_budget.md) (HDWR-07).

The processing chain data widths grow through the pipeline:

| Stage | Input Width | Output Width | Rate |
|-------|------------|-------------|------|
| ADC | 8-bit | 8-bit | 400 MSPS |
| DDC (NCO + mixer) | 8-bit | 18-bit I/Q | 400 MHz |
| CIC decimator | 18-bit | 18-bit | 100 MSPS |
| FIR compensation | 18-bit | 18-bit | 100 MSPS |
| Matched filter (FFT) | 18-bit | 32-bit (16+16 I/Q) | Burst |
| Doppler FFT | 16-bit I/Q | 32-bit (16+16 I/Q) | Burst |
| USB output | 32-bit | 32-bit | 100 MHz (FT601) |

---

## 8. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- authoritative symbol definitions ($N_\text{LUT}$, $N_\text{FF}$, $N_\text{BRAM}$, $N_\text{DSP}$)
- [Parameter Table](../00_notation/parameter_table.md) -- FPGA signal processing parameters ($f_s$, $N_\text{CIC}$, $D_\text{CIC}$, $N_\text{FFT}$, $N_\text{Doppler}$, $N_R$)
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Hardware References
- [`01_system_overview.md`](01_system_overview.md) -- clock domain overview (Eq. HW-SYS-1 through HW-SYS-3), system block diagram
- [`03_frequency_synthesis.md`](03_frequency_synthesis.md) -- AD9523 clock distribution (all FPGA clocks except FT601)

### FPGA Source
- `9_Firmware/9_2_FPGA/radar_system_top.v` -- top-level module with clock buffering and module instantiation
- `9_Firmware/9_2_FPGA/cdc_modules.v` -- CDC synchronizer implementations (Gray-coded, single-bit, handshake)
- `9_Firmware/9_2_FPGA/cntrt.xdc` -- Xilinx constraint file (clocks, I/O standards, timing exceptions)
- `9_Firmware/9_2_FPGA/doppler_processor.v` -- Doppler processing parameters
- `9_Firmware/9_2_FPGA/ddc_400m.v` -- DDC with NCO and mixer

### Component Datasheets
- XC7A100T -- Xilinx Artix-7 FPGA (DS181: Artix-7 Data Sheet)
- FT601 -- FTDI USB 3.0 to FIFO Bridge IC
- AD9484 -- 8-bit 500 MSPS ADC with LVDS output
