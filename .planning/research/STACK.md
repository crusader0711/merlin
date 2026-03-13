# Stack Research

**Domain:** Engineering-grade radar system documentation with physics derivations and improvement research surveys
**Researched:** 2026-03-13
**Confidence:** HIGH (documentation tooling), MEDIUM (notation conventions), HIGH (reference management)

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| GitHub Flavored Markdown + LaTeX math | Native (MathJax) | Primary document format for all documentation | The AERIS-10 codebase already lives in a Git repository. GitHub natively renders `$...$` inline math and `$$...$$` block math using MathJax since May 2022. No external tooling required — equations render in the browser, in PRs, and in issue discussions. Engineering team reads docs where they review code. |
| draw.io (diagrams.net) | Current (v24+) | System architecture diagrams, signal flow diagrams, hardware block diagrams | Free, browser-based, exports clean SVG files that embed directly into Markdown. Stores `.drawio` XML in the repo — version-controllable. Superior to Mermaid for non-flow-chart diagrams (RF block diagrams, hardware interconnects, beamforming geometry). Files render as images in GitHub when exported to SVG. |
| Mermaid | v11+ (GitHub-native) | Flowcharts, sequence diagrams, state machines | GitHub renders Mermaid natively in Markdown (no plugin required). Use for software flow: FPGA pipeline stages, STM32 state machines, GUI data flow. Do NOT use for RF/hardware block diagrams — Mermaid's node-link model is wrong for that. |
| WaveDrom | v3+ | Digital timing diagrams for FPGA/microcontroller signals | JSON-based timing diagram tool specifically designed for digital hardware documentation. Renders signal waveforms (clock, SPI, I2C, DDC pipeline timing). The standard tool in FPGA and IC documentation. Embeds as SVG. |
| Zotero | v7 (current) | Reference management for improvement research surveys | Free, open-source. Exports to BibTeX which can be converted to inline citations. Supports IEEE citation style natively (one of 9000+ CSL styles). Browser connector captures papers from IEEE Xplore, arXiv, ResearchGate in one click. Group libraries support team collaboration on the reference database. |

### Supporting Libraries / Tools

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| VSCode + Markdown Preview Enhanced | Current | Local editing with live math preview | Primary editing environment. The "Markdown Preview Enhanced" extension renders MathJax/KaTeX math locally before pushing to GitHub — eliminates surprises. Also previews Mermaid and WaveDrom. |
| markdownlint | v0.37+ | Markdown linting and consistency enforcement | Enforce consistent heading structure, link syntax, code block formatting across all docs. Run as pre-commit hook or CI step. Critical when multiple contributors write documentation. |
| KiCad | v8 (current) | PCB schematic export for hardware documentation | The AERIS-10 hardware documentation needs schematic views of RF front-end, FPGA, STM32 boards. KiCad exports clean SVG schematics. If existing design files exist in KiCad format, this is the tool to generate documentation-quality images. |
| Python + matplotlib | 3.10+ / 3.8+ | Signal model plots and physics illustration | The existing codebase already uses Python + matplotlib. Generate FMCW chirp spectrograms, range-Doppler maps, beamforming patterns as figures embedded in physics documentation. Reproducible plots checked into the repo alongside the docs. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| VSCode | Primary writing environment | Extensions: Markdown Preview Enhanced (math+diagram preview), markdownlint, Spell Right. Set `editor.wordWrap: "on"` for prose files. |
| GitHub PR review | Documentation review workflow | Treat doc PRs like code PRs — reviewers check equation correctness, notation consistency, cross-reference validity. GitHub renders all math/diagrams inline in PR diffs. |
| Git with conventional commits | Version control for docs | Use commit message convention `docs:` prefix for documentation commits to separate from code commits in log. |
| draw.io desktop app | Offline diagram authoring | The desktop app (available free) avoids browser dependency for offline work. Saves `.drawio` files directly to the repo. |

---

## Physics Notation Standards

This section is prescriptive. All physics derivations in the AERIS-10 documentation must follow these conventions to ensure internal consistency across the FMCW theory, beamforming, and detection theory documents.

### Governing Standard

Follow **IEEE 686-2024** (IEEE Standard for Radar Definitions) for terminology, and **IEEE 521-2019** for frequency band designations (X-band = 8–12 GHz). These are the authoritative standards for radar notation — any reviewer from industry or academia will expect these conventions.

### Equation Numbering

Number ALL equations that are referenced elsewhere. Use per-section numbering: (2.3) means Section 2, equation 3. This is standard in textbook-style technical documentation and makes cross-references unambiguous. In Markdown:

```markdown
$$
s(t) = A \cos\!\left(2\pi f_0 t + \pi k t^2\right)
\tag{2.1}
$$
```

