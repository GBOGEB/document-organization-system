# SSOT Regeneration Pipeline — v0.4.9

## Objective

Ensure all SSOT-facing views derive consistently from canonical runtime truth.

## Canonical Hierarchy

```text
js/materials.js
    ↓
Canonical evaluators
    ↓
ssot.json
    ↓
ssot_launcher.html
index_slides.html
```

## Governance Principle

SSOT-facing artifacts must not implement divergent numerical models.

## Current Validation Layers

- numerics regression tests
- export consistency tests
- materials schema validation
- file index integrity validation
- static entrypoint validation
- version coherence validation

## Future Automation Target

Planned deterministic generation flow:

```text
materials.js + ssot.json
    ↓
Generate embedded metadata
    ↓
Generate launcher/slides datasets
    ↓
Generate static artifacts
    ↓
Run validation gates
```

## Release Guidance

Before release tag creation:

1. npm test
2. validate static entrypoints
3. validate version coherence
4. validate SSOT lineage
5. regenerate release artifacts
6. update RTM
7. create release tag
