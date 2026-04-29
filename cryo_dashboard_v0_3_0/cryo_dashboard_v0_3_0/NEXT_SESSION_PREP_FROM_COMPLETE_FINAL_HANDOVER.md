# Next Session Prep - Complete Final Session Handover Zip

Date: 2026-04-29
Target zip: cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER.zip
Staging folder: extracted_complete_final_session_handover/

## Key Context

- The extracted package is a continuation bundle built from v0.4.0 context.
- Current working dashboard baseline is v0.4.6.
- Therefore: treat this zip as a source of reusable ideas/artifacts, not as a direct overwrite source.

## Extracted Structure (verified)

- cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER/README.md
- cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER/docs/COMPLETE_FINAL_SESSION_HANDOVER.md
- cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER/docs/COMPLETE_FINAL_SESSION_HANDOVER.html
- cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER/context/COMPLETE_SESSION_CONTEXT.json
- cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER/context/DMAIC_IDEMPOTENCY_REGISTER.json
- cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER/context/ARTIFACT_MANIFEST.json
- cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER/agent/CODING_AGENT_PROMPT.md
- cryo_dashboard_COMPLETE_FINAL_SESSION_HANDOVER/artifacts/* (includes v0.3.0 and v0.4.0 zip artifacts)

## Safe Merge Strategy (next session)

1. Keep v0.4.6 files as the canonical baseline.
2. Mine only non-regressive content from the handover package:
   - process notes
   - traceability context
   - engineering narrative and checklists
3. Do not replace current runtime files directly from v0.4.0 artifacts:
   - dashboard_modular.html
   - js/app_modular.js
   - js/materials.js
   - data/materials.json
4. If any older artifact contains useful logic, port it as a targeted patch and retest.
5. Run validation after every integration chunk:
   - npm test
   - manual smoke checks on k, cp, tc modes

## Priority Intake Order

1. context/ARTIFACT_MANIFEST.json
2. context/COMPLETE_SESSION_CONTEXT.json
3. docs/COMPLETE_FINAL_SESSION_HANDOVER.md
4. artifacts/ENGINEERING_HANDOVER_v0_4_0.md
5. artifacts/V0_4_0_PREP_BRIEF.md

## Acceptance Criteria for Next Session

- No regression from v0.4.6 behavior (tc, quick outputs, dual-axis plot, filtering, inline errors).
- Documentation alignment remains consistent (README, docs/CHANGELOG, files.html, VERSION, package.json).
- Any imported logic from the zip is traceable in commit message and changelog.

## Recommended First Commands (next session)

From repository root:

```powershell
git status --short
git log -5 --oneline
```

From dashboard folder:

```powershell
npm test
```

Then compare candidate files before patching.
