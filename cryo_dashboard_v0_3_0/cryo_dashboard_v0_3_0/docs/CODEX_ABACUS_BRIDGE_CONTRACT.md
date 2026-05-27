# CODEX / ABACUS Bridge Contract

## Purpose

This dashboard repository is the canonical UI/runtime and source-artifact producer for the cryogenic material dashboard. `/CODEX` and `/ABACUS` must integrate through published artifacts instead of duplicating dashboard state.

## System roles

- **This repository**: canonical dashboard runtime, artifact packaging source, and validation gate owner.
- **`/CODEX`**: integration/control layer and PR-lineage consumer.
- **`/ABACUS`**: downstream analytics consumer and optional release-metadata acknowledger.

## Canonical source surfaces

- Primary runtime: `dashboard_modular.html`
- Runtime orchestrator: `js/app_modular.js`
- Machine-readable artifact indexes: `file_index.yaml`, `file_index.json`
- Bridge manifest: `bridge_manifest.json`
- Material dataset: `data/materials.json`

## Minimal bridge payload

Every bridge handoff must carry:

- dashboard release version
- artifact paths
- material dataset identity
- validation status
- release timestamp

## `/CODEX` contract

`/CODEX` must ingest published dashboard artifacts from `file_index.json` and `bridge_manifest.json`.

Required inputs:

- release version from `VERSION`
- artifact path set from `file_index.json`
- runtime entrypoint (`dashboard_modular.html` + `js/app_modular.js`)
- materials dataset identity from `data/materials.json`
- validation gate status from `npm test`
- release timestamp from `bridge_manifest.json`

`/CODEX` must not:

- duplicate dashboard runtime state
- become a source of truth for materials data
- redefine release metadata outside published artifacts

## `/ABACUS` contract

`/ABACUS` must consume published outputs and validation evidence only.

Allowed consumption:

- release metadata from `bridge_manifest.json`
- artifact paths from `file_index.json`
- materials dataset identity from `data/materials.json`
- downstream-ready outputs generated from published dashboard artifacts

`/ABACUS` may publish back:

- analytics summaries
- synchronized release acknowledgements

`/ABACUS` must not:

- mutate runtime files
- become a second source of truth for materials, runtime, or release state
- consume unpublished internal dashboard structure

## Validation gate

Bridge publication is only valid after this command passes in the dashboard subtree:

```bash
cd /tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0
npm test
```

## Handoff order

1. Update source artifacts in this repository.
2. Refresh `bridge_manifest.json`.
3. Run `npm test`.
4. Publish the handoff to `/CODEX`.
5. Allow `/ABACUS` to consume only the published bridge payload.
