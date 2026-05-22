# Umbrella Multi-Repo PR Package

This package turns the umbrella initiative into a PR-ready coordination brief for the canonical repository `/tmp/workspace/GBOGEB/document-organization-system`, plus the GBA and GBC repo clusters.

## PHASE 1. Initiative boundary

a. Declare `/tmp/workspace/GBOGEB/document-organization-system` as the canonical runtime/reference repo for:
   - dashboard runtime
   - GitHub Pages views
   - SSOT metadata
   - validation baseline

b. Declare GBA and GBC as receiving clusters for adapted patterns, not replacement authorities for the canonical runtime.

c. Run the umbrella initiative in 4 coordinated lanes:
   - Artefacts
   - PRs/Reviews
   - Influence/Stakeholders
   - Integration Hub

## PHASE 2. Coordinated PR units

a. **PR-A — Current repo / reference implementation**
   - Lock the reference architecture around:
     - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/dashboard_modular.html`
     - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/js/app_modular.js`
     - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/ssot.json`
     - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/file_index.json`
     - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/file_index.yaml`

b. **PR-B — GBA cluster assimilation**
   - Adapt SSOT, file-index, handover, validation, and GitHub Pages/view conventions from the canonical repo.

c. **PR-C — GBC cluster assimilation**
   - Adapt orchestration, agent handover, artefact publishing, and interactive HTML view conventions from the canonical repo.

d. **PR-D — Integration Hub**
   - Implement the bridge model for status, action, progress, links, and cross-repo traceability.

## PHASE 3. Artefact split

a. **Runtime artefacts**
   - HTML entrypoints
   - Plotly views
   - decks and slides
   - preview hubs
   - machine-readable indexes
   - SSOT metadata

b. **Governance artefacts**
   - handover docs
   - RTM
   - changelog/release notes
   - deployment confirmation
   - CDN pinning
   - version coherence

c. **Validation artefacts**
   - `npm test`
   - static entrypoint validation
   - file-index integrity checks
   - version coherence checks
   - NIST parity checks

d. **Integration artefacts**
   - Hub links
   - status model
   - bridge contracts
   - repo-to-repo intake manifests

## PHASE 4. PR-ready package

### 1. Umbrella PR title

`program: establish umbrella PR package for canonical repo, GBA, GBC, and integration hub`

### 2. Per-repo PR titles

a. `docs: publish canonical umbrella package for document-organization-system`

b. `program(gba): assimilate canonical SSOT, file-index, handover, validation, and GitHub Pages patterns`

c. `program(gbc): assimilate orchestration, agent handover, artefact publishing, and interactive HTML view patterns`

d. `program(hub): add integration hub bridge for status, links, reviews, progress, and validation traceability`

### 3. Review checklist

a. **Architecture review**
   - [ ] Confirms `/tmp/workspace/GBOGEB/document-organization-system` remains the canonical runtime authority
   - [ ] Confirms GBA and GBC are adaptation targets, not source-of-truth replacements
   - [ ] Confirms Integration Hub remains a bridge layer, not a computation layer

b. **Artefact review**
   - [ ] Confirms canonical runtime artefacts are listed from the reference repo
   - [ ] Confirms governance artefacts include handover, changelog, release, deployment, and CDN controls
   - [ ] Confirms validation artefacts include `npm test`, file-index integrity, static entrypoints, version coherence, and NIST parity

c. **GitHub Pages / live-view review**
   - [ ] Confirms `.nojekyll` pattern remains required where ES modules are served
   - [ ] Confirms live repos expose one human landing page
   - [ ] Confirms live repos expose one machine-readable manifest
   - [ ] Confirms live repos expose one validation command and one version source

d. **Handover review**
   - [ ] Confirms CODEX handover is OpenAI-only, light theme, Copilot disabled
   - [ ] Confirms ABACUS handover is chatLLM + codeLLM CLI, dark theme
   - [ ] Confirms both handovers consume canonical SSOT and file-index inputs first

e. **Stakeholder review**
   - [ ] Confirms artefact owners are explicit
   - [ ] Confirms reviewer roles are explicit
   - [ ] Confirms stakeholder influence map is explicit

## PHASE 5. CODEX handover — OpenAI-only guided session

a. **Title**
   - `CODEX Handover — OpenAI-only guided session`

b. **Environment assumptions**
   - VS Code interface
   - OpenAI/CODEX-only experience
   - Copilot chat/agent disabled
   - Light theme

c. **Consume first**
   - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/ssot.json`
   - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/file_index.json`
   - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/docs/CRYO_DASHBOARD_SESSION_HANDOVER_v0.4.9.md`

d. **Handover text**

```text
You are operating in VS Code with an OpenAI/CODEX-only workflow. Copilot chat and agent capabilities are disabled. Use a light theme. Treat /tmp/workspace/GBOGEB/document-organization-system as the canonical runtime/reference repo for the dashboard, GitHub Pages views, SSOT metadata, and validation baseline.

Consume these files first:
1. /tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/ssot.json
2. /tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/file_index.json
3. /tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/docs/CRYO_DASHBOARD_SESSION_HANDOVER_v0.4.9.md

Your role:
- preserve canonical runtime truth
- prepare structured PR text
- generate review notes
- avoid becoming the runtime source-of-truth outside the canonical repo

Produce outputs in numbered PHASES with lettered TASKS. Separate Artefacts, PR Reviews, and Stakeholder Influence clearly.
```

## PHASE 6. ABACUS handover — chatLLM + codeLLM CLI orchestrator session

a. **Title**
   - `ABACUS Handover — chatLLM + codeLLM CLI orchestrator session`

b. **Environment assumptions**
   - VS Code IDE
   - Dark theme
   - codeLLM in CLI flow
   - chatLLM for planning/chat/agent prep

