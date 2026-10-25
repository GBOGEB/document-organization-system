# Contracts — Cryogenic Material Dashboard SSOT

This directory holds the schema contracts for `../ssot.json`, following the
contract-per-SSOT-artifact convention used across the GBOGEB triad
(`GBOGEB/CODEX`, `GBOGEB/cryoplant-project`, `GBOGEB/ABACUS`).

| File | Role | Runtime dependency |
|------|------|--------------------|
| `ssot.schema.json` | **Authoritative** JSON Schema (draft-07) contract for `ssot.json` | none |
| `ssot.zod.ts` | Zod mirror for parity with the triad's `.zod.ts` tooling | `zod` (dev only) |

## Enforcement

`ssot.schema.json` is enforced by `../tests/ssot_contract.test.js`, which runs in
the existing **zero-dependency** Node test harness (`node:test` + `node:assert`)
and is wired into `npm test`. It checks:

- required top-level keys and `ssot_meta` shape (incl. `canonical_source` = a `GBOGEB/` repo);
- `materials.count` equals `materials.catalog.length`;
- **version coherence**: `ssot_meta.dashboard_version` is the maximum entry in
  `project.version_lineage`, and there are no duplicate version entries — a guard
  against the stale-version / bulk-replace regression class.

The Zod mirror (`ssot.zod.ts`) is intentionally **not** wired into `npm test`
to keep this repo dependency-free; validate it only in a project that already
depends on `zod` (`npm i -D zod`).

## SARIF

`../scripts/nist_sarif_export.mjs` emits SARIF 2.1.0 for the NIST parity and SSOT
contract suites so the dashboard's test evidence can be uploaded to GitHub code
scanning via `actions/upload-sarif`, matching the triad's SARIF convention.
