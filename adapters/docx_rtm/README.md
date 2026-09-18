# DOCX_RTM adapter — JSON SSOT to Word projection

## Boundary

This adapter projects the canonical data-rich JSON document into the existing
`GBOGEB/DOCX_RTM_Automation` Markdown -> DOCX path. It does **not** create a
second document authority.

Authority stays:

```text
Git exact history
    |
    v
data-rich JSON semantic SSOT
    |
    v
DOCX_RTM projection Markdown + outward manifest
    |
    v
Pandoc + reference.docx
    |
    v
DOCX generated view
```

The live DOCX_RTM implementation currently converts Markdown to DOCX with
Pandoc and `config/reference.docx` in
`src/core/rtm_roundtrip.py::md_to_docx`. This adapter targets that interface.

## Heading contract

The JSON source owns:
- stable section ID;
- title;
- hierarchy;
- semantic revision;
- natural-flow placement.

The DOCX template owns:
- visible multilevel numbering;
- Heading 1 / Heading 2 / Heading 3 appearance;
- paragraph/list/table visual styling.

Mapping:

| JSON | Projection Markdown | Expected Word style |
|---|---|---|
| `heading_level: 1` | `# Title` | Heading 1 |
| `heading_level: 2` | `## Title` | Heading 2 |
| `heading_level: 3` | `### Title` | Heading 3 |

The adapter deliberately emits **unnumbered heading text**. Therefore
`config/filters/extend_headings.lua`, which prepends numbers into heading
text, must not be used for this projection. Word/template multilevel numbering
must supply display values such as `3`, `3.2`, and `3.2.1`.

Stable JSON IDs remain the traceability keys even when the displayed Word
number changes.

## Requirement projection

Requirements stay authoritative in the JSON `requirements` array. For human
readability a requirement is rendered once, beneath its **primary placement**
(the first value in `section_ids`). Secondary section links remain in the
outward manifest instead of duplicating the requirement prose.

## Cross-reference projection

The outward manifest preserves:
- section map;
- requirement primary and secondary placements;
- typed `relations`;
- `external_references`;
- source JSON SHA-256;
- generated Markdown SHA-256;
- exact source Git ref when supplied.

DOCX is therefore reproducible from a pinned JSON state without treating the
DOCX as the source of truth.

## Run

```bash
python adapters/docx_rtm/build_projection.py \
  contracts/data_rich_document/examples/adr-001.json \
  --output-dir /tmp/docx_rtm_projection \
  --source-repo GBOGEB/document-organization-system \
  --source-ref <exact-git-sha>
```

Outputs:

```text
ADR-001.projection.md
ADR-001.outward_document_manifest.json
```

The manifest is the bridge receipt for DOCX_RTM intake.

## Fail-closed rules

The adapter refuses to project when:
- the source fails the canonical semantic validator;
- a section exceeds the configured maximum heading depth (default 3);
- a source title already contains a rendered numeric prefix;
- a requirement primary placement cannot resolve;
- duplicate semantic identities exist.

These checks prevent the projection layer from silently repairing or
reinterpreting authoritative JSON.

## DOCX_RTM consumer contract

The consumer may:
1. consume the generated Markdown;
2. pass it through Pandoc;
3. apply `config/reference.docx`;
4. emit DOCX and its hash/receipt.

The consumer must not:
- edit JSON semantics;
- infer new requirements;
- prepend heading numbers into source title text;
- promote derived output to engineering/compliance authority;
- treat a generated DOCX as a competing SSOT.

## Next integration proof

After this adapter passes exact-head CI, the corresponding
`GBOGEB/DOCX_RTM_Automation` bridge should accept the manifest schema and
perform one bounded Markdown -> DOCX render using its reference template. That
consumer proof is separate from this producer projection proof.
