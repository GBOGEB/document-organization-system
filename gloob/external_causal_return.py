#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DEFAULT_POLICY=ROOT/"control"/"external-return-policy.json"
SHA40=re.compile(r"^[0-9a-f]{40}$")


def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def dump(path,value): Path(path).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def handshakes(route_plan):
    out=[]
    for a in route_plan.get("assignments",[]):
        out.append({
            "schema":"gloob-causal-handshake/0.1",
            "route_id":a["route_id"],
            "assignment_digest":a["assignment_digest"],
            "entity_id":a["entity_id"],
            "cause":a["cause"],
            "books":a.get("books",[]),
            "target_repos":a.get("repos",[]),
            "crew":a.get("crew"),
            "opened_from_source_commit":a.get("opened_from_source_commit"),
            "causal_fingerprint":a.get("causal_fingerprint"),
            "required_return":{
                "schema":"gloob-causal-return/0.1",
                "fields":["route_id","assignment_digest","repo","crew","outcome","evidence"],
                "evidence_fields":["source_commit","runner_commit","run_id","steps","conclusion"]
            }
        })
    return {"schema":"gloob-causal-handshake-plan/0.1","mode":"EXTERNAL_RETURN_REQUIRED","handshakes":out}


def validate_return(ret,hs,policy):
    errors=[]
    if ret.get("schema")!="gloob-causal-return/0.1": errors.append("SCHEMA_MISMATCH")
    if ret.get("route_id")!=hs.get("route_id"): errors.append("ROUTE_ID_MISMATCH")
    if ret.get("assignment_digest")!=hs.get("assignment_digest"): errors.append("ASSIGNMENT_DIGEST_MISMATCH")
    if ret.get("repo") not in hs.get("target_repos",[]): errors.append("TARGET_REPO_MISMATCH")
    if ret.get("crew")!=hs.get("crew"): errors.append("CREW_MISMATCH")
    if ret.get("outcome") not in policy.get("accepted_outcomes",[]): errors.append("OUTCOME_UNSUPPORTED")
    ev=ret.get("evidence",{})
    source=str(ev.get("source_commit","")); runner=str(ev.get("runner_commit",""))
    if not SHA40.fullmatch(source) or not SHA40.fullmatch(runner): errors.append("INVALID_EXACT_SHA")
    if source!=runner: errors.append("SOURCE_RUNNER_SHA_MISMATCH")
    try: steps=int(ev.get("steps",0))
    except Exception: steps=0
    if steps<=0: errors.append("ZERO_STEP_RETURN")
    if str(ev.get("conclusion","")).lower()!="success": errors.append("RETURN_NOT_SUCCESS")
    if not ev.get("run_id"): errors.append("RUN_ID_MISSING")
    return errors


def closure_for(hs,ret,policy):
    errors=validate_return(ret,hs,policy)
    if errors:
        return {"route_id":hs["route_id"],"entity_id":hs["entity_id"],"cause":hs["cause"],"state":"REJECT_RETURN","action":"KEEP_ROUTE_OPEN","errors":errors,"return":ret}
    outcome=ret["outcome"]
    if outcome=="RESOLVED": state="RETURN_ACCEPTED_REQUALIFY"; action=policy["resolved_action"]
    elif outcome=="DEFERRED": state="RETURN_ACCEPTED_DEFERRED"; action=policy["deferred_action"]
    else: state="RETURN_ACCEPTED_OWNER_REJECT"; action=policy["rejected_by_owner_action"]
    return {"route_id":hs["route_id"],"entity_id":hs["entity_id"],"cause":hs["cause"],"state":state,"action":action,"errors":[],"return":ret,"control_credit":False}


def process(route_plan,returns,policy):
    hp=handshakes(route_plan); by_route={r.get("route_id"):r for r in returns}
    closures=[]; awaiting=[]
    for hs in hp["handshakes"]:
        ret=by_route.get(hs["route_id"])
        if ret is None:
            awaiting.append({"route_id":hs["route_id"],"entity_id":hs["entity_id"],"cause":hs["cause"],"state":"AWAITING_EXTERNAL_RETURN"})
        else:
            closures.append(closure_for(hs,ret,policy))
    known={h["route_id"] for h in hp["handshakes"]}
    orphans=[r for r in returns if r.get("route_id") not in known]
    ledger={
        "schema":"gloob-external-return-ledger/0.1",
        "policy_id":policy["policy_id"],
        "handshake_count":len(hp["handshakes"]),
        "return_count":len(returns),
        "counts":{
            "AWAITING_EXTERNAL_RETURN":len(awaiting),
            "RETURN_ACCEPTED_REQUALIFY":sum(c["state"]=="RETURN_ACCEPTED_REQUALIFY" for c in closures),
            "RETURN_ACCEPTED_DEFERRED":sum(c["state"]=="RETURN_ACCEPTED_DEFERRED" for c in closures),
            "RETURN_ACCEPTED_OWNER_REJECT":sum(c["state"]=="RETURN_ACCEPTED_OWNER_REJECT" for c in closures),
            "REJECT_RETURN":sum(c["state"]=="REJECT_RETURN" for c in closures),
            "ORPHAN_RETURN":len(orphans)
        },
        "closures":closures,
        "awaiting":awaiting,
        "orphan_returns":orphans
    }
    requalify=[{"route_id":c["route_id"],"entity_id":c["entity_id"],"cause":c["cause"],"trigger":"EXTERNAL_RESOLUTION_ACCEPTED","external_source_commit":c["return"]["evidence"]["source_commit"]} for c in closures if c["state"]=="RETURN_ACCEPTED_REQUALIFY"]
    closure_plan={"schema":"gloob-route-closure-plan/0.1","mode":"EXTERNAL_RETURN_DOES_NOT_GRANT_CONTROL","requalify":requalify,"keep_open":awaiting+[c for c in closures if c["state"] in {"REJECT_RETURN","RETURN_ACCEPTED_DEFERRED"}],"triage":[c for c in closures if c["state"]=="RETURN_ACCEPTED_OWNER_REJECT"],"orphan_returns":orphans}
    return hp,ledger,closure_plan


def load_returns(directory):
    p=Path(directory)
    if not p.exists(): return []
    out=[]
    for path in sorted(p.glob("*.json")):
        value=load(path)
        if isinstance(value,list): out.extend(value)
        else: out.append(value)
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("route_plan"); ap.add_argument("--returns-dir",default=str(ROOT/"control"/"external-returns")); ap.add_argument("--policy",default=str(DEFAULT_POLICY)); ap.add_argument("--handshake-output",default=str(ROOT/"control"/"generated"/"external-handshake-plan.json")); ap.add_argument("--ledger-output",default=str(ROOT/"control"/"generated"/"external-return-ledger.json")); ap.add_argument("--closure-output",default=str(ROOT/"control"/"generated"/"route-closure-plan.json")); args=ap.parse_args()
    hp,ledger,closure=process(load(args.route_plan),load_returns(args.returns_dir),load(args.policy))
    dump(args.handshake_output,hp); dump(args.ledger_output,ledger); dump(args.closure_output,closure)

if __name__=="__main__": main()
