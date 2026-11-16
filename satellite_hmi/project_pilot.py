"""Read-only five-Project pilot intake. An adapter, NOT a session/DAG engine.

Consumer: existing Hub lsaf schemas, existing satellite_hmi/render.py.
A screenshot is a selection assertion, NOT a ChatGPT Project export.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

CONTRACT = "gbogeb.chatgpt-project-cohort/1"
IDS = tuple(f"P{i}" for i in range(1, 6))
STATES = {"SOURCE_SELECTED", "RESERVED", "CAPTURED_UNVERIFIED", "SOURCE_HASH_VERIFIED", "SOURCE_HOLD"}
TARGETS = {
    "GBOGEB/document-organization-system",
    "GBOGEB/pipeline-automation-hub",
    "GBOGEB/GEMINI",
}


def _read_no_duplicate_keys(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("Duplicate JSON key")
        out[k] = v
    return out


def read_cohort(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_read_no_duplicate_keys)


def assess(cohort: dict) -> dict:
    if not isinstance(cohort, dict) or cohort.get("schema") != CONTRACT:
        raise ValueError("Wrong cohort contract")
    if cohort.get("auto_merge") is not False or cohort.get("auto_delete") is not False or cohort.get("authority_transfer") is not False:
        raise ValueError("Prohibited automatic actions")
    rows = cohort.get("projects")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("Exactly five pilot slots required")
    if sorted(r.get("id") for r in rows if isinstance(r, dict)) != list(IDS):
        raise ValueError("Missing or duplicate pilot IDs")
    results = []
    for r in rows:
        if not isinstance(r, dict):
            raise ValueError("Invalid project row")
        status = r.get("status")
        if status not in STATES:
            raise ValueError("Unknown status")
        if r.get("target_repo") not in TARGETS:
            raise ValueError("Unknown owner repository")
        if r.get("capture_kind") not in {None, "HANDOVER_ONLY", "FULL_EXPORT", "SOURCE_FILE"}:
            raise ValueError("Invalid capture kind")
        hashes = r.get("source_hashes", [])
        if not isinstance(hashes, list):
            raise ValueError("Invalid source hashes")
        if any(not isinstance(s, str) or len(s) != 64 or any(c not in "0123456789abcdef" for c in s) for s in hashes):
            raise ValueError("Invalid digest")
        if r.get("source_id_verified") is True and not r.get("original_project_id"):
            raise ValueError("Unbound original project identity")
        if status == "RESERVED" and (r.get("original_project_id") or hashes or r.get("source_id_verified")):
            raise ValueError("Reserved slot cannot have source assertions")
        # A hash of a handover file says nothing about lossless original chat reconstruction.
        original_verified = bool(r.get("source_id_verified")) and bool(hashes) and r.get("capture_kind") == "FULL_EXPORT" and r.get("full_export_coverage_verified") is True
        results.append({
            "id": r["id"], "state": status, "source_status": "SOURCE_PROOF_CANDIDATE" if original_verified else "SOURCE_PROOF_HOLD",
            "ready_for_source_admission": False,
            "source_identity_verified": r.get("source_id_verified") is True,
            "raw_export_coverage_verified": r.get("full_export_coverage_verified") is True,
            "target_repo": r["target_repo"],
        })
    return {
        "schema": "gbogeb.chatgpt-project-receipt/1",
        "cohort_id": cohort.get("cohort_id"),
        "pilot_count": 5, "selected_count": sum(r["state"] != "RESERVED" for r in results),
        "source_admitted": 0, "merge_authorized": False, "delete_authorized": False,
        "state": "PILOT_INCEPTION_SOURCE_PROOF_PENDING", "results": results,
    }


def public_hmi(receipt: dict) -> dict:
    return {
        "schema_version": "satellite-hmi/1",
        "worktree_id": "ChatGPT Project handover five-pilot cohort",
        "source_as_of": "2026-11-16",
        "entries": [
            {
                "id": r["id"], "title": f"Project pilot {r['id']}",
                "group": "Five-Project cohort", "status": "BLOCKED" if r["state"] != "RESERVED" else "UNVERIFIED",
                "detail": f"{r['state']}; source admission withheld",
                "url": "https://github.com/GBOGEB/pipeline-automation-hub/issues/1230"
            } for r in receipt["results"]
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cohort", type=Path)
    p.add_argument("--receipt", type=Path)
    p.add_argument("--projection", type=Path)
    args = p.parse_args()
    result = assess(read_cohort(args.cohort))
    if args.receipt:
        args.receipt.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if args.projection:
        args.projection.write_text(json.dumps(public_hmi(result), sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())