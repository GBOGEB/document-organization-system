# Gloob Control Surveillance Contract v0.9

## Purpose

CONTROL is a guarded operating state, not a target that must continuously move toward the current PCA population mean.

The surveillance layer therefore separates three states:

- `STABLE_CONTROL`: the entity has an established qualifying telemetry epoch and its own measured telemetry remains unchanged.
- `REQUALIFY`: the entity's own telemetry changed and a new exact-SHA epoch is accumulating evidence. Work is not reopened yet.
- `ESCALATE`: the changed telemetry epoch has accumulated the minimum qualification window without establishing CONTROL. Only this state reopens worker work.

## Qualification

The policy file `control/surveillance-policy.json` declares the current publication-control thresholds:

- minimum telemetry-epoch snapshots: 3;
- PC1 maximum step: 0.05;
- PC2+ residual ceiling: 0.70.

These are configurable control-policy thresholds, not engineering acceptance criteria.

## Residual-PC discovery

PC3 and PC4 are discovery surfaces, not optimization targets by default.

Discovery requires both:

1. a real change to the entity's measured telemetry epoch; and
2. a material increase in PC3 or PC4 weighted energy relative to the snapshot immediately before that epoch.

The default v0.9 materiality policy is an absolute weighted-energy increase of at least 0.05 and a relative increase of at least 25%. Discovery output is `DISCOVER_ONLY`; it does not itself reopen worker work.

## Worker boundary

`control-escalation-plan.json` may assign only `ESCALATE` entities. `REQUALIFY` and `STABLE_CONTROL` entities are excluded.

This preserves the sequence:

```text
CONTROL
  -> own telemetry unchanged -> STABLE_CONTROL
  -> own telemetry changed   -> REQUALIFY
                               -> qualifying epoch -> STABLE_CONTROL
                               -> failed epoch     -> ESCALATE -> worker plan

changed epoch + material PC3/PC4 increase
  -> residual discovery receipt
  -> no automatic mutation
```

## CI outputs

Every governed run emits:

- `control-surveillance.json`
- `residual-discovery.json`
- `control-escalation-plan.json`

On the controlled no-change baseline CI requires zero `REQUALIFY`, zero `ESCALATE`, zero residual discoveries, and an empty escalation worker plan.
