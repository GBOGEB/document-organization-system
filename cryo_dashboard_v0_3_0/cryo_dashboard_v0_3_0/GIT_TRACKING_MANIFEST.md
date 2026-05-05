<!-- markdownlint-disable MD022 MD032 -->

# GIT TRACKING MANIFEST v0.4.9
**Generated:** 2026-05-05  
**Purpose:** Definitive tracked-file manifest for the current release



## Track in Git

### Application
- `index.html`
- `dashboard_modular.html`
- `material_properties_dashboard_v1_10.html`
- `files.html`
- `style.css`

### JavaScript Modules
- `js/app.js`
- `js/app_modular.js`
- `js/materials.js`
- `js/numerics.js`
- `js/state.js`
- `js/plots.js`
- `js/export.js`
- `js/debug.js`
- `js/logger.js`

### Data, Schema, Tests
- `data/materials.json`
- `schemas/materials.schema.json`
- `tests/test_numerics.html`
- `tests/test_numerics.js`
- `tests/numerics.test.js`
- `tests/export.test.js`
- `tests/materials.validate.js`

### Canonical Documentation
- `README.md`
- `SETUP_GUIDE.md`
- `DASHBOARD_TESTING_GUIDE.md`
- `STANDALONE_VS_PYTHON.md`
- `GIT_TRACKING_MANIFEST.md`
- `FILE_INDEX_v0.4.9.md`
- `FINAL_HANDOVER.md`
- `docs/CHANGELOG.md`
- `docs/SESSION_DROPIN_HANDOVER_v0.4.9.md`
- `docs/GRAPH_EXPORT_HANDLING_AND_FALLBACK.md`
- `docs/PR_RELEASE_v0.4.9.md`
- `docs/BASELINE_VERIFICATION_v0.4.5.md`
- `docs/ENGINEERING_HANDOVER.md`
- `docs/HANDOVER_v0.4.5.md`
- `docs/LOGIC_EXTRACTION_REGISTER_v0.4.6.md`

### Utilities and Metadata
- `start_server.bat`
- `start_dashboard.ps1`
- `package.json`
- `VERSION`
- `.gitignore`



## Exclude from Git

- `archive_20260427/*` (except tracked dated snapshots like
  `archive_20260427/archived_20260428/`)
- `extracted_handover_pack/`
- `extracted_handover_v1_10_verify/`
- `extracted_html_files/`
- `node_modules/`
- `*.stackdump`
- `*.log`
- `*.zip`
- `.vscode/`
- `.idea/`



## Release Commands

```bash
git status
git --no-pager log --oneline -10
git tag -a v0.4.9 -m "v0.4.9 release"
git archive --format=zip --output=cryo_dashboard_v0.4.9_clean.zip HEAD
```



## Repository Metadata

- Name: `cryo-dashboard`
- Version: `0.4.7`
- Stack: `JavaScript (ES6 modules) + Plotly`
- Data scope: 10 cryogenic materials, 1–300 K



**Manifest Status:** Current for v0.4.9



## Gap Implementation Commits (v0.4.6 session 2026-04-28)

| Commit | Message | Gaps |
|--------|---------|------|
| `d8eff6a` | docs: v0.4.6 coherence pass (9 files) | — |
| `1b9e747` | docs: extraction slice 01 — logic register, feature map, gap list | — |
| `7e4f8ba` | feat(gap-04): rangeStatus validation indicator to delta summary panel | GAP-04 |
| `5e37087` | feat(gap-10,gap-03): average definition note and method equation display | GAP-10, GAP-03 |
| `62efaa0` | feat(gap-02,gap-08): add active equation panel and VBA/NIST audit table | GAP-02, GAP-08 |
| `2cf7a08` | feat(gap-01,gap-05): debug mode toggle and Y-axis min/max override | GAP-01, GAP-05 |
| `f62108e` | feat(gap-06,gap-09): plot point count control and theme-aware Plotly colors | GAP-06, GAP-09 |
| `8a6aad6` | docs: mark GAP-01..10 implemented in register; update tracking manifest | — |
| `3f40af1` | feat(gap-07): layered wall series-R screening panel | GAP-07 |
| `7c85a94` | docs: mark GAP-07 implemented in extraction register | — |
| `02dcf3b` | feat: add A/L inputs and conduction Qdot / cooldown energy to delta summary | — |

**All v1.10 extraction gaps closed. Extraction Slice 01 complete.**
