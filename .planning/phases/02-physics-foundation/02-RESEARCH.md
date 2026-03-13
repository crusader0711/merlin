# Phase 2: Physics Foundation - Research

**Researched:** 2026-03-13
**Domain:** FMCW radar physics, signal models, beamforming, detection theory, noise analysis
**Confidence:** HIGH

## Summary

Phase 2 derives the complete physics foundation for the AERIS-10 radar system from first principles. This covers seven requirement areas: FMCW theory (PHYS-01), LFM waveform model (PHYS-02), beamforming theory (PHYS-03), detection theory (PHYS-04), range-Doppler coupling (PHYS-05), noise figure chain (PHYS-06), and antenna calibration theory (PHYS-07). All derivations are pure mathematics grounded in electromagnetic theory and signal processing fundamentals -- no hardware component model numbers or implementation details belong in this layer. The physics documents will be referenced by every downstream phase (hardware, software, research).

The domain is mature and well-established. FMCW radar theory follows standard treatments in Skolnik ("Introduction to Radar Systems"), Richards ("Fundamentals of Radar Signal Processing"), and Mahafza ("Radar Systems Analysis and Design Using MATLAB"). The derivation structure is deterministic: Maxwell's equations lead to the radar equation; the radar equation with LFM waveform produces beat frequency and range/velocity relationships; the array factor derivation produces beamforming equations; Neyman-Pearson criterion produces CFAR thresholds. The primary risk is not physics complexity but documentation discipline: maintaining consistent notation from the Phase 1 symbol table, using the correct `\tag{}` numbering scheme, keeping derivations symbolic (no inline numerical values), and correctly handling the two-variant system (Nexus vs Extended) with callout blocks.

There are TBD parameters in the parameter table that affect physics derivations: chirp bandwidth $B$, LNA noise figure $F_\text{LNA}$, and antenna gains $G$ for both variants. The derivations must remain symbolic so they are valid regardless of these values. Where numerical evaluation is needed (e.g., range resolution, detection range), the documents should reference the parameter table and note TBD status explicitly.

**Primary recommendation:** Structure as 4 primary documents plus 3 supplementary analysis documents, following the equation prefix conventions from Phase 1. Keep all derivations fully symbolic with parameter table references. Derive the full beat frequency with Doppler term first (PHYS-05), then introduce the stationary-target simplification as a clearly labeled approximation.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PHYS-01 | FMCW theory -- radar equation from first principles, beat frequency, range equation, velocity measurement | Standard Skolnik/Richards derivation path: EM wave propagation -> radar range equation -> FMCW dechirp mixing -> beat frequency -> range/velocity extraction. Use FMCW-N tags. |
| PHYS-02 | LFM waveform model -- chirp signal math, time-bandwidth product, pulse compression gain, ambiguity function | Chirp signal s(t), instantaneous frequency, time-bandwidth product BT, matched filter SNR gain, ambiguity function chi(tau, nu). Use LFM-N tags. |
| PHYS-03 | Beamforming theory -- array factor, phase shift per element for ADAR1000, grating lobe conditions, beam patterns | ULA array factor derivation, progressive phase shift, grating lobe condition d sin(theta) = m*lambda, beam pattern plots. Use BF-N tags. |
| PHYS-04 | Detection theory -- CFAR derivation with Neyman-Pearson, false alarm probability, detection probability curves | Neyman-Pearson lemma -> likelihood ratio test -> threshold -> P_fa/P_d in Gaussian noise -> CA-CFAR sliding window derivation. Use DET-N tags. |
| PHYS-05 | Range-Doppler coupling analysis -- full beat frequency with Doppler term, impact on 30us vs 0.5us chirps | Derive f_b = (2*mu*R)/c + f_d, show coupling ratio mu*T_c dependence, compare 30us vs 0.5us chirp impact, compensation approaches. |
| PHYS-06 | Noise figure chain analysis -- cascaded NF through LNA, mixer, ADC, CIC filter | Friis formula for cascaded noise figure, stage-by-stage analysis, digital processing noise contribution (CIC filter noise growth). Use NF-N tags. |
| PHYS-07 | Antenna array calibration theory -- phase/amplitude error correction, ADAR1000 phase quantization effects | Phase/amplitude error model, array pattern degradation with errors, ADAR1000 quantization (11.25 deg steps), calibration correction matrix. Use CAL-N tags. |
</phase_requirements>

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| GitHub Markdown + MathJax | Native (MathJax 3.x) | All physics derivation documents | Zero build step; `\tag{}` confirmed working; renders display math in-browser |
| `\tag{PREFIX-N}` numbering | MathJax built-in | Equation numbering per conventions.md | Document-prefix scheme (FMCW-N, LFM-N, BF-N, DET-N, NF-N, CAL-N) guarantees cross-project uniqueness |
| `\begin{aligned}...\end{aligned}` | MathJax built-in | Multi-line derivations | Only reliable multi-line math on GitHub; single `\tag{}` per block |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| Python + matplotlib | Beam pattern plots, ambiguity function surfaces, detection probability curves | Generate SVG figures for embedding in physics docs |
| Variant callout blocks | Nexus vs Extended parameter differences | Wherever derivation parameters differ between variants |

