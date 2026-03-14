# Adaptive Beamforming Research

**Purpose:** Survey adaptive beamforming algorithms (MVDR, LCMV, robust beamforming) for the AERIS-10 radar system, with feasibility assessment against Artix-7 FPGA resource constraints and ADAR1000 phase/gain quantization limits.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Beamforming Theory](../01_physics/03_beamforming_theory.md) -- array factor derivation, beam steering, grating lobes
- [Antenna & Beamforming Hardware](../02_hardware/04_antenna_beamforming.md) -- ADAR1000 phase/gain control, beam steering tables
- [FPGA Board](../02_hardware/05_fpga_board.md) -- Artix-7 XC7A100T resource capacity

---

## 1. Current State

### 1.1 Fixed Beam Steering Architecture

The AERIS-10 radar uses **fixed beam steering tables** with no adaptive capability. The beam pattern is determined by pre-computed phase settings stored in firmware beam matrices, as documented in Section 3 of [`02_hardware/04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#3-beam-steering-implementation).

The array factor for the $N = 16$ element uniform linear array (ULA) is (from Eq. (BF-3) in [`01_physics/03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md#2-array-factor)):

$$
AF(\theta) = \sum_{n=0}^{N-1} w_n \, e^{jn\psi} \tag{BF-3}
$$

where $\psi = kd(\sin\theta - \sin\theta_0)$ (Eq. (BF-5)) and $w_n$ are the element weights. In the current system, the weights are uniform ($w_n = 1$) and only the progressive phase shift $\Delta\phi = -kd\sin\theta_0$ (Eq. (BF-4)) is applied.

The firmware defines 31 inter-element phase differences (`phase_differences[31]` in `main.cpp`) mapping to 31 elevation beam positions. Position 15 is broadside ($\Delta\phi = 0$), with symmetric positive and negative steering up to $\Delta\phi = \pm 160°$ (corresponding to $\theta_0 \approx \pm 62.7°$, though the effective scan range is approximately $\pm 33°$ for acceptable beam quality per the grating lobe analysis of Eq. (BF-16)).

### 1.2 ADAR1000 Hardware Constraints

The ADAR1000 beamformer IC imposes two critical precision constraints on any adaptive beamforming scheme:

**Phase quantization:** The ADAR1000 provides 7-bit phase control (128 steps) with a step size of (from Eq. (HW-ANT-1) in [`02_hardware/04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#24-phase-control)):

$$
\Delta\phi_\text{step} = \frac{360°}{128} = 2.8125° \tag{HW-ANT-1}
$$

The maximum phase error per element is $\Delta\phi_\text{step}/2 = 1.40625°$. For $N = 16$ elements, this quantization limits the achievable sidelobe suppression to approximately $-29~\text{dB}$ (predicted by the phase quantization analysis in [`01_physics/03_beamforming_theory.md`](../01_physics/03_beamforming_theory.md)). This is a **hard precision floor** that no adaptive algorithm can overcome without hardware modification.

**Gain quantization:** The ADAR1000 VGA provides 8-bit gain control. The effective gain resolution is approximately $0.5~\text{dB}$ per step. Amplitude tapering for sidelobe control (Section 8 of the beamforming theory) is limited by this resolution.

**SPI update rate:** The firmware writes phase settings via SPI, bypassing the ADAR1000 beam RAM (`MEM_CTRL_BIAS_RAM_BYPASS | MEM_CTRL_BEAM_RAM_BYPASS`). Each 16-element weight update requires 4 ADAR1000 devices x 4 channels x 2 registers (I and Q) = 32 SPI transactions, plus the `LOAD_WORKING` register write per device (4 transactions). At the STM32F746 SPI1 clock rate, each 3-byte SPI transaction takes approximately $1$-$2~\mu\text{s}$, giving a total weight update time of approximately:

$$
T_\text{update} \approx 36 \times 2~\mu\text{s} = 72~\mu\text{s}
$$

This is fast enough for per-beam-position updates but limits the rate of adaptive weight adaptation to the beam scan rate (31 positions per azimuth step).

### 1.3 Current System Limitations

| Aspect | Current State | Impact |
|--------|--------------|--------|
| Weight adaptation | None -- fixed uniform weights | No interference rejection, no adaptive null steering |
| Sidelobe control | Uniform weights: $-13.3~\text{dB}$ first sidelobe (from Eq. (BF-9)) | Interference from sidelobe directions degrades detection |
| Null steering | Not available | Cannot suppress known interferers |
| Pattern optimization | Pre-computed phase tables only | Cannot adapt to changing interference environment |

### 1.4 FPGA Resource Context

The Artix-7 XC7A100T has the following resource capacity (from [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md)):

| Resource | Available | Estimated Used | Remaining |
|----------|-----------|---------------|-----------|
| LUTs | 63,400 | ~16,500 (26%) | ~46,900 |
| DSP48E1 | 240 | ~89 (37%) | ~151 |
| BRAM (36 Kb) | 135 | ~101 (75%) | ~34 |
| Flip-Flops | 126,800 | -- | -- |

**Critical constraint:** BRAM utilization is already at ~75%. Any on-FPGA adaptive beamforming algorithm requiring significant buffer memory faces a tight resource budget. DSP availability (~151 remaining) is the second-most constraining resource for matrix-intensive algorithms.

---

## 2. Literature Survey

### 2.1 MVDR (Minimum Variance Distortionless Response)

The MVDR beamformer, also known as the Capon beamformer, minimizes the output power subject to a distortionless constraint in the look direction:

$$
\min_{\mathbf{w}} \; \mathbf{w}^H \mathbf{R}_{xx} \mathbf{w} \quad \text{subject to} \quad \mathbf{w}^H \mathbf{a}(\theta_0) = 1
$$

where $\mathbf{R}_{xx}$ is the $N \times N$ sample covariance matrix and $\mathbf{a}(\theta_0)$ is the steering vector for the look direction. The closed-form solution is:

$$
\mathbf{w}_\text{MVDR} = \frac{\mathbf{R}_{xx}^{-1} \mathbf{a}(\theta_0)}{\mathbf{a}^H(\theta_0) \mathbf{R}_{xx}^{-1} \mathbf{a}(\theta_0)}
$$

**Computational requirements:**

| Operation | Complexity | For $N = 16$ |
|-----------|-----------|-------------|
| Covariance estimation $\mathbf{R}_{xx}$ | $O(K \cdot N^2)$, $K$ = snapshot count | $K \times 256$ multiply-accumulates |
| Matrix inversion $\mathbf{R}_{xx}^{-1}$ | $O(N^3)$ | 4,096 multiply-accumulates |
| Weight computation | $O(N^2)$ | 256 multiply-accumulates |
| **Total per update** | $O(K \cdot N^2 + N^3)$ | Dominated by covariance estimation |

**Covariance matrix estimation:** MVDR requires $K \geq 2N = 32$ independent snapshots for a well-conditioned $\mathbf{R}_{xx}$ estimate (Rule of thumb: $K \geq 2N$ for reliable inversion). The current system provides $M = 32$ chirps per CPI per beam position, potentially providing exactly the minimum required snapshots if each chirp is treated as an independent spatial sample.

**FPGA implementations:** Published MVDR implementations on Xilinx FPGAs require substantial resources:

| Reference | FPGA | DSP Slices | LUTs | Notes |
|-----------|------|-----------|------|-------|
| MathWorks HDL-optimized MVDR | Kintex UltraScale+ | ~1,000+ | ~50,000+ | 16-element, fixed-point |
| ScienceDirect 2024 | XCKU085 | 4,000+ | -- | Real-time MVDR with matrix inversion |
| Springer 2017 (comparison) | Virtex-7 | ~2,000 | ~30,000 | 8-element array |

These implementations target FPGAs with 2,000-4,000+ DSP slices. The Artix-7 XC7A100T has only 240 DSP48E1 slices, of which ~89 are already used.

**ADAR1000 quantization impact on MVDR:** The MVDR algorithm computes optimal complex weights with full floating-point precision. However, the ADAR1000 quantizes these weights to 7-bit phase ($2.8°$ steps) and 8-bit gain ($0.5~\text{dB}$ steps). This quantization degrades the adaptive null depth. For a $-29~\text{dB}$ phase quantization floor (as predicted for $N = 16$), the achievable null depth of quantized MVDR weights is limited to approximately $-25$ to $-30~\text{dB}$, compared to $-40$ to $-60~\text{dB}$ achievable with unquantized weights. The ADAR1000 quantization, not the algorithm, becomes the precision bottleneck.

**References:**
- Capon, J., "High-resolution frequency-wavenumber spectrum analysis," *Proceedings of the IEEE*, vol. 57, no. 8, pp. 1408-1418, 1969
- Van Trees, H.L., *Optimum Array Processing*, Wiley, 2002, Ch. 6-7
- MathWorks, "FPGA-Based Uniform Linear Array MVDR Beamformer," HDL Coder documentation
- Elgonemy, F. et al., "MVDR Algorithm and FPGA Integration," *ScienceDirect*, 2024

### 2.2 LCMV (Linearly Constrained Minimum Variance)

The LCMV beamformer generalizes MVDR by allowing multiple linear constraints:

$$
\min_{\mathbf{w}} \; \mathbf{w}^H \mathbf{R}_{xx} \mathbf{w} \quad \text{subject to} \quad \mathbf{C}^H \mathbf{w} = \mathbf{f}
$$

where $\mathbf{C}$ is the $N \times L$ constraint matrix and $\mathbf{f}$ is the $L \times 1$ response vector. The closed-form solution is:

$$
\mathbf{w}_\text{LCMV} = \mathbf{R}_{xx}^{-1} \mathbf{C} (\mathbf{C}^H \mathbf{R}_{xx}^{-1} \mathbf{C})^{-1} \mathbf{f}
$$

**Additional capability over MVDR:** LCMV can simultaneously:
- Maintain unity gain in the look direction (same as MVDR)
- Place nulls at known interferer directions (null steering)
- Maintain specified gain in multiple directions (multi-beam)

**Constraint design examples:**
- **Single null:** $\mathbf{C} = [\mathbf{a}(\theta_0), \mathbf{a}(\theta_\text{int})]$, $\mathbf{f} = [1, 0]^T$ -- maintain look direction gain, null at $\theta_\text{int}$
- **Multiple nulls:** Add columns to $\mathbf{C}$ for each interferer direction

**Computational requirements:** Similar to MVDR, with an additional $O(L^3)$ matrix inversion for the constraint subspace. For $L = 2$-$3$ constraints, this overhead is minimal.

**FPGA feasibility:** Same resource requirements as MVDR -- the matrix inversion of $\mathbf{R}_{xx}$ dominates. Published FPGA implementations require comparable DSP/LUT resources (2,000+ DSPs).

**References:**
- Frost, O.L., "An algorithm for linearly constrained adaptive array processing," *Proceedings of the IEEE*, vol. 60, no. 8, pp. 926-935, 1972
- Van Trees, H.L., *Optimum Array Processing*, Wiley, 2002, Ch. 6.6

### 2.3 Hybrid Host-Computed Approach

Given the FPGA resource constraints, a hybrid architecture moves the adaptive weight computation to the host PC while maintaining the ADAR1000 hardware for weight application:

```
Host PC (Python)                    STM32 + ADAR1000
     |                                    |
     v                                    |
Covariance estimation                     |
     |                                    |
     v                                    |
MVDR/LCMV weight computation              |
     |                                    |
     v                                    v
Weight quantization (7-bit phase,    SPI write to ADAR1000
  8-bit gain)  ----USB CDC---->      per beam position
     |                                    |
     v                                    v
Performance monitoring               Beam steering execution
```

**Architecture:** The host PC receives spatial data from the FPGA (individual element signals or covariance statistics), computes optimal weights using NumPy (MVDR/LCMV in Python with full floating-point precision), quantizes the weights to ADAR1000 resolution, and downloads them via USB CDC to the STM32, which writes them to the ADAR1000 via SPI.

**Latency analysis:**

| Stage | Estimated Time |
|-------|---------------|
| USB data transfer (covariance matrix, ~2 KB) | ~0.5-1 ms |
| MVDR weight computation (Python/NumPy, $N = 16$) | ~0.1-0.5 ms |
| Weight quantization | ~0.01 ms |
| USB CDC weight download (32 bytes) | ~0.5-1 ms |
| SPI write to ADAR1000 (36 transactions) | ~0.072 ms |
| **Total round-trip latency** | ~1.2-2.6 ms |

**Update rate constraint:** The hybrid approach can update weights approximately every 1-3 ms. Given that each beam position requires $M = 32$ chirps at PRI $\approx 167~\mu\text{s}$ (long chirp), the CPI duration per beam position is approximately $M \times T_\text{PRI} \approx 5.3~\text{ms}$. The hybrid update latency is shorter than a single CPI, enabling **per-CPI weight adaptation** -- sufficient for slowly varying interference environments.

**Limitations:**
- Cannot adapt faster than the USB round-trip time (~1-3 ms)
- Requires individual element data to be streamed to the host (increases USB bandwidth)
- The current FT601 data pipeline transmits processed range-Doppler maps, not raw per-element data; pipeline modification would be needed

**SPI update time for 16-element weight update** (per Open Question 5 from the research phase): As calculated in Section 1.2, the full 16-element weight update takes approximately $72~\mu\text{s}$ via SPI -- fast enough to not be the bottleneck in the hybrid approach.

### 2.4 Robust Beamforming

Robust beamforming methods reduce sensitivity to steering vector errors and hardware imperfections (including the ADAR1000 phase/gain quantization). These methods are computationally simpler than full MVDR/LCMV.

**Diagonal loading:**

The simplest robust technique adds a scaled identity matrix to the sample covariance:

$$
\mathbf{R}_\text{loaded} = \mathbf{R}_{xx} + \delta \mathbf{I}
$$

where $\delta > 0$ is the diagonal loading factor. This improves the condition number of $\mathbf{R}_{xx}$, reducing sensitivity to:
- Finite sample effects (small $K$)
- Steering vector mismatch (pointing errors, mutual coupling)
- Phase/gain quantization (ADAR1000 precision limits)

The loaded MVDR weight becomes:

$$
\mathbf{w}_\text{robust} = \frac{(\mathbf{R}_{xx} + \delta\mathbf{I})^{-1} \mathbf{a}(\theta_0)}{\mathbf{a}^H(\theta_0)(\mathbf{R}_{xx} + \delta\mathbf{I})^{-1} \mathbf{a}(\theta_0)}
$$

The computational cost is identical to standard MVDR since the loading is applied before inversion. The benefit is improved robustness at the cost of slightly reduced interference rejection.

**Worst-case optimization:**

More sophisticated robust methods optimize performance under worst-case steering vector uncertainty:

$$
\min_{\mathbf{w}} \; \mathbf{w}^H \mathbf{R}_{xx} \mathbf{w} \quad \text{subject to} \quad \min_{\|\mathbf{e}\| \leq \epsilon} |\mathbf{w}^H (\mathbf{a}(\theta_0) + \mathbf{e})| \geq 1
$$

where $\mathbf{e}$ represents the steering vector uncertainty and $\epsilon$ bounds its norm. This can be reformulated as a second-order cone program (SOCP), solvable in polynomial time but computationally heavier than diagonal loading.

**FPGA feasibility for robust beamforming:**

| Approach | Complexity vs. MVDR | FPGA Potential |
|----------|-------------------|----------------|
| Diagonal loading | Same (just add $\delta\mathbf{I}$) | Same as MVDR -- infeasible on Artix-7 |
| Fixed robust weights (pre-computed) | Table lookup only | FEASIBLE (no real-time computation) |
| Worst-case SOCP | Higher than MVDR | INFEASIBLE on Artix-7 |

**Practical approach:** Pre-compute robust beamforming weights offline for the expected interference scenarios, store them in lookup tables, and select the appropriate weight set based on detected interference direction. This avoids real-time matrix inversion entirely but provides limited adaptability.

**References:**
- Li, J., Stoica, P., and Wang, Z., "On robust Capon beamforming and diagonal loading," *IEEE Trans. Signal Processing*, vol. 51, no. 7, pp. 1702-1715, 2003
- Vorobyov, S.A., Gershman, A.B., and Luo, Z.-Q., "Robust adaptive beamforming using worst-case performance optimization," *IEEE Trans. Signal Processing*, vol. 51, no. 2, pp. 313-324, 2003

### 2.5 ADAR1000 Quantization Impact Analysis

The ADAR1000 7-bit phase quantization ($2.8°$ steps) and 8-bit gain control fundamentally limit adaptive beamforming performance. This section quantifies the impact.

**Phase quantization error model:** Each element's applied phase $\phi_n^\text{applied}$ differs from the desired phase $\phi_n^\text{desired}$ by a quantization error $e_n$:

$$
\phi_n^\text{applied} = \phi_n^\text{desired} + e_n, \quad |e_n| \leq \frac{\Delta\phi_\text{step}}{2} = 1.41°
$$

For deterministic rounding (as implemented in `degreesTo7BitPhase()` per Eq. (HW-ANT-5) in [`02_hardware/04_antenna_beamforming.md`](../02_hardware/04_antenna_beamforming.md#34-conversion-to-7-bit-adar1000-register-value)), the phase errors are bounded but not random. The resulting sidelobe floor is approximately:

$$
\text{SLL}_\text{quant} \approx -10\log_{10}\left(\frac{12}{\Delta\phi_\text{step,rad}^2 \cdot N}\right) \approx -29~\text{dB} \quad \text{for } N = 16
$$

This $-29~\text{dB}$ floor means:
- **Adaptive null depth** is limited to approximately $-25$ to $-30~\text{dB}$ regardless of algorithm precision
- **MVDR/LCMV** theoretical null depths of $-40$ to $-60~\text{dB}$ cannot be realized with ADAR1000 hardware
- **Amplitude tapering** for sidelobe control (e.g., Taylor $-30~\text{dB}$, Eq. (BF-18)) approaches the quantization floor -- achievable but with reduced margin

**Gain quantization impact:** The $0.5~\text{dB}$ gain resolution adds a secondary error. For Taylor weights with $\bar{n} = 5$, SLL $= -30~\text{dB}$, the required amplitude taper ratio is approximately 4:1 (12 dB). With $0.5~\text{dB}$ steps, this is represented by 24 discrete gain levels -- adequate resolution for amplitude tapering but limiting for precise adaptive weight control.

**Combined effect:** The phase and gain quantization together establish an effective sidelobe/null floor of approximately $-27$ to $-30~\text{dB}$. Adaptive beamforming provides meaningful improvement only if the desired null depth is within this range. Deep nulls ($< -30~\text{dB}$) are not achievable with the current ADAR1000 hardware.

---

## 3. Gap Analysis

| Gap | Impact | Severity |
|-----|--------|----------|
| **No adaptive weight computation** | Cannot reject interference or steer nulls | HIGH |
| **Fixed beam pattern** (uniform weights only) | First sidelobe at $-13.3~\text{dB}$ -- poor interference rejection | HIGH |
| **No amplitude tapering** | Sidelobes higher than achievable with Taylor/Chebyshev weighting | MEDIUM |
| **No interference detection** | System cannot identify interferer directions for null steering | MEDIUM |
| **ADAR1000 quantization** ($2.8°$ phase, $0.5~\text{dB}$ gain) | Limits achievable null depth to $\sim -29~\text{dB}$ | MEDIUM (hardware constraint) |
| **No per-element data path to host** | Cannot compute covariance matrix for MVDR/LCMV on host | HIGH (for hybrid approach) |

**Prioritized gap summary:**
1. **Adaptive weight computation** (MVDR/LCMV): The fundamental missing capability. Even with ADAR1000 quantization limits, moving from $-13.3~\text{dB}$ sidelobes to $-29~\text{dB}$ null depth is a $16~\text{dB}$ improvement in interference rejection.
2. **Data path for covariance estimation**: The hybrid approach requires per-element spatial data to be available at the host PC, which is not currently supported by the FT601 data pipeline.
3. **Amplitude tapering**: Can be implemented with fixed Taylor/Chebyshev weights as a non-adaptive improvement, using the existing beam matrix architecture.

---

## 4. Feasibility Assessment

### 4.1 MVDR/LCMV on FPGA (Real-Time)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(K \cdot N^2 + N^3)$ per beam position |
| Estimated DSPs required | ~2,000-4,000 (matrix inversion, complex multiply-accumulate) |
| Estimated LUTs required | ~30,000-50,000 (control logic, fixed-point arithmetic) |
| Estimated BRAMs required | ~20-40 ($N \times N$ complex covariance matrix storage) |
| Pipeline integration | Would replace fixed beam steering in `radar_system_top.v` |
| Published reference | ScienceDirect 2024: MVDR on XCKU085 (4,000+ DSPs); MathWorks: MVDR on Kintex UltraScale+ (~1,000 DSPs) |
| **Verdict** | **INFEASIBLE on Artix-7** -- requires ~2,000+ DSPs vs. 151 available |

The Artix-7 XC7A100T with 240 DSP48E1 slices (151 remaining) cannot support real-time MVDR/LCMV matrix operations. Published implementations consistently require Kintex UltraScale+ or Virtex-class FPGAs with 2,000-4,000+ DSP slices. This is a resource gap of approximately 10x-25x.

### 4.2 Hybrid Host-Computed MVDR/LCMV

| Property | Value |
|----------|-------|
| Algorithm complexity | Same as MVDR, but executed in Python/NumPy on host PC |
| FPGA resource cost | Minimal -- only per-element data streaming addition (~2-5 BRAMs for buffering) |
| Host computation time | ~0.1-0.5 ms per weight update (NumPy `linalg.inv` for $16 \times 16$) |
| Round-trip latency | ~1.2-2.6 ms (USB transfer + computation + SPI write) |
| Update rate achievable | Per-CPI (~5.3 ms per beam position) |
| Pipeline modification | Requires streaming per-element ADC data to host via FT601 |
| **Verdict** | **FEASIBLE** -- moves computation off-FPGA, latency acceptable for per-CPI updates |

**Key requirement:** The current FT601 data pipeline transmits processed range-Doppler maps (post-FFT, post-detection). For MVDR covariance estimation, the host needs access to per-element complex samples (pre-beamforming). This requires modifying the FPGA data pipeline to include a per-element data streaming mode -- a significant but bounded engineering effort.

**ADAR1000 quantization limitation:** Even with full-precision MVDR weights computed on the host, the quantized weights applied via ADAR1000 limit null depth to approximately $-29~\text{dB}$. The hybrid approach provides meaningful improvement (from $-13.3~\text{dB}$ uniform sidelobes to $-29~\text{dB}$ adaptive nulls) but cannot achieve the deep nulls ($-40$ to $-60~\text{dB}$) theoretically possible with MVDR.

### 4.3 Robust Beamforming with Diagonal Loading

| Property | Value |
|----------|-------|
| Algorithm complexity | Same as MVDR ($\delta\mathbf{I}$ addition is $O(N)$ overhead) |
| FPGA resource cost | Same as MVDR -- infeasible for real-time on Artix-7 |
| Host-computed variant | Same as hybrid MVDR with improved robustness to quantization errors |
| Pre-computed table variant | Table lookup only -- FEASIBLE on FPGA (~2-4 BRAMs for weight storage) |
| Accuracy improvement | More stable than standard MVDR for small $K$ and quantized weights |
| **Verdict (real-time FPGA)** | **INFEASIBLE** -- same DSP requirements as MVDR |
| **Verdict (host-computed)** | **FEASIBLE** -- preferred over standard MVDR due to quantization robustness |
| **Verdict (pre-computed tables)** | **FEASIBLE** -- limited adaptability but no real-time computation |

### 4.4 Fixed Amplitude Tapering (Non-Adaptive)

| Property | Value |
|----------|-------|
| Algorithm complexity | None (pre-computed weights) |
| FPGA resource cost | Zero additional (weights stored in existing beam matrices) |
| Implementation effort | Modify `initializeBeamMatrices()` to include amplitude weights alongside phase |
| Sidelobe improvement | Taylor $\bar{n} = 5$: from $-13.3~\text{dB}$ to $-30~\text{dB}$ (Eq. (BF-18)) |
| Beamwidth impact | 25% broadening ($\beta_\text{BB} \approx 1.25$) |
| **Verdict** | **FEASIBLE** -- simplest improvement, no real-time computation needed |

### 4.5 Artix-7 Resource Summary

| Approach | DSPs Needed | DSPs Available | LUTs Needed | LUTs Available | Verdict |
|----------|------------|----------------|-------------|----------------|---------|
| Real-time MVDR | ~2,000-4,000 | 151 | ~30,000-50,000 | 46,900 | INFEASIBLE |
| Real-time LCMV | ~2,000-4,000 | 151 | ~30,000-50,000 | 46,900 | INFEASIBLE |
| Real-time robust (SOCP) | >4,000 | 151 | >50,000 | 46,900 | INFEASIBLE |
| Hybrid host-computed | ~0-5 | 151 | ~500-2,000 | 46,900 | FEASIBLE |
| Pre-computed tables | 0 | 151 | ~100-500 | 46,900 | FEASIBLE |
| Fixed amplitude taper | 0 | 151 | 0 | 46,900 | FEASIBLE |

The fundamental constraint is DSP count: real-time matrix inversion for MVDR/LCMV requires 10x-25x more DSP slices than the Artix-7 provides. Moving computation to the host PC eliminates this constraint entirely.

---

## 5. Recommendations

### Priority 1: Hybrid Host-Computed MVDR

- **Expected improvement:** Adaptive null steering with $\sim -29~\text{dB}$ null depth (limited by ADAR1000 quantization), up from $-13.3~\text{dB}$ uniform sidelobes -- approximately $16~\text{dB}$ interference rejection improvement
- **Resource cost:** Minimal FPGA resources (~2-5 BRAMs for per-element data buffering); moderate host CPU load (Python/NumPy)
- **Risk:** MEDIUM -- requires FPGA pipeline modification to stream per-element data; USB bandwidth analysis needed
- **Investigation steps:**
  1. Assess FT601 USB 3.0 bandwidth for streaming $N = 16$ complex element samples per CPI (in addition to existing range-Doppler data)
  2. Prototype MVDR weight computation in Python with diagonal loading for ADAR1000 quantization robustness
  3. Measure actual ADAR1000 null depth with quantized MVDR weights vs. theoretical predictions
  4. Design per-element data streaming mode for the FPGA data pipeline
  5. Validate end-to-end latency (covariance estimation to weight application) against CPI timing

### Priority 2: Robust Beamforming with Diagonal Loading (Host-Computed)

- **Expected improvement:** Same null depth as MVDR but with improved stability against steering vector mismatch, mutual coupling, and ADAR1000 quantization errors
- **Resource cost:** Same as hybrid MVDR; diagonal loading parameter $\delta$ adds negligible computation
- **Risk:** LOW -- diagonal loading is a well-understood regularization technique
- **Investigation steps:**
  1. Implement alongside Priority 1 MVDR (trivial addition of $\delta\mathbf{I}$ to covariance matrix)
  2. Determine optimal $\delta$ as a function of SNR and ADAR1000 quantization error variance
  3. Compare null depth stability between standard MVDR and loaded MVDR across calibration states

### Priority 3: Real-Time FPGA MVDR (Requires FPGA Upgrade)

- **Expected improvement:** Eliminates host-PC latency; enables per-chirp weight adaptation instead of per-CPI
- **Resource cost:** Requires FPGA upgrade to Kintex UltraScale+ or Artix UltraScale+ (per HWRES-06 in Phase 6 research)
- **Risk:** HIGH -- requires PCB redesign, new FPGA bring-up, significant development effort
- **Investigation steps:**
  1. Wait for Phase 6 HWRES-06 (FPGA upgrade path) research results
  2. Identify minimum FPGA with sufficient DSP count for $N = 16$ MVDR (target: 1,000+ DSPs)
  3. Evaluate whether per-chirp adaptation provides meaningful improvement over per-CPI hybrid approach for the AERIS-10 operating environment
  4. Cost-benefit analysis: FPGA upgrade cost vs. hybrid approach performance

### Supplementary: Fixed Amplitude Tapering (Immediate)

- **Expected improvement:** Sidelobe reduction from $-13.3~\text{dB}$ to $-30~\text{dB}$ with Taylor $\bar{n} = 5$ weighting; no adaptive capability but improves baseline interference rejection by $\sim 17~\text{dB}$
- **Resource cost:** Zero -- uses existing beam matrix infrastructure
- **Risk:** LOW -- pre-computed weights, no real-time computation
- **Investigation steps:**
  1. Compute Taylor weights for $N = 16$, $\bar{n} = 5$, SLL $= -30~\text{dB}$
  2. Quantize to ADAR1000 8-bit gain resolution and evaluate sidelobe degradation
  3. Modify `initializeBeamMatrices()` to include gain weights alongside phase settings
  4. Measure beam pattern with amplitude tapering vs. uniform weights

---

## References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- canonical symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Beamforming Theory](../01_physics/03_beamforming_theory.md) -- array factor Eq. (BF-3), steering Eq. (BF-4)/(BF-5), quantization sidelobes, Taylor weighting Eq. (BF-18)
- [Antenna & Beamforming Hardware](../02_hardware/04_antenna_beamforming.md) -- ADAR1000 phase control Eq. (HW-ANT-1), SPI interface, beam matrices
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resource capacity

### Literature
- Capon, J., "High-resolution frequency-wavenumber spectrum analysis," *Proceedings of the IEEE*, vol. 57, no. 8, pp. 1408-1418, 1969
- Frost, O.L., "An algorithm for linearly constrained adaptive array processing," *Proceedings of the IEEE*, vol. 60, no. 8, pp. 926-935, 1972
- Li, J., Stoica, P., and Wang, Z., "On robust Capon beamforming and diagonal loading," *IEEE Trans. Signal Processing*, vol. 51, no. 7, pp. 1702-1715, 2003
- Van Trees, H.L., *Optimum Array Processing*, Wiley, 2002
- Vorobyov, S.A., Gershman, A.B., and Luo, Z.-Q., "Robust adaptive beamforming using worst-case performance optimization," *IEEE Trans. Signal Processing*, vol. 51, no. 2, pp. 313-324, 2003
- Elgonemy, F. et al., "MVDR Algorithm and FPGA Integration," *ScienceDirect*, 2024
- Springer, "MVDR and LCMV Beamformers FPGA Comparison," *Wireless Personal Communications*, 2017
- MathWorks, "FPGA-Based Uniform Linear Array MVDR Beamformer," HDL Coder documentation
