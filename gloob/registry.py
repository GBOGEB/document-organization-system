#!/usr/bin/env python3
"""Executable Gloob Book Registry v0.2 runtime."""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parent
DEFAULT_REGISTRY = ROOT / "registry.yaml"

def _load(path: Path) -> Dict[str, Any]: return json.loads(path.read_text(encoding="utf-8"))
def _digest_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def _digest_obj(value: Any) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return _digest_bytes(payload.encode("utf-8"))
def _file_digest(path: Path) -> str: return _digest_bytes(path.read_bytes())

def load_registry(path: Path = DEFAULT_REGISTRY) -> Dict[str, Any]:
    registry=_load(path)
    if registry.get("schema") != "gloob-book-registry/0.2": raise ValueError("unsupported registry schema")
    return registry

def iter_entries(registry: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for book in registry["books"]:
        for chapter in book["chapters"]:
            for entry in chapter["entries"]:
                yield {**entry,"book_id":book["id"],"book_slug":book["slug"],"chapter_id":chapter["id"],"chapter_slug":chapter["slug"]}

def build_index(registry_path: Path = DEFAULT_REGISTRY) -> Dict[str, Any]:
    registry=load_registry(registry_path); root=registry_path.parent
    shared_path=root/registry["shared_atom_catalog"]; shared_catalog=_load(shared_path); shared_ids={a["id"] for a in shared_catalog["atoms"]}
    operator_path=root/registry.get("operator_catalog","operators.json"); operator_catalog=_load(operator_path); operator_ids={o["id"] for o in operator_catalog.get("operators",[])}
    books={}; entries={}; addresses={}; atom_usage={a:[] for a in shared_ids}; operator_usage={o:[] for o in operator_ids}
    for book in registry["books"]:
        if book["id"] in books: raise ValueError(f"duplicate book id: {book['id']}")
        books[book["id"]]={"slug":book["slug"],"title":book["title"],"address":book["address"]}
    for entry in iter_entries(registry):
        if entry["id"] in entries: raise ValueError(f"duplicate entry id: {entry['id']}")
        if entry["address"] in addresses: raise ValueError(f"duplicate entry address: {entry['address']}")
        graph_path=root/entry["graph"]; graph=_load(graph_path)
        if graph["entry"]["id"] != entry["id"]: raise ValueError(f"graph entry mismatch for {entry['id']}")
        if graph["book"]["id"] != entry["book_id"]: raise ValueError(f"graph book mismatch for {entry['id']}")
        refs=list(entry.get("uses_shared_atoms",[])); graph_refs=list(graph.get("shared_atom_refs",[]))
        if sorted(refs)!=sorted(graph_refs): raise ValueError(f"registry/graph shared Atom mismatch for {entry['id']}")
        unknown=set(refs)-shared_ids
        if unknown: raise ValueError(f"unknown shared Atoms for {entry['id']}: {sorted(unknown)}")
        op_refs=list(graph.get("operator_refs",[])); unknown_ops=set(op_refs)-operator_ids
        if unknown_ops: raise ValueError(f"unknown Operators for {entry['id']}: {sorted(unknown_ops)}")
        record={"slug":entry["slug"],"title":entry["title"],"address":entry["address"],"book_id":entry["book_id"],"chapter_id":entry["chapter_id"],"graph":entry["graph"],"uses_shared_atoms":refs,"operator_refs":op_refs}
        entries[entry["id"]]=record; addresses[entry["address"]]=entry["id"]
        for atom_id in refs: atom_usage.setdefault(atom_id,[]).append(entry["id"])
        for op_id in op_refs: operator_usage.setdefault(op_id,[]).append(entry["id"])
    for users in atom_usage.values(): users.sort()
    for users in operator_usage.values(): users.sort()
    return {"schema":"gloob-registry-index/0.3","registry_id":registry["registry"]["id"],"books":books,"entries":entries,"addresses":addresses,"atom_usage":atom_usage,"operator_usage":operator_usage,"cross_book_references":registry.get("cross_book_references",[])}

def where_used(atom_id: str, registry_path: Path = DEFAULT_REGISTRY) -> List[str]: return build_index(registry_path)["atom_usage"].get(atom_id,[])

def freeze_edition(registry_path: Path = DEFAULT_REGISTRY) -> Dict[str, Any]:
    registry=load_registry(registry_path); root=registry_path.parent; index=build_index(registry_path)
    shared_path=root/registry["shared_atom_catalog"]; shared_catalog=_load(shared_path)
    operator_rel=registry.get("operator_catalog","operators.json"); operator_path=root/operator_rel; operator_catalog=_load(operator_path)
    files={registry_path.name:_file_digest(registry_path),registry["shared_atom_catalog"]:_file_digest(shared_path),operator_rel:_file_digest(operator_path)}
    atom_digests={a["id"]:_digest_obj(a) for a in shared_catalog["atoms"]}; atom_scope={a["id"]:"SHARED" for a in shared_catalog["atoms"]}
    operator_digests={o["id"]:_digest_obj(o) for o in operator_catalog.get("operators",[])}; entry_graph_digests={}
    for entry_id,entry in sorted(index["entries"].items()):
        graph_path=root/entry["graph"]; graph=_load(graph_path); digest=_file_digest(graph_path)
        files[entry["graph"]]=digest; entry_graph_digests[entry_id]=digest
        for atom in graph.get("atoms",[]): atom_digests[atom["id"]]=_digest_obj(atom); atom_scope[atom["id"]]=entry_id
    payload={"files":dict(sorted(files.items())),"atom_digests":dict(sorted(atom_digests.items())),"atom_scope":dict(sorted(atom_scope.items())),"operator_digests":dict(sorted(operator_digests.items())),"entry_graph_digests":dict(sorted(entry_graph_digests.items())),"atom_usage":index["atom_usage"],"operator_usage":index["operator_usage"]}
    edition_digest=_digest_obj(payload)
    return {"schema":"gloob-registry-edition/0.3","id":f"EDITION-GLOOB-{edition_digest[:12].upper()}","sha256":edition_digest,**payload}

def semantic_diff(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    old_atoms=old.get("atom_digests",{}); new_atoms=new.get("atom_digests",{})
    changed_atoms=sorted(a for a in set(old_atoms)|set(new_atoms) if old_atoms.get(a)!=new_atoms.get(a))
    old_graphs=old.get("entry_graph_digests",{}); new_graphs=new.get("entry_graph_digests",{})
    changed_entry_graphs=sorted(e for e in set(old_graphs)|set(new_graphs) if old_graphs.get(e)!=new_graphs.get(e))
    old_ops=old.get("operator_digests",{}); new_ops=new.get("operator_digests",{})
    changed_operators=sorted(o for o in set(old_ops)|set(new_ops) if old_ops.get(o)!=new_ops.get(o))
    affected=set(changed_entry_graphs); scopes={**old.get("atom_scope",{}),**new.get("atom_scope",{})}; usage={**old.get("atom_usage",{}),**new.get("atom_usage",{})}; op_usage={**old.get("operator_usage",{}),**new.get("operator_usage",{})}
    for atom_id in changed_atoms:
        scope=scopes.get(atom_id)
        if scope and scope!="SHARED": affected.add(scope)
        affected.update(usage.get(atom_id,[]))
    for op_id in changed_operators: affected.update(op_usage.get(op_id,[]))
    return {"schema":"gloob-registry-semantic-diff/0.3","from":old.get("id"),"to":new.get("id"),"changed_atoms":changed_atoms,"changed_operators":changed_operators,"changed_entry_graphs":changed_entry_graphs,"affected_entries":sorted(affected)}

def simulate_atom_change(snapshot: Dict[str, Any], atom_id: str) -> Dict[str, Any]:
    changed=copy.deepcopy(snapshot)
    if atom_id not in changed["atom_digests"]: raise KeyError(atom_id)
    changed["atom_digests"][atom_id]=_digest_obj({"previous":changed["atom_digests"][atom_id],"mutation":"simulated"})
    changed["sha256"]=_digest_obj({k:v for k,v in changed.items() if k!="sha256"}); changed["id"]=f"EDITION-GLOOB-{changed['sha256'][:12].upper()}"; return changed

def _write_or_print(value: Any, output: str | None) -> None:
    text=json.dumps(value,indent=2,sort_keys=True)+"\n"
    if output: Path(output).write_text(text,encoding="utf-8")
    else: print(text,end="")

def main() -> None:
    parser=argparse.ArgumentParser(description="Gloob Book Registry v0.2"); parser.add_argument("--registry",default=str(DEFAULT_REGISTRY)); sub=parser.add_subparsers(dest="command",required=True)
    p_index=sub.add_parser("index"); p_index.add_argument("--output")
    p_where=sub.add_parser("where-used"); p_where.add_argument("atom_id")
    p_freeze=sub.add_parser("freeze"); p_freeze.add_argument("--output")
    p_diff=sub.add_parser("diff"); p_diff.add_argument("old"); p_diff.add_argument("new"); p_diff.add_argument("--output")
    args=parser.parse_args(); registry_path=Path(args.registry)
    if args.command=="index": _write_or_print(build_index(registry_path),args.output)
    elif args.command=="where-used": _write_or_print({"atom_id":args.atom_id,"entries":where_used(args.atom_id,registry_path)},None)
    elif args.command=="freeze": _write_or_print(freeze_edition(registry_path),args.output)
    elif args.command=="diff": _write_or_print(semantic_diff(_load(Path(args.old)),_load(Path(args.new))),args.output)
if __name__=="__main__": main()
