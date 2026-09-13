#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import pca_priority

MIN_SNAPSHOTS=3
PC1_DRIFT_TOLERANCE=0.05
RESIDUAL_CEILING=0.70


def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))


def recompute(snapshot):
    report=pca_priority.report_from_rows(snapshot["telemetry"]["rows"])
    return {"receipt":snapshot["receipt"],"report":report}


def residual(report,entity_id):
    total=0.0
    for c in report.get("components",[])[1:]:
        score=float(c.get("scores",{}).get(entity_id,0.0))
        total += float(c.get("explained_variance_ratio",0.0))*score*score
    return math.sqrt(total)


def ranking_row(report,entity_id):
    return next((r for r in report.get("ranking",[]) if r["entity_id"]==entity_id),None)


def telemetry_signature(report,entity_id):
    row=ranking_row(report,entity_id)
    if not row: return None
    return tuple(sorted((k,float(v)) for k,v in row.get("telemetry",{}).items()))


def latest_telemetry_epoch(snapshots,entity_id):
    """Return the trailing snapshots for which this entity's own telemetry is unchanged.

    PCA axes are population-dependent. An unrelated graph decomposition may rotate those
    axes even when this entity did not change. CONTROL therefore remains sticky inside
    an unchanged telemetry epoch once a qualifying three-snapshot window has been
    observed; a real change to the entity's own measured feature vector starts a new
    qualification epoch.
    """
    if not snapshots: return []
    latest_sig=telemetry_signature(snapshots[-1]["report"],entity_id)
    if latest_sig is None: return []
    out=[]
    for snap in reversed(snapshots):
        if telemetry_signature(snap["report"],entity_id)!=latest_sig: break
        out.append(snap)
    return list(reversed(out))


def window_qualifies(window,entity_id,pc1_tolerance,residual_ceiling):
    if len(window)<2: return False
    pc1=[float(s["report"]["components"][0]["scores"][entity_id]) for s in window]
    drift=max(abs(b-a) for a,b in zip(pc1,pc1[1:]))
    residuals=[residual(s["report"],entity_id) for s in window]
    return drift<=pc1_tolerance and all(x<=residual_ceiling for x in residuals)


def analyze(history,min_snapshots=MIN_SNAPSHOTS,pc1_tolerance=PC1_DRIFT_TOLERANCE,residual_ceiling=RESIDUAL_CEILING):
    snapshots=[recompute(s) for s in history.get("snapshots",[])]
    if len(snapshots)<min_snapshots:
        return {"schema":"gloob-recursive-control/0.2","state":"INSUFFICIENT_HISTORY","snapshot_count":len(snapshots),"required":min_snapshots,"entities":[]}
    latest=snapshots[-1]["report"]
    ids={r["entity_id"] for r in latest["ranking"]}
    entities=[]
    for eid in sorted(ids):
        row=ranking_row(latest,eid)
        epoch=latest_telemetry_epoch(snapshots,eid)
        epoch_count=len(epoch)
        recent=epoch[-min_snapshots:]
        if len(recent)>1:
            pc1=[float(s["report"]["components"][0]["scores"][eid]) for s in recent]
            drift=max(abs(b-a) for a,b in zip(pc1,pc1[1:]))
        else:
            drift=0.0
        res=residual(latest,eid)
        stable=epoch_count>=min_snapshots and drift<=pc1_tolerance
        established=False
        if epoch_count>=min_snapshots:
            for start in range(0,epoch_count-min_snapshots+1):
                if window_qualifies(epoch[start:start+min_snapshots],eid,pc1_tolerance,residual_ceiling):
                    established=True
                    break
        qualification_count=0
        for snap in reversed(epoch):
            if residual(snap["report"],eid)<=residual_ceiling: qualification_count+=1
            else: break
        state="CONTROL" if established else "IMPROVE"
        entities.append({
            "entity_id":eid,"entity_type":row["entity_type"],"state":state,
            "pc1_saturated":stable,"pc1_max_step":round(drift,6),
            "residual_pc2_plus":round(res,6),"priority":row["priority"],
            "telemetry_epoch_snapshots":epoch_count,
            "residual_qualification_count":qualification_count,
            "control_established_in_epoch":established
        })
    remaining=sum(float(c["explained_variance_ratio"]) for c in latest.get("components",[])[1:])
    entities.sort(key=lambda x:(x["state"]!="IMPROVE",-x["residual_pc2_plus"],-x["priority"],x["entity_id"]))
    return {"schema":"gloob-recursive-control/0.2","state":"CLASSIFIED","snapshot_count":len(snapshots),"window":min_snapshots,"pc1_drift_tolerance":pc1_tolerance,"residual_ceiling":residual_ceiling,"classification_policy":"TELEMETRY_EPOCH_HYSTERESIS","pc1_explained_variance":latest["components"][0]["explained_variance_ratio"],"pc2_plus_explained_variance":remaining,"entities":entities}


def residual_worker_plan(control,capacity=2):
    if capacity<1: raise ValueError("capacity must be >= 1")
    candidates=[x for x in control.get("entities",[]) if x["state"]=="IMPROVE"]
    candidates.sort(key=lambda x:(-x["residual_pc2_plus"],-x["priority"],x["entity_id"]))
    loads=[0.0]*capacity; assignments=[]
    for x in candidates:
        worker=min(range(capacity),key=lambda i:(loads[i],i)); work=max(x["residual_pc2_plus"],0.001)
        assignments.append({"entity_id":x["entity_id"],"entity_type":x["entity_type"],"worker":f"worker-{worker+1}","focus":"PC2_PLUS_RESIDUAL","residual":x["residual_pc2_plus"],"priority":x["priority"],"qualification_count":x.get("residual_qualification_count",0)}); loads[worker]+=work
    return {"schema":"gloob-residual-worker-plan/0.2","mode":"PLAN_ONLY","capacity":capacity,"assignments":assignments,"worker_residual_load":{f"worker-{i+1}":round(loads[i],6) for i in range(capacity)}}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("history"); ap.add_argument("--control-output",default=str(ROOT/"control"/"generated"/"recursive-control.json")); ap.add_argument("--worker-output",default=str(ROOT/"control"/"generated"/"residual-worker-plan.json")); ap.add_argument("--capacity",type=int,default=2); args=ap.parse_args()
    out=analyze(load(args.history)); workers=residual_worker_plan(out,args.capacity)
    Path(args.control_output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"); Path(args.worker_output).write_text(json.dumps(workers,indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__=="__main__": main()
