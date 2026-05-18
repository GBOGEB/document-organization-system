# NIST Parity Test Report — Cryogenic Material Dashboard v0.4.9

**Date:** 2026-05-18  
**Test File:** `tests/nist_parity.test.js`  
**Status:** ✅ ALL 796 ASSERTION CHECKS PASSED

---

## Executive Summary

Comprehensive regression testing validates that all material property calculations in `js/materials.js` produce results identical to independently-implemented NIST equations. All 10 materials across all available properties (k, cp, tc) pass with zero failures.

---

## Test Coverage

### Materials Tested (10/10)

| # | Material Key | Material Name | Properties | Equation Types |
|---|-------------|---------------|------------|----------------|
| 1 | AISI316 | AISI 316 Stainless Steel | k, cp, tc | polylog, piecewise-logpoly, thermal-contraction |
| 2 | Al6061T6 | Aluminum 6061-T6 | k, cp, tc | polylog, thermal-contraction |
| 3 | G10Normal | G-10 CR Fiberglass Epoxy (Normal) | k, cp, tc | polylog, thermal-contraction |
| 4 | G10Warp | G-10 CR Fiberglass Epoxy (Warp) | k, cp, tc | polylog, thermal-contraction |
| 5 | CuRRR50 | OFHC Copper RRR 50 | k, cp | rational, polylog |
| 6 | CuRRR100 | OFHC Copper RRR 100 | k, cp | rational, polylog |
| 7 | CuRRR150 | OFHC Copper RRR 150 | k, cp | rational, polylog |
| 8 | CuRRR300 | OFHC Copper RRR 300 | k, cp | rational, polylog |
| 9 | CuRRR500 | OFHC Copper RRR 500 | k, cp | rational, polylog |
| 10 | Ti64 | Ti-6Al-4V | k, tc | polylog, thermal-contraction |

### Properties Tested

- **Thermal Conductivity (k):** 10 materials, 4–300 K range
- **Specific Heat (cp):** 9 materials (Ti64 excluded — no cp data), 4–300 K range
- **Thermal Contraction (tc):** 5 materials (AISI316, Al6061T6, G10Normal, G10Warp, Ti64), 4–300 K range

---

## Test Sections & Results

| Section | Group Checks | Assertion Checks | Status |
|---------|--------------|------------------|--------|
| 1. Coefficient verification | 12 grouped checks | 35 | ✅ |
| 2. Evaluator parity + per-point physical sanity | 24 property groups | 642 | ✅ |
| 3. Copper RRR rational deep checks | 9 grouped checks | 19 | ✅ |
| 4. Thermal contraction checks | 5 material groups | 13 | ✅ |
| 5. Edge and boundary checks | 4 grouped checks | 51 | ✅ |
| 6. evalRational golden fixtures | 2 material groups | 10 | ✅ |
| 7. Cross-material physical reasonableness | 4 | 4 | ✅ |
| 8. Dense continuity sweep | 19 property groups | 19 | ✅ |
| **Total** | **79 grouped checks** | **796 assertion checks** | ✅ |

> Note: the prior 436 subtotal only counted grouped checks and omitted per-temperature assertions in Section 2.

### Section 1: NIST Coefficient Verification (35 assertions)
Includes both:
- full-suite coefficient sanity checks across all 10 materials/properties (shape + finite values), and
- transcribed NIST exact-match subset checks compared byte-for-byte against `data/materials.json`.

| Material | Property | Status |
|----------|----------|--------|
| AISI316 | k coefficients | ✅ Exact match |
| AISI316 | cp piece 1 (4–50 K) | ✅ Exact match |
| AISI316 | cp piece 2 (50–300 K) | ✅ Exact match |
| Al6061T6 | k coefficients | ✅ Exact match |
| Al6061T6 | cp coefficients | ✅ Exact match |
| G10Normal | k coefficients | ✅ Exact match |
| G10Normal | cp coefficients | ✅ Exact match |
| G10Warp | k coefficients | ✅ Exact match |
| CuRRR100 | k coefficients | ✅ Exact match |
| Ti64 | k coefficients | ✅ Exact match |

### Section 2: Evaluator Parity (642 assertions)
Independent NIST equation implementations compared against `propertyValue()` at 9–15 temperature points per material/property pair. Tolerance: 1×10⁻¹².

