# Federation Hub & Cross-Repo SSOT Registry

**Slice:** 05 — Federation SSOT Hub + Pages Recovery · **Added:** 2026-10-26
**Integration model:** cross-link (b) — repos stay separate; this satellite **extends**, and never replaces, the W110 triad SSOT / contract / Zod / SARIF conventions. All changes are **additive and non-destructive**; no governed file in ABACUS / CODEX / cryoplant-project was modified.

---

## 1. What this is

A repo-local index that links `GBOGEB/document-organization-system` (the cryogenic material dashboard satellite) to the rest of the GBOGEB code space **by reference**:

| Role (W110) | Repo |
|---|---|
| Child engineering truth | `GBOGEB/cryoplant-project` (private) |
| DOW consumption analysis | `GBOGEB/ABACUS` |
| KEB semantic-runtime receipts / **registry of record** | `GBOGEB/CODEX` |
| Satellite (this repo) | `GBOGEB/document-organization-system` |

The **registry of record** stays `GBOGEB/CODEX:federation/mip/W110_CANONICAL_SSOT_REGISTRY.*`. This file is a local pointer/index that makes the satellite discoverable and promotable; actual promotion to an ACTIVE satellite entry in CODEX remains a **human-review action**.

## 2. Components

| File | Purpose |
|---|---|
| `federation/registry.json` | Machine-readable cross-repo registry (schema_version `federation-registry/1.0`). |
| `contracts/registry.schema.json` | Dependency-free JSON Schema (draft-07) governing the registry — mirrors the triad `contracts/*.schema.json` convention. |
| `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/tests/registry_contract.test.js` | 8 zero-dependency checks; wired into `npm test` / `test:contract`. |
| `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/federation_hub.html` | Human launcher that renders the registry (live fetch + embedded `file://` fallback). Linked from `ssot_launcher.html`. |
| `docs/deploy/pages.yml.txt` | GitHub Pages deploy workflow, shipped **as text** — the owner copies it to `.github/workflows/pages.yml` (the Abacus GitHub App cannot push under `.github/workflows/`). |

The hub **re-implements no property-evaluation logic** (`evalRational` / `evalProp` stay only in `js/materials.js` and the SSOT viewers) — it only lists and links, so it cannot introduce an evaluator-parity regression.

## 3. Contract & parity gating

`registry_contract.test.js` enforces:

- required top-level keys and `schema_version` / `owner` / `registry_of_record` patterns;
- `local_ssot_pointer` resolves to a real file;
- `repos[]` well-formed, **no duplicates**;
- exactly **one** `is_self` repo and it is this repository (and not `reference_only`);
- every **local** (self-repo) artifact/entry-point path that looks like a concrete file exists on disk (external repo artifacts are reference-only and intentionally not disk-checked);
- all external repos are `reference_only: true` (guards against accidental self-mutation claims).

Run: `npm test` (full) or `npm run test:contract` (contracts only). Current suite: **823 NIST + 5 ssot_contract + 8 registry_contract = 836, all pass.**

## 4. GitHub Pages recovery

**Root cause of the 404:** Pages Source was the legacy **`main:/docs`**, but the dashboard lives under `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/` (outside `/docs`), so every dashboard URL returned HTTP 404.

**Fix:** the workflow in `docs/deploy/pages.yml.txt` assembles a Pages artifact (dashboard subtree + `federation/` + `.nojekyll` + a root redirect to the hub) and deploys it through the GitHub Actions Pages path.

**Two owner actions required to go live** (the Abacus GitHub App cannot push workflow files, so step 1 is manual):

1. Copy the workflow into place and commit it:
   ```bash
   mkdir -p .github/workflows
   cp docs/deploy/pages.yml.txt .github/workflows/pages.yml
   git add .github/workflows/pages.yml && git commit -m "ci: add Pages deploy workflow" && git push
   ```
2. Set **Settings → Pages → Build and deployment → Source = "GitHub Actions"**.

Until that toggle is flipped the site still serves the legacy `/docs` source and the dashboard is **not live**. After flipping it and the workflow run completing, expected URLs:

- Landing (redirect): `https://gbogeb.github.io/document-organization-system/landing.html`
- Federation Hub: `https://gbogeb.github.io/document-organization-system/federation_hub.html`
- SSOT Launcher: `https://gbogeb.github.io/document-organization-system/ssot_launcher.html`
- Slides / Modular / Legacy / Index: same base + respective file name.

## 5. Out of scope / non-blocking

- Triad registry promotion (satellite → ACTIVE in CODEX W110) — human review.
- Security-alert inventory — needs the fine-grained PAT (see `CROSS_REPO_ASSIMILATION_REPORT.md` §9); cryoplant code scanning still disabled.
- `qps_contract_canonicalization` divergence across three repos — consolidation recommended, human review.