GitHub MathJax renders `\tag{}` correctly for equation labeling.

### Symbol Conventions (FMCW-Specific)

Use these symbols consistently across all documents:

| Symbol | Meaning | Rationale |
|--------|---------|-----------|
| $f_0$ | Carrier frequency (10 GHz) | IEEE 686 convention for center frequency |
| $B$ | Chirp bandwidth | Universal FMCW notation |
| $T_c$ | Chirp duration | Subscript `c` for chirp |
| $k = B/T_c$ | Chirp rate (Hz/s) | Standard FMCW derivation notation |
| $\tau$ | Round-trip time delay | Greek tau is universal for time delay in radar |
| $R$ | Range to target | Capital R for range (IEEE 686) |
| $f_b$ | Beat frequency | Subscript `b` for beat |
| $v_r$ | Radial velocity | Subscript `r` for radial |
| $f_d$ | Doppler frequency | Subscript `d` for Doppler (IEEE 686) |
| $\lambda$ | Wavelength | Universal |
| $\mathbf{a}(\theta)$ | Array steering vector | Bold lowercase vector, argument is angle |
| $\mathbf{w}$ | Beamforming weight vector | Bold lowercase for complex weight vector |
| $N$ | Number of array elements (16) | Capital N, define once per document |
| $d$ | Element spacing | Lowercase d, typically $d = \lambda/2$ |
| $\theta_s$ | Scan angle | Subscript `s` for scan/steer |
| $P_{fa}$ | Probability of false alarm | IEEE standard abbreviation |
| $P_d$ | Probability of detection | IEEE standard abbreviation |
| $\text{SNR}$ | Signal-to-noise ratio | Roman (upright) font — it is an abbreviation, not a variable |
| $\text{CFAR}$ | Constant false alarm rate | Roman font, defined on first use |

### Matrix/Vector Notation

- Matrices: Bold uppercase, e.g., $\mathbf{R}$ for covariance matrix
- Vectors: Bold lowercase, e.g., $\mathbf{x}$ for signal vector
- Scalars: Italic, e.g., $N$, $T_c$
- Sets: Calligraphic uppercase, e.g., $\mathcal{H}_0$, $\mathcal{H}_1$ for hypothesis testing
- Operators: Roman (upright) font — $\text{E}[\cdot]$, $\text{Var}[\cdot]$, $\det(\cdot)$, $\text{tr}(\cdot)$

This follows the Haykin/Richards/Mahafza conventions used in the standard radar signal processing textbooks and is consistent with IEEE Transactions on Signal Processing notation.

---

## Document Format Conventions

### File Organization

```
docs/
  physics/
    01_fmcw_waveform.md         # FMCW theory and chirp model
    02_range_doppler.md         # Range-Doppler processing derivation
    03_beamforming.md           # Phased array and beamforming theory
    04_detection_theory.md      # CFAR, Neyman-Pearson, ROC curves
  hardware/
    01_system_overview.md
    02_rf_frontend.md
    03_fpga_architecture.md
    04_microcontroller.md
    05_antenna_array.md
    06_power_management.md
  software/
    01_fpga_pipeline.md         # DDC → CIC → matched filter → FFT → CFAR
    02_python_gui.md
    03_matlab_processing.md
  research/
    01_detection_improvements.md
    02_signal_processing_improvements.md
    03_hardware_improvements.md
  assets/
    diagrams/                   # .drawio source files
    plots/                      # Python-generated figures
    images/                     # Photos, screenshots
```

### Cross-Referencing

Use relative Markdown links for all cross-references:
```markdown
See [CFAR detection theory](../physics/04_detection_theory.md#cfar-algorithm) for derivation.
```

Anchor names auto-generate from headings in GitHub Markdown: `## CFAR Algorithm` becomes `#cfar-algorithm`. Use lowercase with hyphens. This is how internal navigation works without a static site generator.

### Math Rendering Approach

