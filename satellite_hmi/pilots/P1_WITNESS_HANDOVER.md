# Pilot P1 — user-selected pinned ChatGPT Project

**Scope:** five distinct user-selected ChatGPT Projects; first project identified only by a user-provided pinned-Project screenshot and owner's instruction. Four other candidate Projects will be supplied later. **Do not guess Project name, chat list, internal IDs or source contents.**

## Witness ledger (observable, not synthetic)

| Gate | Observation | Status |
| --- | --- | --- |
| E0 | Owner selects screenshot Project as P1 and reports pinned | USER_ATTESTED |
| E1 | Canonical GitHub outward owner located: document-organization-system PR #85 merged | VERIFIED_REMOTE |
| E2 | Existing semantic session owner: Hub #1230 / PR #1231 | VERIFIED_REMOTE |
| E3 | Five-slot cohort manifest and fail-closed local tests | LOCAL_TEST |
| E4 | Original Project ID, exact title, project chat inventory | NOT_OBSERVED |
| E5 | Selected Project handover/export bytes hashed locally | NOT_OBSERVED |
| E6 | Real project cold-start N->N+1 reconstruction | NOT_EXECUTED |
| E7 | Draft GitHub integration PR | PENDING until PR URL recorded |
| E8 | Native CI, eligible independent review, owner admission | NOT_EXECUTED |

## Owner action in pinned ChatGPT Project (manual, no APIs assumed)

1. Open the **already pinned Project**. Start a new chat in that Project (or place this exchange there if the UI offers that action).
2. Paste the P1 prompt from the corresponding Chat response; identify 1-3 representative chats and/or attach a selected handover file as a Project source. Do not move controlled engineering material to a public Project.
3. Ask the Project chat to produce a **source-labeled** `P1_HANDOVER.md` with its *observed* titles, sources, artifacts, open issues, next action and unknowns. Where source material is inaccessible, record `UNKNOWN`, not a fictitious transcript.
4. Retain the file privately; if saved locally, run `python satellite_hmi/project_capture.py --source "<local file>" --alias P1 --capture-kind HANDOVER_ONLY --receipt "<private directory>/P1.receipt.private.json"`.
5. User may place the selected source file and private receipt under existing Drive `codex_history/03_HANDOVERS/CHATGPT_PROJECT_PILOT_20261116/P1/` (do not put private data in public GitHub). Return a redacted handover or results in chat.

## Exit condition

This program can reach **draft PR created** before source admission; that is an engineering handoff milestone, *not proof that the pinned Project's chats were read*. A full P1 end-to-end acceptance requires actual selected Project source, byte receipt, deterministic cold-start replay, SHA-bound exact-head CI and independent review. Deletion/merge remain forbidden without owner approval.