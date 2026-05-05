<#
.SYNOPSIS
  Cryo Dashboard — Release preparation script.

.DESCRIPTION
  Automates every step needed before opening a PR:
    1. Reads the current version from VERSION and prompts for the next version.
    2. Bumps VERSION, README.md, GIT_TRACKING_MANIFEST.md header.
    3. Prepends a new dated section to docs/CHANGELOG.md.
    4. Regenerates docs/PR_RELEASE_<new>.md with PR title, description and
       merge checklist, and copies the body to the clipboard.
    5. Runs a version-consistency check across all canonical files and reports
       any mismatches.

.PARAMETER NewVersion
  Target version string, e.g. "v0.4.8". If omitted the script prompts interactively.

.PARAMETER ChangelogEntries
  A hashtable with keys "Added", "Changed", "Fixed", "Removed" — each an array
  of strings describing the changes. If omitted the script opens a mini wizard.

.EXAMPLE
  .\scripts\prepare-release.ps1 -NewVersion v0.4.8

.EXAMPLE
  .\scripts\prepare-release.ps1
  # Runs in interactive wizard mode.
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$NewVersion = "",
    [hashtable]$ChangelogEntries = $null
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Paths ────────────────────────────────────────────────────────────────────
$root = $PSScriptRoot | Split-Path -Parent   # one level above /scripts
$versionFile = Join-Path $root "VERSION"
$readmeFile = Join-Path $root "README.md"
$manifestFile = Join-Path $root "GIT_TRACKING_MANIFEST.md"
$changelogFile = Join-Path $root "docs\CHANGELOG.md"
$docsDir = Join-Path $root "docs"
$htmlFile = Join-Path $root "dashboard_modular.html"
$jsFile = Join-Path $root "js\app_modular.js"

