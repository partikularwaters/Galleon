# Separated responsibilities

Use this when planning, implementation, review, and continuation have distinct
readers or repeated responsibilities. Separate records because their jobs differ.

```text
project/
  AGENTS.md
  CONTEXT.md
  work/
    CONTEXT.md
    plan.md
    result-review.md
  state.md
  src/
```

For example, `work/CONTEXT.md` explains the work area's inputs, permitted outputs,
and review boundary. `plan.md` owns the task scope and checks. `result-review.md`
owns observed findings and limits. `state.md` links to both and names the next
step; it does not repeat their full contents.

Benefit: each reader can find the relevant agreement or evidence quickly.
Cost: more files and links require maintenance.
For a short task with one reader, keep these sections in a single task record.
Separate review evidence does not itself supply human acceptance.
