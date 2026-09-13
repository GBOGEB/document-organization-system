#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import telemetry, pca_priority, glob_runtime

OUT=ROOT/"control"/"generated"; OUT.mkdir(parents=True,exist_ok=True)
META={
    "source_commit":os.getenv("CONTROL_SOURCE_SHA",os.getenv("GITHUB_SHA","LOCAL")),
    "runner_commit":os.getenv("GITHUB_SHA","LOCAL"),
    "run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
    "event":os.getenv("GITHUB_EVENT_NAME","LOCAL"),
    "source":"measured repository telemetry"
}

def write(name,payload):
    (OUT/name).write_text(json.dumps({"receipt":META,"payload":payload},indent=2,sort_keys=True)+"\n",encoding="utf-8")

write("measured-telemetry.json",telemetry.snapshot())
write("pca-priority.json",pca_priority.report())
write("rebuild-shared-authority.json",glob_runtime.plan_rebuild(["ATOM-GLOOB-FEDERATED-AUTHORITY"]))
write("worker-plan.json",glob_runtime.plan_workers(2,["ATOM-GLOOB-FEDERATED-AUTHORITY"]))
