#!/usr/bin/env python3
"""Dependency-free Gloob Book v0.1 renderer: one graph -> HTML/Markdown/PDF + receipt."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

PROFILES = {"compact": 1, "standard": 3, "deep": 5}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_graph(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    graph = json.loads(raw)
    validate_graph(graph)
    return graph, sha256_bytes(raw)


def validate_graph(graph: dict) -> None:
    for key in ("book", "chapter", "entry"):
        obj = graph[key]
        if not SLUG_RE.fullmatch(obj["slug"]):
            raise ValueError(f"invalid slug for {key}: {obj['slug']}")
    for atom in graph.get("atoms", []):
        if not SLUG_RE.fullmatch(atom["slug"]):
            raise ValueError(f"invalid atom slug: {atom['slug']}")
        if not 1 <= int(atom["min_depth"]) <= 5:
            raise ValueError(f"invalid depth: {atom['id']}")
    if not graph["entry"]["address"].startswith("gloob://"):
        raise ValueError("entry address must be a gloob:// URI")


def project(graph: dict, depth: int) -> dict:
    projected = dict(graph)
    projected["atoms"] = [a for a in graph["atoms"] if int(a["min_depth"]) <= depth]
    projected["projection"] = {"depth": depth}
    return projected


def atom_text(atom: dict) -> str:
    value = atom.get("value", "")
    unit = atom.get("unit")
    text = f"{value} {unit}" if unit else str(value)
    note = atom.get("note")
    return f"{text} — {note}" if note else text


def render_markdown(graph: dict, profile: str) -> str:
    e = graph["entry"]
    lines = [
        f"# {graph['book']['title']}",
        "",
        f"## {graph['chapter']['title']}",
        "",
        f'<a id="{e["slug"]}"></a>',
        f"### {e['title']}",
        "",
        f"`{e['address']}` · profile `{profile}` · depth `{graph['projection']['depth']}`",
        "",
    ]
    for atom in graph["atoms"]:
        lines += [f'<a id="{atom["slug"]}"></a>', f"#### {atom['heading']}", "", atom_text(atom), ""]
    if graph["projection"]["depth"] >= 5:
        lines += ['<a id="source-bindings"></a>', "#### Source bindings", ""]
        for src in graph["sources"]:
            lines.append(f"- `{src['id']}` — `{src['repo']}@{src['commit']}:{src['path']}` ({src['authority']})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_html(graph: dict, profile: str) -> str:
    e = graph["entry"]
    cards = []
    for atom in graph["atoms"]:
        cards.append(
            f'<section class="atom" id="{html.escape(atom["slug"])}">'
            f'<h3>{html.escape(atom["heading"])}</h3>'
            f'<p>{html.escape(atom_text(atom))}</p>'
            f'<small>{html.escape(atom["id"])} · depth {atom["min_depth"]}</small></section>'
        )
    source_html = ""
    if graph["projection"]["depth"] >= 5:
        rows = "".join(
            f"<tr><td>{html.escape(s['id'])}</td><td>{html.escape(s['repo'])}</td>"
            f"<td><code>{html.escape(s['commit'])}</code></td><td>{html.escape(s['authority'])}</td></tr>"
            for s in graph["sources"]
        )
        source_html = f"<h2 id=\"source-bindings\">Source bindings</h2><table><tr><th>ID</th><th>Repo</th><th>Commit</th><th>Authority</th></tr>{rows}</table>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(e['title'])}</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:980px;margin:40px auto;padding:0 24px;line-height:1.55}}
header{{border-bottom:2px solid currentColor;margin-bottom:24px}} .meta{{opacity:.72}} .atom{{border:1px solid #bbb;border-radius:10px;padding:16px;margin:12px 0}}
code{{overflow-wrap:anywhere}} table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #bbb;padding:8px;text-align:left}} small{{opacity:.65}}
@media print{{body{{max-width:none;margin:0}} .atom{{break-inside:avoid}}}}
</style></head><body>
<header><h1>{html.escape(graph['book']['title'])}</h1><h2>{html.escape(graph['chapter']['title'])}</h2><h2 id="{html.escape(e['slug'])}">{html.escape(e['title'])}</h2>
<p class="meta"><code>{html.escape(e['address'])}</code> · profile <b>{profile}</b> · depth {graph['projection']['depth']}</p></header>
{''.join(cards)}{source_html}
</body></html>"""


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_lines(text: str, width: int = 88) -> list[str]:
    words, lines, line = text.split(), [], ""
    for word in words:
        if len(line) + len(word) + 1 > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        lines.append(line)
    return lines or [""]


