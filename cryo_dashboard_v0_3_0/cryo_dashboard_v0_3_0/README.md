# Cryogenic Material Dashboard v0.4.6

## Purpose

Cryogenic engineering dashboard for evaluating NIST material properties over temperature and integrating engineering quantities for thermal design.

Primary outputs:

```text
THERMAL CONDUCTIVITY (k)
  k(T)        [W/(m·K)]
  ∫k(T)dT     [W/m]
  Qdot        [W] = (A/L) × ∫k(T)dT

SPECIFIC HEAT (cp)
  cp(T)       [J/(kg·K)]
  ∫cp(T)dT    [J/kg]
  Energy      [J] = m × ∫cp(T)dT

THERMAL CONTRACTION (tc)  [v0.4.6+, 5 materials]
  Y(T)        [x1e-5]  (L(T)-L293)/L293
  Strain      [m/m]
  ΔL          [m]  between T1 and T2
```

## Current Applications

- `index.html` — version selector and capability overview
- `dashboard_modular.html` — modular v0.4.6 dashboard (ES6 modules) — **primary**
- `material_properties_dashboard_v1_10.html` — legacy v1.10 dashboard (deprecated, reference only)
- `files.html` — file browser and canonical documentation entry point

## Version Summary

```text
v0.1.0  Tabbed dashboard concept
v0.2.0  Single-file engineering dashboard
v0.3.0  Modular architecture baseline
v0.4.0  10 NIST materials + k/cp merge
v0.4.1  Integration method comparison panel
v0.4.2  Gauss-Legendre added to comparison/export
v0.4.3  Download Plot button + PNG export flow
v0.4.4  Single Method / Compare All result mode
v0.4.5  Delta Summary panel + delta/integral export alignment
v0.4.6  GAP-01→10 features, Quick Outputs KPI strip, dual-axis plot,
        thermal contraction Y(T) property (5 materials), material
        dropdown filtering by property, v1.10 deprecated
```

## Materials Included (10)

1. AISI316
2. Al6061T6
3. G10Normal
4. G10Warp
5. CuRRR50
6. CuRRR100
7. CuRRR150
8. CuRRR300
9. CuRRR500
10. Ti64

Source-of-truth data: `data/materials.json`

## How to Run

Use a local HTTP server (required for ES modules and `fetch()`):

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/index.html
```

Windows shortcuts:

```text
start_server.bat
start_dashboard.ps1
```

## Validation

```bash
npm test
```

This runs:

- `tests/numerics.test.js`
- `tests/materials.validate.js`

## Key References

- Changelog: `docs/CHANGELOG.md`
- Engineering handover: `docs/ENGINEERING_HANDOVER.md`
- Setup instructions: `SETUP_GUIDE.md`
- Standalone vs Python guidance: `STANDALONE_VS_PYTHON.md`

## Contact

Organization: Studiecentrum voor Kernenergie (SCK CEN)
Version: 0.4.5
Last Updated: 2026-04-28