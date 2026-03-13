# FMCW Radar Theory

**Purpose:** Derive the fundamental FMCW radar equations from first principles -- electromagnetic wave propagation through the radar range equation, beat frequency with full Doppler coupling, range and velocity measurement, and range-Doppler coupling analysis.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules

---

## 1. Electromagnetic Wave Propagation

A radar transmits an electromagnetic wave that propagates through free space, reflects off a target, and returns to the receiver. The transmitted signal is a sinusoidal carrier modulated by the waveform of interest. For a narrowband signal, the transmitted electric field at the antenna can be written as:

$$
s_t(t) = A_t \cos\!\left(2\pi f_c t + \phi_t(t)\right) \tag{FMCW-1}
$$

where $f_c$ is the carrier frequency (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)) and $\phi_t(t)$ encodes any frequency modulation applied to the waveform. The signal propagates at the speed of light $c$ and encounters a target at range $R$.

### Round-Trip Delay

The signal travels from transmitter to target and back, covering a total path length of $2R$. The round-trip delay is:

$$
\tau = \frac{2R}{c} \tag{FMCW-2}
$$

where $\tau$ is the round-trip delay (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)).

### Doppler Shift from a Moving Target

If the target has a radial velocity $v$ (defined in the [Symbol Table](../00_notation/symbol_table.md#range-and-velocity)) with the convention that $v > 0$ corresponds to an approaching target, the range changes with time as $R(t) = R_0 - vt$. The round-trip delay becomes time-dependent:

$$
\tau(t) = \frac{2R(t)}{c} = \frac{2(R_0 - vt)}{c} \tag{FMCW-3}
$$

The received signal is a delayed and frequency-shifted copy of the transmitted signal. The frequency shift due to target motion -- the Doppler frequency -- is:

$$
f_d = \frac{2v}{\lambda} = \frac{2v f_c}{c} \tag{FMCW-4}
$$

where $\lambda = c / f_c$ is the wavelength (defined in the [Symbol Table](../00_notation/symbol_table.md#range-and-velocity)). The sign convention is that $f_d > 0$ for approaching targets ($v > 0$) and $f_d < 0$ for receding targets.

---

## 2. Radar Range Equation

The radar range equation relates the received signal power to the transmitted power, antenna characteristics, target properties, and propagation losses. It is derived step by step from first principles.

### Step 1: Transmitted Power Density

A transmitter radiates power $P_t$ (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)) through an antenna with gain $G$ (defined in the [Symbol Table](../00_notation/symbol_table.md#antenna-and-beamforming)). The power density at range $R$ from an isotropic radiator would be $P_t / (4\pi R^2)$. With antenna gain $G$, the power density at the target is:

$$
S_\text{inc} = \frac{P_t G}{4\pi R^2} \tag{FMCW-5}
$$

### Step 2: Power Intercepted by the Target

The target intercepts a portion of this incident power proportional to its radar cross section $\sigma$ (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)), which has units of area. The total power intercepted and re-radiated by the target is:

$$
P_\text{refl} = S_\text{inc} \cdot \sigma = \frac{P_t G \sigma}{4\pi R^2} \tag{FMCW-6}
$$

### Step 3: Reflected Power Density at the Receiver

The target re-radiates the intercepted power isotropically (by definition of $\sigma$). The power density of the reflected signal back at the receiver, at range $R$ from the target, is:

$$
S_\text{ret} = \frac{P_\text{refl}}{4\pi R^2} = \frac{P_t G \sigma}{(4\pi)^2 R^4} \tag{FMCW-7}
$$

### Step 4: Power Captured by the Receive Antenna

The receive antenna captures the reflected power through its effective aperture $A_e$. For an antenna with gain $G$ (assuming the same antenna is used for transmit and receive -- monostatic radar), the effective aperture is:

$$
A_e = \frac{G \lambda^2}{4\pi} \tag{FMCW-8}
$$

The received power is therefore:

$$
\begin{aligned}
P_r &= S_\text{ret} \cdot A_e \\
&= \frac{P_t G \sigma}{(4\pi)^2 R^4} \cdot \frac{G \lambda^2}{4\pi} \\
&= \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4}
\end{aligned}
\tag{FMCW-9}
$$

### Step 5: Noise Power

The receiver has a thermal noise floor determined by the noise bandwidth $B_n$ (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)), the reference temperature $T_0$, and the system noise figure $F$ (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)):

$$
P_n = k_B T_0 B_n F \tag{FMCW-10}
$$

where $k_B$ is the Boltzmann constant.

### Step 6: Signal-to-Noise Ratio

Combining the received power from Eq. (FMCW-9) with the noise power from Eq. (FMCW-10) and including total system losses $L$ (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)), the single-pulse signal-to-noise ratio is:

