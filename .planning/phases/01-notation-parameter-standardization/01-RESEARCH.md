# Phase 1: Notation & Parameter Standardization - Research

**Researched:** 2026-03-13
**Domain:** Radar notation conventions, system parameter cataloging, equation formatting for GitHub-native Markdown
**Confidence:** HIGH

## Summary

Phase 1 establishes three foundational deliverables before any physics derivations begin: a project-wide symbol table (NOTN-01), a master system parameter table for both AERIS-10 variants (NOTN-02), and an equation numbering/cross-reference convention (NOTN-03). This phase is a prerequisite for all subsequent phases -- inconsistent notation discovered mid-project requires expensive retroactive corrections across every downstream document.

The symbol table must reconcile three independent naming worlds that currently exist in the codebase: the firmware world (`T1`, `PRI1`, `m_max`, `n_max`, `Guard`), the FPGA world (`IF_FREQ`, `FS`, `ADC_WIDTH`, `DOPPLER_FFT_SIZE`, `CHIRPS_PER_FRAME`), and the Python GUI world (`system_frequency`, `chirp_duration_1`, `max_distance`). None of these align with standard radar notation (Skolnik/Richards/IEEE 686). The symbol table must define the canonical mathematical symbol for each concept, then map it to every codebase identifier where it appears. The master parameter table must capture actual numerical values for both AERIS-10 Nexus (3 km, patch array, ~1 W per element) and Extended (20 km, slotted waveguide, 10 W GaN per element) variants, extracted from `main.cpp`, `GUI_V6.py`, FPGA Verilog parameters, and the README.

For equation formatting, GitHub natively renders MathJax via `$...$` (inline) and `$$...$$` (display) delimiters in `.md` files. The `\tag{}` command is confirmed working for manual equation numbering. However, `\ref{}` and `\eqref{}` cross-references do NOT work on GitHub's native renderer because equation numbering is not enabled by default and GitHub does not support automatic equation numbering configuration. The convention must therefore use manual `\tag{}` labels with a human-readable numbering scheme and plain-text cross-references (e.g., "see Eq. (2.3)") rather than LaTeX-style automatic referencing.

**Primary recommendation:** Create three Markdown files -- `00_notation/symbol_table.md`, `00_notation/parameter_table.md`, and `00_notation/conventions.md` -- as the first committed deliverables, referenced by every subsequent document.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| NOTN-01 | Project-wide symbol table following IEEE 686-2024 notation conventions | Standard radar notation mapped below; codebase audit identifies all symbols needing standardization; IEEE 686-2024 confirmed as authority for definitions |
| NOTN-02 | Master system parameter table with canonical values for both AERIS-10 variants (Nexus/Extended) | All parameter values extracted from main.cpp, GUI_V6.py, FPGA Verilog, and README; variant differences cataloged |
| NOTN-03 | Equation numbering convention and cross-reference format established | GitHub MathJax capabilities and limitations documented; manual \tag{} scheme designed; cross-reference convention specified |
</phase_requirements>

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| GitHub Markdown + MathJax | Native (MathJax 3.x) | All documentation files | Zero build step; renders in browser; team already uses GitHub |
| `\tag{}` macro | MathJax built-in | Manual equation numbering | Only reliable numbering method on GitHub's renderer |
| Markdown tables | Native | Parameter tables, symbol tables | GitHub renders natively; diff-friendly in PRs |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| markdownlint | Consistency enforcement | CI or pre-commit check on all `.md` files |
| VS Code + Markdown Preview Enhanced | Local preview with MathJax | Authoring equations before push |

### What NOT to Use

| Instead of | Why Not |
|------------|---------|
| `\ref{}` / `\eqref{}` in GitHub Markdown | Not supported by GitHub's native MathJax renderer -- silently fails |
| Automatic equation numbering (`tags: 'ams'`) | Requires MathJax config that GitHub does not expose |
| LaTeX-compiled PDFs | Breaks docs-as-code workflow; not diffable in PRs |
| Image-rendered equations (codecogs.com) | Dark mode breakage; not searchable; URL-dependent |

## Architecture Patterns

### Recommended Documentation Structure

```
00_notation/
  symbol_table.md          # NOTN-01: Project-wide symbol table
  parameter_table.md       # NOTN-02: Master system parameter table (both variants)
  conventions.md           # NOTN-03: Equation numbering, cross-ref format, document templates
```

