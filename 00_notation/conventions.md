# AERIS-10 Documentation Conventions

This file is the **single source of truth** for how all AERIS-10 project documents format equations, reference other documents, and present mathematical content. Every author contributing to this documentation set must follow these conventions. If a rule is not covered here, propose an addition before deviating.

For canonical symbol definitions, see [`symbol_table.md`](symbol_table.md). For numerical parameter values, see [`parameter_table.md`](parameter_table.md).

---

## 1. Equation Numbering Convention

All equations are numbered using a **document-prefix scheme** to guarantee uniqueness across the entire project. Each document is assigned a unique prefix; equations within that document are numbered sequentially from 1.

### Prefix Assignments

| Document Topic | Prefix | Example Tags |
|----------------|--------|-------------|
| FMCW theory | `FMCW` | Eq. (FMCW-1), Eq. (FMCW-2) |
| LFM waveform model | `LFM` | Eq. (LFM-1), Eq. (LFM-2) |
| Beamforming & array factor | `BF` | Eq. (BF-1), Eq. (BF-2) |
| Detection theory (CFAR, Neyman-Pearson) | `DET` | Eq. (DET-1), Eq. (DET-2) |
| Noise figure & calibration | `NF` | Eq. (NF-1), Eq. (NF-2) |
| Calibration procedures | `CAL` | Eq. (CAL-1), Eq. (CAL-2) |
| Hardware documentation | `HW` | Eq. (HW-1), Eq. (HW-RF-1) for subsections |
| Software documentation | `SW` | Eq. (SW-1), Eq. (SW-2) |

### Syntax

Use the MathJax `\tag{}` command inside a display-math block:

```markdown
$$
R = \frac{c \cdot f_b}{2\mu} \tag{FMCW-1}
$$
```

This renders as:

$$
R = \frac{c \cdot f_b}{2\mu} \tag{FMCW-1}
$$

### Rules

- Every equation that is **referenced anywhere** in the project MUST have a `\tag{}`.
- Unreferenced display equations MAY omit tags.
- Tags must be unique across the entire project. The prefix scheme guarantees this.
- Number sequentially within each document: `FMCW-1`, `FMCW-2`, `FMCW-3`, etc.
- If a document grows subsections that need independent numbering, use a sub-prefix: `HW-RF-1`, `HW-PWR-1`.

---

## 2. Cross-Reference Format

GitHub's native MathJax renderer does **NOT** support `\ref{}`, `\eqref{}`, or `\label{}`. All cross-references use plain-text conventions.

### Within the Same Document

Use plain text with the tag in parentheses:

```markdown
Substituting the chirp rate into Eq. (FMCW-1), we obtain...
```

### Cross-Document References

Include the file path as a Markdown link with a heading anchor for deep linking:

```markdown
Using the range equation Eq. (FMCW-1) in [`physics/01_fmcw_theory.md`](../physics/01_fmcw_theory.md#range-equation)...
```

### Symbol References

When introducing a symbol for the first time in a document, link to the symbol table:

```markdown
The transmitted power $P_t$ (defined in the [Symbol Table](../00_notation/symbol_table.md#detection-and-signal)) is...
```

### Parameter Value References

Never embed numerical values inline. Reference the parameter table:

```markdown
Using the system parameters from the [Parameter Table](../00_notation/parameter_table.md#waveform-and-timing)...
```

---

## 3. MathJax Usage Rules for GitHub

### Supported (use these)

| Feature | Syntax | Example |
|---------|--------|---------|
| Inline math | `$...$` | $f_c = 10.5~\text{GHz}$ |
| Display math | `$$...$$` | Block equations |
| Manual tags | `\tag{LABEL}` | `\tag{FMCW-1}` |
| Text in math | `\text{}` | `\text{SNR}` |
| Fractions | `\frac{}{}` | `\frac{c}{2B}` |
| Auto-sizing delimiters | `\left( \right)` | `\left(\frac{a}{b}\right)` |
| Standard LaTeX math | Greek, subscripts, superscripts, etc. | $\lambda$, $f_{r,1}$, $R^4$ |
| Aligned multi-line | `\begin{aligned}...\end{aligned}` inside `$$` | See below |

### NOT Supported (never use these)