$$
\text{SNR} = \frac{P_r}{P_n} = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4 k_B T_0 B_n F L} \tag{FMCW-11}
$$

This is the **monostatic radar range equation** in SNR form. It applies to any pulsed or CW radar; the FMCW-specific processing gain from dechirp and FFT is addressed in subsequent sections.

> **Variant Note:**
> | | Nexus | Extended |
> |--|-------|----------|
> | $P_t$ per element | 1 W (ADTR1107) | 10 W (QPA2962 GaN) |
> | Antenna gain $G$ | TBD (8x16 patch array) | TBD (32x16 slotted waveguide) |
>
> See the [Parameter Table](../00_notation/parameter_table.md#rf-front-end) for current values and TBD status.

---

## 3. FMCW Modulation

In Frequency-Modulated Continuous Wave (FMCW) radar, the transmitted signal is a linear frequency modulated (LFM) chirp. During each chirp of duration $T_c$ (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)), the instantaneous frequency sweeps linearly across bandwidth $B$ (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)).

### Transmitted Signal

The chirp rate is $\mu = B / T_c$ (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)). Within a single chirp interval $0 \le t \le T_c$, the transmitted signal in complex baseband form is:

$$
s_t(t) = \exp\!\left(j2\pi\!\left(f_c t + \frac{\mu}{2} t^2\right)\right) \tag{FMCW-12}
$$

The instantaneous frequency is $f_i(t) = f_c + \mu t$, sweeping from $f_c$ to $f_c + B$ over the chirp duration.

### Received Signal

The signal reflects off a target at range $R$ moving with radial velocity $v$. Using the time-varying delay from Eq. (FMCW-3), the received signal is:

$$
s_r(t) = A_r \exp\!\left(j2\pi\!\left(f_c(t - \tau(t)) + \frac{\mu}{2}(t - \tau(t))^2\right)\right) \tag{FMCW-13}
$$

where $A_r$ accounts for the amplitude reduction from path loss, RCS, and antenna gain per the radar range equation (Eq. (FMCW-11)), and $\tau(t)$ is the time-varying round-trip delay from Eq. (FMCW-3).

### Dechirp Mixing

The FMCW receiver multiplies the received signal by the conjugate of the transmitted signal -- the **dechirp** or **stretch processing** operation:

$$
s_\text{IF}(t) = s_r(t) \cdot s_t^*(t) \tag{FMCW-14}
$$

This operation removes the chirp modulation and produces a constant-frequency tone whose frequency encodes the target range and velocity.

---

## 4. Beat Frequency Derivation (Full Form)

This section derives the complete beat frequency including both the range term and the Doppler term. The Doppler contribution is retained throughout -- it is **not** simplified away.

Substituting Eqs. (FMCW-12) and (FMCW-13) into the dechirp operation of Eq. (FMCW-14), the phase of the intermediate frequency (IF) signal is:

$$
\begin{aligned}
\phi_\text{IF}(t) &= 2\pi\!\left[f_c(t - \tau(t)) + \frac{\mu}{2}(t - \tau(t))^2\right] - 2\pi\!\left[f_c t + \frac{\mu}{2} t^2\right] \\
&= 2\pi\!\left[-f_c \tau(t) - \mu t \tau(t) + \frac{\mu}{2}\tau(t)^2\right]
\end{aligned}
\tag{FMCW-15}
$$

Substituting the time-varying delay $\tau(t) = 2(R_0 - vt)/c$ from Eq. (FMCW-3):

$$
\begin{aligned}
\phi_\text{IF}(t) &= 2\pi\!\left[-f_c \cdot \frac{2(R_0 - vt)}{c} - \mu t \cdot \frac{2(R_0 - vt)}{c} + \frac{\mu}{2}\!\left(\frac{2(R_0 - vt)}{c}\right)^{\!2}\right]
\end{aligned}
$$

Expanding and collecting terms by powers of $t$:

