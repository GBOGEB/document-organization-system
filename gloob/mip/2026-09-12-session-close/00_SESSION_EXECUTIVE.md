# Gloob Book v0.1 — 3P5 + MIP session closure

Date: 2026-09-12
Repository authority: `GBOGEB/document-organization-system`
Baseline main SHA: `913f577ae63ef53da71633fad2bbbeb1c646c58a`

## Outcome

This session established and runtime-proved the first controlled Gloob Book contract:

- Book is a logical semantic publication, not a repository.
- Many sources and operators may feed one canonical graph.
- Stable immutable IDs are semantic join keys.
- Human-readable slugs are navigation aliases and explicit Markdown/HTML anchors.
- One graph projects to compact, standard and deep views.
- The same graph emits HTML, Markdown and PDF.
- Provenance binds sources, exact repo SHAs, authority class and evidence class.
- Runtime receipts prove execution without conferring engineering acceptance.

## Control state

PR #39 established Book Manifest v0.1.
PR #40 repaired canonical Markdown anchors and added executable mutation-propagation DoV.

PR #40 head:
`95c7f72d2a85277cb56c65166ad684aa7feb599c`

PR #40 merge:
`913f577ae63ef53da71633fad2bbbeb1c646c58a`

Exact-head PR contract run:
`34686083249` → `success`

Fresh-main contract run:
`34688334758` → `success`

Fresh-main Pages run:
`34688334252` → `success`

Therefore:

- Book v0.1 DoD: ACHIEVED
- Book v0.1 runtime DoV: ACHIEVED
- Book v0.1 state: CONTROL
- Global programme DoV: unchanged by this local control promotion

## Next narrow victory condition

Start Book Registry v0.2 without reopening controlled v0.1 semantics:

`registry.yaml → multiple Books → multiple Entries → shared Atoms → WHERE_USED → cross-book references → Edition freeze/diff → affected-entry incremental rebuild`.