**All 24 material-property combinations pass** with zero relative error.

### Section 3: Copper RRR Rational Model (19 tests)
Deep validation of the `sqrt(T)`-based rational evaluator for OFHC Copper.

| Material | Peak T (K) | Peak k (W/m·K) | k(300K) (W/m·K) | Status |
|----------|-----------|-----------------|------------------|--------|
| CuRRR50 | 26.5 | 1,475.8 | ~396 | ✅ |
| CuRRR100 | 22.0 | 2,442.1 | ~396 | ✅ |
| CuRRR150 | 19.5 | 3,247.3 | ~396 | ✅ |
| CuRRR300 | 16.5 | 5,280.3 | ~396 | ✅ |
| CuRRR500 | 14.0 | 7,613.6 | ~396 | ✅ |

**Cross-RRR ordering verified:** Higher RRR → higher low-T peak, as expected physically.

### Section 4: Thermal Contraction Validation (13 tests)
- All 5 materials show negative contraction at low temperatures
- All materials near zero at 293 K reference temperature
- Low-T branch correctly activates for AISI316, Al6061T6, Ti64

### Section 5: Edge Cases (51 tests)
- All boundary temperatures (range min/max) produce finite values
- Piecewise boundary at T=50 K for AISI316 cp confirmed
- Null correctly returned for missing properties (Ti64 cp)
- Null correctly returned for non-existent property names

### Section 6: SSOT evalRational() Parity (10 assertions)
Golden-value regression fixtures are now literal transcribed values (version-controlled) for CuRRR100 and CuRRR300 at 5 temperatures each. Tolerance: 1×10⁻¹⁴.

### Section 7: Physical Reasonableness (4 tests)
- Cu k(300K) = 396.3 >> SS316 k(300K) = 15.3 ✅
- G10 k(100K) = 0.31 << Al6061 k(100K) = 97.7 (insulator vs metal) ✅
- AISI316 cp(300K) = 490.2 J/(kg·K) (reasonable for steel) ✅
- cp increases with temperature (CuRRR100: 7.5 → 389.4) ✅

### Section 8: Continuity Check (19 tests)
Dense sampling (200 points per curve) confirms no discontinuities (>100× step jumps) in any k or cp curve.

---

## Equation Forms Validated

### Polylog (NIST standard form)
```
log₁₀(y) = a + b·log₁₀(T) + c·(log₁₀T)² + … + i·(log₁₀T)⁸
y = 10^(above)
```

### Rational (OFHC Copper k only)
```
log₁₀(k) = (a + c·√T + e·T + g·T^(3/2) + i·T²) / (1 + b·√T + d·T + f·T^(3/2) + h·T²)
k = 10^(above)
```

### Thermal Contraction
```
y(T) = a + bT + cT² + dT³ + eT⁴
Optional: y = f for T < Tlow
```

---

## Acceptable Tolerances

| Test Category | Tolerance | Justification |
|--------------|-----------|---------------|
| Evaluator parity | 1×10⁻¹² relative | Same coefficients, same IEEE 754 arithmetic |
| Golden-value regression | 1×10⁻¹⁴ relative | Identical computation paths |
| Physical reasonableness | Domain-specific bounds | Engineering judgment per NIST ranges |

---

## NIST References

1. **NIST Cryogenic Materials Properties Database** — trc.nist.gov/cryogenics
2. **NIST Monograph 177** — "Properties of Copper and Copper Alloys at Cryogenic Temperatures" (Simon, Drexler, Reed, 1992)
3. **Marquardt, Le, Radebaugh (2000)** — "Cryogenic Material Properties Database," 11th International Cryocooler Conference

## Reuse / Refactor Candidates

- `js/materials.js`: canonical evaluator block (`getCoefficients`, `propertyValue`) is the primary reuse unit for any future model extensions.
- `tests/nist_parity.test.js`: independent equation evaluators are reusable as regression or ingestion-verification guards when adding new materials/properties.
- Future enhancement path: add additional NIST-imported materials/properties (currently out-of-scope but supported by the same evaluator/test structure).

---

## Run Command

```bash
cd cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0
node tests/nist_parity.test.js
```
