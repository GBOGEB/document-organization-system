# Gloob Book / Registry / Gateway

This directory contains the executable Gloob publication stack.

## Controlled stack

```text
Book v0.1
   ↓
Registry v0.2
   ↓
Gateway v0.3
   ↓
Synchronized views v0.4
```

The controlled gateway is `gloob/index.html`. The synchronized Book ↔ Graph, selective provenance, Timeline, and Runtime surface is `gloob/views.html`.

## One graph, multiple projections

```text
registry.yaml
   |
   +--> Book / Entry discovery
   +--> shared Atom references / WHERE_USED
   +--> cross-Book references
   |
entry graph
   |
   +--> compact  depth 1
   +--> standard depth 3
   +--> deep     depth 5
   |             |
   |             +--> HTML
   |             +--> Markdown
   |             +--> PDF
   |             +--> SHA-256 receipt
   |
   +--> synchronized Book / Graph view
   +--> selective provenance
   +--> control timeline
   +--> runtime receipts
```

## Run

```bash
python gloob/render_book.py --all-profiles
python -m unittest discover -s gloob/tests -p "test_*.py"
```

Canonical entry example:

```text
gloob://qplant/energy/lkt-invcop
```

Immutable IDs remain semantic/provenance join keys. Slugs remain human navigation aliases. Runtime receipts prove observed publication/runtime behaviour only and do not confer engineering acceptance.
