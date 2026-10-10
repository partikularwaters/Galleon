# Compact memory example

A small timer project has one active quiet-mode change and one maintainer.

```text
project/
  AGENTS.md
  memory/
    CONTEXT.md
    state.md
  tasks/
    quiet-mode.md
  src/
```

`memory/CONTEXT.md` contains two modes. Capture reads the task, actual changes, and
current Git state, then writes the state record. Restore reads the state and its
links, compares them with current files, and reports the next action without writes.

A filled `state.md` could say:

> Quiet mode is implemented, and the focused timing checks passed. The result
> still needs the review required by `tasks/quiet-mode.md`. The next action is to
> review whether muted alerts remain understandable. Evidence and decisions live
> in that task record; no dependent change should infer acceptance from the tests.

Benefit: two memory files give the next session a predictable route.
Cost: accumulated jobs can crowd the state record. Keep it current and link to
historical work rather than copying it. An existing task record can serve the same
purpose if it already has clear capture and resume rules.

This is a synthetic example, not an observed project or actual approval.

## Optional focused-reading routine

The timer's maintainer could add this agreement to memory/CONTEXT.md:

```text
Measure at session start and after a completed quiet-mode phase.
Always: AGENTS.md, memory/CONTEXT.md, memory/state.md.
Quiet-mode phase: tasks/quiet-mode.md.
Add a source file only when this phase needs to assess its reading cost.
Use our agreed read-only estimator with explicit paths.
Save the concise summary in memory/state.md during capture.
Restore may measure, but does not save or restructure.
```

For example, the saved summary could identify those four paths, the post-phase
measurement point, the rough estimation method, and whether narrower reads would
help. Actual numbers must come from the command; none are asserted here. A new
phase resolves its own task and references, so this list does not apply forever.
The benefit is a visible, small resume set. The cost is maintaining that set and
interpreting an approximate signal. If the task remains easy to navigate, there
may be no reason to change it.
