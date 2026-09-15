#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_POLICY = ROOT / "control" / "dispatch-policy.json"


def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def dump(path, value): Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def dispatch_id(route, target_repo):
    return "DISPATCH-" + digest({
        "route_id": route["route_id"],
        "assignment_digest": route["assignment_digest"],
        "target_repo": target_repo,
        "crew": route["crew"],
    })[:16].upper()


def envelope(route, target_repo, transport_mode="IMMUTABLE_GLOOB_POINTER", pilot=False):
    body = {
        "schema": "gloob-dispatch-envelope/0.1",
        "dispatch_id": dispatch_id(route, target_repo),
        "route_id": route["route_id"],
        "assignment_digest": route["assignment_digest"],
        "entity_id": route["entity_id"],
        "cause": route["cause"],
        "books": route.get("books", []),
        "target_repo": target_repo,
        "crew": route["crew"],
        "opened_from_source_commit": route.get("opened_from_source_commit"),
        "causal_fingerprint": route.get("causal_fingerprint"),
        "transport": {"mode": transport_mode, "pilot": bool(pilot)},
        "required_ack": {"schema": "gloob-dispatch-ack/0.1"},
        "required_return": {
            "schema": "gloob-causal-return/0.1",
            "outcomes": ["RESOLVED", "DEFERRED", "REJECTED_BY_OWNER"],
        },
    }
    body["envelope_digest"] = digest(body)
    return body


def validate_envelope(value, policy):
    errors = []
    if value.get("schema") != "gloob-dispatch-envelope/0.1": errors.append("SCHEMA_MISMATCH")
    for key in ("dispatch_id", "route_id", "assignment_digest", "target_repo", "crew", "envelope_digest"):
        if not value.get(key): errors.append("MISSING_" + key.upper())
    mode = value.get("transport", {}).get("mode")
    if mode not in policy.get("transport_modes", []): errors.append("TRANSPORT_MODE_UNSUPPORTED")
    claimed = value.get("envelope_digest")
    unsigned = dict(value); unsigned.pop("envelope_digest", None)
    if claimed and claimed != digest(unsigned): errors.append("ENVELOPE_DIGEST_MISMATCH")
    return errors


def plan(route_plan, policy, transport_mode="IMMUTABLE_GLOOB_POINTER"):
    envelopes = []
    for route in route_plan.get("assignments", []):
        for repo in route.get("repos", []):
            e = envelope(route, repo, transport_mode=transport_mode)
            errors = validate_envelope(e, policy)
            if errors: raise ValueError({"route_id": route.get("route_id"), "errors": errors})
            envelopes.append(e)
    return {
        "schema": "gloob-dispatch-plan/0.1",
        "policy_id": policy["policy_id"],
        "mode": "CAUSE_BOUND_DISPATCH_ONLY",
        "dispatch_count": len(envelopes),
        "envelopes": envelopes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("route_plan")
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    ap.add_argument("--transport-mode", default="IMMUTABLE_GLOOB_POINTER")
    ap.add_argument("--output", default=str(ROOT / "control" / "generated" / "dispatch-plan.json"))
    args = ap.parse_args()
    out = plan(load(args.route_plan), load(args.policy), args.transport_mode)
    dump(args.output, out)


if __name__ == "__main__": main()
