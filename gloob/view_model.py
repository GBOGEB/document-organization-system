#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def flatten_entries(registry):
    rows = []
    for book in registry.get("books", []):
        for chapter in book.get("chapters", []):
            for entry in chapter.get("entries", []):
                rows.append({"book": book, "chapter": chapter, "entry": entry})
    return rows


def semantic_atoms(graph, shared_catalog, depth=99):
    local = [dict(a, scope="LOCAL") for a in graph.get("atoms", []) if int(a.get("min_depth", 1)) <= depth]
    wanted = set(graph.get("shared_atom_refs", []))
    shared = [dict(a, scope="SHARED") for a in shared_catalog.get("atoms", []) if a["id"] in wanted and int(a.get("min_depth", 1)) <= depth]
    return local + shared


def graph_projection(record, graph, shared_catalog, depth=99):
    atoms = semantic_atoms(graph, shared_catalog, depth)
    nodes = [
        {"id": record["book"]["id"], "type": "BOOK", "label": record["book"]["title"]},
        {"id": record["chapter"]["id"], "type": "CHAPTER", "label": record["chapter"]["title"]},
        {"id": record["entry"]["id"], "type": "ENTRY", "label": record["entry"]["title"]},
    ]
    nodes += [{"id": a["id"], "type": "SHARED_ATOM" if a["scope"] == "SHARED" else "ATOM", "label": a["heading"]} for a in atoms]
    edges = [
        {"from": record["book"]["id"], "type": "CONTAINS", "to": record["chapter"]["id"]},
        {"from": record["chapter"]["id"], "type": "CONTAINS", "to": record["entry"]["id"]},
    ]
    edges += [{"from": record["entry"]["id"], "type": "HAS_ATOM", "to": a["id"]} for a in atoms]
    edges += graph.get("edges", [])
    return {"nodes": nodes, "edges": edges, "atoms": atoms}


def relevant_events(record, timeline):
    entry_id = record["entry"]["id"]
    return sorted(
        [e for e in timeline.get("events", []) if "*" in e.get("entry_ids", []) or entry_id in e.get("entry_ids", [])],
        key=lambda e: e["sequence"],
    )


def provenance_projection(record, graph, shared_catalog, timeline, level="summary", semantic_id=None):
    sources = []
    for source in graph.get("sources", []):
        row = {"id": source["id"], "authority": source.get("authority", "")}
        if level != "summary":
            row.update(repo=source.get("repo", ""), path=source.get("path", ""), commit=source.get("commit", ""))
        sources.append(row)
    out = {
        "target": semantic_id or record["entry"]["id"],
        "level": level,
        "sources": sources,
        "shared": [a["id"] for a in semantic_atoms(graph, shared_catalog) if a["scope"] == "SHARED"],
    }
    if level == "runtime":
        out["operators"] = graph.get("operators", [])
        out["runtime"] = relevant_events(record, timeline)
    return out


def runtime_projection(record, timeline):
    events = relevant_events(record, timeline)
    return {
        "proofs": [e for e in events if e["kind"] == "RUNTIME_PROOF"],
        "promotions": [e for e in events if e["kind"] == "PROMOTION"],
    }