$$
\begin{aligned}
\phi_\text{IF}(t) &= -\frac{4\pi f_c R_0}{c}
+ 2\pi\!\left(\frac{2f_c v}{c} - \frac{2\mu R_0}{c}\right) t
+ 2\pi\!\left(\frac{2\mu v}{c}\right) t^2
+ \text{(residual video terms)}
\end{aligned}
$$

The instantaneous frequency of the IF signal is $(1/2\pi) \, d\phi_\text{IF}/dt$. Ignoring the $t^2$ term (the **residual video phase**, which is negligible for targets with $v \ll c$), the beat frequency is:

$$
\boxed{f_b = \frac{2\mu R_0}{c} \pm f_d = \frac{2\mu R_0}{c} \pm \frac{2v}{\lambda}} \tag{FMCW-16}
$$

This is the **full beat frequency equation** for FMCW radar. It consists of two terms:

1. **Range beat term** $f_R = 2\mu R_0 / c$: proportional to target range, arising from the delay-induced frequency offset between transmitted and received chirps.
2. **Doppler term** $\pm f_d = \pm 2v/\lambda$: proportional to target radial velocity, arising from the frequency shift of the carrier.

The sign convention is: $+f_d$ for approaching targets ($v > 0$), $-f_d$ for receding targets ($v < 0$), corresponding to the received frequency being shifted higher (approaching) or lower (receding) relative to the transmitted frequency.

The residual video phase term $2\mu v t^2 / c$ is negligible when $2\mu v T_c / c \ll f_b$, which holds for all realistic target velocities at the AERIS-10 operating frequencies. This term is sometimes called **range migration within a chirp** and becomes significant only for very long chirps or very high velocities.

---

## 5. Range Equation

For a **stationary target** ($v = 0$, hence $f_d = 0$), the beat frequency from Eq. (FMCW-16) reduces to the range beat term only:

$$
f_b \big|_{v=0} = \frac{2\mu R}{c} \tag{FMCW-17}
$$

Inverting for range:

$$
R = \frac{c \, f_b}{2\mu} \tag{FMCW-18}
$$

> **Stationary-Target Approximation:** Eq. (FMCW-18) is valid only when the Doppler contribution to the beat frequency is negligible compared to the range beat term, i.e., when:
>
> $$f_d \ll \frac{2\mu R}{c}$$
>
> For moving targets, the range estimate from Eq. (FMCW-18) is biased by $\pm f_d$. The range-Doppler coupling analysis in Section 9 quantifies this bias for the AERIS-10 chirp parameters.

---

## 6. Range Resolution

Two targets at ranges $R_1$ and $R_2$ produce beat frequencies $f_{b,1}$ and $f_{b,2}$. They are resolvable if the frequency difference exceeds the minimum resolvable frequency separation, which for a chirp of duration $T_c$ is $\Delta f_\text{min} = 1/T_c$.

From Eq. (FMCW-17):

$$
\begin{aligned}
\Delta f_b &= f_{b,2} - f_{b,1} = \frac{2\mu(R_2 - R_1)}{c} = \frac{2\mu \,\Delta R}{c}
\end{aligned}
$$

Setting $\Delta f_b = 1/T_c$ and using $\mu = B / T_c$:

$$
\begin{aligned}
\frac{1}{T_c} &= \frac{2 \cdot (B/T_c) \cdot \Delta R}{c} \\
\Delta R &= \frac{c}{2B}
\end{aligned}
\tag{FMCW-19}
$$

