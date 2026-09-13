#!/usr/bin/env python3
from __future__ import annotations
import argparse, io, json, os, tempfile, urllib.request, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
HEADERS=lambda token:{"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"gloob-recursive-control"}

def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))

def bundle_from_dir(path):
    path=Path(path); telemetry=load(path/"measured-telemetry.json")
    return {"receipt":telemetry["receipt"],"telemetry":telemetry["payload"]}

def request_json(url,token):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS(token))) as r: return json.loads(r.read().decode("utf-8"))

def download_zip(url,token):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS(token))) as r: return r.read()

def github_bundles(repo,token,limit=8):
    data=request_json(f"https://api.github.com/repos/{repo}/actions/artifacts?name=gloob-control-receipts&per_page=30",token)
    artifacts=[a for a in data.get("artifacts",[]) if not a.get("expired")]
    artifacts.sort(key=lambda a:a.get("created_at",''),reverse=True)
    out=[]; errors=[]
    for art in artifacts[:limit]:
        try:
            raw=download_zip(art["archive_download_url"],token)
            with tempfile.TemporaryDirectory() as td:
                with zipfile.ZipFile(io.BytesIO(raw)) as z: z.extractall(td)
                hits=list(Path(td).rglob("measured-telemetry.json"))
                if not hits: raise ValueError("measured-telemetry.json missing")
                out.append(bundle_from_dir(hits[0].parent))
        except Exception as exc:
            errors.append({"artifact_id":art.get("id"),"run_id":art.get("workflow_run",{}).get("id"),"error":f"{type(exc).__name__}: {exc}"})
    return out,errors,len(artifacts)

def dedup(bundles):
    by={}
    for b in bundles:
        key=str(b.get("receipt",{}).get("source_commit",''))
        if key: by[key]=b
    def run_key(b):
        try:return int(b["receipt"].get("run_id",0))
        except:return 0
    return sorted(by.values(),key=run_key)

def federate(current_dir,repo=None,token=None,limit=8):
    bundles=[]; errors=[]; available=0
    if repo and token:
        prior,errors,available=github_bundles(repo,token,limit); bundles.extend(prior)
    if current_dir and (Path(current_dir)/"measured-telemetry.json").exists(): bundles.append(bundle_from_dir(current_dir))
    snapshots=dedup(bundles)
    return {"schema":"gloob-federated-control-history/0.2","artifact_candidates":available,"download_errors":errors,"snapshot_count":len(snapshots),"distinct_source_commits":[s["receipt"]["source_commit"] for s in snapshots],"snapshots":snapshots}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--current",default=str(ROOT/"control"/"generated")); ap.add_argument("--output",default=str(ROOT/"control"/"generated"/"federated-history.json")); ap.add_argument("--limit",type=int,default=8)
    args=ap.parse_args(); repo=os.getenv("GITHUB_REPOSITORY"); token=os.getenv("GITHUB_TOKEN")
    value=federate(args.current,repo,token,args.limit); Path(args.output).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:value[k] for k in ("artifact_candidates","snapshot_count","distinct_source_commits","download_errors")},indent=2))

if __name__=="__main__": main()
