## v0.4.9-nist
**Date:** 2026-05-18

### Added
- **NIST Parity Regression Test Suite** (`tests/nist_parity.test.js`): 769 assertions validating all 10 materials × all properties against independently-implemented NIST equations.
  - Coefficient verification against NIST-published values
  - Evaluator parity at 9–15 temperature points per material/property
  - Copper RRR rational model deep validation (peak detection, cross-RRR ordering, room-temp convergence)
  - Thermal contraction validation (low-T branch, reference point)
  - Edge cases: boundary conditions, null properties, piecewise boundaries
  - Physical reasonableness checks and continuity validation
- **NIST Parity Test Report** (`docs/NIST_PARITY_TEST_REPORT_v0.4.9.md`)
- **GitHub Pages Deployment Checklist** (`docs/GITHUB_PAGES_DEPLOYMENT_CHECKLIST.md`)
- Added `test:nist` script to `package.json`
- NIST parity tests integrated into main `npm test` pipeline

### Metrics

| Metric | Value | KPI Target |
|--------|-------|------------|
| Total assertion checks | 769/769 pass | 100% pass |
| Materials covered | 10/10 | 100% of current catalog |
| Property models covered | polylog, piecewise-logpoly, rational, thermal-contraction | All production equation types |
| Property availability coverage | k: 10/10, cp: 9/10, tc: 5/10 | Match available source data |
| Main pipeline coverage | numerics + export + materials + file index + static + version + NIST parity | Full gate pass |

### DMAIC Trace (Quality Control)

| DMAIC Stage | Trace Evidence |
|-------------|----------------|
| Define | Risk: model/equation drift between NIST coefficients and runtime evaluators |
| Measure | Added 769-assertion regression suite + per-section report metrics |
| Analyze | Rational-model and boundary behavior probed with targeted fixtures and continuity sweeps |
| Improve | Added literal golden fixtures, expanded deployment checklist validation depth |
| Control | `npm test` gate enforces ongoing parity/integrity checks on each change |

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
