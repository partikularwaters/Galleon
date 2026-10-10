# Route memory procedures by the actual job

A recurring catalogue project captures both data-import work and editorial reviews.
The import procedure needs source provenance and rejected-row evidence; editorial
review needs reviewed entries and unresolved wording decisions. Reading every
special-case instruction at each handoff has become unnecessary work.

The project could keep its existing memory entries and give those cases focused
procedures:

```text
memory/
  CONTEXT.md                    routes to modes and existing state owners
  capture.md                    common save rules and case selection
  capture/
    import-job.md               import-specific inputs and evidence owners
    editorial-review.md         review-specific inputs and decision owners
  restore.md                    common read-only checks and case selection
  restore/
    import-job.md               recover current import and unresolved rows
    editorial-review.md         recover review scope and outstanding decisions
```

This is an option, not the next stage every project must reach. If only capture
needs separate cases, restore.md can remain one cohesive procedure. Existing task,
progress, and decision records stay at their owners outside these procedure files.
The capture.md and restore.md entries explicitly own their linked directories;
additional folder routers are unnecessary when these routes already suffice.

A small capture entry could say:

> Read the current task and verify its actual result. Save continuation at the
> existing session owner; decisions and detailed evidence retain their own homes.
> For an import handoff, follow capture/import-job.md. For an editorial handoff,
> follow capture/editorial-review.md. Neither route may originate acceptance.
> If both jobs need capture, use the project's declared order or resolve overlapping
> writes first. Do not guess an order or load every case by default.

An import-specific procedure could say:

> Select for a current import job. Read the capture entry, selected task, source
> provenance, and rejected-row report. Save the import's verified position and next
> action at the existing session owner, linking to those evidence owners. Stop if
> the observed source or result contradicts the task. Do not duplicate the reports.

Restore follows its own entry and selected case without writes. A capture route
does not establish permission to use the same writes during restoration.

Benefit: the agent reads common rules and the relevant case, while each owner
maintains one procedure. Cost: selection conditions and links need maintenance.
A split helps only if the whole selected path is clearer and proportionate.
If one procedure is merely verbose, tighten repetition and use section reads
instead. Keep useful, cohesive references intact.

Use the [entry form](../_templates/memory-procedure-router.md) and
[focused procedure form](../_templates/memory-focused-procedure.md) for a concrete
proposal. Map the original instructions and update their incoming routes before
an agreed reorganization. These synthetic examples assert no executed migration or
fresh-session result.