All subsequent documentation phases (`physics/`, `hardware/`, `software/`, `research/`) will reference these files as the single source of truth for notation and parameters.

### Pattern 1: Symbol Table Layout

**What:** A three-column table mapping mathematical symbol to definition to units, organized by domain (waveform, antenna, signal processing, detection).

**When to use:** Every document in the project references this table for consistent notation.

**Example:**

```markdown
## Waveform Parameters

| Symbol | Definition | Units | IEEE 686 Ref |
|--------|-----------|-------|--------------|
| $f_c$ | Center (carrier) frequency | Hz | carrier frequency |
| $B$ | Chirp bandwidth (sweep range) | Hz | bandwidth |
| $T_c$ | Chirp duration (pulse width) | s | pulse duration |
| $\mu$ | Chirp rate (sweep slope), $\mu = B / T_c$ | Hz/s | chirp rate |
| $f_b$ | Beat frequency (IF after dechirp) | Hz | beat frequency |
| $f_r$ | Pulse repetition frequency (PRF) | Hz | pulse repetition frequency |
| $T_r$ | Pulse repetition interval (PRI), $T_r = 1/f_r$ | s | pulse repetition interval |
```

### Pattern 2: Parameter Table with Variant Columns

**What:** A table with one row per parameter and separate columns for Nexus and Extended values, plus a column mapping to the codebase variable name.

**Example:**

```markdown
| Parameter | Symbol | Nexus (AERIS-10N) | Extended (AERIS-10X) | Firmware Variable | FPGA Parameter |
|-----------|--------|-------------------|----------------------|-------------------|----------------|
| Center frequency | $f_c$ | 10.5 GHz | 10.5 GHz | `system_frequency` (GUI) | -- |
| Long chirp duration | $T_{c,1}$ | 30 us | 30 us | `T1` (main.cpp) | `USE_LONG_CHIRP` |
| Short chirp duration | $T_{c,2}$ | 0.5 us | 0.5 us | `T2` (main.cpp) | -- |
| PRF (long chirp) | $f_{r,1}$ | 5.988 kHz | 5.988 kHz | `PRI1=167us` (main.cpp) | -- |
| Chirps per position | $M$ | 32 | 32 | `m_max` (main.cpp) | `CHIRPS_PER_FRAME` |
| Beam positions | $N_\text{el}$ | 31 | 31 | `n_max` (main.cpp) | -- |
| Output power per element | $P_t$ | ~1 W (ADTR1107) | 10 W (QPA2962 GaN) | -- | -- |
| Antenna type | -- | 8x16 patch array | 32x16 slotted waveguide | -- | -- |
```

### Pattern 3: Equation Numbering Convention

**What:** Manual `\tag{}` numbering with section-based scheme: `(Section.Number)`.

**Example:**

```markdown
The range to a target is derived from the beat frequency:

$$
R = \frac{c \cdot f_b}{2\mu} \tag{2.1}
$$

where $\mu = B/T_c$ is the chirp rate defined in the symbol table.

Substituting the chirp rate into Eq. (2.1), we obtain...
```

**Numbering scheme:**
- Section 1: Waveform fundamentals -- Eq. (1.1), (1.2), ...
- Section 2: Range and velocity -- Eq. (2.1), (2.2), ...
- Section 3: Beamforming -- Eq. (3.1), (3.2), ...
- Section 4: Detection theory -- Eq. (4.1), (4.2), ...
- Cross-document references use full path: "Eq. (2.3) in `physics/01_fmcw_theory.md`"

### Pattern 4: Variant Callout Block

**What:** A standardized admonition block used whenever Nexus and Extended values differ.

**Example:**

```markdown
> **Variant Note:**
> | | Nexus | Extended |
> |--|-------|----------|
> | $P_t$ per element | 1 W | 10 W |
> | Antenna gain $G$ | ~20 dBi (patch) | ~30 dBi (waveguide) |
> | Max detection range | 3 km | 20 km |
```

### Anti-Patterns to Avoid