The repo is on GitHub. Use GitHub-native math rendering:
- Inline: `$expression$`
- Block: `$$` delimiters on separate lines, or ` ```math ` blocks

Do NOT use image-based math (generating PNG from LaTeX). This breaks in dark mode, cannot be copy-pasted, and is uneditable. Native MathJax rendering is the correct choice for a GitHub-hosted repo.

---

## Research Survey Methodology

For the improvement research documents (CFAR alternatives, ML-based detection, hardware miniaturization):

### Literature Source Priority

1. **IEEE Xplore** — Primary source. IEEE Transactions on Radar Systems, IEEE Transactions on Aerospace and Electronic Systems, IEEE Transactions on Signal Processing. Use the Zotero browser connector to capture directly.
2. **arXiv** — Preprints for recent ML-based radar work (2022–2025). The `eess.SP` (Electrical Engineering Signal Processing) category is the right filter.
3. **ResearchGate / Semantic Scholar** — Secondary discovery. Verify that papers found here are actually published in IEEE/Springer venues before citing.
4. **Manufacturer application notes** — Analog Devices (ADAR1000, ADF4382), Xilinx/AMD (Artix-7 DSP48 resources). High authority for hardware-specific improvements.

### Survey Document Structure

Each improvement research document should follow this structure:

1. **Problem statement** — What specific limitation of the current AERIS-10 are we addressing?
2. **Current implementation** — What does AERIS-10 do today? (Cross-reference to software/hardware docs)
3. **Literature survey** — Organized by approach category (e.g., for detection: OS-CFAR, CA-CFAR, CNN-based, etc.)
4. **Comparison table** — Techniques vs. metrics (detection probability, false alarm rate, computational cost, FPGA feasibility)
5. **Recommendations** — What is implementable on the existing XC7A100T + STM32F746 hardware?
6. **References** — IEEE citation format

### Citation Format

Use IEEE citation format inline. In Markdown, numbered footnote-style citations work well:

```markdown
CA-CFAR detection adapts the threshold to local clutter statistics [1],
while OS-CFAR provides robustness to interfering targets [2].
```

With a References section at the bottom of each document. Zotero can export a formatted IEEE reference list.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| GitHub Markdown + native MathJax | LaTeX + PDF (Overleaf/pdflatex) | Use LaTeX if the goal is formal publication (journal paper, conference proceedings). For a living repo-based reference document that engineers read daily, Markdown is strictly better — it diffs cleanly in Git, renders inline in GitHub, and requires no compile step. |
| GitHub Markdown + native MathJax | MkDocs Material + MathJax | Use MkDocs if you want a navigable website with search, sidebar navigation, and custom styling. For this project (internal engineering reference, already in a Git repo), the added complexity of a static site generator is not justified. GitHub's native rendering covers the need. |
| draw.io | Mermaid (for all diagrams) | Use Mermaid for flowcharts and sequence diagrams — it is genuinely better there. Do NOT use Mermaid for RF block diagrams, hardware interconnect diagrams, or antenna geometry figures — Mermaid's graph model cannot express spatial hardware layout. |
| Zotero | Mendeley / EndNote | Mendeley is now owned by Elsevier and requires an account with data collection. EndNote is expensive. Zotero is free, open-source, and exports to BibTeX/CSL. For a team environment, Zotero group libraries are the right choice. |
| Python + matplotlib plots | MATLAB figures | The AERIS-10 already has Python in the codebase. Reusing Python + matplotlib for documentation figures keeps the toolchain consistent. MATLAB is appropriate if the team's signal processing work is primarily in MATLAB — but for reproducible documentation figures checked into Git, Python scripts are preferable. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Word / Google Docs | Does not version-control equations or diagrams. Diffs are binary or unreadable. Equations are images that degrade when edited. Breaks the docs-as-code workflow entirely. | GitHub Markdown with native math |
| Image-rendered LaTeX equations (PNG/SVG from codecogs.com) | External dependency, breaks in dark mode, cannot be copy-pasted as text, no equation editing without regenerating images, URL-dependent rendering | Native GitHub MathJax `$...$` syntax |
| Confluence / Notion | Cloud-hosted, not version-controlled with the codebase, requires separate auth, breaks the single-repo model, equation support is weaker | GitHub Markdown in repo |
| Sphinx + RST | RST syntax is significantly harder to read/write than Markdown for an engineering team not already in the Python docs ecosystem. MathJax support requires additional extensions. Overkill for this use case. | GitHub Markdown natively |
| Lucidchart / Visio | Paid tools, cloud-locked, files are not version-controllable as human-readable diffs | draw.io (free, open, XML-based) |
| Hand-drawn ASCII timing diagrams | Illegible at scale, not maintainable | WaveDrom for digital signal timing |

---

## Stack Patterns by Variant

**If writing FMCW physics derivations:**
- Use `$$` block equations with `\tag{n}` for numbered equations
- Define all symbols in a "Notation" subsection at the start of the document
- Use `\mathbf{}` for vectors/matrices consistently throughout
- Include a derivation trail — show intermediate steps, not just final results, because the audience is engineers who need to understand the signal model to make improvements

**If writing hardware documentation:**
- Use draw.io for block diagrams exported to SVG
- Use WaveDrom for any timing diagrams (SPI initialization sequences, FPGA pipeline latency)
- Include actual register values and configuration sequences alongside the block diagrams
- Cross-reference to the specific datasheet section (e.g., "ADAR1000 datasheet §7.3 SPI Interface")

**If writing FPGA pipeline documentation:**
- Use Mermaid for the processing pipeline flow (DDC → CIC → matched filter → FFT → CFAR)
- Use WaveDrom for signal timing at module interfaces
- Include DSP48 resource utilization numbers from Vivado implementation reports
- Note clock domain crossings explicitly — this is a common source of bugs

**If writing improvement research surveys:**
- Structure around the AERIS-10's specific pain points (range, clutter, speed, size) — not generic survey coverage
- For each technique, explicitly state: "Implementable on XC7A100T: YES/NO/PARTIAL" with reasoning
- Cite only primary sources (IEEE/conference papers) — do not cite Wikipedia, tutorial sites, or manufacturer marketing

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| GitHub Markdown math (`$...$`) | All modern GitHub views | Introduced May 2022. Works in .md files, Issues, Discussions, PRs, Wikis. Does NOT render in plain `README.txt` files (must be `.md`). |
| Mermaid in GitHub Markdown | GitHub.com (native, no plugin) | Use ` ```mermaid ` fenced code blocks. Renders in .md files and wikis. Does not render in GitHub Pages without additional config. |
| WaveDrom | Browser/VSCode plugin | Not natively rendered on GitHub — export to SVG and embed as image. Use VSCode extension "WaveDrom Preview" for local editing. |
| draw.io SVG | All Markdown renderers | Export from draw.io as SVG with "Embed fonts" enabled. Embed with standard `![](path/to/diagram.svg)` syntax. |
| MathJax `\tag{}` | GitHub MathJax renderer | Confirmed supported. Use for equation numbering in block equations. |

