# Linked existing homes

Use this when the project already has useful architecture, decision, and progress
records. Keep them authoritative and connect them through a small router.

```text
project/
  AGENTS.md
  CONTEXT.md
  architecture/
    overview.md
  decisions/
    storage-choice.md
  tasks/
    indexing.md
  progress.md
```

For example, `CONTEXT.md` routes design questions to `architecture/overview.md`,
storage decisions to `decisions/storage-choice.md`, and current indexing work to
`tasks/indexing.md`. The task links to the storage decision instead of copying it.
The existing `progress.md` owns the current state and next action.

Benefit: existing knowledge survives without competing copies.
Cost: links need maintenance, and owners must be clear.
Do not create a new memory directory when the existing progress record already
supports continuation. If only one task matters, a compact record may suffice.
