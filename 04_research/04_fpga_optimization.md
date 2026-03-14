# FPGA Pipeline Optimization Research

**Purpose:** Survey optimization techniques for the AERIS-10 FPGA signal processing pipeline, evaluating HLS, loop unrolling, multi-bank memory, and pipeline parallelism against Artix-7 XC7A100T resource constraints.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resources, clock domains, module inventory
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- signal processing pipeline architecture

---

## 1. Current State

The AERIS-10 FPGA signal processing pipeline is implemented on the Xilinx Artix-7 XC7A100T and processes digitized IF samples through ten stages, from ADC acquisition at 400 MHz through Doppler processing and USB output at 100 MHz. The complete pipeline architecture is documented in [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md).

### 1.1 Pipeline Architecture Summary

The pipeline consists of the following major processing stages (see Table 1.1 in [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md#11-signal-flow-summary)):

| Stage | Function | Key Module | Clock |
|-------|----------|------------|-------|
| 1 | ADC Acquisition | `lvds_to_cmos_400m` + `ad9484_lvds_to_cmos_400m` | 400 MHz |
| 2 | Clock Domain Crossing | `cdc_adc_to_processing` | 400 -> 100 MHz |
| 3 | Digital Down-Conversion | `ddc_400m_enhanced` | 400/100 MHz |
| 4 | DDC Output Interface | `ddc_input_interface` | 100 MHz |
| 5 | Reference Chirp Loading | `chirp_memory_loader_param` + `latency_buffer_2159` | 100 MHz |
| 6 | Matched Filter | `matched_filter_multi_segment` | 100 MHz |
| 7 | Range Bin Decimation | `range_bin_decimator` | 100 MHz |
| 8 | Doppler Processing | `doppler_processor_optimized` | 100 MHz |
| 9 | Threshold Detection | `radar_system_top.v` (inline) | 100 MHz |
| 10 | USB Output | `usb_data_interface` | FT601 100 MHz |

The pipeline operates across three primary clock domains (400 MHz ADC, 100 MHz system, 100 MHz FT601) with clock domain crossings handled by 3-stage synchronizers (see Section 4 of [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md#4-cdc-synchronizers) for Eq. (HW-FPGA-4)).

### 1.2 Module Inventory

The FPGA contains 25+ Verilog modules organized by function (see Section 5 of [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md#5-fpga-module-inventory)). Key processing modules include:

- Two 1024-point FFT cores (`fft_1024_forward_enhanced`, `fft_1024_inverse_enhanced`) using radix-2 DIT architecture
- Multi-segment matched filter (`matched_filter_multi_segment`) with overlap-save segmentation (Eq. (SW-4) in [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md))
- 32-point Doppler FFT via Xilinx `xfft_32` IP core with Hamming windowing
- 5-stage CIC decimator ($D_\text{CIC} = 4$, gain $G_\text{CIC} = 2^{10}$, Eq. (SW-3))
- 32-tap FIR compensation filter for CIC droop correction

### 1.3 Current Resource Utilization

Theoretical per-module estimates from Section 2.2 of [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md#22-resource-utilization):

| Resource | Estimated Used | Available ($N_\text{LUT}$, $N_\text{DSP}$, $N_\text{BRAM}$) | Utilization | Headroom |
|----------|---------------|--------------------------------------------------------------|-------------|----------|
| LUTs | ~16,500 | 63,400 | ~26% | ~46,900 |
| DSP48E1 | ~88 | 240 | ~37% | ~152 |
| BRAM (36 Kb) | ~101 | 135 | ~75% | ~34 |
| Flip-Flops | -- | 126,800 | -- | -- |

> **Important:** These are theoretical estimates based on Verilog module parameters, pending Vivado implementation reports. Actual utilization may differ due to synthesis optimizations, routing congestion, and Vivado tool decisions. All optimization proposals in this document use these theoretical estimates as the baseline and should be re-evaluated when Vivado reports become available.

### 1.4 Key Performance Characteristics

- **FFT architecture:** 1024-point radix-2 decimation-in-time (DIT), consuming ~4,000 LUTs + 16 DSPs + 20 BRAMs per instance (two instances: forward and inverse)
- **Doppler FFT:** 32-point via Xilinx IP core, processing 64 range bins with Hamming window
- **Matched filter latency:** 3187-cycle latency buffer at 100 MHz ($31.87~\mu\text{s}$) to align reference chirp with FFT pipeline output (see Section 6.2 of [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md))
- **Memory access pattern:** Single-port BRAM used for Doppler processor data storage ($N_\text{rb} \times M = 64 \times 32 = 2048$ entries, chirp-major addressing per Eq. (SW-6))

---

## 2. Literature Survey

### 2.1 Vitis HLS vs. Hand-Coded Verilog

High-Level Synthesis (HLS) tools, specifically Xilinx Vitis HLS (formerly Vivado HLS, rebranded in 2020), enable C/C++ algorithm descriptions to be compiled directly to RTL. This offers significant development velocity improvements at the cost of resource efficiency.

**Performance comparison:**

| Metric | Hand-Coded Verilog | Vitis HLS | Notes |
|--------|-------------------|-----------|-------|
| Development time | 1x (baseline) | ~0.25x (4x faster) | HLS eliminates manual FSM, datapath, and control logic design |
| LUT utilization | 1x (baseline) | 1.15--1.30x (15--30% overhead) | HLS generates conservative control logic and pipeline registers |
| DSP utilization | 1x (baseline) | 1.0--1.10x (0--10% overhead) | DSP inference is generally efficient in HLS |
| BRAM utilization | 1x (baseline) | 1.05--1.20x (5--20% overhead) | HLS may infer additional buffering |
| Clock frequency achievable | Up to device limit | Typically 10--20% lower | HLS may not optimize critical paths as aggressively |

**Quality of Results (QoR) comparison methodology:** QoR comparison should be performed by implementing the same algorithm (e.g., a 32-tap FIR filter) in both hand-coded Verilog and Vitis HLS, then comparing post-synthesis resource utilization and maximum clock frequency from Vivado implementation reports.

**Applicability to AERIS-10 pipeline:**

| Module | HLS Suitability | Rationale |
|--------|----------------|-----------|
| FFT cores (1024-pt) | LOW | Performance-critical; hand-coded radix-2 DIT already optimized for DSP/BRAM balance |
| Matched filter | LOW | Complex multi-segment FSM with overlap-save; hand-coded provides tighter control |
| Doppler processor | LOW | Tight integration with Xilinx `xfft_32` IP; HLS provides no advantage |
| USB interface | MEDIUM | Less timing-critical; HLS could simplify packet formatting logic |
| Control logic / FSMs | MEDIUM-HIGH | Edge detectors, chirp controllers, mode selection -- HLS reduces development time with minimal penalty |
| CIC decimator | LOW | Simple cascaded structure; hand-coded is already compact (~200 LUTs) |

**Resource-constrained Artix-7 consideration:** On the XC7A100T, the 15--30% LUT overhead of HLS is tolerable for non-critical modules (given ~46,900 LUTs of headroom) but could be problematic if applied to performance-critical modules like the FFT, where hand-coded Verilog provides tighter resource control. HLS is best suited for modules where development velocity matters more than resource efficiency.

### 2.2 Loop Unrolling for FFT and Matched Filter

The current 1024-point FFT uses a radix-2 DIT architecture, which requires $\log_2(N_\text{FFT}) = 10$ butterfly stages, each containing $N_\text{FFT}/2 = 512$ butterfly operations.

**Radix-4 FFT optimization:**

A radix-4 FFT reduces the number of stages from $\log_2(N) = 10$ to $\log_4(N) = 5$ stages, each containing $N/4 = 256$ radix-4 butterfly operations. The radix-4 butterfly performs the equivalent of two radix-2 stages in a single iteration.

| Architecture | Stages | Butterflies/Stage | Complex Multiplies | Clock Cycles (est.) | DSP Usage (est.) |
|-------------|--------|-------------------|-------------------|---------------------|------------------|
| Radix-2 (current) | 10 | 512 | 5,120 | ~5,120 | 16 |
| Radix-4 | 5 | 256 | 2,560 | ~2,560 | ~32 |
| Split-radix | 5 | 256 | ~2,180 | ~2,180 | ~28 |

**Throughput improvement:** Radix-4 reduces clock cycles by approximately 2x compared to radix-2 for the same $N_\text{FFT}$. This directly reduces the matched filter processing chain latency (currently 3187 cycles at 100 MHz) by shortening the forward FFT and inverse FFT contributions.

**DSP cost:** Radix-4 butterflies require approximately 2x the DSPs of radix-2 butterflies due to the larger butterfly unit. For a single 1024-point FFT:

- Radix-2 (current): ~16 DSPs per FFT instance
- Radix-4: ~32 DSPs per FFT instance

With two FFT instances (forward + inverse), the upgrade from radix-2 to radix-4 would increase DSP usage from ~32 to ~64, consuming an additional ~32 DSPs from the ~152 available -- feasible within current headroom.

**Split-radix alternative:** Split-radix FFT achieves a further ~15% reduction in complex multiplications versus radix-4, with DSP usage between radix-2 and radix-4. However, split-radix has irregular butterfly patterns that increase control logic complexity and LUT usage.

### 2.3 Multi-Bank Memory Architecture

The current Doppler processor (`doppler_processor_optimized`) uses single-port BRAM with chirp-major addressing (Eq. (SW-6) in [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md)):

$$
\text{addr} = \text{chirp\_index} \times N_\text{rb} + \text{range\_bin}
$$

This limits memory bandwidth: the processor can only read OR write in a given clock cycle, not both simultaneously. During the `S_ACCUMULATE` state, incoming chirp data must be written before the previous frame's data can be read for FFT processing.

**Dual-port BRAM optimization:**

Artix-7 BRAMs are natively dual-port (each 36 Kb BRAM has two independent read/write ports). The current design uses only single-port mode. Switching to dual-port mode allows simultaneous read and write operations with no additional BRAM resource cost:

| Mode | Read Bandwidth | Write Bandwidth | Concurrent R/W | Additional BRAMs |
|------|---------------|----------------|-----------------|------------------|
| Single-port (current) | 100 MHz x 32-bit | 100 MHz x 32-bit | No | 0 (baseline) |
| Dual-port (proposed) | 100 MHz x 32-bit | 100 MHz x 32-bit | Yes | 0 |

**Performance benefit:** Dual-port operation enables ping-pong buffering -- one port writes incoming chirp data from the current frame while the other port reads the previous frame's data for Doppler FFT processing. This eliminates the sequential write-then-read constraint and can reduce Doppler processing time by up to 50% for the accumulation phase.

**Bank interleaving for FFT butterfly operations:**

For the 1024-point FFT, butterfly operations require reading two data points with specific address patterns (bit-reversed for DIT, sequential for DIF). With single-port BRAM, each butterfly requires two sequential read cycles. Bank interleaving across 2 or 4 BRAM banks allows both butterfly inputs to be read in a single cycle:

| Banks | Reads per Butterfly | Speedup | Additional BRAMs |
|-------|-------------------|---------|------------------|
| 1 (current) | 2 cycles | 1x | 0 |
| 2 banks | 1 cycle | ~2x | +20 per FFT instance |
| 4 banks | 1 cycle (prefetch) | ~2x | +40 per FFT instance |

> **BRAM constraint warning:** The current estimated BRAM utilization is ~75% (101/135). Adding 2-bank interleaving for both FFT instances would require ~40 additional BRAMs, pushing total utilization to ~104% -- **infeasible**. Single-FFT 2-bank interleaving (+20 BRAMs) would push utilization to ~90%, which is at the upper limit of practical FPGA design. Bank interleaving is BRAM-constrained on this device.

### 2.4 Pipeline Parallelism

The current pipeline processes range bins serially -- one range bin at a time through the matched filter and Doppler processor chain. Pipeline parallelism duplicates processing paths to handle multiple range bins concurrently.

**2x parallelism:**

| Resource | Single Path (current) | 2x Parallel | Delta |
|----------|---------------------|-------------|-------|
| LUTs | ~16,500 (total) | ~22,500 | +6,000 |
| DSPs | ~88 | ~120 | +32 |
| BRAMs | ~101 | ~131 | +30 |

A 2x parallel path duplicates the matched filter and Doppler processor cores, achieving 2x throughput at the cost of approximately doubling the resource usage of these modules. The ADC front-end, DDC, and USB interface remain single-instance.

**4x parallelism:**

| Resource | Single Path (current) | 4x Parallel | Delta |
|----------|---------------------|-------------|-------|
| LUTs | ~16,500 (total) | ~34,500 | +18,000 |
| DSPs | ~88 | ~184 | +96 |
| BRAMs | ~101 | ~191 | +90 (exceeds 135) |

> **Infeasibility:** 4x parallelism requires ~191 BRAMs, exceeding the 135 available on the XC7A100T by 41%. Even 2x parallelism pushes BRAM utilization to ~97%, which is impractical for reliable implementation (routing congestion typically limits practical BRAM usage to ~85--90%).

**Area-time tradeoff summary:**

| Parallelism | Throughput Gain | LUT % | DSP % | BRAM % | Verdict |
|------------|----------------|-------|-------|--------|---------|
| 1x (current) | 1.0x | 26% | 37% | 75% | Baseline |
| 2x | 2.0x | 35% | 50% | 97% | MARGINAL (BRAM-constrained) |
| 4x | 4.0x | 54% | 77% | 141% | INFEASIBLE |

---

## 3. Gap Analysis

The current FPGA pipeline is functionally correct but not optimized for throughput or resource efficiency. The following gaps exist between the current implementation and achievable performance:

### 3.1 Memory Bandwidth Limitation

**Gap:** Single-port BRAM usage in the Doppler processor prevents simultaneous read/write operations, serializing data accumulation and FFT processing. The Artix-7 BRAM architecture natively supports dual-port operation, meaning this bandwidth limitation is a design choice, not a hardware constraint.

**Impact:** Doppler processing throughput is approximately 50% lower than achievable with dual-port BRAM, extending the time between frame outputs.

### 3.2 FFT Clock Cycle Efficiency

**Gap:** The radix-2 DIT architecture uses approximately 2x the clock cycles of a radix-4 implementation for the same $N_\text{FFT} = 1024$. Given sufficient DSP headroom (~152 DSPs available), a radix-4 or split-radix FFT is feasible.

**Impact:** The matched filter processing chain latency (currently contributing to the 3187-cycle buffer at 100 MHz) could be reduced, improving pipeline throughput and potentially allowing more chirps per frame or faster scan rates.

### 3.3 No HLS Evaluation

**Gap:** All modules are hand-coded in Verilog. No evaluation has been performed to determine which modules would benefit from HLS-based development for maintenance velocity, even at the cost of modest resource overhead.

**Impact:** Future modifications to non-critical modules (control logic, USB interface, chirp controller) require Verilog expertise. HLS could lower the barrier for algorithm iteration on these modules.

### 3.4 Serial Range Bin Processing

**Gap:** Range bins are processed one at a time through the Doppler FFT. While full pipeline parallelism is BRAM-constrained (Section 2.4), partial optimizations such as pipelined FFT output buffering could improve throughput without duplicating entire processing paths.

**Impact:** Frame processing time scales linearly with $N_\text{rb} = 64$ range bins. Optimizations to the per-bin processing latency have a 64x multiplied effect on total frame time.

---

## 4. Feasibility Assessment

> **Note:** All resource estimates below are based on theoretical utilization from Phase 3, pending Vivado implementation reports. Actual feasibility may differ. A conservative 30% overhead margin is recommended when evaluating proposals against resource limits.

### 4.1 Dual-Port BRAM for Doppler Processor

| Property | Value |
|----------|-------|
| Optimization type | Memory access pattern change |
| Algorithm complexity | No change |
| Additional LUTs | ~100--300 (dual-port address generation logic) |
| Additional DSPs | 0 |
| Additional BRAMs | 0 (existing BRAMs reconfigured to dual-port mode) |
| Current LUT utilization after | ~26% (negligible change) |
| Current DSP utilization after | ~37% (no change) |
| Current BRAM utilization after | ~75% (no change) |
| Estimated throughput improvement | Up to 1.5x for Doppler processing phase |
| Pipeline integration | Modifies `doppler_processor_optimized` BRAM instantiation and FSM |
| Risk | LOW -- dual-port is native BRAM capability; no additional resources required |
| Verdict | **FEASIBLE** -- no additional resources, immediate throughput gain |

### 4.2 Radix-4 FFT (Replacing Radix-2)

| Property | Value |
|----------|-------|
| Optimization type | Algorithm change (loop unrolling) |
| Algorithm complexity | $O(N \log_4 N)$ vs. current $O(N \log_2 N)$ -- same asymptotic, fewer iterations |
| Additional LUTs | ~2,000--4,000 per FFT instance (larger butterfly unit) |
| Additional DSPs | ~16 per FFT instance (~32 total for forward + inverse) |
| Additional BRAMs | 0--2 per instance (twiddle factor ROM may be slightly larger) |
| Current LUT utilization after | ~32--39% |
| Current DSP utilization after | ~50% |
| Current BRAM utilization after | ~75--76% |
| Estimated throughput improvement | ~2x reduction in FFT clock cycles |
| Pipeline integration | Replaces `fft_1024_forward_enhanced` and `fft_1024_inverse_enhanced` |
| Risk | MEDIUM -- requires redesign of FFT core and verification of twiddle factor precision |
| Verdict | **FEASIBLE** -- trades DSP for speed within available headroom |

### 4.3 Multi-Bank BRAM Interleaving for FFT

| Property | Value |
|----------|-------|
| Optimization type | Memory architecture change |
| Algorithm complexity | No change |
| Additional LUTs | ~500--1,000 per FFT instance (bank select logic) |
| Additional DSPs | 0 |
| Additional BRAMs | ~20 per FFT instance (~40 total for forward + inverse) |
| Current LUT utilization after | ~28% |
| Current DSP utilization after | ~37% |
| Current BRAM utilization after | **~105% (EXCEEDS CAPACITY)** |
| Estimated throughput improvement | ~2x reduction in memory access cycles per butterfly |
| Pipeline integration | Restructures FFT memory subsystem |
| Risk | HIGH -- exceeds BRAM capacity for both FFT instances |
| Verdict | **INFEASIBLE** for both FFT instances; **MARGINAL** for single FFT instance (~90% BRAM) |

### 4.4 HLS for Non-Critical Modules

| Property | Value |
|----------|-------|
| Optimization type | Development methodology change |
| Algorithm complexity | No change (same functionality) |
| Additional LUTs | ~150--500 per module (15--30% overhead on ~1,000--1,500 LUT modules) |
| Additional DSPs | 0 |
| Additional BRAMs | 0--2 (HLS-inferred buffering) |
| Current LUT utilization after | ~27% |
| Current DSP utilization after | ~37% |
| Current BRAM utilization after | ~75--76% |
| Estimated throughput improvement | None (development velocity improvement, not runtime) |
| Pipeline integration | Replaces individual modules with HLS-generated equivalents |
| Candidate modules | `usb_data_interface`, `plfm_chirp_controller_enhanced`, `edge_detector_enhanced`, `level_shifter_interface` |
| Risk | LOW -- non-critical modules; HLS overhead is within resource budget |
| Verdict | **FEASIBLE** -- improves development velocity with minimal resource impact |

### 4.5 2x Pipeline Parallelism

| Property | Value |
|----------|-------|
| Optimization type | Structural duplication |
| Algorithm complexity | No change (same algorithm, duplicated hardware) |
| Additional LUTs | ~6,000 |
| Additional DSPs | ~32 |
| Additional BRAMs | ~30 |
| Current LUT utilization after | ~35% |
| Current DSP utilization after | ~50% |
| Current BRAM utilization after | **~97%** |
| Estimated throughput improvement | 2.0x |
| Pipeline integration | Duplicates matched filter and Doppler processor paths with input demux and output mux |
| Risk | HIGH -- BRAM utilization at 97% leaves no margin for routing; practical FPGA designs limit BRAM usage to ~85--90% |
| Verdict | **MARGINAL** -- theoretically fits but BRAM utilization too high for reliable implementation |

### 4.6 Summary Table

| Optimization | LUT Impact | DSP Impact | BRAM Impact | Throughput Gain | Verdict |
|-------------|-----------|-----------|------------|----------------|---------|
| Dual-port BRAM (Doppler) | +0.5% | 0% | 0% | 1.5x Doppler | **FEASIBLE** |
| Radix-4 FFT | +6--13% | +13% | +1% | 2x FFT | **FEASIBLE** |
| Multi-bank BRAM (FFT) | +2% | 0% | +30% | 2x memory | **INFEASIBLE** (both) |
| HLS (non-critical) | +1% | 0% | +1% | Dev velocity | **FEASIBLE** |
| 2x parallelism | +9% | +13% | +22% | 2x throughput | **MARGINAL** |

---

## 5. Recommendations

### Priority 1: Dual-Port BRAM for Doppler Processor

- **Expected improvement:** Up to 1.5x Doppler processing throughput via simultaneous read/write
- **Resource cost:** Negligible (~100--300 additional LUTs; no additional DSPs or BRAMs)
- **Risk:** LOW -- leverages native Artix-7 BRAM dual-port capability
- **Rationale:** This is the highest-value optimization because it requires no additional resources. The current single-port BRAM usage in `doppler_processor_optimized` artificially limits memory bandwidth when the hardware natively supports dual-port access. Ping-pong buffering enables concurrent data accumulation and FFT processing.
- **Investigation steps:**
  1. Verify Doppler processor BRAM instantiation parameters in `doppler_processor.v`
  2. Prototype dual-port BRAM instantiation with separate read/write address generators
  3. Modify the Doppler FSM to enable concurrent `S_ACCUMULATE` (write port) and `S_LOAD_FFT` (read port) operation
  4. Validate with Vivado simulation and measure actual throughput improvement

### Priority 2: Radix-4 FFT (1024-Point)

- **Expected improvement:** ~2x reduction in FFT clock cycles, reducing matched filter pipeline latency
- **Resource cost:** ~32 additional DSPs (from ~88 to ~120), ~4,000 additional LUTs
- **Risk:** MEDIUM -- requires full FFT core redesign and twiddle factor ROM recalculation
- **Rationale:** DSP headroom (~152 available) supports this optimization. The 2x speedup in the FFT directly reduces the matched filter processing chain latency (currently requiring a 3187-cycle latency buffer). This is a classical area-time tradeoff that the current DSP budget can accommodate.
- **Investigation steps:**
  1. Evaluate Xilinx FFT IP core (`xfft_v9_1`) in radix-4 mode vs. current custom radix-2
  2. Generate twiddle factor ROM for 1024-point radix-4 FFT and verify BRAM usage
  3. Synthesize standalone radix-4 FFT module in Vivado to obtain actual resource utilization
  4. Compare QoR (LUTs, DSPs, BRAMs, max frequency) between hand-coded radix-4 and Xilinx IP

### Priority 3: Vitis HLS for Non-Critical Modules

- **Expected improvement:** ~4x faster development iteration for control and interface modules
- **Resource cost:** ~150--500 additional LUTs per module (15--30% overhead)
- **Risk:** LOW -- applies only to non-timing-critical modules with ample resource headroom
- **Rationale:** Modules such as `usb_data_interface`, `plfm_chirp_controller_enhanced`, and `level_shifter_interface` are control-oriented and not on the critical processing path. HLS conversion of these modules would improve development velocity for future modifications without impacting pipeline throughput.
- **Investigation steps:**
  1. Select one candidate module (recommended: `plfm_chirp_controller_enhanced`) for HLS proof-of-concept
  2. Implement the equivalent algorithm in C++ with Vitis HLS pragmas
  3. Compare post-synthesis resource utilization and maximum clock frequency against hand-coded version
  4. Document QoR comparison to establish HLS overhead baseline for this project

### Not Recommended at This Time

**Multi-bank BRAM interleaving for FFT:** Exceeds BRAM capacity when applied to both FFT instances. Even for a single instance, the resulting ~90% BRAM utilization provides insufficient routing margin.

**2x or 4x pipeline parallelism:** BRAM-constrained. The ~30 additional BRAMs required for 2x parallelism would push utilization to ~97%, which is impractical. 4x parallelism exceeds BRAM capacity entirely.

---

## References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- Section 5 (Signal Processing) and Section 6 (Software Signal Processing)
- [Parameter Table](../00_notation/parameter_table.md) -- Signal Processing (FPGA) section
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resource capacity (Section 2), clock domains (Section 3), module inventory (Section 5)
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- 10-stage pipeline architecture, FFT parameters, Doppler processor design

### External References
- Xilinx, *7 Series FPGAs Memory Resources User Guide* (UG473) -- BRAM dual-port configuration
- Xilinx, *7 Series DSP48E1 Slice User Guide* (UG479) -- DSP48E1 architecture for FFT butterfly operations
- Xilinx, *Artix-7 FPGAs Data Sheet: DC and AC Switching Characteristics* (DS181)
- Xilinx, *Vitis High-Level Synthesis User Guide* (UG1399) -- HLS design methodology and QoR optimization
- Xilinx, *Fast Fourier Transform LogiCORE IP Product Guide* (PG109) -- `xfft_v9_1` IP core configuration (radix-2, radix-4, pipelined streaming)
- Proakis, J.G. and Manolakis, D.G., *Digital Signal Processing: Principles, Algorithms, and Applications*, 4th ed., Pearson, 2006 -- Radix-4 and split-radix FFT algorithms (Ch. 8)
- Duhamel, P. and Vetterli, M., "Fast Fourier Transforms: A Tutorial Review and a State of the Art," *Signal Processing*, vol. 19, no. 4, pp. 259--299, 1990
