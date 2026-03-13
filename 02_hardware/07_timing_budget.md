# End-to-End Timing Budget

**Purpose:** Trace latency from antenna to display for the complete AERIS-10 signal processing pipeline, documenting chirp sequence timing (including guard time), full scan timing, stage-by-stage FPGA pipeline latency, and overall system responsiveness.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [FPGA Board](05_fpga_board.md) -- clock domains and module inventory
- [Frequency Synthesis](03_frequency_synthesis.md) -- clock sources and rates

---

## 1. Overview

The AERIS-10 timing budget quantifies the time required for each stage of the radar's operation, from chirp transmission through digital processing to display output. Understanding this budget is essential for:

- Computing the total scan time for a full 360-degree revolution
- Identifying processing bottlenecks in the FPGA pipeline
- Determining system responsiveness (time from target illumination to detection display)
- Verifying that processing completes within the available chirp interval

The timing budget is organized into three levels:

1. **Chirp sequence timing** -- the per-beam-position waveform schedule including guard time
2. **Full scan timing** -- the time for a complete azimuth revolution with stepper motor movement
3. **FPGA pipeline latency** -- stage-by-stage processing delay from ADC input to USB output

---

## 2. Chirp Sequence Timing

The firmware function `executeChirpSequence()` (`main.cpp:445--466`) implements the per-beam-position waveform schedule. Each beam position transmits $M$ chirps split into two subsequences separated by a guard interval.

### 2.1 Chirp Sequence Structure

For each beam position, the chirp sequence consists of:

1. **Long chirp subsequence:** $M/2$ chirps at PRI $T_{r,1}$, each with chirp duration $T_{c,1}$ (`T1` in `main.cpp`) followed by a listen interval of $T_{r,1} - T_{c,1}$
2. **Guard time:** $T_\text{guard}$ (`Guard` in `main.cpp`) -- a dead time separating the two chirp modes to allow transients to settle and prevent inter-mode interference
3. **Short chirp subsequence:** $M/2$ chirps at PRI $T_{r,2}$, each with chirp duration $T_{c,2}$ (`T2` in `main.cpp`) followed by a listen interval of $T_{r,2} - T_{c,2}$

### 2.2 Firmware Variable Mapping

| Standard Symbol | Firmware Variable | Value | Description |
|----------------|-------------------|-------|-------------|
| $M$ | `m_max` | 32 | Total chirps per beam position |
| $T_{c,1}$ | `T1` | $30~\mu\text{s}$ | Long chirp duration |
| $T_{c,2}$ | `T2` | $0.5~\mu\text{s}$ | Short chirp duration |
| $T_{r,1}$ | `PRI1` | $167~\mu\text{s}$ | Long chirp PRI |
| $T_{r,2}$ | `PRI2` | $175~\mu\text{s}$ | Short chirp PRI |
| $T_\text{guard}$ | `Guard` | $175.4~\mu\text{s}$ | Guard time between subsequences |

All values are from `main.cpp:178--184` and documented in the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing).

### 2.3 Per-Beam-Position Time

The total time for one beam position is the sum of the two chirp subsequences and the guard interval:

$$
T_\text{pos} = \frac{M}{2} \cdot T_{r,1} + T_\text{guard} + \frac{M}{2} \cdot T_{r,2} \tag{HW-TIM-1}
$$

The long chirp subsequence duration is:

$$
T_\text{long} = \frac{M}{2} \cdot T_{r,1} \tag{HW-TIM-2}
$$

The short chirp subsequence duration is:

$$
T_\text{short} = \frac{M}{2} \cdot T_{r,2} \tag{HW-TIM-3}
$$

Using the system parameters from the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing):

$$
\begin{aligned}
T_\text{long} &= 16 \times 167~\mu\text{s} = 2672~\mu\text{s} \\
T_\text{short} &= 16 \times 175~\mu\text{s} = 2800~\mu\text{s} \\
T_\text{pos} &= 2672 + 175.4 + 2800 = 5647.4~\mu\text{s} \approx 5.65~\text{ms}
\end{aligned}
\tag{HW-TIM-4}
$$

