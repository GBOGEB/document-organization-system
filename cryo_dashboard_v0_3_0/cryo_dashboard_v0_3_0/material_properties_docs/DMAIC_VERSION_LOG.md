# DMAIC and Version Log

## DMAIC baseline

### Define

Problem:

```text
The original VBA material-property logic needs to become a portable engineering calculator.
```

Goal:

```text
Create a standalone HTML dashboard for quick review and practical engineering checks, with a future pathway to Python/Streamlit for validated engineering workflows.
```

Constraints:

```text
- HTML must run without Python.
- Users may open it from a local folder, network drive, or static server.
- It must expose equations, coefficients, assumptions, and validation status.
- It must support interval calculations between T1 and T2.
```

### Measure

Inputs:

```text
Material
Property
T1
T2
Integration method
Number of integration intervals / plot points
Area A
Length L
Mass m
Layer definitions
Y-axis controls
```

Outputs:

```text
y(T1)
y(T2)
Delta y
Integral over T1-T2
Integral-average value
Conduction heat leak Qdot
Cooldown/warmup energy E
Layered-wall screening estimate
Validation PASS/WARNING
CSV export
Print/save-as-PDF report
Debug intermediate values
```

### Analyze

Key findings from the session:

```text
1. Single-point lookup is less useful than interval-based engineering calculation.
2. NIST equation form must be visible and implemented correctly.
3. AISI316 cp piecewise behavior must be visible and traceable.
4. HTML is useful as a quick standalone calculator, but not as a full validated engineering platform.
5. Streamlit/Python remains the better route for heavy simulation, Excel integration, batch workflows, and validation pipelines.
6. User review identified UI clarity issues around output labels, integration method, average definition, and piecewise equations.
7. v1.10 added debug mode and validation transparency.
```

### Improve

Version sequence:

```text
v1.0  - Initial static HTML preview.
v1.1  - Interval workflow with T1/T2, integral, average.
v1.2  - Engineering mode: conduction heat leak and cooldown/warmup energy.
v1.3  - HTML vs Streamlit capability explanation.
v1.4  - DMAIC revision and standalone HTML positioning.
v1.5  - Semi-engineering HTML: Simpson concept, layered wall, overlays, PDF/export concept.
v1.6  - Robust standalone rebuild with plain JS and no external dependencies.
v1.7  - Hardcoded material options and fallback/self-test concept.
v1.8  - Validated HTML with self-test and benchmark values.
v1.9  - NIST equation/coefficient visibility and multi-material audit notes.
v1.10 - Debug and validation release candidate: explicit outputs, Simpson/trapezoid equations, debug mode, Y-axis controls, layered wall screening, validation indicators, updated DMAIC log.
```

### Control

Controlled elements:

```text
- Version number and changelog.
- Source VBA retained.
- Equation form displayed in UI.
- Coefficients displayed in UI.
- Valid temperature range displayed in UI.
- Piecewise logic displayed where applicable.
- Integration method displayed and selectable.
- Debug mode exposes intermediate values.
- Same inputs should produce same outputs.
- Review comments become traceable next-version changes.
```

## Next expected version

v1.11 should be created only after review of v1.10.

Likely v1.11 themes:

```text
- Fix any remaining v1.10 UI or numerical issues.
- Improve mobile layout if needed.
- Strengthen layered-wall solver.
- Improve material/property availability messages.
- Add more structured validation tests for each material/property.
- Optionally split JS/data from HTML if moving from prototype to maintainable package.
```

