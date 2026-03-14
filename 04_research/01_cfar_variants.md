# CFAR Variant Comparison for AERIS-10

**Purpose:** Survey Cell-Averaging (CA), Ordered-Statistic (OS), Greatest-Of CA (GOCA), and Smallest-Of CA (SOCA) CFAR variants with false alarm performance, detection probability, computational cost, and Artix-7 XC7A100T resource estimates to guide future detection subsystem improvements.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [FPGA Pipeline](../03_software/01_fpga_pipeline.md) -- current threshold detection (Stage 9)
- [Detection Theory](../01_physics/04_detection_theory.md) -- CFAR derivation (Eqs. DET-17 through DET-24)
- [FPGA Board](../02_hardware/05_fpga_board.md) -- XC7A100T resource capacity

---

## 1. Current State

The AERIS-10 radar currently uses a **fixed magnitude threshold** for target detection, NOT a true CFAR algorithm. The detection logic in `radar_system_top.v` computes the L1 norm (Manhattan distance) of the Doppler output and compares it against a hardcoded constant (see Eq. (SW-7) in [`03_software/01_fpga_pipeline.md`](../03_software/01_fpga_pipeline.md#10-stage-8-threshold-detection)):

$$
|I| + |Q| > 10{,}000 \tag{SW-7}
$$

where $I$ and $Q$ are the 16-bit signed Doppler output components (`rx_doppler_real`, `rx_doppler_imag`). Despite the Verilog variable names using CFAR terminology (`rx_cfar_detection`, `cfar_valid`, `cfar_counter`), the implementation is a simple magnitude comparator with no adaptive threshold computation.

### Consequences of Fixed Threshold Detection

1. **Uncontrolled false alarm rate.** The probability of false alarm $P_{fa}$ (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)) varies directly with the noise power level. When noise increases (e.g., due to interference, temperature changes, or clutter), $P_{fa}$ rises uncontrollably; when noise decreases, $P_{fa}$ drops and detection sensitivity is wasted.

2. **No reference cell architecture.** True CFAR detectors estimate local noise power from $N_\text{ref}$ reference cells (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)) surrounding the cell under test (CUT). The current system has no reference cells, guard cells, or sliding window mechanism.

3. **No clutter-edge handling.** At boundaries between clutter regions and clear regions, the fixed threshold either misses targets (threshold too high relative to local noise) or generates excessive false alarms (threshold too low).

4. **No multi-target robustness.** When multiple targets are present, the fixed threshold cannot adapt to the local interference environment around each cell under test.

### CFAR Theory Baseline

The theoretical foundation for CFAR detection is derived in [`01_physics/04_detection_theory.md`](../01_physics/04_detection_theory.md). The key results are:

- **Noise power estimate** (Eq. DET-17): $\hat{P}_n = \frac{1}{N_\text{ref}} \sum_{i=1}^{N_\text{ref}} T_i$ where $T_i = |x_i|^2$
- **CFAR test** (Eq. DET-18): $T_\text{CUT} \gtrless \alpha \cdot \hat{P}_n$
- **False alarm probability** (Eq. DET-19): $P_{fa} = \left(1 + \frac{\alpha}{N_\text{ref}}\right)^{-N_\text{ref}}$
- **Threshold multiplier** (Eq. DET-20): $\alpha = N_\text{ref}\!\left(P_{fa}^{-1/N_\text{ref}} - 1\right)$
- **CFAR loss** (Eq. DET-24): $L_\text{CFAR} \approx \frac{1}{N_\text{ref}} \cdot \frac{P_d}{(1 - P_d) \ln(P_{fa})}$

These derivations assume i.i.d. exponential reference cells (Rayleigh-distributed complex noise) in a homogeneous environment.

### FPGA Resource Context

