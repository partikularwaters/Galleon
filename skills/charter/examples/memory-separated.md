# Separated memory example

A recurring catalogue project has different readers for progress, continuation,
and durable decisions. Those distinct needs justify separate record owners.

```text
memory/
  CONTEXT.md
  progress.md
  session.md
  decisions/
    index.md
    identifier-policy.md
```

Progress says: "The import mapping is drafted; it has not been applied."
Session says: "Resolve ownership of the historical note, then review the mapping."
The decision index links to the identifier policy; rationale stays in that record.
Task-specific commands and evidence stay with the task, outside these summaries.

Initially, CONTEXT.md can still contain both capture and restore procedures.
If capture needs detailed write-owner instructions while restore needs a distinct
verification sequence, promote to:

```text
memory/
  CONTEXT.md
  capture.md
  restore.md
  progress.md
  session.md
  decisions/
```

CONTEXT.md now routes rather than repeats the procedure contents.
Benefit: each reader loads the state relevant to its job.
Cost: more links and maintenance. Distinct ownership justifies this structure;
file length alone does not. Keep compact or linked memory when it already works.

This is synthetic, and the illustrated promotion is a proposal, not permission.
