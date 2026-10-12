# Preserve session work deliberately

We recommend a durable place for verified state and a clear procedure for reading
it next time. Chat history alone is a weak handoff: a new session may not have it,
and important decisions can be buried among abandoned ideas.

Prefer the project's existing convention when it works. If no such convention
exists, propose compact memory first, with a concrete preview. Explain the other
forms rather than prescribing a universal skeleton. For a disposable answer with
no continuation need, a saved memory structure may be unnecessary.

## Contents

- [Reading this guide](#reading-this-guide)
- [Three useful forms](#three-useful-forms)
- [Start with one procedure entry](#start-with-one-procedure-entry)
- [Capture and restore are different modes](#capture-and-restore-are-different-modes)
- [Split procedures only when useful](#split-procedures-only-when-useful)
- [When separate procedures also grow crowded](#when-separate-procedures-also-grow-crowded)
- [When current records accumulate settled history](#when-current-records-accumulate-settled-history)
- [Check the claim you actually need](#check-the-claim-you-actually-need)
- [Optional reading-cost routine](#optional-reading-cost-routine)

## Reading this guide

If the project already defines adequate capture and restore procedures, use them
and skip this guide. Otherwise read the comparison below, then only the selected
example and relevant template. Read the procedure-split section only when different
inputs, rules, or maintenance justify that question. If already separated procedures
cover several distinct jobs, read the routed-procedure section instead. Do not load
every alternative.

## Three useful forms

| Form | Choose when | Benefit | Cost |
| --- | --- | --- | --- |
| [Compact](examples/memory-compact.md) | One active job and few owners | A clear save/resume route with two files | State needs pruning as work accumulates |
| [Linked existing homes](examples/memory-linked.md) | Decisions, progress, and evidence already have owners | Preserve those owners without competing copies | Routes must stay accurate |
| [Separated](examples/memory-separated.md) | Different readers need different kinds of state | Focused reads and distinct maintenance | More records and links to maintain |

Recommend compact memory for a new, small project unless its work suggests a better
form. Recommend linked homes before replacing an existing working system. Separation
must earn its place through different inputs, rules, readers, or maintenance needs,
not through file length alone.

## Start with one procedure entry

```text
memory/
  CONTEXT.md    capture and restore procedures
  state.md      verified current work and next action
```

For example: "We could add `memory/CONTEXT.md` to say how to save and resume work,
and `memory/state.md` to hold the current job, checked result, unresolved issues,
and next action. This gives the next session a reliable starting point. If your
existing task record already does this, we can use it instead."

Show the [procedure template](_templates/memory-CONTEXT.md) and
[state template](_templates/memory-state.md), adjusted to actual owners. The template
file is named `memory-CONTEXT.md` to distinguish it in this library; its proposed
project destination is `memory/CONTEXT.md`. Do not apply it just because it exists.

## Capture and restore are different modes

Capture checks actual work, then writes verified state at agreed record homes.
Restore reads those records, checks the current project, and reports the next action.
Restore does not silently update notes, repair files, or turn old checks into current
results. A matching Git commit alone cannot establish that uncommitted files match.

Keep both modes in `memory/CONTEXT.md` initially. Name each mode's inputs, permitted
writes, checks, and stopping behavior. Decisions, evidence, and implementation must
retain their existing owners. Save actual approval when relevant, never invent it.

## Split procedures only when useful

```text
memory/
  CONTEXT.md    routes to each procedure and state owner
  capture.md    save procedure
  restore.md    read-only resume procedure
  state.md
```

Separate procedures when saving and resuming need materially different inputs,
rules, or maintenance. Use the [capture](_templates/capture.md) and
[restore](_templates/restore.md) templates as starting points, leaving a small router
in CONTEXT.md. Procedure separation does not require separate state records, and
separate state records do not automatically require separate procedure files.
An existing `restoration.md` or another coherent name can remain authoritative.

Remember performs capture and can recommend a missing boundary or earned split.
Charter proposes the design. Scaffold establishes agreed missing files; Import
applies an agreed change to existing ones. Do not restructure during capture.

## When separate procedures also grow crowded

First identify what is growing. Move accumulated task evidence back to its existing
owner, remove avoidable repetition through an agreed edit, or read only relevant
sections when a procedure remains cohesive. A longer capture.md or restore.md is
not automatically a reason to create more files.

When distinct recurring jobs have different inputs, record owners, or checks,
keep the existing mode entry as a short router and give each case a focused
procedure. Common mandatory rules stay at that entry; each selected case narrows
them. Restore and all its cases remain read-only. Split only the mode that needs
it, rather than mirroring directories for symmetry.

The [routed example](examples/memory-routed-procedures.md),
[entry form](_templates/memory-procedure-router.md), and
[focused procedure form](_templates/memory-focused-procedure.md) show this option.
Read them only for this particular growth problem. Compare the whole selected
reading path, including the router and common rules; smaller individual files do
not necessarily make the job cheaper or clearer.

Propose a preservation mapping before reorganization: where each original rule
will live, which links change, and which selection paths need checking. Keep one
active owner per rule and no competing old procedure. Charter plans this change;
Import applies an agreed mapping. Remember can identify the need but does not
reorganize while saving. If a focused case later grows, use the same test again:
real differences in work justify separation; arbitrary length does not.

## When current records accumulate settled history

This differs from a complicated capture or restore procedure. Keep current work,
blockers, and the next action in the live record; move coherent settled threads or
completed milestones to numbered history only under an agreed capture procedure.
Preserve unresolved consequences in current memory, and keep decisions and evidence
at their existing owners. Session narrative and progress outcomes are different
responsibilities, not duplicate histories.

The [numbered-history example](examples/memory-numbered-history.md) and
[rollover form](_templates/memory-history-rollover.md) show a concrete option.
Place index.md inside the collection it lists, such as history/ or completed/.
The parent entry links to that index without repeating its contents. An existing
small index can remain instead; CONTEXT.md is for a distinct working contract or
entry responsibility, not merely a folder with several items.

Use stable archive-order numbers and descriptive topics. No renumbering, compulsory
phase scheme, or fixed count threshold is needed. Verify preservation and links
before removing moved details from the live record. Restore reads current records
first, then selected history only when relevant. An authorized routine rollover
is part of capture; designing a new layout remains a structural proposal.

## Check the claim you actually need

Verify that the saved facts match the work. When dependable fresh-session recovery
matters, observe a fresh session using the project's route and plain resume request.
Report any outside memory or coaching that influenced it. A planted-drift exercise
can test stopping behavior for consequential work; it is not compulsory after every
save. Keep project-specific verification requirements intact.

Do not save credentials, unnecessary personal details, or full transcripts by
default. These working records are not automatically suitable for public Git.

## Optional reading-cost routine

A project can use a small reading-cost check to notice when routine context grows
crowded. The purpose is to keep coding agents focused and support progressive
reading: start with the entry and current task, then load detail when the job needs
it. Measurement makes growth visible, so the project can address unnecessary reading
before it becomes habitual. But a count cannot guarantee that files stay lean or
that an agent follows their routes. Clear ownership and useful navigation still matter.

If this would help, propose a reading set in the existing memory or phase contract.
Use the project's own command first; the [optional estimator](token-count.md) accepts
explicit files when no adequate command exists. No repository scan is needed.

Include the entry instructions and routers used to resume, the current continuation
record, the active plan or phase contract, and references that phase actually requires.
Include source files only when their reading cost matters to the job. Leave out
installed dependencies, generated output, old history, and previous count reports
unless the current work specifically needs them. A linked-home project should name
its existing state owner, not create memory/state.md to fit this example.

The project chooses the checkpoints. A useful proposal is:

- At session start, read the saved summary and resolve the current reading set.
  Remeasure if the project requires a fresh estimate; otherwise label it as saved
  evidence rather than a measurement of current files.
- After a completed phase, measure the records needed to understand its result or
  begin the next phase. Identify which set was measured because different phases
  may require different files.
- During capture, save a concise summary at the existing continuation owner. Name
  the measured files, measurement point, command or method, rough result, and
  interpretation. Link to a fuller report only if one is useful and has an agreed home.

Restore stays read-only. Running a read-only measurement can fit restoration, but
saving its output belongs to authorized capture or subsequent work. Report an input
failure and its effect on the estimate; do not treat a failed count as success.

For example: "The next phase needs the task plan and storage reference. The reference
has grown, but only its migration section is relevant. Read that section first;
keep the file intact unless repeated reading needs or different owners justify a
split." The helper measures whole files, so this is a reading recommendation, not
a measured section count. If there is no useful change to propose, record that and
continue; do not ask the human what to do after every count. Apply the project's
approval rules when a consequential change is proposed.

Compare trends only when the file set and measurement method are comparable.
Growth alone does not establish bloat, and a large cohesive reference may be useful.
Counts also do not verify content integrity: two different files can have the same
count. Keep any required byte or result checks separate.

The summary describes the files at the measurement point, usually before saving
it. Exclude a separate count report from routine measurement, and do not repeatedly
remeasure and rewrite a state record just because adding its summary changes its
length. The [compact example](examples/memory-compact.md) shows a small declared set.