The XC7A100T provides the following resources (see Table 2.1 in [`02_hardware/05_fpga_board.md`](../02_hardware/05_fpga_board.md#22-resource-utilization)):

| Resource | Total Available | Estimated Used | Estimated Available | Utilization |
|----------|----------------|----------------|---------------------|-------------|
| LUTs ($N_\text{LUT}$) | 63,400 | ~16,500 | ~46,900 | ~26% |
| DSP48E1 ($N_\text{DSP}$) | 240 | ~88 | ~152 | ~37% |
| Block RAM ($N_\text{BRAM}$) | 135 | ~101 | ~34 | ~75% |
| Flip-Flops ($N_\text{FF}$) | 126,800 | -- | -- | -- |

> **Note:** Resource estimates are theoretical (pending Vivado implementation reports). BRAM is the most constrained resource. All feasibility assessments below use conservative margins (30% overhead on theoretical estimates per Phase 5 research recommendations).

---

## 2. Literature Survey

This section surveys four CFAR variants plus a multi-mode architecture, each evaluated for detection performance, computational complexity, and FPGA implementation cost.

### 2.1 CA-CFAR (Cell-Averaging CFAR)

**Algorithm.** The CA-CFAR estimates local noise power as the arithmetic mean of the square-law detector outputs across all $N_\text{ref}$ reference cells:

$$
\hat{P}_n = \frac{1}{N_\text{ref}} \sum_{i=1}^{N_\text{ref}} T_i \tag{CFAR-1}
$$

The threshold is set as $T_\text{thresh} = \alpha \cdot \hat{P}_n$, where the threshold multiplier $\alpha$ is computed from Eq. (DET-20) in [`01_physics/04_detection_theory.md`](../01_physics/04_detection_theory.md) to achieve the desired $P_{fa}$.

**Assumed clutter distribution.** CA-CFAR assumes the reference cells contain i.i.d. samples from an exponential distribution (equivalently, the complex noise envelope is Rayleigh-distributed). This assumption holds for thermal noise and homogeneous sea clutter but breaks down for land clutter (which often follows K-distribution or Weibull statistics) and at clutter boundaries.

**Detection performance.** In homogeneous Rayleigh clutter, CA-CFAR achieves the optimal detection probability among all CFAR detectors -- it is the maximum-likelihood estimate of noise power. The detection probability $P_d$ vs. SNR follows the Marcum Q-function curves in Eqs. (DET-21) and (DET-22), with an additional CFAR loss of approximately $1/N_\text{ref}$ (see Eq. DET-24). For $N_\text{ref} = 32$ and $P_d = 0.9$, the CFAR loss is approximately 0.8 dB.

**1D vs. 2D CFAR.** The AERIS-10 produces a range-Doppler map with $N_\text{rb} = 64$ range bins and $N_\text{Doppler} = 32$ Doppler bins. A 1D CA-CFAR applies the sliding window along the range dimension only, treating each Doppler bin independently. A 2D CA-CFAR uses reference cells in both range and Doppler dimensions, providing better noise estimation in non-homogeneous environments at the cost of increased reference cell count and BRAM usage.

For the AERIS-10 map dimensions, a 1D CFAR with $N_\text{ref} = 32$ and $N_\text{guard} = 4$ processes 64 range bins per Doppler column. A 2D CFAR with an $8 \times 4$ reference window ($N_\text{ref} = 32$ cells in a 2D annular region) provides better clutter characterization but requires storing multiple rows of the range-Doppler map simultaneously.

**Computational complexity.** $O(N_\text{ref})$ per cell under test. For a sliding window implementation, the running sum can be maintained incrementally: add the new leading cell, subtract the departing trailing cell, requiring only 2 additions per CUT regardless of $N_\text{ref}$.

**FPGA implementation.** Published CA-CFAR FPGA implementations report 8,260 LUTs on a Stratix II for a 16-reference-cell configuration [1]. The implementation includes the sliding window buffer, magnitude computation, threshold multiplication, and comparison logic. Scaling to 32 reference cells adds buffer depth but minimal logic.

### 2.2 OS-CFAR (Ordered-Statistic CFAR)

**Algorithm.** The OS-CFAR replaces the arithmetic mean with an order statistic. The reference cells are sorted by magnitude, and the $k$-th smallest value is used as the noise power estimate:

$$
\hat{P}_n = T_{(k)} \tag{CFAR-2}
$$

where $T_{(1)} \le T_{(2)} \le \cdots \le T_{(N_\text{ref})}$ is the sorted sequence of reference cell magnitudes, and $k$ is the rank parameter (typically $k \approx 3N_\text{ref}/4$).

The threshold multiplier $\alpha_\text{OS}$ for OS-CFAR differs from the CA-CFAR multiplier and must be computed numerically or from tabulated values based on $N_\text{ref}$, $k$, and the desired $P_{fa}$.

**Assumed clutter distribution.** OS-CFAR is designed for non-homogeneous environments. It provides robustness against up to $N_\text{ref} - k$ interfering targets in the reference window, because the order statistic rejects the largest values. The noise estimate remains valid as long as fewer than $N_\text{ref} - k$ reference cells are contaminated by targets. The algorithm assumes the underlying noise follows a Rayleigh distribution, but the order-statistic approach provides inherent robustness to deviations, including moderate K-distribution and Weibull clutter scenarios.

**Detection performance.** In homogeneous environments, OS-CFAR incurs higher CFAR loss than CA-CFAR (typically 1-2 dB additional) because the order statistic is a less efficient estimator of the noise power than the sample mean. However, in multi-target environments, OS-CFAR maintains controlled $P_{fa}$ while CA-CFAR's false alarm rate degrades due to target masking.

**$P_d$ vs. SNR.** For a given $P_{fa}$, OS-CFAR requires approximately 1-2 dB higher SNR than CA-CFAR to achieve the same $P_d$ in homogeneous environments. This penalty decreases as $N_\text{ref}$ increases.

**Computational complexity.** $O(N_\text{ref} \log N_\text{ref})$ due to the sorting requirement. FPGA implementations typically use bitonic sorting networks, which require $\frac{1}{2} N_\text{ref} (\log_2 N_\text{ref})^2$ comparator stages. For $N_\text{ref} = 32$: approximately 400 comparators.

**FPGA implementation.** OS-CFAR FPGA implementations require approximately 2-3x the LUT count of CA-CFAR for equivalent reference window sizes due to the sorting network. For $N_\text{ref} = 32$, the bitonic sort alone requires approximately 5,000-8,000 LUTs, plus the threshold computation and comparison logic.

### 2.3 GOCA-CFAR (Greatest-Of Cell-Averaging CFAR)

**Algorithm.** GOCA-CFAR splits the reference window into leading and trailing halves, computes the cell average in each half independently, and selects the greater of the two estimates:

$$
\hat{P}_n = \max\!\left(\frac{1}{N_\text{ref}/2} \sum_{i=1}^{N_\text{ref}/2} T_i^{\text{lead}},\;\; \frac{1}{N_\text{ref}/2} \sum_{i=1}^{N_\text{ref}/2} T_i^{\text{lag}}\right) \tag{CFAR-3}
$$

The threshold multiplier $\alpha_\text{GO}$ is adjusted to maintain the desired $P_{fa}$ given the max-selection operation, which inflates the threshold relative to standard CA-CFAR.

**Assumed clutter distribution.** GOCA-CFAR assumes Rayleigh clutter in each half-window. It is specifically designed for clutter-edge scenarios where the leading and trailing windows see different noise levels. By selecting the maximum, GOCA prevents the lower-noise half from setting a threshold that is too low relative to the higher-noise half, thus avoiding false alarms at clutter edges.

**Detection performance.** In homogeneous environments, GOCA-CFAR has slightly worse $P_d$ than CA-CFAR (approximately 0.5-1 dB additional CFAR loss) because the max-selection systematically overestimates noise power. At clutter edges, GOCA maintains the designed $P_{fa}$ while CA-CFAR's $P_{fa}$ can increase by orders of magnitude. The tradeoff is increased target masking: when a strong target appears in one half-window, the elevated noise estimate from that half is always selected, potentially masking weaker targets nearby.

**Computational complexity.** $O(N_\text{ref})$ -- same as CA-CFAR plus one comparison operation. The leading and trailing sums can be computed with the same incremental sliding window technique.

**FPGA implementation.** GOCA-CFAR requires approximately 10-20% more LUTs than CA-CFAR: two independent half-window accumulators, a comparator for the max selection, and the same threshold multiplication and comparison logic. The additional hardware is minimal.

### 2.4 SOCA-CFAR (Smallest-Of Cell-Averaging CFAR)

**Algorithm.** SOCA-CFAR is the dual of GOCA: it selects the smaller of the two half-window averages:

$$
\hat{P}_n = \min\!\left(\frac{1}{N_\text{ref}/2} \sum_{i=1}^{N_\text{ref}/2} T_i^{\text{lead}},\;\; \frac{1}{N_\text{ref}/2} \sum_{i=1}^{N_\text{ref}/2} T_i^{\text{lag}}\right) \tag{CFAR-4}
$$

**Assumed clutter distribution.** Same as GOCA-CFAR (Rayleigh in each half-window). SOCA is designed for multi-target scenarios: when one half-window contains interfering targets that elevate its average, the min-selection uses the uncontaminated half-window instead.

**Detection performance.** SOCA-CFAR reduces target masking compared to CA-CFAR and GOCA-CFAR: if interfering targets are present in only one half-window, the other half provides a clean noise estimate. However, at clutter edges, SOCA uses the lower-noise half-window, setting a threshold that is too low for the higher-noise region and dramatically increasing $P_{fa}$. This makes SOCA unsuitable as a standalone detector in clutter-edge environments.

**$P_d$ vs. SNR.** In homogeneous environments, SOCA-CFAR has comparable or slightly better $P_d$ than GOCA-CFAR because the min-selection does not inflate the noise estimate as aggressively.

**Computational complexity.** $O(N_\text{ref})$ -- identical to GOCA-CFAR with a min comparator instead of max.

**FPGA implementation.** Resource requirements are essentially identical to GOCA-CFAR (~10-20% more LUTs than CA-CFAR). The only difference is the min vs. max comparison.

### 2.5 Multi-Mode CFAR

**Algorithm.** Multi-mode CFAR runs CA, OS, and GO (or a subset) in parallel and selects the detection result based on a mode-switching criterion. The mode selector evaluates the ratio of the two half-window averages or the spread of the reference cells to determine the local environment type (homogeneous, clutter edge, multi-target) and selects the appropriate CFAR variant.

**Assumed clutter distribution.** Adapts across Rayleigh and non-Rayleigh environments by switching between variants optimized for each case.

**Detection performance.** Multi-mode CFAR achieves near-optimal performance across diverse environments by combining the strengths of each variant: CA for homogeneous, GO for clutter edges, OS for multi-target. The detection probability penalty in any single environment is small (<1 dB) compared to the environment-matched single-mode variant.

**Computational complexity.** $O(N_\text{ref} \log N_\text{ref})$ (dominated by the OS-CFAR sorting requirement).

**FPGA implementation.** A multi-mode CM-CM CFAR processor was reported to require 23,741 LUTs on an Artix-7 XC7A100T [2]. This includes parallel CA, OS, and GO processing paths, mode-switching logic, and output multiplexing. This represents approximately 37% of the total LUT capacity and approximately 51% of the estimated available LUT headroom (~46,900 LUTs).

### 2.6 Comparison Summary

| Variant | $P_{fa}$ Control | Multi-Target Robustness | Clutter Edge | Complexity | Relative LUTs |
|---------|-----------------|------------------------|--------------|------------|---------------|
| CA-CFAR | Optimal (homogeneous) | Poor (masking) | Poor (inflated $P_{fa}$) | $O(N_\text{ref})$ | 1x (baseline) |
| OS-CFAR | Good | Excellent ($N_\text{ref} - k$ interferers) | Moderate | $O(N_\text{ref} \log N_\text{ref})$ | 2-3x |
| GOCA-CFAR | Good (edges) | Poor (masking) | Excellent | $O(N_\text{ref})$ | 1.1-1.2x |
| SOCA-CFAR | Poor (edges) | Good | Poor (inflated $P_{fa}$) | $O(N_\text{ref})$ | 1.1-1.2x |
| Multi-mode | Near-optimal | Good-Excellent | Good-Excellent | $O(N_\text{ref} \log N_\text{ref})$ | 5-8x |

---

## 3. Gap Analysis

The following gaps are prioritized by impact on system detection performance, listed from highest to lowest priority.

### 3.1 No Adaptive Threshold (Critical)

The fixed threshold of 10,000 (Eq. SW-7) provides no adaptation to changing noise conditions. Any true CFAR implementation would address this gap by estimating local noise power from reference cells and setting the threshold as $\alpha \cdot \hat{P}_n$.

**Impact:** False alarm rate varies by orders of magnitude with noise level changes. In high-noise conditions, the detector either floods with false alarms or (if the threshold is set conservatively) misses real targets.

### 3.2 Uncontrolled False Alarm Rate (Critical)

Without CFAR, the system cannot guarantee a specified $P_{fa}$. For operational radar systems, $P_{fa}$ is a design parameter (typically $10^{-4}$ to $10^{-8}$) that determines the threshold through the Neyman-Pearson framework (see Eqs. DET-2 and DET-3 in [`01_physics/04_detection_theory.md`](../01_physics/04_detection_theory.md)).

### 3.3 No Clutter-Edge Handling (High)

Ground-based operation at X-band (see [Parameter Table](../00_notation/parameter_table.md)) produces clutter environments with distinct boundaries (buildings, terrain features). The fixed threshold cannot adapt at these boundaries. GOCA-CFAR or multi-mode CFAR would address this gap.

### 3.4 No Multi-Target Robustness (Medium)

When multiple targets occupy nearby range-Doppler cells, a CA-CFAR reference window containing target energy would elevate the noise estimate and mask weaker targets. OS-CFAR or SOCA-CFAR would provide robustness against this failure mode.

### 3.5 No 2D Detection Structure (Medium)

The current detector operates on individual Doppler output samples without considering the 2D structure of the range-Doppler map ($64 \times 32$). A 2D CFAR would exploit both range and Doppler dimensions for noise estimation.

### 3.6 Unknown Clutter Distribution (Low -- Requires Data)

The optimal CFAR variant depends on the clutter statistics (Rayleigh, K-distribution, Weibull). No measured clutter data from the AERIS-10 system is currently available. A clutter characterization campaign would inform variant selection.

---

## 4. Feasibility Assessment

All resource estimates below use the available headroom from Section 1: ~46,900 LUTs, ~152 DSP48E1 slices, ~34 Block RAMs. Estimates include a 30% conservative margin over published or theoretical values per the Phase 5 research methodology.

### 4.1 CA-CFAR with 32 Reference Cells, 4 Guard Cells

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N_\text{ref})$ per cell under test |
| Estimated LUTs | ~3,000-4,000 (sliding window + magnitude + threshold multiply + comparator) |
| Estimated DSPs | 2-4 (magnitude computation, threshold multiplication) |
| Estimated BRAMs | 2-4 (reference cell buffer for 1D window; 6-10 for 2D window) |
| Clock cycles per detection | ~$N_\text{ref} + N_\text{guard} + 1 = 37$ per CUT (pipelined: 1 per CUT after fill) |
| Pipeline integration | Replaces inline threshold in `radar_system_top.v` (Stage 9), inserted after Doppler output |
| Published reference | 8,260 LUTs for 16-cell CA-CFAR on Stratix II [1]; scaling to 32 cells adds ~500 LUTs |
| Verdict | **FEASIBLE** -- well within Artix-7 headroom (< 9% of available LUTs, < 3% DSPs, < 12% BRAMs) |

### 4.2 OS-CFAR with 32 Reference Cells

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N_\text{ref} \log N_\text{ref})$ per cell under test |
| Estimated LUTs | ~8,000-12,000 (bitonic sorting network + threshold logic) |
| Estimated DSPs | 2-4 (magnitude, threshold multiply) |
| Estimated BRAMs | 3-6 (reference cell buffer + sorting workspace) |
| Clock cycles per detection | ~$\frac{1}{2} N_\text{ref} (\log_2 N_\text{ref})^2 = 400$ comparisons; pipelined throughput depends on network depth |
| Pipeline integration | Same as CA-CFAR (Stage 9 replacement) |
| Published reference | 2-3x CA-CFAR LUT count for equivalent $N_\text{ref}$ in published FPGA implementations |
| Verdict | **FEASIBLE** -- fits within headroom (~17-26% of available LUTs) but significant resource cost |

