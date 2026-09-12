# Gloob Book slug index

Canonical Book address: `gloob://qplant`

| Object | Immutable ID | Slug | Gloob / Markdown address |
|---|---|---|---|
| Book | `BOOK-QPLANT` | `qplant` | `gloob://qplant` |
| Chapter | `CH-ENERGY` | `energy` | `gloob://qplant/energy` |
| Entry | `ENTRY-LKT-INVCOP` | `lkt-invcop` | `gloob://qplant/energy/lkt-invcop` |
| Atom | `ATOM-LKT-INVCOP-DECISION` | `offered-point-status` | `#offered-point-status` |
| Atom | `ATOM-LKT-INVCOP` | `invcop` | `#invcop` |
| Atom | `ATOM-LKT-QEQ` | `equivalent-load` | `#equivalent-load` |
| Atom | `ATOM-LKT-POWER` | `total-power` | `#total-power` |
| Atom | `ATOM-LKT-DIRECT-SUBTOTAL` | `direct-load-subtotal` | `#direct-load-subtotal` |
| Atom | `ATOM-LKT-CWS` | `cws-support` | `#cws-support` |
| Atom | `ATOM-LKT-EXPECTED` | `expected-pre-uncertainty` | `#expected-pre-uncertainty` |
| Atom | `ATOM-LKT-UNCERTAINTY` | `power-uncertainty` | `#power-uncertainty` |
| Atom | `ATOM-LKT-SAT` | `sat-metering-boundary` | `#sat-metering-boundary` |
| Atom | `ATOM-LKT-SOURCE` | `engineering-source` | `#engineering-source` |
| Atom | `ATOM-CODEX-RECEIPT` | `runtime-receipt-pattern` | `#runtime-receipt-pattern` |

## Rule

Slugs are human navigation aliases. Immutable IDs remain the join keys for semantic graph edges, provenance, receipts and rename-safe lineage.

Where a Markdown renderer auto-generates heading anchors, prefer the canonical slug above for links emitted by Gloob. The HTML gateway uses these slugs explicitly as DOM IDs and URL hash targets.