- **Inline parameter values in derivations:** Never write "$f_c = 10.5$ GHz" in a physics derivation. Keep derivations symbolic; actual numbers live only in `parameter_table.md` and are referenced.
- **Duplicate parameter definitions:** If a parameter appears in two documents, one must link to the other. Never define the same value in two places.
- **Mixed notation across documents:** Never use $B$ for bandwidth in one document and $\Delta f$ in another. The symbol table is authoritative.
- **Unlabeled equations that are later referenced:** If an equation will be referenced anywhere, it must have a `\tag{}`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Equation numbering | Custom HTML/JS | MathJax `\tag{}` | Only method that works in GitHub's renderer |
| Parameter consistency | Manual copy-paste | Single `parameter_table.md` with links | Eliminates drift between documents |
| Symbol definitions | Per-document notation sections | Single `symbol_table.md` | One source of truth across 15+ documents |
| Unit formatting | Ad-hoc text | Consistent pattern: `$f_c = 10.5~\text{GHz}$` | MathJax `\text{}` renders units upright; tilde provides non-breaking space |

## Common Pitfalls

### Pitfall 1: Notation Drift Across Documents
**What goes wrong:** Physics docs use $\tau$ for pulse width, hardware docs use $T$, software docs use `pulse_duration` -- all for the same concept.
**Why it happens:** Different authors, different references (Skolnik uses $\tau$, Richards uses $T$).
**How to avoid:** Symbol table created FIRST, before any derivation. One symbol per concept, no exceptions.
**Warning signs:** PR review catches different symbols for same quantity.

### Pitfall 2: GitHub MathJax Silent Failures
**What goes wrong:** `\eqref{}`, `\label{}`, `\ref{}`, `\begin{align}` with numbering -- all silently render incorrectly or not at all on GitHub.
**Why it happens:** GitHub's MathJax renderer is a subset. No equation numbering config is exposed.
**How to avoid:** Use ONLY `\tag{}` for numbering. Test every equation pattern on GitHub before committing to it.
**Warning signs:** Equations look correct in VS Code preview but broken on GitHub web view.

### Pitfall 3: Inconsistent Codebase-to-Symbol Mapping
**What goes wrong:** The parameter table maps `T1` to $T_{c,1}$ but a later document references the firmware variable without translating to the standard symbol.
**Why it happens:** Convenience -- authors copy variable names from code instead of looking up the standard symbol.
**How to avoid:** Parameter table includes a "Firmware Variable" column. Every document that mentions a codebase value must also show the standard symbol.
**Warning signs:** Grep for raw variable names (`T1`, `PRI1`, `m_max`) appearing in physics/hardware docs without the corresponding symbol.

### Pitfall 4: Missing Parameters for One Variant
**What goes wrong:** Parameter table is complete for Nexus but Extended values are "TBD" -- downstream documents silently assume Nexus values apply to Extended.
**Why it happens:** Nexus data is more accessible in the codebase; Extended (GaN) parameters require datasheet lookup.
**How to avoid:** Both variant columns must be filled before Phase 1 is declared complete. Mark genuinely unknown values as "TBD -- required before Phase 2" with explicit flags.
**Warning signs:** Any "TBD" in the parameter table at phase completion.

### Pitfall 5: Equation Tags Not Unique Across Documents
**What goes wrong:** `physics/01_fmcw_theory.md` and `physics/02_signal_model.md` both have an Eq. (1.1).
**Why it happens:** Each document starts numbering from (1.1).
**How to avoid:** Assign section number ranges per document: FMCW theory = Section 1-2, Signal model = Section 3-4, etc. OR prefix with document abbreviation: Eq. (FMCW-1), Eq. (SIG-1). The convention must be decided in `conventions.md`.

## Code Examples

### MathJax Display Equation with Tag (GitHub-compatible)

```markdown
$$
P_r = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4 L} \tag{1.1}
$$
```

Renders as the radar range equation with label "(1.1)" on the right.

### MathJax Inline Symbol Reference

```markdown
The transmitted power $P_t$ (see [Symbol Table](../00_notation/symbol_table.md#transmitter-parameters))
is amplified by the ADTR1107 front-end IC.
```

### Variant-Aware Parameter Reference

```markdown
Using the system parameters from the [Master Parameter Table](../00_notation/parameter_table.md):

$$
R_\text{max} = \left(\frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 S_\text{min} L}\right)^{1/4} \tag{2.5}
$$

> **Variant Note:** For AERIS-10N, $P_t = 1~\text{W}$ per element; for AERIS-10X, $P_t = 10~\text{W}$ (QPA2962 GaN).
```

### Cross-Document Equation Reference (Plain Text)

```markdown
Substituting the beat frequency expression from Eq. (1.3) in
[`physics/01_fmcw_theory.md`](../physics/01_fmcw_theory.md#range-equation)
into the range resolution formula...
```

