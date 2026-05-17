# Historical Snapshot Policy — v0.4.9

## Purpose

Distinguish active runtime documentation from historical engineering lineage.

## Active Runtime Documents

These should remain aligned to the active runtime version:

- `README.md`
- `VERSION`
- `package.json`
- `ssot.json`
- active runtime HTML entrypoints
- active RTM and validation documents

## Historical Snapshot Documents

Historical artifacts intentionally preserve prior engineering state.

Examples:

- older handovers
- archived release notes
- frozen session exports
- DMAIC lineage snapshots
- historical PR references

## Required Visual Banner

Historical/frozen artifacts should contain a clear banner such as:

```text
ARCHIVAL SNAPSHOT — Historical Engineering State
```

or:

```text
HISTORICAL RELEASE SNAPSHOT — NOT ACTIVE RUNTIME
```

## Governance Rule

Do not blindly rewrite historical references during active runtime upgrades.

The runtime coherence scanner only validates active runtime/package-facing surfaces.
