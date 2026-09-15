#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import pca_priority, recursive_control, registry as reg, telemetry

DEFAULT_ROUTES=ROOT/"control"/"causal-route-registry.json"
CAUSE_CLASSES=("SOURCE","ATOM","EDGE","OPERATOR","RUNTIME","FEDERATED_RETURN")


def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def digest(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
def stable(items): return sorted(items,key=lambda x:json.dumps(x,sort_keys=True,separators=(",",":")))


def cause_block(items):
    values=stable(items)
    return {"fingerprint":digest(values),"items":values}


def entity_block(entity_type,books,entries,causes):
    blocks={k:cause_block(causes.get(k,[])) for k in CAUSE_CLASSES}
    fp=digest({"entity_type":entity_type,"books":sorted(books),"entries":sorted(entries),"causes":{k:v["fingerprint"] for k,v in blocks.items()}})
    return {"entity_type":entity_type,"books":sorted(books),"entries":sorted(entries),"fingerprint":fp,"causes":blocks}


def causal_snapshot():
    registry=reg.load_registry(ROOT/"registry.yaml"); index=reg.build_index(ROOT/"registry.yaml")
    shared=load(ROOT/registry["shared_atom_catalog"]); shared_by={x["id"]:x for x in shared.get("atoms",[])}
    ops=load(ROOT/registry.get("operator_catalog","operators.json")); op_by={x["id"]:x for x in ops.get("operators",[])}
    timeline=load(ROOT/"control"/"timeline.json")
    entries={}; graph_by={}
    for eid,meta in index["entries"].items():
        g=load(ROOT/meta["graph"]); graph_by[eid]=g
        sources=[{k:s.get(k) for k in ("id","repo","path","commit","blob","authority") if s.get(k) is not None} for s in g.get("sources",[])]
        local_atoms=[{"scope":"LOCAL","value":a} for a in g.get("atoms",[])]
        shared_atoms=[{"scope":"SHARED","value":shared_by[a]} for a in g.get("shared_atom_refs",[]) if a in shared_by]
        events=telemetry.explicit_events_for(eid,timeline)
        federated=[s for s in sources if s.get("authority") in {"RUNTIME_RECEIPT","OBSERVED_EXECUTION"} or str(s.get("id","")).startswith("SRC-CODEX-")]
        entries[eid]=entity_block("ENTRY",[meta["book_id"]],[eid],{
            "SOURCE":sources,"ATOM":local_atoms+shared_atoms,"EDGE":g.get("edges",[]),
            "OPERATOR":[op_by[o] for o in g.get("operator_refs",[]) if o in op_by],
            "RUNTIME":events,"FEDERATED_RETURN":federated})

    entities=dict(entries)
    for bid in sorted(index["books"]):
        eids=sorted(e for e,m in index["entries"].items() if m["book_id"]==bid); causes={k:[] for k in CAUSE_CLASSES}
        for eid in eids:
            for k in CAUSE_CLASSES: causes[k].extend(entries[eid]["causes"][k]["items"])
        entities[bid]=entity_block("BOOK",[bid],eids,causes)

    rows={r["entity_id"]:r for r in telemetry.measured_rows()}
    atom_users={}; edge_users={}; op_users={}
    for eid,g in graph_by.items():
        for a in [x["id"] for x in g.get("atoms",[])]+list(g.get("shared_atom_refs",[])): atom_users.setdefault(a,set()).add(eid)
        for e in g.get("edges",[]): edge_users.setdefault(e["type"],set()).add(eid)
        for o in g.get("operator_refs",[]): op_users.setdefault(o,set()).add(eid)

    for entity_id,row in rows.items():
        if entity_id in entities: continue
        typ=row["entity_type"]
        if typ in {"ATOM","SHARED_ATOM"}:
            eids=sorted(atom_users.get(entity_id,set())); books={index["entries"][e]["book_id"] for e in eids}; causes={k:[] for k in CAUSE_CLASSES}
            if entity_id in shared_by: causes["ATOM"]=[{"scope":"SHARED","value":shared_by[entity_id]}]
            else:
                for e in eids:
                    for a in graph_by[e].get("atoms",[]):
                        if a["id"]==entity_id: causes["ATOM"].append({"scope":"LOCAL","entry":e,"value":a})
            for e in eids:
                for edge in graph_by[e].get("edges",[]):
                    if edge.get("to")==entity_id or edge.get("from")==entity_id: causes["EDGE"].append({"entry":e,**edge})
                for s in graph_by[e].get("sources",[]):
                    if any(x.get("type")=="AUTHORITY_FOR" and x.get("from")==s.get("id") and x.get("to")==entity_id for x in graph_by[e].get("edges",[])): causes["SOURCE"].append(s)
            entities[entity_id]=entity_block(typ,books,eids,causes)
        elif typ=="EDGE_TYPE":
            edge_type=entity_id.replace("EDGE-TYPE-","",1); eids=sorted(edge_users.get(edge_type,set())); books={index["entries"][e]["book_id"] for e in eids}; causes={k:[] for k in CAUSE_CLASSES}
            causes["EDGE"]=[{"entry":e,**edge} for e in eids for edge in graph_by[e].get("edges",[]) if edge.get("type")==edge_type]
            entities[entity_id]=entity_block(typ,books,eids,causes)
        elif typ=="OPERATOR":
            eids=sorted(op_users.get(entity_id,set())); books={index["entries"][e]["book_id"] for e in eids}; causes={k:[] for k in CAUSE_CLASSES}
            if entity_id in op_by: causes["OPERATOR"]=[op_by[entity_id]]
            causes["RUNTIME"]=telemetry.explicit_events_for(entity_id,timeline)
            entities[entity_id]=entity_block(typ,books,eids,causes)
    return {"schema":"gloob-causal-fingerprint/0.1","entities":dict(sorted(entities.items()))}


def recompute_entity(entity):
    causes={k:entity.get("causes",{}).get(k,{}).get("items",[]) for k in CAUSE_CLASSES}
    return entity_block(entity["entity_type"],entity.get("books",[]),entity.get("entries",[]),causes)


def row(snapshot,eid): return next((r for r in snapshot.get("telemetry",{}).get("rows",[]) if r.get("entity_id")==eid),None)
def causal_entity(snapshot,eid): return snapshot.get("causal",{}).get("entities",{}).get(eid)


def causal_epoch(snaps,eid):
    usable=[s for s in snaps if causal_entity(s,eid)]
    if not usable: return [],None
    fp=causal_entity(usable[-1],eid)["fingerprint"]; out=[]
    for s in reversed(usable):
        if causal_entity(s,eid)["fingerprint"]!=fp: break
        out.append(s)
    out=list(reversed(out)); baseline=usable[len(usable)-len(out)-1] if len(usable)>len(out) else None
    return out,baseline


def changed_causes(baseline,current,eid):
    a=causal_entity(baseline,eid) if baseline else None; b=causal_entity(current,eid)
    if not a or not b: return []
    return [k for k in CAUSE_CLASSES if a["causes"][k]["fingerprint"]!=b["causes"][k]["fingerprint"]]


def feature_delta(baseline,current,eid):
    a=row(baseline,eid) if baseline else None; b=row(current,eid)
    if not a or not b: return {}
    return {f:float(b.get(f,0))-float(a.get(f,0)) for f in pca_priority.FEATURES if float(b.get(f,0))!=float(a.get(f,0))}


def window_qualifies(snaps,eid,policy):
    q=policy["qualification"]
    if len(snaps)<int(q["minimum_epoch_snapshots"]): return False
    reports=[{"report":pca_priority.report_from_rows(s["telemetry"]["rows"])} for s in snaps[-int(q["minimum_epoch_snapshots"]):]]
    return recursive_control.window_qualifies(reports,eid,float(q["pc1_max_step"]),float(q["pc2_plus_residual_ceiling"]))


def repos_for(entity,causes,route_registry):
    repos=set(); items=[]
    for cause in causes: items.extend(entity["causes"][cause]["items"])
    if any(c in {"SOURCE","FEDERATED_RETURN"} for c in causes):
        for item in items:
            if isinstance(item,dict) and item.get("repo"): repos.add(item["repo"])
    for book in entity.get("books",[]):
        cfg=route_registry.get("books",{}).get(book,{})
        if not repos and cfg.get("domain_repo"): repos.add(cfg["domain_repo"])
        if not repos and cfg.get("semantic_repo"): repos.add(cfg["semantic_repo"])
    if not repos: repos.add(route_registry.get("default_repo","GBOGEB/document-organization-system"))
    return sorted(repos)


def bound_route(eid,cause,centity,cfg,route_registry,current):
    route={"entity_id":eid,"cause":cause,"books":centity["books"],"repos":repos_for(centity,[cause],route_registry),"crew":cfg.get("crew","CAUSAL_TRIAGE"),"action":"OPEN_BOUNDED_WORK","reason":"FAILED_CAUSAL_EPOCH_QUALIFICATION","causal_fingerprint":centity["fingerprint"],"opened_from_source_commit":current.get("receipt",{}).get("source_commit")}
    identity={k:route[k] for k in ("entity_id","cause","books","repos","crew","causal_fingerprint","opened_from_source_commit")}
    route["route_id"]="ROUTE-"+digest(identity)[:16].upper()
    route["assignment_digest"]=digest({**identity,"route_id":route["route_id"]})
    route["return_contract"]={"schema":"gloob-causal-return/0.1","must_echo":["route_id","assignment_digest"],"exact_sha":True,"steps_gt_zero":True}
    return route


def attribute(history,surveillance,route_registry,policy):
    snaps=[s for s in history.get("snapshots",[]) if s.get("causal")]
    if not snaps: return {"schema":"gloob-causal-attribution/0.2","state":"NO_CAUSAL_HISTORY","entities":[],"routes":[]}
    current=snaps[-1]; min_n=int(policy["qualification"]["minimum_epoch_snapshots"]); entities=[]; routes=[]
    for sitem in surveillance.get("entities",[]):
        eid=sitem["entity_id"]; centity=causal_entity(current,eid)
        if not centity: continue
        epoch,baseline=causal_epoch(snaps,eid); causes=changed_causes(baseline,current,eid); changed=baseline is not None
        qualifies=window_qualifies(epoch,eid,policy) if len(epoch)>=min_n else False
        if not changed: state="UNCHANGED_CONTROL"
        elif len(epoch)<min_n: state="CAUSAL_REQUALIFY"
        elif qualifies: state="CAUSAL_CONTROL"
        else: state="CAUSAL_ESCALATE"
        item={"entity_id":eid,"entity_type":centity["entity_type"],"books":centity["books"],"state":state,"causal_epoch_snapshots":len(epoch),"changed_causes":causes,"feature_delta":feature_delta(baseline,current,eid),"attributed":bool(causes) or not changed}
        entities.append(item)
        if state=="CAUSAL_ESCALATE" and causes:
            for cause in causes:
                cfg=route_registry.get("cause_routes",{}).get(cause,route_registry.get("fallback_route",{}))
                routes.append(bound_route(eid,cause,centity,cfg,route_registry,current))
    counts={k:sum(e["state"]==k for e in entities) for k in ("UNCHANGED_CONTROL","CAUSAL_REQUALIFY","CAUSAL_CONTROL","CAUSAL_ESCALATE")}
    return {"schema":"gloob-causal-attribution/0.2","state":"ATTRIBUTED","causal_snapshot_count":len(snaps),"counts":counts,"entities":entities,"routes":routes}


def route_plan(attribution):
    return {"schema":"gloob-causal-route-plan/0.2","mode":"CAUSE_BOUND_HANDSHAKE_REQUIRED","assignments":attribution.get("routes",[]),"blocked_unattributed":[e["entity_id"] for e in attribution.get("entities",[]) if e["state"]=="CAUSAL_ESCALATE" and not e.get("attributed")]}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("history"); ap.add_argument("surveillance"); ap.add_argument("--routes",default=str(DEFAULT_ROUTES)); ap.add_argument("--policy",default=str(ROOT/"control"/"surveillance-policy.json")); ap.add_argument("--attribution-output",default=str(ROOT/"control"/"generated"/"causal-attribution.json")); ap.add_argument("--plan-output",default=str(ROOT/"control"/"generated"/"causal-route-plan.json")); args=ap.parse_args()
    out=attribute(load(args.history),load(args.surveillance),load(args.routes),load(args.policy)); plan=route_plan(out)
    Path(args.attribution_output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path(args.plan_output).write_text(json.dumps(plan,indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__=="__main__": main()
