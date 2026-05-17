# SSOT Regeneration Pipeline — v0.4.9

## Objective

Formalize deterministic regeneration around `ssot.json` and `data/materials.json`.

## Canonical Inputs

- `ssot.json`
- `data/materials.json`
- `file_index.json`
- `file_index.yaml`

## Reviewable Outputs

- `ssot_launcher.html`
- `index_slides.html`
- `files.html`
- RTM documentation

## Required Validation Gates

```bash
npm test
npm run validate:version
npm run validate:static
npm run ssot:plan
```

## Future TODO

- template-driven SSOT HTML generation
- snapshot diff validation
- generated artifact CI uploads
- schema validation for ssot.json
