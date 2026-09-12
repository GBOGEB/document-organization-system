# Gloob Gateway Contract v0.3

## Purpose

Expose the controlled Book Registry v0.2 through one user-facing Gloob Library gateway without collapsing Book, Entry, Source, Operator, or authority boundaries.

## Routing contract

Canonical browser routes use:

`?book=<book-slug>&entry=<entry-slug>&profile=<compact|standard|deep>#<canonical-atom-slug>`

The route is a presentation alias. Immutable Book/Entry/Atom IDs remain semantic identity.

## Required behaviour

1. Load `registry.yaml` as the discovery authority.
2. Populate Book and Entry selectors from the registry.
3. Resolve the selected Entry to its declared graph path.
4. Preserve compact/standard/deep projection controls.
5. Preserve source-binding visibility and authority wording.
6. Render shared Atoms from the canonical shared-Atom catalog rather than copying them into each Entry graph.
7. Expose cross-Book references as navigable Entry links.
8. Copy a canonical route containing Book, Entry, profile, and canonical Entry hash.
9. Every registry Entry must resolve to an existing graph.
10. Existing Book v0.1 and Registry v0.2 tests remain green.

## Authority boundary

The gateway is a projection/discovery surface only. It does not become authority for engineering facts, cost facts, runtime receipts, or evidence maturity.

## DoV

Gateway v0.3 may be promoted to CONTROL only after:

- exact-head CI executes >0 steps and passes Book v0.1 + MIP + Registry v0.2 + Gateway v0.3 contracts;
- PR merge;
- fresh-main repeat passes;
- Pages deployment passes or, if independently delayed, has no semantic contract failure.
