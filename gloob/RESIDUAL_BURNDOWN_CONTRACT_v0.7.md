# Gloob Residual Burn-down v0.7

## Purpose

Burn down measured PC2/PC3/PC4 residual pressure without deleting useful semantic structure or manually overriding Recursive Control v0.6.

## Corrective lanes

1. **Telemetry attribution** — publication-wide `entry_ids:["*"]` receipts remain publication/control evidence and are not multiplied into every Entry, Book, or Operator row.
2. **Operator canonicalisation** — publication operators live once in `operators.json`; Entry graphs reference immutable Operator IDs through `operator_refs`.
3. **Semantic decomposition** — the LKT offered-point root remains the decision summary while power-breakdown and evidence-boundary Atoms move to dedicated Entries. Atoms are moved, never copied.
4. **Residual reverse-load** — PC2/PC3/PC4 scores are reverse-loaded through feature contributions to concrete Entries, Atoms, sources, edge types, Operators, cross-Book references, and explicit runtime events.

## PCA population rule

Features are z-standardised **within entity class** before covariance/PCA is composed across the population. BOOK, ENTRY, ATOM, SHARED_ATOM, EDGE_TYPE, and OPERATOR raw cardinalities are not directly comparable. This prevents normal class scale (for example, one publication Operator reused by all Entries) from being treated as a defect.

This is a measurement correction, not a variance-suppression rule. PC1-PC4 remain computed from measured repository telemetry with no expert-seeded scores.

## Reverse-load rule

A residual may only justify a corrective slice when its dominant loading can be mapped back to concrete governed structure. Useful topology is not deleted merely to reduce a PCA score. In particular, cross-Book conformance and shared-authority links remain when semantically required.

## Automatic disposition

Recursive Control v0.6 remains the disposition authority:

- at least three distinct real source-SHA telemetry snapshots are required;
- `PC1 max step <= 0.05` is required for saturation;
- `PC2+ residual <= 0.70` is required for automatic CONTROL under the current policy;
- otherwise the entity remains IMPROVE and appears in the residual worker plan.

No v0.7 code path directly promotes an entity.

## DoV

1. inherited Book/Registry/Gateway/View/Control tests remain green;
2. exact-head runtime emits measured telemetry, recursive control, residual worker plan, and `residual-burndown.json`;
3. federation contains at least three distinct source SHAs with no silent history collapse;
4. the latest three same-model observations are used for saturation;
5. merge only after exact-head PASS;
6. fresh-main Contract and Pages PASS before `Residual Burn-down v0.7 CONTROL`.