> **Pitfall Warning (Pitfall 7):** The guard time $T_\text{guard} = 175.4~\mu\text{s}$ is critical and must not be omitted from timing calculations. It accounts for approximately 3.1% of the per-position time. Omitting it leads to an underestimate of $T_\text{pos}$ by $175.4~\mu\text{s}$ per beam position, accumulating to a significant error over a full scan.

### 2.4 Chirp Duty Cycle

The fraction of each PRI spent transmitting (chirp duty cycle) differs between the two modes:

$$
\eta_\text{long} = \frac{T_{c,1}}{T_{r,1}} \tag{HW-TIM-5}
$$

$$
\eta_\text{short} = \frac{T_{c,2}}{T_{r,2}} \tag{HW-TIM-6}
$$

For the long chirp mode, $\eta_\text{long} = 30/167 \approx 18.0\%$. For the short chirp mode, $\eta_\text{short} = 0.5/175 \approx 0.29\%$. The low duty cycle of the short chirp mode reflects the very short pulse duration $T_{c,2}$ relative to the PRI.

---

## 3. Full Scan Timing

The AERIS-10 performs a 360-degree azimuth scan using a stepper motor while electronically steering the beam through $N_\text{el}$ elevation positions at each azimuth step.

### 3.1 Elevation Scan

At each azimuth position, the beam is steered through all $N_\text{el}$ elevation positions. The firmware (`main.cpp:482--512`) iterates through beam positions using the `matrix1`, `vector_0`, and `matrix2` steering vectors. The total elevation scan time is:

$$
T_\text{el} = N_\text{el} \times T_\text{pos} \tag{HW-TIM-7}
$$

Using $N_\text{el} = 31$ positions (see [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing)):

$$
T_\text{el} = 31 \times 5647.4~\mu\text{s} = 175{,}069.4~\mu\text{s} \approx 175.1~\text{ms}
$$

### 3.2 Stepper Motor Movement

Between azimuth positions, the stepper motor rotates to the next azimuth angle. The stepper motor parameters from `main.cpp:195,518--523`:

| Parameter | Value | Firmware Variable |
|-----------|-------|-------------------|
| Steps per revolution | 200 | `Stepper_steps` |
| Azimuth positions per revolution | 50 | `y_max` |
| Steps per azimuth move | 4 | `Stepper_steps / y_max` |
| Step pulse high time | $500~\mu\text{s}$ | `delay_us(500)` |
| Step pulse low time | $500~\mu\text{s}$ | `delay_us(500)` |
| Time per step | $1~\text{ms}$ | High + low |

The stepper movement time per azimuth position is:

$$
T_\text{step} = \frac{S_\text{rev}}{N_\text{az}} \times t_\text{step} \tag{HW-TIM-8}
$$

where $S_\text{rev} = 200$ is the total steps per revolution, $N_\text{az} = 50$ is the number of azimuth positions, and $t_\text{step} = 1~\text{ms}$ is the time per step (500 us high + 500 us low). Thus $T_\text{step} = 4 \times 1~\text{ms} = 4~\text{ms}$.

### 3.3 Full Revolution Time

The total time for one complete 360-degree revolution is:

$$
T_\text{rev} = N_\text{az} \times (T_\text{el} + T_\text{step}) \tag{HW-TIM-9}
$$

Substituting the computed values:

$$
\begin{aligned}
T_\text{rev} &= 50 \times (175.1~\text{ms} + 4~\text{ms}) \\
&= 50 \times 179.1~\text{ms} \\
&= 8955~\text{ms} \approx 8.96~\text{s}
\end{aligned}
\tag{HW-TIM-10}
$$

This gives a scan rate of approximately $1 / T_\text{rev} \approx 0.112~\text{Hz}$, or roughly one revolution every 9 seconds. The scan rate is dominated by the elevation scan time; stepper motor movement contributes only $4 / 179.1 \approx 2.2\%$ of the per-azimuth time.

---

## 4. FPGA Pipeline Latency

