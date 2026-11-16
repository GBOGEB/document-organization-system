#!/usr/bin/env python3
"""Validator for the Master Document Transmittal Table contract.

Standard library only (same convention as contracts/data_rich_document).
transmittal.schema.json is the shape contract; this module re-checks shape
without a third-party JSON Schema engine and adds the cross-row invariants
JSON Schema cannot express:

  INV-T1  Functional name lock: Functional_Name must equal registry[Prefix],
          so a row cannot revert to an author-based or ad-hoc name.
  INV-T2  (Prefix, Version) is unique.
  INV-T3  Latest ALX + date prevails: per prefix, the highest Version is the
          current row, and its Date may not be older than any earlier row.
  INV-T4  Approved_PDF_Flag = true requires MIN, ALX_ID and Date.
  GATE-5  Transmittal MIN population: COMPLETE only when every current row
          has MIN, ALX_ID and Date. Otherwise BLOCKED_INPUT, listing gaps.

Exit codes: 0 = valid (Gate 5 may still be BLOCKED_INPUT and is reported),
1 = contract violation, 2 = valid but --require-gate5 given and Gate 5 blocked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PREFIX_RE = re.compile(r"^\[AD_(\d{2})\]$")
FUNC_RE = re.compile(r"^AD_(\d{2})_[A-Z][A-Za-z0-9]*(_[A-Za-z0-9]+)*$")
ALX_RE = re.compile(r"^\d{8}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_RE = re.compile(r"^v(\d{2})$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
PLACEHOLDER_MIN = {"TBD", "tbd", "N/A", "-", "?"}

ROW_FIELDS = (
    "Prefix",
    "Functional_Name",
    "MIN",
    "ALX_ID",
    "Date",
    "Version",
    "Approved_PDF_Flag",
)
ROW_OPTIONAL = ("Note",)

# Contractor-facing export name: [AD_13]_AD_13_MCS_Secondary_Interface_Catalogue_v01.pdf
FILENAME_RE = re.compile(
    r"^(\[AD_(\d{2})\])_(AD_\d{2}_[A-Z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)*)_(v\d{2})\.pdf$"
)


def contractor_filename(row: Dict[str, Any]) -> str:
    return f"{row['Prefix']}_{row['Functional_Name']}_{row['Version']}.pdf"


def _shape_errors(data: Any) -> List[str]:
    errors: List[str] = []
    if not isinstance(data, dict):
        return ["top level must be an object"]

    allowed_top = {"schema_version", "alx_folder", "registry", "rows"}
    for key in sorted(set(data) - allowed_top):
        errors.append(f"unexpected top-level key {key!r}")
    for key in sorted(allowed_top - set(data)):
        errors.append(f"missing top-level key {key!r}")
    if errors:
        return errors

    if not isinstance(data["schema_version"], str) or not SEMVER_RE.match(data["schema_version"]):
        errors.append("schema_version must be MAJOR.MINOR.PATCH")
    if not isinstance(data["alx_folder"], str) or not ALX_RE.match(data["alx_folder"]):
        errors.append("alx_folder must be an 8-digit ALX number")

    registry = data["registry"]
    if not isinstance(registry, dict) or not registry:
        errors.append("registry must be a non-empty object")
    else:
        for prefix, name in registry.items():
            m = PREFIX_RE.match(prefix)
            if not m:
                errors.append(f"registry key {prefix!r} is not of the form [AD_##]")
                continue
            if not isinstance(name, str) or not FUNC_RE.match(name):
                errors.append(f"registry[{prefix}] {name!r} is not a functional name AD_##_Name")
            elif FUNC_RE.match(name).group(1) != m.group(1):
                errors.append(f"registry[{prefix}] {name!r} number does not match its prefix")

    rows = data["rows"]
    if not isinstance(rows, list) or not rows:
        errors.append("rows must be a non-empty array")
        return errors

    for i, row in enumerate(rows):
        where = f"rows[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{where} must be an object")
            continue
        for key in sorted(set(row) - set(ROW_FIELDS) - set(ROW_OPTIONAL)):
            errors.append(f"{where}: unexpected field {key!r}")
        for key in ROW_FIELDS:
            if key not in row:
                errors.append(f"{where}: missing field {key!r}")
        if any(k not in row for k in ROW_FIELDS):
            continue

        if not isinstance(row["Prefix"], str) or not PREFIX_RE.match(row["Prefix"]):
            errors.append(f"{where}: Prefix {row['Prefix']!r} is not [AD_##]")
        if not isinstance(row["Functional_Name"], str) or not FUNC_RE.match(row["Functional_Name"]):
            errors.append(f"{where}: Functional_Name {row['Functional_Name']!r} is not AD_##_Name")

        mn = row["MIN"]
        if mn is not None and (not isinstance(mn, str) or not mn.strip() or mn.strip() in PLACEHOLDER_MIN):
            errors.append(f"{where}: MIN must be a real value or null (placeholders like 'TBD' are not allowed)")
        alx = row["ALX_ID"]
        if alx is not None and (not isinstance(alx, str) or not ALX_RE.match(alx)):
            errors.append(f"{where}: ALX_ID {alx!r} must be an 8-digit string or null")
        date = row["Date"]
        if date is not None and (not isinstance(date, str) or not DATE_RE.match(date)):
            errors.append(f"{where}: Date {date!r} must be YYYY-MM-DD or null")
        if not isinstance(row["Version"], str) or not VERSION_RE.match(row["Version"]):
            errors.append(f"{where}: Version {row['Version']!r} must be vNN")
        if not isinstance(row["Approved_PDF_Flag"], bool):
            errors.append(f"{where}: Approved_PDF_Flag must be boolean")
        if "Note" in row and not isinstance(row["Note"], str):
            errors.append(f"{where}: Note must be a string")
    return errors


def _current_rows(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    current: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        p = row["Prefix"]
        if p not in current or row["Version"] > current[p]["Version"]:
            current[p] = row
    return current


def validate_transmittal(data: Any) -> Tuple[List[str], Dict[str, Any]]:
    """Return (errors, gate5_report). Errors empty means the contract holds."""
    errors = _shape_errors(data)
    if errors:
        return errors, {"status": "NOT_EVALUATED", "missing": []}

    registry: Dict[str, str] = data["registry"]
    rows: List[Dict[str, Any]] = data["rows"]

    seen: Dict[Tuple[str, str], int] = {}
    for i, row in enumerate(rows):
        where = f"rows[{i}] {row['Prefix']} {row['Version']}"

        # INV-T1
        locked = registry.get(row["Prefix"])
        if locked is None:
            errors.append(f"{where}: prefix not in registry")
        elif row["Functional_Name"] != locked:
            errors.append(
                f"{where}: Functional_Name {row['Functional_Name']!r} does not match locked name {locked!r}"
            )

        # INV-T2
        key = (row["Prefix"], row["Version"])
        if key in seen:
            errors.append(f"{where}: duplicate of rows[{seen[key]}]")
        else:
            seen[key] = i

        # INV-T4
        if row["Approved_PDF_Flag"]:
            missing = [f for f in ("MIN", "ALX_ID", "Date") if row[f] is None]
            if missing:
                errors.append(f"{where}: Approved_PDF_Flag=true but missing {', '.join(missing)}")

    # INV-T3
    current = _current_rows(rows)
    for prefix, cur in current.items():
        if cur["Date"] is None:
            continue
        for row in rows:
            if row["Prefix"] == prefix and row is not cur and row["Date"] and row["Date"] > cur["Date"]:
                errors.append(
                    f"{prefix}: current {cur['Version']} dated {cur['Date']} is older than "
                    f"{row['Version']} dated {row['Date']} (latest ALX + date must prevail)"
                )

    # GATE-5
    gaps = []
    for prefix in sorted(current):
        cur = current[prefix]
        missing = [f for f in ("MIN", "ALX_ID", "Date") if cur[f] is None]
        if missing:
            gaps.append({"prefix": prefix, "version": cur["Version"], "missing": missing})
    gate5 = {"status": "COMPLETE" if not gaps else "BLOCKED_INPUT", "missing": gaps}
    return errors, gate5


def check_filename(name: str, registry: Dict[str, str]) -> Optional[str]:
    """Return an error string if an exported PDF name breaks the convention, else None."""
    m = FILENAME_RE.match(name)
    if not m:
        return f"{name!r}: not of the form [AD_##]_AD_##_Functional_Name_vNN.pdf"
    prefix, num, func, _ver = m.groups()
    if not func.startswith(f"AD_{num}_"):
        return f"{name!r}: functional name number does not match prefix {prefix}"
    locked = registry.get(prefix)
    if locked is None:
        return f"{name!r}: prefix {prefix} not in registry"
    if func != locked:
        return f"{name!r}: name {func!r} does not match locked name {locked!r}"
    return None


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("transmittal", type=Path, help="transmittal JSON file")
    ap.add_argument("--filenames", type=Path, help="text file, one exported PDF name per line, to check")
    ap.add_argument("--require-gate5", action="store_true", help="exit 2 if Gate 5 is not COMPLETE")
    args = ap.parse_args(argv)

    data = json.loads(args.transmittal.read_text(encoding="utf-8"))
    errors, gate5 = validate_transmittal(data)

    if args.filenames and not errors:
        for line in args.filenames.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                err = check_filename(line, data["registry"])
                if err:
                    errors.append(err)

    report = {"valid": not errors, "errors": errors, "gate_5": gate5}
    if not errors:
        report["expected_filenames"] = [contractor_filename(r) for r in _current_rows(data["rows"]).values()]
    print(json.dumps(report, indent=2))

    if errors:
        return 1
    if args.require_gate5 and gate5["status"] != "COMPLETE":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
