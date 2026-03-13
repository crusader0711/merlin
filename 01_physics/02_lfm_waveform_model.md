# LFM Waveform Model

**Purpose:** Derive the Linear Frequency Modulated (LFM) chirp signal mathematics, time-bandwidth product, matched filter theory, pulse compression, sidelobe structure, and ambiguity function for the AERIS-10 radar system.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [FMCW Theory](01_fmcw_theory.md) -- beat frequency, range equation, and range-Doppler coupling

---

## 1. LFM Chirp Signal

The transmitted signal in the AERIS-10 system is a Linear Frequency Modulated (LFM) chirp. During each pulse of duration $T_c$ (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)), the carrier frequency sweeps linearly across the chirp bandwidth $B$ (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)).

### Complex Baseband Representation

The LFM chirp signal in complex baseband form, gated by a rectangular window over the chirp duration, is:

$$
s(t) = \operatorname{rect}\!\left(\frac{t}{T_c}\right) \exp\!\left(j2\pi\!\left(f_c t + \frac{\mu}{2} t^2\right)\right) \tag{LFM-1}
$$

where the rectangular window is defined as:

$$
\operatorname{rect}\!\left(\frac{t}{T_c}\right) =
\begin{cases}
1, & |t| \le T_c / 2 \\
0, & |t| > T_c / 2
\end{cases}
\tag{LFM-2}
$$

and $\mu$ is the chirp rate (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)):

$$
\mu = \frac{B}{T_c} \tag{LFM-3}
$$

### Instantaneous Frequency

The instantaneous frequency of the chirp is obtained from the time derivative of the phase $\phi(t) = 2\pi(f_c t + \mu t^2 / 2)$:

$$
f_i(t) = \frac{1}{2\pi}\frac{d\phi}{dt} = f_c + \mu t \tag{LFM-4}
$$

Over the chirp duration $-T_c/2 \le t \le T_c/2$, the instantaneous frequency sweeps linearly from $f_c - B/2$ to $f_c + B/2$. The total frequency excursion equals the chirp bandwidth $B$, and the sweep rate is constant at $\mu$ Hz/s.

**Physical interpretation:** The LFM chirp distributes its energy across the full bandwidth $B$ during the pulse duration $T_c$. This spread-spectrum property is what enables pulse compression -- recovering range resolution determined by $B$ from a long pulse of duration $T_c$.

---

## 2. Time-Bandwidth Product

The time-bandwidth product (TBP) is the fundamental figure of merit for an LFM waveform. It is defined as:

$$
\text{TBP} = B \, T_c \tag{LFM-5}
$$

The TBP determines two critical system properties:

1. **Pulse compression ratio:** The ratio of the uncompressed pulse width $T_c$ to the compressed pulse width $\tau_c = 1/B$ (derived in Section 4) equals $B T_c$. A larger TBP means greater compression and finer range resolution from a longer pulse.

2. **Processing gain:** The matched filter output SNR gain relative to the input SNR equals the TBP (derived in Section 3). This is the fundamental advantage of pulse compression radar -- achieving the range resolution of a short pulse while transmitting the energy of a long pulse.

### Chirp Mode Comparison

The AERIS-10 system operates in two chirp modes with different durations $T_{c,1}$ and $T_{c,2}$ (see the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing) for values). Both modes share the same bandwidth $B$ (currently TBD). The TBP for each mode is:

$$
\begin{aligned}
\text{TBP}_1 &= B \, T_{c,1} \\
\text{TBP}_2 &= B \, T_{c,2}
\end{aligned}
\tag{LFM-6}
$$

The ratio of time-bandwidth products is:

$$
\frac{\text{TBP}_1}{\text{TBP}_2} = \frac{T_{c,1}}{T_{c,2}} \tag{LFM-7}
$$