The FPGA signal processing pipeline transforms raw ADC samples into range-Doppler detection maps. Each processing stage introduces latency measured in clock cycles within its respective clock domain. This section estimates the per-stage latency; actual values require Vivado timing reports (see [STATE.md blockers](../.planning/STATE.md)).

All stage references correspond to Verilog modules documented in [`05_fpga_board.md` Section 5](05_fpga_board.md#5-fpga-module-inventory).

### 4.1 ADC Capture

**Module:** `ad9484_interface_400m` (400 MHz domain)

The AD9484 LVDS DDR interface captures one 8-bit sample per clock cycle using `IDDR` primitives in `SAME_EDGE_PIPELINED` mode. The pipeline mode adds 1 clock cycle of latency for output registration.

$$
t_\text{ADC} = \frac{N_\text{ADC,cyc}}{f_\text{ADC}} \tag{HW-TIM-11}
$$

where $N_\text{ADC,cyc} \approx 2$ cycles (IBUFDS + IDDR pipeline) at $f_\text{ADC} = 400~\text{MHz}$, giving $t_\text{ADC} \approx 5~\text{ns}$.

### 4.2 Clock Domain Crossing (400 MHz to 100 MHz)

**Module:** `cdc_adc_to_processing` (400 MHz source, 100 MHz destination)

The 3-stage Gray-coded CDC synchronizer (`cdc_modules.v`, documented in [`05_fpga_board.md` Section 4](05_fpga_board.md#4-cdc-synchronizers)) introduces synchronization latency:

$$
t_\text{CDC} = \frac{S_\text{CDC}}{f_\text{dst}} \tag{HW-TIM-12}
$$

where $S_\text{CDC} = 3$ synchronizer stages and $f_\text{dst} = 100~\text{MHz}$. This gives $t_\text{CDC} = 30~\text{ns}$.

### 4.3 Digital Down-Conversion (DDC)

**Module:** `ddc_400m_enhanced` (400 MHz front-end, 100 MHz output)

The DDC performs NCO mixing to translate the IF signal ($f_\text{IF}$, see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga)) to baseband. The NCO uses a 16-bit phase accumulator (`NCO_WIDTH = 16` in `ddc_400m.v`). The DDC latency is dominated by the mixer multiply and output registration:

$$
t_\text{DDC} \approx \frac{3}{f_\text{ADC}} = \frac{3}{400~\text{MHz}} = 7.5~\text{ns} \tag{HW-TIM-13}
$$

This accounts for the NCO lookup (1 cycle), multiply (1 cycle), and output register (1 cycle).

### 4.4 CIC Decimation

**Module:** `cic_decimator_4x_enhanced` (100 MHz domain)

The CIC filter has $N_\text{CIC} = 5$ stages with decimation factor $D_\text{CIC} = 4$ and comb delay $M_\text{comb} = 1$ (`STAGES = 5`, `DECIMATION = 4`, `COMB_DELAY = 1` in `cic_decimator_4x_enhanced.v`). The CIC group delay at DC for a single-stage CIC with decimation $D$ and comb delay $M_\text{comb}$ is:

$$
\tau_\text{CIC,group} = \frac{N_\text{CIC} \cdot D_\text{CIC} \cdot M_\text{comb}}{2 \cdot f_s} \tag{HW-TIM-14}
$$

For the AERIS-10 configuration: $\tau_\text{CIC,group} = (5 \times 4 \times 1) / (2 \times 400~\text{MHz}) = 25~\text{ns}$. However, the CIC filter also requires $D_\text{CIC}$ input samples to produce one output, so the effective latency includes the decimation fill time:

$$
t_\text{CIC} = \tau_\text{CIC,group} + \frac{D_\text{CIC}}{f_s} = 25~\text{ns} + 10~\text{ns} = 35~\text{ns} \tag{HW-TIM-15}
$$

After CIC decimation, the output rate is $f_s / D_\text{CIC} = 100~\text{MSPS}$ per Eq. (HW-FPGA-5) in [`05_fpga_board.md`](05_fpga_board.md#7-signal-processing-pipeline-data-flow).

### 4.5 FIR Compensation Filter

**Module:** `fir_lowpass_parallel_enhanced` (100 MHz domain)

The FIR droop compensation filter has 32 taps (`TAPS = 32` in `fir_lowpass.v`). For a parallel multiply-accumulate architecture, the latency is approximately:

$$
t_\text{FIR} = \frac{N_\text{taps}}{f_\text{sys}} = \frac{32}{100~\text{MHz}} = 320~\text{ns} \tag{HW-TIM-16}
$$

> **Note:** A pipelined parallel implementation may reduce this to a few clock cycles; the estimate above assumes sequential accumulation. Actual latency depends on Vivado synthesis decisions.

### 4.6 Matched Filter (Pulse Compression)

**Module:** `matched_filter_multi_segment` (100 MHz domain)

The matched filter performs frequency-domain convolution using $N_\text{FFT}$-point forward and inverse FFTs (`BUFFER_SIZE = 1024` in `matched_filter_multi_segment.v`). The long chirp requires multiple segments:

- Long chirp: `LONG_CHIRP_SAMPLES = 3000`, processed in `LONG_SEGMENTS = 4` overlapping segments of 1024 samples with `OVERLAP_SAMPLES = 128`
- Short chirp: `SHORT_CHIRP_SAMPLES = 50`, processed in `SHORT_SEGMENTS = 1` segment (zero-padded to 1024)

The matched filter latency per segment includes buffer fill time plus two FFTs (forward and inverse):

$$
t_\text{MF,seg} = \frac{N_\text{FFT}}{f_\text{out}} + 2 \cdot t_\text{FFT} \tag{HW-TIM-17}
$$

where $f_\text{out} = f_s / D_\text{CIC} = 100~\text{MHz}$ is the CIC output rate. The buffer fill time is $1024 / 100~\text{MHz} = 10.24~\mu\text{s}$. Each 1024-point radix-2 FFT requires $\log_2(1024) = 10$ butterfly stages, with pipeline latency approximately $10 \times 1024 / 100~\text{MHz} \approx 102.4~\mu\text{s}$ for a streaming architecture, or as few as $\sim 1024$ cycles for a pipelined radix-2 butterfly.

For a single long chirp, the total matched filter time across all segments is:

$$
t_\text{MF,long} = N_\text{seg,long} \times t_\text{MF,seg} \tag{HW-TIM-18}
$$

Estimating $t_\text{FFT} \approx 10.24~\mu\text{s}$ (1024 cycles at 100 MHz):

$$
t_\text{MF,long} \approx 4 \times (10.24 + 2 \times 10.24)~\mu\text{s} = 4 \times 30.72~\mu\text{s} \approx 122.9~\mu\text{s}
$$

For the short chirp: $t_\text{MF,short} \approx 1 \times 30.72~\mu\text{s} \approx 30.7~\mu\text{s}$.

### 4.7 Doppler Processing

**Module:** `doppler_processor_optimized` (100 MHz domain)

The Doppler processor accumulates range profiles across $M$ chirps and applies a $N_\text{Doppler}$-point FFT to $N_R$ range bins (`DOPPLER_FFT_SIZE = 32`, `RANGE_BINS = 64`, `CHIRPS_PER_FRAME = 32` in `doppler_processor.v`).

The Doppler processing latency has two components:

**Accumulation latency:** Data is collected across all $M$ chirps in a beam position. This is not additional wall-clock latency because accumulation occurs during the chirp sequence, but the Doppler FFT cannot begin until all $M$ chirps have been received:

$$
t_\text{Doppler,acc} = M \times T_{r,\text{avg}} \approx T_\text{pos} \tag{HW-TIM-19}
$$

This is inherent to the coherent processing interval and is already accounted for in $T_\text{pos}$.

**Processing latency:** After accumulation, the 32-point Doppler FFT is applied to each of the 64 range bins:

$$
t_\text{Doppler,proc} = N_R \times \frac{N_\text{Doppler} \cdot \log_2 N_\text{Doppler}}{f_\text{sys}} \tag{HW-TIM-20}
$$

Estimating: $t_\text{Doppler,proc} = 64 \times (32 \times 5) / 100~\text{MHz} = 64 \times 1.6~\mu\text{s} = 102.4~\mu\text{s}$.

> **Note:** A pipelined implementation processing multiple range bins in parallel would significantly reduce this estimate.

### 4.8 CFAR Detection

The CFAR detector scans the range-Doppler map to identify targets exceeding the adaptive threshold. The processing time depends on the reference cell window size ($N_\text{ref}$, $N_\text{guard}$) and the map dimensions ($N_R \times N_\text{Doppler}$):

$$
t_\text{CFAR} \approx \frac{N_R \times N_\text{Doppler}}{f_\text{sys}} = \frac{64 \times 32}{100~\text{MHz}} = 20.48~\mu\text{s} \tag{HW-TIM-21}
$$

This assumes one clock cycle per cell for threshold comparison after the reference window has been accumulated.

### 4.9 USB Output (FT601)

**Module:** `usb_data_interface` (100 MHz system to 100 MHz FT601 domain)

Data transfer from the FPGA to the host PC uses the FT601 USB 3.0 interface. The CDC handshake crossing (`cdc_handshake`, documented in [`05_fpga_board.md` Section 4.3](05_fpga_board.md#43-handshake-based-cdc)) introduces approximately 4 destination clock cycles per transfer.

For a range-Doppler map of $N_R \times N_\text{Doppler} = 64 \times 32 = 2048$ complex values at 32 bits each:

$$
t_\text{USB} = \frac{N_R \times N_\text{Doppler} \times W_\text{data}}{f_\text{FT601} \times W_\text{bus}} \tag{HW-TIM-22}
$$

where $W_\text{data} = 32$ bits per value and $W_\text{bus} = 32$ bits (FT601 bus width). This gives $t_\text{USB} = 2048 / 100~\text{MHz} = 20.48~\mu\text{s}$ for raw data transfer, plus CDC handshake overhead.

### 4.10 Pipeline Latency Summary

The total FPGA pipeline latency from ADC input to USB output is:

$$
t_\text{pipeline} = t_\text{ADC} + t_\text{CDC} + t_\text{DDC} + t_\text{CIC} + t_\text{FIR} + t_\text{MF} + t_\text{Doppler,proc} + t_\text{CFAR} + t_\text{USB} \tag{HW-TIM-23}
$$

| Stage | Symbol | Est. Latency | Clock Domain | Notes |
|-------|--------|-------------|--------------|-------|
| ADC capture | $t_\text{ADC}$ | $\sim 5~\text{ns}$ | 400 MHz | IBUFDS + IDDR |
| CDC (400 to 100 MHz) | $t_\text{CDC}$ | $\sim 30~\text{ns}$ | 100 MHz | 3-stage Gray sync |
| DDC | $t_\text{DDC}$ | $\sim 7.5~\text{ns}$ | 400 MHz | NCO + mixer |
| CIC decimation | $t_\text{CIC}$ | $\sim 35~\text{ns}$ | 100 MHz | 5-stage, 4x decim |
| FIR compensation | $t_\text{FIR}$ | $\sim 320~\text{ns}$ | 100 MHz | 32-tap parallel |
| Matched filter (long) | $t_\text{MF}$ | $\sim 123~\mu\text{s}$ | 100 MHz | 4 segments, FFT-based |
| Doppler processing | $t_\text{Doppler,proc}$ | $\sim 102~\mu\text{s}$ | 100 MHz | 32-pt FFT, 64 bins |
| CFAR detection | $t_\text{CFAR}$ | $\sim 20.5~\mu\text{s}$ | 100 MHz | Map scan |
| USB output | $t_\text{USB}$ | $\sim 20.5~\mu\text{s}$ | FT601 100 MHz | 2048 values |
| **Total pipeline** | $t_\text{pipeline}$ | $\sim 266~\mu\text{s}$ | -- | Theoretical estimate |

> **Important:** These latency values are theoretical estimates based on module parameters and assumed architectures. Actual latency requires Vivado implementation timing reports, which are not currently available. The matched filter and Doppler processor dominate the pipeline latency and are the most sensitive to implementation details.

---

## 5. End-to-End Latency Summary

The complete latency from "target illuminated by radar beam" to "target displayed on GUI" comprises four contributions:

$$
t_\text{total} = T_\text{pos} + t_\text{pipeline} + t_\text{USB,xfer} + t_\text{PC} \tag{HW-TIM-24}
$$

| Contributor | Symbol | Est. Time | Fraction | Notes |
|-------------|--------|-----------|----------|-------|
| Chirp acquisition (CPI) | $T_\text{pos}$ | $5.65~\text{ms}$ | 93.4% | Dominated by $M = 32$ chirps |
| FPGA processing | $t_\text{pipeline}$ | $\sim 0.27~\text{ms}$ | 4.5% | Matched filter + Doppler |
| USB transfer to PC | $t_\text{USB,xfer}$ | $< 0.1~\text{ms}$ | $< 1.7\%$ | USB 3.0 bulk transfer |
| PC processing (GUI) | $t_\text{PC}$ | $\sim 1\text{--}10~\text{ms}$ | Variable | DBSCAN, Kalman, rendering |

**Key insight:** The per-beam-position dwell time $T_\text{pos}$ dominates the end-to-end latency. FPGA processing completes well within the available inter-position time, confirming that the processing pipeline does not bottleneck the scan rate.

### 5.1 Timing Margin

The FPGA must complete processing of one beam position's data before the next position's data arrives. The available processing window is $T_\text{pos} \approx 5.65~\text{ms}$, and the estimated pipeline latency is $t_\text{pipeline} \approx 0.27~\text{ms}$, leaving a timing margin of:

$$
t_\text{margin} = T_\text{pos} - t_\text{pipeline} \approx 5.38~\text{ms} \tag{HW-TIM-25}
$$

This represents a margin factor of $\sim 21\times$, indicating that the FPGA pipeline has substantial headroom.

---

## 6. References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- symbols for $T_{r,1}$, $T_{r,2}$, $T_\text{guard}$, $M$, $N_\text{el}$, $N_\text{az}$, $f_s$, $N_\text{FFT}$, $t_\text{pipeline}$
- [Parameter Table](../00_notation/parameter_table.md) -- canonical timing values, FPGA parameters, stepper motor steps
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules

### Hardware Cross-References
- [`05_fpga_board.md`](05_fpga_board.md) -- FPGA module inventory (Section 5), clock domains (Section 3), CDC synchronizers (Section 4), pipeline data flow Eq. (HW-FPGA-5) and Eq. (HW-FPGA-6)
- [`03_frequency_synthesis.md`](03_frequency_synthesis.md) -- AD9523 clock tree providing ADC (400 MHz), system (100 MHz), and DAC (120 MHz) clocks
- [`02_rf_frontend.md`](02_rf_frontend.md) -- AD9484 ADC LVDS interface specifications

### Firmware Sources
- `main.cpp:178--184` -- Radar timing parameters ($T_{c,1}$, $T_{r,1}$, $T_{c,2}$, $T_{r,2}$, $T_\text{guard}$, $M$)
- `main.cpp:445--466` -- `executeChirpSequence()` function implementing the dual-mode chirp schedule with guard time
- `main.cpp:468--529` -- `runRadarPulseSequence()` function implementing beam steering loop and stepper motor control
- `main.cpp:195` -- Stepper motor steps per revolution (`Stepper_steps = 200`)

### FPGA Sources
- `ddc_400m.v` -- DDC parameters (`ADC_WIDTH = 8`, `NCO_WIDTH = 16`, `IF_FREQ`, `FS`)
- `cic_decimator_4x_enhanced.v` -- CIC parameters (`STAGES = 5`, `DECIMATION = 4`, `COMB_DELAY = 1`)
- `matched_filter_multi_segment.v` -- Matched filter parameters (`BUFFER_SIZE = 1024`, `LONG_CHIRP_SAMPLES = 3000`, `SHORT_CHIRP_SAMPLES = 50`, `LONG_SEGMENTS = 4`)
- `doppler_processor.v` -- Doppler parameters (`DOPPLER_FFT_SIZE = 32`, `RANGE_BINS = 64`, `CHIRPS_PER_FRAME = 32`)