> **BRAM note:** OS-CFAR BRAM requirements are modest (3-6 blocks). This does not trigger the BRAM constraint flag (threshold: 20 BRAMs per Pitfall 1).

### 4.3 GOCA-CFAR with 32 Reference Cells (16 per half)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N_\text{ref})$ per cell under test |
| Estimated LUTs | ~3,500-5,000 (two half-window accumulators + max comparator + threshold logic) |
| Estimated DSPs | 2-4 (same as CA-CFAR) |
| Estimated BRAMs | 2-4 (same as CA-CFAR) |
| Clock cycles per detection | ~$N_\text{ref}/2 + 2 = 18$ per CUT (pipelined: 1 per CUT after fill) |
| Pipeline integration | Same as CA-CFAR (Stage 9 replacement) |
| Published reference | ~10-20% LUT overhead vs. CA-CFAR from published comparisons |
| Verdict | **FEASIBLE** -- marginal cost increase over CA-CFAR (<11% of available LUTs) |

### 4.4 SOCA-CFAR with 32 Reference Cells (16 per half)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N_\text{ref})$ per cell under test |
| Estimated LUTs | ~3,500-5,000 (identical to GOCA-CFAR, min instead of max) |
| Estimated DSPs | 2-4 |
| Estimated BRAMs | 2-4 |
| Clock cycles per detection | ~18 per CUT (pipelined: 1 per CUT after fill) |
| Pipeline integration | Same as CA-CFAR (Stage 9 replacement) |
| Published reference | Same resource profile as GOCA-CFAR |
| Verdict | **FEASIBLE** -- same resource profile as GOCA-CFAR |

