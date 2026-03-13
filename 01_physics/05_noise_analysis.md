# Noise Figure Chain Analysis

**Purpose:** Trace noise through the complete AERIS-10 receive chain -- from antenna thermal noise through analog components (LNA, mixer, IF amplifier) to the ADC and digital processing (CIC decimation filter) -- quantifying each stage's noise contribution to establish the system noise figure budget.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules

---

## 1. Thermal Noise Power

Every conductor at a nonzero temperature generates noise due to random thermal motion of charge carriers (Johnson-Nyquist noise). The available noise power at the output of a resistor at temperature $T$ over a bandwidth $B_n$ is

$$
P_n = k_B \, T \, B_n \tag{NF-1}
$$

where $k_B$ is the Boltzmann constant (defined in the [Symbol Table](../00_notation/symbol_table.md#physical-constants)) and $B_n$ is the **noise bandwidth** of the receiver. At the standard reference temperature $T_0 = 290~\text{K}$, the noise power spectral density is

$$
N_0 = k_B \, T_0 \approx -174~\text{dBm/Hz} \tag{NF-2}
$$

The noise bandwidth $B_n$ is distinct from the signal bandwidth $B$; it is defined as the bandwidth of an ideal rectangular filter that would pass the same total noise power as the actual receiver transfer function $H(f)$:

$$
B_n = \frac{\displaystyle\int_0^\infty |H(f)|^2 \, df}{|H(f_0)|^2} \tag{NF-3}
$$

where $f_0$ is the frequency of peak gain. For a matched filter in an FMCW radar, $B_n$ is related to the chirp parameters; the exact relationship is developed in the FMCW theory document ([`01_fmcw_theory.md`](01_fmcw_theory.md)), where the noise floor against which targets must be detected is $P_n = k_B T_0 B_n$.

---

## 2. Noise Figure Definition

The **noise figure** $F$ of a two-port network quantifies how much the network degrades the signal-to-noise ratio. It is defined as the ratio of input SNR to output SNR when the input noise source is at the standard temperature $T_0 = 290~\text{K}$:

$$
F = \frac{\text{SNR}_\text{in}}{\text{SNR}_\text{out}} \tag{NF-4}
$$

Since any real component adds some noise, $F \geq 1$ (i.e., $\text{NF}_\text{dB} \geq 0~\text{dB}$). An ideal noiseless component has $F = 1$.

The noise figure is equivalently expressed through the **equivalent noise temperature** $T_e$, which represents the additional noise contributed by the device referred to its input:

$$
T_e = T_0 (F - 1) \tag{NF-5}
$$

A device with noise figure $F$ behaves as a noiseless device followed by an additive noise source of power $k_B T_e B_n$.

The noise figure expressed in decibels is

$$
\text{NF}_\text{dB} = 10 \log_{10}(F) \tag{NF-6}
$$

> **Conversion Reminder:**
>
> | Quantity | Linear | dB |
> |----------|--------|----|
> | Noise figure | $F$ (ratio $\geq 1$) | $\text{NF}_\text{dB} = 10\log_{10}(F)$ |
> | Gain | $G$ (ratio) | $G_\text{dB} = 10\log_{10}(G)$ |
> | Linear from dB | $F = 10^{\text{NF}_\text{dB}/10}$ | -- |
>
> **All $F$ and $G$ values in the Friis cascade formula (next section) are linear ratios, NOT dB.** Mixing dB and linear values is the most common error in noise figure calculations.

---

## 3. Friis Cascaded Noise Figure

When multiple stages are cascaded in series, the system noise figure is determined by the **Friis formula**. For an $M$-stage receive chain with individual noise figures $F_1, F_2, \ldots, F_M$ and available power gains $G_1, G_2, \ldots, G_M$ (all in **linear**, not dB):

$$
F_\text{sys} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2} + \cdots + \frac{F_M - 1}{\displaystyle\prod_{i=1}^{M-1} G_i} \tag{NF-7}
$$

### Derivation

Consider a cascade of two stages. The output noise power of Stage 1 (referred to its input) is $k_B T_0 B_n F_1 G_1$. Stage 2 adds its own noise, referred to Stage 2's input, of $k_B T_0 B_n (F_2 - 1)$. Referred to the input of Stage 1, this is $k_B T_0 B_n (F_2 - 1) / G_1$ (dividing by Stage 1's gain). Thus the total input-referred noise is