### Reference Texts

| Text | Author(s) | Use |
|------|-----------|-----|
| Introduction to Radar Systems (4th ed.) | Skolnik | Radar equation, noise figure, detection theory fundamentals |
| Fundamentals of Radar Signal Processing (2nd ed.) | Richards | LFM waveform model, ambiguity function, matched filter theory |
| Radar Systems Analysis and Design Using MATLAB (3rd ed.) | Mahafza | CFAR derivation, beamforming patterns, numerical validation |
| Phased Array Antenna Handbook (3rd ed.) | Mailloux | Array factor, grating lobes, calibration theory |
| IEEE 686-2024 | IEEE | Notation authority (via Phase 1 symbol table) |

## Architecture Patterns

### Recommended Document Structure

```
01_physics/
  01_fmcw_theory.md          # PHYS-01 + PHYS-05: FMCW fundamentals + range-Doppler coupling
  02_lfm_waveform_model.md   # PHYS-02: LFM chirp signal, pulse compression, ambiguity function
  03_beamforming_theory.md   # PHYS-03: Array factor, steering, grating lobes
  04_detection_theory.md     # PHYS-04: Neyman-Pearson, CFAR derivation
  05_noise_analysis.md       # PHYS-06: Cascaded noise figure chain
  06_calibration_theory.md   # PHYS-07: Phase/amplitude error correction
```

### Document Dependency Order

```
01_fmcw_theory.md
  |
  +--> 02_lfm_waveform_model.md (references beat frequency, range equation)
  |       |
  |       +--> 04_detection_theory.md (references SNR from matched filter)
  |
  +--> 03_beamforming_theory.md (references wavelength, frequency from FMCW)
  |       |
  |       +--> 06_calibration_theory.md (references array factor, phase model)
  |
  +--> 05_noise_analysis.md (references radar equation SNR)
```

The FMCW theory document is the root dependency. It must be written first. Documents 02 and 03 can proceed in parallel after 01 is complete. Documents 04, 05, and 06 depend on their respective parents.

### Pattern 1: First-Principles Derivation Flow

**What:** Each physics document follows a consistent derivation progression: fundamental principle -> mathematical model -> system-specific application -> variant callout.

**When to use:** Every derivation in this phase.

**Structure:**
```markdown
## N. [Topic Name]

[Prose introducing the physical principle and why it matters for FMCW radar]

Starting from [fundamental equation/principle]:

$$
[fundamental equation] \tag{PREFIX-1}
$$

[Derivation steps with prose explaining each transition]

$$
[intermediate result] \tag{PREFIX-2}
$$

[Final result with physical interpretation]

$$
[final result] \tag{PREFIX-3}
$$

> **Variant Note:**
> | | Nexus | Extended |
> |--|-------|----------|
> | [differing parameter] | [value] | [value] |
```

### Pattern 2: Symbolic-Only Derivations

**What:** All derivations use symbols from the symbol table. Numerical values appear ONLY in variant callout blocks or explicit "numerical evaluation" subsections that reference parameter_table.md.

**Why:** Keeps derivations general; avoids the anti-pattern of hardcoding values into equations.

### Anti-Patterns to Avoid

