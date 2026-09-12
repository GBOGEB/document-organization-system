# Drop-in fresh-chat resume instruction

Take over **Gloob Book execution** from the controlled MIP closure in `GBOGEB/document-organization-system`.

## Frozen starting state

Treat `GBOGEB/document-organization-system@913f577ae63ef53da71633fad2bbbeb1c646c58a` as the **Book v0.1 CONTROL baseline**.

PR #40 is merged. Its exact head `95c7f72d2a85277cb56c65166ad684aa7feb599c` passed `Gloob Book Contract` in run `34686083249`. The fresh `main` merge SHA `913f577ae63ef53da71633fad2bbbeb1c646c58a` passed the same contract in run `34688334758`, and Pages passed in run `34688334252`.

Therefore do not describe Book v0.1 CI as queued or DoV as withheld. Local Book v0.1 DoD and DoV are ACHIEVED and state is CONTROL.

## Preserve these invariants

- Book is a stable logical semantic publication, not a repository.
- Many sources + many operators → one canonical graph → one Book identity → many depth/views.
- Immutable IDs are semantic join keys.
- Slugs are human navigation aliases and explicit Markdown/HTML anchors.
- Slug rename must not change immutable identity; aliases preserve old links.
- One graph emits compact/standard/deep views and HTML/Markdown/PDF.
- Publication, engineering, cost and runtime-receipt authority remain distinct.
- Runtime receipt proves execution only and does not confer engineering acceptance.
- Authority class and evidence maturity remain separate dimensions.
- Reuse atoms by reference; do not duplicate source-authoritative content.

## Execute next

Implement **Book Registry v0.2** as the next controlled increment:

`registry.yaml → multiple Books → multiple Entries → shared Atoms → WHERE_USED → cross-book references → Edition freeze/diff → affected-entry incremental rebuild`.

Minimum DoD:
1. two Books,
2. three Entries,
3. one shared Atom referenced by more than one Entry/Book,
4. reverse WHERE_USED,
5. immutable Edition manifest/digest,
6. slug aliases,
7. incremental affected-entry rebuild.

Minimum DoV:
- exact-head CI executes >0 steps and PASS,
- mutation proves only affected projections rebuild,
- stable IDs/source bindings do not drift,
- fresh-main exact-SHA repeat PASS.

Do not redesign controlled Book v0.1 semantics unless a failing invariant proves a repair is necessary.

Use the MIP closure files in `gloob/mip/2026-09-12-session-close/` as the session handover authority.
