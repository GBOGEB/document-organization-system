#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import telemetry

FEATURES=telemetry.FEATURES

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm(v): return math.sqrt(dot(v,v))
def matvec(a,v): return [sum(a[i][j]*v[j] for j in range(len(v))) for i in range(len(a))]

def standardize(rows):
    cols=[[float(r[f]) for r in rows] for f in FEATURES]
    means=[sum(c)/len(c) for c in cols]
    std=[]
    for c,m in zip(cols,means):
        std.append(math.sqrt(sum((x-m)**2 for x in c)/max(1,len(c)-1)))
    return [[0.0 if s==0 else (float(r[f])-m)/s for f,m,s in zip(FEATURES,means,std)] for r in rows]

def covariance(z):
    n=len(z); p=len(FEATURES)
    return [[sum(z[r][i]*z[r][j] for r in range(n))/max(1,n-1) for j in range(p)] for i in range(p)]

def components(cov,count=2):
    work=[r[:] for r in cov]; total=sum(cov[i][i] for i in range(len(cov))); out=[]
    for k in range(min(count,len(cov))):
        v=[float(i+1+k) for i in range(len(cov))]; n=norm(v); v=[x/n for x in v]
        for _ in range(250):
            w=matvec(work,v); n=norm(w)
            if n < 1e-12: break
            nv=[x/n for x in w]
            if norm([a-b for a,b in zip(nv,v)]) < 1e-10: v=nv; break
            v=nv
        eig=max(0.0,dot(v,matvec(work,v)))
        if sum(v)<0: v=[-x for x in v]
        out.append({"name":f"PC{k+1}","eigenvalue":eig,"explained_variance_ratio":0.0 if total==0 else eig/total,"loadings":{f:v[i] for i,f in enumerate(FEATURES)}})
        for i in range(len(work)):
            for j in range(len(work)): work[i][j]-=eig*v[i]*v[j]
    return out

def report():
    snap=telemetry.snapshot(); rows=snap["rows"]; z=standardize(rows); comps=components(covariance(z),2)
    for c in comps:
        vec=[c["loadings"][f] for f in FEATURES]
        c["scores"]={rows[i]["entity_id"]:dot(z[i],vec) for i in range(len(rows))}
    pc1=comps[0]["scores"] if comps else {r["entity_id"]:0.0 for r in rows}
    lo,hi=min(pc1.values()),max(pc1.values()); ranking=[]
    for r in rows:
        raw=pc1[r["entity_id"]]; pr=50.0 if hi==lo else 100.0*(raw-lo)/(hi-lo)
        ranking.append({"entity_id":r["entity_id"],"entity_type":r["entity_type"],"priority":round(pr,6),"pc1_score":round(raw,6),"telemetry":{f:r[f] for f in FEATURES}})
    ranking.sort(key=lambda x:(-x["priority"],x["entity_type"],x["entity_id"]))
    return {"schema":"gloob-pca-priority/0.1","basis":"MEASURED_REPOSITORY_TELEMETRY","features":FEATURES,"components":comps,"ranking":ranking}

def entry_priorities(): return {r["entity_id"]:r["priority"] for r in report()["ranking"] if r["entity_type"]=="ENTRY"}

if __name__=="__main__": print(json.dumps(report(),indent=2,sort_keys=True))