- **Skipping intermediate steps:** Engineering audience expects to trace every algebraic step. Do not jump from radar equation to final range expression without showing the dechirp mixing, beat frequency extraction, and range inversion steps.
- **Stationary-target simplification without flagging:** The simplified beat frequency $f_b = 2\mu R/c$ omits the Doppler term. Always derive the full expression $f_b = 2\mu R/c \pm f_d$ first, then introduce the simplification as a labeled approximation with conditions for validity.
- **Inline numerical values in derivations:** Never write $\Delta R = c/2B = 0.375$ m. Write $\Delta R = c/2B$ and reference the parameter table.
- **Redefining symbols:** Never introduce a symbol not in symbol_table.md. If a new symbol is needed, add it to the symbol table first, then use it.
- **Mixing physics and hardware:** Physics documents describe mathematical models. Component model numbers (ADAR1000, ADTR1107) belong in hardware documentation. The beamforming document derives the array factor for a generic N-element ULA with inter-element spacing d; the hardware document applies it to the specific 16-element ADAR1000 configuration.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Ambiguity function derivation | Ad-hoc derivation from scratch | Standard Richards/Levanon treatment of chi(tau, nu) for LFM | The LFM ambiguity function is a well-known closed-form result; deriving it incorrectly is easy and produces wrong sidelobe predictions |
| Cascaded noise figure | Custom noise chain formula | Friis formula (standard cascade) | Friis formula handles arbitrary N-stage cascade; hand-rolling a custom formula for 4 stages risks sign errors in dB/linear conversions |
| CFAR false alarm probability | Direct integration of threshold exceedance | Standard CA-CFAR P_fa formula from Skolnik/Richards | The P_fa for CA-CFAR with N reference cells is $(1 + T/N)^{-N}$ where T is threshold multiplier; deriving from scratch requires careful handling of chi-squared distributions |
| Array pattern with errors | Monte Carlo only | Analytical error model (Mailloux) + Monte Carlo validation | Analytical model gives closed-form relationship between phase error variance and sidelobe level; Monte Carlo alone gives no insight |

## Common Pitfalls

### Pitfall 1: Range-Doppler Coupling Omission
**What goes wrong:** The beat frequency is derived as $f_b = 2\mu R/c$ without the Doppler term, making all downstream range calculations wrong for moving targets.
**Why it happens:** Most introductory FMCW treatments assume stationary targets for simplicity.
**How to avoid:** Derive the full beat frequency $f_b = 2\mu R/c \pm f_d$ in Section 1 of the FMCW theory document. Dedicate PHYS-05 to analyzing the coupling ratio. Show that for the 30 us chirp with large bandwidth, the Doppler shift is a small fraction of the beat frequency, but for the 0.5 us chirp, the coupling is proportionally much larger.
**Warning signs:** If the FMCW document has no Doppler term in the beat frequency equation, the derivation is incomplete.

### Pitfall 2: dB vs Linear Confusion in Noise Figure Chain
**What goes wrong:** Mixing dB and linear noise figure values in Friis formula produces wildly incorrect cascaded noise figures.
**Why it happens:** Component datasheets specify NF in dB; Friis formula requires linear F values.
**How to avoid:** State Friis formula in linear (F), explicitly show the dB-to-linear conversion step, work the entire cascade in linear, convert the result back to dB at the end. Include a clearly labeled conversion reminder.
**Warning signs:** If cascaded NF values seem unreasonably low (below LNA NF) or high (above sum of all stages), there is a dB/linear error.

### Pitfall 3: Grating Lobe Condition for Half-Wavelength Spacing
**What goes wrong:** Concluding that $d = \lambda/2$ spacing eliminates grating lobes for all scan angles, when in fact it only eliminates them for broadside. At maximum scan angle, the visible-space boundary shifts.
**Why it happens:** The standard textbook statement "$d \leq \lambda/2$ prevents grating lobes" is correct for the full $\pm 90$ degree scan range. But the AERIS-10 scans to approximately $\pm 33$ degrees (based on ADAR1000 phase range), so the grating lobe condition can actually be relaxed -- $d$ could be larger than $\lambda/2$ without grating lobes appearing in the scan range. The derivation must show this nuance.
**How to avoid:** Derive the general grating lobe condition $d(\sin\theta_0 + \sin\theta_\text{GL}) = m\lambda$ and evaluate for the actual scan range, not just the theoretical maximum.

