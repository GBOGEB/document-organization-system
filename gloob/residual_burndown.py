#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import pca_priority, registry as reg, telemetry

FEATURES=telemetry.FEATURES

def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))

def graph_for_entry(entry_id,index): return load(ROOT/index["entries"][entry_id]["graph"])

def targets_for(entity_id,entity_type,feature,index,registry,timeline):
    if entity_type=="ENTRY":
        g=graph_for_entry(entity_id,index)
        if feature=="structural_degree": return {"atoms":[a["id"] for a in g.get("atoms",[])]+list(g.get("shared_atom_refs",[])),"edges":[f"{e['from']}::{e['type']}::{e['to']}" for e in g.get("edges",[])]}
        if feature=="scope_size": return {"atoms":[a["id"] for a in g.get("atoms",[])]+list(g.get("shared_atom_refs",[]))}
        if feature=="reuse_count": return {"shared_atoms":list(g.get("shared_atom_refs",[]))}
        if feature=="source_count": return {"sources":[s["id"] for s in g.get("sources",[])]}
        if feature=="operator_count": return {"operators":list(g.get("operator_refs",[]))}
        if feature=="cross_ref_count": return {"cross_book_references":[x for x in index.get("cross_book_references",[]) if entity_id in (x.get("from_entry"),x.get("to_entry"))]}
        if feature in {"runtime_proof_count","promotion_count"}: return {"events":[e["id"] for e in timeline.get("events",[]) if entity_id in e.get("entry_ids",[])]}
    if entity_type=="BOOK":
        eids=[eid for eid,e in index["entries"].items() if e["book_id"]==entity_id]
        return {"entries":sorted(eids)}
    if entity_type=="OPERATOR":
        return {"entries":index.get("operator_usage",{}).get(entity_id,[]),"operator":entity_id}
    if entity_type in {"ATOM","SHARED_ATOM"}:
        return {"entries":index.get("atom_usage",{}).get(entity_id,[]),"atom":entity_id}
    if entity_type=="EDGE_TYPE": return {"edge_type":entity_id.removeprefix("EDGE-TYPE-")}
    return {}

def decompose(control=None):
    rows=telemetry.snapshot()["rows"]; report=pca_priority.report_from_rows(rows); z=pca_priority.standardize(rows)
    row_idx={r["entity_id"]:i for i,r in enumerate(rows)}; ranking={r["entity_id"]:r for r in report["ranking"]}
    index=reg.build_index(ROOT/"registry.yaml"); registry=reg.load_registry(ROOT/"registry.yaml"); timeline=load(ROOT/"control"/"timeline.json")
    if control and control.get("state")=="CLASSIFIED": targets=[x for x in control.get("entities",[]) if x["state"]=="IMPROVE"]
    else: targets=[]
    out=[]
    for item in targets:
        eid=item["entity_id"]; etype=item["entity_type"]; i=row_idx.get(eid)
        if i is None: continue
        pcs=[]
        for comp in report.get("components",[])[1:4]:
            score=float(comp["scores"].get(eid,0.0)); evr=float(comp["explained_variance_ratio"])
            contributions=[]
            for j,f in enumerate(FEATURES):
                signed=z[i][j]*float(comp["loadings"][f])
                contributions.append({"feature":f,"signed_contribution":round(signed,6),"magnitude":round(abs(signed),6),"reverse_load":targets_for(eid,etype,f,index,registry,timeline)})
            contributions.sort(key=lambda x:(-x["magnitude"],x["feature"]))
            pcs.append({"component":comp["name"],"explained_variance_ratio":evr,"score":round(score,6),"weighted_energy":round(evr*score*score,6),"feature_contributions":contributions})
        pcs.sort(key=lambda x:(-x["weighted_energy"],x["component"]))
        out.append({"entity_id":eid,"entity_type":etype,"state":item["state"],"priority":ranking.get(eid,{}).get("priority",0.0),"residual_pc2_plus":item["residual_pc2_plus"],"components":pcs})
    out.sort(key=lambda x:(-x["residual_pc2_plus"],-x["priority"],x["entity_id"]))
    return {"schema":"gloob-residual-burndown/0.1","basis":"CURRENT_MEASURED_PCA","entities":out}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--control",default=str(ROOT/"control"/"generated"/"recursive-control.json")); ap.add_argument("--output",default=str(ROOT/"control"/"generated"/"residual-burndown.json")); args=ap.parse_args()
    control=load(args.control) if Path(args.control).exists() else None
    Path(args.output).write_text(json.dumps(decompose(control),indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__=="__main__": main()
