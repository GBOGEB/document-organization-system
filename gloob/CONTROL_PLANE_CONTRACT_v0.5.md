# Gloob Control Plane v0.5

## Closed loop

```text
Ask / Act
   ↓
measured registry + graph + exact-SHA timeline telemetry
   ↓
standardised feature matrix
   ↓
PCA PC1 / PC2
   ↓
entity priority ranking
   ↓
changed Atom → affected Entry rebuild plan
   ↓
priority + measured work units → FAST / HEAVY worker plan
   ↓
exact-run JSON receipts
```

## Ask

Read-only bindings expose Entry state, WHERE_USED, provenance, runtime proof and measured priority.

## Act

Actions are fail-closed `PLAN_ONLY`. Rebuild, worker assignment and edition freeze produce deterministic plans/snapshots; no executor mutation is implied.

## Measured telemetry

The feature matrix is derived from repository state, not expert-seeded scores. Entity classes include Books, Entries, Atoms/shared Atoms, edge types and Operators.

Features:

- `structural_degree`
- `scope_size`
- `reuse_count`
- `source_count`
- `runtime_proof_count`
- `promotion_count`
- `operator_count`
- `cross_ref_count`

## PCA

Features are z-standardised. A dependency-free covariance eigensolver emits PC1 and PC2 loadings, scores and explained-variance ratios. PC1 is sign-oriented deterministically and min-max projected to a 0–100 priority rank.

## Feedback

A changed shared Atom fans out through Registry `WHERE_USED`; a local Atom resolves only to its owning Entry. Affected Entries are ordered by measured PCA priority. Worker planning uses the same ranking plus measured structural work units and greedily balances requested capacity across `FAST` and `HEAVY` lanes.

## Runtime receipts

CI emits and uploads:

- `measured-telemetry.json`
- `pca-priority.json`
- `rebuild-shared-authority.json`
- `worker-plan.json`

Each receipt is bound to `GITHUB_SHA` and `GITHUB_RUN_ID`.

## Authority boundary

Runtime/control receipts prove publication-control behaviour only. They do not promote engineering evidence or transfer source authority.

## DoV

1. inherited Book/Registry/Gateway/View tests remain green;
2. v0.5 tests prove measured-only telemetry, PCA, blast radius and PLAN_ONLY worker feedback;
3. exact-head run executes and uploads control receipts;
4. merge only after exact-head PASS;
5. fresh-main contract + Pages PASS before `Control Plane v0.5 CONTROL`.