### 4.5 Multi-Mode CFAR (CA + OS + GO Parallel)

| Property | Value |
|----------|-------|
| Algorithm complexity | $O(N_\text{ref} \log N_\text{ref})$ (OS sorting dominates) |
| Estimated LUTs | ~23,000-31,000 (parallel CA, OS, GO paths + mode selector) |
| Estimated DSPs | 6-12 (parallel magnitude/threshold paths) |
| Estimated BRAMs | 8-14 (buffers for parallel paths) |
| Clock cycles per detection | Variable by selected mode; parallel processing allows single-cycle output selection |
| Pipeline integration | Same as CA-CFAR (Stage 9 replacement) |
| Published reference | 23,741 LUTs on Artix-7 XC7A100T [2] |
| Verdict | **MARGINAL** -- requires ~49-66% of available LUT headroom; feasible but leaves limited margin for other improvements |

> **BRAM flag:** Multi-mode CFAR at 8-14 BRAMs approaches but does not exceed the 20-BRAM caution threshold. However, combined with other proposed improvements (clutter rejection, range extension), total BRAM usage may become a binding constraint.

### 4.6 Feasibility Summary

| Variant | LUTs (est.) | % Available | DSPs | BRAMs | Verdict |
|---------|-------------|-------------|------|-------|---------|
| CA-CFAR | 3,000-4,000 | 6-9% | 2-4 | 2-4 | **FEASIBLE** |
| OS-CFAR | 8,000-12,000 | 17-26% | 2-4 | 3-6 | **FEASIBLE** |
| GOCA-CFAR | 3,500-5,000 | 7-11% | 2-4 | 2-4 | **FEASIBLE** |
| SOCA-CFAR | 3,500-5,000 | 7-11% | 2-4 | 2-4 | **FEASIBLE** |
| Multi-mode | 23,000-31,000 | 49-66% | 6-12 | 8-14 | **MARGINAL** |