---

## Installation

```bash
# VSCode extensions (install via command palette or CLI)
code --install-extension shd101wyy.markdown-preview-enhanced
code --install-extension DavidAnson.vscode-markdownlint
code --install-extension ban.spellright

# Python plotting dependencies (for documentation figures)
pip install matplotlib numpy scipy

# markdownlint CLI (for CI/pre-commit checks)
npm install -g markdownlint-cli

# Zotero — download from https://www.zotero.org/download/
# draw.io desktop — download from https://github.com/jgraph/drawio-desktop/releases
# WaveDrom editor — https://wavedrom.com/editor.html (browser) or VSCode extension
```

---

## Sources

- [GitHub Writing Mathematical Expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions) — Confirmed MathJax support, `$...$` syntax, `\tag{}` rendering. HIGH confidence.
- [GitHub Blog: Math Support in Markdown](https://github.blog/news-insights/product-news/math-support-in-markdown/) — Official announcement, confirms production availability. HIGH confidence.
- [IEEE 686-2024 Standard for Radar Definitions](https://standards.ieee.org/ieee/686/10853/) — Authoritative notation source. HIGH confidence.
- [IEEE 521-2019 Letter Designations for Radar-Frequency Bands](https://ieeexplore.ieee.org/document/8999849/) — X-band definition 8–12 GHz. HIGH confidence.
- [WaveDrom Digital Timing Diagram Engine](https://wavedrom.com/) — Actively maintained, VSCode integration confirmed. HIGH confidence.
- [draw.io Blog: Mermaid Diagrams](https://www.drawio.com/blog/mermaid-diagrams) — Confirms draw.io as active tool with Mermaid support. HIGH confidence.
- [Mermaid Diagramming Tool](https://mermaid.js.org/) — GitHub-native rendering confirmed. HIGH confidence.
- [Zotero Quick Start Guide](https://www.zotero.org/support/quick_start_guide) — IEEE citation style, group libraries, BibTeX export confirmed. HIGH confidence.
- [Mermaid vs Lucidchart vs Draw.io 2025 Comparison](https://www.tools-online.app/blog/Free-Diagram-Tools-Comparison---Mermaid-vs-Lucidchart-vs-Drawio-vs-Visio-2025) — Draw.io confirmed as leading free option. MEDIUM confidence (comparison site).
- [NATO RTO EN-SET-086bis: Fundamentals of Signal Processing for Phased Array Radar](https://publications.sto.nato.int/publications/STO%20Educational%20Notes/RTO-EN-SET-086bis/EN-SET-086bis-01.pdf) — Notation conventions for steering vectors, beamforming weights. HIGH confidence.
- [arXiv: Comprehensive Survey of ML Applied to Radar Signal Processing](https://ar5iv.labs.arxiv.org/html/2009.13702) — Survey structure reference. MEDIUM confidence (arXiv preprint).

---

*Stack research for: AERIS-10 FMCW radar system documentation and improvement research*
*Researched: 2026-03-13*
