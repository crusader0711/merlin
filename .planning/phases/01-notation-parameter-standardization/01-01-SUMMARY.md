---
phase: 01-notation-parameter-standardization
plan: 01
subsystem: notation
tags: [mathjax, ieee-686, symbol-table, equation-numbering, github-markdown]

# Dependency graph
requires:
  - phase: none
    provides: first phase, no dependencies
provides:
  - Project-wide equation numbering convention with document-prefix tags
  - MathJax usage rules for GitHub (supported vs unsupported features)
  - Cross-reference format for equations and symbols
  - Variant callout block template for Nexus vs Extended differences
  - Authoritative symbol table with 57 symbols across 6 domains
  - Anti-patterns list preventing notation drift
  - Document template skeleton for all future documents
affects: [01-02-parameter-table, phase-2-physics, phase-3-hardware, phase-4-software]

# Tech tracking
tech-stack:
  added: [MathJax \tag{} manual numbering, GitHub-native Markdown math]
  patterns: [document-prefix equation tags, plain-text cross-references, variant callout blocks]

key-files:
  created:
    - 00_notation/conventions.md
    - 00_notation/symbol_table.md
  modified: []

key-decisions:
  - "Document-prefix equation numbering (FMCW-N, LFM-N, BF-N, etc.) chosen over section-based numbering to guarantee cross-document uniqueness"
  - "Plain-text cross-references (Eq. (FMCW-1)) chosen because GitHub MathJax does not support \\ref{}/\\eqref{}"
  - "IEEE 686-2024 as notation authority with Skolnik/Richards as secondary references"
  - "Physical constants (c, k_B, T_0) included in symbol table with exact values; all system parameter values deferred to parameter_table.md"

patterns-established:
  - "Document-prefix \\tag{PREFIX-N} for all referenced equations"
  - "Unit formatting: $value~\\text{Unit}$ with tilde for non-breaking space"
  - "Variant callout block for Nexus vs Extended differences"
  - "Anti-pattern: never inline parameter values in derivations"
  - "Every new document links to symbol_table.md and parameter_table.md in Prerequisites section"

requirements-completed: [NOTN-01, NOTN-03]

# Metrics
duration: 3min
completed: 2026-03-13
---

# Phase 1 Plan 01: Equation/Formatting Conventions and Symbol Table Summary

**Document-prefix equation numbering convention and 57-symbol IEEE 686-aligned table establishing notation authority for all AERIS-10 documentation**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-13T22:15:22Z
- **Completed:** 2026-03-13T22:17:57Z
- **Tasks:** 2
- **Files created:** 2

## Accomplishments

- Created `conventions.md` defining equation numbering (document-prefix tags), cross-reference format, MathJax rules, variant callouts, anti-patterns, and document template
- Created `symbol_table.md` with 57 symbols across 6 domain sections (waveform/timing, range/velocity, antenna/beamforming, detection/signal, signal processing, physical constants)
- Established IEEE 686-2024 as the notation authority for the entire project
- Both files cross-reference each other and the future `parameter_table.md`

## Task Commits

Each task was committed atomically:

1. **Task 1: Create equation numbering convention and formatting rules** - `14bfebb` (feat)
2. **Task 2: Create project-wide symbol table** - `93cbc69` (feat)

## Files Created/Modified

- `00_notation/conventions.md` - Equation numbering convention, cross-reference format, MathJax usage rules, variant callout template, anti-patterns, document template
- `00_notation/symbol_table.md` - Project-wide symbol table with IEEE 686-2024 aligned notation across 6 domains

## Decisions Made

- **Document-prefix numbering over section-based:** Chose `FMCW-N`, `LFM-N`, `BF-N` prefixes instead of `1.1`, `2.1` section numbers. Rationale: guarantees uniqueness across the entire documentation set without requiring cross-document coordination of section number ranges.
- **Plain-text cross-references:** Since `\ref{}` and `\eqref{}` do not work on GitHub, adopted plain-text "Eq. (PREFIX-N)" with Markdown links for cross-document references.
- **Physical constants in symbol table:** Included exact values for $c$, $k_B$, $T_0$ in the symbol table since these are universal constants, not system-specific parameters. All system parameter values are deferred to `parameter_table.md`.
- **IEEE 686-2024 as primary authority:** Chose IEEE 686 over Skolnik-specific or Richards-specific conventions for maximum standards compliance.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Notation conventions and symbol table are committed and ready for use by all subsequent documents
- Plan 01-02 (master system parameter table) can proceed immediately -- it will create `parameter_table.md` which is already referenced by both files created in this plan
- All Phase 2 physics documents will import notation from these files

---
*Phase: 01-notation-parameter-standardization*
*Completed: 2026-03-13*