Note: This uses Markdown links with heading anchors, NOT MathJax `\ref{}`.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Image-rendered LaTeX (codecogs) | GitHub-native MathJax `$...$` | May 2022 | No external dependencies; dark mode compatible |
| `\eqref{}` cross-references | Manual `\tag{}` + plain-text "Eq. (X.Y)" | GitHub MathJax limitation (ongoing) | Must design numbering convention up front |
| Per-document notation sections | Single project-wide symbol table | Best practice for multi-document sets | Eliminates notation drift |

## Codebase Parameter Audit

### Parameters Extracted from Firmware (`main.cpp`)

| Variable | Value | Meaning | Needs Symbol |
|----------|-------|---------|--------------|
| `T1` | 30.0 us | Long chirp duration | $T_{c,1}$ |
| `T2` | 0.5 us | Short chirp duration | $T_{c,2}$ |
| `PRI1` | 167.0 us | Long chirp PRI | $T_{r,1}$ |
| `PRI2` | 175.0 us | Short chirp PRI | $T_{r,2}$ |
| `Guard` | 175.4 us | Guard time between sequences | $T_\text{guard}$ |
| `m_max` | 32 | Chirps per beam position | $M$ |
| `n_max` | 31 | Beam elevation positions | $N_\text{el}$ |
| `y_max` | 50 | Azimuth positions per revolution | $N_\text{az}$ |
| `IF_freq` | 120 MHz | IF frequency | $f_\text{IF}$ |
| `phase_differences[31]` | -160 to +160 deg | Inter-element phase shifts per beam | $\Delta\phi_n$ |
| `Stepper_steps` | 200 | Steps per revolution | -- (mechanical) |
| `sampleRate` | 370 Hz | DAC sample rate for PA control | -- (housekeeping) |
| `wavelength` (line 1133) | 0.02857 m | Wavelength at 10.5 GHz | $\lambda$ |
| `element_spacing` (line 1134) | $\lambda/2$ | Array element spacing | $d$ |
| `Mag_Declination` | -0.61 deg | Magnetic declination | -- (GPS/nav) |

### Parameters Extracted from FPGA Verilog

| Parameter | File | Value | Meaning | Needs Symbol |
|-----------|------|-------|---------|--------------|
| `IF_FREQ` | ddc_400m.v | 120 MHz | IF frequency for DDC | $f_\text{IF}$ |
| `FS` | ddc_400m.v | 400 MHz | ADC sample rate | $f_s$ |
| `ADC_WIDTH` | ddc_400m.v | 8 bits | ADC data width | -- (implementation) |
| `NCO_WIDTH` | ddc_400m.v | 16 bits | NCO phase accumulator width | -- (implementation) |
| `STAGES` | cic_decimator.v | 5 | CIC filter stages | $N_\text{CIC}$ |
| `DECIMATION` | cic_decimator.v | 4 | CIC decimation factor | $D_\text{CIC}$ |
| `BUFFER_SIZE` | matched_filter.v | 1024 | FFT/matched filter buffer | $N_\text{FFT}$ |
| `LONG_CHIRP_SAMPLES` | matched_filter.v | 3000 | Long chirp reference length | -- |
| `SHORT_CHIRP_SAMPLES` | matched_filter.v | 50 | Short chirp reference length | -- |
| `DOPPLER_FFT_SIZE` | doppler_processor.v | 32 | Doppler FFT size | $N_\text{Doppler}$ |
| `RANGE_BINS` | doppler_processor.v | 64 | Range bins | $N_R$ |
| `CHIRPS_PER_FRAME` | doppler_processor.v | 32 | Chirps per CPI | $M$ |
| `USE_LONG_CHIRP` | radar_system_top.v | 1 | Chirp mode select | -- (config) |
| `DOPPLER_ENABLE` | radar_system_top.v | 1 | Doppler processing enable | -- (config) |

### Parameters Extracted from Python GUI (`GUI_V6.py`)

