# Accumulating records

Use this when similar records are created, accumulate, and must be retrieved later.
For example, repeated customer-support incidents need consistent identity and links.
This is about retrieval and evidence, not a mandatory execution sequence.

```text
incidents/
  CONTEXT.md
  index.md
  _templates/
    incident.md
  date-parser.md
```

The router explains how to find a record. The index holds short links and useful
retrieval labels; the individual record owns its facts and evidence. A small library
can combine routing and indexing in CONTEXT.md instead of adding a separate index.

Use [the record form](../_templates/record.md) only when an existing form is missing.
For example, a record can identify the symptom, actual state, evidence, and next
response without inventing a status schema or splitting rationale into another file.

Benefit: future work can find prior facts and known failures.
Cost: records and the index need maintenance. Incomplete or inconsistent records
can mislead readers. Prefer one task record when there are few instances and no
retrieval difficulty. Do not label an index a knowledge model merely because it
links to reference material. This layout is synthetic, not an observed success.

An index normally lives inside the folder whose records it lists. A parent router
links to it instead of repeating the listing. When the collection only needs a
contents list and its working rules already have an owner, index.md can suffice
without a local CONTEXT.md. Add a folder contract only for a distinct responsibility.
The [numbered-memory example](memory-numbered-history.md) applies this to settled
session history and completed progress.
