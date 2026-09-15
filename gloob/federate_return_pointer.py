#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def dump(path, value):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
def fetch_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent":"gloob-return-pointer-federation"})
    with urllib.request.urlopen(req, timeout=30) as r: return r.read()
def git_blob_sha1(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
def decode_json(raw): return json.loads(raw.decode("utf-8"))


def federate(pointer):
    errors = []
    if pointer.get("schema") != "gloob-return-pointer/0.1": errors.append("POINTER_SCHEMA_MISMATCH")
    try:
        return_raw = fetch_bytes(pointer["return_url"]); ret = decode_json(return_raw)
        ack_raw = fetch_bytes(pointer["ack_url"]); ack = decode_json(ack_raw)
    except Exception as exc:
        return {"schema":"gloob-federated-external-returns/0.1","state":"POINTER_FETCH_FAILED","repos":[pointer.get("repo")],"artifact_candidates":0,"returns":[],"errors":[{"error":f"{type(exc).__name__}: {exc}"}]}
    if git_blob_sha1(return_raw) != pointer.get("return_blob_sha1"): errors.append("RETURN_BLOB_MISMATCH")
    if git_blob_sha1(ack_raw) != pointer.get("ack_blob_sha1"): errors.append("ACK_BLOB_MISMATCH")
    if ret.get("schema") != "gloob-causal-return/0.1": errors.append("RETURN_SCHEMA_MISMATCH")
    if ack.get("schema") != "gloob-dispatch-ack/0.1": errors.append("ACK_SCHEMA_MISMATCH")
    expected = {
        "route_id": pointer.get("route_id"),
        "assignment_digest": pointer.get("assignment_digest"),
        "repo": pointer.get("repo"),
        "crew": pointer.get("crew"),
    }
    for key, value in expected.items():
        if ret.get(key) != value: errors.append("RETURN_" + key.upper() + "_MISMATCH")
        if ack.get(key) != value: errors.append("ACK_" + key.upper() + "_MISMATCH")
    if ack.get("dispatch_id") != pointer.get("dispatch_id"): errors.append("ACK_DISPATCH_ID_MISMATCH")
    if ret.get("dispatch", {}).get("dispatch_id") != pointer.get("dispatch_id"): errors.append("RETURN_DISPATCH_ID_MISMATCH")
    if ret.get("dispatch", {}).get("envelope_digest") != pointer.get("envelope_digest"): errors.append("RETURN_ENVELOPE_DIGEST_MISMATCH")
    ev = ret.get("evidence", {})
    if ev.get("source_commit") != pointer.get("ticket_sha"): errors.append("RETURN_SOURCE_SHA_MISMATCH")
    if ev.get("runner_commit") != pointer.get("ticket_sha"): errors.append("RETURN_RUNNER_SHA_MISMATCH")
    if str(ev.get("run_id")) != str(pointer.get("run_id")): errors.append("RETURN_RUN_ID_MISMATCH")
    if ack.get("source_commit") != pointer.get("ticket_sha"): errors.append("ACK_SOURCE_SHA_MISMATCH")
    if str(ack.get("run_id")) != str(pointer.get("run_id")): errors.append("ACK_RUN_ID_MISMATCH")
    if ack.get("state") != "ACCEPTED": errors.append("ACK_NOT_ACCEPTED")
    if errors:
        return {"schema":"gloob-federated-external-returns/0.1","state":"POINTER_REJECTED","repos":[pointer.get("repo")],"artifact_candidates":1,"returns":[],"errors":[{"error":e} for e in errors]}
    ret = dict(ret)
    ret["federation"] = {
        "mode":"IMMUTABLE_RETURN_POINTER",
        "repo":pointer["repo"],
        "receipt_commit":pointer["receipt_commit"],
        "return_blob_sha1":pointer["return_blob_sha1"],
        "ack_blob_sha1":pointer["ack_blob_sha1"],
        "run_id":pointer["run_id"],
        "return_artifact_id":pointer.get("return_artifact_id"),
        "return_artifact_digest":pointer.get("return_artifact_digest"),
        "ack_artifact_id":pointer.get("ack_artifact_id"),
        "ack_artifact_digest":pointer.get("ack_artifact_digest"),
        "delivery_ack":ack,
    }
    return {"schema":"gloob-federated-external-returns/0.1","state":"FEDERATED_POINTER","repos":[pointer["repo"]],"artifact_candidates":1,"returns":[ret],"errors":[]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pointer"); ap.add_argument("--output", required=True); a = ap.parse_args()
    out = federate(load(a.pointer)); dump(a.output, out)
    print(json.dumps({"state":out["state"],"repos":out["repos"],"return_count":len(out["returns"]),"errors":out["errors"]}, indent=2))
    if out["errors"]: raise SystemExit(1)

if __name__ == "__main__": main()