| Variable | Value | Meaning | Needs Symbol |
|----------|-------|---------|--------------|
| `system_frequency` | 10e9 (NOTE: says 10.5 GHz in comment) | Center frequency | $f_c$ |
| `chirp_duration_1` | 30e-6 | Long chirp duration | $T_{c,1}$ |
| `chirp_duration_2` | 0.5e-6 | Short chirp duration | $T_{c,2}$ |
| `chirps_per_position` | 32 | Chirps per beam position | $M$ |
| `freq_min` | 10e6 | Minimum IF frequency | -- |
| `freq_max` | 30e6 | Maximum IF frequency | -- |
| `prf1` | 1000 Hz | PRF long chirp | $f_{r,1}$ |
| `prf2` | 2000 Hz | PRF short chirp | $f_{r,2}$ |
| `max_distance` | 50000 m | Max display range | $R_\text{max}$ |

### Inconsistencies Found

1. **Center frequency:** README says 10.5 GHz, GUI `system_frequency` defaults to 10e9 (10.0 GHz), firmware `wavelength` constant uses 0.02857 m which implies 10.5 GHz. The parameter table must resolve this.
2. **PRF values:** Firmware defines `PRI1 = 167 us` (implying PRF = 5988 Hz), but GUI defines `prf1 = 1000 Hz`. These may refer to different things (FPGA chirp timing vs. GUI display rate). Must be clarified.
3. **ADC bits:** FPGA `ADC_WIDTH = 8` in ddc_400m.v, but STACK.md says "AD9484 14-bit ADC." The AD9484 is 8-bit at 500 MSPS -- must verify actual part and resolution.
4. **Beam steering range:** README says "+/-45 degrees" but `phase_differences[31]` array goes from -160 to +160 degrees inter-element phase, which maps to steering angles via $\theta = \arcsin(\Delta\phi \cdot \lambda / (2\pi d))$.

## Standard Radar Notation Reference

The following symbols follow conventions from Skolnik ("Introduction to Radar Systems"), Richards ("Fundamentals of Radar Signal Processing"), and IEEE 686-2024 definitions:

### Waveform & Timing
| Symbol | Meaning | Common Alternatives |
|--------|---------|--------------------|
| $f_c$ | Carrier/center frequency | $f_0$ |
| $B$ | Chirp bandwidth | $\Delta f$, $BW$ |
| $T_c$ | Chirp duration (pulse width) | $\tau$, $T_p$, $T_\text{chirp}$ |
| $\mu$ | Chirp rate (slope) | $k$, $S$, $\gamma$ |
| $f_r$ | Pulse repetition frequency | PRF |
| $T_r$ | Pulse repetition interval | PRI, $T_\text{PRI}$ |
| $M$ | Number of pulses per CPI | $N_p$, $K$ |

### Range & Velocity
| Symbol | Meaning | Common Alternatives |
|--------|---------|--------------------|
| $R$ | Range to target | $r$ |
| $f_b$ | Beat frequency | $f_\text{IF}$, $f_\text{beat}$ |
| $v$ | Target radial velocity | $\dot{R}$ |
| $f_d$ | Doppler frequency | $f_D$ |
| $\Delta R$ | Range resolution | $\delta R$, $R_\text{res}$ |
| $\Delta v$ | Velocity resolution | $\delta v$ |

### Antenna & Beamforming
| Symbol | Meaning | Common Alternatives |
|--------|---------|--------------------|
| $N$ | Number of array elements | $N_e$ |
| $d$ | Inter-element spacing | $\Delta x$ |
| $\theta$ | Beam steering angle | $\theta_0$ (scan), $\theta_s$ |
| $\Delta\phi$ | Phase shift per element | $\psi$ |
| $G$ | Antenna gain | $G_t$ (transmit), $G_r$ (receive) |
| $AF(\theta)$ | Array factor | -- |

### Detection & Signal
| Symbol | Meaning | Common Alternatives |
|--------|---------|--------------------|
| $P_t$ | Transmit power | $P_\text{tx}$ |
| $P_r$ | Received power | $P_\text{rx}$ |
| $\sigma$ | Radar cross section | RCS |
| $\lambda$ | Wavelength | -- |
| $L$ | System losses | $L_s$ |
| $F$ | Noise figure | NF |
| $T_0$ | Reference temperature (290 K) | $T_\text{ref}$ |
| $k_B$ | Boltzmann constant | $k$ |
| $P_{fa}$ | Probability of false alarm | $P_\text{FA}$ |
| $P_d$ | Probability of detection | $P_D$ |
| $\text{SNR}$ | Signal-to-noise ratio | -- |

