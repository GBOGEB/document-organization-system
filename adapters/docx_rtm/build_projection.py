#!/usr/bin/env python3
"""Project canonical data-rich JSON into the existing DOCX_RTM Markdown intake.

The JSON document remains semantic SSOT. This module emits:
1. deterministic Markdown with unnumbered ATX headings;
2. an outward-document manifest carrying hashes, mapping and authority guards.

The generated Markdown is intended for the existing DOCX_RTM Pandoc path using
config/reference.docx so Word controls display numbering/styles.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ADAPTER_VERSION = "1.0.0"
MANIFEST_SCHEMA = "gbogeb.docx-rtm-outward-document-manifest/1.0.0"
DEFAULT_MAX_HEADING_LEVEL = 3
NUMBERED_TITLE_RE = re.compile(r"^\s*\d{1,3}(?:\.\d+)*[.)]?\s+")


class ProjectionError(ValueError):
    """Raised when authoritative input cannot be projected without ambiguity."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(data: Any) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_semantic_validator():
    validator_path = _repo_root() / "contracts" / "data_rich_document" / "validate_document.py"
    spec = importlib.util.spec_from_file_location("data_rich_document_validator", validator_path)
    if spec is None or spec.loader is None:
        raise ProjectionError(f"cannot load semantic validator: {validator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_document


def validate_source(data: Dict[str, Any]) -> None:
    errors = _load_semantic_validator()(data)
    if errors:
        joined = "\n- ".join(errors)
        raise ProjectionError(f"source JSON failed semantic validation:\n- {joined}")


def flatten_outline(nodes: List[Dict[str, Any]]) -> Iterable[str]:
    for node in nodes:
        yield node["section_id"]
        yield from flatten_outline(node.get("children", []))


def _yaml_quote(value: str) -> str:
    # JSON double-quoted strings are valid YAML scalar syntax.
    return json.dumps(value, ensure_ascii=False)


def _anchor(value: str) -> str:
    return value.lower()


def _section_lookup(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {section["id"]: section for section in data["sections"]}


def _requirements_by_primary_section(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    result: Dict[str, List[Dict[str, Any]]] = {}
    section_ids = {section["id"] for section in data["sections"]}
    for req in data["requirements"]:
        placements = req.get("section_ids", [])
        if not placements:
            raise ProjectionError(f"{req['id']}: requirement has no section placement")
        primary = placements[0]
        if primary not in section_ids:
            raise ProjectionError(f"{req['id']}: primary section {primary!r} does not exist")
        result.setdefault(primary, []).append(req)
    for requirements in result.values():
        requirements.sort(key=lambda item: item["id"])
    return result


def _validate_projection_contract(
    data: Dict[str, Any],
    max_heading_level: int,
) -> None:
    if max_heading_level < 1 or max_heading_level > 6:
        raise ProjectionError("max_heading_level must be between 1 and 6")

    sections = _section_lookup(data)
    for section_id in flatten_outline(data["outline"]):
        section = sections[section_id]
        level = int(section["heading_level"])
        if level > max_heading_level:
            raise ProjectionError(
                f"{section_id}: heading_level {level} exceeds projection maximum "
                f"{max_heading_level}"
            )
        if NUMBERED_TITLE_RE.match(section["title"]):
            raise ProjectionError(
                f"{section_id}: title appears to contain rendered numbering: "
                f"{section['title']!r}; numbering belongs to the Word template"
            )

    _requirements_by_primary_section(data)


def _render_content_block(block: Dict[str, Any]) -> List[str]:
    text = block.get("text", "").strip()
    if not text:
        return []

    block_type = block.get("type", "paragraph")
    if block_type == "decision":
        return [f"**Decision.** {text}", ""]
    if block_type == "rationale":
        return [f"**Rationale.** {text}", ""]
    if block_type == "risk":
        return [f"**Risk.** {text}", ""]
    if block_type == "assumption":
        return [f"**Assumption.** {text}", ""]
    if block_type == "interface":
        return [f"**Interface.** {text}", ""]
    return [text, ""]


def _render_requirement(req: Dict[str, Any]) -> List[str]:
    title = req["title"].strip()
    req_id = req["id"]
    lines = [
        f"**[{req_id} — {title}]{{#{_anchor(req_id)}}}**",
        "",
        req["shall_statement"].strip(),
        "",
        f"- Priority: {req['priority']}",
        f"- Risk: {req['risk']}",
    ]

    rationale = req.get("rationale", "").strip()
    if rationale:
        lines.append(f"- Rationale: {rationale}")

    verification = req.get("verification", {})
    lines.append(f"- Verification: {verification.get('method', 'not_defined')} / {verification.get('status', 'not_defined')}")

    secondary = req.get("section_ids", [])[1:]
    if secondary:
        lines.append(f"- Secondary section links: {', '.join(secondary)}")

    refs = req.get("references", [])
    if refs:
        lines.append(f"- References: {', '.join(refs)}")

    lines.append("")
    return lines


def render_markdown(
    data: Dict[str, Any],
    max_heading_level: int = DEFAULT_MAX_HEADING_LEVEL,
) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
    validate_source(data)
    _validate_projection_contract(data, max_heading_level)

    document = data["document"]
    sections = _section_lookup(data)
    req_by_section = _requirements_by_primary_section(data)

    lines: List[str] = [
        "---",
        f"title: {_yaml_quote(document['title'])}",
        f"document_id: {_yaml_quote(document['id'])}",
        f"version: {_yaml_quote(document['version'])}",
        'semantic_authority: "JSON_SSOT"',
        'display_numbering: "WORD_TEMPLATE"',
        "---",
        "",
    ]

    section_map: List[Dict[str, Any]] = []
    requirement_map: List[Dict[str, Any]] = []

    for section_id in flatten_outline(data["outline"]):
        section = sections[section_id]
        level = int(section["heading_level"])
        marker = "#" * level
        anchor = _anchor(section_id)
        lines.extend([f"{marker} {section['title']} {{#{anchor}}}", ""])

        section_map.append(
            {
                "section_id": section_id,
                "title": section["title"],
                "heading_level": level,
                "markdown_anchor": anchor,
                "word_style_expected": f"Heading {level}",
                "display_number_source": "WORD_TEMPLATE",
                "source_revision": section["revision"]["version"],
            }
        )

        for block in section.get("content_blocks", []):
            lines.extend(_render_content_block(block))

        for req in req_by_section.get(section_id, []):
            lines.extend(_render_requirement(req))
            requirement_map.append(
                {
                    "requirement_id": req["id"],
                    "primary_section_id": section_id,
                    "secondary_section_ids": req.get("section_ids", [])[1:],
                    "markdown_anchor": _anchor(req["id"]),
                    "source_revision": req["revision"]["version"],
                }
            )

    markdown = "\n".join(lines).rstrip() + "\n"
    return markdown, section_map, requirement_map


def build_manifest(
    data: Dict[str, Any],
    source_bytes: bytes,
    markdown: str,
    section_map: List[Dict[str, Any]],
    requirement_map: List[Dict[str, Any]],
    source_repo: str = "",
    source_ref: str = "",
    source_path: str = "",
) -> Dict[str, Any]:
    document = data["document"]
    return {
        "schema": MANIFEST_SCHEMA,
        "adapter": {
            "name": "data-rich-json-to-docx-rtm",
            "version": ADAPTER_VERSION,
            "producer_repo": "GBOGEB/document-organization-system",
        },
        "source": {
            "document_id": document["id"],
            "document_version": document["version"],
            "semantic_ssot": "JSON",
            "git_repo": source_repo or None,
            "git_ref": source_ref or None,
            "path": source_path or None,
            "sha256": sha256_bytes(source_bytes),
        },
        "projection": {
            "format": "MARKDOWN",
            "sha256": sha256_bytes(markdown.encode("utf-8")),
            "heading_contract": {
                "maximum_heading_level": DEFAULT_MAX_HEADING_LEVEL,
                "numbering": "TEMPLATE_MANAGED",
                "heading_text_contains_numbers": False,
                "style_map": {
                    "1": "Heading 1",
                    "2": "Heading 2",
                    "3": "Heading 3",
                },
            },
            "section_count": len(section_map),
            "requirement_count": len(requirement_map),
        },
        "docx_rtm_consumer": {
            "repo": "GBOGEB/DOCX_RTM_Automation",
            "markdown_to_docx_entrypoint": "src/core/rtm_roundtrip.py::RTMRoundtrip.md_to_docx",
            "reference_doc": "config/reference.docx",
            "required_pandoc_behavior": "apply reference.docx heading styles and template multilevel numbering",
            "forbidden_numbering_filter": "config/filters/extend_headings.lua",
            "forbidden_reason": "it prepends numbering into heading text and would duplicate template-managed numbering",
        },
        "section_map": section_map,
        "requirement_map": requirement_map,
        "relations": data["relations"],
        "external_references": data["external_references"],
        "authority": {
            "rendered_output_authoritative": False,
            "authority_transfer": False,
            "engineering_credit": False,
            "compliance_credit": False,
            "semantic_changes_allowed_in_consumer": False,
        },
    }


def project_file(
    source_path: Path,
    output_dir: Path,
    source_repo: str = "",
    source_ref: str = "",
    max_heading_level: int = DEFAULT_MAX_HEADING_LEVEL,
) -> Tuple[Path, Path]:
    source_bytes = source_path.read_bytes()
    data = json.loads(source_bytes.decode("utf-8"))
    markdown, section_map, requirement_map = render_markdown(
        data,
        max_heading_level=max_heading_level,
    )
    manifest = build_manifest(
        data,
        source_bytes=source_bytes,
        markdown=markdown,
        section_map=section_map,
        requirement_map=requirement_map,
        source_repo=source_repo,
        source_ref=source_ref,
        source_path=str(source_path),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = data["document"]["id"]
    md_path = output_dir / f"{stem}.projection.md"
    manifest_path = output_dir / f"{stem}.outward_document_manifest.json"

    md_path.write_text(markdown, encoding="utf-8", newline="\n")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return md_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_json", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-repo", default="")
    parser.add_argument("--source-ref", default="")
    parser.add_argument(
        "--max-heading-level",
        type=int,
        default=DEFAULT_MAX_HEADING_LEVEL,
    )
    args = parser.parse_args()

    try:
        md_path, manifest_path = project_file(
            args.source_json,
            args.output_dir,
            source_repo=args.source_repo,
            source_ref=args.source_ref,
            max_heading_level=args.max_heading_level,
        )
    except (OSError, json.JSONDecodeError, ProjectionError) as exc:
        print(f"FAIL: {exc}")
        return 1

    print(f"PASS: projection Markdown -> {md_path}")
    print(f"PASS: outward manifest -> {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
