#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
import registry as reg
import view_model

FEATURES = ["structural_degree","scope_size","reuse_count","source_count","runtime_proof_count","promotion_count","operator_count","cross_ref_count"]

def load(rel): return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def records(registry): return {r["entry"]["id"]: r for r in view_model.flatten_entries(registry)}

def explicit_events_for(entity_id, timeline):
    """Return only receipts explicitly attributed to an entity.

    Publication-wide `*` events prove the publication/control surface and must not be
    replicated into every Entry, Book or Operator row. Replication previously made
    runtime/promotion exposure scale with graph cardinality rather than observed scope.
    """
    return [e for e in timeline.get("events",[]) if entity_id in e.get("entry_ids",[])]

def measured_rows():
    registry = reg.load_registry(ROOT / "registry.yaml")
    index = reg.build_index(ROOT / "registry.yaml")
    timeline = load("control/timeline.json")
    recs = records(registry)
    graphs = {eid: load(rec["entry"]["graph"]) for eid,rec in recs.items()}
    shared = load(registry["shared_atom_catalog"])
    shared_ids = {a["id"] for a in shared.get("atoms",[])}
    operator_catalog = load(registry.get("operator_catalog", "operators.json"))
    known_ops = {o["id"] for o in operator_catalog.get("operators",[])}
    rows, atom_entries, atom_sources, edge_entries, op_entries = [], {}, {}, {}, {}

    for eid,g in graphs.items():
        local = {a["id"] for a in g.get("atoms",[])}
        shared_refs = set(g.get("shared_atom_refs",[])); atoms = local | shared_refs
        for a in local: atom_entries.setdefault(a,set()).add(eid)
        for a in shared_refs: atom_entries.setdefault(a,set()).add(eid)
        for edge in g.get("edges",[]):
            edge_entries.setdefault(edge["type"],set()).add(eid)
            if edge["type"] == "AUTHORITY_FOR" and str(edge.get("to","")).startswith("ATOM-"):
                atom_sources[edge["to"]] = atom_sources.get(edge["to"],0) + 1
        op_refs=set(g.get("operator_refs",[]))
        unknown=op_refs-known_ops
        if unknown: raise ValueError(f"unknown operator refs for {eid}: {sorted(unknown)}")
        for op in op_refs: op_entries.setdefault(op,set()).add(eid)
        ev = explicit_events_for(eid,timeline)
        xrefs = [x for x in index.get("cross_book_references",[]) if eid in (x.get("from_entry"),x.get("to_entry"))]
        rows.append(dict(entity_id=eid,entity_type="ENTRY",book_id=recs[eid]["book"]["id"],
            structural_degree=len(g.get("edges",[]))+len(atoms),scope_size=len(atoms),
            reuse_count=sum(len(index["atom_usage"].get(a,[eid])) for a in shared_refs),
            source_count=len(g.get("sources",[])),runtime_proof_count=sum(e["kind"]=="RUNTIME_PROOF" for e in ev),
            promotion_count=sum(e["kind"]=="PROMOTION" for e in ev),operator_count=len(op_refs),cross_ref_count=len(xrefs)))

    for book in registry.get("books",[]):
        eids=[e["id"] for c in book.get("chapters",[]) for e in c.get("entries",[])]
        atoms=set(); ops=set(); edge_count=source_count=0; ev=[]
        for eid in eids:
            g=graphs[eid]; atoms |= {a["id"] for a in g.get("atoms",[])} | set(g.get("shared_atom_refs",[]))
            ops |= set(g.get("operator_refs",[])); edge_count += len(g.get("edges",[])); source_count += len(g.get("sources",[])); ev += explicit_events_for(eid,timeline)
        xrefs=[x for x in index.get("cross_book_references",[]) if x.get("from_entry") in eids or x.get("to_entry") in eids]
        rows.append(dict(entity_id=book["id"],entity_type="BOOK",book_id=book["id"],structural_degree=edge_count+len(atoms),scope_size=len(eids),
            reuse_count=sum(len(index["atom_usage"].get(a,[])) for a in atoms if a in shared_ids),source_count=source_count,
            runtime_proof_count=sum(e["kind"]=="RUNTIME_PROOF" for e in ev),promotion_count=sum(e["kind"]=="PROMOTION" for e in ev),operator_count=len(ops),cross_ref_count=len(xrefs)))

    via={}
    for x in index.get("cross_book_references",[]):
        if x.get("via_atom"): via[x["via_atom"]]=via.get(x["via_atom"],0)+1
    for atom_id,eids in sorted(atom_entries.items()):
        books={index["entries"][e]["book_id"] for e in eids}
        rows.append(dict(entity_id=atom_id,entity_type="SHARED_ATOM" if atom_id in shared_ids else "ATOM",book_id=next(iter(books)) if len(books)==1 else "MULTI",
            structural_degree=len(eids)+atom_sources.get(atom_id,0),scope_size=len(eids),reuse_count=len(eids),source_count=atom_sources.get(atom_id,0),runtime_proof_count=0,promotion_count=0,operator_count=0,cross_ref_count=via.get(atom_id,0)))

    for typ,eids in sorted(edge_entries.items()):
        count=sum(1 for g in graphs.values() for e in g.get("edges",[]) if e["type"]==typ)
        rows.append(dict(entity_id="EDGE-TYPE-"+typ,entity_type="EDGE_TYPE",book_id="MULTI",structural_degree=count,scope_size=len(eids),reuse_count=len(eids),source_count=0,runtime_proof_count=0,promotion_count=0,operator_count=0,cross_ref_count=sum(x.get("type")==typ for x in index.get("cross_book_references",[]))))

    for op,eids in sorted(op_entries.items()):
        ev=explicit_events_for(op,timeline)
        rows.append(dict(entity_id=op,entity_type="OPERATOR",book_id="MULTI",structural_degree=len(eids),scope_size=len(eids),reuse_count=len(eids),source_count=0,
            runtime_proof_count=sum(e["kind"]=="RUNTIME_PROOF" for e in ev),promotion_count=sum(e["kind"]=="PROMOTION" for e in ev),operator_count=1,cross_ref_count=0))
    return sorted(rows,key=lambda r:(r["entity_type"],r["entity_id"]))

def snapshot():
    global_events=[e for e in load("control/timeline.json").get("events",[]) if "*" in e.get("entry_ids",[])]
    return {"schema":"gloob-measured-telemetry/0.2","expert_seeded_scores":False,"global_control_events":len(global_events),"features":FEATURES,"rows":measured_rows()}

if __name__ == "__main__": print(json.dumps(snapshot(),indent=2,sort_keys=True))
