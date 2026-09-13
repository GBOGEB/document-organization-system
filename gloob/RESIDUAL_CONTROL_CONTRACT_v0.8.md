# Gloob Residual Control Contract v0.8

## Purpose

Residual CONTROL is a longitudinal state, not a cross-sectional distance-to-mean label.
PCA axes may rotate when unrelated Books, Entries, Atoms, edge types or operators are added or decomposed. An entity that has already demonstrated a qualifying CONTROL window therefore remains CONTROL while its own measured telemetry vector is unchanged.

## Qualification policy

An entity starts a new telemetry epoch whenever its own measured feature vector changes.
Within that epoch, CONTROL requires at least three distinct exact-source-SHA snapshots in which:

- PC1 maximum step is no greater than 0.05; and
- PC2+ residual is no greater than 0.70.

Once such a window has been observed, CONTROL is sticky for the remainder of that unchanged telemetry epoch. A later PCA rotation caused only by changes elsewhere does not demote the entity. Any change to the entity's own telemetry starts a new qualification epoch and returns it to IMPROVE until the three-snapshot rule is satisfied again.

## W119 corrective slices

The second residual burn-down pulse executes two source-preserving semantic decompositions:

1. `ENTRY-LKT-INVCOP` retains the invCOP decision and invCOP metric, while `ATOM-LKT-QEQ` and `ATOM-LKT-POWER` move to `ENTRY-LKT-PERFORMANCE-POINT`.
2. `ENTRY-LKT-EVIDENCE-BOUNDARY` retains the canonical engineering/SAT boundary, while the CODEX runtime-receipt authority moves to `ENTRY-LKT-RUNTIME-RECEIPT`.

Atoms are moved, not copied. Source authority remains unchanged. `DECOMPOSES_TO` records the hierarchy and both publication operators continue to be referenced from the canonical operator catalog.

## First observed qualifying snapshot

Exact source SHA `e363ef84d0263a74d347f4ad59a28dab3507906f`, run `34752922857`, produced the first W119 telemetry-epoch observation. The changed residual surfaces were all below the 0.70 ceiling but remained IMPROVE with qualification count 1, as required.

Representative residuals:

- `EDGE-TYPE-DECOMPOSES_TO`: 0.650770
- `ENTRY-LKT-INVCOP`: 0.567870
- `ENTRY-LKT-RUNTIME-RECEIPT`: 0.545138
- `ENTRY-LKT-EVIDENCE-BOUNDARY`: 0.481863
- `EDGE-TYPE-CONTAINS`: 0.451572
- `EDGE-TYPE-TRANSFORMED_BY`: 0.451572
- `ENTRY-LKT-PERFORMANCE-POINT`: 0.432846

No promotion is declared from this single snapshot.
