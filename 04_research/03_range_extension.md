# Range Extension via SNR Optimization

**Purpose:** Survey coherent and non-coherent integration techniques for extending AERIS-10 detection range, with range migration analysis for CPI extension proposals and Artix-7 feasibility assessments.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Noise Figure Chain](../01_physics/05_noise_analysis.md) -- system noise figure budget (Eqs. NF-1 through NF-18)
- [FMCW Theory](../01_physics/01_fmcw_theory.md) -- radar range equation and Doppler measurement
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- current Doppler processing implementation (Stages 4--7)

---

## 1. Current State

The AERIS-10 radar detection range is governed by the monostatic radar range equation, Eq. (FMCW-11) in [`01_physics/01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md#signal-to-noise-ratio):

$$
\text{SNR} = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4 k_B T_0 B_n F_\text{total} L} \tag{FMCW-11}
$$

where $F_\text{total}$ is the complete system noise figure from antenna to digital output, traced through the four-stage analog chain and the CIC digital processing chain in Eqs. (NF-1) through (NF-18) of [`01_physics/05_noise_analysis.md`](../01_physics/05_noise_analysis.md). The representative system noise figure is $F_\text{sys} \approx 3.36~\text{dB}$ (placeholder values, pending parameter resolution), with the LNA noise figure dominating per the Friis cascade analysis of Eq. (NF-7) and Eq. (NF-8).

### Current Integration Parameters

The system currently implements coherent integration across $M = 32$ chirps per CPI in the Doppler processor (Stage 7 of the FPGA pipeline, see [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md#9-stage-7-doppler-processing), Eq. (SW-6)):

| Parameter | Symbol | Current Value | Source |
|-----------|--------|---------------|--------|
| Chirps per CPI | $M$ | 32 | `CHIRPS_PER_FRAME` in `doppler_processor.v` |
| Doppler FFT size | $N_\text{Doppler}$ | 32 | `DOPPLER_FFT_SIZE` |
| Range bins (decimated) | $N_\text{rb}$ | 64 | `RANGE_BINS` |
| FFT size (range) | $N_\text{FFT}$ | 1024 | `BUFFER_SIZE` |
| Hamming window | $w[n]$ | 32-point Q15 | Pre-calculated coefficients in `doppler_processor.v` |

The Doppler processor accumulates $M$ chirps in block RAM with chirp-major addressing (Eq. (SW-6)), applies a Hamming window, and computes a 32-point FFT per range bin using the Xilinx `xfft_32` IP core. The coherent integration gain is inherent in the Doppler FFT: coherent summation of $M$ chirps provides an SNR improvement of $M$ (in linear scale), corresponding to $10\log_{10}(32) = 15.1~\text{dB}$.

### Current Range Limitations

With the current integration gain, detection range is limited by:

1. **Noise figure chain:** The system noise figure $F_\text{total}$ from Eq. (NF-18) sets the noise floor against which targets must be detected
2. **Processing gain:** The matched filter provides $G_p = B T_c$ (Eq. (LFM-14) in [`01_physics/02_lfm_waveform_model.md`](../01_physics/02_lfm_waveform_model.md)), and the Doppler FFT adds $10\log_{10}(M) = 15.1~\text{dB}$
3. **ADC dynamic range:** The 8-bit AD9484 limits the quantization noise floor to $-49.9~\text{dBFS}$ (Eq. (NF-11)), constraining the usable dynamic range

No non-coherent integration is implemented. No range migration compensation is available. No adaptive CPI selection exists.

---

## 2. Literature Survey

Range can be extended by increasing the post-processing SNR. From the radar range equation (Eq. (FMCW-11)), the detection range $R$ scales as the fourth root of SNR:

$$
R \propto \text{SNR}^{1/4}
$$

Therefore, an SNR improvement of $\Delta\text{SNR}_\text{dB}$ extends range by a factor:

$$
\frac{R_\text{new}}{R_\text{old}} = 10^{\Delta\text{SNR}_\text{dB} / 40}
$$

### 2.1 Coherent Integration (Longer CPI)

Coherent integration sums the complex (I/Q) returns from $M$ pulses with proper phase alignment. For $M$ coherently integrated pulses with identical target return, the SNR improves by a factor of $M$ relative to a single pulse:

$$
\text{SNR}_\text{CI} = M \cdot \text{SNR}_\text{single}
$$

The current system uses $M = 32$. Extending to larger values of $M$:

| CPI Extension | $M$ | $\Delta\text{SNR}$ (vs. $M{=}32$) | Range Extension Factor | Cumulative $\text{SNR}_\text{CI}$ |
|---------------|-----|-----------------------------------|------------------------|-----------------------------------|
| Current | 32 | Reference (0 dB) | 1.00x | $15.1~\text{dB}$ above single pulse |
| 2x CPI | 64 | $+3.0~\text{dB}$ | 1.19x | $18.1~\text{dB}$ |
| 4x CPI | 128 | $+6.0~\text{dB}$ | 1.41x | $21.1~\text{dB}$ |
| 8x CPI | 256 | $+9.0~\text{dB}$ | 1.68x | $24.1~\text{dB}$ |

**Diminishing returns:** Each doubling of $M$ yields only 3 dB of additional SNR and approximately 19% range extension. The cost in CPI duration (and thus update rate) grows linearly while the range benefit grows logarithmically.

**Doppler resolution improvement:** Increasing $M$ also improves velocity resolution. From Eq. (FMCW-21) in [`01_physics/01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md#velocity-measurement), the velocity resolution is $\Delta v = \lambda / (2 M T_r)$, which halves when $M$ doubles.

### 2.2 Non-Coherent Integration

When coherent integration is limited by target phase instability, platform motion, or CPI duration constraints, **non-coherent integration** provides reduced but still useful gain. Non-coherent integration sums the magnitude-squared (power) of individual pulse returns, discarding phase information:

$$
\text{SNR}_\text{NCI} \approx \sqrt{K} \cdot \text{SNR}_\text{single}
$$

where $K$ is the number of non-coherently integrated looks. The exact gain depends on the probability of detection and false alarm rate; the $\sqrt{K}$ approximation is valid for moderate-to-high SNR regimes (Albersheim's approximation).

**Comparison to coherent integration:**

| Property | Coherent ($M$ pulses) | Non-Coherent ($K$ looks) |
|----------|----------------------|--------------------------|
| SNR gain | $M$ (linear) | $\approx \sqrt{K}$ |
| SNR gain (dB) | $10\log_{10}(M)$ | $\approx 5\log_{10}(K)$ |
| Phase required | Yes (complex I/Q) | No (magnitude only) |
| Doppler resolution | $\lambda / (2 M T_r)$ | Not applicable |
| Target motion tolerance | Low (requires coherent across CPI) | High (tolerates inter-look motion) |

**Post-Doppler non-coherent integration:** A practical approach combines both methods. The Doppler FFT performs coherent integration within each CPI of $M$ chirps, producing a range-Doppler map. Then, multiple consecutive range-Doppler maps are non-coherently integrated (summing magnitude-squared values across maps). This two-stage approach captures the coherent gain within a CPI and adds non-coherent gain across CPIs without requiring phase coherence over long intervals.

For $K$ non-coherently integrated CPIs, the total SNR improvement is approximately:

$$
\text{SNR}_\text{total} \approx M \cdot \sqrt{K} \cdot \text{SNR}_\text{single}
$$

### 2.3 Longer CPI with Range Migration Compensation

**CRITICAL per Pitfall 6:** Every CPI extension proposal must include range migration analysis.

When the CPI duration $T_\text{CPI} = M \cdot T_r$ is extended, fast-moving targets may migrate through one or more range bins during the integration interval. A target at radial velocity $v$ traverses a range distance of $v \cdot T_\text{CPI}$ during the CPI. Range migration exceeds one range bin when:

$$
v \cdot T_\text{CPI} > \Delta R = \frac{c}{2B}
$$

The critical velocity at which range migration equals one range bin is:

$$
v_\text{crit} = \frac{\Delta R}{T_\text{CPI}} = \frac{c}{2 B \cdot M \cdot T_r}
$$

For the current system parameters (with $\Delta R = c / (2B)$ from Eq. (FMCW-19) and CPI duration $T_\text{CPI} = M \cdot T_r$):

| CPI | $M$ | $T_\text{CPI}$ | $v_\text{crit}$ | Range Migration Status |
|-----|-----|-----------------|------------------|------------------------|
| Current | 32 | $32 \cdot T_r$ | $\Delta R / (32 T_r)$ | Baseline |
| 2x | 64 | $64 \cdot T_r$ | $\Delta R / (64 T_r)$ | $v_\text{crit}$ halved |
| 4x | 128 | $128 \cdot T_r$ | $\Delta R / (128 T_r)$ | $v_\text{crit}$ quartered |
| 8x | 256 | $256 \cdot T_r$ | $\Delta R / (256 T_r)$ | $v_\text{crit}$ reduced 8x |

**Maximum unambiguous velocity** is also affected by CPI extension. The unambiguous velocity from Eq. (FMCW-22) in [`01_physics/01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md) is $v_\text{max} = \lambda / (4 T_r)$, which depends on $T_r$ (PRI) and is independent of $M$. However, the Doppler resolution improves to $\Delta v = \lambda / (2 M T_r)$, and range migration may corrupt the Doppler spectrum for targets near $v_\text{max}$.

#### Keystone Transform

The **Keystone transform** is the primary technique for compensating range migration in the slow-time dimension. It operates by resampling the range-compressed data along the slow-time axis to remove the range-velocity coupling:

1. Apply range FFT to each pulse (already performed by matched filter, Stage 5)
2. For each range-frequency bin, resample the slow-time samples using interpolation to compensate for the range walk term $2 v t / c$
3. Apply Doppler FFT on the corrected data

The Keystone transform requires a 2D resampling buffer (all $M$ chirps for all $N_\text{rb}$ range bins) and an interpolation engine. The interpolation is typically linear or sinc-based, requiring multiplier resources.

#### Other Range Migration Compensation Techniques

- **Range-velocity decoupling via second-order compensation:** Corrects both first-order (linear) and second-order (acceleration) range migration terms. More resource-intensive than Keystone.
- **Hough transform detection:** Detects range migration trajectories directly in the range-slow-time plane. Computationally expensive ($O(N^2)$ or higher) and generally not suitable for real-time FPGA implementation.
- **Segmented integration:** Divides the CPI into sub-CPIs short enough to avoid range migration, performs coherent integration within each sub-CPI, then non-coherently integrates across sub-CPIs. This is a practical hybrid approach.

---

## 3. Gap Analysis

| Gap | Current System | Desired Capability | Priority |
|-----|---------------|-------------------|----------|
| Limited coherent integration | $M = 32$ chirps, fixed | Configurable $M$ up to 128+ | High |
| No non-coherent integration | Not implemented | Post-Doppler magnitude-squared accumulation across CPIs | Medium |
| No range migration compensation | Not implemented | Keystone transform or segmented integration for extended CPI | Medium-Low |
| No adaptive CPI selection | Fixed $M = 32$ | Dynamic CPI based on target velocity estimates | Low |
| Fixed Hamming window | 32-point only | Window length matched to CPI | Coupled with CPI extension |

The primary gap is the fixed CPI of $M = 32$ chirps. Doubling to $M = 64$ provides a meaningful 3 dB SNR improvement with modest BRAM cost. Non-coherent integration across CPIs requires minimal additional logic but provides diminishing returns compared to coherent extension. Range migration compensation is relevant only for CPI extensions beyond $M = 128$, where $v_\text{crit}$ drops low enough to affect practical target velocities.

---

## 4. Feasibility Assessment

All resource estimates reference the Artix-7 XC7A100T capacity from [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md#22-resource-utilization), Section 2.1:

| Resource | Total Available | Current Est. Usage | Remaining |
|----------|----------------|-------------------|-----------|
| LUTs | 63,400 | ~16,500 (~26%) | ~46,900 |
| DSP48E1 | 240 | ~88 (~37%) | ~152 |
| Block RAM (36 Kb) | 135 | ~101 (~75%) | ~34 |
| Flip-Flops | 126,800 | -- | -- |

> **Caution:** Resource utilization is based on theoretical estimates from Phase 3, pending Vivado implementation reports. A 30% overhead margin is assumed for all estimates below.

### 4.1 Coherent Integration Extension ($M = 64$)

Extending from $M = 32$ to $M = 64$ requires doubling the Doppler accumulation memory and using a 64-point FFT instead of the current 32-point FFT.

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(M \log M)$ per range bin (FFT) |
| Additional BRAMs | 4--6 (doubling Doppler memory from 2048 to 4096 entries at 32-bit) |
| Additional DSPs | 4--8 (64-point FFT butterfly operations) |
| Additional LUTs | ~500--1,000 (FFT control logic, wider counters) |
| Pipeline integration | Replace `xfft_32` with `xfft_64`; update `DOPPLER_FFT_SIZE`, `CHIRPS_PER_FRAME` |
| Window coefficients | 64-point Hamming stored in LUT (minimal cost) |
| Verdict | **FEASIBLE** -- BRAM cost within remaining headroom |

### 4.2 Coherent Integration Extension ($M = 128$)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(M \log M)$ per range bin |
| Additional BRAMs | 12--16 (quadrupling Doppler memory from 2048 to 8192 entries) |
| Additional DSPs | 8--12 (128-point FFT) |
| Additional LUTs | ~1,500--2,500 |
| Pipeline integration | Replace `xfft_32` with `xfft_128` IP; major Doppler processor redesign |
| Range migration concern | $v_\text{crit}$ quartered -- range migration compensation may be needed for fast targets |
| Verdict | **MARGINAL** -- BRAM-constrained; 12--16 additional BRAMs approaches remaining ~34 headroom |

### 4.3 Non-Coherent Integration (Post-Doppler Accumulation)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N_\text{rb} \times N_\text{Doppler})$ per CPI (magnitude-squared + accumulate) |
| Additional BRAMs | 2--4 (accumulation buffer: $64 \times 32 = 2048$ entries at 32-bit) |
| Additional DSPs | 2--4 (magnitude-squared computation: $I^2 + Q^2$) |
| Additional LUTs | ~500--1,000 (accumulation control, CPI counter) |
| Pipeline integration | Insert after Doppler output (Stage 7), before threshold detection (Stage 8) |
| Accumulation depth | Configurable $K = 2, 4, 8$ CPIs |
| Verdict | **FEASIBLE** -- minimal resource cost, moderate SNR benefit |

### 4.4 Range Migration Compensation (Keystone Transform)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(M \times N_\text{rb})$ per CPI (2D resampling with interpolation) |
| Additional BRAMs | 15--25 (2D buffer: $M \times N_\text{rb}$ at 32-bit; interpolation coefficients) |
| Additional DSPs | 8--16 (interpolation multipliers) |
| Additional LUTs | ~3,000--5,000 (resampling controller, address generation) |
| Pipeline integration | Between range FFT output and Doppler FFT input; requires restructuring pipeline |
| Verdict | **INFEASIBLE on current BRAM budget** -- 15--25 additional BRAMs exceeds margin when combined with CPI extension |

---

## 5. Recommendations

### Priority 1: Coherent Integration Extension to $M = 64$

- **Expected improvement:** $+3.0~\text{dB}$ SNR, 1.19x range extension
- **Resource cost:** 4--6 BRAMs, 4--8 DSPs, ~1,000 LUTs
- **Risk:** LOW -- straightforward FFT IP core substitution; Xilinx provides `xfft_64` IP
- **Investigation steps:**
  1. Generate Xilinx FFT IP core for 64-point transform and verify resource utilization against estimates
  2. Extend Hamming window coefficient table to 64 points
  3. Validate Doppler processor state machine with $M = 64$ chirp accumulation
  4. Characterize range migration impact at $M = 64$ for expected target velocity range
  5. Measure end-to-end pipeline latency impact from doubled CPI duration

### Priority 2: Post-Doppler Non-Coherent Integration

- **Expected improvement:** $\approx +1.5~\text{dB}$ per doubling of $K$ (for $K = 4$ CPIs: $\approx +3~\text{dB}$)
- **Resource cost:** 2--4 BRAMs, 2--4 DSPs, ~1,000 LUTs
- **Risk:** LOW -- simple magnitude-squared accumulation; does not affect existing pipeline
- **Investigation steps:**
  1. Design accumulation buffer for $N_\text{rb} \times N_\text{Doppler}$ magnitude-squared values
  2. Determine optimal $K$ (number of CPIs to accumulate) based on target dynamics and scan rate constraints
  3. Evaluate impact on scan update rate (accumulating $K$ CPIs delays target reports by $K \times T_\text{CPI}$)
  4. Consider exponential moving average as an alternative to fixed-window accumulation for continuous operation

### Priority 3: Range Migration Compensation (Research Stage)

- **Expected improvement:** Enables $M > 128$ without target velocity restrictions
- **Resource cost:** 15--25 BRAMs, 8--16 DSPs, ~5,000 LUTs -- exceeds current BRAM headroom
- **Risk:** HIGH -- BRAM-constrained; requires significant pipeline restructuring
- **Investigation steps:**
  1. Quantify the segmented integration alternative: divide $M = 128$ into four sub-CPIs of $M_\text{sub} = 32$, coherently integrate within each, non-coherently combine across sub-CPIs
  2. Evaluate whether segmented integration achieves sufficient SNR gain without the BRAM cost of Keystone
  3. If Keystone is required, assess FPGA upgrade path (e.g., Artix UltraScale+ with larger BRAM capacity -- see Phase 6 HWRES-06)
  4. Characterize target velocity distribution in the AERIS-10 operating environment to determine whether range migration is a practical concern

---

## References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- $M$, $N_\text{Doppler}$, $N_\text{rb}$, $N_\text{FFT}$, $T_r$, $\lambda$, $\Delta R$
- [Parameter Table](../00_notation/parameter_table.md) -- chirp duration, bandwidth, PRF
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [FMCW Theory](../01_physics/01_fmcw_theory.md) -- radar range equation (Eq. FMCW-11), velocity resolution (Eq. FMCW-21)
- [Noise Figure Chain](../01_physics/05_noise_analysis.md) -- system noise figure (Eqs. NF-1 through NF-18)
- [LFM Waveform Model](../01_physics/02_lfm_waveform_model.md) -- processing gain (Eq. LFM-14)
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- Doppler processor (Stage 7, Eq. SW-6), matched filter (Stage 5)
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resource capacity (Section 2.1)

### External References
- Skolnik, M.I., *Introduction to Radar Systems*, 4th ed., McGraw-Hill, 2008 -- Ch. 2 (radar equation), Ch. 8 (pulse integration)
- Richards, M.A., *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014 -- Ch. 7 (coherent integration), Ch. 9 (non-coherent integration)
- Perry, R.P., DiPietro, R.C., and Fante, R.L., "SAR Imaging of Moving Targets," *IEEE Trans. Aerospace and Electronic Systems*, vol. 35, no. 1, pp. 188--200, Jan. 1999 -- Keystone transform
- Xu, J., Yu, J., Peng, Y., and Xia, X., "Radon-Fourier Transform for Radar Target Detection," *IEEE Trans. Aerospace and Electronic Systems*, vol. 47, no. 2, pp. 1186--1202, Apr. 2011 -- range migration compensation methods
- Li, Y., Zeng, T., and Long, T., "Range Migration Compensation and Doppler Ambiguity Resolution by Keystone Transform," *Multidimensional Systems and Signal Processing*, 2016 -- FPGA-relevant Keystone implementation considerations
