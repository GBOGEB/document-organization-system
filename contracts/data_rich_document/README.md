# Data-rich document contract v1

## Purpose

This contract makes a complex engineering document a machine-readable graph without turning the rendered Word/PDF/HTML document into a second source of truth.

The canonical store is JSON. Human-facing formats are projections.

The model is designed for ADR, OCD, RTM/DTM, requirements specifications, technical narratives and other documents where sections, requirements, evidence, interfaces and decisions evolve continuously.

## Core rules

1. **Stable identity beats numbering.** Section IDs such as `SEC-ARCH-001` are immutable. Rendered numbers such as `3.2` are derived from outline position and may change when content moves.
2. **The outline is a placement map, not a content duplicate.** `outline` establishes hierarchy and natural reading order. The canonical title and body live in `sections`.
3. **Content is atomic enough to refine safely.** A section owns ordered `content_blocks` with stable IDs so one paragraph, table, note, decision or requirement summary can be revised without replacing the whole section.
4. **Cross-references are typed edges.** `relations` state why two nodes are connected: `depends_on`, `interfaces_with`, `refines`, `satisfies`, `verifies`, `supersedes`, `precedes`, and so on.
5. **Requirements remain structured data.** A requirement stores its shall statement, rationale, priority, risk, allocation, verification and references independently from where it is rendered.
6. **Change is transactional.** Proposed changes live in `change_sets`. Only approved/applied changes become the current document state. Reversion creates a new change event; history is not erased.
7. **Git is the durable revision ledger.** The JSON `history` summarizes semantic document changes; Git records exact bytes, authorship, branches, diffs and rollback points.
8. **Generated views are disposable.** Word, PDF, Markdown and HTML are outputs described by `render_profiles`; they do not override JSON authority.

## Recommended repository layout

```text
contracts/data_rich_document/
├─ document.schema.json
├─ README.md
├─ validate_document.py
├─ examples/
│  └─ adr-001.json
└─ tests/
   └─ test_validate_document.py
```

## Section placement and natural-flow adaptation

Each section has:
- an immutable `id`
- `parent_section_id`
- a sparse integer `rank` (1000, 2000, 3000...) among siblings
- a `placement` rationale

Sparse ranks intentionally leave insertion space. A new section can be inserted at rank 1500 without renumbering stable IDs. Renderers sort siblings by rank and derive visible numbering.

When new approved content changes the meaning of an older section, update the older section in the same approved change set. Do not append contradictory text merely to preserve history. Preserve the old state in Git/history and use `supersedes` or `refines` relations when the semantic relationship matters.

## Section-level version control

Every section carries:
- `revision.version`
- `revision.status`
- `revision.based_on`
- `revision.updated_at`
- optional `revision.approved_by`

Every content block can carry its own `version`.

This gives two useful scales:
- document release version for externally controlled baselines;
- section/block revision for continuous refinement between baselines.

The validator checks referential and structural invariants. Git remains the exact rollback mechanism.

## Change-set workflow

A bounded edit should follow:

```text
propose
  -> place
  -> analyze affected relations
  -> self-correct dependent text
  -> validate
  -> human approve
  -> apply
  -> render
  -> record receipt/history
```

A `change_set` stores target IDs and JSON-Pointer-like paths, operation, rationale and approval state. This is deliberately compatible with future JSON Patch tooling without making raw patch operations the only authoring interface.

## Multi-interface rendering

`render_profiles` maps the same JSON truth to:
- Word / DOCX: section depth -> Heading 1/2/3..., with numbering supplied by the Word template.
- Markdown: section depth -> `#`, `##`, `###`.
- HTML: stable section IDs become anchors for hyperlinks.
- PDF: generated from an approved DOCX/HTML/Markdown view, carrying document/version metadata.

Visible section numbers must be derived during rendering. They are never the primary key.

## Cross-reference resolution

All internal targets must resolve to an existing:
- section ID
- content block ID
- requirement ID
- relation ID where explicitly allowed

External evidence is declared in `external_references` and addressed by its own stable ID.

This separation prevents a string such as "SR.2" from being ambiguous about whether it is an internal requirement, a section, or an external source.

## Requirement model

A requirement is not merely prose inside a section. It is a structured record with:
- immutable ID
- title
- shall statement
- rationale
- priority
- risk
- section placement links
- external/internal references
- allocation
- verification
- revision metadata

A section may summarize or present requirements, but the requirement object remains authoritative for requirement semantics.

## Approval and rollback

A normal rollback does not delete history. Create a new change set with `reverts_change_set` pointing to the prior applied change set. This creates an auditable forward event that restores a prior semantic state.

## Validation

Run:

```bash
python contracts/data_rich_document/validate_document.py \
  contracts/data_rich_document/examples/adr-001.json

python -m unittest \
  contracts.data_rich_document.tests.test_validate_document
```

The semantic validator checks:
- unique IDs;
- valid section parentage and no hierarchy cycles;
- unique sibling ranks;
- outline/section consistency;
- valid requirement section links;
- valid relation endpoints;
- valid internal references;
- current document version represented in history;
- applied change sets present in history.

JSON Schema validation can additionally be performed by any Draft 2020-12 compatible validator using `document.schema.json`.

## Authority boundary

This contract governs document organization, traceability and projection. It does not create engineering truth by itself. Engineering, procurement, compliance and acceptance claims still require their proper source/approval authority.
