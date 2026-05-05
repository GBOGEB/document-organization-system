# GitHub Pages Publish Guide (Hosted-First)

## Goal

Publish the dashboard so users open links directly (no localhost requirement), while preserving a clean recursive/idempotent evolution path.

## Runtime Truth

- Works by double-click (`file://`):
  - `index.html`
  - `files.html`
  - `html_preview_hub.html`
  - `material_properties_dashboard_v1_10.html`
- Requires HTTP context (hosted HTTPS or local HTTP):
  - `dashboard_modular.html` (ES modules + JSON fetch)

GitHub Pages provides HTTPS, so `dashboard_modular.html` works directly when hosted.

## Recommended Publish Layout

Keep this folder as the canonical site root:

- `index.html`
- `files.html`
- `dashboard_modular.html`
- `material_properties_dashboard_v1_10.html`
- `html_preview_hub.html`
- `data/`
- `js/`
- `style.css`
- `docs/` (reference docs)

## GitHub Pages Setup

1. Push branch with current canonical artifacts.
2. In GitHub repo settings: `Pages`.
3. Source: deploy from branch.
4. Branch: choose your publish branch.
5. Folder: `/` rooted at this project folder (or use a dedicated pages branch containing this folder content).
6. Save and wait for Pages URL.
7. Verify links:
   - `index.html`
   - `files.html`
   - `dashboard_modular.html`

## Canonical Link Validation Rule

Before each release:

- Validate every `href` in `files.html` exists in the project root tree.
- Confirm `docs/CHANGELOG.md` top entry matches release version.
- Confirm `VERSION` matches release tag.

## Deprecate / Prune Guidance

Keep in canonical release:

- Runtime core: `index.html`, `files.html`, `dashboard_modular.html`, `material_properties_dashboard_v1_10.html`, `html_preview_hub.html`
- Runtime dependencies: `js/`, `data/`, `style.css`
- Control docs: `README.md`, `docs/CHANGELOG.md`, `visual_key.yaml`, `GIT_TRACKING_MANIFEST.md`

Move out of publish payload (archive-only):

- `archive_20260427/`
- `extracted_*` folders
- `.venv/`
- temporary/bundle artifacts: `*.zip`, `bash.exe.stackdump`, `_validate_tmp.py`

## Suggested Recursive Release Pattern

- `release/v0.4.6-pages` (publish branch or tag)
- `feature/*` branches for iterative DMAIC loops
- `docs/CHANGELOG.md` updated every iteration
- `files.html` governance block refreshed every iteration

## Operational Nudge

For user onboarding, always share hosted URL to `index.html` first.
Only share direct `dashboard_modular.html` URL for advanced users.
