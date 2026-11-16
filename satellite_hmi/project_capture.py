"""Hash a user-selected export/handover locally; never upload or execute it.

A SHA-256 receipt verifies bytes of the supplied file ONLY, not a full ChatGPT chat.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

MAX_BYTES = 50 * 1024 * 1024


def receipt_for_file(source: Path, alias: str, capture_kind: str) -> dict:
    if not re.fullmatch(r"P[1-5]", alias):
        raise ValueError("Pilot alias must be P1-P5")
    if capture_kind not in {"HANDOVER_ONLY", "FULL_EXPORT", "SOURCE_FILE"}:
        raise ValueError("Unknown capture kind")
    path = source.expanduser().absolute()
    if not path.exists() or not path.is_file():
        raise ValueError("Source must be an existing regular file")
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Symlink source refused")
    before = path.stat()
    if before.st_size > MAX_BYTES:
        raise ValueError("File too large for pilot")
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            total += len(chunk)
            if total > MAX_BYTES:
                raise ValueError("Streaming size limit exceeded")
            h.update(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or total != after.st_size:
        raise ValueError("Source changed during hashing")
    return {
        "schema": "gbogeb.project-local-file-receipt/1",
        "pilot_id": alias,
        "capture_kind": capture_kind,
        "file_bytes": total,
        "sha256_actual_bytes": h.hexdigest(),
        "original_chat_id": None,
        "original_chat_byte_completeness": "UNKNOWN",
        "chat_lossless_claim": False,
        "publication_authorized": False,
        "merge_authorized": False,
        "note": "Hash verifies selected local file bytes, not project transcript coverage",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--alias", required=True, choices=["P1", "P2", "P3", "P4", "P5"])
    ap.add_argument("--capture-kind", required=True, choices=["HANDOVER_ONLY", "FULL_EXPORT", "SOURCE_FILE"])
    ap.add_argument("--receipt", required=True, type=Path)
    args = ap.parse_args()
    result = receipt_for_file(args.source, args.alias, args.capture_kind)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    # x means no overwriting previous evidence; no private source path in the receipt
    with args.receipt.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(f"PILOT_{args.alias}_LOCAL_FILE_HASH_VERIFIED ({result['file_bytes']} bytes); chat reconstruction UNKNOWN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())