> **Variant Note -- Chirp Mode Comparison:**
> | | Long Chirp | Short Chirp |
> |--|-----------|-------------|
> | Chirp duration $T_c$ | $T_{c,1}$ | $T_{c,2}$ |
> | Time-bandwidth product | $B \, T_{c,1}$ | $B \, T_{c,2}$ |
> | Relative TBP | $T_{c,1} / T_{c,2}$ | 1 (reference) |
>
> See the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing) for numerical values. Both modes achieve the same range resolution $\Delta R = c/(2B)$ (since $B$ is shared), but the long chirp provides proportionally higher processing gain.

---

## 3. Matched Filter Theory

The matched filter is the linear filter that maximizes the output signal-to-noise ratio for a known signal in additive white Gaussian noise. This is a consequence of the Schwarz inequality and is the optimal linear detector in the Neyman-Pearson sense.

### Matched Filter Definition

For a transmitted signal $s(t)$, the matched filter impulse response is the time-reversed, conjugated replica:

$$
h(t) = s^*(-t) \tag{LFM-8}
$$

Equivalently, the matched filter frequency response is the conjugate of the signal spectrum:

$$
H(f) = S^*(f) \tag{LFM-9}
$$

where $S(f) = \mathcal{F}\{s(t)\}$ is the Fourier transform of the transmitted signal.

### Output SNR Maximization

The matched filter output is the convolution of the received signal with the matched filter impulse response. When the received signal consists of a scaled copy of $s(t)$ embedded in white Gaussian noise with power spectral density $N_0/2$, the output SNR at the peak of the matched filter response is:

$$
\text{SNR}_\text{out} = \frac{2E}{N_0} \tag{LFM-10}
$$

where $E$ is the signal energy:

$$
E = \int_{-\infty}^{\infty} |s(t)|^2 \, dt \tag{LFM-11}
$$

This result is independent of the waveform shape -- any signal with the same energy achieves the same peak output SNR through its matched filter. The matched filter output SNR depends only on the total signal energy and the noise spectral density.

### Processing Gain

For the LFM chirp of Eq. (LFM-1) with unit amplitude over duration $T_c$, the signal energy is $E = T_c$. The input SNR (ratio of signal power to noise power in bandwidth $B$) is:

$$
\text{SNR}_\text{in} = \frac{1}{N_0 B} \tag{LFM-12}
$$

The ratio of output to input SNR defines the processing gain:

$$
G_p = \frac{\text{SNR}_\text{out}}{\text{SNR}_\text{in}} = \frac{2E / N_0}{1 / (N_0 B)} = 2 E B = 2 T_c B \approx B \, T_c \tag{LFM-13}
$$

where the factor of 2 arises from the two-sided noise spectral density convention and is conventionally absorbed into the definition. The processing gain of the matched filter equals the time-bandwidth product:

$$
\boxed{G_p = B \, T_c} \tag{LFM-14}
$$

This connects to the radar range equation: the single-pulse SNR from Eq. (FMCW-11) in [`01_fmcw_theory.md`](01_fmcw_theory.md#signal-to-noise-ratio) is enhanced by the processing gain $G_p$ after matched filtering. The post-matched-filter SNR is:

$$
\text{SNR}_\text{MF} = \text{SNR} \cdot G_p = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4 k_B T_0 B_n F L} \cdot B \, T_c \tag{LFM-15}
$$

---

## 4. Pulse Compression

Pulse compression is the physical realization of matched filtering for the LFM waveform. It converts the long chirp pulse of duration $T_c$ into a narrow compressed pulse of width $\tau_c$, achieving the range resolution of a short pulse while maintaining the energy of the long pulse.

### Compressed Pulse Width

The matched filter output for the LFM chirp has a mainlobe width (measured between the first nulls of the sinc-like envelope) determined by the bandwidth:

$$
\tau_c = \frac{1}{B} \tag{LFM-16}
$$

This is the compressed pulse width. The compression ratio is:

$$
\frac{T_c}{\tau_c} = B \, T_c = \text{TBP} \tag{LFM-17}
$$

### Connection to Range Resolution

