#!/usr/bin/env python3
from __future__ import annotations
import argparse, io, json, os, tempfile, urllib.error, urllib.request, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
HEADERS=lambda token:{"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"gloob-external-return-federation"}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None

def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def request_json(url,token):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS(token))) as r: return json.loads(r.read().decode("utf-8"))
def download_zip(url,token):
    opener=urllib.request.build_opener(NoRedirect); req=urllib.request.Request(url,headers=HEADERS(token))
    try:
        with opener.open(req) as r: return r.read()
    except urllib.error.HTTPError as exc:
        if exc.code not in (301,302,303,307,308) or not exc.headers.get("Location"): raise
        with urllib.request.urlopen(urllib.request.Request(exc.headers["Location"],headers={"User-Agent":"gloob-external-return-federation"})) as r: return r.read()

def open_repos(handshake_plan):
    return sorted({repo for h in handshake_plan.get("handshakes",[]) for repo in h.get("target_repos",[])})

def extract_returns(raw):
    out=[]
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(io.BytesIO(raw)) as z: z.extractall(td)
        for p in sorted(Path(td).rglob("*.json")):
            try: value=load(p)
            except Exception: continue
            vals=value if isinstance(value,list) else [value]
            out.extend(v for v in vals if isinstance(v,dict) and v.get("schema")=="gloob-causal-return/0.1")
    return out

def federate(handshake_plan,token,artifact_name="gloob-causal-return",per_repo=10):
    repos=open_repos(handshake_plan); returns=[]; errors=[]; candidates=0
    if not repos: return {"schema":"gloob-federated-external-returns/0.1","state":"NO_OPEN_HANDSHAKES","repos":[],"artifact_candidates":0,"returns":[],"errors":[]}
    if not token: return {"schema":"gloob-federated-external-returns/0.1","state":"TOKEN_UNAVAILABLE","repos":repos,"artifact_candidates":0,"returns":[],"errors":[]}
    for repo in repos:
        try:
            data=request_json(f"https://api.github.com/repos/{repo}/actions/artifacts?name={artifact_name}&per_page={per_repo}",token)
            arts=[a for a in data.get("artifacts",[]) if not a.get("expired")]; candidates+=len(arts)
            for a in arts[:per_repo]:
                try:
                    for r in extract_returns(download_zip(a["archive_download_url"],token)):
                        r=dict(r); r["federation"]={"repo":repo,"artifact_id":a.get("id"),"run_id":a.get("workflow_run",{}).get("id"),"digest":a.get("digest")}; returns.append(r)
                except Exception as exc: errors.append({"repo":repo,"artifact_id":a.get("id"),"error":f"{type(exc).__name__}: {exc}"})
        except Exception as exc: errors.append({"repo":repo,"error":f"{type(exc).__name__}: {exc}"})
    by={}
    for r in returns:
        ev=r.get("evidence",{}); key=(r.get("route_id"),ev.get("source_commit"),r.get("outcome")); by[key]=r
    values=sorted(by.values(),key=lambda r:(str(r.get("route_id")),str(r.get("evidence",{}).get("source_commit"))))
    return {"schema":"gloob-federated-external-returns/0.1","state":"FEDERATED","repos":repos,"artifact_candidates":candidates,"returns":values,"errors":errors}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("handshake_plan"); ap.add_argument("--output",default=str(ROOT/"control"/"generated"/"federated-external-returns.json")); ap.add_argument("--artifact-name",default="gloob-causal-return"); args=ap.parse_args()
    token=os.getenv("GLOOB_FEDERATION_TOKEN") or os.getenv("GITHUB_TOKEN")
    out=federate(load(args.handshake_plan),token,args.artifact_name); Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("state","repos","artifact_candidates","errors")},indent=2))
if __name__=="__main__": main()
