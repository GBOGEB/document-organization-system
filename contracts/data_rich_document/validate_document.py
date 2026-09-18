#!/usr/bin/env python3
"""Semantic validator for the GBOGEB data-rich document contract.

This intentionally uses only the Python standard library. JSON Schema validates
shape; this module validates cross-object invariants that JSON Schema cannot
express cleanly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


def _walk_outline(nodes: List[Dict[str, Any]], parent: str | None = None):
    for node in nodes:
        section_id = node["section_id"]
        yield section_id, parent
        yield from _walk_outline(node.get("children", []), section_id)


def _register_id(seen: Dict[str, str], value: str, kind: str, errors: List[str]) -> None:
    if value in seen:
        errors.append(f"duplicate id {value!r}: {seen[value]} and {kind}")
    else:
        seen[value] = kind


def validate_document(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    required_top = {
        "schema_version",
        "document",
        "outline",
        "sections",
        "requirements",
        "relations",
        "external_references",
        "change_sets",
        "history",
        "render_profiles",
    }
    missing = sorted(required_top - set(data))
    if missing:
        return [f"missing top-level keys: {', '.join(missing)}"]

    document = data["document"]
    sections = data["sections"]
    requirements = data["requirements"]
    relations = data["relations"]
    external_refs = data["external_references"]
    change_sets = data["change_sets"]
    history = data["history"]
    render_profiles = data["render_profiles"]

    seen: Dict[str, str] = {}
    _register_id(seen, document["id"], "document", errors)

    section_by_id: Dict[str, Dict[str, Any]] = {}
    block_by_id: Dict[str, Dict[str, Any]] = {}
    for section in sections:
        sid = section["id"]
        _register_id(seen, sid, "section", errors)
        section_by_id[sid] = section
        for block in section.get("content_blocks", []):
            bid = block["id"]
            _register_id(seen, bid, "content_block", errors)
            block_by_id[bid] = block

    requirement_by_id = {}
    for req in requirements:
        rid = req["id"]
        _register_id(seen, rid, "requirement", errors)
        requirement_by_id[rid] = req

    relation_by_id = {}
    for rel in relations:
        rid = rel["id"]
        _register_id(seen, rid, "relation", errors)
        relation_by_id[rid] = rel

    external_by_id = {}
    for ref in external_refs:
        rid = ref["id"]
        _register_id(seen, rid, "external_reference", errors)
        external_by_id[rid] = ref

    change_by_id = {}
    for change in change_sets:
        cid = change["id"]
        _register_id(seen, cid, "change_set", errors)
        change_by_id[cid] = change

    history_by_id = {}
    for event in history:
        hid = event["id"]
        _register_id(seen, hid, "history_event", errors)
        history_by_id[hid] = event

    for profile in render_profiles:
        _register_id(seen, profile["id"], "render_profile", errors)

    all_ids: Set[str] = set(seen)

    # Section parentage, depth and sibling ranks.
    sibling_ranks: Dict[str | None, Dict[int, str]] = {}
    for sid, section in section_by_id.items():
        placement = section["placement"]
        parent = placement.get("parent_section_id")
        rank = placement["rank"]
        ranks = sibling_ranks.setdefault(parent, {})
        if rank in ranks:
            errors.append(
                f"sibling rank collision under {parent!r}: "
                f"{ranks[rank]} and {sid} both use {rank}"
            )
        else:
            ranks[rank] = sid

        level = section["heading_level"]
        if parent is None:
            if level != 1:
                errors.append(f"{sid}: root section must have heading_level 1")
        elif parent not in section_by_id:
            errors.append(f"{sid}: parent section {parent!r} does not exist")
        else:
            expected = section_by_id[parent]["heading_level"] + 1
            if level != expected:
                errors.append(
                    f"{sid}: heading_level {level} does not follow parent "
                    f"{parent} level {expected - 1}"
                )

        for neighbor_key in ("after_section_id", "before_section_id"):
            neighbor = placement.get(neighbor_key)
            if neighbor is not None and neighbor not in section_by_id:
                errors.append(f"{sid}: {neighbor_key} {neighbor!r} does not exist")

    # Parent cycles.
    for sid in section_by_id:
        chain: Set[str] = set()
        cursor: str | None = sid
        while cursor is not None:
            if cursor in chain:
                errors.append(f"section hierarchy cycle detected at {cursor}")
                break
            chain.add(cursor)
            parent = section_by_id.get(cursor, {}).get("placement", {}).get("parent_section_id")
            cursor = parent if isinstance(parent, str) else None

    # Outline must contain every section exactly once and agree with parentage.
    outline_pairs = list(_walk_outline(data["outline"]))
    outline_ids = [sid for sid, _ in outline_pairs]
    if len(outline_ids) != len(set(outline_ids)):
        errors.append("outline contains duplicate section references")

    missing_in_outline = sorted(set(section_by_id) - set(outline_ids))
    unknown_in_outline = sorted(set(outline_ids) - set(section_by_id))
    if missing_in_outline:
        errors.append(f"sections missing from outline: {', '.join(missing_in_outline)}")
    if unknown_in_outline:
        errors.append(f"outline references unknown sections: {', '.join(unknown_in_outline)}")

    for sid, outline_parent in outline_pairs:
        if sid in section_by_id:
            declared_parent = section_by_id[sid]["placement"].get("parent_section_id")
            if declared_parent != outline_parent:
                errors.append(
                    f"{sid}: outline parent {outline_parent!r} != "
                    f"placement parent {declared_parent!r}"
                )

    # Outline order must follow sparse rank order among siblings.
    def check_order(nodes: List[Dict[str, Any]], parent: str | None = None) -> None:
        known = [n for n in nodes if n["section_id"] in section_by_id]
        observed = [n["section_id"] for n in known]
        expected = sorted(
            observed,
            key=lambda sid: section_by_id[sid]["placement"]["rank"],
        )
        if observed != expected:
            errors.append(
                f"outline order under {parent!r} does not follow section rank: "
                f"observed={observed}, expected={expected}"
            )
        for node in known:
            check_order(node.get("children", []), node["section_id"])

    check_order(data["outline"])

    # Requirement and block references.
    for req in requirements:
        rid = req["id"]
        for sid in req.get("section_ids", []):
            if sid not in section_by_id:
                errors.append(f"{rid}: unknown section_id reference {sid!r}")
        for ref in req.get("references", []):
            if ref not in all_ids:
                errors.append(f"{rid}: unresolved reference {ref!r}")
        for ref in req.get("verification", {}).get("evidence_refs", []):
            if ref not in all_ids:
                errors.append(f"{rid}: unresolved verification evidence {ref!r}")

    for sid, section in section_by_id.items():
        for block in section.get("content_blocks", []):
            bid = block["id"]
            for ref in block.get("source_refs", []):
                if ref not in all_ids:
                    errors.append(f"{bid}: unresolved source_ref {ref!r}")
            for ref in block.get("supersedes", []):
                if ref not in block_by_id:
                    errors.append(f"{bid}: supersedes unknown content block {ref!r}")

    # Relations are typed edges and therefore both endpoints must resolve.
    for rel in relations:
        for side in ("from", "to"):
            target = rel[side]
            if target not in all_ids:
                errors.append(f"{rel['id']}: unresolved {side} endpoint {target!r}")

    # Change sets must target existing stable identities. Reverts must resolve.
    for change in change_sets:
        cid = change["id"]
        revert = change.get("reverts_change_set")
        if revert is not None and revert not in change_by_id:
            errors.append(f"{cid}: reverts unknown change set {revert!r}")
        for op in change.get("changes", []):
            target = op["target_id"]
            if target not in all_ids:
                errors.append(f"{cid}: change targets unknown id {target!r}")
            path = op.get("path", "")
            if not path.startswith("/"):
                errors.append(f"{cid}: change path must start with '/': {path!r}")

    # Current release must be represented in semantic history.
    current_version = document["version"]
    history_versions = {event["document_version"] for event in history}
    if current_version not in history_versions:
        errors.append(
            f"current document version {current_version!r} is absent from history"
        )

    # Applied/reverted change sets must be traceable from at least one history event.
    history_change_ids = {
        cid for event in history for cid in event.get("change_set_ids", [])
    }
    for cid, change in change_by_id.items():
        if change["status"] in {"applied", "reverted"} and cid not in history_change_ids:
            errors.append(
                f"{cid}: status {change['status']!r} but no history event references it"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.document.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 2

    errors = validate_document(data)
    if errors:
        print(f"FAIL: {len(errors)} semantic invariant(s) violated")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "PASS: data-rich document semantic invariants "
        f"({data['document']['id']} v{data['document']['version']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
