"""Dependency-free, read-only Drive satellite HMI projection. Does not sync or authorize."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

STATUSES = {"VERIFIED_METADATA", "LOCAL_QA", "OPEN", "BLOCKED", "UNVERIFIED", "HOLD_ENGINEERING", "DRAFT"}


def _safe_url(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("URL must be a string")
    if re.search(r"[\x00-\x1f\x7f\\]", value):
        raise ValueError("URL contains control characters or backslashes")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only credential-free HTTPS links are allowed")
    return html.escape(value, quote=True)


def render(manifest: dict) -> str:
    if not isinstance(manifest, dict) or not isinstance(manifest.get("entries"), list):
        raise ValueError("entries[] is required")
    if len(manifest["entries"]) > 5000:
        raise ValueError("Too many manifest entries")
    seen = set()
    rows = []
    for entry in manifest["entries"]:
        if not isinstance(entry, dict):
            raise ValueError("Entry must be an object")
        key = entry.get("id")
        if not isinstance(key, str) or not key or key in seen:
            raise ValueError("Missing or duplicated entry id")
        seen.add(key)
        status = entry.get("status", "UNVERIFIED")
        if status not in STATUSES:
            raise ValueError("Unknown release status")
        title = html.escape(str(entry.get("title", key)))
        group = html.escape(str(entry.get("group", "Other")))
        detail = html.escape(str(entry.get("detail", "")))
        url = _safe_url(entry["url"]) if entry.get("url") else None
        link = f'<a href="{url}" target="_blank" rel="noopener noreferrer">Open source link</a>' if url else '<span class="muted">No authoritative link yet</span>'
        rows.append((group, f'<div class="node" data-search="{html.escape((key+" "+str(entry.get("title", key))+" "+str(entry.get("group", "Other"))+" "+str(entry.get("detail", ""))+" "+status).lower(), quote=True)}"><span class="dot"></span><div><strong>{title}</strong><div class="meta">{detail}</div>{link}</div><span class="status">{status}</span></div>'))
    sections = []
    for group in dict.fromkeys(g for g, _ in rows):
        sections.append(f'<details open><summary>{group}</summary>{"".join(row for g,row in rows if g==group)}</details>')
    title = html.escape(str(manifest.get("worktree_id", "Satellite worktree")))
    asof = html.escape(str(manifest.get("source_as_of", "UNVERIFIED")))
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'">
<title>Drive Satellite | %s</title>
<style>:root{color-scheme:light dark;--p:#59267c;--v:#8d4aac;--b:#eddbef}*{box-sizing:border-box}body{font:15px/1.5 Aptos,Arial,sans-serif;margin:0;background:#fbf8fc;color:#30233b}.wrap{max-width:1060px;margin:auto;padding:clamp(14px,4vw,42px)}header{border-bottom:4px solid var(--v);background:linear-gradient(115deg,#42145d,#71328c);color:white}h1{font-size:clamp(24px,3vw,36px);margin:6px 0}header p{opacity:.92}.sub{font-size:13px;color:#5f5164;margin:16px 0}input{width:100%%;padding:12px 14px;border:1px solid #c8b6d0;border-radius:10px;background:white;color:#2c1737;font-size:16px}.pill{display:inline-block;padding:3px 9px;background:#f4e7f7;color:#62317c;border-radius:30px;font-size:12px;font-weight:700}[hidden]{display:none!important}details{background:white;margin:14px 0;border:1px solid #e5d9e8;border-radius:12px;overflow:hidden}summary{cursor:pointer;background:#f3eaf5;padding:14px 18px;font-weight:700}.node{display:grid;grid-template-columns:10px 1fr auto;align-items:start;gap:14px;padding:14px 18px;border-top:1px solid #eee4ef}.dot{background:var(--v);border-radius:50%%;width:9px;height:9px;margin-top:6px}.meta{font-size:13px;color:#675b6d;margin:3px 0}.status{font:700 11px/1.4 Consolas,monospace;border:1px solid #dbcee1;border-radius:5px;padding:5px 6px;overflow-wrap:anywhere;max-width:170px}a{color:#65318a}a:focus,input:focus,summary:focus{outline:3px solid #ad52c5;outline-offset:2px}.muted{color:#777}footer{margin:25px 0;font-size:13px;border-top:1px solid #e9dbe9;padding-top:18px}@media(max-width:600px){.node{grid-template-columns:8px 1fr}.status{grid-column:2;max-width:max-content}summary{padding:14px}header{overflow-wrap:anywhere}}</style>
<header><div class="wrap"><span class="pill">READ ONLY · PROJECTION</span><h1>Google Drive Satellite Worktree</h1><p>%s</p></div></header>
<main class="wrap"><p class="sub">Source snapshot: %s · This interface links to objects; it cannot approve design, release or publish.</p><label for="q">Find an artifact, gate or action</label><input id="q" type="search" placeholder="Search this snapshot" autocomplete="off"><p id="count" role="status" aria-live="polite"></p>%s<footer>Local offline HTML projection. Evidence classes and release decisions remain with authoritative owners.</footer></main>
<script>const q=document.getElementById('q'),rows=[...document.querySelectorAll('.node')],out=document.getElementById('count');function filter(){const needle=q.value.trim().toLowerCase();let n=0;for(const el of rows){const show=el.dataset.search.includes(needle);el.hidden=!show;if(show)n++}for(const section of document.querySelectorAll('details')){section.hidden=![...section.querySelectorAll('.node')].some(x=>!x.hidden)}out.textContent=n+' of '+rows.length+' entries';}q.addEventListener('input',filter);filter();</script></html>''' % (title,title,asof,''.join(sections))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    args.output.write_text(render(json.loads(args.manifest.read_text(encoding="utf-8"))), encoding="utf-8")
    print(f"Generated {args.output} ({args.output.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
