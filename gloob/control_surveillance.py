#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import pca_priority, recursive_control

DEFAULT_POLICY=ROOT/"control"/"surveillance-policy.json"


def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))


def row_signature(snapshot,entity_id):
    for row in snapshot.get("telemetry",{}).get("rows",[]):
        if row.get("entity_id")==entity_id:
            return tuple(sorted((f,float(row.get(f,0))) for f in pca_priority.FEATURES))
    return None


def reports(history):
    return [{"receipt":s.get("receipt",{}),"telemetry":s.get("telemetry",{}),"report":pca_priority.report_from_rows(s["telemetry"]["rows"])} for s in history.get("snapshots",[])]


def component_energy(report,entity_id,name):
    comp=next((c for c in report.get("components",[]) if c.get("name")==name),None)
    if not comp: return 0.0
    score=float(comp.get("scores",{}).get(entity_id,0.0))
    return float(comp.get("explained_variance_ratio",0.0))*score*score


def discovery_for_entity(snaps,entity,policy):
    epoch_count=int(entity.get("telemetry_epoch_snapshots",0))
    epoch_start=len(snaps)-epoch_count
    if epoch_start<=0: return []
    baseline=snaps[epoch_start-1]["report"]; current=snaps[-1]["report"]
    out=[]; cfg=policy["residual_discovery"]
    for name in cfg.get("components",["PC3","PC4"]):
        before=component_energy(baseline,entity["entity_id"],name)
        after=component_energy(current,entity["entity_id"],name)
        delta=after-before
        rel=delta/max(abs(before),1e-9)
        material=delta>=float(cfg["minimum_weighted_energy_delta"]) and rel>=float(cfg["minimum_relative_energy_increase"])
        if material:
            out.append({"entity_id":entity["entity_id"],"entity_type":entity["entity_type"],"component":name,"baseline_weighted_energy":round(before,6),"current_weighted_energy":round(after,6),"delta":round(delta,6),"relative_increase":round(rel,6),"action":cfg.get("action","DISCOVER_ONLY")})
    return out


def surveil(history,policy):
    q=policy["qualification"]
    control=recursive_control.analyze(history,min_snapshots=int(q["minimum_epoch_snapshots"]),pc1_tolerance=float(q["pc1_max_step"]),residual_ceiling=float(q["pc2_plus_residual_ceiling"]))
    if control.get("state")!="CLASSIFIED":
        return {"schema":"gloob-control-surveillance/0.1","state":"INSUFFICIENT_HISTORY","control":control,"entities":[],"discoveries":[]}
    snaps=reports(history); entities=[]; discoveries=[]
    for x in control.get("entities",[]):
        if x.get("control_established_in_epoch"):
            surveillance="STABLE_CONTROL"
        elif int(x.get("telemetry_epoch_snapshots",0)) < int(q["minimum_epoch_snapshots"]):
            surveillance="REQUALIFY"
        else:
            surveillance="ESCALATE"
        epoch_start=len(snaps)-int(x.get("telemetry_epoch_snapshots",0))
        changed_epoch=epoch_start>0
        item=dict(x)
        item.update({"surveillance_state":surveillance,"changed_epoch":changed_epoch,"reopen_work":surveillance=="ESCALATE"})
        entities.append(item)
        if changed_epoch and surveillance in {"REQUALIFY","ESCALATE"}:
            discoveries.extend(discovery_for_entity(snaps,x,policy))
    entities.sort(key=lambda x:({"ESCALATE":0,"REQUALIFY":1,"STABLE_CONTROL":2}[x["surveillance_state"]],-x["residual_pc2_plus"],x["entity_id"]))
    return {"schema":"gloob-control-surveillance/0.1","state":"SURVEILLING","policy_id":policy["policy_id"],"snapshot_count":control["snapshot_count"],"counts":{k:sum(e["surveillance_state"]==k for e in entities) for k in ("STABLE_CONTROL","REQUALIFY","ESCALATE")},"entities":entities,"discoveries":discoveries}


def escalation_plan(surveillance,capacity=2):
    if capacity<1: raise ValueError("capacity must be >= 1")
    candidates=[e for e in surveillance.get("entities",[]) if e.get("reopen_work")]
    candidates.sort(key=lambda e:(-e["residual_pc2_plus"],-e["priority"],e["entity_id"]))
    loads=[0.0]*capacity; assignments=[]
    for e in candidates:
        i=min(range(capacity),key=lambda j:(loads[j],j)); load=max(float(e["residual_pc2_plus"]),0.001)
        assignments.append({"entity_id":e["entity_id"],"entity_type":e["entity_type"],"worker":f"worker-{i+1}","reason":"FAILED_NEW_TELEMETRY_EPOCH_QUALIFICATION","residual":e["residual_pc2_plus"]})
        loads[i]+=load
    return {"schema":"gloob-control-escalation-plan/0.1","mode":"PLAN_ONLY","assignments":assignments,"worker_load":{f"worker-{i+1}":round(v,6) for i,v in enumerate(loads)}}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("history"); ap.add_argument("--policy",default=str(DEFAULT_POLICY)); ap.add_argument("--capacity",type=int,default=2); ap.add_argument("--surveillance-output",default=str(ROOT/"control"/"generated"/"control-surveillance.json")); ap.add_argument("--discovery-output",default=str(ROOT/"control"/"generated"/"residual-discovery.json")); ap.add_argument("--plan-output",default=str(ROOT/"control"/"generated"/"control-escalation-plan.json")); args=ap.parse_args()
    policy=load(args.policy); out=surveil(load(args.history),policy); plan=escalation_plan(out,args.capacity)
    Path(args.surveillance_output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path(args.discovery_output).write_text(json.dumps({"schema":"gloob-residual-discovery/0.1","policy_id":policy["policy_id"],"discoveries":out.get("discoveries",[])},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    Path(args.plan_output).write_text(json.dumps(plan,indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__=="__main__": main()
