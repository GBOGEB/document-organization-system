<!-- markdownlint-disable MD024 -->

# Changelog

## v0.4.6

### Added

- `dashboard_modular.html` + `js/app_modular.js`: **Debug mode toggle** — checkbox in Debug Panel header controls visibility of step-through calculation output (`#debugPanel`). (GAP-01)
- `js/materials.js` + `dashboard_modular.html`: **Active equation panel** — `equationText()` renders source, equation form, range, and coefficients for the active material/property into `#equationPanel`. (GAP-02)
- `js/app_modular.js`: **Method equation display** — `methodEquationNote()` helper appended to integration results panel showing the active numerical method's formula. (GAP-03)
- `js/materials.js` + `js/app_modular.js`: **Range status validation indicator** — `rangeStatus()` added to `materials.js`; result displayed in Delta Summary panel with `.ok`/`.warning` styling. (GAP-04)
- `dashboard_modular.html` + `js/app_modular.js`: **Y-axis min/max override** — two number inputs above `#mainPlot` let users pin the Plotly y-axis; leaving blank restores auto-range. (GAP-05)
- `dashboard_modular.html` + `js/app_modular.js`: **Plot point count control** — separate `plotPoints` input (default 200) drives plot resolution independently of integration step count. (GAP-06)
- `dashboard_modular.html` + `js/app_modular.js`: **Layered wall series-R screening panel** — 3-layer table with per-layer material select, L, and A; computes `k_avg`, series R, and Qdot using trapezoid integration over T₁–T₂. (GAP-07)
- `dashboard_modular.html`: **VBA/NIST audit table** — static 6-row table documenting coefficient-level discrepancies between VBA implementation and NIST reference. (GAP-08)
- `dashboard_modular.html` + `js/app_modular.js`: **Dark/light theme toggle** — `localStorage`-persisted theme switch; Plotly chart re-renders with correct `font.color` and `gridcolor` on every toggle. (GAP-09)
- `js/app_modular.js`: **Average definition note** — appended to Integration Results panel explaining that average = (1/|ΔT|) × ∫property(T) dT, and method-specific k/cp note for compare mode. (GAP-10)
- `dashboard_modular.html` + `js/app_modular.js`: **Area / Length inputs and Qdot** — `areaInput` (A [m²]) and `lengthInput` (L [m]) added to controls. Delta Summary now shows `Conduction Qdot = (A/L) × ∫k dT` for k, and `Cooldown energy = m × ∫cp dT` for cp; updates live on input change.
- `docs/LOGIC_EXTRACTION_REGISTER_v0.4.6.md`: Extraction Slice 01 register — full gap list, feature map, discrepancy record, and Status column tracking implementation commits.
- `dashboard_modular.html` + `js/app_modular.js`: **Quick Outputs KPI strip** — 8-card KPI panel below Global Controls showing property values at T1/T2, integral, average, delta, derived engineering value (Qdot/energy/strain), and validation status. tc mode shows Y(T1), Y(T2), strain, Δstrain, ΔL.
- `js/app_modular.js` + `js/plots.js`: **Dual-axis integration plot** — second Plotly chart shows property curve (fill-to-zero) on primary y-axis and cumulative integral on secondary y-axis.
- `data/materials.json` + `js/materials.js` + `js/app_modular.js`: **Thermal contraction Y(T) property** — new `tc` property type (`thermal-contraction`) added. 5-coefficient polynomial with optional low-T constant branch (`tlow`/`f`). Materials with tc data: AISI316, Al6061T6, G10Normal, G10Warp, Ti64. Copper variants have k and cp only.
- `dashboard_modular.html` + `js/app_modular.js`: **Known Length and length-reference inputs** — engineering inputs for ΔL calculation from Y(T) values. Reference mode: L293 or L(T1).
- `js/app_modular.js`: **Property-based material filtering** — `materialSelect` dropdown auto-filters to materials that have data for the selected property. Switching to `tc` hides copper variants; fallback to k-materials if filtered list is empty.
- `index.html` + `files.html` + `material_properties_dashboard_v1_10.html`: **v1.10 deprecated** — v1.10 demoted to "Legacy (Deprecated)" across all navigation; deprecation banner added to v1.10 page itself.
- `tests/materials.validate.js`: Extended to accept `thermal-contraction` type and validate 5-coefficient array, optional `tlow`/`f` fields.

### Changed

