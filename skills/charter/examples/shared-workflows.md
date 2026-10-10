# Several workflows, shared references

Use this when two real recurring workflows need different procedures but share
stable project rules. A feature workflow and a release workflow may read the same
architecture reference while producing different outputs.

```text
project/
  CONTEXT.md
  references/
    architecture.md
  feature-work/
    CONTEXT.md
  release-work/
    CONTEXT.md
```

The root routes the request to the relevant workflow. Each local contract names its
job, working inputs, outputs, and applicable human decisions. Both link to the same
architecture owner. Neither copies the other workflow's procedure or creates its
own competing architecture specification.

Benefit: separate work stays legible while stable knowledge has one home.
Cost: shared references and routes must remain accurate as workflows evolve.
Keep one contract when the alleged workflows are just variants of one simple task.
Do not create release or pipeline folders for work that has not actually arisen.
This is a synthetic option, not a prescribed lifecycle or verified runtime result.