The range resolution $\Delta R$ (defined in the [Symbol Table](../00_notation/symbol_table.md#range-and-velocity)) depends only on the chirp bandwidth $B$ and is independent of chirp duration. Wider bandwidth yields finer range resolution.

> **Note:** The chirp bandwidth $B$ is currently TBD in the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing). Once resolved from the ADF4382 configuration, the numerical range resolution can be computed.

---

## 7. Velocity Measurement

Target velocity is extracted from the Doppler frequency $f_d$. In FMCW radar, $f_d$ is measured by observing the phase progression of the beat signal across $M$ successive chirps within a coherent processing interval (CPI).

Each chirp produces a complex sample of the beat signal at the target's range bin. Across $M$ chirps (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)), the phase of these samples advances by $2\pi f_d T_r$ per chirp, where $T_r$ is the pulse repetition interval (PRI). A Doppler FFT of size $M$ across the slow-time dimension extracts $f_d$.

From the Doppler frequency in Eq. (FMCW-4), the target radial velocity is:

$$
v = \frac{\lambda f_d}{2} \tag{FMCW-20}
$$

The velocity resolution is determined by the total CPI duration $M T_r$, which sets the minimum resolvable Doppler frequency $\Delta f_d = 1 / (M T_r)$:

$$
\Delta v = \frac{\lambda \, \Delta f_d}{2} = \frac{\lambda}{2 M T_r} \tag{FMCW-21}
$$

---

## 8. Maximum Unambiguous Range and Velocity

### Maximum Unambiguous Range

A target must produce its echo before the next chirp is transmitted; otherwise, the echo from range $R$ appears indistinguishable from a closer target illuminated by the subsequent chirp. The echo from the maximum unambiguous range must arrive within one PRI:

$$
\tau_\text{max} = \frac{2 R_\text{max}}{c} \le T_r
$$

Therefore:

$$
R_\text{max} = \frac{c \, T_r}{2} = \frac{c}{2 f_r} \tag{FMCW-22}
$$

where $f_r = 1/T_r$ is the pulse repetition frequency (defined in the [Symbol Table](../00_notation/symbol_table.md#waveform-and-timing-parameters)).

> **Variant Note:**
> | | Nexus | Extended |
> |--|-------|----------|
> | Long chirp PRI $T_{r,1}$ | 167 $\mu$s | 167 $\mu$s |
> | Short chirp PRI $T_{r,2}$ | 175 $\mu$s | 175 $\mu$s |
>
> See the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing) for all PRI values.

### Maximum Unambiguous Velocity

The Doppler frequency is sampled once per chirp at rate $f_r$. By the Nyquist sampling theorem, the maximum unambiguous Doppler frequency is $f_{d,\text{max}} = f_r / 2$. Using Eq. (FMCW-20):

$$
v_\text{max} = \frac{\lambda \, f_{d,\text{max}}}{2} = \frac{\lambda \, f_r}{4} \tag{FMCW-23}
$$

### Range-Velocity Tradeoff

Equations (FMCW-22) and (FMCW-23) are coupled through the PRF $f_r$. Their product yields the fundamental range-velocity ambiguity constraint:

$$
R_\text{max} \cdot v_\text{max} = \frac{c \, \lambda}{8} \tag{FMCW-24}
$$

This product depends only on the carrier frequency (through $\lambda$) and is a fixed constraint of the waveform. Increasing the PRF improves maximum unambiguous velocity at the cost of reduced maximum unambiguous range, and vice versa.

---

## 9. Range-Doppler Coupling Analysis

The full beat frequency in Eq. (FMCW-16) contains both a range term and a Doppler term. If the range is estimated from the beat frequency alone using the stationary-target approximation of Eq. (FMCW-18), the Doppler term introduces a range estimation error. This is **range-Doppler coupling**.

### Coupling Ratio

The severity of the coupling is characterized by the ratio of the Doppler term to the range beat term:

$$
\kappa = \frac{f_d}{f_R} = \frac{f_d}{\displaystyle\frac{2\mu R}{c}} = \frac{f_d \, c}{2\mu R} \tag{FMCW-25}
$$

where $\kappa$ is the coupling ratio. Substituting $\mu = B / T_c$ and $f_d = 2v/\lambda$:

$$
\kappa = \frac{2v \, c}{2 \lambda \cdot (B / T_c) \cdot R} = \frac{v \, c \, T_c}{\lambda \, B \, R} \tag{FMCW-26}
$$

The coupling is proportional to target velocity $v$ and chirp duration $T_c$, and inversely proportional to bandwidth $B$ and range $R$.

### Range Error from Doppler

When the Doppler term is neglected, the range estimate from Eq. (FMCW-18) includes an error:

$$
\Delta R_\text{Doppler} = \frac{c \, f_d}{2\mu} = \frac{c \, f_d \, T_c}{2B} = \frac{v \, T_c}{\lambda} \cdot \frac{c}{2B} \cdot \frac{\lambda}{1} = \frac{v \, T_c}{B} \cdot \frac{c \, f_c}{c} \cdot \frac{1}{f_c}
$$

Simplifying directly from the beat frequency:

$$
\Delta R_\text{Doppler} = \frac{c \, f_d}{2\mu} = \frac{v \, c \, T_c}{\lambda \, B} \tag{FMCW-27}
$$

This range error is independent of the true target range and depends on velocity, chirp duration, bandwidth, and wavelength.

### Comparison: Long Chirp vs. Short Chirp

The AERIS-10 system operates in two chirp modes with durations $T_{c,1}$ and $T_{c,2}$ (see the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing) for values). The coupling ratio from Eq. (FMCW-26) scales linearly with chirp duration. Taking the ratio of coupling for the two modes at the same range and velocity:

$$
\frac{\kappa_1}{\kappa_2} = \frac{T_{c,1}}{T_{c,2}} \tag{FMCW-28}
$$

Using the system values from the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing):

