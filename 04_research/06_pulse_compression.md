# Pulse Compression Improvements

**Purpose:** Survey NLFM waveform optimization, windowed matched filter techniques, and stretch processing enhancements for improving AERIS-10 pulse compression performance, with DAC feasibility analysis and Artix-7 resource assessments.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [LFM Waveform Model](../01_physics/02_lfm_waveform_model.md) -- chirp signal mathematics, matched filter theory, sidelobe structure
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- matched filter implementation (Stages 4--5)
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resource capacity and DAC interface

---

## 1. Current State

The AERIS-10 system transmits a Linear Frequency Modulated (LFM) chirp waveform defined by Eq. (LFM-1) in [`01_physics/02_lfm_waveform_model.md`](../01_physics/02_lfm_waveform_model.md). The chirp sweeps linearly across bandwidth $B$ during the pulse duration $T_c$, with chirp rate $\mu = B / T_c$ (Eq. (LFM-3)).

### Current Matched Filter Implementation

Pulse compression is performed by the matched filter in Stage 5 of the FPGA pipeline ([`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md#7-stage-5-matched-filter-pulse-compression), Sections 7.1--7.3). The implementation uses frequency-domain convolution via the overlap-save method:

| Parameter | Value | Source |
|-----------|-------|--------|
| FFT size | $N_\text{FFT} = 1024$ | `BUFFER_SIZE` in `matched_filter_multi_segment.v` |
| Long chirp samples | 3000 | `LONG_CHIRP_SAMPLES` |
| Short chirp samples | 50 | `SHORT_CHIRP_SAMPLES` |
| Segments (long chirp) | $N_\text{seg} = 4$ | Eq. (SW-4): $\lceil(3000 - 128) / 896\rceil = 4$ |
| Overlap | $L_\text{overlap} = 128$ | `OVERLAP_SAMPLES` |
| Reference format | 16-bit I/Q | Stored in `.mem` files |
| Processing chain | Forward FFT, spectral multiply, inverse FFT | `matched_filter_processing_chain` |

The reference chirp coefficients are stored in block RAM and loaded by `chirp_memory_loader_param` (Stage 4). The reference is the complex conjugate of the transmitted chirp spectrum -- the standard matched filter definition per Eq. (LFM-9).

### Current Sidelobe Performance

The current system uses a **rectangular window** (no tapering) on the LFM chirp, resulting in the sinc-like compressed pulse envelope described by Eq. (LFM-20). The peak sidelobe level (PSL) is:

$$
\text{PSL}_\text{rect} = -13.3~\text{dB} \tag{LFM-21}
$$

This first sidelobe at $-13.3~\text{dB}$ below the mainlobe peak can mask weak targets adjacent to strong reflectors. The sidelobe structure follows the $\operatorname{sinc}(B\tau)$ pattern from the matched filter output envelope (Eq. (LFM-19)), with sidelobes decaying as $1 / (B\tau)$.

### Current Waveform Generation

The transmit chirp waveform is generated from `.mem` files loaded into FPGA block RAM and output via the 120 MHz DAC interface (`dac_interface_single`):

| Parameter | Value | Source |
|-----------|-------|--------|
| DAC resolution | 8-bit | `dac_interface_single.v` |
| DAC clock | $f_\text{DAC} = 120~\text{MHz}$ | Eq. (HW-FPGA-2) in [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md#32-120-mhz-dac-domain) |
| Waveform storage | `.mem` files (I/Q) | `chirp_memory_loader_param.v` |
| Long chirp segments | 3 segments | Segment files `long_chirp_seg[0-2]_{i,q}.mem` |
| Short chirp segments | 1 segment | `short_chirp_{i,q}.mem` |

The 8-bit DAC resolution and 120 MHz sample rate are critical constraints for any waveform modification proposal.

---

## 2. Literature Survey

### 2.1 NLFM Waveform Optimization

**Nonlinear Frequency Modulation (NLFM)** achieves low sidelobe levels without the SNR loss associated with windowed LFM. Instead of applying a window to the matched filter (which reduces the coherent gain), NLFM shapes the frequency modulation function itself so that the matched filter output inherently has low sidelobes.

#### Principle

In an LFM chirp, the instantaneous frequency sweeps linearly: $f_i(t) = f_c + \mu t$ (Eq. (LFM-4)). In NLFM, the sweep is nonlinear:

$$
f_i(t) = f_c + g(t)
$$

where $g(t)$ is a nonlinear frequency function designed such that the matched filter output has sidelobes below a target level (typically $-40$ to $-50~\text{dB}$). The key insight is that the instantaneous bandwidth (local frequency sweep rate) controls the local time-bandwidth product, and by spending more time at the band edges (slower sweep rate), the effective spectral weighting resembles a window function -- but applied in the transmit domain rather than the receive domain, avoiding SNR loss.

#### Optimization Methods

1. **Genetic Algorithm (GA) Optimization:** The frequency function $g(t)$ is parameterized (e.g., as a polynomial or piecewise-linear function) and optimized via genetic algorithms to minimize peak sidelobe level. The 2025 Scientific Reports paper demonstrates GA-optimized NLFM achieving $-45~\text{dB}$ sidelobes with less than $0.1~\text{dB}$ mainlobe widening compared to windowed LFM.

2. **Spline-Based Frequency Functions:** The frequency modulation is represented as a B-spline with control points optimized for sidelobe performance. Spline representations provide smooth frequency transitions that are favorable for DAC generation and Doppler tolerance.

3. **Piecewise-Linear FM (PLFM):** The frequency modulation is divided into segments with different (but constant) sweep rates. Each segment's sweep rate and duration are optimized for sidelobe performance. This is the simplest NLFM variant and maps directly to the current `.mem` file architecture -- each segment's samples can be pre-computed and stored.

#### Doppler Tolerance

A critical consideration for FMCW radar is Doppler tolerance. LFM chirps are inherently Doppler-tolerant because the ambiguity function ridge (Eq. (LFM-24)) runs along $\nu = -\mu\tau$, meaning a Doppler shift simply displaces the range peak without distorting it. NLFM waveforms generally have **reduced Doppler tolerance** because the non-uniform sweep rate causes the ambiguity function to lose the clean ridge structure.

For the AERIS-10 system, Doppler tolerance must be evaluated against the maximum expected Doppler shift to ensure NLFM sidelobe performance is maintained across the target velocity range.

#### NLFM Sidelobe Performance Summary

| Method | Achievable PSL | Mainlobe Widening | SNR Loss | Doppler Tolerance |
|--------|---------------|-------------------|----------|-------------------|
| GA-optimized NLFM | $-45$ to $-50~\text{dB}$ | $< 5\%$ | $< 0.1~\text{dB}$ | Reduced (design-dependent) |
| Spline NLFM | $-40$ to $-45~\text{dB}$ | $< 10\%$ | $< 0.2~\text{dB}$ | Moderate |
| Piecewise-linear FM | $-35$ to $-40~\text{dB}$ | $< 8\%$ | $< 0.1~\text{dB}$ | Good (closer to LFM) |

### 2.2 Windowed Matched Filter Improvements

An alternative to NLFM is applying a window function to the matched filter reference in the frequency domain. This reduces sidelobes at the cost of SNR loss (processing loss) and mainlobe widening.

The current system uses no window on the matched filter (equivalent to a rectangular window). Applying standard window functions to the reference chirp spectrum before the inverse FFT in the matched filter processing chain would achieve the following:

| Window | Peak Sidelobe Level | Mainlobe Width Factor | Processing Loss |
|--------|--------------------|-----------------------|-----------------|
| Rectangular (current) | $-13.3~\text{dB}$ | $1.0 \times (1/B)$ | $0~\text{dB}$ |
| Hamming | $-42.8~\text{dB}$ | $1.50 \times (1/B)$ | $1.34~\text{dB}$ |
| Hanning | $-31.5~\text{dB}$ | $1.44 \times (1/B)$ | $1.42~\text{dB}$ |
| Taylor ($\bar{n} = 5$, SLL $= -35~\text{dB}$) | $-35~\text{dB}$ | $1.28 \times (1/B)$ | $0.76~\text{dB}$ |
| Taylor ($\bar{n} = 5$, SLL $= -40~\text{dB}$) | $-40~\text{dB}$ | $1.35 \times (1/B)$ | $1.02~\text{dB}$ |
| Chebyshev ($-40~\text{dB}$) | $-40~\text{dB}$ | $1.39 \times (1/B)$ | $1.10~\text{dB}$ |

These values are consistent with the windowing analysis in Section 5 of [`01_physics/02_lfm_waveform_model.md`](../01_physics/02_lfm_waveform_model.md#5-sidelobe-structure-and-windowing), Eq. (LFM-21).

**Implementation approach:** The window is applied to the reference chirp spectrum (frequency-domain) before the spectral multiplication in the matched filter processing chain. This requires:

1. Pre-computing window coefficients for the $N_\text{FFT} = 1024$-point frequency domain
2. Storing coefficients in a LUT (1024 entries at 16-bit = 2 KBytes, easily fits in BRAM or distributed RAM)
3. Multiplying each reference spectrum bin by the window coefficient during the spectral multiply stage

**Tradeoff:** Windowed matched filtering exchanges SNR for sidelobe suppression. The processing loss column quantifies the coherent gain reduction -- this loss is subtracted from the processing gain $G_p = B T_c$ of Eq. (LFM-14). For the Taylor window at $-35~\text{dB}$ SLL, the $0.76~\text{dB}$ processing loss is modest and provides a $21.7~\text{dB}$ sidelobe improvement over the current rectangular window.

### 2.3 Stretch Processing Optimization

For FMCW radar, the dechirp (stretch processing) operation described in Eq. (FMCW-14) of [`01_physics/01_fmcw_theory.md`](../01_physics/01_fmcw_theory.md) is already the baseline signal processing approach. The AERIS-10 DDC (Stage 2) performs digital down-conversion from $f_\text{IF}$ to baseband, and the range FFT resolves targets in the beat frequency domain.

Potential stretch processing improvements include:

1. **Zero-Padding for Interpolated FFT:** Extending the $N_\text{FFT} = 1024$-point FFT with zero-padding to 2048 or 4096 points provides interpolated frequency bins, improving the precision of beat frequency estimation. This does not improve true range resolution (which is set by bandwidth $B$ per Eq. (LFM-18)) but reduces the scalloping loss from discrete FFT bins.

2. **Chirp-Z Transform (CZT) for Fine Resolution:** The CZT computes the DFT over a restricted frequency band with finer frequency spacing than the FFT. For targets of interest at specific range intervals, the CZT can provide sub-bin frequency resolution. Resource cost is higher than the FFT ($O(N \log N)$ but with larger constants due to the complex exponential multiplication).

3. **Frequency Estimation Enhancement:** Parabolic interpolation or Gaussian fitting on the FFT magnitude peak provides sub-bin frequency estimation with negligible additional resource cost (3 multiplications and 1 division per peak).

---

## 3. Gap Analysis

| Gap | Current System | Desired Capability | Priority |
|-----|---------------|-------------------|----------|
| High sidelobes | $-13.3~\text{dB}$ PSL (rectangular window) | $-35$ to $-45~\text{dB}$ PSL | High |
| SNR loss from windowing | Not applicable (no window) | Low-loss sidelobe reduction | High |
| No NLFM capability | LFM only; fixed `.mem` coefficients | NLFM waveform generation | Medium |
| Fixed matched filter reference | Reference chirp loaded from `.mem` | Configurable reference with window options | Medium |
| No sub-bin range estimation | Nearest-bin FFT only | Interpolated frequency estimation | Low |

The primary gap is the $-13.3~\text{dB}$ sidelobe level, which limits the system's ability to detect weak targets near strong reflectors. A $-35~\text{dB}$ or better PSL would provide adequate masking margin for most scenarios. The windowed matched filter is the lowest-risk approach to address this gap, while NLFM offers superior performance if the DAC precision constraint can be met.

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

### 4.1 Windowed Matched Filter (Taylor/Hamming)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N_\text{FFT})$ -- one additional multiply per frequency bin |
| Additional BRAMs | 0--1 (1024 x 16-bit window coefficients = 2 KB; may fit in distributed RAM) |
| Additional DSPs | 2 (window coefficient multiply for I and Q channels) |
| Additional LUTs | ~200--400 (coefficient addressing, control logic) |
| Pipeline integration | Add window multiply into spectral multiply stage of `matched_filter_processing_chain` |
| Configurable windows | Multiple window coefficient sets can share the same LUT with a select input |
| Verdict | **FEASIBLE** -- minimal resource cost; can be integrated into existing spectral multiply |

### 4.2 NLFM Waveform Generation

| Property | Value |
|----------|-------|
| Algorithm complexity | Pre-computed offline; FPGA only stores and outputs samples |
| Additional BRAMs | 0 (replaces existing `.mem` files with NLFM coefficients; same sample count) |
| Additional DSPs | 0 (no change to DAC output path) |
| Additional LUTs | ~100--200 (coefficient addressing unchanged; possible format adaptation) |
| Matched filter update | NLFM reference chirp must replace LFM reference in `chirp_memory_loader_param` |
| Pipeline integration | Transparent -- chirp memory architecture unchanged |

**DAC Precision Analysis (Open Question 4):**

The current DAC is an 8-bit interface operating at $f_\text{DAC} = 120~\text{MHz}$ (Eq. (HW-FPGA-2)). NLFM waveform fidelity is constrained by:

1. **Amplitude quantization:** 8 bits provide $2^8 = 256$ amplitude levels. The NLFM waveform's nonlinear phase modulation requires precise amplitude and phase representation. For the I/Q components output to the DAC, each channel has only 256 levels.

2. **Phase quantization impact on sidelobes:** The achievable sidelobe level is limited by the DAC resolution. For an $n$-bit DAC, the quantization noise floor is approximately $-6.02n - 1.76~\text{dB}$ below full scale (Eq. (NF-11) in [`01_physics/05_noise_analysis.md`](../01_physics/05_noise_analysis.md)). For $n = 8$ bits, this gives $-49.9~\text{dBFS}$.

3. **NLFM coefficient precision requirement:** To achieve $-45~\text{dB}$ PSL, the waveform samples must be accurate to better than $-45~\text{dB}$ relative to the mainlobe. With an 8-bit DAC providing a $-49.9~\text{dBFS}$ noise floor, the quantization-limited PSL is approximately $-45~\text{dB}$ for well-designed NLFM waveforms, leaving only ~5 dB of margin.

4. **Practical assessment:** Published NLFM implementations on 8-bit DACs report achieving $-35$ to $-40~\text{dB}$ sidelobes in practice, degraded from the theoretical $-45~\text{dB}$ by quantization effects, DAC nonlinearity (DNL/INL), and clock jitter. This is still significantly better than the current $-13.3~\text{dB}$ rectangular window performance.

| DAC Parameter | Value | Impact on NLFM |
|---------------|-------|----------------|
| Resolution | 8-bit | Limits PSL to approximately $-40~\text{dB}$ in practice |
| Sample rate | 120 MHz | Adequate for NLFM (same as LFM baseline) |
| SQNR floor | $-49.9~\text{dBFS}$ | Sets hard limit on achievable PSL |
| Practical PSL (8-bit NLFM) | $-35$ to $-40~\text{dB}$ | Degraded from theoretical by quantization |

**Verdict:** **FEASIBLE with degraded sidelobe performance** -- NLFM can be implemented with no additional FPGA resources (same memory architecture), but the 8-bit DAC limits achievable PSL to approximately $-35$ to $-40~\text{dB}$ rather than the theoretical $-45$ to $-50~\text{dB}$.

### 4.3 Stretch Processing Improvements

#### Zero-Padded FFT

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N \log N)$ for $N = 2048$ or $4096$ |
| Additional BRAMs | 10--20 (doubled or quadrupled FFT buffer) |
| Additional DSPs | 8--16 (larger FFT butterfly) |
| Additional LUTs | ~2,000--4,000 |
| Pipeline integration | Replace 1024-point FFT with 2048 or 4096-point FFT IP |
| Benefit | Reduced scalloping loss (~0.5 dB improvement); NO true resolution improvement |
| Verdict | **MARGINAL** -- high BRAM cost for modest benefit; not recommended unless combined with other FFT changes |

#### Parabolic Peak Interpolation

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(1)$ per detected peak (3 multiplies, 1 divide) |
| Additional BRAMs | 0 |
| Additional DSPs | 1--2 (for division/multiply) |
| Additional LUTs | ~200--500 |
| Pipeline integration | Post-detection refinement; no impact on main pipeline |
| Benefit | Sub-bin frequency accuracy (~0.1 bin width) |
| Verdict | **FEASIBLE** -- minimal cost, useful for range accuracy improvement |

---

## 5. Recommendations

### Priority 1: Windowed Matched Filter (Immediate Improvement)

- **Expected improvement:** Sidelobe reduction from $-13.3~\text{dB}$ to $-35~\text{dB}$ (Taylor, $\bar{n} = 5$) with only $0.76~\text{dB}$ processing loss
- **Resource cost:** 0--1 BRAM, 2 DSPs, ~400 LUTs (< 1% of available resources)
- **Risk:** LOW -- well-understood technique, minimal pipeline changes, reversible (switch back to rectangular window by loading unity coefficients)
- **Investigation steps:**
  1. Pre-compute Taylor window coefficients ($\bar{n} = 5$, SLL $= -35~\text{dB}$) at 1024 points in 16-bit fixed-point
  2. Integrate window coefficient multiply into `matched_filter_processing_chain` spectral multiply stage
  3. Validate sidelobe performance using range profile measurements with known point targets
  4. Compare Taylor, Hamming, and Chebyshev windows on measured data to select optimal tradeoff
  5. Evaluate impact of processing loss on detection range (0.76 dB loss reduces range by factor $10^{-0.76/40} \approx 0.957$, or ~4% range reduction)

### Priority 2: NLFM Waveform (Better Sidelobes, DAC Validation Required)

- **Expected improvement:** Sidelobes of $-35$ to $-40~\text{dB}$ with $< 0.1~\text{dB}$ processing loss (vs. $0.76~\text{dB}$ for Taylor window)
- **Resource cost:** 0 additional BRAMs, 0 DSPs, ~200 LUTs (replaces existing chirp coefficients)
- **Risk:** MEDIUM -- requires DAC feasibility validation for 8-bit/120 MHz constraint; Doppler tolerance must be characterized
- **Investigation steps:**
  1. Simulate NLFM waveform with 8-bit quantization to determine achievable PSL with the current DAC resolution
  2. Compare GA-optimized, spline, and piecewise-linear NLFM approaches for the AERIS-10 bandwidth and chirp duration
  3. Characterize Doppler tolerance of candidate NLFM waveforms against the maximum expected target velocity
  4. Generate NLFM `.mem` files and verify compatibility with `chirp_memory_loader_param` architecture
  5. Update matched filter reference coefficients to match the NLFM transmit waveform
  6. If 8-bit DAC proves insufficient for target PSL, evaluate as part of ADC/DAC upgrade research (Phase 6 HWRES-04)

### Priority 3: Stretch Processing Improvements (Low Priority)

- **Expected improvement:** Sub-bin range accuracy via parabolic interpolation (~0.1 bin width improvement)
- **Resource cost:** ~500 LUTs, 1--2 DSPs
- **Risk:** LOW -- post-detection processing, does not affect main pipeline
- **Investigation steps:**
  1. Implement parabolic peak interpolation as a post-detection refinement stage
  2. Evaluate whether sub-bin accuracy provides meaningful improvement for the AERIS-10 range resolution
  3. Zero-padded FFT is NOT recommended due to BRAM cost -- parabolic interpolation achieves similar accuracy at far lower cost

---

## References

### Project Documentation
- [Symbol Table](../00_notation/symbol_table.md) -- $B$, $T_c$, $\mu$, $N_\text{FFT}$, $w[n]$, $\Delta R$
- [Parameter Table](../00_notation/parameter_table.md) -- chirp bandwidth, pulse duration, DAC specifications
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [LFM Waveform Model](../01_physics/02_lfm_waveform_model.md) -- LFM chirp (Eq. LFM-1), matched filter (Eqs. LFM-8, LFM-9), pulse compression (Eq. LFM-16), sidelobes (Eq. LFM-21), ambiguity function (Eq. LFM-23)
- [Noise Figure Chain](../01_physics/05_noise_analysis.md) -- ADC quantization noise (Eq. NF-11)
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- matched filter (Stage 5, Eqs. SW-4), reference chirp loading (Stage 4)
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resources (Section 2.1), DAC domain (Section 3.2, Eq. HW-FPGA-2)

### External References
- Skolnik, M.I., *Introduction to Radar Systems*, 4th ed., McGraw-Hill, 2008 -- Ch. 8 (pulse compression, sidelobe reduction)
- Richards, M.A., *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014 -- Ch. 6 (matched filtering, windowing), Ch. 4 (waveform design)
- Levanon, N. and Mozeson, E., *Radar Signals*, Wiley, 2004 -- Ch. 6 (NLFM waveform design), Ch. 7 (mismatched filtering)
- Scientific Reports, "Optimization of Nonlinear Frequency Modulated Waveforms for Radar Applications," 2025 -- GA-optimized NLFM achieving $-45~\text{dB}$ sidelobes
- Collins, T. and Atkins, P., "Nonlinear Frequency Modulation Chirps for Active Sonar," *IEE Proc. Radar, Sonar & Navigation*, vol. 146, no. 6, pp. 312--316, Dec. 1999 -- foundational NLFM design methodology
- Harris, F.J., "On the Use of Windows for Harmonic Analysis with the Discrete Fourier Transform," *Proc. IEEE*, vol. 66, no. 1, pp. 51--83, Jan. 1978 -- comprehensive window function comparison