The compressed pulse width directly determines the range resolution. Two targets separated by $\Delta R$ produce echoes with a time-of-arrival difference of $\Delta \tau = 2\Delta R / c$. They are resolvable when this difference exceeds the compressed pulse width:

$$
\Delta \tau \ge \tau_c = \frac{1}{B}
$$

Therefore:

$$
\Delta R = \frac{c \, \tau_c}{2} = \frac{c}{2B} \tag{LFM-18}
$$

This is identical to Eq. (FMCW-19) in [`01_fmcw_theory.md`](01_fmcw_theory.md#range-resolution), confirming that range resolution depends only on bandwidth and is independent of pulse duration.

### Matched Filter Output Envelope

The matched filter output for the unweighted LFM chirp has the form of a sinc function modulated by a residual chirp phase:

$$
|y(\tau)| = T_c \left|\operatorname{sinc}\!\left(B\tau \!\left(1 - \frac{|\tau|}{T_c}\right)\right)\right| \tag{LFM-19}
$$

where $\tau$ is the delay relative to the peak. For $|\tau| \ll T_c$ (which holds for any practical compressed pulse since $\tau_c = 1/B \ll T_c$), this simplifies to:

$$
|y(\tau)| \approx T_c \left|\operatorname{sinc}(B\tau)\right| \tag{LFM-20}
$$

The mainlobe has a $-3~\text{dB}$ width of approximately $0.89/B$ and first nulls at $\tau = \pm 1/B$.

---

## 5. Sidelobe Structure and Windowing

### Unweighted Sidelobe Levels

The sinc-like compressed pulse of Eq. (LFM-20) has sidelobes that decay slowly. The peak sidelobe level (PSL) for the unweighted (rectangular window) case is:

$$
\text{PSL}_\text{rect} = -13.3~\text{dB} \tag{LFM-21}
$$

This first sidelobe at $-13.3~\text{dB}$ below the mainlobe peak can mask weak targets adjacent to strong reflectors. In practice, a window function $w[n]$ (defined in the [Symbol Table](../00_notation/symbol_table.md#signal-processing)) is applied to reduce the sidelobe level at the cost of widening the mainlobe.

### Windowing Tradeoffs

Applying a window function to the matched filter (equivalently, tapering the signal spectrum before inverse FFT) reduces sidelobes but widens the mainlobe, degrading range resolution. The fundamental tradeoff is:

| Window | Peak Sidelobe Level | Mainlobe Width Factor | Processing Loss |
|--------|--------------------|-----------------------|-----------------|
| Rectangular (none) | $-13.3~\text{dB}$ | $1.0 \times (1/B)$ | $0~\text{dB}$ |
| Hamming | $-42.8~\text{dB}$ | $1.50 \times (1/B)$ | $1.34~\text{dB}$ |
| Taylor ($\bar{n} = 5$, SLL $= -35~\text{dB}$) | $-35~\text{dB}$ | $1.28 \times (1/B)$ | $0.76~\text{dB}$ |

**Resolution-sidelobe tradeoff:** Hamming weighting achieves a $29.5~\text{dB}$ sidelobe improvement over the rectangular window at the cost of $50\%$ mainlobe widening (degrading range resolution from $c/(2B)$ to approximately $1.5 \cdot c/(2B)$). Taylor weighting provides a more favorable compromise, achieving $-35~\text{dB}$ sidelobes with only $28\%$ mainlobe widening.

The processing loss column quantifies the SNR reduction due to windowing -- the window reduces the coherent gain of the matched filter because it applies non-uniform weights to the signal spectrum. This loss is subtracted from the processing gain $G_p$ of Eq. (LFM-14).

---

## 6. Ambiguity Function

The ambiguity function characterizes a waveform's joint range-Doppler resolution and coupling. It is the fundamental tool for analyzing how well a radar waveform can simultaneously resolve targets in range (delay) and velocity (Doppler).

### Definition

The ambiguity function is defined as:

$$
\chi(\tau, \nu) = \int_{-\infty}^{\infty} s(t) \, s^*\!(t - \tau) \, e^{j2\pi \nu t} \, dt \tag{LFM-22}
$$

where $\tau$ is the delay (related to range by $\tau = 2R/c$) and $\nu$ is the Doppler frequency shift (defined in the [Symbol Table](../00_notation/symbol_table.md#signal-processing)). The squared magnitude $|\chi(\tau, \nu)|^2$ is called the ambiguity surface.

### Ambiguity Function for the LFM Chirp

Substituting the LFM signal from Eq. (LFM-1) into the definition of Eq. (LFM-22), the ambiguity function for the LFM chirp evaluates to:

$$
|\chi(\tau, \nu)| = \left(1 - \frac{|\tau|}{T_c}\right) \left|\operatorname{sinc}\!\left((\nu + \mu\tau)(T_c - |\tau|)\right)\right|, \quad |\tau| \le T_c \tag{LFM-23}
$$

The key feature is the argument of the sinc function: $\nu + \mu\tau$. The peak of the ambiguity function (where the sinc argument is zero) occurs along the line:

$$
\nu = -\mu\tau \tag{LFM-24}
$$

This is the **tilted ridge** characteristic of the LFM waveform. The ridge is tilted in the $(\tau, \nu)$ plane with slope $-\mu = -B/T_c$, coupling delay and Doppler measurements.

### Interpretation for the AERIS-10 System

The ambiguity function reveals four critical system properties:

#### (a) Range Resolution (Zero-Doppler Cut)

Setting $\nu = 0$ in Eq. (LFM-23) gives the zero-Doppler cut:

$$
|\chi(\tau, 0)| = \left(1 - \frac{|\tau|}{T_c}\right) \left|\operatorname{sinc}(\mu\tau(T_c - |\tau|))\right| \tag{LFM-25}
$$

For $|\tau| \ll T_c$, this reduces to $|\operatorname{sinc}(B\tau)|$, consistent with the matched filter output of Eq. (LFM-20). The first null occurs at $\tau = 1/B$, confirming the range resolution:

$$
\Delta R = \frac{c}{2B}
$$

as derived in Eq. (LFM-18) and Eq. (FMCW-19) of [`01_fmcw_theory.md`](01_fmcw_theory.md#range-resolution).

#### (b) Velocity Resolution (Zero-Delay Cut)

Setting $\tau = 0$ in Eq. (LFM-23) gives the zero-delay cut:

$$
|\chi(0, \nu)| = \left|\operatorname{sinc}(\nu T_c)\right| \tag{LFM-26}
$$

The first null occurs at $\nu = 1/T_c$, giving the Doppler resolution of a single chirp pulse:

$$
\Delta f_{d,\text{pulse}} = \frac{1}{T_c} \tag{LFM-27}
$$

The corresponding single-pulse velocity resolution is:

$$
\Delta v_\text{pulse} = \frac{\lambda}{2T_c} \tag{LFM-28}
$$

In practice, the AERIS-10 achieves finer velocity resolution by coherent integration across $M$ chirps in the Doppler FFT, yielding $\Delta v = \lambda / (2 M T_r)$ as given in Eq. (FMCW-21) of [`01_fmcw_theory.md`](01_fmcw_theory.md#velocity-measurement).

#### (c) Range-Doppler Coupling

The tilted ridge of Eq. (LFM-24) means that a Doppler shift $\nu$ is indistinguishable from a delay offset $\Delta\tau = -\nu/\mu$ (and vice versa). The coupling slope is:

$$
\frac{d\tau}{d\nu} = -\frac{1}{\mu} = -\frac{T_c}{B} \tag{LFM-29}
$$

Converting to range and velocity units:

$$
\frac{\Delta R}{\Delta v} = \frac{c}{2} \cdot \frac{d\tau}{d\nu} \cdot \frac{2}{\lambda} = -\frac{c \, T_c}{\lambda \, B} \tag{LFM-30}
$$

This is consistent with the range error from Doppler given in Eq. (FMCW-27) of [`01_fmcw_theory.md`](01_fmcw_theory.md#range-doppler-coupling-analysis). For the AERIS-10 system, the coupling magnitude scales with $T_c / B$: the long chirp mode ($T_{c,1}$) has a coupling slope that is $T_{c,1}/T_{c,2}$ times that of the short chirp mode ($T_{c,2}$), consistent with the analysis in Eq. (FMCW-28).

The 2D range-Doppler FFT processing used in the AERIS-10 FPGA pipeline separates range and Doppler, effectively resolving along the ridge rather than across it. This is why the range-Doppler map does not suffer from the coupling inherent in single-pulse range estimation.

#### (d) First Sidelobe Level

The sidelobe structure of the ambiguity function along the zero-Doppler cut follows the sinc pattern discussed in Section 5, with a peak sidelobe level of $-13.3~\text{dB}$ for the unweighted case (Eq. (LFM-21)). Along the ridge direction, the sidelobes are modulated by the triangular envelope $(1 - |\tau|/T_c)$, which provides additional suppression at larger delays.

---

## 7. System-Specific Analysis

### Processing Gain Comparison

The matched filter processing gain from Eq. (LFM-14) for each chirp mode is:

$$
\begin{aligned}
G_{p,1} &= B \, T_{c,1} \\
G_{p,2} &= B \, T_{c,2}
\end{aligned}
\tag{LFM-31}
$$

In decibels:

$$
\begin{aligned}
G_{p,1}\,[\text{dB}] &= 10\log_{10}(B \, T_{c,1}) \\
G_{p,2}\,[\text{dB}] &= 10\log_{10}(B \, T_{c,2})
\end{aligned}
\tag{LFM-32}
$$

The processing gain advantage of the long chirp over the short chirp is:

$$
\Delta G_p\,[\text{dB}] = 10\log_{10}\!\left(\frac{T_{c,1}}{T_{c,2}}\right) \tag{LFM-33}
$$

> **Variant Note -- Processing Gain:**
> | | Long Chirp | Short Chirp |
> |--|-----------|-------------|
> | Chirp duration $T_c$ | $T_{c,1}$ | $T_{c,2}$ |
> | Processing gain | $B \, T_{c,1}$ | $B \, T_{c,2}$ |
> | Relative gain | $10\log_{10}(T_{c,1}/T_{c,2})~\text{dB}$ above short chirp | Reference |
>
> See the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing) for numerical values. Both modes share bandwidth $B$ (currently TBD), so range resolution is identical. The long chirp trades higher processing gain and finer Doppler resolution for increased range-Doppler coupling and reduced maximum unambiguous velocity.

### Design Tradeoffs

The two chirp modes represent complementary operating points in the AERIS-10 system:

- **Long chirp ($T_{c,1}$):** Higher processing gain $G_{p,1}$, finer Doppler resolution $\Delta v_\text{pulse} = \lambda/(2T_{c,1})$, but stronger range-Doppler coupling (slope $\propto T_{c,1}/B$) and lower maximum unambiguous range (constrained by $T_{r,1}$).

- **Short chirp ($T_{c,2}$):** Lower processing gain $G_{p,2}$, coarser Doppler resolution, but weaker range-Doppler coupling and wider unambiguous range. Better suited for detecting fast-moving targets where Doppler-induced range bias must be minimized.

---

## References

- [Symbol Table](../00_notation/symbol_table.md) -- canonical symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both AERIS-10 variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- [FMCW Theory](01_fmcw_theory.md) -- beat frequency derivation, range equation, range-Doppler coupling
- Richards, M.A., *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014 -- LFM waveform analysis (Ch. 4), matched filtering (Ch. 6), ambiguity function (Ch. 3)
- Skolnik, M.I., *Introduction to Radar Systems*, 4th ed., McGraw-Hill, 2008 -- Pulse compression radar (Ch. 8), waveform design (Ch. 11)
- Levanon, N. and Mozeson, E., *Radar Signals*, Wiley, 2004 -- Ambiguity function theory (Ch. 3-4), LFM properties (Ch. 5)
