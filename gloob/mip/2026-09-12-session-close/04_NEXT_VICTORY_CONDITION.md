# Next victory condition — Book Registry v0.2

Do not reopen Book v0.1 unless an invariant actually fails.

## Execution chain

```text
Book v0.1 CONTROL
    ↓
registry.yaml
    ↓
multiple Book manifests
    ↓
multiple Chapters / Entries
    ↓
shared Atom references
    ↓
reverse WHERE_USED
    ↓
cross-book references
    ↓
Edition freeze + diff
    ↓
incremental affected-entry rebuild
    ↓
exact-head runtime proof
    ↓
Registry v0.2 CONTROL
```

## Minimum acceptance

1. At least two Books registered.
2. At least three Entries registered.
3. At least one Atom is shared by reference, not copied.
4. Reverse `WHERE_USED` resolves every registered Atom to consuming Entries/Books.
5. Edition manifests freeze exact graph/source/operator digests.
6. A one-Atom mutation rebuilds only affected projections.
7. Slug aliases survive rename without changing immutable IDs.
8. Exact-head CI and fresh-main repeat both PASS.
