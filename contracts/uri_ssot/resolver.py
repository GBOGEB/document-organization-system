#!/usr/bin/env python3
"""URI SSOT resolver: RFC 3986 parse, RFC 3986 section 6 normalization, contract emit.

Reference implementation for ``Resolve-GbogebArtifactUri.ps1``; both are checked
against the same vectors in ``vectors.json``.

Rules (DOV = definition of validity):

DOV-1  ``None``, empty or whitespace-only input resolves to ``None``.
DOV-2  An empty authority (``file:///C:/x`` -> ``""``) is distinct from an
       absent one (``urn:a:b`` -> ``None``); ``has_authority`` records which.
DOV-3  ``foo:bar/baz`` is an absolute URI with scheme ``foo`` (RFC 3986 section
       3.1); it is never demoted to a relative path. The ``./`` prefix belongs
       to *writing* a relative reference whose first segment contains a colon
       (section 4.2); ``to_relative_reference`` does that.

Windows drive paths (``C:\\x``, ``C:/x``) and UNC paths (``\\\\host\\share``)
are file-system paths, not URIs; they are classified as such and converted to
``file:`` URIs per RFC 8089 appendix E. ``javascript:``, ``vbscript:`` and
``data:`` URIs are kept as parsed but flagged ``executable_scheme`` so a
consumer can refuse them. A ``#oid:<dotted>`` fragment yields ``fragment_oid``;
no OID is ever invented. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Optional

SCHEMA_VERSION = "gbogeb.uri-ssot/1"
EXECUTABLE_SCHEMES = frozenset({"javascript", "vbscript", "data"})

# RFC 3986 appendix B, with the scheme restricted to the section 3.1 grammar.
_URI = re.compile(
    r"^(?:(?P<scheme>[A-Za-z][A-Za-z0-9+.\-]*):)?"
    r"(?://(?P<authority>[^/?#]*))?"
    r"(?P<path>[^?#]*)"
    r"(?:\?(?P<query>[^#]*))?"
    r"(?:#(?P<fragment>.*))?$",
    re.DOTALL,
)
_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
_UNC = re.compile(r"^\\\\[^\\/]+[\\/]")
_PCT = re.compile(r"%[0-9A-Fa-f]{2}")
_OID = re.compile(r"^oid:(?P<oid>[0-2](?:\.(?:0|[1-9][0-9]*))+)$")


def remove_dot_segments(path: str) -> str:
    """RFC 3986 section 5.2.4."""
    out: list[str] = []
    while path:
        if path.startswith("../"):
            path = path[3:]
        elif path.startswith("./"):
            path = path[2:]
        elif path.startswith("/./"):
            path = path[2:]
        elif path == "/.":
            path = "/"
        elif path.startswith("/../"):
            path = path[3:]
            if out:
                out.pop()
        elif path == "/..":
            path = "/"
            if out:
                out.pop()
        elif path in (".", ".."):
            path = ""
        else:
            start = 1 if path.startswith("/") else 0
            cut = path.find("/", start)
            seg, path = (path, "") if cut == -1 else (path[:cut], path[cut:])
            out.append(seg)
    return "".join(out)


def _upper_pct(text: str) -> str:
    """RFC 3986 section 6.2.2.1: percent-encoding hex digits are case-normalized."""
    return _PCT.sub(lambda m: m.group(0).upper(), text)


def _normalize_authority(authority: str) -> str:
    """Lower-case the host only (userinfo and port are left as given)."""
    userinfo, sep, hostport = authority.rpartition("@")
    if hostport.startswith("["):  # IP-literal
        end = hostport.find("]")
        host, rest = (hostport[: end + 1], hostport[end + 1:]) if end != -1 else (hostport, "")
    else:
        host, colon, port = hostport.partition(":")
        rest = colon + port
    return f"{userinfo}{sep}{_upper_pct(host.lower())}{rest}"


def to_relative_reference(path: str) -> str:
    """Write ``path`` as a relative reference (RFC 3986 section 4.2).

    A first segment containing ``:`` would be read as a scheme, so it gets a
    ``./`` prefix; ``foo:bar/baz`` -> ``./foo:bar/baz``.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError("path must be a non-empty string")
    first = path.split("/", 1)[0]
    if ":" in first:
        return "./" + path
    return path


def _windows_path_to_file_uri(text: str) -> str:
    """RFC 8089 appendix E.2 (drive letter) and E.3 (UNC)."""
    forward = text.replace("\\", "/")
    if _UNC.match(text):
        return "file:" + forward  # //host/share/... -> file://host/share/...
    return "file:///" + forward


def resolve(text: Optional[str]) -> Optional[dict]:
    """Return the URI SSOT contract for ``text``, or ``None`` (DOV-1)."""
    if text is None or not isinstance(text, str) or not text.strip():
        return None
    original = text
    trimmed = text.strip()
    kind = "uri"
    if _DRIVE.match(trimmed):
        kind, trimmed = "windows_drive_path", _windows_path_to_file_uri(trimmed)
    elif _UNC.match(trimmed):
        kind, trimmed = "unc_path", _windows_path_to_file_uri(trimmed)

    m = _URI.match(trimmed)
    if m is None:  # appendix B matches every string; kept fail-closed
        raise ValueError(f"unparseable reference: {original!r}")
    scheme = m.group("scheme")
    authority = m.group("authority")
    path, query, fragment = m.group("path"), m.group("query"), m.group("fragment")

    is_absolute = scheme is not None
    if kind == "uri":
        kind = "absolute_uri" if is_absolute else "relative_reference"
    scheme_n = scheme.lower() if scheme else None
    authority_n = _normalize_authority(authority) if authority is not None else None
    path_n = _upper_pct(path)
    if is_absolute or authority is not None:
        path_n = remove_dot_segments(path_n)
    query_n = _upper_pct(query) if query is not None else None
    fragment_n = _upper_pct(fragment) if fragment is not None else None

    # RFC 3986 section 5.3 recomposition.
    canonical = ""
    if scheme_n is not None:
        canonical += scheme_n + ":"
    if authority_n is not None:
        canonical += "//" + authority_n
    canonical += path_n
    if query_n is not None:
        canonical += "?" + query_n
    if fragment_n is not None:
        canonical += "#" + fragment_n

    oid_match = _OID.match(fragment) if fragment is not None else None
    return {
        "schema_version": SCHEMA_VERSION,
        "original": original,
        "kind": kind,
        "is_absolute": is_absolute,
        "scheme": scheme_n,
        "has_authority": authority is not None,
        "authority": authority_n,
        "path": path_n,
        "query": query_n,
        "fragment": fragment_n,
        "fragment_oid": oid_match.group("oid") if oid_match else None,
        "executable_scheme": scheme_n in EXECUTABLE_SCHEMES,
        "canonical": canonical,
    }


if __name__ == "__main__":
    for arg in sys.argv[1:] or [sys.stdin.read()]:
        sys.stdout.write(json.dumps(resolve(arg), indent=2, sort_keys=True) + "\n")
