# Gloob synchronized views v0.4

One selected semantic ID drives Book, Graph, Provenance, Timeline, and Runtime projections.

## Invariants

- Book and Graph share immutable semantic IDs.
- Selecting an Atom in either projection selects the same ID.
- Provenance expands by summary, evidence, and runtime levels.
- Timeline events are exact-SHA and workflow-run bound.
- Runtime receipts prove publication/runtime behaviour only and do not confer engineering acceptance.
- Gateway v0.3 routing remains backward compatible.