---

## 5. Recommendations

### Priority 1: CA-CFAR (Immediate Feasibility)

- **Expected improvement:** Controlled $P_{fa}$ (e.g., $10^{-6}$) regardless of noise level, replacing the uncontrolled false alarm behavior of the fixed threshold
- **Resource cost:** ~3,000-4,000 LUTs, 2-4 DSPs, 2-4 BRAMs (< 9% of available headroom)
- **Risk:** LOW -- well-understood algorithm with multiple published FPGA implementations; the CA-CFAR derivation is already documented in the project (Eqs. DET-17 through DET-20)
- **Recommended investigation steps:**
  1. Determine reference cell count ($N_\text{ref}$) and guard cell count ($N_\text{guard}$) based on the range-Doppler map dimensions ($N_\text{rb} = 64$ range bins, $N_\text{Doppler} = 32$ Doppler bins)
  2. Evaluate 1D CFAR (range-only) vs. 2D CFAR (range and Doppler) based on processing latency requirements and BRAM availability
  3. Simulate CA-CFAR detection performance ($P_d$ vs. SNR) for the AERIS-10 noise floor using the noise figure analysis from [`01_physics/05_noise_analysis.md`](../01_physics/05_noise_analysis.md)
  4. Prototype in Python/MATLAB using recorded range-Doppler data before committing to Verilog RTL

