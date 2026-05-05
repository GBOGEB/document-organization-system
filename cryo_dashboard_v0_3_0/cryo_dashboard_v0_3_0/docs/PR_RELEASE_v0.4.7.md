# PR Release Pack - v0.4.7

## Purpose

Use this file as the merge-ready checklist and PR body scaffold for the v0.4.7
release.

## Suggested PR Title

`release(v0.4.7): comparison modes + overlay guardrails + canonical artifact refresh`

## Suggested PR Description

### Summary

This PR promotes the dashboard to v0.4.7 and focuses on comparison UX clarity
and release-canonical alignment.

### Functional Changes

- Added B1 comparison mode selector: `raw`, `normalized`, `split`.
- Added B1N normalized companion panel in split mode.
- Enforced maximum of 4 comparison overlays.
- Prevented duplicate primary-material overlay.
- Comparison selector now keeps all materials visible and disables entries with
  no data for selected property.
- Improved theme toggle visibility with explicit state label
  (`Theme: Light/Dark`).

### Canonical Artifact Updates

- `VERSION` -> `v0.4.7`
- `docs/CHANGELOG.md` -> new `v0.4.7` section
- `README.md` -> updated runtime/version references
- `GIT_TRACKING_MANIFEST.md` -> updated release tag/archive examples and version
- `FILE_INDEX_v0.4.7.md` -> new canonical file index snapshot
- `docs/SESSION_DROPIN_HANDOVER_v0.4.7.md` -> new continuation handover
- `docs/GRAPH_EXPORT_HANDLING_AND_FALLBACK.md` -> updated to v0.4.7 and
  comparison mode behavior

### Validation

- IDE diagnostics: no errors in updated dashboard HTML/JS files.
- Automated tests: could not execute in this environment because `npm` is not
  installed in the active shell.

## Merge Checklist

- [ ] Open dashboard and verify B1 comparison mode switch (`raw`, `normalized`,
  `split`).
- [ ] Verify overlay cap at 4 and status feedback message.
- [ ] Verify disabled selector options for materials without selected-property
  data.
- [ ] Verify no duplicate primary material line in B1 comparison overlays.
- [ ] Verify theme toggle is visible and updates label correctly.
- [ ] Run `npm test` in an environment where Node/npm is available.
- [ ] Confirm `VERSION` and `docs/CHANGELOG.md` are aligned to v0.4.7.
