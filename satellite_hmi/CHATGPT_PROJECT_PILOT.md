# ChatGPT Project / Gemini / Google Drive handover ingress — bounded pilot

**Scope:** metadata-only, read-only-first external handover audit for the *existing* satellite HMI in `GBOGEB/document-organization-system` (#84, merged PR #85). This is not a second session genome, semantic index, Kahn/DAG engine, federation bus or approval gate. Existing Hub `lsaf/` (#1230, PR #1231) owns those functions; GEMINI #56 owns original tranche identity reconciliation.

## Actual surfaces

- **ChatGPT Project:** selected chats, saved responses, project instructions, and a linked Google Drive folder. A Project's contextual memory is **not** an export of all chat bytes; only user-authorized selected captures are ingested.
- **Google Drive:** reuse `codex_history/03_HANDOVERS/CHATGPT_PROJECT_PILOT_20261116` as a private interchange *projection*. No live DB, lease state, source-of-truth decisions or tokens in synchronized folders.
- **GitHub:** the public `satellite_hmi/intake_audit.py` code and synthetic tests; private/source content remains out of public GitHub. The Hub LSAF manifest and engineering-source repos retain authority.

## Pilot cohort (minimum, not fake evidence)

1. One **user-selected ChatGPT session** or response saved as a Project source; record `capture_kind=HANDOVER_ONLY` unless all original bytes are present.
2. One **Gemini reconciliation** (`GEMINI_TO_CHATGPT_RECONCILIATION_20261116`), classified `DERIVED`, not treated as independent identity proof.
3. One **GitHub worktree handover** with real branch/head/issue/PR refs and an observed, not guessed, `git status --porcelain` receipt.

Each candidate has `session_alias`, `provider`, `source_locator` (private), `capture_kind`, `source_as_of`, `sha256` (null until actual bytes hashed), `privacy_class`, `repo_owner`, `issue_ref`, `pr_ref`, `classification`, `blocking_dependencies` and `next_action`. Never publish the private manifest or unredacted chat content.

## Execution in ChatGPT Projects

1. In ChatGPT create/select a project (suggested `GBOGEB | Session Handover Pilot`); in project settings set instructions from the brief below. Add an *authorized private* Drive folder link as a project source; Google Drive content is queried live when used, **not pre-synchronized** to the project.
2. Save one useful handover response to the Project's sources, or upload a selected file. Do not assume a full chat export or an API for enumerating every chat/project. Managed ChatGPT workspaces may not expose self-service full-history exports.
3. Transfer only explicitly selected source bytes to a private Drive inbox; verify `Get-FileHash -Algorithm SHA256` (or `sha256sum`) and record the exact source version. Do not infer a digest from narrative or hashes copied from Gemini.
4. Run the existing guarded notebook from merged PR #85 for *user-triggered* dry-run validation, then opt-in hydration. It must not automatically execute retrieved files, overwrite, push or merge.
5. Audit the original tranche manifest locally, optionally against `Handover.glob.yaml` and an independently measured source inventory:

```powershell
python satellite_hmi/intake_audit.py ./MANIFEST.json --yaml ./Handover.glob.yaml --receipt ./intake_receipt.private.json --projection ./public_hmi_manifest.json --strict
python -m unittest discover -s satellite_hmi/tests -p 'test_*.py' -v
python satellite_hmi/render.py ./public_hmi_manifest.json ./00_PORTFOLIO_HMI_INDEX.html
```

Expected source behavior: `--strict` exits **2** on unresolved accounting/proof holds, even if the public HMI projection is generated for review. The source cannot be admitted for deletion by this adapter.

## Verification targets

- **Local 3-source smoke:** source ID, byte proof, privacy boundary and target repo/issue/PR links independently checked. No fabricated `VERIFIED` or `PASS` status.
- **Adversarial:** duplicate IDs, invalid JSON and SHA-256, mismatched counts, traversal, symlink, arbitrary HTTPS/code injection, malicious paths, missing local worktree and false-ready admission.
- **Cold-start continuation:** independent agent receives `HANDOVER.md`, `GLOB.yaml`, `MANIFEST.json` and source receipts and reproduces intended READY/BLOCKED and unresolved source identities.
- **Scale:** only after no false-ready in local pilot, compare with Hub PR #1231 existing 12-case convergence gate; do not multiply independent DAG engines.

## Project instruction snippet

> Treat the Project as a working context, not an export of full transcripts. For each bounded iteration emit an explicit source manifest, change delta, handover, glob and action register. Identify GitHub owner/issue/PR and the last observed SHA. Mark any missing original bytes or repository checks `UNKNOWN`. Use Drive only as a user-authorized interchange; GitHub/owner-controlled source remains authority. Do not auto-delete, auto-rename, push, publish or merge. Do not turn summaries into `BYTE_LOSSLESS` evidence.

## Source correction and open gates

The original Tranche A–H per-row arithmetic sums to **139 table rows, 136 per-tranche unique entries, 132 proposed deletion candidates, 4 holds**, inconsistent with its declared 136/134/131/3. Gemini's later reconciliation proposes 3 overlaps; no immutable original chat IDs, screenshot-by-screenshot independently reviewed crosswalk or verbatim original chat export was provided. `GEMINI #56 = IDENTITY_PROOF_HOLD`; **eligible deletion count 0**.

`LOCAL_QA` (when tested) is not `EXACT_HEAD_CI`, `HUMAN_APPROVAL` or `OWNER_ADMISSION`. Track each independently. Do not use any engineering dossiers in public fixtures.