### Pitfall 4: CIC Filter Noise Growth Ignored in Noise Chain
**What goes wrong:** The noise figure chain stops at the ADC and ignores digital processing noise contributions, particularly CIC filter noise growth from limited wordlength.
**Why it happens:** Traditional Friis analysis covers analog components only. The CIC decimator adds quantization noise and has passband droop that affects effective SNR.
**How to avoid:** Extend the noise analysis past the ADC to include CIC filter noise growth. The CIC filter with $N_\text{CIC}$ stages and decimation factor $D_\text{CIC}$ has a processing gain of $D_\text{CIC}^{N_\text{CIC}}$ in the ideal case, but bit growth and truncation reduce this. Document the effective noise figure contribution of the digital processing chain.

### Pitfall 5: ADAR1000 Phase Quantization Underestimated
**What goes wrong:** Treating the ADAR1000 as having continuous phase control when it actually has discrete phase steps.
**Why it happens:** The ADAR1000 datasheet specifies 360 degrees in 2.8 degree steps (approximately 128 states, 7-bit resolution). This quantization produces deterministic phase errors that affect beam pointing accuracy and sidelobe levels.
**How to avoid:** Model the phase quantization as a deterministic error (not random) with maximum error of half the step size (1.4 degrees). Derive the impact on beam pointing error and peak sidelobe level. The ADAR1000 also has independent gain control per element (attenuator) -- document both phase and amplitude quantization effects.

### Pitfall 6: Ambiguity Function Plotted but Not Interpreted
**What goes wrong:** The LFM ambiguity function is derived and plotted but not connected to the system's actual range and Doppler resolution, coupling, and sidelobe behavior.
**Why it happens:** The ambiguity function is mathematically elegant but its practical implications require careful interpretation specific to the system parameters.
**How to avoid:** After deriving the general LFM ambiguity function, explicitly extract: (1) range resolution from the -3 dB width of the zero-Doppler cut, (2) velocity resolution from the -3 dB width of the zero-delay cut, (3) range-Doppler coupling slope from the ridge orientation, (4) first sidelobe level and its impact on masking weak targets near strong ones.

## Code Examples

### FMCW Beat Frequency Derivation (Full Form)
```markdown
The transmitted LFM signal and received (delayed + Doppler-shifted) signal mix to produce:

$$
f_b = \frac{2\mu R}{c} \pm f_d = \frac{2\mu R}{c} \pm \frac{2v}{\lambda} \tag{FMCW-4}
$$

where the $+$ sign applies for approaching targets and $-$ for receding targets
(using the convention that $v > 0$ means approaching). The first term is the
**range beat** and the second is the **Doppler shift**.
```

### Array Factor for ULA
```markdown
For a uniform linear array of $N$ elements with inter-element spacing $d$
and progressive phase shift $\Delta\phi$:

$$
AF(\theta) = \sum_{n=0}^{N-1} w_n \, e^{jn(kd\sin\theta + \Delta\phi)} \tag{BF-1}
$$

where $k = 2\pi/\lambda$ is the wavenumber, $w_n$ is the amplitude weight
for element $n$ (defined in the [Symbol Table](../00_notation/symbol_table.md)),
and $\Delta\phi = -kd\sin\theta_0$ steers the beam to angle $\theta_0$.
```

### CA-CFAR Threshold
```markdown
For Cell-Averaging CFAR with $N_\text{ref}$ reference cells (total, both
sides of the cell under test), the threshold multiplier $\alpha$ that
achieves a desired false alarm probability $P_{fa}$ is:

$$
\alpha = N_\text{ref} \left( P_{fa}^{-1/N_\text{ref}} - 1 \right) \tag{DET-5}
$$

This result assumes the reference cells contain i.i.d. exponentially
distributed noise samples (Swerling Case 0 target model).
```

### Friis Cascaded Noise Figure
```markdown
For an $M$-stage receive chain with individual noise figures $F_1, F_2, \ldots, F_M$
and available gains $G_1, G_2, \ldots, G_M$ (all in linear, NOT dB):

$$
F_\text{sys} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2} + \cdots + \frac{F_M - 1}{\prod_{i=1}^{M-1} G_i} \tag{NF-1}
$$

Converting: $F_\text{linear} = 10^{\text{NF}_\text{dB}/10}$ and
$\text{NF}_\text{sys,dB} = 10 \log_{10}(F_\text{sys})$.
```

## Detailed Derivation Roadmap

### Document 1: FMCW Theory (01_fmcw_theory.md) -- Prefix: FMCW

Covers PHYS-01 and PHYS-05.