### Priority 2: GOCA-CFAR (Clutter-Edge Enhancement)

- **Expected improvement:** Maintained $P_{fa}$ at clutter boundaries (terrain, buildings) where CA-CFAR fails; approximately 0.5-1 dB additional CFAR loss vs. CA-CFAR in homogeneous environments
- **Resource cost:** ~3,500-5,000 LUTs, 2-4 DSPs, 2-4 BRAMs (~10% overhead vs. CA-CFAR)
- **Risk:** LOW -- minor extension of CA-CFAR architecture; can be implemented as a configuration option alongside CA-CFAR
- **Recommended investigation steps:**
  1. Characterize the AERIS-10 clutter environment through field measurements at representative deployment sites
  2. Compare CA-CFAR vs. GOCA-CFAR $P_{fa}$ at simulated clutter edges using measured or modeled clutter power profiles
  3. Determine whether clutter-edge handling justifies the minor additional CFAR loss in homogeneous regions

### Priority 3: OS-CFAR (Multi-Target Robustness)

- **Expected improvement:** Robust detection in multi-target environments (up to $N_\text{ref} - k$ interferers in the reference window); 1-2 dB additional CFAR loss vs. CA-CFAR in homogeneous environments
- **Resource cost:** ~8,000-12,000 LUTs, 2-4 DSPs, 3-6 BRAMs (2-3x CA-CFAR)
- **Risk:** MEDIUM -- sorting network complexity requires careful FPGA timing closure; bitonic sort at 100 MHz for 32 elements is achievable but non-trivial
- **Recommended investigation steps:**
  1. Evaluate the multi-target density expected in AERIS-10 operational scenarios to determine whether OS-CFAR robustness is necessary
  2. Select the rank parameter $k$ based on expected maximum target density in the reference window
  3. Prototype bitonic sorting network for $N_\text{ref} = 32$ and verify timing closure at 100 MHz on XC7A100T

