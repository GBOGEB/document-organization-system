# Drop-in fresh-chat resume instruction

Take over **Gloob execution** from the durable v1.1 session closure in `GBOGEB/document-organization-system`.

## Frozen starting state

Treat `GBOGEB/document-organization-system@c831758a247d928220e4b85efc13e3e74ba7da51` as the **External Causal-Return Closure v1.1 CONTROL product baseline**.

PR #52 is merged. Its exact head `6f32a0712700bf80d49bb1c85c11813cf8ece420` passed `Gloob Book Contract` in run `34926808606`. The fresh-main merge SHA `c831758a247d928220e4b85efc13e3e74ba7da51` passed the same contract in run `34926844761`, and Pages passed in run `34926844148`.

Fresh-main control artifact `10379618104` has digest `sha256:0aeac9c845e27bbde1d5da2261ef04a933fd10de13d74eac1d363c58bd12f168`.

Live state at closure:

- 32 `STABLE_CONTROL`, 0 `REQUALIFY`, 0 `ESCALATE`.
- 32 `UNCHANGED_CONTROL`, 0 `CAUSAL_REQUALIFY`, 0 `CAUSAL_ESCALATE`.
- 0 causal routes, 0 handshakes, 0 external returns, 0 closure actions.
- Federated history: 9 telemetry snapshots, 7 causal snapshots, 8 surveillance snapshots, 1 external-return snapshot, 0 download errors.

Do not reopen residual PCA work merely because PC2/PC3/PC4 variance exists.

## Preserve these invariants

- Statistical residual is not work.
- CONTROL is sticky only through an unchanged entity telemetry signature; a real entity change starts a new qualification epoch.
- Work opens only after a changed entity fails qualification and a concrete causal surface is attributed.
- Cause classes are SOURCE, ATOM, EDGE, OPERATOR, RUNTIME and FEDERATED_RETURN.
- Routes are bound by deterministic `route_id` and `assignment_digest`.
- External returns must match route, assignment, target repo and crew, and prove exact `source_commit == runner_commit`, >0 steps and successful runtime.
- A valid `RESOLVED` return closes the external assignment and triggers local requalification. It does **not** grant CONTROL.
- Publication, engineering and runtime authority remain distinct.
- No open route means no broad cross-repo return crawling.

## Execute next — v1.2

Implement **Federated Mission Dispatch + Responder Runtime**. The first-red is the actuation gap between an emitted Gloob handshake and actual governed target-repository work start.

Use this execution sequence:

1. Re-fetch current `main` and this handover package.
2. Preserve `c831758a...` as the v1.1 product CONTROL baseline even if the handover package itself was merged later.
3. Define deterministic dispatch-envelope identity derived from the existing handshake/route identity.
4. Add target-repo ingress with replay, stale-route and supersession protection.
5. Add delivery acknowledgement distinct from final causal return.
6. Bind responder capability/crew eligibility without fabricating unavailable crew facts.
7. Execute one **real** target-repo workflow >0 steps on an exact SHA.
8. Publish `gloob-causal-return` from the target repo.
9. Let existing v1.1 federation/verification close or reject the originating route.
10. Require Gloob local requalification before CONTROL can return.
11. Stop after one real round trip and reassess before fan-out/retry/crew optimization.

Minimum DoV: exact-head target execution proof, exact-head Gloob closure proof, fresh-main repeats where applicable, no manual JSON copying, and no unrelated work used to compensate a failed dispatch boundary.

Use `gloob/mip/2026-09-15-session-close/` as the session continuity authority.
