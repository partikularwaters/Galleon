# Choose the smallest useful working agreement

Start with the real job and its existing owners. A clear instruction in conversation
can be enough for low-impact work. Save an agreement when repeated work, consequential
changes, or handoffs make a durable record useful.

## Show a small example

For example: "Your architecture folder explains the design, but not what this API
reorganization may change. We could put this task agreement in
`architecture/api-reorganization.md`. It would make the scope and completion checks
visible to both you and the coding agent. Alternatively, we can add the same scope
to your existing task record."

When an agreement is missing and an illustration helps, use
[_templates/work-contract.md](_templates/work-contract.md) as a blank and
[the filled example](examples/api-reorganization.md) to illustrate the benefit.
Adapt it to the project; do not impose its folder or wording.

## Names and owners

ICM places a working folder's contract in `CONTEXT.md`: inputs, process, outputs,
and a human check. Use [the folder template](_templates/CONTEXT.md) when that role
is missing and justified. Descriptive kebab-case names fit individual work records.
`_templates/` and `_shared/` distinguish supporting material; an underscore does not
make content private or Git-ignored. Number folders only when sequence matters.

A root entry file routes agents to the records. A larger reference collection can
have its own router. Keep those routes small and keep detailed content at its owner.
Do not force every folder to contain a contract or rename an existing coherent
convention merely to match these examples. Do not keep two copies of the same rule.

## Offer proportionate choices

Explain the actual gap, show the proposed text, and explain the benefit and cost.
Offer an existing record, a small new record, or a narrower task when appropriate.
Resolve missing authority before consequential writes. Once the current agreement
covers the work, use it rather than repeatedly requesting the same approval.

The precedent is [ICM](https://arxiv.org/html/2603.16021v2). These templates are
Galleon's adaptations, not a claim that ICM requires every field below.

## Compare project shapes

These are alternatives, not mandatory skeletons. Each example explains its benefit,
cost, and when to use something smaller:

- [Compact job](examples/compact-job.md): one task with few owners.
- [Linked existing homes](examples/linked-existing-homes.md): connect useful records without copying them.
- [Separated responsibilities](examples/separated-responsibilities.md): distinct planning, review, and continuation needs.
- [Sequential pipeline](examples/sequential-pipeline.md): real recurring stages with intermediate outputs.

Use the optional [plan form](_templates/plan.md) when an existing form is missing.
The reusable blank belongs to Galleon; an adapted agreement belongs to the project.
Do not add a file just to satisfy a template.

## Memory deserves an explicit proposal

Use [memory guidance](memory-guide.md) to compare compact, linked, and separated
forms. Preserve session work deliberately, while respecting existing project style.

## Select by the observed job

Start with existing owners and the actual gap. If an agreement already covers it,
use that agreement and skip these templates. Otherwise read only the relevant
example: a single job, linked owners, separated responsibilities, or a recurring
pipeline. These are choices about responsibility and movement, not maturity levels.
They can coexist when the work warrants it. Never choose a shape by matching names
or because a template happens to be installed.

## Other jobs need different references

These options address movement and retrieval rather than a universal project type.
Consult only the one selected by actual work:

- [Accumulating records](examples/record-library.md): similar instances need retrieval and a consistent record shape.
- [Shared workflows](examples/shared-workflows.md): several real procedures share stable reference owners.
- [Change impact](change-impact.md): an edit's immediate consumers or known failure patterns are unclear.

Stable reference material is not automatically a knowledge bundle. Avoid labels
that hide the actual job. If existing routes and records already explain the work,
keep them rather than adding an index, component card, or workflow tree.

## Measure only when the cost matters

Prefer an existing project command. Otherwise the [optional file estimator](token-count.md)
can provide a labeled rough count without loading file contents into model context.
Size is one factor alongside relevant sections, actual read frequency, ownership,
and migration cost. The measurement does not authorize a split or prove token savings.

## Browse resources when useful

The [forms index](_templates/index.md) lists reusable blanks, and the
[illustrations index](examples/index.md) lists filled examples. Use these for
browsing or finding a known resource. Normal execution follows SKILL.md's
conditional routes and the selected guide; neither index is a mandatory read.
Existing project forms still come first.
