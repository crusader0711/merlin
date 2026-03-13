# Calibration Theory

**Purpose:** Model phase and amplitude errors in phased array elements, analyze the impact of ADAR1000 phase/amplitude quantization on beam pattern fidelity, and derive the measurement-based calibration correction procedure with residual error bounds.

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules
- [Beamforming Theory](03_beamforming_theory.md) -- array factor and phase model

---

## 1. Per-Element Error Model

In an ideal phased array, element $n$ contributes to the array factor with nominal amplitude weight $a_n$ (defined in the [Symbol Table](../00_notation/symbol_table.md#antenna-and-beamforming)) and the intended phase $n\psi$. In a real system, each element exhibits a phase error $\delta\phi_n$ (defined in the [Symbol Table](../00_notation/symbol_table.md#antenna-and-beamforming)) and an amplitude error $\delta a_n$ (defined in the [Symbol Table](../00_notation/symbol_table.md#antenna-and-beamforming)). The actual complex response of element $n$ is:

$$
h_n = (a_n + \delta a_n) \, e^{j\delta\phi_n} \tag{CAL-1}
$$

instead of the ideal response $a_n$. The error sources include:

- **Manufacturing tolerances:** variations in element geometry, feed network path lengths, and component values.
- **Component aging:** drift in phase shifter and attenuator characteristics over time.
- **Temperature drift:** thermal expansion altering element spacing and feed network electrical lengths.
- **Feed network imbalances:** unequal power splitting and phase delays in the corporate feed.

Each source contributes independently to $\delta\phi_n$ and $\delta a_n$. The total error at each element is the superposition of all sources.

---

## 2. Array Pattern with Errors

Substituting the per-element error model of Eq. (CAL-1) into the array factor of Eq. (BF-3) from [Beamforming Theory](03_beamforming_theory.md), the array factor with errors is:

$$
AF_\text{err}(\theta) = \sum_{n=0}^{N-1} (a_n + \delta a_n) \, e^{j(n\psi + \delta\phi_n)} \tag{CAL-2}
$$

This can be decomposed into the ideal array factor plus a perturbation term. Expanding:

$$
\begin{aligned}
AF_\text{err}(\theta) &= \sum_{n=0}^{N-1} a_n \, e^{jn\psi} \cdot e^{j\delta\phi_n} + \sum_{n=0}^{N-1} \delta a_n \, e^{j(n\psi + \delta\phi_n)}
\end{aligned}
$$

For small errors ($|\delta\phi_n| \ll 1$ and $|\delta a_n / a_n| \ll 1$), using $e^{j\delta\phi_n} \approx 1 + j\delta\phi_n$:

$$
\begin{aligned}
AF_\text{err}(\theta) &\approx \underbrace{\sum_{n=0}^{N-1} a_n \, e^{jn\psi}}_{AF_\text{ideal}(\theta)} + \underbrace{\sum_{n=0}^{N-1} (j a_n \delta\phi_n + \delta a_n) \, e^{jn\psi}}_{\Delta AF(\theta)}
\end{aligned}
\tag{CAL-3}
$$

The perturbation $\Delta AF(\theta)$ represents the difference between the actual and ideal patterns. It is a weighted sum over the array with error-dependent coefficients, and its angular structure determines how the errors distort the beam pattern.

---

## 3. RMS Sidelobe Level with Random Errors

When the errors $\delta\phi_n$ and $\delta a_n$ are modeled as zero-mean random variables (appropriate for manufacturing tolerances and aging effects), the average sidelobe power can be derived statistically. Following the Mailloux formulation, the expected value of the sidelobe power relative to the main beam is:

$$
\overline{\text{SLL}} \approx \frac{1}{N} \sum_{n=0}^{N-1} \left(\left|\frac{\delta a_n}{a_n}\right|^2 + |\delta\phi_n|^2\right) \tag{CAL-4}
$$

For uniform weights ($a_n = 1$) and identically distributed errors with RMS amplitude error $\sigma_a$ and RMS phase error $\sigma_\phi$ (in radians):

$$
\overline{\text{SLL}} \approx \sigma_a^2 + \sigma_\phi^2 \tag{CAL-5}
$$

Physical interpretation: random errors raise the average sidelobe floor to a level determined by the sum of the amplitude and phase error variances. This floor is independent of the taper and acts as a lower bound on achievable sidelobe performance. For example, to maintain an average sidelobe floor below $-30$ dB ($\overline{\text{SLL}} < 10^{-3}$), the combined error variance must satisfy $\sigma_a^2 + \sigma_\phi^2 < 10^{-3}$, requiring RMS errors below approximately $\sigma_\phi < 1.8°$ and $\sigma_a < 0.032$ ($3.2\%$).

---

## 4. ADAR1000 Phase Quantization

The ADAR1000 beamformer IC provides discrete phase control with 128 states over a full $360°$ range (7-bit resolution). The phase step size is:

$$
\Delta\phi_\text{step} = \frac{360°}{128} = 2.8125° \tag{CAL-6}
$$

The maximum phase quantization error for any desired phase setting is half the step size:

$$
|\delta\phi_\text{quant}| \le \frac{\Delta\phi_\text{step}}{2} = 1.40625° \approx 0.0245~\text{rad} \tag{CAL-7}
$$

**This error is deterministic, not random.** For a given set of desired phase shifts (determined by the steering angle $\theta_0$), each element's quantization error is a fixed, predictable value -- the difference between the desired continuous phase and the nearest available discrete state. The error pattern repeats exactly every time the beam is steered to the same angle.

### Beam Pointing Error

The quantization errors produce a systematic bias in the beam pointing direction. The beam pointing error due to phase quantization is bounded by:

$$
|\Delta\theta_\text{quant}| \le \frac{\Delta\phi_\text{step}}{2kd\cos\theta_0} = \frac{\Delta\phi_\text{step}}{2 \cdot (2\pi d/\lambda) \cdot \cos\theta_0} \tag{CAL-8}
$$

This bound follows from the sensitivity of the steering equation Eq. (BF-4) in [Beamforming Theory](03_beamforming_theory.md) to phase perturbations. The pointing error increases with scan angle ($1/\cos\theta_0$) because the same phase error maps to a larger angular error when the beam is steered away from broadside.

### Peak Sidelobe Degradation

Because the quantization error pattern is deterministic and periodic (with period related to the phase step size and steering angle), it creates specific spurious sidelobes at predictable angular locations rather than raising the average sidelobe floor uniformly as random errors do (Eq. (CAL-5)). The peak quantization sidelobe level for $N$ elements with maximum quantization error $\delta\phi_\text{max}$ is approximately:

$$
\text{SLL}_\text{quant} \approx \frac{1}{N} \left(\frac{N \delta\phi_\text{max}}{2}\right)^{\!2} = \frac{N \delta\phi_\text{max}^2}{4} \tag{CAL-9}
$$

For $N = 16$ and $\delta\phi_\text{max} = 0.0245$ rad, this evaluates to approximately $-29$ dB. The 7-bit phase resolution is therefore sufficient for sidelobe requirements up to approximately $-25$ to $-30$ dB, but the deterministic quantization lobes must be analyzed for each specific steering angle to ensure they do not coincide with critical angular sectors.

---

## 5. ADAR1000 Amplitude Quantization

The ADAR1000 provides independent gain control per element through a variable attenuator. The attenuator offers discrete amplitude settings that limit how precisely amplitude tapers (Taylor, Chebyshev) can be realized.

The amplitude quantization error for element $n$ is:

$$
\delta a_{\text{quant},n} = a_{n,\text{actual}} - a_{n,\text{desired}} \tag{CAL-10}
$$

where $a_{n,\text{actual}}$ is the nearest available discrete gain setting to the desired weight $a_{n,\text{desired}}$.

The impact on taper accuracy is most significant for tapering functions with large dynamic range (ratio of maximum to minimum weight). The Chebyshev taper, which requires precise edge-element weights, is more sensitive to amplitude quantization than the Taylor taper, which has smoother weight variation across the aperture. The achievable sidelobe level is bounded by the amplitude quantization floor in the same manner as Eq. (CAL-5), with $\sigma_a$ replaced by the RMS amplitude quantization error.

---

## 6. Mutual Coupling Effects

Mutual coupling between array elements modifies the effective excitation of each element. When element $n$ is driven, it induces currents on neighboring elements through electromagnetic coupling. This effect is captured by the coupling matrix $\mathbf{C}$, an $N \times N$ matrix where entry $C_{mn}$ represents the coupling coefficient from element $n$ to element $m$.

The actual element excitation vector $\mathbf{v}_\text{actual}$ differs from the intended excitation $\mathbf{w}$ due to coupling:

$$
\mathbf{v}_\text{actual} = \mathbf{C} \, \mathbf{w} \tag{CAL-11}
$$

To achieve the desired excitation (and hence the desired beam pattern from Eq. (BF-3) in [Beamforming Theory](03_beamforming_theory.md)), the applied weights must pre-compensate for coupling:

$$
\mathbf{w}_\text{applied} = \mathbf{C}^{-1} \mathbf{w}_\text{desired} \tag{CAL-12}
$$

This inversion requires knowledge of $\mathbf{C}$, which can be obtained from electromagnetic simulation, direct S-parameter measurement, or estimated through the calibration procedure described in the next section.

The active element pattern for element $n$ in the array environment is:

$$
F_{e,n}^\text{active}(\theta) = \sum_{m=0}^{N-1} C_{mn} \, F_e(\theta) \, e^{jmkd\sin\theta}
$$

where $F_e(\theta)$ is the isolated element pattern. For interior elements of a large array, the coupling environment is approximately uniform, and the active element pattern is nearly identical across elements. Edge elements experience asymmetric coupling and require individual characterization.

---

## 7. Calibration Correction Procedure

Measurement-based calibration determines the per-element complex error and computes a correction vector to restore ideal array performance. The procedure consists of four steps.

### Step 1: Measurement

Inject a known signal and measure the complex response of each element. Methods include:

- **Far-field source:** place a reference transmitter at a known angle and measure each element's output individually (by disabling all other elements or using element-level digitization).
- **Mutual coupling self-calibration:** exploit the known coupling between adjacent elements to extract relative phase and amplitude differences without an external source.

The measured complex response of element $n$ is:

$$
h_{n,\text{meas}} = (a_n + \delta a_n) \, e^{j\delta\phi_n} \cdot S_\text{ref} \tag{CAL-13}
$$

where $S_\text{ref}$ is the known reference signal (common to all elements and cancelled in the ratio below).

### Step 2: Compute Correction Vector

The correction for element $n$ is the ratio of the ideal response to the measured response:

$$
c_n = \frac{a_n}{h_{n,\text{meas}} / S_\text{ref}} = \frac{a_n}{(a_n + \delta a_n) \, e^{j\delta\phi_n}} \tag{CAL-14}
$$

This correction simultaneously compensates both amplitude and phase errors. Its magnitude corrects the amplitude ($|c_n| = a_n / (a_n + \delta a_n)$) and its phase corrects the phase error ($\angle c_n = -\delta\phi_n$).

### Step 3: Apply Correction

The correction is applied through the ADAR1000 phase and gain registers. For each element $n$:

- Set the phase register to the desired steering phase plus the phase correction: $\phi_{n,\text{applied}} = n \cdot (-kd\sin\theta_0) + \angle c_n$.
- Set the gain register to the desired amplitude weight scaled by the amplitude correction: $a_{n,\text{applied}} = a_{n,\text{desired}} \cdot |c_n|$.

### Step 4: Verify

After applying corrections, measure the array pattern (or a set of diagnostic beam positions) and compare against the expected pattern from [Beamforming Theory](03_beamforming_theory.md). If residual errors exceed the specification, iterate the calibration measurement.

---

## 8. Residual Error Analysis

Even with perfect calibration measurement (zero measurement noise), the discrete phase and amplitude steps of the ADAR1000 create a floor on achievable correction accuracy. The applied correction is quantized to the nearest available ADAR1000 state, leaving a residual error.

### Residual Phase Error

The correction phase $\angle c_n$ is quantized to the nearest ADAR1000 phase state. The residual phase error after calibration is bounded by half the phase step:

$$
|\delta\phi_{n,\text{residual}}| \le \frac{\Delta\phi_\text{step}}{2} \tag{CAL-15}
$$

This is identical to Eq. (CAL-7) -- calibration cannot reduce the phase error below the quantization floor.

### Residual Amplitude Error

Similarly, the correction amplitude $|c_n|$ is quantized to the nearest attenuator setting, leaving a residual amplitude error bounded by half the amplitude step size.

### Post-Calibration Sidelobe Floor

The residual errors after calibration are deterministic (determined by the specific quantization of each element's correction). The worst-case post-calibration sidelobe level combines the residual quantization errors from Eq. (CAL-9) with any measurement noise in the calibration data:

$$
\text{SLL}_\text{post-cal} \ge \text{SLL}_\text{quant} \tag{CAL-16}
$$

The quantization-limited sidelobe floor from Eq. (CAL-9) represents the fundamental performance limit of the ADAR1000 beamformer. No calibration procedure can achieve sidelobe levels below this floor without either:
- Increasing the phase/amplitude resolution (different hardware),
- Applying algorithmic compensation that accounts for the deterministic quantization pattern, or
- Using element-level digital beamforming to bypass the analog quantization entirely.

---

## References

- [Symbol Table](../00_notation/symbol_table.md) -- canonical symbol definitions
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both AERIS-10 variants
- [Conventions](../00_notation/conventions.md) -- equation numbering and formatting rules
- [Beamforming Theory](03_beamforming_theory.md) -- array factor Eq. (BF-3), steering Eq. (BF-4), and beam pattern equations
- Mailloux, R.J., *Phased Array Antenna Handbook*, 3rd ed., Artech House, 2018 -- Error analysis (Ch. 7), quantization effects (Ch. 7.3), calibration procedures (Ch. 7.5)
- Skolnik, M.I., *Introduction to Radar Systems*, 4th ed., McGraw-Hill, 2008 -- Phased array errors and calibration (Ch. 9)
