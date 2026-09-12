# Gloob Book Registry Contract v0.2

## Purpose

Registry v0.2 layers multi-Book discovery, shared semantic reuse and change-impact analysis above the controlled Book v0.1 entry/render contract. It does **not** replace source authority or duplicate source-bearing content.

## Controlled composition

```text
many authority sources
        ↓
entry graphs
        ↓
shared Atom references
        ↓
Book Registry
   ├─ Book index
   ├─ Entry index
   ├─ WHERE_USED
   ├─ cross-Book references
   ├─ Edition freeze/digest
   └─ semantic diff → affected Entries
        ↓
existing Book v0.1 projection/render contract
```

## v0.2 invariants

1. Book and Entry immutable IDs remain the semantic join keys.
2. Slugs remain human-facing aliases, never identity.
3. Every Entry points to one graph path and that graph must declare the same Book/Entry IDs.
4. Shared Atoms are canonical catalog objects referenced by ID; they are not copied into consuming entry graphs.
5. Registry-declared shared Atom references must exactly match the Entry graph `shared_atom_refs` list.
6. Unknown shared Atom IDs fail validation.
7. `WHERE_USED(atom)` returns all consuming Entries, including across Books.
8. Cross-Book references are explicit registry edges and may bind through shared Atoms.
9. An Edition is a deterministic SHA-256 digest over the registry, shared Atom catalog, Entry graph files and per-Atom digests.
10. Semantic diff identifies changed Atoms and Entry graphs, then computes the minimal affected Entry set.
11. A changed shared Atom fans out to every consuming Entry; a changed local Atom affects its owning Entry.
12. Existing Book v0.1 HTML/Markdown/PDF projection tests must remain green.

## Current specimen

Books:
- `BOOK-QPLANT`
- `BOOK-GLOOB`

Entries:
- `ENTRY-LKT-INVCOP`
- `ENTRY-GLOOB-BOOK-CONTRACT`
- `ENTRY-GLOOB-SESSION-CONTROL`

Shared Atoms:
- `ATOM-GLOOB-BOOK-NOT-REPO`
- `ATOM-GLOOB-FEDERATED-AUTHORITY`

The federated-authority Atom is consumed by all three Entries and therefore provides the first executable cross-Book `WHERE_USED` / fan-out specimen.

## Runtime interface

```bash
python gloob/registry.py index
python gloob/registry.py where-used ATOM-GLOOB-FEDERATED-AUTHORITY
python gloob/registry.py freeze --output edition.json
python gloob/registry.py diff old-edition.json new-edition.json
```

## DoD

- [x] Registry manifest
- [x] Multiple Books
- [x] Multiple Entries
- [x] Shared Atom catalog
- [x] Reverse `WHERE_USED`
- [x] Explicit cross-Book reference
- [x] Deterministic Edition freeze
- [x] Semantic Edition diff
- [x] Changed Atom → affected Entry propagation
- [x] Backward compatibility with Book v0.1 graph/render path

## DoV gate

Promotion to `Registry v0.2 CONTROL` requires:

1. exact-head PR CI executes >0 steps and passes all Book v0.1 + Registry v0.2 tests;
2. PR is merged;
3. fresh `main` CI repeats successfully on the merge SHA.