**Section flow:**
1. **Electromagnetic wave propagation** -- plane wave, round-trip delay $\tau = 2R/c$, Doppler shift from moving target
2. **Radar range equation** -- derive from first principles (power density, RCS, effective aperture, noise power): $\text{SNR} = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4 k_B T_0 B_n F L}$
3. **FMCW modulation** -- LFM chirp transmitted, received signal delayed and Doppler-shifted, dechirp mixing operation
4. **Beat frequency derivation (FULL)** -- derive $f_b = 2\mu R/c \pm f_d$ with both range and Doppler terms (PHYS-05 core)
5. **Range equation** -- invert beat frequency: $R = c f_b / (2\mu)$ (stationary target approximation, labeled)
6. **Range resolution** -- $\Delta R = c / (2B)$
7. **Velocity measurement** -- Doppler frequency across CPI: $v = \lambda f_d / 2$
8. **Maximum unambiguous range and velocity** -- $R_\text{max} = c / (2 f_r)$, $v_\text{max} = \lambda f_r / 4$
9. **Range-Doppler coupling analysis (PHYS-05)** -- coupling ratio $f_d / (2\mu R/c)$, evaluate for $T_{c,1} = 30$ us vs $T_{c,2} = 0.5$ us, compensation approaches (2D FFT processing, range migration correction)

**Equation budget:** FMCW-1 through approximately FMCW-20.

**Variant callouts:** Transmit power $P_t$ (1 W Nexus vs 10 W Extended), antenna gain $G$ (TBD for both), maximum detection range.

### Document 2: LFM Waveform Model (02_lfm_waveform_model.md) -- Prefix: LFM

Covers PHYS-02.

**Section flow:**
1. **LFM chirp signal** -- $s(t) = \text{rect}(t/T_c) \exp(j2\pi(f_c t + \mu t^2/2))$, instantaneous frequency $f_i(t) = f_c + \mu t$
2. **Time-bandwidth product** -- $BT_c$ and its significance for pulse compression
3. **Matched filter theory** -- optimal filter $h(t) = s^*(-t)$, output SNR gain = $BT_c$
4. **Pulse compression** -- compressed pulse width $\tau_c = 1/B$, range resolution connection
5. **Sidelobe structure** -- sinc-like compressed pulse, first sidelobe at -13.3 dB, windowing tradeoffs (Hamming, Taylor)
6. **Ambiguity function** -- $|\chi(\tau, \nu)| = |\text{sinc}(B\tau - \mu T_c \tau \nu)| \cdot |\text{sinc}(T_c \nu)|$ (simplified), ridge slope = $\mu$, range-Doppler coupling visualization
7. **System-specific analysis** -- BT product for both chirp modes ($T_{c,1}$ and $T_{c,2}$), processing gain comparison

**Equation budget:** LFM-1 through approximately LFM-15.

### Document 3: Beamforming Theory (03_beamforming_theory.md) -- Prefix: BF

Covers PHYS-03.

**Section flow:**
1. **Uniform linear array (ULA) geometry** -- element positions, far-field assumption, path length differences
2. **Array factor derivation** -- $AF(\theta) = \sum w_n e^{jn\psi}$ where $\psi = kd\sin\theta + \Delta\phi$
3. **Beam steering** -- set $\Delta\phi = -kd\sin\theta_0$ to steer to $\theta_0$
4. **Closed-form array factor** -- geometric series result for uniform weights: $AF(\theta) = \sin(N\psi/2) / \sin(\psi/2)$
5. **Half-power beamwidth** -- $\theta_{3\text{dB}} \approx 0.886\lambda / (Nd\cos\theta_0)$ for broadside
6. **Grating lobe conditions** -- general condition $d(\sin\theta_0 + \sin\theta_\text{GL}) = m\lambda$, evaluate for $d = \lambda/2$ with scan range $\pm 33$ degrees
7. **Element pattern and mutual coupling** -- effect of individual element pattern on total pattern
8. **Amplitude tapering** -- Taylor, Chebyshev weighting for sidelobe reduction, tradeoff with beamwidth
9. **2D beam pattern** -- extension to planar array (8x2 subarray configuration)

**Equation budget:** BF-1 through approximately BF-15.

**New symbols needed in symbol_table.md:** $k$ (wavenumber), $\psi$ (electrical angle), $w_n$ (element weight), $\theta_0$ (steering angle), $\theta_{3\text{dB}}$ (half-power beamwidth). Check symbol table -- $w[n]$ exists for window function; $w_n$ for element weights may need disambiguation.

