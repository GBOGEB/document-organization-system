# GitHub Pages Deployment Checklist — Cryogenic Material Dashboard v0.4.9

**Target URL:** `https://gbogeb.github.io/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/`

---

## Pre-Deployment Verification

### 1. Test Suite (all must pass)
```bash
cd cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0
npm test
```

- [ ] `numerics.test.js` — Integration method regression fixtures
- [ ] `export.test.js` — Export consistency
- [ ] `materials.validate.js` — Material database schema validation
- [ ] `file_index_integrity.test.js` — File index integrity
- [ ] `static_entrypoints.test.js` — Entry point existence
- [ ] `version-coherence-check.js` — Version string coherence
- [ ] `nist_parity.test.js` — **766 NIST parity regression tests**

### 2. Data Integrity
- [ ] `data/materials.json` is valid JSON
- [ ] All 10 materials present with correct properties
- [ ] Coefficients match NIST published values (verified by nist_parity.test.js)
- [ ] `ssot.json` is valid JSON and contains current metadata

### 3. Asset Verification
- [ ] `.nojekyll` file exists at repository root (prevents Jekyll processing)
- [ ] All relative paths are correct (no absolute or `file://` paths in HTML)
- [ ] CDN links for Plotly.js and Reveal.js are valid HTTPS URLs
- [ ] No hardcoded `localhost` references in production files

### 4. Entry Points
| Entry Point | File | Status |
|-------------|------|--------|
| Landing page | `index.html` | [ ] Verified |
| Modular dashboard | `dashboard_modular.html` | [ ] Verified |
| File browser | `files.html` | [ ] Verified |
| Preview hub | `html_preview_hub.html` | [ ] Verified |
| SSOT launcher | `ssot_launcher.html` | [ ] Verified |
| Slide deck | `index_slides.html` | [ ] Verified |

---

## Deployment Steps

### Step 1: Merge to Main
```bash
# Ensure all changes are on main branch
git checkout main
git pull origin main
```

### Step 2: Enable GitHub Pages
1. Navigate to **Settings → Pages** in the GitHub repository
2. Set **Source** to: `Deploy from a branch`
3. Set **Branch** to: `main` / `/ (root)`
4. Click **Save**

### Step 3: Verify Build
- GitHub Actions will automatically build and deploy
- Check the **Actions** tab for deployment status
- First deployment may take 2-5 minutes

---

## Post-Deployment Validation

### Automated Checks
```bash
# Verify pages are accessible (run from any machine)
curl -s -o /dev/null -w "%{http_code}" https://gbogeb.github.io/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/index.html
# Expected: 200

curl -s -o /dev/null -w "%{http_code}" https://gbogeb.github.io/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/data/materials.json
# Expected: 200
```

### Manual Checks
- [ ] Landing page loads without console errors
- [ ] SSOT launcher renders Plotly charts correctly
- [ ] Copper RRR k(T) curves show characteristic low-T peaks
- [ ] Slide deck navigates through all 15 slides
- [ ] Modular dashboard loads material data and computes integrals
- [ ] Theme toggle (dark/light) works on launcher
- [ ] No mixed-content warnings (HTTP resources on HTTPS page)

### Cross-Browser
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest, if available)

---

## Rollback Procedure

If issues are found post-deployment:

### Quick Rollback (disable Pages)
1. Go to **Settings → Pages**
2. Set **Source** to **None**
3. Click **Save** — site goes offline immediately

### Code Rollback
```bash
# Identify last known good commit
git log --oneline -10

# Revert to specific commit (creates a new commit, preserves history)
git revert HEAD --no-edit
git push origin main

# Or reset to specific commit (destructive — use only if necessary)
git reset --hard <commit-sha>
git push origin main --force-with-lease
```

### Cache Invalidation
- GitHub Pages has a ~10-minute cache TTL
- For immediate updates, append cache-busting query params:
  `?v=<timestamp>` (already implemented for `materials.json`)

---

## Known Limitations

1. **CORS on `file://`**: The `dashboard_modular.html` uses `fetch()` for `materials.json`, which requires HTTP(S). Works on GitHub Pages; does **not** work when opened via `file://` directly.
2. **CDN Dependencies**: Plotly.js (~3.5 MB) and Reveal.js are loaded from CDN. If CDN is down, charts and slides won't render.
3. **No Service Worker**: The dashboard does not work offline. All CDN resources must be available.
4. **Single Branch Deploy**: GitHub Pages deploys from `main`. All changes must be merged to `main` before they appear on the live site.

---

## Version History

| Version | Date | Key Change |
|---------|------|------------|
| v0.4.9 | 2026-05-14 | Initial SSOT system integration |
| v0.4.9-fix | 2026-05-18 | evalRational() fix + NIST lineage |
| v0.4.9-nist | 2026-05-18 | 766-test NIST parity regression suite |
