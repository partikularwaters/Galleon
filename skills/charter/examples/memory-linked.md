# Memory linked to existing owners

An existing project already owns progress, decisions, and task evidence separately.

```text
project/
  CONTEXT.md
  memory/
    CONTEXT.md
  progress.md
  decisions/
    storage-choice.md
  tasks/
    indexing.md
```

The memory contract routes capture to those owners: current progress goes to
`progress.md`, durable choices stay in `decisions/`, and task evidence stays in
`tasks/indexing.md`. Restore reads progress and follows only the current task and
relevant decision links. There is no duplicate memory/state.md.

For example, progress says: "Indexing checks passed within the agreed scope.
See the task record for evidence and the storage decision for rationale. Next:
perform the project's required result review before expanding the change."

Benefit: existing authority survives, and readers avoid competing versions.
Cost: inaccurate links or ambiguous owners can break continuation. Check both.
Recommend this form before replacing a working record system with a new one.

This is synthetic; passing checks here are illustrative, not an actual result.
