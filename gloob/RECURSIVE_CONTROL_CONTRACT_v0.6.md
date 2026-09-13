# Gloob Recursive Control v0.6

## Purpose

Close the Gloob control loop by federating prior runtime receipts back into measured telemetry history, recomputing PCA under the current algorithm, detecting PC1 saturation, separating PC2+ residual variance, and focusing workers on entities that remain in IMPROVE.

## Recursive loop

```text
current measured telemetry receipt
        +
prior exact-run receipt artifacts
        |
        v
federated SHA history
        |
        v
recompute PC1..PC4 from each telemetry snapshot
        |
        +--> PC1 drift / saturation
        +--> PC2+ residual energy
        |
        v
CONTROL / IMPROVE classification
        |
        v
PLAN_ONLY residual worker allocation
        |
        v
new exact-run receipts
        +-----------------------------^
```

## Federation

CI reads prior `gloob-control-receipts` artifacts through the repository Actions API, extracts measured telemetry, appends the current run, and deduplicates by `source_commit`.

Historical PCA outputs are not trusted as analysis authority. Every historical measured-telemetry payload is recomputed using the current PCA algorithm so comparisons remain schema-consistent.

## Minimum evidence

At least three distinct source-SHA snapshots are required before an entity can be classified. Fewer snapshots produce `INSUFFICIENT_HISTORY` and no CONTROL promotion.

## PCA saturation

The current model emits PC1 through PC4.

An entity is `pc1_saturated` when its maximum PC1 step over the latest three snapshots is at or below `0.05`.

Saturation alone does not imply CONTROL.

## Residual control

Residual energy is computed from PC2+ component scores weighted by their explained-variance ratios.

The initial governed residual ceiling is `0.70`.

Classification rule:

```text
CONTROL = three-snapshot history
          AND PC1 max step <= 0.05
          AND PC2+ residual <= 0.70

otherwise IMPROVE
```

Thresholds are control-policy parameters, not engineering acceptance criteria.

## Worker concentration

Residual worker planning is `PLAN_ONLY`.

Only `IMPROVE` entities are eligible. They are ordered first by descending PC2+ residual and then by existing measured priority. CONTROL entities are excluded from the active worker queue.

## Authority boundary

Recursive control classifies publication/control-system work only. It does not transfer source authority, promote engineering evidence, or convert runtime proof into engineering acceptance.

## DoV

1. inherited v0.1-v0.5 tests remain green;
2. PC1-PC4 are emitted from measured telemetry;
3. federation obtains at least three distinct `source_commit` snapshots from real receipt artifacts plus the current run;
4. exact-head CI emits `federated-history.json`, `recursive-control.json`, and `residual-worker-plan.json`;
5. exact-head source-SHA binding remains valid;
6. merge only after exact-head PASS;
7. fresh-main repeat must PASS before `Recursive Control v0.6 CONTROL`.
