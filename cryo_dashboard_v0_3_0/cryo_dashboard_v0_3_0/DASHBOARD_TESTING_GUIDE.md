<!-- markdownlint-disable MD009 MD022 MD026 MD031 MD032 MD060 -->

# Dashboard Modular v0.4.7 - Testing Guide

## Spot-Check Reference Values

Use these to quickly verify the dashboard is computing correctly. Settings:
select the material and property, set T1/T2 as shown, 100 integration steps,
Romberg method.

| Material | Property | T1 (K) | T2 (K) | Expected ∫ (Romberg) | Trapezoid (~) | Units |
|---|---|---|---|---|---|---|
| AISI316 | k | 20 | 300 | **3 012.150** | 3 012.080 | W/m |
| AISI316 | cp | 20 | 300 | **93 190.19** | 93 189.95 | J/kg |
| CuRRR100 | k | 4 | 300 | **194 330.57** | 194 228.84 | W/m |

> Values are the authoritative regression fixtures from
> `tests/numerics.test.js`. Romberg and Gauss-Legendre agree to < 0.001%.
> Trapezoid error ~0.05% on smooth curves, ~0.05–0.5% for peaked CuRRR k(T). If
> your result deviates > 0.5% from the Romberg column, the computation is
> incorrect — check browser console for errors.



### 1. Fixed Module Import Issues
- **File**: `dashboard_modular.html`
- **Change**: Updated import from `./js/app.js` to `./js/app_modular.js`
- **Reason**: The original `app.js` was designed for the full tabbed interface
  with HTML element IDs that don't exist in `dashboard_modular.html`

### 2. Created New App Entry Point
- **File**: `js/app_modular.js` (NEW)
- **Purpose**: Dedicated entry point for the simple modular dashboard
- **Features**:
  - Material selection dropdown population
  - Property selector (k/cp)
  - Temperature range controls (Tmin, Tmax, nsteps)
  - All 4 integration methods: Trapezoid, Simpson's 1/3, Romberg, Gauss-Legendre
    4-pt
  - Mass input for energy calculations
  - Interactive Plotly plots (main plot + integration plot)
  - Evaluation table
  - Integration results display
  - Energy results display
  - CSV/JSON export functionality
  - Debug panel
  - Theme toggle support

### 3. Added Missing Integration Methods
- **File**: `js/numerics.js`
- **Added**: `rombergIntegration()` and `gaussLegendre4()` functions
- **Reason**: These methods were listed in the HTML dropdown but not implemented

### 4. Removed Unused Imports
- **File**: `js/app_modular.js`
- **Change**: Removed unused import of `exportCsv` and `exportJson` from
  `./export.js`
- **Reason**: Export behavior is centralized in `js/export.js` and exercised via
  consistency tests.

### 5. Added Export Consistency Validation
- **Files**: `js/export.js`, `tests/export.test.js`
- **Change**: Centralized modular CSV/JSON export payload generation and added
  checks that exported Delta Summary and method-comparison values stay aligned.
- **Reason**: CSV/JSON outputs now prove the same values shown in the UI.

### 6. Clarified k(T) vs cp(T) Labels
- **Files**: `dashboard_modular.html`, `js/app_modular.js`
- **Change**: Tightened labels, tooltips, and result messaging so the active
  property clearly indicates `k(T)` or `cp(T)`.
- **Reason**: Reduce ambiguity in engineering interpretation without changing
  calculations.

## Manual Testing Instructions

