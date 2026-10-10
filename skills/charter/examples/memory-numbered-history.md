# Current memory with numbered history

A small application has finished foundation and UI work and is now building motion.
Its capture procedure already permits preserving settled threads and completed
milestones. Session continuity and progress need different summaries, but do not
need separate folder contracts yet.

```text
memory/
  CONTEXT.md                   owners, modes, and relevant routes
  capture.md                   save and agreed rollover procedure
  restore.md                   read-only recovery procedure
  sessions/
    session.md                 current continuation and unresolved threads
    history/
      index.md                 short links and coverage labels
      01-foundation-work.md
      02-ui-work.md
  progress/
    progress.md                active work, blockers, and current milestone
    completed/
      index.md                 short links to completed outcomes
      01-first-version.md
      02-first-version-rework.md
```

The project can begin smaller: capture and restore may share memory/CONTEXT.md,
and one existing current-state owner may suffice. This example shows numbered
history, not a mandatory memory skeleton. Existing decision and evidence owners
stay outside these summaries; do not relocate them just to match this tree.

A current session note could say:

> UI work is settled; its useful history is in history/02-ui-work.md. Motion work
> is active, and reduced-motion behavior still needs review. The next action is to
> check that behavior under the current task agreement. Its decisions and evidence
> remain in that task's existing records.

An index inside history/ could contain these short entries, linked to the actual
files when adopted:

| Record | Coverage | Read when |
| --- | --- | --- |
| 01-foundation-work.md | Initial setup and its unresolved constraints | The current job depends on those constraints |
| 02-ui-work.md | Settled UI thread and links to evidence | A UI decision or implementation needs tracing |

The parent memory entry points to sessions/session.md for continuation and
progress/progress.md for task status. Each current record or the entry can point to
its collection's index. Do not copy the whole history listing into every router.
If useful short lists already live at an adequate owner, an index file is optional.

```text
Settled thread or milestone
  -> preserve a coherent numbered record
  -> add its index link
  -> retain open work and a pointer in current memory
  -> verify preservation and routes

New session
  -> current records
  -> relevant index, only if needed
  -> selected history, only if needed
```

The two number sequences are independent. A completed progress record names what
met the project's completion criteria, while a historical session record explains
useful continuity. Archiving a thread does not complete its unfinished tasks.
A version label in a filename does not establish a published release.

Use the [rollover form](../_templates/memory-history-rollover.md) for the procedure,
and adapt the existing [state form](../_templates/memory-state.md) or
[record form](../_templates/record.md) rather than requiring new schemas. If a
folder later needs distinct capture, access, or maintenance rules, propose a local
CONTEXT.md; index.md remains the collection list. Do not add a contract just because
several numbered files exist.

Benefit: current reads stay focused while earlier work remains findable. Cost:
indices and links need maintenance, and the distinction between current status and
history must stay clear. Use meaningful boundaries instead of splitting coherent
work at an arbitrary size. These are synthetic examples, not an observed rollover
or proof of independent restoration.
