## v0.4.9-fix
**Date:** 2026-05-18

### Fixed
- **evalRational() alignment**: Fixed rational evaluator in `ssot_launcher.html` and `index_slides.html` to match canonical `js/materials.js rational()` model — uses `sqrt(T)`-based terms with all 9 coefficients `[a..i]` instead of incorrect `log10(T)`-based polynomial ratio with 8 coefficients.
- Copper RRR k(T) traces in SSOT presentation views now render correctly.

### Added
- **NIST data lineage**: Added full 6-step traceability chain to `ssot.json` — from NIST Monograph 177 source data through `js/materials.js` to rendered Plotly charts.
- **Rational model specification**: Documented canonical rational model form, coefficient labels, and NIST reference in `ssot.json`.
- Updated session handover document (`CRYO_DASHBOARD_SESSION_HANDOVER_v0.4.9.md`) with PR #16 post-merge fix details.

## v0.4.9
**Date:** 2026-05-15

### Added
- Introduced modular export test enhancements for Rate of Integral validations.
- Introduced Metadata Diff HTML visualization for metadata review.
- Created focused branches for v0.4.9 (patches) and v0.8 feature rebuilds.
- Added modular CI pipeline audit workflow for the dashboard subtree.
- **SSOT system**: `ssot.json` (canonical data source), `index_slides.html` (15-slide Reveal.js presentation), `ssot_launcher.html` (navigation hub with live charts).

### Fixed
- Addressed modular CSV/JSON integration mismatches.
- Implemented test assertions for JSON consistency across delta summaries.
- Added file-index integrity gate to verify YAML/JSON consolidation and block
  fallback-only artifact sets.

### Notes
- CI pipeline audit now validates v0.4.9 modular artifact integrity.