### Document 4: Detection Theory (04_detection_theory.md) -- Prefix: DET

Covers PHYS-04.

**Section flow:**
1. **Binary hypothesis testing** -- $H_0$ (noise only) vs $H_1$ (signal + noise)
2. **Neyman-Pearson lemma** -- maximize $P_d$ subject to $P_{fa} \leq \alpha$, likelihood ratio test
3. **Gaussian noise model** -- threshold for known signal in Gaussian noise, $P_{fa}$ and $P_d$ in terms of Q-function
4. **Square-law detector** -- magnitude-squared of complex signal, exponential distribution under $H_0$, non-central chi-squared under $H_1$
5. **Swerling target models** -- Cases 0 (non-fluctuating), I, II, III, IV; probability distributions for RCS fluctuation
6. **CA-CFAR derivation** -- sliding window, reference cells, guard cells, threshold multiplier $\alpha = N_\text{ref}(P_{fa}^{-1/N_\text{ref}} - 1)$
7. **Detection probability curves** -- $P_d$ vs SNR for various $P_{fa}$ values and Swerling cases
8. **CFAR loss** -- SNR penalty of CFAR vs fixed threshold, dependence on reference window size
9. **Non-homogeneous environments** -- when CA-CFAR fails (clutter edges, multiple targets), motivation for OS-CFAR and GO/SO-CFAR (setting up Phase 5 research)

**Equation budget:** DET-1 through approximately DET-20.

### Document 5: Noise Analysis (05_noise_analysis.md) -- Prefix: NF

Covers PHYS-06.

**Section flow:**
1. **Thermal noise power** -- $P_n = k_B T_0 B_n$, noise temperature, noise bandwidth
2. **Noise figure definition** -- $F = \text{SNR}_\text{in} / \text{SNR}_\text{out}$, relationship to noise temperature $T_e = T_0(F-1)$
3. **Friis cascaded noise figure** -- general M-stage formula
4. **AERIS-10 receive chain stages** -- LNA (ADTR1107), mixer (LT5552), IF amplifier, ADC (AD9484) -- symbolic analysis with placeholder NF/gain values referencing parameter_table.md TBDs
5. **ADC noise contribution** -- quantization noise power $\sigma_q^2 = \Delta^2/12$, effective noise figure of ADC as function of bit depth and full-scale range
6. **CIC filter noise analysis** -- bit growth through CIC stages, processing gain vs quantization noise growth, effective noise contribution
7. **System noise figure budget** -- complete chain from antenna to digital output

**Equation budget:** NF-1 through approximately NF-12.

**TBD handling:** The ADTR1107 LNA noise figure and LT5552 mixer noise figure are TBD in the parameter table. The derivation must be fully symbolic. Include a subsection titled "Numerical Evaluation (Pending Parameter Resolution)" that shows how to substitute values once TBDs are resolved.

### Document 6: Calibration Theory (06_calibration_theory.md) -- Prefix: CAL

Covers PHYS-07.

**Section flow:**
1. **Error model** -- phase error $\delta\phi_n$ and amplitude error $\delta a_n$ per element, effect on array factor
2. **Array pattern with errors** -- $AF_\text{err}(\theta) = \sum (a_n + \delta a_n) e^{j(n\psi + \delta\phi_n)}$
3. **RMS sidelobe level with random errors** -- $\overline{\text{SLL}} \approx (1/N) \sum |\delta a_n / a_n|^2 + |\delta\phi_n|^2$ (Mailloux result)
4. **ADAR1000 phase quantization** -- 2.8 degree step size, deterministic error model (not random), maximum quantization error = 1.4 degrees, beam pointing error bound
5. **ADAR1000 amplitude quantization** -- attenuator resolution, impact on amplitude taper accuracy
6. **Mutual coupling effects** -- coupling matrix $\mathbf{C}$, active element pattern vs isolated element pattern, effect on calibration
7. **Calibration correction** -- measurement-based calibration: inject known signal, measure per-element response, compute correction vector, apply via ADAR1000 phase/gain registers
8. **Residual error analysis** -- post-calibration error bounds given ADAR1000 quantization limits

**Equation budget:** CAL-1 through approximately CAL-12.