c. **Control model**
   - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/material_properties_docs/IDEMPOTENT_RECURSIVE_CONTROL.md`

d. **Handover text**

```text
You are operating in VS Code with a dark theme. Use codeLLM in CLI flow and use chatLLM for planning, chat, and agent preparation. Treat /tmp/workspace/GBOGEB/document-organization-system as the canonical reference node and use its SSOT and file indexes as machine-ingest inputs.

Consume these files first:
1. /tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/ssot.json
2. /tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/file_index.json
3. /tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/material_properties_docs/IDEMPOTENT_RECURSIVE_CONTROL.md

Your role:
- orchestrate across repos
- maintain cluster-level status and progress
- consume SSOT and file indexes as machine inputs
- coordinate bridge tasks, not domain runtime logic ownership

Use the idempotent/recursive control model to keep work traceable, repeatable, and version-aware. Produce outputs in numbered PHASES with lettered TASKS. Separate Artefacts, PR Reviews, and Stakeholder Influence clearly.
```

## PHASE 7. GitHub Pages / live-views integration brief

a. Standardize GitHub Pages as the live-view layer for:
   - decks
   - 2D plots
   - 3D plots
   - heat maps
   - contours
   - preview hubs

b. Reuse the canonical Pages pattern:
   - root `.nojekyll`
   - subtree `.nojekyll`
   - static HTML entrypoints
   - pinned Plotly assets
   - machine-readable navigation

c. Require every live repo to expose:
   - one human landing page
   - one machine-readable manifest
   - one validation command
   - one release/version source

d. Treat the following canonical files as the reference set:
   - `/tmp/workspace/GBOGEB/document-organization-system/.nojekyll`
   - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/.nojekyll`
   - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/README.md`
   - `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/docs/CDN_PINNING.md`
   - `/tmp/workspace/GBOGEB/document-organization-system/.github/workflows/modular-ci-audit.yml`

## PHASE 8. Integration Hub brief

a. **Purpose**
   - bridge repos, not compute domain logic

b. **Minimum responsibilities**
   - link repos
   - show status/progress
   - expose PR state
   - expose review state
   - expose deploy/live-view state
   - expose validation state

c. **Minimum data contract**
   - repo name
   - canonical owner
   - current version
   - entrypoints
   - validation command
   - artefact manifest URL
   - handover doc URL
   - stakeholder/reviewer owner

d. **Hub ingest model**
   - use `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/ssot.json`
   - use `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/file_index.json`
   - keep cluster adapters thin and traceable

## Artefacts / PR reviews / stakeholder influence

### 1. Artefact owners

a. Current repo maintainers — runtime, SSOT, validation

b. GBA leads — assimilation of canonical patterns into cluster A

c. GBC leads — assimilation of orchestration/view patterns into cluster B

d. Integration Hub owners — cross-repo linking and status model

### 2. PR reviewers

a. Technical reviewer — runtime and architecture

b. Validation reviewer — tests, CI, release gates

c. UX/view reviewer — Pages, decks, Plotly rendering

d. Governance reviewer — handover, ownership, traceability

### 3. Stakeholder influence

a. Runtime stakeholders — users relying on live HTML and GitHub Pages views

b. Agent stakeholders — CODEX and ABACUS operators

c. Governance stakeholders — repo owners, release approvers, maintainers

d. Integration stakeholders — users needing unified status and progress across repo clusters

## Copilot agent session — exact 8-step execution brief

1. Inventory the canonical runtime, SSOT, Pages entrypoints, validation, and handover files in `/tmp/workspace/GBOGEB/document-organization-system`.
2. Draft the umbrella PR initiative with 4 lanes: current repo, GBA, GBC, and Integration Hub.
3. Split outputs into Artefact, PR Review, and Stakeholder Influence sections.
4. Produce the CODEX handover message for the OpenAI-only light-theme workflow.
5. Produce the ABACUS handover message for the chatLLM/codeLLM CLI dark-theme workflow.
6. Produce the GitHub Pages/live-views integration brief for decks, Plotly plots, heat maps, contours, and HTML artefacts.
7. Produce the Integration Hub brief for linking, status, progress, and bridge contracts.
8. Finalize a rollout sheet with owner, repo cluster, deliverable, review path, validation path, and stakeholder signoff.

## Rollout sheet

| Phase | Owner | Repo cluster | Deliverable | Review path | Validation path | Stakeholder signoff |
|---|---|---|---|---|---|---|
| 1 | Current repo maintainers | Canonical repo | Reference architecture lock | Technical + governance review | `/tmp/workspace/GBOGEB/document-organization-system/cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0/package.json` `npm test` | Runtime stakeholders |
| 2 | GBA leads | GBA | SSOT/file-index/handover/Pages assimilation | Technical + validation review | Cluster-local adaptation checks against canonical manifests | Governance stakeholders |
| 3 | GBC leads | GBC | Orchestration/handover/publishing/view assimilation | Technical + UX/view review | Cluster-local adaptation checks against canonical manifests | Agent stakeholders |
| 4 | Integration Hub owners | Hub | Cross-repo bridge, status, and traceability contract | Governance + integration review | Manifest ingest validation against canonical SSOT/file-index model | Integration stakeholders |

## Direct instruction for the next agent session

```text
Create an umbrella multi-repo PR package for GBOGEB/document-organization-system, GBA cluster, and GBC cluster. Do not collapse runtime authority away from the current repo. Produce 4 coordinated PR briefs, 2 handover messages (CODEX and ABACUS), one GitHub Pages/live-views integration brief, and one Integration Hub brief. Structure output in numbered PHASES with lettered TASKS. Separate artefacts, PR reviews, and stakeholder influence clearly.
```
