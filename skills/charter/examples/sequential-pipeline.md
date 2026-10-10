# Sequential pipeline

Use this when a real recurring job has ordered steps with useful intermediate
outputs. ICM's numbered stages express that order.

```text
project/
  AGENTS.md
  CONTEXT.md
  _shared/
    writing-rules.md
  01_research/
    CONTEXT.md
    output/
  02_drafting/
    CONTEXT.md
    output/
```

For example, research produces `01_research/output/findings.md`. The drafting
contract names that file as its working input and `_shared/writing-rules.md` as
its reference. A human checks factual support before drafting proceeds. Each
stage contract names the actual relative paths from its own folder.

Benefit: humans can inspect intermediate work, and agents load only the current
stage's inputs and references.
Cost: a pipeline adds coordination and is unsuitable for work that does not
actually repeat in this order. Do not number folders merely for appearance.
For one report, a compact task record may be enough.
