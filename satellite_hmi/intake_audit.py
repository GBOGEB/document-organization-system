"""Read-only, fail-closed audit of external tranche handovers.

This adapter does not hydrate, delete, merge, publish, schedule, or approve sources.
The existing satellite_hmi/render.py owns HTML; Hub/CODEX own federation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

TRANCHES = tuple(f"Tranche_{letter}" for letter in "ABCDEFGH")
FIELDS = ("rows", "unique", "safe_to_delete", "hold_or_keep")
TOTALS = {
    "rows": "total_sidebar_rows_inspected",  # optional in JSON v3; YAML may contain one
    "unique": "unique_chats",
    "safe_to_delete": "safe_to_delete",
    "hold_or_keep": "keep_or_verify",
}
YAML_TOTALS = {
    "rows": "total_sidebar_rows_inspected",
    "unique": "unique_chats_audited",
    "safe_to_delete": "safe_to_delete_immediately",
    "hold_or_keep": "keep_or_verify_locally_count",
}
DIGEST = re.compile(r"[0-9a-fA-F]{64}\Z")


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)


def safe_relative(name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError("Unsafe inventory path")
    p = PurePosixPath(name)
    if p.is_absolute() or any(part in (".", "..", "") for part in name.split("/")):
        raise ValueError("Unsafe inventory path")
    return Path(*p.parts)


def verify_inventory(inventory: dict, source_root: Path) -> list[str]:
    """Verify independently provided sha256 hashes against actual source bytes."""
    if not isinstance(inventory, dict) or not inventory or len(inventory) > 2000:
        raise ValueError("Non-empty bounded inventory object required")
    root = source_root.resolve(strict=True)
    issues = []
    total_size = 0
    for name, expected in sorted(inventory.items()):
        path = safe_relative(name)
        if not isinstance(expected, str) or not DIGEST.fullmatch(expected):
            raise ValueError("Invalid SHA-256 in inventory")
        target = root / path
        if any((root / Path(*path.parts[:i])).is_symlink() for i in range(1, len(path.parts) + 1)):
            raise ValueError("Symlink target refused")
        if not target.is_file() or not target.resolve().is_relative_to(root):
            issues.append(f"MISSING_OR_OUTSIDE:{name}")
            continue
        size = target.stat().st_size
        total_size += size
        if size > 10 * 1024 * 1024 or total_size > 50 * 1024 * 1024:
            raise ValueError("Inventory size limit exceeded")
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected.lower():
            issues.append(f"SHA_MISMATCH:{name}")
    return issues


def _yaml_scalar(text: str, key: str):
    # Only audits explicitly named scalar fields; it is NOT a general YAML parser.
    matches = re.findall(rf"^  {re.escape(key)}:\s*(\d+)\s*$", text, re.MULTILINE)
    return int(matches[0]) if len(matches) == 1 else None


def audit(manifest: dict, yaml_text: str | None = None, inventory_issues: list[str] | None = None) -> dict:
    if not isinstance(manifest, dict) or not isinstance(manifest.get("tranche_counts"), dict):
        raise ValueError("Missing tranche_counts object")
    counts = manifest["tranche_counts"]
    if not all(key in counts for key in TRANCHES):
        raise ValueError("Tranches A-H all required")
    issues = []
    sums = dict.fromkeys(FIELDS, 0)
    for tranche in TRANCHES:
        row = counts[tranche]
        if not isinstance(row, dict):
            raise ValueError("Tranche must be an object")
        for field in FIELDS:
            value = row.get(field)
            if type(value) is not int or value < 0:
                raise ValueError(f"Invalid count {tranche}.{field}")
            sums[field] += value
        if row["unique"] > row["rows"] or row["safe_to_delete"] + row["hold_or_keep"] != row["unique"]:
            issues.append(f"ROW_CONFLICT:{tranche}")
    declared = {}
    for field, key in TOTALS.items():
        val = counts.get(key) if key is not None else None
        declared[field] = val
        if val is None:
            issues.append(f"DECLARED_MISSING:{field}")
        elif type(val) is not int or val < 0:
            raise ValueError(f"Invalid declared total: {key}")
        elif val != sums[field]:
            issues.append(f"TOTAL_CONFLICT:{field}")
    if sums["unique"] > sums["rows"]:
        issues.append("UNIQUE_EXCEEDS_ROWS")
    if yaml_text is not None:
        for field, key in YAML_TOTALS.items():
            observed = _yaml_scalar(yaml_text, key)
            if observed is None:
                issues.append(f"YAML_MISSING_OR_AMBIGUOUS:{key}")
            elif observed != sums[field]:
                issues.append(f"YAML_CONFLICT:{field}")
    if inventory_issues is None:
        issues.append("INDEPENDENT_SOURCE_HASHES_NOT_VERIFIED")
    else:
        issues.extend(inventory_issues)
    # Source-hash success alone never proves reconstructed chat bodies or deletion safety.
    issues.append("LOSSLESS_CHAT_RECONSTRUCTION_NOT_VERIFIED")
    return {
        "contract": "gbogeb.external-handover-audit/1",
        "authority_transfer": False,
        "merge_authorized": False,
        "delete_authorized": False,
        "actual_totals": sums,
        "declared_totals": declared,
        "issues": sorted(set(issues)),
        "status": "HOLD_SOURCE_ACCOUNTING" if any(x.startswith(("TOTAL_CONFLICT", "ROW_CONFLICT", "YAML_CONFLICT", "DECLARED_MISSING")) for x in issues) else "HOLD_SOURCE_PROOF",
        "eligible_deletions": 0,
    }


def public_projection(receipt: dict, source_as_of: str = "UNVERIFIED") -> dict:
    # Metadata-only; do not export private Drive identifiers, chat titles or contents.
    return {
        "schema_version": "satellite-hmi/1",
        "worktree_id": "External Tranche Handover — read-only integration gate",
        "source_as_of": source_as_of,
        "entries": [
            {"id": "handover-audit", "title": "Tranche A-H intake audit", "group": "01 Source", "status": "BLOCKED", "detail": receipt["status"] + ": source accounting and retention not admitted"},
            {"id": "satellite-owner", "title": "Satellite HMI owner", "group": "02 Integration", "status": "VERIFIED_METADATA", "url": "https://github.com/GBOGEB/document-organization-system/issues/84", "detail": "Reuse existing renderer and guarded hydrator; no new bus"},
            {"id": "federation-owner", "title": "Hub federation owner", "group": "02 Integration", "status": "OPEN", "url": "https://github.com/GBOGEB/pipeline-automation-hub/pull/1209", "detail": "Existing OID crosswalk; admission independently qualified"},
            {"id": "session-owner", "title": "Session recovery owner", "group": "03 Governance", "status": "BLOCKED", "url": "https://github.com/GBOGEB/pipeline-automation-hub/issues/1230", "detail": "Original reconstruction and individual proof required before deletion"},
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--yaml", type=Path, help="Optional original Handover.glob.yaml for scalar cross-check")
    ap.add_argument("--inventory", type=Path, help="Independent JSON path-to-sha256 inventory")
    ap.add_argument("--source-root", type=Path, help="Root for file integrity verification")
    ap.add_argument("--receipt", type=Path, help="Write local redacted result JSON")
    ap.add_argument("--projection", type=Path, help="Write public-safe renderer input JSON")
    ap.add_argument("--strict", action="store_true", help="Exit 2 while any admission hold remains")
    args = ap.parse_args()
    if bool(args.inventory) != bool(args.source_root):
        ap.error("--inventory and --source-root must be supplied together")
    evidence = verify_inventory(read_json(args.inventory), args.source_root) if args.inventory else None
    receipt = audit(read_json(args.manifest), args.yaml.read_text(encoding="utf-8") if args.yaml else None, evidence)
    output = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.write_text(output, encoding="utf-8")
    if args.projection:
        args.projection.write_text(json.dumps(public_projection(receipt), indent=2) + "\n", encoding="utf-8")
    print(output, end="")
    return 2 if args.strict and receipt["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())