<!-- markdownlint-disable MD022 MD032 MD036 -->

# FILE INDEX v0.4.7
**Updated:** 2026-05-05  
**Purpose:** Canonical navigation index for the v0.4.7 package.



## 1) Dashboard UI

- `index.html` — landing page and version selector
- `dashboard_modular.html` — modular dashboard (v0.4.7)
- `material_properties_dashboard_v1_10.html` — legacy single-file dashboard
- `files.html` — file browser and documentation hub
- `style.css` — shared styling



## 2) JavaScript Modules

- `js/app.js` — index page controller
- `js/app_modular.js` — modular dashboard controller
- `js/materials.js` — NIST property evaluators
- `js/numerics.js` — Trapezoid, Simpson, Romberg, Gauss-Legendre
- `js/state.js` — calculation state
- `js/plots.js` — Plotly rendering and PNG export
- `js/export.js` — CSV/JSON export
- `js/debug.js` — debug output
- `js/logger.js` — event logging



## 3) Data, Schema, Tests

- `data/materials.json` — material database
- `schemas/materials.schema.json` — materials schema
- `tests/test_numerics.html` — browser test harness
- `tests/test_numerics.js` — browser numerics checks
- `tests/numerics.test.js` — Node numerics tests
- `tests/export.test.js` — CSV/JSON export consistency checks
- `tests/materials.validate.js` — materials validation tests



## 4) Canonical Documentation

- `README.md`
- `SETUP_GUIDE.md`
- `DASHBOARD_TESTING_GUIDE.md`
- `STANDALONE_VS_PYTHON.md`
- `GIT_TRACKING_MANIFEST.md`
- `FILE_INDEX_v0.4.7.md` (canonical index)
- `FINAL_HANDOVER.md`
- `docs/CHANGELOG.md`
- `docs/SESSION_DROPIN_HANDOVER_v0.4.7.md`
- `docs/GRAPH_EXPORT_HANDLING_AND_FALLBACK.md`



## 5) Scripts and Metadata

- `start_server.bat` — Windows server launcher
- `start_dashboard.ps1` — PowerShell launcher
- `VERSION` — source-of-truth version file
- `package.json` — scripts and metadata
- `handover.glob.yaml`, `SESSION_CONTEXT.json` — handover metadata
- `file_index.yaml`, `file_index.json` — machine-readable intake indexes



## Summary

- Active version: **v0.4.7**
- Modular integration methods: **4**
- Comparison overlay limit: **4**
- Primary start page: `index.html`



*End of file index*
