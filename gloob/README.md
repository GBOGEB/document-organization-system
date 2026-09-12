# Gloob Book v0.1

This directory is the first executable Gloob Book primitive.

## One graph, multiple projections

```text
book.manifest.yaml
      |
graph/qplant-energy.json
      |
      +--> compact  depth 1
      +--> standard depth 3
      +--> deep     depth 5
                 |
                 +--> HTML
                 +--> Markdown
                 +--> PDF
                 +--> SHA-256 receipt
```

## Run

```bash
python gloob/render_book.py --all-profiles
python -m unittest discover -s gloob/tests -p "test_*.py"
```

Generated example slugs follow:

```text
qplant-energy-lkt-invcop-compact.*
qplant-energy-lkt-invcop-standard.*
qplant-energy-lkt-invcop-deep.*
```

Canonical entry address:

```text
gloob://qplant/energy/lkt-invcop
```

Markdown-friendly navigation uses slugs, while immutable IDs remain the semantic/provenance join keys.