**New symbols needed:** $\delta\phi_n$ (phase error), $\delta a_n$ (amplitude error), $a_n$ (nominal amplitude weight), $\mathbf{C}$ (coupling matrix). These must be added to symbol_table.md before use.

## State of the Art

| Aspect | Standard Treatment | Notes |
|--------|--------------------|-------|
| FMCW beat frequency | Full derivation including Doppler term | Mature since 1970s; Richards Ch. 4 is definitive |
| LFM ambiguity function | Closed-form expression well-known | Levanon & Mozeson "Radar Signals" is the reference |
| Phased array beamforming | Array factor with progressive phase shift | Mailloux (3rd ed.) or Balanis "Antenna Theory" |
| CFAR detection | CA-CFAR P_fa formula standard since Finn & Johnson (1968) | Extended to OS-CFAR, GO/SO-CFAR in 1980s-1990s |
| Cascaded noise figure | Friis formula (1944) | Extended to include ADC and digital processing in modern treatments |
| Array calibration | Measurement-based correction standard practice | ADAR1000-specific calibration procedures in ADI application notes |

No "state of the art" changes affect this phase -- the physics is stable and well-established. The derivation approach should follow textbook treatments without attempting novel formulations.

## Symbol Table Additions Required

Before writing physics documents, these symbols must be added to `00_notation/symbol_table.md`:

| Symbol | Definition | Units | Section |
|--------|-----------|-------|---------|
| $k$ | Wavenumber, $k = 2\pi/\lambda$ | rad/m | Antenna and Beamforming |
| $\psi$ | Electrical angle, $\psi = kd\sin\theta + \Delta\phi$ | rad | Antenna and Beamforming |
| $\theta_0$ | Beam steering angle (desired) | rad or deg | Antenna and Beamforming |
| $\theta_{3\text{dB}}$ | Half-power beamwidth | rad or deg | Antenna and Beamforming |
| $w_n$ | Amplitude weight for array element $n$ | -- | Antenna and Beamforming |
| $\alpha$ | CFAR threshold multiplier | -- | Detection and Signal |
| $N_\text{ref}$ | Number of CFAR reference cells (total) | -- | Detection and Signal |
| $N_\text{guard}$ | Number of CFAR guard cells (total) | -- | Detection and Signal |
| $T_e$ | Equivalent noise temperature | K | Detection and Signal |
| $B_n$ | Noise bandwidth | Hz | Detection and Signal |
| $\delta\phi_n$ | Phase error for element $n$ | rad | Antenna and Beamforming |
| $\delta a_n$ | Amplitude error for element $n$ | -- | Antenna and Beamforming |
| $a_n$ | Nominal amplitude weight for element $n$ | -- | Antenna and Beamforming |
| $\tau$ | Round-trip delay, $\tau = 2R/c$ | s | Waveform and Timing |
| $\chi(\tau, \nu)$ | Ambiguity function | -- | Signal Processing |

Note: $w_n$ (element amplitude weight) and $w[n]$ (window function) are distinct. The symbol table already has $w[n]$; $w_n$ should be added with a note clarifying the distinction, or they should be unified as $w_n$ serving both purposes (element weight IS the window function applied to the array).

## TBD Parameters Affecting This Phase

These parameters are marked TBD in parameter_table.md and are needed for numerical evaluation (though derivations remain symbolic):

| Parameter | Symbol | Impact | Mitigation |
|-----------|--------|--------|------------|
| Chirp bandwidth | $B$ | Range resolution $\Delta R = c/2B$, time-bandwidth product $BT_c$, pulse compression gain | Keep symbolic; note TBD in numerical evaluation sections |
| LNA noise figure (Nexus) | $F_\text{LNA}$ | Dominates cascaded system noise figure | Derive Friis chain symbolically; show sensitivity to $F_\text{LNA}$ |
| LNA noise figure (Extended) | $F_\text{LNA}$ | Same | Same |
| Antenna gain (Nexus) | $G$ | Detection range via radar equation | Keep symbolic; use $G$ without numerical substitution |
| Antenna gain (Extended) | $G$ | Same | Same |

**Recommendation:** Where the document needs a numerical worked example to build intuition, use placeholder values clearly labeled: "Using representative values $B = 400$ MHz, $F_\text{LNA} = 3$ dB (to be confirmed against component datasheets)..." This gives readers a concrete sense of magnitude while preserving the TBD status.