| Feature | Why Not |
|---------|---------|
| `\ref{}` | Not supported -- silently fails or renders literal text |
| `\eqref{}` | Not supported -- same as `\ref{}` |
| `\label{}` | Not supported -- GitHub does not track labels |
| Automatic numbering (`tags: 'ams'`) | Requires MathJax config that GitHub does not expose |
| `\begin{align}` with auto-numbering | Numbers do not render; use `aligned` inside `$$` instead |
| `\newcommand` | Not supported in GitHub's renderer |
| `\DeclareMathOperator` | Not supported -- use `\operatorname{}` instead |

### Unit Formatting Standard

Units are always set in upright text with a non-breaking space (tilde) separating the number from the unit:

```markdown
$f_c = 10.5~\text{GHz}$
$T_c = 30~\mu\text{s}$
$P_t = 1~\text{W}$
```

### Multi-Line Equations

Use `\begin{aligned}...\end{aligned}` inside a `$$` block with a single `\tag{}`:

```markdown
$$
\begin{aligned}
R_\text{max} &= \frac{c \cdot T_r}{2} \\
&= \frac{c}{2 f_r}
\end{aligned}
\tag{FMCW-5}
$$
```

---

## 4. Variant Callout Block

The AERIS-10 system has two variants: **Nexus** (AERIS-10N) and **Extended** (AERIS-10X). Whenever a derivation or specification differs between variants, use the following standardized admonition block:

```markdown
> **Variant Note:**
> | | Nexus | Extended |
> |--|-------|----------|
> | $P_t$ per element | 1 W | 10 W |
> | Antenna gain $G$ | ~20 dBi (patch) | ~30 dBi (waveguide) |
```

### Rules

- Place the variant callout immediately after the equation or paragraph where the difference matters.
- Include only the parameters that differ -- do not repeat shared values.
- Values in the callout block should match the [Parameter Table](parameter_table.md) exactly. If they diverge, the Parameter Table is authoritative.

---

## 5. Anti-Patterns

The following practices are **prohibited** across all project documents.

### 5.1 Never Inline Parameter Values in Derivations

Keep derivations symbolic. Numerical values belong only in `parameter_table.md`.

- **Wrong:** "The range resolution is $\Delta R = \frac{c}{2B} = \frac{3 \times 10^8}{2 \times 400 \times 10^6} = 0.375~\text{m}$"
- **Right:** "The range resolution is $\Delta R = \frac{c}{2B}$" with a reference to the parameter table for numerical evaluation.

### 5.2 Never Define the Same Parameter in Two Places

If a parameter value appears in two documents, one must link to the other. The parameter table is the single source of truth.

### 5.3 Never Use Different Symbols for the Same Concept

The [Symbol Table](symbol_table.md) is authoritative. Do not use $\tau$ for pulse width in one document and $T_c$ in another.

### 5.4 Never Use Raw Codebase Variable Names Without the Standard Symbol

When referencing firmware or FPGA variables, always provide the standard symbol alongside:

- **Wrong:** "The firmware sets `T1` to 30 us"
- **Right:** "The firmware sets the long chirp duration $T_{c,1}$ (`T1` in `main.cpp`) to $30~\mu\text{s}$"

### 5.5 Never Use Unsupported MathJax Features

See Section 3. Using `\ref{}`, `\eqref{}`, `\label{}`, or automatic numbering will silently break on GitHub.

---

## 6. Document Template

Every project document should follow this structure:

```markdown
# [Document Title]

**Purpose:** [One sentence describing what this document covers]

**Prerequisites:** Familiarity with:
- [Symbol Table](../00_notation/symbol_table.md) -- all symbols used herein
- [Parameter Table](../00_notation/parameter_table.md) -- numerical values for both variants
- [Conventions](../00_notation/conventions.md) -- equation formatting rules

---

## 1. [First Section]

[Derivation or content using \tag{PREFIX-N} for all referenced equations]

> **Variant Note:**
> | | Nexus | Extended |
> |--|-------|----------|
> | [parameter] | [value] | [value] |

## 2. [Second Section]

[Continue with sequential tags: PREFIX-N+1, PREFIX-N+2, ...]

---

## References

- [Symbol Table](../00_notation/symbol_table.md)
- [Parameter Table](../00_notation/parameter_table.md)
- [Any external references: IEEE standards, textbooks, datasheets]
```

### Template Rules

- The **Prerequisites** section must always link to the symbol table, parameter table, and this conventions file.
- Sections are numbered with Markdown headings (`## 1.`, `## 2.`, etc.).
- A **References** section appears at the end of every document.
- The variant callout block is used wherever Nexus and Extended values differ.
- All equations follow the document-prefix `\tag{}` scheme defined in Section 1 of this file.
