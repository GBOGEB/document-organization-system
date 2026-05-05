<!-- markdownlint-disable MD060 -->

# 🧊 Cryogenic Material Property Dashboard — v0.4.7

**SCK CEN Engineering Tool** — 10 NIST materials · k(T) + cp(T) + Thermal
Contraction · 1–300 K

## 🌐 Quickest Access — No Install Required

### Option 1 — GitHub Pages (primary, recommended)

Open the hosted URL in any browser. No Python, no server, no install.

```text
https://gbogeb.github.io/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/index.html
```

All pages — including `dashboard_modular.html` — work directly over HTTPS. For
setup steps see
[`docs/GITHUB_PAGES_PUBLISH_GUIDE.md`](docs/GITHUB_PAGES_PUBLISH_GUIDE.md).

### Option 2 — Double-click (file://) fallback

**Legacy dashboard only** — `material_properties_dashboard_v1_10.html` is fully
self-contained. Double-click the file in Windows Explorer or macOS Finder. Opens
in any browser, no server needed.

> Note: `dashboard_modular.html` uses ES6 `import` modules which browsers block
> from `file://`. Use Option 1 or Option 3 for the modular dashboard.

### Option 3 — Local Python server (dev/test)

```bash
# From the project folder:
python -m http.server 8000
# Then open:
http://localhost:8000/index.html
```

Windows shortcuts: double-click `start_server.bat` or run `start_dashboard.ps1`.



## 📋 Access Matrix

| Page | GitHub Pages | Double-click file:// | Local http:// |
|---|---|---|---|
| `index.html` (landing) | ✅ | ✅ | ✅ |
| `dashboard_modular.html` *(primary v0.4.7)* | ✅ | ❌ ES6 modules blocked | ✅ |
| `material_properties_dashboard_v1_10.html` *(legacy v1.10)* | ✅ | ✅ self-contained | ✅ |
| `files.html` (this navigator) | ✅ | ✅ | ✅ |
| `html_preview_hub.html` | ✅ | ✅ | ✅ |



## 🧭 Navigation

```
index.html          ← Start here — version selector and capability tier guide
  ├─ dashboard_modular.html     ← Primary v0.4.7 dashboard (GitHub Pages or localhost)
  ├─ material_properties_dashboard_v1_10.html  ← Legacy v1.10 (double-click OK)
  └─ files.html     ← Full artifact navigator + this spot-check guide
```

## 🟢 Start Here

If you only open three things, use this order:

1. `index.html` — first entry point and runtime chooser.
2. `files.html` — canonical navigator for docs, previews, and artifact classes.
3. `dashboard_modular.html` — primary v0.4.7 runtime once you are ready to
   calculate/export.

Minimum artifact set for handover or clean reuse:

- `index.html`
- `files.html`
- `dashboard_modular.html`
- `data/materials.json`
- `js/app_modular.js`
- `js/materials.js`
- `README.md`
- `FINAL_HANDOVER.md`
- `docs/CHANGELOG.md`
- `docs/SESSION_DROPIN_HANDOVER_v0.4.7.md`
- `VERSION`

Machine-readable companion indexes:

- `file_index.yaml`
- `file_index.json`

Use `files.html` for human navigation. Use `file_index.yaml` or
`file_index.json` for scripted intake, handover packaging, or external tooling.



## 📊 What the Dashboard Computes

```text
THERMAL CONDUCTIVITY k(T)  [W/(m·K)]
  k at T1, k at T2
  ∫k(T)dT  [W/m]     — integral over T1→T2
  Qdot     [W]       — (A [m²] / L [m]) × ∫k dT

SPECIFIC HEAT cp(T)  [J/(kg·K)]
  cp at T1, cp at T2
  ∫cp(T)dT [J/kg]    — integral over T1→T2
  Energy   [J]       — m [kg] × ∫cp dT  (cooldown/warmup energy)

THERMAL CONTRACTION Y(T)  [×10⁻⁵]  (v0.4.7, 5 materials)
  Y = (L(T) − L₂₉₃) / L₂₉₃
  Strain   [m/m]
  ΔL       [m]       — between T1 and T2
```

**Integration methods available:** Trapezoid · Simpson 1/3 · Romberg ·
Gauss-Legendre 4-pt

**Compare All mode** runs all four methods simultaneously and reports %
deviation vs Romberg.



## ✅ Spot-Check Reference Values

Use these to verify the dashboard is computing correctly after setup. Set 100
integration steps, use the Romberg method.