- `js/app_modular.js`: `calculate()` now computes a separate `plotT`/`plotValues` array at `plotPoints` resolution, keeping integration accuracy independent of plot density.
- `js/app_modular.js`: `updatePlot()` reads `data-theme` on every render to pass correct Plotly `font.color`, axis colors, and `gridcolor` for dark and light themes.
- `js/app_modular.js`: `populateLayerSelects()` auto-populates layer material dropdowns from the loaded database (k-property materials only).
- `js/app_modular.js`: `materialSelect` now fires `calculate()` automatically on change (no manual Calculate button required after switching material).
- `js/materials.js`: `loadMaterialDatabase()` uses `cache: "no-store"` + timestamp query parameter to prevent browser caching of `materials.json`.
- `dashboard_modular.html`: `#calcError` inline error div replaces `alert()` for missing-property error feedback.

## v0.4.5

### Added

- `dashboard_modular.html`: Added a dedicated `Delta Summary` panel with two output lines for `Δk = k(T2) - k(T1)` and `∫k dT [T1→T2]`.

### Changed

- `js/app_modular.js`: Added state-read-only Delta Summary rendering sourced from already-computed values (`currentState.values` and selected-method `currentState.integral`) with active-method awareness.
- `js/app_modular.js`: CSV export now includes `delta_k` and `integral_k` rows using the exact same formatted values shown in Delta Summary.
- `js/export.js`: Modular CSV/JSON export payload generation is now centralized so exported Delta Summary values and method rows share one source of truth.
- `js/app_modular.js`: JSON export now includes modular `deltaSummary` values aligned with the visible Delta Summary panel.
- `dashboard_modular.html`: Property labels, panel headings, and tooltips now clarify whether the active curve is `k(T)` or `cp(T)` and that the integral is the selected property over the chosen temperature range.
- `js/app_modular.js`: Integration and energy messaging now explicitly distinguish conductivity-only results from mass-based `cp(T)` energy output.
- `tests/numerics.test.js`: Added deterministic regression fixtures for all four numerical methods using fixed material/range inputs.
- `tests/export.test.js`: Added export consistency checks to ensure CSV/JSON outputs match the same Delta Summary and method-comparison values shown in the UI.
- `tests/materials.validate.js`: Updated validation coverage to the nested v0.4.5 material-property schema used by `materials.json`.

## v0.4.4

### Added

- `dashboard_modular.html`: Added a visible result mode toggle near the Integration Results panel with `Single Method` and `Compare All` options.

### Changed

- `js/app_modular.js`: Added UI-only mode handling to switch panel visibility between selected-method result and full four-method comparison.
- `js/app_modular.js`: CSV export now follows the active mode: single selected method in `Single Method`, all four methods in `Compare All`.

## v0.4.3

### Added

- `dashboard_modular.html`: Added a `Download Plot` button in the Property vs Temperature panel.
- `js/plots.js`: Added `downloadMainPlotPng()` to export the current `mainPlot` as PNG using the visible plot dimensions and a timestamped filename (`cryo_plot_YYYYMMDD_HHMM.png`).

### Changed

- `js/app_modular.js`: Wired `downloadPlotBtn` click handling to the new plot export function.

## v0.4.2

### Added

- `js/app_modular.js`: Added Gauss-Legendre 4-point method to integration method comparison panel.
  All four methods (Trapezoid, Simpson fixed, Romberg, Gauss-Legendre 4-pt) are displayed side-by-side
  with numeric integrals and % deviation from Romberg reference.

### Changed

- `js/app_modular.js`: CSV export extended with Gauss-Legendre 4-pt integral and % vs Romberg row.
- `js/app_modular.js`: JSON export `methodComparison` object extended with `gauss` key.

## v0.4.1

### Added

- `dashboard_modular.html`: Added Integration Method Comparison panel.
- `js/app_modular.js`: Added side-by-side Trapezoid, Simpson fixed, and Romberg integral values with percent difference vs Romberg.

### Changed

- `js/app_modular.js`: Unified numeric formatting for displayed outputs and CSV/JSON exports to ensure exact value consistency.

## v0.3.0

### Added

- Modular production-style structure.
- `data/materials.json` as material source of truth.
- `js/materials.js` for material models.
- `js/numerics.js` for numerical methods.
- `js/state.js` for state, validation, and calculations.
- `js/plots.js` for Plotly rendering.
- `js/export.js` for CSV/JSON/PNG export.
- `js/app.js` for orchestration.
- Documentation folder with engineering handover.

### Preserved from v0.2.0

- Heat-load calculation.
- Tmin/Tmax.
- Method selector.
- Data modes.
- Normalized/absolute comparison.
- Error table.
- Traceability.
- Export functions.

### Known Caveats

- SS316 coefficients are placeholders.
- Smoothed data mode is moving-average based.
