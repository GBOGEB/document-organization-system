# Cross-Repo SSOT Pointer — document-organization-system

> Repo-local SSOT pointer for the GBOGEB multi-repo federation.
> Machine-readable companion: [`CROSS_REPO_SSOT_POINTER.json`](./CROSS_REPO_SSOT_POINTER.json)

## Why this file exists

The federation's cross-repo registry of record is
`GBOGEB/CODEX:federation/mip/W110_CANONICAL_SSOT_REGISTRY` (JSON + Markdown +
`.zod.ts`). Its disposition for smaller repositories is:

```
DEFER_FOR_SMALL_REPOS_UNTIL_REPO_LOCAL_SSOT_POINTERS_EXIST
```

This file **is** that repo-local SSOT pointer for
`GBOGEB/document-organization-system`, making the repository eligible for
promotion from `DEFER` to an active satellite entry in the triad registry. It is
**additive and non-destructive**: it does not modify the triad registry. Actual
registry promotion remains a human-review action (see the cross-repo
assimilation report).

## Canonical SSOT artifact

| Item | Path |
|------|------|
| SSOT | `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/ssot.json` |
| JSON-Schema contract | `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/contracts/ssot.schema.json` |
| Zod contract mirror | `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/contracts/ssot.zod.ts` |
| Contract test (zero-dep) | `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/tests/ssot_contract.test.js` |
| NIST parity evidence | `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/tests/nist_parity.test.js` |
| SARIF exporter | `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/scripts/nist_sarif_export.mjs` |

## Triad authority boundary (reference only)

| Role | Repo |
|------|------|
| Child engineering truth | `GBOGEB/cryoplant-project` |
| DOW consumption analysis | `GBOGEB/ABACUS` |
| KEB semantic-runtime receipts | `GBOGEB/CODEX` |
| This satellite | `GBOGEB/document-organization-system` (cryo material dashboard) |

## Integration model

Cross-linking (model **b**): repositories stay separate. The dashboard SSOT
**extends** — it does not replace — the existing SSOT / contract / Zod / SARIF
conventions of the triad.
