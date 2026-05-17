# Feature -> Test -> File RTM — Cryogenic Dashboard v0.4.9

| RTM ID | Feature / Requirement | Runtime Files | Validation Gate |
|---|---|---|---|
| RTM-001 | Material database integrity | `data/materials.json`, `js/materials.js` | `tests/materials.validate.js` |
| RTM-002 | Numerical integration stability | `js/numerics.js` | `tests/numerics.test.js` |
| RTM-003 | Export consistency | `js/export.js`, `js/app_modular.js` | `tests/export.test.js` |
| RTM-004 | File index coherence | `file_index.json`, `file_index.yaml` | `tests/file_index_integrity.test.js` |
| RTM-005 | Static browser entrypoints | `index.html`, `dashboard_modular.html`, `files.html`, `ssot_launcher.html`, `index_slides.html` | `tests/static_entrypoints.test.js` |
| RTM-006 | Runtime version coherence | `VERSION`, `README.md`, `package.json`, `ssot.json` | `scripts/version-coherence-check.js` |
| RTM-007 | SSOT regeneration planning | `ssot.json`, `scripts/regenerate-ssot-views.js` | `npm run ssot:plan` |

## Guidance

Historical snapshots may intentionally preserve older version references. Active runtime/package-facing surfaces should align to v0.4.9.
