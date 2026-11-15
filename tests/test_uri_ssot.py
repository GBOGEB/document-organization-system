#!/usr/bin/env python3
"""URI SSOT resolver: shared vectors, schema conformance and RFC round-trips.

Runs under pytest or as a plain script (standard library only).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "contracts" / "uri_ssot"))

import resolver  # noqa: E402

VECTORS = json.loads((ROOT / "contracts" / "uri_ssot" / "vectors.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "contracts" / "uri_ssot" / "uri-ssot-contract.schema.json").read_text(encoding="utf-8"))
FIELDS = SCHEMA["required"]


def test_vectors_are_not_empty():
    # A gate that checks nothing must not pass.
    assert len(VECTORS["resolve"]) >= 20 and len(VECTORS["to_relative_reference"]) >= 3


def test_resolve_vectors():
    failures = []
    for v in VECTORS["resolve"]:
        got = resolver.resolve(v["input"])
        if v.get("expect_null"):
            if got is not None:
                failures.append((v["id"], "expected null", got))
            continue
        for key, want in v["expect"].items():
            if got is None or got.get(key) != want:
                failures.append((v["id"], key, want, None if got is None else got.get(key)))
    assert not failures, failures


def test_to_relative_reference_vectors():
    for v in VECTORS["to_relative_reference"]:
        assert resolver.to_relative_reference(v["input"]) == v["expect"], v["id"]


def test_relative_reference_round_trip_stays_relative():
    # Writing then re-reading a colon path must give a relative reference
    # with the same path (RFC 3986 section 4.2).
    out = resolver.resolve(resolver.to_relative_reference("foo:bar/baz"))
    assert out["kind"] == "relative_reference" and out["path"] == "./foo:bar/baz"


def test_contract_shape_matches_schema():
    allowed_kinds = set(SCHEMA["properties"]["kind"]["enum"])
    for v in VECTORS["resolve"]:
        got = resolver.resolve(v["input"])
        if got is None:
            continue
        assert list(sorted(got)) == sorted(FIELDS), v["id"]
        assert got["schema_version"] == SCHEMA["properties"]["schema_version"]["const"]
        assert got["kind"] in allowed_kinds
        assert got["has_authority"] == (got["authority"] is not None), v["id"]
        assert got["is_absolute"] == (got["scheme"] is not None), v["id"]


def test_canonical_is_idempotent():
    for v in VECTORS["resolve"]:
        got = resolver.resolve(v["input"])
        if got is None:
            continue
        again = resolver.resolve(got["canonical"])
        assert again["canonical"] == got["canonical"], v["id"]


def test_remove_dot_segments_rfc_examples():
    # RFC 3986 section 5.2.4 worked examples.
    assert resolver.remove_dot_segments("/a/b/c/./../../g") == "/a/g"
    assert resolver.remove_dot_segments("mid/content=5/../6") == "mid/6"


def test_to_relative_reference_rejects_blank():
    for bad in ("", "   ", None):
        try:
            resolver.to_relative_reference(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted {bad!r}")


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001
                failed += 1
                print(f"FAIL {name}: {exc!r}")
    raise SystemExit(1 if failed else 0)