### Priority 4: Multi-Mode CFAR (Comprehensive -- Future)

- **Expected improvement:** Near-optimal detection across all environment types (homogeneous, clutter edge, multi-target) with automatic mode selection
- **Resource cost:** ~23,000-31,000 LUTs, 6-12 DSPs, 8-14 BRAMs (49-66% of available LUT headroom)
- **Risk:** HIGH -- consumes a large fraction of available resources, limiting headroom for other improvements (clutter rejection, range extension, FPGA optimization); complex mode-switching logic requires extensive verification
- **Recommended investigation steps:**
  1. Implement CA-CFAR first (Priority 1) and evaluate whether the single-mode performance is sufficient for operational requirements
  2. If multi-mode is needed, evaluate sequential mode testing (run CA first, switch to GO or OS only when environment non-homogeneity is detected) to reduce parallel resource consumption
  3. Consider implementing the mode selector on the host PC (Python) with only the selected CFAR variant active on the FPGA at any given time

---

## References

[1] A. Khodjet-Kesba, K. Benhala, K. Abdessamad, and A. Bouazza, "FPGA Implementation of Efficient CFAR Algorithm for Radar Systems," *Sensors*, vol. 23, no. 3, p. 1487, Jan. 2023. [Online]. Available: https://pmc.ncbi.nlm.nih.gov/articles/PMC9861839/

[2] Y. M. Park and S. Kim, "Improved CFAR algorithm for multiple environmental conditions," *Signal, Image and Video Processing*, vol. 18, pp. 4271-4280, 2024. [Online]. Available: https://link.springer.com/article/10.1007/s11760-024-03001-x

[3] M. I. Skolnik, *Introduction to Radar Systems*, 4th ed. New York, NY, USA: McGraw-Hill, 2008, ch. 5, 16.

[4] M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed. New York, NY, USA: McGraw-Hill, 2014, ch. 10.

[5] B. R. Mahafza, *Radar Systems Analysis and Design Using MATLAB*, 3rd ed. Boca Raton, FL, USA: CRC Press, 2013, ch. 6-7.

[6] Xilinx, "7 Series DSP48E1 Slice User Guide," UG479, v1.11, Nov. 2014.

[7] Xilinx, "Artix-7 FPGAs Data Sheet: DC and AC Switching Characteristics," DS181, v1.28, Feb. 2022.
