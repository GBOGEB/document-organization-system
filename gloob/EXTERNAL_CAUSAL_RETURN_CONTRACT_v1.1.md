# External Causal Return Contract v1.1

## Purpose

A cause-bound Gloob route is not manually acknowledged. It becomes an external handshake, is executed by the implicated repository/crew, returns exact-SHA runtime evidence, and is automatically dispositioned by Gloob.

## State machine

```text
CAUSAL_ESCALATE
  -> OPEN_BOUNDED_WORK
  -> EXTERNAL_RETURN_REQUIRED
       -> no return                    -> AWAITING_EXTERNAL_RETURN
       -> invalid/stale/zero-step      -> REJECT_RETURN -> KEEP_ROUTE_OPEN
       -> DEFERRED                     -> RETURN_ACCEPTED_DEFERRED -> KEEP_ROUTE_OPEN
       -> REJECTED_BY_OWNER            -> RETURN_ACCEPTED_OWNER_REJECT -> CAUSAL_TRIAGE
       -> RESOLVED + exact-SHA proof   -> RETURN_ACCEPTED_REQUALIFY
                                          -> close external route
                                          -> start local causal requalification
                                          -> CONTROL only after local qualification
```

An external return never grants CONTROL directly.

## Handshake

Each route has deterministic `route_id` and `assignment_digest`. The handshake identifies the entity, causal class, Book, target repository set, crew, opening source commit, causal fingerprint, and required return fields.

## Return artifact

The target repository publishes an Actions artifact named `gloob-causal-return` containing JSON with schema `gloob-causal-return/0.1`:

```json
{
  "schema": "gloob-causal-return/0.1",
  "route_id": "ROUTE-...",
  "assignment_digest": "...",
  "repo": "GBOGEB/example",
  "crew": "SOURCE_EVIDENCE_CREW",
  "outcome": "RESOLVED",
  "evidence": {
    "source_commit": "40-hex-sha",
    "runner_commit": "same-40-hex-sha",
    "run_id": "123",
    "steps": 8,
    "conclusion": "success"
  }
}
```

Accepted outcomes are `RESOLVED`, `DEFERRED`, and `REJECTED_BY_OWNER`.

## Verification

Gloob rejects a return unless route ID, assignment digest, repository, crew, exact SHA, run ID, positive executed step count, and successful conclusion all bind to the open handshake.

## Federation

`federate_external_returns.py` queries only repositories addressed by currently open handshakes. No open handshake means no cross-repository call. Matching return artifacts are deduplicated by route, evidence SHA and outcome and passed to `external_causal_return.py`.

The resulting `external-return-ledger.json` and `route-closure-plan.json` are included in `gloob-control-receipts` so subsequent control history contains the causal-return disposition.

## Outputs

- `external-handshake-plan.json`
- `federated-external-returns.json`
- `external-return-ledger.json`
- `route-closure-plan.json`

The live unchanged CONTROL baseline must emit zero handshakes, zero returns and zero closure actions.
