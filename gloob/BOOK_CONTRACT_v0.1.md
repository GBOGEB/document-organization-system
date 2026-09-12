# Gloob Book Contract v0.1

## Purpose

A Gloob Book is one logical semantic publication assembled from many repositories, sources and operators. Repositories remain authoritative for their own facts; the Book Manifest federates those facts without copying authority.

## Canonical hierarchy

`LIBRARY -> BOOK -> EDITION -> CHAPTER -> ENTRY -> ATOM`

Execution and provenance objects are orthogonal:

`SOURCE -> AUTHORITY -> OPERATOR -> RUN -> RECEIPT`

Presentation objects are projections:

`VIEW -> DEPTH -> RENDERER -> ARTIFACT`

## IDs and Markdown-friendly slugs

Every addressable object has:

- an immutable machine ID, for joins and lineage;
- a human slug, for navigation and Markdown anchors where possible;
- a canonical Gloob URI built from slugs.

Example:

```text
ID:      ENTRY-LKT-INVCOP
slug:    lkt-invcop
URI:     gloob://qplant/energy/lkt-invcop
heading: ## LKT invCOP offered point
anchor:  #lkt-invcop-offered-point
```

Slug rules:

1. lowercase ASCII;
2. words separated by `-`;
3. stable within the parent scope;
4. no semantic meaning is inferred from a slug alone;
5. renaming a slug does not change the immutable ID;
6. aliases may preserve old Markdown links after a rename.

## Authority classes

- `CANONICAL`: repo owns the fact/object.
- `FEDERATED`: repo contributes content without becoming the owner of all book semantics.
- `DERIVED`: generated from bound canonical/federated inputs.
- `RUNTIME_RECEIPT`: observed execution/provenance evidence; not engineering acceptance by itself.

## Edge vocabulary v0.1

- `CONTAINS`
- `HAS_ATOM`
- `SOURCED_FROM`
- `AUTHORITY_FOR`
- `TRANSFORMED_BY`
- `EMITS_RECEIPT`
- `PROJECTS_AS`
- `ALIASES`

## Depth projection

Atoms carry a minimum depth. A projection includes atoms where `min_depth <= requested_depth`.

| Profile | Depth | Intent |
|---|---:|---|
| compact | 1 | decision/executive surface |
| standard | 3 | normal engineering book view |
| deep | 5 | calculations, source binding and provenance |

The same graph is rendered at every depth; no separate compact or deep source document is maintained.

## DoD v0.1

- Book Manifest exists and is source-bound.
- IDs, slugs and Gloob URIs validate.
- One QPLANT entry binds at least two repositories.
- Source/authority and operator/receipt edges are explicit.
- Compact, standard and deep projections are monotonic.
- One renderer emits HTML, Markdown and PDF from the same JSON graph.
- Every render emits a SHA-256 receipt binding graph input, profile/depth and output hashes.

## DoV v0.1

Change one canonical atom value, rerun the renderer, and prove:

1. all affected projections change;
2. unaffected stable IDs remain unchanged;
3. source bindings still resolve to repo/path/commit;
4. every artifact receipt binds to the new graph SHA-256.