# ── Helper: coloured output ───────────────────────────────────────────────────
function Write-Step  ([string]$msg) { Write-Host "  » $msg" -ForegroundColor Cyan }
function Write-Ok    ([string]$msg) { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn  ([string]$msg) { Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Write-Fail  ([string]$msg) { Write-Host "  ✗ $msg" -ForegroundColor Red }
function Divider { Write-Host ("-" * 68) -ForegroundColor DarkGray }

# ── Read current version ──────────────────────────────────────────────────────
$currentVersion = (Get-Content $versionFile -Raw).Trim()
Write-Host ""
Write-Host "  Cryo Dashboard — Release Preparation" -ForegroundColor White
Divider
Write-Host "  Current version : $currentVersion" -ForegroundColor DarkCyan

# ── Resolve new version ───────────────────────────────────────────────────────
if (-not $NewVersion) {
    $NewVersion = Read-Host "  New version (e.g. v0.4.8)"
}
$NewVersion = $NewVersion.Trim()
if ($NewVersion -notmatch '^v\d+\.\d+\.\d+$') {
    Write-Fail "Version must match vMAJOR.MINOR.PATCH (got '$NewVersion'). Aborting."
    exit 1
}
if ($NewVersion -eq $currentVersion) {
    Write-Warn "New version equals current version ($currentVersion). Nothing to do."
    exit 0
}
Write-Host "  Target version  : $NewVersion" -ForegroundColor White
Divider

# ── Collect changelog entries ─────────────────────────────────────────────────
$sections = @("Added", "Changed", "Fixed", "Removed")
if ($null -eq $ChangelogEntries) {
    $ChangelogEntries = @{}

    # ── Auto-seed from docs/PR_RELEASE_<currentVersion>.md if it exists ──────
    $existingPackFile = Join-Path $docsDir "PR_RELEASE_$currentVersion.md"
    $seededSections = @{}
    if (Test-Path $existingPackFile) {
        Write-Host ""
        Write-Host "  Found docs/PR_RELEASE_$currentVersion.md — importing entries..." -ForegroundColor DarkCyan
        $packContent = Get-Content $existingPackFile -Raw
        foreach ($sec in $sections) {
            # Match "### Added" (or Changed/Fixed/Removed) block up to next ### or ##
            if ($packContent -match "(?s)###\s+$sec\s*\n(.*?)(?=\n###|\n##|$)") {
                $block = $Matches[1]
                $items = @($block -split "`n" |
                    Where-Object { $_ -match '^\s*-\s+.+' } |
                    ForEach-Object { ($_ -replace '^\s*-\s+', '').Trim() } |
                    Where-Object { $_ -ne '' })
                if ($items.Count -gt 0) {
                    $seededSections[$sec] = $items
                    Write-Ok "  Seeded [$sec]: $($items.Count) item(s) from PR pack"
                }
            }
        }
    }

    # ── Interactive wizard — shows seeded items and lets user add more ────────
    Write-Host ""
    Write-Host "  Changelog entries (one per line; blank line = done)." -ForegroundColor DarkCyan
    if ($seededSections.Count -gt 0) {
        Write-Host "  Pre-loaded from PR_RELEASE_$currentVersion.md. Add extras or just press Enter." -ForegroundColor DarkGray
    }
    foreach ($sec in $sections) {
        $items = if ($seededSections.ContainsKey($sec)) { [System.Collections.Generic.List[string]]$seededSections[$sec] } else { [System.Collections.Generic.List[string]]@() }
        if ($items.Count -gt 0) {
            Write-Host "  [$sec] — pre-loaded $($items.Count) item(s):" -ForegroundColor Yellow
            $items | ForEach-Object { Write-Host "    · $_" -ForegroundColor DarkGray }
            Write-Host "  Add more (blank to finish):" -ForegroundColor Yellow
        }
        else {
            Write-Host "  [$sec] (blank to skip):" -ForegroundColor Yellow
        }
        while ($true) {
            $line = Read-Host "    +"
            if ([string]::IsNullOrWhiteSpace($line)) { break }
            $items.Add($line.Trim())
        }
        if ($items.Count -gt 0) { $ChangelogEntries[$sec] = $items.ToArray() }
    }
}

# ── 1. Bump VERSION ───────────────────────────────────────────────────────────
Write-Step "Updating VERSION → $NewVersion"
Set-Content -Path $versionFile -Value $NewVersion -NoNewline
Write-Ok "VERSION"

# ── 2. Bump README.md title line ──────────────────────────────────────────────
Write-Step "Updating README.md"
$readmeContent = Get-Content $readmeFile -Raw
$readmeNew = $readmeContent -replace [regex]::Escape($currentVersion), $NewVersion
if ($readmeNew -ne $readmeContent) {
    Set-Content -Path $readmeFile -Value $readmeNew -NoNewline
    Write-Ok "README.md"
}
else {
    Write-Warn "README.md — pattern '$currentVersion' not found, skipped."
}

# ── 3. Bump GIT_TRACKING_MANIFEST.md header ───────────────────────────────────
Write-Step "Updating GIT_TRACKING_MANIFEST.md"
$manifestContent = Get-Content $manifestFile -Raw
$manifestNew = $manifestContent -replace [regex]::Escape($currentVersion), $NewVersion
$today = Get-Date -Format "yyyy-MM-dd"
$manifestNew = $manifestNew -replace '(?<=\*\*Generated:\*\* )[\d-]+', $today
if ($manifestNew -ne $manifestContent) {
    Set-Content -Path $manifestFile -Value $manifestNew -NoNewline
    Write-Ok "GIT_TRACKING_MANIFEST.md"
}
else {
    Write-Warn "GIT_TRACKING_MANIFEST.md — version pattern not found, skipped."
}

# ── 4. Prepend CHANGELOG.md section ──────────────────────────────────────────
Write-Step "Prepending $NewVersion section to CHANGELOG.md"
$changelogContent = Get-Content $changelogFile -Raw

# Build the new section text
$newSection = @()
$newSection += "## $NewVersion`n"
$newSection += "**Date:** $today`n"
foreach ($sec in $sections) {
    if ($ChangelogEntries.ContainsKey($sec) -and $ChangelogEntries[$sec].Count -gt 0) {
        $newSection += "`n### $sec`n"
        foreach ($item in $ChangelogEntries[$sec]) {
            $newSection += "- $item`n"
        }
    }
}
$newSection += "`n"
$newSectionText = $newSection -join ""

# Insert after the first heading line ("# Changelog\n")
$changelogNew = $changelogContent -replace '(# Changelog\s*\n)', "`$1`n$newSectionText"
Set-Content -Path $changelogFile -Value $changelogNew -NoNewline
Write-Ok "docs/CHANGELOG.md"

# ── 5. Build PR body text ─────────────────────────────────────────────────────
Write-Step "Generating PR release pack"

$prTitle = "release($NewVersion): <describe this release — edit before pasting>"

# Summarise changelog entries for the PR body
$prFuncLines = @()
foreach ($sec in $sections) {
    if ($ChangelogEntries.ContainsKey($sec) -and $ChangelogEntries[$sec].Count -gt 0) {
        $prFuncLines += "**$sec**"
        foreach ($item in $ChangelogEntries[$sec]) { $prFuncLines += "- $item" }
    }
}
$prFuncBlock = if ($prFuncLines.Count -gt 0) { $prFuncLines -join "`n" } else { "_(no entries provided)_" }

# Detect touched canonical files for the "Canonical Artifact Updates" section
$canonicalFiles = @(
    @{ path = $versionFile; label = '`VERSION`' },
    @{ path = $readmeFile; label = '`README.md`' },
    @{ path = $changelogFile; label = '`docs/CHANGELOG.md`' },
    @{ path = $manifestFile; label = '`GIT_TRACKING_MANIFEST.md`' }
)
$canonicalLines = $canonicalFiles | ForEach-Object { "- $($_.label) → bumped to $NewVersion" }
$canonicalBlock = $canonicalLines -join "`n"

# Checklist items
$checklistBase = @(
    "Open dashboard and smoke-test affected panels.",
    "Verify version label in dashboard title bar reads $NewVersion.",
    "Run `npm test` in an environment where Node/npm is available.",
    "Confirm `VERSION` and `docs/CHANGELOG.md` are aligned to $NewVersion.",
    "Squash-merge (or rebase-merge) into `main` after review."
)
$checklistBlock = ($checklistBase | ForEach-Object { "- [ ] $_" }) -join "`n"

$prBody = @"
## Summary

Promotes the dashboard to $NewVersion.

## Functional Changes

$prFuncBlock

## Canonical Artifact Updates

$canonicalBlock

## Validation

- IDE diagnostics: no errors in updated dashboard HTML/JS files.
- Automated tests: run `npm test` before merge.

## Merge Checklist

$checklistBlock
"@

# ── 6. Write docs/PR_RELEASE_<version>.md ────────────────────────────────────
$prFile = Join-Path $docsDir "PR_RELEASE_$NewVersion.md"
$prFileContent = @"
# PR Release Pack — $NewVersion

## Suggested PR Title

``$prTitle``

## Suggested PR Description

$prBody
"@
Set-Content -Path $prFile -Value $prFileContent -Encoding UTF8
Write-Ok "docs/PR_RELEASE_$NewVersion.md"

# Copy body to clipboard
try {
    Set-Clipboard -Value $prBody
    Write-Ok "PR body copied to clipboard — paste directly into the GitHub PR description."
}
catch {
    Write-Warn "Clipboard copy failed (non-interactive session?). PR body is in docs/PR_RELEASE_$NewVersion.md"
}

# ── 7. Version consistency check across all files ─────────────────────────────
Divider
Write-Host "  Version consistency check" -ForegroundColor White
Divider

$filesToCheck = @(
    $versionFile,
    $readmeFile,
    $manifestFile,
    $changelogFile,
    $htmlFile,
    $jsFile
)

$issues = @()
foreach ($f in $filesToCheck) {
    if (-not (Test-Path $f)) {
        Write-Warn "  SKIP  $(Split-Path $f -Leaf) — file not found"
        continue
    }
    $content = Get-Content $f -Raw
    $hasNew = $content -match [regex]::Escape($NewVersion)
    $hasOld = $content -match [regex]::Escape($currentVersion)
    $rel = $f.Replace($root + "\", "")

    if ($hasNew -and -not $hasOld) {
        Write-Ok "  OK    $rel"
    }
    elseif ($hasNew -and $hasOld) {
        Write-Warn "  MIXED $rel — contains BOTH $currentVersion and $NewVersion. Review manually."
        $issues += $rel
    }
    elseif (-not $hasNew) {
        Write-Warn "  MISS  $rel — $NewVersion not found. Update manually if needed."
        $issues += $rel
    }
}

Divider
if ($issues.Count -eq 0) {
    Write-Ok "All checked files are consistent with $NewVersion."
}
else {
    Write-Warn "$($issues.Count) file(s) need manual review (see MISS / MIXED above)."
}

Write-Host ""
Write-Host "  Done. Next steps:" -ForegroundColor White
Write-Host "    git add -A" -ForegroundColor DarkGray
Write-Host "    git commit -m `"chore(release): bump to $NewVersion and update canonicals`"" -ForegroundColor DarkGray
Write-Host "    Then push via the clean worktree and open the PR." -ForegroundColor DarkGray
Write-Host ""
