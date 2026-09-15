# Cold-start restart checklist

Use this when restarting without the original chat.

1. Open `gloob/mip/2026-09-15-session-close/09_RESUME_PROMPT.md`.
2. Re-fetch `main`; do not assume it still equals the frozen v1.1 product baseline.
3. Preserve `c831758a247d928220e4b85efc13e3e74ba7da51` as the v1.1 CONTROL reference even if later handover commits exist.
4. Inspect `01_CURRENT_STATE.yaml`, `03_DOD_DOV_STATUS.yaml`, `05_BACKLOG_AND_FIRST_RED.yaml`, `10_3PR_STATUS.yaml`, and `11_MIP_STATUS.yaml`.
5. Verify the package integrity manifest before trusting the handover files.
6. Re-fetch the latest Gloob contract workflow and any currently open PRs before execution claims.
7. Confirm there is no new telemetry epoch or open causal route that supersedes this handover.
8. If the baseline remains quiet, start at **v1.2 outbound actuation**; do not reopen PCA residual work.
9. Build one real dispatch round trip only: dispatch envelope → target ingress → delivery ack → responder runtime >0 steps → exact-SHA return → v1.1 closure → local requalification.
10. Stop after the first exact-SHA round trip and re-run 3PR/MIP before scaling.

## Hard invariants

- No external return grants CONTROL.
- No PCA rotation alone opens work.
- No generic worker assignment bypasses causal attribution.
- No broad repo crawling occurs without an open route.
- No manual JSON copying counts as federated return closure.
- No queued workflow counts as PASS.
- No exact-SHA proof may be replaced by narrative confidence.

## Recovery if the first-red moves

If a new real telemetry epoch or causal route exists when restarting, classify that observed state first. The v1.2 dispatch frontier remains the default only when no newer concrete red supersedes it.
