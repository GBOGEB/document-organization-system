# P1 — pinned ChatGPT Project, witnessed source ingress

Paste this in **a new chat inside the already-pinned Project selected in the screenshot**. Do not use this as a generic new Project: the chosen source must remain the user's selected Project.

---

You are preparing a **read-only source handover** for the GBOGEB five-Project pilot, cohort `GBOGEB-CGPT-5P-20261116`, slot **P1**. The receiver is [document-organization-system PR #89](https://github.com/GBOGEB/document-organization-system/pull/89), with existing session semantics governed by [Hub #1230 / PR #1231](https://github.com/GBOGEB/pipeline-automation-hub/issues/1230) and source reconciliation by [GEMINI #56](https://github.com/GBOGEB/GEMINI/issues/56).

1. State the Project's **displayed title** and distinguish `USER_VISIBLE`, `GIVEN_TEXT`, `RETRIEVED_SOURCE`, `INFERRED`, and `UNKNOWN`. Do **not** fabricate a Project ID, list of chats, chat order, full transcript, git SHA, run result or historical decision. Do not assume that any source was available simply because it is in the same Project.
2. Select at most **three relevant chats or Project files** you can actually cite from this context. For each, record title, exact accessible source reference (or `UNKNOWN`), observed date (or null), decision/action, linked canonical GitHub repo/issue/PR, and source completeness `FULL_TEXT|EXCERPT|SUMMARY_ONLY|UNKNOWN`.
3. Create a bounded handover with: objective, source inventory, current solution/decisions, observed implemented artifacts, unresolved blockers, 1-3 next unblocked tasks, owner and DoD/DoV for each. Include `authority_transfer=false`, `automatic_merge=false`, `chat_deletion=false`, `project_rename=false`, `source_publication=false`.
4. Emit machine-readable `P1_PROJECT_HANDOVER.json` and human-readable `P1_HANDOVER.md`, `P1_GLOB.yaml`, and `P1_BSLN_ACTIONS.md`. Unknown values are null; stable Project-local aliases may be assigned, but they are **not** original immutable chat IDs.
5. Do not claim byte-lossless history from summaries. If you cannot access source bytes, set `capture_kind=HANDOVER_ONLY` and `source_bytes_sha256=null`. Do not include passwords, personal data, private Google Drive IDs, or controlled engineering source in a response intended for public GitHub.
6. Finish with a **redacted return message** containing: Project displayed title; number of source items actually inspected; distinct source evidence classes; exact open GitHub anchors; one READY task; one BLOCKED task; and your explicit `P1_SOURCE_CAPTURE_STATUS`.

After generating the files, the user should retain them in the selected Project or a private Drive worktree. A local checksum can be computed with the repository's `satellite_hmi/project_capture.py`, but such a checksum only proves the chosen handover file bytes. Nothing here automatically reads the entire Project or creates/merges GitHub PRs.