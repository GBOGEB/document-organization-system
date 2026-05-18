# Cryogenic Dashboard v0.4.9 — Recursive Engineering Handover

This handover consolidates the uploaded ZIP review, SSOT validation, stale-item analysis, version-coherence audit, recursive TODO mapping, and canonical repository interpretation.

## Canonical Interpretation

Canonical runtime/tool repository:
- `GBOGEB/document-organization-system`

Supplemental/development repository:
- `GBOGEB/CODEX`

Canonical dashboard subtree:
- `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/`

## Key Findings

- SSOT integration is already largely merged through prior PR lineage.
- Active runtime metadata still contains mixed v0.4.6/v0.4.7/v0.4.8 references.
- Historical release files should not be blanket-rewritten.
- `package.json` required alignment to v0.4.9.
- Runtime/static entrypoints remain:
  - `index.html`
  - `files.html`
  - `dashboard_modular.html`
  - `ssot_launcher.html`
  - `index_slides.html`

## Validation State

Prior local validation pass:

```text
All numerics tests passed.
All export consistency tests passed.
Material database validation passed.
```

A previous PR discussion referenced a floating-point tolerance assertion drift in CI. That should be reviewed independently from this metadata coherence pass.

## Stale Item Classification

Three groups were identified:

1. Active coherence items (should generally align to v0.4.9)
2. Historical snapshots (should usually remain frozen)
3. Future-check/legacy references requiring human review

## Recommended Next Steps

| Priority | Action |
|---|---|
| P0 | Align active package-facing version markers to v0.4.9 |
| P0 | Re-run `npm test` on branch and after merge |
| P1 | Preserve historical v0.4.6/v0.4.7/v0.4.8 handovers as archival snapshots |
| P1 | Decide long-term role of duplicate `cryo_dashboard_ssot/` export bundle |
| P1 | Add automated version-coherence scanner |
| P2 | Create final v0.4.9 release tag after merge |

## Cross-Repo Policy

### document-organization-system

Canonical for:
- Runtime dashboard
- GitHub Pages deployment
- Materials database
- JS modules and tests
- Release metadata
- Changelogs and handovers

### CODEX

Supplemental for:
- Recursive engineering handover
- Agent/development notes
- Delta maps
- Automation workflows

CODEX should not silently become the runtime source of truth.

## Branches Created During Session

- `codex/cryo-v0.4.9-session-handover` in `GBOGEB/document-organization-system`
- `codex/cryo-v0.4.9-session-handover` in `GBOGEB/CODEX`

## Full Artifact Pack

The exhaustive local handover bundle additionally contains:
- recursive stale-item register
- CODEX ↔ canonical delta map
- static standalone HTML handover
- expanded TODO/RTM structure

## SSOT System — Post-Merge Fix (2026-05-18)

### PR #16 Status
- **Merged**: 2026-05-15T02:13:14Z into `main`
- **Title**: `release(v0.4.9): SSOT Integration — Canonical Data, Reveal.js Presentation, Launcher Hub`
- **Review feedback addressed**: Copilot PR reviewer identified `evalRational()` bug in both `ssot_launcher.html` and `index_slides.html`

### Bug Fix: evalRational() Alignment

**Problem**: The SSOT presentation files used a `log10(T)`-based polynomial ratio with 8 coefficients for the rational evaluator, but the dashboard's canonical `js/materials.js` uses a **sqrt(T)-based** form with **9 coefficients** `[a..i]`:

```
log₁₀(k) = (a + c·√T + e·T + g·T^(3/2) + i·T²) / (1 + b·√T + d·T + f·T^(3/2) + h·T²)
```

**Impact**: All Copper RRR k(T) traces in slides and launcher were rendering incorrect curves.

**Fix applied** (PR branch `fix/ssot-rational-evaluator-and-docs`):
- `ssot_launcher.html` — `evalRational()` rewritten to match `js/materials.js rational()`
- `index_slides.html` — `evalRational()` rewritten to match `js/materials.js rational()`
- `ssot.json` — Added full `data_lineage` section with 6-step traceability chain from NIST source → rendered plots
- `ssot.json` — Added `rational_model_specification` with canonical source reference

### NIST Data Lineage (New in ssot.json)

Full traceability chain documented:
1. NIST Monograph 177 / Cryogenic Material Properties DB → published coefficients
2. `js/materials.js` coefficient arrays → hardcoded verbatim from NIST
3. `js/materials.js` evaluator functions → canonical `logpoly()`, `rational()`, `evalProperty()`
4. `ssot.json` material catalog → metadata summary (references js/materials.js as authority)
5. SSOT presentation views → embed MDATA with aligned evaluators
6. Rendered Plotly charts → point-by-point traces from aligned evaluators

### SSOT File Inventory

| File | Role | Status |
|------|------|--------|
| `ssot.json` | Canonical metadata + lineage | ✅ Updated with data_lineage |
| `ssot_launcher.html` | Navigation hub with live charts | ✅ evalRational() fixed |
| `index_slides.html` | 15-slide Reveal.js presentation | ✅ evalRational() fixed |

### Remaining Open Items

| Priority | Item | Status |
|----------|------|--------|
| P1 | Create v0.4.9 release tag after merge | Pending |
| P1 | Broader NIST equation parity regression tests | Gap documented in ssot.json |
| P2 | Method tolerance band tests | Gap documented |
| P2 | Automated version-coherence scanner | Recommended |

End of handover.
