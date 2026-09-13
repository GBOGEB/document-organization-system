#!/usr/bin/env python3
from __future__ import annotations
import argparse, io, json, os, tempfile, urllib.request, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))

def bundle_from_dir(path):
    path=Path(path); telemetry=load(path/"measured-telemetry.json")
    return {"receipt":telemetry["receipt"],"telemetry":telemetry["payload"]}

def request_json(url,token):
    req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
    with urllib.request.urlopen(req) as r: return json.loads(r.read().decode("utf-8"))

def download_zip(url,token):
    req=urllib.request.Request(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
    with urllib.request.urlopen(req) as r: return r.read()

def github_bundles(repo,token,limit=8):
    data=request_json(f"https://api.github.com/repos/{repo}/actions/artifacts?name=gloob-control-receipts&per_page=30",token)
    artifacts=[a for a in data.get("artifacts",[]) if not a.get("expired")]
    artifacts.sort(key=lambda a:a.get("created_at",''),reverse=True)
    out=[]
    for art in artifacts[:limit]:
        try:
            raw=download_zip(art["archive_download_url"],token)
            with tempfile.TemporaryDirectory() as td:
                with zipfile.ZipFile(io.BytesIO(raw)) as z: z.extractall(td)
                p=Path(td)
                hits=list(p.rglob("measured-telemetry.json"))
                if hits: out.append(bundle_from_dir(hits[0].parent))
        except Exception:
            continue
    return out

def dedup(bundles):
    by={}
    for b in bundles:
        key=str(b.get("receipt",{}).get("source_commit",''))
        if key: by[key]=b
    return sorted(by.values(),key=lambda b:str(b["receipt"].get("run_id","")))

def federate(current_dir,repo=None,token=None,limit=8):
    bundles=[]
    if repo and token: bundles.extend(github_bundles(repo,token,limit))
    if current_dir and (Path(current_dir)/"measured-telemetry.json").exists(): bundles.append(bundle_from_dir(current_dir))
    return {"schema":"gloob-federated-control-history/0.1","snapshots":dedup(bundles)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--current",default=str(ROOT/"control"/"generated")); ap.add_argument("--output",default=str(ROOT/"control"/"generated"/"federated-history.json")); ap.add_argument("--limit",type=int,default=8)
    args=ap.parse_args(); repo=os.getenv("GITHUB_REPOSITORY"); token=os.getenv("GITHUB_TOKEN")
    value=federate(args.current,repo,token,args.limit); Path(args.output).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__=="__main__": main()