$$
\begin{aligned}
P_{n,\text{sys}} &= k_B T_0 B_n \left[ F_1 + \frac{F_2 - 1}{G_1} \right]
\end{aligned}
$$

Extending by induction to $M$ stages yields Eq. (NF-7).

### Key Insight

The first-stage noise figure $F_1$ appears directly, while subsequent stages are divided by the cumulative gain of all preceding stages. This is why the **LNA (first stage) dominates the system noise figure** provided it has sufficient gain. A high-gain, low-noise LNA suppresses the noise contributions of all downstream stages.

### Conversion Procedure (dB to Linear and Back)

Component datasheets specify noise figure in dB. To apply Eq. (NF-7):

1. **Convert each stage to linear:** $F_k = 10^{\text{NF}_{k,\text{dB}}/10}$ and $G_k = 10^{G_{k,\text{dB}}/10}$
2. **Apply Eq. (NF-7)** using linear values only
3. **Convert the result back to dB:** $\text{NF}_{\text{sys,dB}} = 10\log_{10}(F_\text{sys})$

---

## 4. AERIS-10 Receive Chain Stages

The AERIS-10 receive chain (both Nexus and Extended variants) consists of the following stages from antenna to digital output. Component identifiers reference the [Parameter Table](../00_notation/parameter_table.md#rf-front-end).

| Stage | Component | Noise Figure | Gain | Notes |
|-------|-----------|-------------|------|-------|
| 1 | LNA (ADTR1107) | $F_\text{LNA}$ | $G_\text{LNA}$ | Integrated T/R module; NF TBD from datasheet |
| 2 | Mixer (LT5552) | $F_\text{mix}$ | $G_\text{mix}$ | Double-balanced mixer; conversion loss $\Rightarrow G_\text{mix} < 1$ |
| 3 | IF amplifier | $F_\text{IF}$ | $G_\text{IF}$ | Post-mixer gain stage (if present in signal path) |
| 4 | ADC (AD9484) | $F_\text{ADC}$ | $G_\text{ADC}$ | 8-bit, 500 MSPS rated, operated at 400 MSPS |

Applying the Friis formula Eq. (NF-7) to this four-stage chain:

$$
F_\text{sys} = F_\text{LNA} + \frac{F_\text{mix} - 1}{G_\text{LNA}} + \frac{F_\text{IF} - 1}{G_\text{LNA} \, G_\text{mix}} + \frac{F_\text{ADC} - 1}{G_\text{LNA} \, G_\text{mix} \, G_\text{IF}} \tag{NF-8}
$$

All values in Eq. (NF-8) are **linear ratios**. For the current AERIS-10 system, $F_\text{LNA}$ and other component noise figures are TBD (see [Parameter Table](../00_notation/parameter_table.md#tbd-tracking)). Sections 5 and 6 below derive the ADC and CIC contributions that extend the chain beyond the analog stages.

> **Note on mixer gain:** The LT5552 is a passive mixer with conversion *loss*. Its gain $G_\text{mix}$ is less than unity ($G_\text{mix} < 1$, i.e., $G_{\text{mix,dB}} < 0~\text{dB}$). This means the mixer's own noise figure and the noise of subsequent stages are amplified in the Friis cascade, making the LNA gain $G_\text{LNA}$ critical for suppressing these contributions.

---

## 5. ADC Noise Contribution

The AD9484 is an 8-bit ADC (see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga)). The limited bit depth makes quantization noise a significant contributor to the system noise budget -- far more so than for higher-resolution ADCs (e.g., 14-bit or 16-bit).

### 5.1 Quantization Noise Power

An ideal $b$-bit ADC with full-scale voltage $V_\text{FS}$ has a least significant bit (LSB) voltage of

$$
\Delta = \frac{V_\text{FS}}{2^b} \tag{NF-9}
$$

The quantization error is uniformly distributed over $[-\Delta/2, +\Delta/2]$, giving a quantization noise power (variance) of

$$
\sigma_q^2 = \frac{\Delta^2}{12} = \frac{V_\text{FS}^2}{12 \cdot 2^{2b}} \tag{NF-10}
$$

### 5.2 Signal-to-Quantization-Noise Ratio

For a full-scale sinusoidal input, the signal power is $P_\text{sig} = V_\text{FS}^2 / 8$. The theoretical maximum signal-to-quantization-noise ratio (SQNR) is

$$
\text{SQNR}_\text{dB} = 6.02 \, b + 1.76~\text{dB} \tag{NF-11}
$$

For the AD9484 with $b = 8$ bits:

$$
\text{SQNR}_\text{dB} = 6.02 \times 8 + 1.76 = 49.9~\text{dB}
$$

This means the quantization noise floor sits at $-49.9~\text{dBFS}$ (dB below full scale). For comparison, a 14-bit ADC achieves $\text{SQNR} = 86.0~\text{dB}$, giving a $36.1~\text{dB}$ advantage. The 8-bit quantization noise floor is therefore a **dominant constraint** on the AERIS-10 digital noise floor.

### 5.3 Effective Noise Figure of the ADC

The ADC's effective noise figure depends on the signal level relative to the ADC full scale. Defining $F_\text{ADC}$ as the ratio of total output noise (thermal + quantization) to the input thermal noise alone:

$$
F_\text{ADC} = 1 + \frac{\sigma_q^2}{k_B T_0 B_n G_\text{chain}} \tag{NF-12}
$$

where $G_\text{chain} = G_\text{LNA} \, G_\text{mix} \, G_\text{IF}$ is the total gain of the analog chain preceding the ADC. This expression shows that:

- **Higher analog gain** (larger $G_\text{chain}$) reduces the effective ADC noise figure by raising the thermal noise power at the ADC input above the quantization noise floor.
- **Wider noise bandwidth** $B_n$ similarly increases input thermal noise relative to quantization noise.
- The ADC noise figure is **not a fixed number** -- it depends on system configuration.

When the analog gain is insufficient, quantization noise dominates and $F_\text{ADC}$ becomes large, degrading the system noise figure in Eq. (NF-8). For the 8-bit AD9484, ensuring that the analog chain provides enough gain to keep thermal noise above the quantization floor is a critical design constraint.

### 5.4 Effective Number of Bits (ENOB)

In practice, the AD9484 achieves fewer effective bits than the nominal 8 due to aperture jitter, differential nonlinearity (DNL), integral nonlinearity (INL), and clock jitter. The effective number of bits (ENOB) is related to the measured signal-to-noise-and-distortion ratio (SINAD) by

$$
\text{ENOB} = \frac{\text{SINAD}_\text{dB} - 1.76}{6.02} \tag{NF-13}
$$

The datasheet ENOB determines the actual quantization noise floor, which may be several dB worse than the theoretical $-49.9~\text{dBFS}$.

---

## 6. CIC Filter Noise Analysis

The CIC (Cascaded Integrator-Comb) decimation filter is a critical digital processing stage that follows the ADC. The AERIS-10 uses $N_\text{CIC} = 5$ stages with decimation factor $D_\text{CIC} = 4$ (see [Parameter Table](../00_notation/parameter_table.md#signal-processing-fpga), FPGA parameter `STAGES` and `DECIMATION` in `cic_decimator.v`).

### 6.1 CIC Processing Gain

An ideal CIC decimation filter provides processing gain by averaging (filtering) the input signal over a wider bandwidth before decimating. For $N_\text{CIC}$ stages with decimation factor $D_\text{CIC}$, the DC gain is

$$
G_\text{CIC} = D_\text{CIC}^{N_\text{CIC}} \tag{NF-14}
$$

For the AERIS-10 parameters: $G_\text{CIC} = 4^5 = 1024$, corresponding to $30.1~\text{dB}$ of processing gain. This gain applies to the signal at DC (or equivalently, the center of the passband); it does not apply uniformly across the entire passband.

### 6.2 Bit Growth

The CIC filter accumulates values across stages, requiring increased word length to avoid overflow. The output bit width $b_\text{out}$ for an $N_\text{CIC}$-stage CIC with decimation factor $D_\text{CIC}$ and input width $b_\text{in}$ is

$$
b_\text{out} = b_\text{in} + N_\text{CIC} \left\lceil \log_2(D_\text{CIC}) \right\rceil \tag{NF-15}
$$

For the AERIS-10: $b_\text{out} = 8 + 5 \times \lceil\log_2(4)\rceil = 8 + 5 \times 2 = 18~\text{bits}$.

If the downstream processing path truncates or rounds back to a narrower word width, additional quantization noise is introduced. This truncation noise must be accounted for in the noise budget.

### 6.3 Passband Droop

The CIC filter's frequency response is

$$
|H_\text{CIC}(f)|^2 = \left| \frac{\sin(\pi D_\text{CIC} f / f_s)}{\sin(\pi f / f_s)} \right|^{2 N_\text{CIC}} \tag{NF-16}
$$

where $f_s$ is the ADC sampling frequency. The passband is not flat: the response droops toward the edges of the passband, reducing the effective SNR for signals away from DC. For a 5-stage CIC with $D_\text{CIC} = 4$, the droop at the passband edge ($f = f_s / (2 D_\text{CIC})$) can be several dB, which must be compensated by a downstream compensation filter or accounted for as a loss in the noise budget.

### 6.4 Effective Noise Figure of CIC Processing

The CIC filter contributes to the system noise budget through two mechanisms:

1. **Processing gain** (beneficial): Noise bandwidth is reduced by decimation, improving SNR by approximately $10\log_{10}(D_\text{CIC}) = 6.0~\text{dB}$ per stage of decimation (for white noise input). However, the CIC filter is not an ideal decimation filter -- its finite stopband rejection allows some aliased noise to fold back into the passband.

2. **Truncation/rounding noise** (detrimental): If the 18-bit CIC output is truncated to a narrower width for subsequent processing, the truncation introduces quantization noise with variance $\sigma_\text{trunc}^2 = \Delta_\text{trunc}^2 / 12$, analogous to Eq. (NF-10).

The effective noise figure contribution of the digital chain can be expressed as

$$
F_\text{digital} = \frac{1}{G_\text{CIC,eff}} \left(1 + \frac{\sigma_\text{trunc}^2}{\sigma_\text{in}^2}\right) \tag{NF-17}
$$

where $G_\text{CIC,eff}$ is the effective processing gain (accounting for passband droop and aliased noise) and $\sigma_\text{in}^2$ is the noise power at the CIC input. When the full 18-bit output is preserved, the truncation term vanishes and $F_\text{digital} \approx 1/G_\text{CIC,eff}$ -- the CIC filter improves SNR.

---

## 7. System Noise Figure Budget

### 7.1 Complete Chain

Combining the analog Friis cascade (Eq. (NF-8)) with the digital processing contributions, the complete system noise figure from antenna to digital output is

$$
F_\text{total} = F_\text{sys} + \frac{F_\text{digital} - 1}{G_\text{LNA} \, G_\text{mix} \, G_\text{IF} \, G_\text{ADC}} \tag{NF-18}
$$

where $F_\text{sys}$ is the analog chain noise figure from Eq. (NF-8), $F_\text{digital}$ is defined in Eq. (NF-17), and $G_\text{ADC}$ represents the ADC's effective gain (unity for an ideal ADC mapping full-scale input to full-scale digital output).

### 7.2 Noise Budget Table

The following table traces noise through each stage symbolically. All values are **linear** unless explicitly marked as dB.

| Stage | Component | Noise Figure | Gain | Cumulative $F_\text{sys}$ |
|-------|-----------|-------------|------|---------------------------|
| 1 | LNA (ADTR1107) | $F_\text{LNA}$ | $G_\text{LNA}$ | $F_\text{LNA}$ |
| 2 | Mixer (LT5552) | $F_\text{mix}$ | $G_\text{mix}$ | $F_\text{LNA} + \dfrac{F_\text{mix} - 1}{G_\text{LNA}}$ |
| 3 | IF amplifier | $F_\text{IF}$ | $G_\text{IF}$ | $F_\text{LNA} + \dfrac{F_\text{mix} - 1}{G_\text{LNA}} + \dfrac{F_\text{IF} - 1}{G_\text{LNA} G_\text{mix}}$ |
| 4 | ADC (AD9484) | $F_\text{ADC}$ | $G_\text{ADC}$ | $F_\text{sys}$ per Eq. (NF-8) |
| 5 | CIC filter (digital) | $F_\text{digital}$ | $G_\text{CIC,eff}$ | $F_\text{total}$ per Eq. (NF-18) |

The system noise figure $F_\text{total}$ feeds directly into the radar range equation (see [`01_fmcw_theory.md`](01_fmcw_theory.md)), where the SNR at the detector is

$$
\text{SNR} = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4 k_B T_0 B_n F_\text{total} L}
$$

Higher $F_\text{total}$ directly reduces detection range.

### 7.3 Numerical Evaluation (Pending Parameter Resolution)

Several component noise figures and gains are TBD in the [Parameter Table](../00_notation/parameter_table.md#tbd-tracking). Once resolved, substitute into Eq. (NF-8) as follows:

**Step 1 -- Convert datasheet values to linear:**

| Stage | $\text{NF}_\text{dB}$ | $F$ (linear) | $G_\text{dB}$ | $G$ (linear) |
|-------|----------------------|--------------|---------------|--------------|
| LNA | $\text{NF}_\text{LNA,dB}$ | $10^{\text{NF}_\text{LNA,dB}/10}$ | $G_\text{LNA,dB}$ | $10^{G_\text{LNA,dB}/10}$ |
| Mixer | $\text{NF}_\text{mix,dB}$ | $10^{\text{NF}_\text{mix,dB}/10}$ | $G_\text{mix,dB}$ | $10^{G_\text{mix,dB}/10}$ |
| IF amp | $\text{NF}_\text{IF,dB}$ | $10^{\text{NF}_\text{IF,dB}/10}$ | $G_\text{IF,dB}$ | $10^{G_\text{IF,dB}/10}$ |

**Step 2 -- Substitute into Eq. (NF-8) and compute $F_\text{sys}$.**

**Step 3 -- Convert result:** $\text{NF}_\text{sys,dB} = 10\log_{10}(F_\text{sys})$.

#### Representative Example (Placeholder Values)

> **Caution:** The following values are **representative placeholders** for illustration only. They must be confirmed against component datasheets before use in system performance predictions. See the [Parameter Table](../00_notation/parameter_table.md#tbd-tracking) for current TBD status.

Using representative values:
- $F_\text{LNA} = 3~\text{dB}$ (to be confirmed against ADTR1107 datasheet) $\Rightarrow F_\text{LNA,lin} = 10^{0.3} \approx 2.0$
- $G_\text{LNA} = 20~\text{dB}$ $\Rightarrow G_\text{LNA,lin} = 100$
- $F_\text{mix} = 10~\text{dB}$ (typical double-balanced mixer) $\Rightarrow F_\text{mix,lin} = 10.0$
- $G_\text{mix} = -7~\text{dB}$ (conversion loss) $\Rightarrow G_\text{mix,lin} = 0.2$
- $F_\text{IF} = 4~\text{dB}$ $\Rightarrow F_\text{IF,lin} = 2.51$
- $G_\text{IF} = 30~\text{dB}$ $\Rightarrow G_\text{IF,lin} = 1000$

Substituting into Eq. (NF-8):

$$
\begin{aligned}
F_\text{sys} &= 2.0 + \frac{10.0 - 1}{100} + \frac{2.51 - 1}{100 \times 0.2} + \frac{F_\text{ADC} - 1}{100 \times 0.2 \times 1000} \\
&= 2.0 + 0.09 + 0.076 + \frac{F_\text{ADC} - 1}{20{,}000} \\
&\approx 2.17 \quad \text{(neglecting ADC term due to large denominator)}
\end{aligned}
$$

This corresponds to $\text{NF}_\text{sys} \approx 10\log_{10}(2.17) \approx 3.36~\text{dB}$.

**Observation:** With $20~\text{dB}$ of LNA gain, the LNA noise figure ($3~\text{dB}$) dominates, adding only $0.36~\text{dB}$ from all subsequent analog stages. The ADC contribution through the Friis chain is negligible when the cumulative analog gain is high. However, the ADC quantization noise floor ($-49.9~\text{dBFS}$) independently constrains dynamic range, as discussed in Section 5.

---

## References

- [Symbol Table](../00_notation/symbol_table.md) -- symbol definitions for $F$, $G$, $k_B$, $T_0$, $N_\text{CIC}$, $D_\text{CIC}$, $f_s$
- [Parameter Table](../00_notation/parameter_table.md) -- component values (LNA, mixer, ADC, CIC parameters)
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- [FMCW Theory](01_fmcw_theory.md) -- radar range equation and SNR definition
- Skolnik, M.I. *Introduction to Radar Systems*, 4th ed., McGraw-Hill, 2008 -- Chapters 2 (radar equation) and 11 (noise figure)
- Friis, H.T. "Noise Figures of Radio Receivers," *Proceedings of the IRE*, vol. 32, no. 7, pp. 419--422, July 1944
- Analog Devices, "AD9484 Datasheet," 8-bit, 500 MSPS ADC
- Hogenauer, E.B. "An Economical Class of Digital Filters for Decimation and Interpolation," *IEEE Trans. ASSP*, vol. 29, no. 2, pp. 155--162, April 1981
