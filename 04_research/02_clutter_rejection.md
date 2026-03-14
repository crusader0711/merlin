# Clutter Rejection for AERIS-10

**Purpose:** Survey clutter rejection approaches -- Moving Target Indication (MTI), Doppler notch filtering, recursive background subtraction, and delay-line cancellation -- with pipeline integration analysis, computational cost, and Artix-7 XC7A100T resource estimates to guide future signal processing improvements.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- Stages 6-7 (matched filter and Doppler processing)
- [FMCW Theory](../01_physics/01_fmcw_theory.md) -- Doppler shift and velocity measurement
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resource capacity

---

## 1. Current State

The AERIS-10 radar has **no clutter rejection mechanism**. The receive pipeline (documented in [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md)) processes digitized IF samples through matched filtering (Stage 6), range bin decimation (Stage 7), and Doppler processing (Stage 8) without any explicit clutter suppression between or within these stages.

### Doppler Processing Baseline

The Doppler processor (`doppler_processor_optimized`, Stage 8 in the pipeline) computes a $N_\text{Doppler}$-point FFT across $M$ chirps for each of $N_\text{rb}$ range bins (see Eq. (SW-6) in [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md#9-stage-7-doppler-processing)):

$$
\text{addr} = \text{chirp\_index} \times N_\text{rb} + \text{range\_bin} \tag{SW-6}
$$

with $N_\text{Doppler} = 32$ Doppler bins, $M = 32$ chirps per CPI, and $N_\text{rb} = 64$ range bins. A Hamming window is applied before the Doppler FFT.

The Doppler FFT provides velocity discrimination: each Doppler bin corresponds to a velocity interval. However, the zero-Doppler bin (bin 0) contains both the returns from stationary targets and ground clutter with no mechanism to separate them. In a ground-based radar operating at X-band ($f_c \approx 10.5~\text{GHz}$, see [Parameter Table](../00_notation/parameter_table.md)), stationary clutter returns from buildings, terrain, vegetation, and ground can be orders of magnitude stronger than target returns.

### Clutter Impact

Without clutter rejection:

1. **Zero-Doppler bin dominated by clutter.** Stationary ground clutter energy is concentrated in Doppler bin 0 and leaks into adjacent bins through the Hamming window sidelobes. The Hamming window provides approximately $-43~\text{dB}$ sidelobe suppression, but strong clutter can still leak into neighboring Doppler bins.

2. **Dynamic range limitation.** The 8-bit ADC ($\text{AD9484}$, see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga)) provides $\sim 49.9~\text{dB}$ SQNR. Strong ground clutter can consume a significant fraction of this dynamic range, reducing the effective dynamic range available for target detection.

3. **Threshold detector degradation.** The fixed threshold detector (Eq. SW-7, $|I| + |Q| > 10{,}000$) is applied to all Doppler bins including the clutter-dominated zero-Doppler bin. Clutter returns routinely exceed this threshold, generating persistent false detections at zero and near-zero Doppler.

4. **No platform motion compensation.** If the radar platform is moving (e.g., vehicle-mounted), the clutter Doppler shifts away from bin 0 by the platform velocity component. Without compensation, clutter energy spreads across multiple Doppler bins.

### Pipeline Integration Context

The clutter rejection insertion point is between the matched filter output (Stage 6) and the Doppler processor input (Stage 8), specifically at or around the range bin decimation stage (Stage 7). This is the standard position in radar processing chains because:

- Clutter rejection operates on slow-time (pulse-to-pulse) data, which becomes available after matched filtering produces range profiles for each chirp
- The Doppler FFT should operate on clutter-suppressed data to maximize the dynamic range of the Doppler spectrum

The matched filter output provides 16-bit signed I/Q range profiles (`pc_i`, `pc_q`, `pc_valid`) at 100 MHz (see [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md#7-stage-5-matched-filter-pulse-compression) Stage 6). After range bin decimation, the data rate is reduced to $N_\text{rb} = 64$ range bins per chirp.

### FPGA Resource Context

Available headroom on the XC7A100T (see Table 2.1 in [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md#22-resource-utilization)):

| Resource | Available Headroom |
|----------|--------------------|
| LUTs | ~46,900 of 63,400 |
| DSP48E1 | ~152 of 240 |
| Block RAM | ~34 of 135 |

BRAM is the most constrained resource. Clutter rejection approaches that require storing full range-Doppler maps in BRAM must be evaluated carefully.

---

## 2. Literature Survey

This section surveys four clutter rejection approaches applicable to the AERIS-10 FMCW radar, each evaluated for effectiveness, computational complexity, and FPGA implementation cost.

### 2.1 MTI -- Moving Target Indication

MTI is the classical approach to clutter rejection in pulsed and FMCW radar systems. Three MTI sub-techniques are applicable to the AERIS-10 architecture.

#### 2.1.1 Background Subtraction

**Algorithm.** Compute a running average of the range profile across chirps and subtract it from each new chirp's range profile:

$$
\bar{x}[n, k] = \beta \cdot \bar{x}[n, k-1] + (1 - \beta) \cdot x[n, k] \tag{CR-1}
$$

$$
y[n, k] = x[n, k] - \bar{x}[n, k] \tag{CR-2}
$$

where $x[n, k]$ is the range profile for range bin $n$ at chirp $k$, $\bar{x}[n, k]$ is the exponentially weighted moving average, $y[n, k]$ is the clutter-suppressed output, and $\beta$ is the forgetting factor ($0.9 \le \beta \le 0.999$ typically).

**Performance.** Background subtraction removes stationary clutter by canceling the DC component of the slow-time signal. The improvement factor $I_\text{MTI}$ (clutter attenuation in dB) depends on the stability of the clutter return:

- Perfectly stationary clutter: $I_\text{MTI} \to \infty$ (limited by ADC quantization)
- Slowly varying clutter (vegetation in wind): $I_\text{MTI} \approx 20-30~\text{dB}$

**Blind speeds.** Background subtraction has no blind speeds -- it only cancels the DC (zero-velocity) component.

**FPGA resources.** Requires storing the running average $\bar{x}[n, k]$ for each range bin. For $N_\text{rb} = 64$ range bins with 16-bit I/Q (32 bits per bin): $64 \times 32 = 2{,}048$ bits = 0.25 KB. This fits in distributed RAM (no BRAM required for 1D). For full 1024-bin range profiles before decimation: $1{,}024 \times 32 = 32{,}768$ bits = 4 KB = approximately 1 BRAM.

#### 2.1.2 FIR High-Pass Filter

**Algorithm.** Apply a FIR high-pass filter to the slow-time samples at each range bin. A 1st-order FIR canceller (single delay-line subtraction) is the simplest MTI filter:

$$
y[n, k] = x[n, k] - x[n, k-1] \tag{CR-3}
$$

A 2nd-order FIR canceller provides deeper notch at zero Doppler:

$$
y[n, k] = x[n, k] - 2x[n, k-1] + x[n, k-2] \tag{CR-4}
$$

**Performance.** The frequency response of the 1st-order canceller is $H(f) = 2j \sin(\pi f T_\text{PRI})$, which has nulls at $f = 0$ and $f = 1/T_\text{PRI}$ (the PRF). The improvement factor for a 1st-order canceller against stationary clutter with Gaussian spectral spread $\sigma_c$ is:

$$
I_\text{MTI} = \frac{1}{1 - \rho} \tag{CR-5}
$$

where $\rho = \exp(-8\pi^2 \sigma_c^2 T_\text{PRI}^2)$ is the correlation coefficient between adjacent chirps. For narrowband clutter ($\sigma_c \ll 1/T_\text{PRI}$), $I_\text{MTI}$ can exceed 40 dB.

**Blind speeds.** The FIR canceller has blind speeds at integer multiples of the ambiguous velocity $v_\text{amb} = \lambda f_r / 2$ where $f_r$ is the PRF and $\lambda$ is the wavelength. At these velocities, target returns are also canceled. A 2nd-order canceller has the same blind speeds but a wider notch (improved clutter rejection at the cost of more velocity blindness near zero Doppler).

**FPGA resources.** 1st-order: ~100-200 LUTs (subtractor, register for delayed sample). 2nd-order: ~200-300 LUTs (two delays, weighted subtraction). No DSP slices needed for simple subtract. BRAM: 1 per range bin set for delay storage ($N_\text{rb} \times 32$ bits per delay tap).

#### 2.1.3 IIR Notch Filter at Zero Doppler

**Algorithm.** A 2nd-order IIR notch filter with a narrow rejection band centered at zero Doppler:

$$
H(z) = \frac{1 - 2\cos(\omega_0) z^{-1} + z^{-2}}{1 - 2r\cos(\omega_0) z^{-1} + r^2 z^{-2}} \tag{CR-6}
$$

where $\omega_0 = 0$ (zero Doppler), $r$ is the pole radius ($0.9 \le r < 1$) controlling notch bandwidth.

**Performance.** The IIR notch provides a narrower rejection band than the FIR canceller, preserving more of the Doppler spectrum for target detection. The notch depth is theoretically infinite at $\omega_0$, with the 3-dB bandwidth controlled by $r$:

$$
\Delta\omega_{3\text{dB}} \approx 2(1 - r) \tag{CR-7}
$$

For $r = 0.95$: $\Delta\omega_{3\text{dB}} \approx 0.1$ radians, corresponding to a narrow notch that removes zero-Doppler clutter while preserving targets at very low (but non-zero) velocities.

**Blind speeds.** The IIR notch only cancels a narrow band around zero Doppler. Targets with velocities outside the notch bandwidth are preserved. No periodically repeated blind speeds (unlike FIR cancellers).

**FPGA resources.** ~300-500 LUTs for the 2nd-order IIR structure with fixed-point coefficients. 2-4 DSP48E1 slices for the multiply-accumulate operations. BRAM: minimal (IIR state is only 2 registers per range bin).

### 2.2 Doppler Notch Filtering

**Algorithm.** A digital notch filter with complex coefficients that can reject clutter at any Doppler frequency, not limited to zero Doppler. The center frequency $\omega_0$ is programmable:

$$
H(z) = \frac{1 - 2\cos(\omega_0) z^{-1} + z^{-2}}{1 - 2r\cos(\omega_0) z^{-1} + r^2 z^{-2}} \tag{CR-8}
$$

For platform motion compensation, $\omega_0$ is set to the Doppler frequency corresponding to the platform velocity:

$$
\omega_0 = \frac{2\pi \cdot 2 v_\text{platform}}{v_\text{amb}} \tag{CR-9}
$$

where $v_\text{platform}$ is the platform velocity and $v_\text{amb}$ is the ambiguous velocity.

**Performance.** Adaptive Doppler notch placement allows clutter rejection when the radar platform is in motion. The improvement factor depends on the accuracy of the platform velocity estimate (from GPS/IMU, see [`02_hardware/07_timing_budget.md`](../02_hardware/07_timing_budget.md)) and the notch bandwidth. A 2nd-order IIR notch provides 30-50 dB rejection at the center frequency.

**Adaptive notch placement.** The notch center frequency can be updated per scan or per CPI using IMU-derived platform velocity. This requires recomputing the filter coefficients $\cos(\omega_0)$ at the update rate -- a trivial computation for the STM32 microcontroller, which can pass the updated coefficient to the FPGA via a control register.

**Blind speeds.** Targets with velocities matching the notch center frequency are suppressed. The notch width determines the velocity resolution loss.

**FPGA resources.** ~200-500 LUTs for a 2nd-order IIR filter with programmable coefficients. 2-4 DSP48E1 slices. Minimal BRAM (coefficient storage only). The programmable coefficient adds a small control register interface (~50 LUTs).

### 2.3 Recursive Background Subtraction

**Algorithm.** Maintain an exponentially weighted moving average (EWMA) of the full range-Doppler map and subtract it from each new frame:

$$
\bar{X}[n, m, k] = \beta \cdot \bar{X}[n, m, k-1] + (1 - \beta) \cdot X[n, m, k] \tag{CR-10}
$$

$$
Y[n, m, k] = X[n, m, k] - \bar{X}[n, m, k] \tag{CR-11}
$$

where $X[n, m, k]$ is the range-Doppler map value at range bin $n$, Doppler bin $m$, and frame $k$.

**Performance.** Recursive background subtraction removes all persistent returns (both stationary and slowly moving clutter) by subtracting the historical average. It is effective against clutter that is stable across multiple CPIs. The forgetting factor $\beta$ controls the adaptation rate: higher $\beta$ provides better clutter cancellation for stationary clutter but slower adaptation to changing environments.

**Advantage over MTI.** Background subtraction in the range-Doppler domain removes persistent returns at any Doppler frequency, not just zero Doppler. This handles scenarios where clutter has non-zero Doppler (e.g., rotating structures, vibrating objects).

**FPGA resources -- BRAM intensive.** Storing the EWMA of the full range-Doppler map requires:

$$
\text{BRAM}_\text{bg} = \frac{N_\text{rb} \times N_\text{Doppler} \times W_\text{data}}{36{,}864} \tag{CR-12}
$$

For $N_\text{rb} = 64$, $N_\text{Doppler} = 32$, and $W_\text{data} = 32$ bits (16-bit I + 16-bit Q):

$$
\text{BRAM}_\text{bg} = \frac{64 \times 32 \times 32}{36{,}864} = \frac{65{,}536}{36{,}864} \approx 1.8~\text{BRAMs} \tag{CR-13}
$$

For the mean values (I and Q stored separately with higher precision, e.g., 32-bit accumulators):

$$
\text{BRAM}_\text{bg,acc} = \frac{64 \times 32 \times 64}{36{,}864} = \frac{131{,}072}{36{,}864} \approx 3.6~\text{BRAMs} \tag{CR-14}
$$

> **BRAM assessment:** At 4-6 BRAMs total (current map + accumulator), this is well within the 34-BRAM headroom. The earlier concern about BRAM intensity is mitigated by the relatively small range-Doppler map dimensions ($64 \times 32$).

### 2.4 Delay-Line Clutter Cancellation (Pulse-Pair)

**Algorithm.** The simplest clutter rejection method: subtract the previous chirp's range profile from the current chirp. This is equivalent to the 1st-order FIR MTI canceller (Eq. CR-3) but specifically described in the context of FMCW pulse-pair processing:

$$
y[n, k] = x[n, k] - x[n, k-1] \tag{CR-15}
$$

A 2-pulse delay canceller subtracts with binomial weights:

$$
y[n, k] = x[n, k] - 2x[n, k-1] + x[n, k-2] \tag{CR-16}
$$

**Performance.** The 1-pulse canceller provides a single null at zero Doppler with improvement factor given by Eq. (CR-5). The 2-pulse canceller provides a double null (wider notch) at zero Doppler. Improvement factors for stationary clutter:

| Canceller | Improvement Factor (typical) | Blind Speeds |
|-----------|------------------------------|--------------|
| 1-pulse | 25-35 dB | At $v = k \cdot v_\text{amb}$, $k = 0, 1, 2, \ldots$ |
| 2-pulse | 35-50 dB | Same as 1-pulse, wider notch |

**Implementation simplicity.** The delay-line canceller is the simplest clutter rejection approach: one register (or small BRAM buffer) per range bin, one subtractor, and no multiply operations. It can be implemented in under 100 LUTs.

**Limitations.** Limited improvement factor compared to IIR notch or multi-pulse MTI. Blind speeds at multiples of $v_\text{amb}$ cannot be avoided with a single-PRF system.

**Pipeline insertion point.** Operates on slow-time data between the matched filter output (Stage 6) and the range bin decimator (Stage 7) -- or equivalently, between range bin decimation (Stage 7) and the Doppler processor (Stage 8). Inserting after decimation reduces BRAM requirements (64 vs. 1024 range bins to buffer).

**FPGA resources.** 1-pulse: ~50-100 LUTs, 0 DSPs, <1 BRAM (64 range bins x 32 bits = 256 bytes). 2-pulse: ~80-150 LUTs, 0 DSPs, <1 BRAM (two delay lines).

---

## 3. Gap Analysis

### 3.1 No Clutter Filtering (Critical)

The current pipeline has no clutter suppression at any stage. Zero-Doppler clutter dominates in ground-based operation and directly corrupts the threshold detector.

**Impact:** Persistent false detections from stationary ground clutter. The fixed threshold (Eq. SW-7) does not distinguish between target returns and clutter returns in the same Doppler bin.

### 3.2 Zero-Doppler Clutter Dominance (Critical)

For a ground-based radar, stationary ground clutter power at X-band can exceed thermal noise by 40-60 dB. The zero-Doppler bin and its sidelobe-contaminated neighbors carry this energy with no attenuation.

**Impact:** Effective detection sensitivity is severely degraded in Doppler bins near zero. Slow-moving targets (pedestrians, vehicles at low speed) are masked by clutter sidelobes.

### 3.3 No Platform Motion Compensation (High)

If the AERIS-10 is deployed on a moving platform, the clutter Doppler shifts away from bin 0. Without compensation, clutter energy spreads across multiple Doppler bins, further degrading detection performance.

**Impact:** Mobile deployment scenarios become impractical without Doppler compensation. The GPS/IMU subsystem (documented in [`02_hardware/07_timing_budget.md`](../02_hardware/07_timing_budget.md)) provides velocity information that could feed an adaptive Doppler notch filter, but no such mechanism exists.

### 3.4 Clutter Environment Not Characterized (Medium)

No measured clutter statistics are available for the AERIS-10 system. The clutter power distribution (Rayleigh, K-distribution, Weibull, log-normal) is unknown. This affects:

- Choice of clutter rejection approach and adaptation parameters
- Forgetting factor $\beta$ for background subtraction
- Notch bandwidth for IIR filters
- Expected improvement factor in the operational environment

### 3.5 No Pre-Doppler Clutter Suppression (Medium)

Clutter rejection is most effective when applied before the Doppler FFT (which distributes clutter energy across the spectrum through windowing sidelobes). The current pipeline has no processing stage between the matched filter and the Doppler processor dedicated to clutter suppression.

---

## 4. Feasibility Assessment

All resource estimates use available headroom: ~46,900 LUTs, ~152 DSP48E1 slices, ~34 Block RAMs. Estimates include 30% conservative margin.

### 4.1 2-Pulse Delay-Line Canceller (1st Order)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(1)$ per sample (single subtraction) |
| Estimated LUTs | ~50-100 |
| Estimated DSPs | 0 |
| Estimated BRAMs | <1 (64 range bins x 32 bits = 256 bytes in distributed RAM) |
| Improvement factor | 25-35 dB (stationary clutter) |
| Pipeline integration | Between range bin decimation (Stage 7) and Doppler processor (Stage 8); operates on decimated range profile |
| Published reference | Skolnik Ch. 15; standard delay-line canceller architecture |
| Verdict | **FEASIBLE** -- trivial resource cost, immediate benefit |

### 4.2 MTI FIR High-Pass Filter (2nd Order)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(1)$ per sample (weighted subtraction of 2 delayed samples) |
| Estimated LUTs | ~200-300 |
| Estimated DSPs | 0-2 (for weighted subtraction; can use LUT-based multiply) |
| Estimated BRAMs | <1 (two delay lines, 64 range bins each) |
| Improvement factor | 35-50 dB (stationary clutter) |
| Pipeline integration | Same as delay-line canceller (between Stage 7 and Stage 8) |
| Published reference | Skolnik Ch. 15; MathWorks MTI reference implementation |
| Verdict | **FEASIBLE** -- minimal resource cost, significant improvement over 1st order |

### 4.3 IIR Notch Filter (2nd Order, Zero Doppler)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(1)$ per sample (2nd-order IIR recursion) |
| Estimated LUTs | ~300-500 |
| Estimated DSPs | 2-4 (multiply-accumulate for IIR coefficients) |
| Estimated BRAMs | <1 (IIR state: 2 registers per range bin, 64 bins = 512 bytes) |
| Improvement factor | 30-50 dB (narrowband clutter); tunable notch width via pole radius $r$ |
| Pipeline integration | Same insertion point; provides narrower notch than FIR, preserving more low-Doppler targets |
| Published reference | Standard IIR notch filter design; coefficients computable from desired notch frequency and bandwidth |
| Verdict | **FEASIBLE** -- moderate resource cost, excellent selectivity |

### 4.4 Adaptive Doppler Notch Filter (Programmable Center Frequency)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(1)$ per sample (same IIR structure, programmable coefficients) |
| Estimated LUTs | ~350-550 (IIR + coefficient register interface) |
| Estimated DSPs | 2-4 |
| Estimated BRAMs | <1 |
| Improvement factor | 30-50 dB at programmable Doppler frequency |
| Pipeline integration | Same insertion point; STM32 updates notch center frequency via control register based on GPS/IMU velocity |
| Published reference | Standard adaptive notch filter; coefficient update computed on STM32 |
| Verdict | **FEASIBLE** -- slight additional complexity over fixed notch; enables mobile platform operation |

### 4.5 Recursive Background Subtraction (Range-Doppler Domain)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(1)$ per cell (EWMA update + subtraction) |
| Estimated LUTs | ~500-800 (EWMA logic, subtraction, forgetting factor multiply) |
| Estimated DSPs | 2-4 (forgetting factor multiplication) |
| Estimated BRAMs | 4-6 (map storage + accumulator, per Eq. CR-14) |
| Improvement factor | 20-40 dB (depends on clutter stationarity and $\beta$) |
| Pipeline integration | Operates after Doppler FFT (Stage 8) output; requires full range-Doppler map buffering |
| Published reference | Standard EWMA background subtraction; widely used in video surveillance and radar |
| Verdict | **FEASIBLE** -- moderate BRAM cost (4-6 of 34 available); removes persistent returns at any Doppler |

> **BRAM note:** At 4-6 BRAMs, this approach consumes 12-18% of available BRAM headroom. If combined with a CFAR implementation (2-4 BRAMs from SWRES-01), total additional BRAM usage would be 6-10 BRAMs, leaving 24-28 BRAMs for other improvements. This is within acceptable limits but should be tracked.

### 4.6 Feasibility Summary

| Approach | LUTs (est.) | % Available | DSPs | BRAMs | Verdict |
|----------|-------------|-------------|------|-------|---------|
| Delay-line canceller (1st) | 50-100 | <1% | 0 | <1 | **FEASIBLE** |
| MTI FIR filter (2nd) | 200-300 | <1% | 0-2 | <1 | **FEASIBLE** |
| IIR notch (zero Doppler) | 300-500 | ~1% | 2-4 | <1 | **FEASIBLE** |
| Adaptive Doppler notch | 350-550 | ~1% | 2-4 | <1 | **FEASIBLE** |
| Background subtraction | 500-800 | ~2% | 2-4 | 4-6 | **FEASIBLE** |

All approaches are well within the Artix-7 resource headroom. The clutter rejection problem is fundamentally less resource-intensive than CFAR detection because the algorithms are simple linear operations applied per range bin or per range-Doppler cell.

---

## 5. Recommendations

### Priority 1: 2-Pulse Delay-Line Canceller (Immediate, Simplest)

- **Expected improvement:** 25-35 dB stationary clutter suppression; eliminates dominant zero-Doppler clutter in ground-based operation
- **Resource cost:** ~50-100 LUTs, 0 DSPs, <1 BRAM (trivial)
- **Risk:** LOW -- single subtraction operation per range bin; well-understood algorithm with decades of deployment history
- **Recommended investigation steps:**
  1. **Clutter measurement campaign** (FIRST STEP): Collect raw range profile data from the AERIS-10 in a representative deployment environment to characterize clutter power, spectral spread, and temporal stability
  2. Implement 1-pulse canceller between range bin decimation (Stage 7) and Doppler processor (Stage 8) as a proof-of-concept
  3. Measure improvement factor using recorded data before and after cancellation
  4. Evaluate whether blind speed limitations at multiples of $v_\text{amb}$ are acceptable for the operational velocity range

### Priority 2: MTI FIR Filter (2nd Order)

- **Expected improvement:** 35-50 dB clutter suppression; wider notch than 1st-order canceller provides better rejection of slowly fluctuating clutter (vegetation, sea surface)
- **Resource cost:** ~200-300 LUTs, 0-2 DSPs, <1 BRAM
- **Risk:** LOW -- extension of Priority 1 with an additional delay tap and weighted subtraction
- **Recommended investigation steps:**
  1. Compare 1st-order vs. 2nd-order canceller improvement factors using measured clutter data from the measurement campaign
  2. Evaluate the velocity blindness penalty: 2nd-order canceller has a wider rejection notch, potentially masking slow-moving targets
  3. Consider implementing both 1st and 2nd order as selectable modes (minimal additional resource cost)

### Priority 3: Adaptive Doppler Notch Filter

- **Expected improvement:** 30-50 dB clutter rejection at any programmable Doppler frequency; enables mobile platform operation with GPS/IMU-driven notch placement
- **Resource cost:** ~350-550 LUTs, 2-4 DSPs, <1 BRAM
- **Risk:** MEDIUM -- requires integration with GPS/IMU velocity estimate via STM32 control interface; notch bandwidth selection requires tuning based on measured clutter spectral width
- **Recommended investigation steps:**
  1. Quantify the STM32-to-FPGA coefficient update latency to determine maximum supportable platform acceleration
  2. Determine appropriate notch bandwidth ($\Delta\omega_{3\text{dB}}$) from measured clutter spectral characteristics
  3. Evaluate whether the GPS/IMU velocity accuracy (documented in [`02_hardware/07_timing_budget.md`](../02_hardware/07_timing_budget.md)) is sufficient for precise notch placement

### Priority 4: Recursive Background Subtraction (Complementary)

- **Expected improvement:** 20-40 dB rejection of persistent returns at any Doppler frequency, including non-zero-Doppler persistent interference
- **Resource cost:** ~500-800 LUTs, 2-4 DSPs, 4-6 BRAMs
- **Risk:** MEDIUM -- operates post-Doppler FFT, so it complements (not replaces) pre-Doppler MTI filtering; forgetting factor $\beta$ requires tuning to balance adaptation speed vs. clutter rejection depth
- **Recommended investigation steps:**
  1. Implement only after Priorities 1-3 are evaluated, as pre-Doppler MTI may provide sufficient clutter rejection alone
  2. Determine optimal forgetting factor $\beta$ from measured clutter temporal statistics
  3. Evaluate BRAM budget impact in conjunction with planned CFAR implementation (SWRES-01)

### Recommended First Step: Clutter Measurement Campaign

Before implementing any clutter rejection algorithm, characterize the AERIS-10 clutter environment through field measurements. This campaign should:

1. Record raw range profile data (pre-detection) across multiple deployment sites (urban, suburban, open field)
2. Compute clutter power spectral density to determine spectral spread $\sigma_c$
3. Characterize clutter amplitude distribution (Rayleigh, K-distribution, Weibull) for each site type
4. Measure clutter-to-noise ratio (CNR) as a function of range and elevation angle
5. Assess clutter temporal stability (decorrelation time) to determine forgetting factor $\beta$ and MTI improvement factor limits

This measurement data will inform:
- Selection of clutter rejection approach and parameters
- CFAR variant selection (SWRES-01) for the measured clutter distribution
- Validation of implemented clutter rejection improvement factors

---

## References

[1] M. I. Skolnik, *Introduction to Radar Systems*, 4th ed. New York, NY, USA: McGraw-Hill, 2008, ch. 15 (MTI and Pulse-Doppler Radar).

[2] M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed. New York, NY, USA: McGraw-Hill, 2014, ch. 8 (Moving Target Indication).

[3] MathWorks, "Ground Clutter Mitigation with Moving Target Indication (MTI) Radar," Radar Toolbox Documentation. [Online]. Available: https://www.mathworks.com/help/radar/ug/ground-clutter-mitigation-with-moving-target-indication-mti-radar.html

[4] W. L. Melvin and J. A. Scheer, Eds., *Principles of Modern Radar: Advanced Techniques*. Raleigh, NC, USA: SciTech Publishing, 2013, ch. 2 (STAP and Clutter Mitigation).

[5] B. R. Mahafza, *Radar Systems Analysis and Design Using MATLAB*, 3rd ed. Boca Raton, FL, USA: CRC Press, 2013, ch. 8 (MTI and Pulse Doppler Radar).

[6] Xilinx, "Artix-7 FPGAs Data Sheet: DC and AC Switching Characteristics," DS181, v1.28, Feb. 2022.