### Step 1: Start Local HTTP Server
Since the dashboard uses ES6 modules, it must be served via HTTP (not file://)

**Option A - Using Python:**
```bash
python -m http.server 8000
```

**Option B - Using the batch file:**
```bash
start_server.bat
```

**Option C - Using Node.js (if installed):**
```bash
npx http-server -p 8000
```

### Step 2: Open Dashboard in Browser
Navigate to: `http://localhost:8000/dashboard_modular.html`

### Step 3: Test Each Integration Method

#### Test 1: Trapezoid Method
1. Select Material: `copper` (or any material)
2. Select Property: `k` (thermal conductivity)
3. Set Temperature Range: `Tmin = 4`, `Tmax = 300`, `nsteps = 100`
4. Select Integration Method: `Trapezoid`
5. Mass: `1` kg
6. Click **Calculate**
7. **Expected Results**:
   - Main plot shows thermal conductivity vs temperature curve
   - Evaluation table shows T and k values
   - Integration results display the integral value
   - Energy results show Q values
   - Integration plot shows cumulative integral
   - Debug panel shows calculation details

#### Test 2: Simpson's 1/3 Method
1. Keep same settings as Test 1
2. Change Integration Method to: `Simpson's 1/3`
3. Click **Calculate**
4. **Expected Results**: Similar to Test 1 but integral value may differ
   slightly due to different numerical method

#### Test 3: Romberg Integration
1. Keep same settings
2. Change Integration Method to: `Romberg`
3. Click **Calculate**
4. **Expected Results**: Higher accuracy integral value (typically more accurate
   than trapezoid/simpson for smooth functions)

#### Test 4: Gauss-Legendre 4-point
1. Keep same settings
2. Change Integration Method to: `Gauss-Legendre 4-pt`
3. Click **Calculate**
4. **Expected Results**: High accuracy integral value using Gaussian quadrature

#### Test 5: Specific Heat (cp)
1. Select Property: `cp` (specific heat)
2. Select Material: `helium` (or any material)
3. Temperature Range: `Tmin = 4`, `Tmax = 300`, `nsteps = 100`
4. Any integration method
5. Click **Calculate**
6. **Expected Results**:
   - Plot shows specific heat vs temperature
   - Y-axis label: "cp (J/kg·K)"
   - Integration units: J/kg

### Step 4: Test Export Functionality

#### Export CSV
1. After calculating, click **Export CSV**
2. **Expected**: Downloads a CSV file with format
   `{material}_{property}_{Tmin}-{Tmax}K.csv`
3. **Content**: Should contain Delta Summary rows (`delta_k`, `integral_k`) plus
   either the selected integral row or the Compare All method rows before the
   temperature/value table

#### Export JSON
1. After calculating, click **Export JSON**
2. **Expected**: Downloads a JSON file with format
   `{material}_{property}_{Tmin}-{Tmax}K.json`
3. **Content**: Should contain metadata, `deltaSummary`, `selectedIntegral`,
   `methodComparison`, and the temperature/value data array

#### Export Consistency Check
1. Run a calculation in `Single Method`
2. Confirm the Delta Summary values shown in the UI match the CSV `delta_k` and
   `integral_k` rows and the JSON `deltaSummary` values
3. Switch to `Compare All`
4. Confirm each CSV method row and `% vs Romberg` row matches the JSON
   `methodComparison` object

### Step 5: Test Theme Toggle
1. Click the theme icon (🌙/☀️) in the top-right corner
2. **Expected**: Dashboard switches between light and dark modes
3. Refresh page - theme should persist

### Step 6: Test Navigation
1. Click "← Back to Home" link
2. **Expected**: Returns to `index.html` (main landing page)

## Expected Console Output (No Errors)
Open browser DevTools (F12) → Console tab
- Should see no errors
- May see informational messages about Plotly initialization

## Automated Validation

### Primary Test Command

```bash
npm test
```

Current expected scope:
- `tests/numerics.test.js`
- `tests/export.test.js`
- `tests/materials.validate.js`

### Portable Node.js Workaround

If machine-wide Node.js installation is blocked, use the portable local test
workflow documented in `docs/BASELINE_VERIFICATION_v0.4.5.md`.

## Known Working Configurations

### Materials with k property:
- copper
- aluminum
- stainless_steel_304
- titanium
- g10
- polyimide

### Materials with both k and cp:
- helium
- nitrogen
- neon
- hydrogen

## Troubleshooting

### Error: "Cannot find module"
- **Cause**: Not running via HTTP server (opened as file://)
- **Solution**: Use `python -m http.server 8000`

### Error: "Failed to fetch"
- **Cause**: File paths incorrect or server not serving from correct directory
- **Solution**: Ensure server is started from the project root directory

### Blank plots
- **Cause**: Plotly.js not loaded or JavaScript error
- **Solution**: Check browser console for errors

### "Calculate" button does nothing
- **Cause**: JavaScript error preventing initApp from running
- **Solution**: Check browser console for errors

### Integration method returns 0 or NaN
- **Cause**: Material doesn't have the selected property, or temperature range
  is invalid
- **Solution**: Verify material has the property (check data/materials.json)

## Files Modified/Created

### Created:
- `js/app_modular.js` (240 lines) - New modular dashboard entry point
- `DASHBOARD_TESTING_GUIDE.md` (this file)
- `tests/export.test.js` - Export consistency validation for Delta Summary and
  Compare All rows

### Modified:
- `dashboard_modular.html` - Updated import to use app_modular.js
- `js/numerics.js` - Added rombergIntegration() and gaussLegendre4()
- `js/export.js` - Centralized modular export payload generation for CSV/JSON
  consistency
- `start_server.bat` - Updated to show server status

### Not Modified (by design):
- `js/app.js` - Remains for the full tabbed dashboard
- `js/state.js` - Used by full dashboard, not by modular dashboard
- `js/plots.js` - Used by full dashboard, not by modular dashboard

## Comparison: app.js vs app_modular.js

| Feature | app.js (Full Dashboard) | app_modular.js (Modular) |
|---------|------------------------|--------------------------|
| Target HTML | Complex tabbed interface | Simple single-panel layout |
| Required IDs | cursorT, areaInput, lengthInput, dataMode, comparisonMode | materialSelect, propertySelect, Tmin, Tmax, nsteps, integrationMethod |
| State Management | Uses state.js computeMaterialState() | Direct calculation inline |
| Plotting | Uses plots.js module | Inline Plotly calls |
| Export | Uses export.js module | Uses export.js modular builders via app integration |
| Integration Methods | 3 methods via state.js | 4 methods directly implemented |
| Complexity | ~300 lines + dependencies | 240 lines standalone |

## Baseline Reference

- `docs/BASELINE_VERIFICATION_v0.4.5.md` records the current manual smoke
  checks, exact `npm test` output, and the portable Node.js test helper used in
  this environment.

## Integration Method Accuracy Comparison

For smooth functions like thermal conductivity:
1. **Gauss-Legendre 4-pt** - Highest accuracy (7th degree polynomial exact)
2. **Romberg** - Very high accuracy (Richardson extrapolation)
3. **Simpson's 1/3** - Good accuracy (3rd degree polynomial exact)
4. **Trapezoid** - Baseline accuracy (linear interpolation)

For the same temperature range and nsteps, all methods should give similar
results (within 1-2%), with Gauss and Romberg typically being most accurate.