> **Variant Note -- Chirp Mode Comparison:**
> | | Long Chirp | Short Chirp |
> |--|-----------|-------------|
> | Chirp duration $T_c$ | $T_{c,1} = 30~\mu\text{s}$ | $T_{c,2} = 0.5~\mu\text{s}$ |
> | Duration ratio $T_{c,1} / T_{c,2}$ | 60 | 1 (reference) |
> | Relative coupling $\kappa$ | $60 \times \kappa_2$ | $\kappa_2$ |
>
> The long chirp has 60 times the coupling ratio of the short chirp. However, the long chirp also provides proportionally more range samples and better SNR through longer integration.

Although $\kappa_1 / \kappa_2 = 60$ shows the long chirp has higher absolute coupling, whether this is operationally significant depends on the chirp bandwidth $B$ (currently TBD). The coupling ratio from Eq. (FMCW-26) also contains $B$ in the denominator -- a large bandwidth reduces coupling for both modes.

For a concrete assessment: at a representative target velocity $v$ and range $R$, the range error from Eq. (FMCW-27) for each chirp mode is:

$$
\begin{aligned}
\Delta R_{\text{Doppler},1} &= \frac{v \, c \, T_{c,1}}{\lambda \, B} \\
\Delta R_{\text{Doppler},2} &= \frac{v \, c \, T_{c,2}}{\lambda \, B}
\end{aligned}
\tag{FMCW-29}
$$

These are to be evaluated numerically once $B$ is resolved in the [Parameter Table](../00_notation/parameter_table.md#tbd-tracking) and compared against the range resolution $\Delta R = c / (2B)$ from Eq. (FMCW-19) to determine whether the coupling produces errors exceeding one range bin.

### Compensation Approaches

Two standard approaches compensate for range-Doppler coupling in FMCW radar:

**1. Two-Dimensional FFT Processing (Range-Doppler Map)**

Rather than estimating range from the beat frequency of a single chirp, the FMCW processor constructs a range-Doppler map by performing:
- A **range FFT** on each chirp's IF samples to extract beat frequencies (range bins).
- A **Doppler FFT** across $M$ chirps at each range bin to extract the Doppler frequency.

The 2D FFT naturally separates the range and Doppler contributions to the beat frequency. The range dimension resolves $f_R = 2\mu R / c$, while the Doppler dimension resolves $f_d = 2v / \lambda$. This is the standard processing approach used in the AERIS-10 FPGA pipeline.

**2. Range Migration Correction**

For targets with high radial velocity, the target echo may shift across range bins during the CPI (a phenomenon called **range migration** or **range walk**). The migration over $M$ chirps is:

$$
\Delta R_\text{migration} = v \cdot M \cdot T_r \tag{FMCW-30}
$$

If $\Delta R_\text{migration} > \Delta R$ (the range resolution), the target energy spreads across multiple range bins, degrading detection performance. Range migration correction algorithms (e.g., Keystone transform or range-bin alignment) compensate by re-aligning the range bins before Doppler processing.

For the AERIS-10 system with $M$ chirps per CPI and PRI values $T_{r,1}$ and $T_{r,2}$, the migration distances are to be evaluated numerically once $B$ (and hence $\Delta R$) is determined, using values from the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing).

---

## References

- [Symbol Table](../00_notation/symbol_table.md) -- canonical symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both AERIS-10 variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- Skolnik, M.I., *Introduction to Radar Systems*, 4th ed., McGraw-Hill, 2008 -- Radar range equation derivation (Ch. 2), noise and detection fundamentals (Ch. 5)
- Richards, M.A., *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014 -- FMCW waveform analysis (Ch. 4), range-Doppler processing (Ch. 7)
