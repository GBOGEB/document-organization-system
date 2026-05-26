<!-- markdownlint-disable MD022 MD032 MD036 -->

# FILE INDEX v0.4.9
**Updated:** 2026-05-05  
**Purpose:** Canonical navigation index for the v0.4.9 package.  
**Source:** Generated from `VERSION` and `scripts/regenerate-ssot-views.js`.

## 1) Dashboard UI

- `index.html` — landing page and version selector
- `dashboard_modular.html` — modular dashboard (v0.4.9)
- `files.html` — file browser and documentation hub
- `html_preview_hub.html` — visual preview hub for HTML entry points
- `ssot_launcher.html` — SSOT launcher view
- `index_slides.html` — SSOT presentation deck
- `material_properties_dashboard_v1_10.html` — legacy single-file dashboard
- `style.css` — shared styling

## 2) JavaScript Modules

- `js/app_modular.js` — modular dashboard controller
- `js/materials.js` — NIST property evaluators
- `js/numerics.js` — Trapezoid, Simpson, Romberg, Gauss-Legendre
- `js/plots.js` — Plotly rendering and PNG export
- `js/export.js` — CSV/JSON export

## 3) Data, Schema, Tests

- `data/materials.json` — material database
- `schemas/materials.schema.json` — materials schema
- `tests/numerics.test.js` — Node numerics tests
- `tests/export.test.js` — CSV/JSON export consistency checks
- `tests/materials.validate.js` — materials validation tests
- `tests/file_index_integrity.test.js` — generated file-index integrity checks
- `tests/static_entrypoints.test.js` — static entrypoint and reference checks
- `tests/nist_parity.test.js` — NIST parity regression suite

## 4) Canonical Documentation

- `README.md`
- `FINAL_HANDOVER.md`
- `SESSION_SUMMARY.md`
- `docs/CHANGELOG.md`
- `docs/CRYO_DASHBOARD_SESSION_HANDOVER_v0.4.9.md`
- `docs/NIST_PARITY_TEST_REPORT_v0.4.9.md`
- `docs/GITHUB_PAGES_DEPLOYMENT_CHECKLIST.md`
- `docs/SSOT_REGENERATION_PIPELINE_v0.4.9.md`
- `FILE_INDEX_v0.4.9.md`
- `DASHBOARD_TESTING_GUIDE.md`
- `GIT_TRACKING_MANIFEST.md`

## 5) Scripts and Metadata

- `VERSION` — source-of-truth release version
- `package.json` — scripts and metadata
- `scripts/regenerate-ssot-views.js` — deterministic generator for file-index artifacts
- `scripts/version-coherence-check.js` — active version consistency validation
- `file_index.yaml`, `file_index.json` — generated machine-readable intake indexes

## Summary

- Active version: **v0.4.9**
- Machine-readable indexes: **file_index.yaml, file_index.json**
- Primary start page: `index.html`

*End of generated file index*