| Material | Property | T1 (K) | T2 (K) | Expected ∫ (Romberg) | Units |
|---|---|---|---|---|---|
| AISI316 | k | 20 | 300 | **3 012.150** | W/m |
| AISI316 | cp | 20 | 300 | **93 190.19** | J/kg |
| CuRRR100 | k | 4 | 300 | **194 330.57** | W/m |

> These values are the authoritative regression fixtures from
> `tests/numerics.test.js`. Trapezoid will differ slightly (expect ~0.04% lower
> on smooth curves); Romberg and Gauss-Legendre agree to < 0.001%.



## 🗂️ Materials (10)

| # | Key | Name | k | cp | tc |
|---|---|---|---|---|---|
| 1 | AISI316 | AISI 316 Stainless Steel | ✅ | ✅ | ✅ |
| 2 | Al6061T6 | Aluminum 6061-T6 | ✅ | ✅ | ✅ |
| 3 | G10Normal | G-10 CR Fiberglass (Normal) | ✅ | ✅ | — |
| 4 | G10Warp | G-10 CR Fiberglass (Warp) | ✅ | — | ✅ |
| 5 | CuRRR50 | Copper RRR=50 | ✅ | ✅ | — |
| 6 | CuRRR100 | Copper RRR=100 | ✅ | ✅ | — |
| 7 | CuRRR150 | Copper RRR=150 | ✅ | ✅ | — |
| 8 | CuRRR300 | Copper RRR=300 | ✅ | ✅ | — |
| 9 | CuRRR500 | Copper RRR=500 | ✅ | ✅ | — |
| 10 | Ti64 | Titanium Ti-6Al-4V | ✅ | ✅ | ✅ |

Source: NIST cryogenic properties database. All coefficients validated against
NIST reference values.



## 🔢 Version History

| Version | Track | Key change |
|---|---|---|
| v1.0–v1.10 | VBA/HTML legacy | Standalone self-contained HTML; DMAIC log in `material_properties_docs/DMAIC_VERSION_LOG.md` |
| v0.3.0 | Modular JS | ES6 module architecture baseline |
| v0.4.0 | Modular JS | 10 NIST materials + k/cp merge |
| v0.4.4 | Modular JS | Single Method / Compare All result mode |
| v0.4.5 | Modular JS | Delta Summary panel; delta/integral export alignment |
| v0.4.6 | Modular JS | Thermal contraction Y(T); KPI strip; dual-axis plot; v1.10 deprecated |
| v0.4.7 | Modular JS | B1 comparison raw/normalized/split view; max-4 overlays; disabled no-data compare entries |

Full modular changelog: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)

> **v0.4.x release gate**: `npm test` must pass → validation → version bump in
> `VERSION` → `git push`.



## 🧪 Automated Tests

```bash
npm test
```

Runs:

- `tests/numerics.test.js` — regression fixtures for all 4 integration methods
  across 3 material/property cases
- `tests/export.test.js` — CSV/JSON export consistency vs UI Delta Summary
  values
- `tests/materials.validate.js` — schema validation for all materials in
  `data/materials.json`

### Next Iteration Validation TODO (Engineering Depth)

Current tests provide strong regression coverage, but the release gate should be
expanded with explicit engineering validation layers:

- Typical-value acceptance windows by material/property/range (quick sanity
  envelope)
- Direct NIST-equation parity checks over expanded temperature slices
- Method-to-method tolerance bands documented as pass/fail criteria

Target artifact updates for next iteration:
- `tests/numerics.test.js` (expanded matrix)
- `DASHBOARD_TESTING_GUIDE.md` (acceptance thresholds)
- release-time validation report generated from test outputs



## 📁 Key Files

| File | Purpose |
|---|---|
| `data/materials.json` | Canonical NIST coefficient database |
| `js/materials.js` | Property evaluator and NIST equation forms |
| `js/numerics.js` | All 4 numerical integration methods |
| `js/app_modular.js` | v0.4.7 primary orchestrator |
| `docs/CHANGELOG.md` | v0.4.x engineering changelog |
| `material_properties_docs/DMAIC_VERSION_LOG.md` | v1.x VBA/HTML lineage log |
| `DASHBOARD_TESTING_GUIDE.md` | Manual test procedures with expected output guide |
| `docs/GITHUB_PAGES_PUBLISH_GUIDE.md` | Step-by-step GitHub Pages publish guide |



## 📞 Contact

Organization: Studiecentrum voor Kernenergie (SCK CEN) Version: 0.4.7 | Last
Updated: 2026-05-04