def render_pdf(graph: dict, profile: str) -> bytes:
    text_lines = [graph["book"]["title"], graph["chapter"]["title"], graph["entry"]["title"], graph["entry"]["address"], f"profile={profile} depth={graph['projection']['depth']}", ""]
    for atom in graph["atoms"]:
        text_lines.append(atom["heading"])
        text_lines.extend(wrap_lines(atom_text(atom)))
        text_lines.append("")
    if graph["projection"]["depth"] >= 5:
        text_lines.append("Source bindings")
        for src in graph["sources"]:
            text_lines.extend(wrap_lines(f"{src['id']} {src['repo']}@{src['commit']}:{src['path']} [{src['authority']}]"))
    pages = [text_lines[i:i+48] for i in range(0, len(text_lines), 48)] or [[]]
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    page_ids = [4 + i * 2 for i in range(len(pages))]
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode())
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for idx, lines in enumerate(pages):
        page_obj_id = 4 + idx * 2
        content_obj_id = page_obj_id + 1
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_obj_id} 0 R >>".encode())
        commands = ["BT", "/F1 10 Tf", "50 790 Td", "13 TL"]
        first = True
        for line in lines:
            if not first:
                commands.append("T*")
            commands.append(f"({pdf_escape(line)}) Tj")
            first = False
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", "replace")
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")
    out = bytearray(b"%PDF-1.4\n%GLOOB\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode())
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(out)


def render_all(graph_path: Path, out_dir: Path, profile: str) -> dict:
    graph, graph_sha = load_graph(graph_path)
    depth = PROFILES[profile]
    projected = project(graph, depth)
    stem = f"{graph['book']['slug']}-{graph['chapter']['slug']}-{graph['entry']['slug']}-{profile}"
    out_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "html": render_html(projected, profile).encode(),
        "md": render_markdown(projected, profile).encode(),
        "pdf": render_pdf(projected, profile),
    }
    outputs = {}
    for ext, payload in payloads.items():
        path = out_dir / f"{stem}.{ext}"
        path.write_bytes(payload)
        outputs[ext] = {"path": str(path), "sha256": sha256_bytes(payload), "bytes": len(payload)}
    receipt = {
        "schema": "gloob-render-receipt/0.1",
        "operator": "OP-GLOOB-RENDER",
        "entry_id": graph["entry"]["id"],
        "entry_slug": graph["entry"]["slug"],
        "address": graph["entry"]["address"],
        "profile": profile,
        "depth": depth,
        "input": {"path": str(graph_path), "sha256": graph_sha},
        "outputs": outputs,
        "source_commits": [{"repo": s["repo"], "commit": s["commit"], "path": s["path"]} for s in graph["sources"]],
    }
    receipt_path = out_dir / f"{stem}.receipt.json"
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    receipt_path.write_bytes(receipt_bytes)
    return receipt


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--graph", type=Path, default=Path(__file__).with_name("graph") / "qplant-energy.json")
    p.add_argument("--out-dir", type=Path, default=Path(__file__).with_name("examples"))
    p.add_argument("--profile", choices=PROFILES, default="standard")
    p.add_argument("--all-profiles", action="store_true")
    args = p.parse_args()
    profiles = PROFILES if args.all_profiles else [args.profile]
    receipts = [render_all(args.graph, args.out_dir, name) for name in profiles]
    print(json.dumps(receipts, indent=2))


if __name__ == "__main__":
    main()