## Open Questions

1. **Chirp bandwidth $B$ is TBD**
   - What we know: The ADF4382 synthesizers generate the LO; chirp LUT files exist in FPGA memory; the system operates at 10.5 GHz center frequency
   - What's unclear: The actual sweep range of the chirp (i.e., $B$), which determines range resolution
   - Recommendation: Derive symbolically. If chirp LUT analysis or ADF4382 register dump becomes available, add to parameter_table.md and update numerical examples

2. **Which variant is primary for derivations?**
   - What we know: STATE.md flags this as a blocker. Nexus (3 km) and Extended (20 km) have different transmit power and antenna configurations
   - What's unclear: Whether derivations should default to Nexus parameters or Extended
   - Recommendation: Derive everything symbolically (applies to both). Use variant callout blocks per conventions.md wherever parameters differ. No primary variant is needed if derivations are symbolic.

3. **ADC is 8-bit, not 14-bit**
   - What we know: parameter_table.md resolved this -- AD9484 is 8-bit at 400 MSPS
   - Impact on physics: The 8-bit ADC has significantly less dynamic range than a 14-bit ADC. ADC quantization noise floor is $-6.02 \times 8 - 1.76 = -49.9$ dB below full scale. This limits effective noise figure of the digital chain.
   - Recommendation: The noise analysis document must address 8-bit quantization noise explicitly as a dominant contributor in the digital chain.

4. **Symbol table disambiguation: $w_n$ vs $w[n]$**
   - What we know: $w[n]$ is defined in the symbol table as "window function (discrete)"; beamforming needs element amplitude weights $w_n$
   - What's unclear: Whether to treat these as the same concept (array tapering IS windowing) or keep them distinct
   - Recommendation: Add $w_n$ as "element amplitude weight" in the Antenna and Beamforming section. Note in the beamforming document that applying a window function $w[n]$ to the array is equivalent to amplitude tapering with weights $w_n = w[n]$.

## Sources

### Primary (HIGH confidence)
- Skolnik, M.I. "Introduction to Radar Systems" (4th ed., McGraw-Hill, 2008) -- Radar equation, noise figure, detection theory
- Richards, M.A. "Fundamentals of Radar Signal Processing" (2nd ed., McGraw-Hill, 2014) -- LFM waveforms, matched filter, ambiguity function, CFAR
- Mailloux, R.J. "Phased Array Antenna Handbook" (3rd ed., Artech House, 2017) -- Array factor, calibration, error analysis
- IEEE 686-2024 -- Notation authority (via Phase 1 symbol table)
- Phase 1 deliverables: `00_notation/conventions.md`, `symbol_table.md`, `parameter_table.md` -- Notation and parameter constraints

### Secondary (MEDIUM confidence)
- Mahafza, B.R. "Radar Systems Analysis and Design Using MATLAB" (3rd ed., CRC Press, 2013) -- CFAR derivations, numerical validation patterns
- Levanon, N. and Mozeson, E. "Radar Signals" (Wiley, 2004) -- Ambiguity function theory
- Analog Devices ADAR1000 datasheet -- Phase quantization (2.8 degree steps), gain control specifications
- Analog Devices ADTR1107 datasheet -- Integrated T/R module specifications (NF TBD from datasheet)
- [Infineon FMCW Radar DSP Handout](https://www.infineon.com/dgdl/Infineon-FMCW_RADAR_Digital_Signal_Processing_Handout-Training-v01_00-EN.pdf) -- Pipeline structure reference

### Tertiary (LOW confidence)
- None -- all physics in this phase is well-established textbook material

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- GitHub MathJax confirmed working in Phase 1; textbook references are authoritative and stable
- Architecture: HIGH -- Document structure follows standard radar textbook organization (Skolnik chapter order)
- Derivation correctness: HIGH -- All formulas are well-known, published in multiple textbooks, cross-verifiable
- Pitfalls: HIGH -- Range-Doppler coupling omission and dB/linear confusion are well-documented failure modes in FMCW radar documentation
- TBD parameters: MEDIUM -- Several key parameters ($B$, $F_\text{LNA}$, $G$) remain unresolved; symbolic derivations mitigate this

**Research date:** 2026-03-13
**Valid until:** Indefinitely -- FMCW radar physics is stable; notation conventions from Phase 1 are locked
