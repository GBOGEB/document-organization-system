#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from statistics import median

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import registry as reg
import view_model, telemetry, pca_priority

REGISTRY=ROOT/"registry.yaml"; TIMELINE=ROOT/"control"/"timeline.json"
def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def recs():
    r=reg.load_registry(REGISTRY)
    return r,{x["entry"]["id"]:x for x in view_model.flatten_entries(r)}

def local_owners(atom_id):
    registry,records=recs(); out=[]
    for eid,row in records.items():
        graph=load(ROOT/row["entry"]["graph"])
        if atom_id in {a["id"] for a in graph.get("atoms",[])}: out.append(eid)
    return sorted(out)

def ask_entry(entry_id):
    index=reg.build_index(REGISTRY)
    if entry_id not in index["entries"]: raise KeyError(entry_id)
    row=next(r for r in telemetry.measured_rows() if r["entity_id"]==entry_id)
    pri=next(r for r in pca_priority.report()["ranking"] if r["entity_id"]==entry_id)
    return {"entry":index["entries"][entry_id],"telemetry":row,"priority":pri}

def ask_where_used(atom_id):
    registry=reg.load_registry(REGISTRY); users=reg.where_used(atom_id,REGISTRY) or local_owners(atom_id)
    return {"atom_id":atom_id,"entries":users}

def ask_provenance(entry_id,level="summary"):
    if level not in {"summary","evidence","runtime"}: raise ValueError(level)
    registry,records=recs()
    if entry_id not in records: raise KeyError(entry_id)
    row=records[entry_id]; graph=load(ROOT/row["entry"]["graph"]); shared=load(ROOT/registry["shared_atom_catalog"]); timeline=load(TIMELINE)
    return view_model.provenance_projection(row,graph,shared,timeline,level,entry_id)

def ask_runtime(entry_id):
    _,records=recs()
    if entry_id not in records: raise KeyError(entry_id)
    return view_model.runtime_projection(records[entry_id],load(TIMELINE))

def priority_report(): return pca_priority.report()

def plan_rebuild(atom_ids):
    index=reg.build_index(REGISTRY); priorities=pca_priority.entry_priorities(); affected=set(); reasons={}
    for atom in atom_ids:
        users=index["atom_usage"].get(atom,[]) or local_owners(atom)
        for eid in users:
            affected.add(eid); reasons.setdefault(eid,[]).append(atom)
    items=[{"entry_id":e,"priority":priorities.get(e,0.0),"changed_atoms":sorted(reasons.get(e,[]))} for e in affected]
    items.sort(key=lambda x:(-x["priority"],x["entry_id"]))
    return {"schema":"gloob-rebuild-plan/0.1","mode":"PLAN_ONLY","changed_atoms":sorted(set(atom_ids)),"affected_entries":[x["entry_id"] for x in items],"work_items":items}

def plan_workers(capacity=2,atom_ids=None):
    if capacity<1: raise ValueError("capacity must be >= 1")
    rows={r["entity_id"]:r for r in telemetry.measured_rows() if r["entity_type"]=="ENTRY"}; priorities=pca_priority.entry_priorities()
    candidates=plan_rebuild(atom_ids)["affected_entries"] if atom_ids else sorted(rows,key=lambda e:(-priorities.get(e,0.0),e))
    costs={e:rows[e]["scope_size"]+rows[e]["structural_degree"]+rows[e]["source_count"]+rows[e]["operator_count"] for e in candidates}
    threshold=median(costs.values()) if costs else 0; loads=[0.0]*capacity; assignments=[]
    for eid in sorted(candidates,key=lambda e:(-priorities.get(e,0.0),-costs[e],e)):
        worker=min(range(capacity),key=lambda i:(loads[i],i)); lane="FAST" if costs[eid]<=threshold else "HEAVY"
        assignments.append({"entry_id":eid,"worker":f"worker-{worker+1}","lane":lane,"priority":priorities.get(eid,0.0),"estimated_units":costs[eid]}); loads[worker]+=costs[eid]
    return {"schema":"gloob-worker-plan/0.1","mode":"PLAN_ONLY","capacity":capacity,"lane_threshold_units":threshold,"assignments":assignments,"worker_loads":{f"worker-{i+1}":loads[i] for i in range(capacity)}}

def freeze_edition_plan():
    edition=reg.freeze_edition(REGISTRY)
    return {"schema":"gloob-freeze-plan/0.1","mode":"PLAN_ONLY","edition_id":edition["id"],"sha256":edition["sha256"]}
