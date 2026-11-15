---
name: gdrive-worktree-hmi
description: Build and reconcile a read-only Google Drive satellite worktree with a single-file HTML VFS/HMI, a user-triggered Colab hydration notebook, declarative manifest, reproducible integrity receipts and GitHub integration pointers. Use for Drive worktree handovers, cross-repository DAG/portfolio navigation, state-delta propagation, or safe hybrid ChatGPT/Gemini workflows. Avoid duplicate worktrees and never promote unverified engineering decisions or CI evidence.
---

# GDrive Worktree HMI — declarative companion

This skill contains **instructions only**, with no bundled executable code. It can be loaded in runtimes that reject skill directories containing scripts, subject to that runtime's skill-format and connector support. Generate execution artifacts on demand; do not assume Google Drive or Colab is authenticated.

## 1. Reconcile before provisioning

1. Obtain the folder URL/ID and existing artifact URLs, using connected Google Drive tools. If the folder exists, inventory its direct children before generating anything.
2. Read `Handover.glob.yaml`, `MANIFEST.json`, any existing HMI, notebook, and owner ledger. Preserve IDs, approved naming, revision dates and provenance. Do not invent ALX/MIN numbers, SHAs or release approvals.
3. Search relevant GitHub issues/PRs and identify a single owner per concern. Prefer a bounded draft PR in the outward-artifact repository, the existing federation bridge for sync, and the engineering-source repository for engineering decisions. Do not create a second bridge, ledger or DAG kernel.
4. Treat the Drive folder as a **projection and handover cache**, not engineering SSOT or GitHub source authority. Mark conflicting claims `CONFLICT` or `UNVERIFIED` rather than silently overwriting.

## 2. Build the four satellite surfaces

Create or update in place when allowed:

- `00_PORTFOLIO_HMI_INDEX.html`: single self-contained HTML with a collapsible virtual hierarchy, keyboard-searchable labels, accessible release status, links to real Drive/GitHub objects, a visible `source_as_of`, and no external JS dependency. Prefer metadata-only embedded JSON. Treat file contents as untrusted text and escape them. No tokens or sensitive technical details inside a public copy.
- `01_WORKTREE_HYDRATOR.ipynb`: user-triggered mount and local hydration only. Validate SHA-256 from actual bytes, reject invalid paths and symlink targets, impose per-file and total-size caps, never execute hydrated files, never auto-run source files or auto-push to GitHub. GitHub sync is off by default and requires explicit user permission, repository, branch, diff review and authentication outside the notebook.
- `Handover.glob.yaml` and `MANIFEST.json`: retain the source originals. Where a prior `sha256:` value is not exactly 64 hexadecimal digits or a file digest lacks actual bytes, report `NOT_VERIFIED` and create a *separate* v2 receipt rather than granting PASS.
- `AGENT_DROPIN_HANDOVER.txt` and `BSLN_ACTIONS.md`: concise reset context, current PR/issue link, source IDs, blockers, owner decisions, tests and per-action DoD/DoV. Preserve revision history and gate outcomes.

## 3. Gate boundaries

`G0 SOURCE_IDENTITY` -> `G1 MANIFEST_INTEGRITY` -> `G2 HMI_READONLY_QA` -> `G3 HYDRATION_NEGATIVE_TESTS` -> `G4 INDEPENDENT_REVIEW` -> `G5 OWNER_RELEASE_APPROVAL`.

Never interpret `LOCKED` as approved without owner evidence. Never derive SIL classification, LOPA consequence categories, gas CoA acceptance limits, legal precedence of source systems or actual physical control decisions from narrative assumptions. Put such claims in a source-RFI lane with `HOLD_ENGINEERING` until evidence and owner disposition exist. Do not auto-rename existing ALX originals or mutate contractor release packages.

## 4. Delta/ledger contract

Each action carries `id`, `owner`, `source_ref`, `input_sha256` (nullable), `change`, `status`, `blocking_dependencies`, `test_receipt` (nullable), `head_sha` (nullable), and `next_action`. IDs are stable. Merge by immutable action ID, keep event history, never call non-verbatim compression *lossless* unless the raw source or a verifiably sufficient reconstruction remains available. Re-render only the impacted projection after changed source IDs or hashes; leave unrelated artifacts unchanged.

## 5. Verify and report

Perform two lanes: structural/negative tests (invalid JSON, tampered hashes, duplicate IDs, path traversal, unsupported URLs, unknown gate status, non-existent links) and visual/browser QA (desktop/mobile overflow, tree/search/accordion behavior, keyboard focus, offline open). No self-reported CI PASS: distinguish `LOCAL_TEST`, `EXACT_HEAD_CI`, `HUMAN_REVIEW`, `OWNER_ADMISSION`. End with exact changed file links, GitHub PR/issue URLs and SHAs, unresolved conditions, explicit next Kahn-ready tasks. For write attempts that fail or are unavailable, return local artifacts and a truthful non-written status.