### Signal Processing
| Symbol | Meaning | Common Alternatives |
|--------|---------|--------------------|
| $f_s$ | Sampling frequency | $F_s$ |
| $N_\text{FFT}$ | FFT size | $N$ |
| $D$ | Decimation factor | $R$ (overloaded with range) |
| $w[n]$ | Window function | $h[n]$ |

## Open Questions

1. **Center frequency: 10.0 GHz or 10.5 GHz?**
   - What we know: README and firmware wavelength constant say 10.5 GHz; GUI defaults to 10.0 GHz.
   - What's unclear: Which is the actual operating frequency.
   - Recommendation: Use 10.5 GHz as canonical (matches README, wavelength constant, and badge). Flag GUI default as potentially outdated.

2. **PRF discrepancy between firmware and GUI**
   - What we know: `PRI1 = 167 us` in firmware (PRF = 5988 Hz); `prf1 = 1000 Hz` in GUI.
   - What's unclear: Whether these refer to the same thing or different timing levels.
   - Recommendation: Document both in parameter table with clear annotations. Likely `PRI1` is the chirp-level interval and `prf1` is a display/processing rate. Must be verified.

3. **AD9484 actual bit width**
   - What we know: FPGA uses 8-bit data path; datasheet says AD9484 is 8-bit 500 MSPS.
   - What's unclear: STACK.md claims "14-bit" which conflicts.
   - Recommendation: Verify against actual datasheet. AD9484 is an 8-bit ADC. The "14-bit" may be a confusion with a different ADC in the design or a planned upgrade.

4. **Extended variant antenna gain and specific power specs**
   - What we know: QPA2962 GaN at 10 W; 32x16 slotted waveguide array.
   - What's unclear: Exact antenna gain, noise figure for Extended variant front-end.
   - Recommendation: Mark as "TBD -- datasheet lookup" in parameter table if not available from codebase. Do not block Phase 1 completion but flag for Phase 2.

## Sources

### Primary (HIGH confidence)
- AERIS-10 codebase direct analysis: `main.cpp` (lines 178-244), `GUI_V6.py` (lines 70-87), `radar_system_top.v` (lines 122-124), `ddc_400m.v` (lines 33-40), `doppler_processor.v` (lines 4-8), `matched_filter_multi_segment.v` (lines 42-53), `cic_decimator_4x_enhanced.v` (lines 14-16) -- extracted all parameter values
- [GitHub Writing Mathematical Expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions) -- confirmed `$...$`, `$$...$$`, and ` ```math ` syntax support
- [IEEE 686-2024 Standard for Radar Definitions](https://ieeexplore.ieee.org/document/10815038) -- notation authority (definitions, not full symbol table accessible without purchase)
- AERIS-10 README.md -- variant specifications, system architecture, component list

### Secondary (MEDIUM confidence)
- [MathJax Automatic Equation Numbering Documentation](https://docs.mathjax.org/en/latest/input/tex/eqnumbers.html) -- confirms `\tag{}`, `\label{}`, `\ref{}` behavior in MathJax (but GitHub does not expose config)
- [Radartutorial.eu - Radar Range Equation](https://www.radartutorial.eu/01.basics/The%20Radar%20Range%20Equation.en.html) -- standard radar notation reference
- [TI Introduction to mmWave Sensing: FMCW Radars](https://www.ti.com/content/dam/videos/external-videos/ko-kr/2/3816841626001/5415203482001.mp4/subassets/mmwaveSensing-FMCW-offlineviewing_0.pdf) -- FMCW notation conventions
- Project research summary (`.planning/research/SUMMARY.md`) -- confirmed `\tag{}` support, toolchain decisions

### Tertiary (LOW confidence)
- IEEE 686-2024 specific symbol table -- standard purchased but full symbol list not available from web search; notation recommendations above are based on widely-adopted Skolnik/Richards conventions that IEEE 686 aligns with

## Metadata

**Confidence breakdown:**
- Standard stack (MathJax/GitHub): HIGH -- verified against official GitHub docs
- Notation conventions: HIGH -- standard radar notation from established textbooks; IEEE 686 aligns
- Codebase parameter audit: HIGH -- extracted directly from source files
- GitHub MathJax limitations: HIGH -- confirmed via official docs and community testing
- Variant-specific parameters: MEDIUM -- Nexus values well-documented in code; Extended values partially from README only

**Research date:** 2026-03-13
**Valid until:** Indefinite for notation conventions; 90 days for MathJax/GitHub rendering behavior
