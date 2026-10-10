# Understand what an edit affects

Use this guide when existing project records cannot explain the immediate effects
of a proposed change. Do not build a system-map tree merely because this guide exists.
A small note in the current task may suffice.

## Start from the actual edit

Identify the component or repeated pattern, its source locations, immediate callers
or readers, relevant tests, and known failure modes. Inspect actual references and
behavior; a design intention is not evidence of implementation.

For example, a date formatter might affect a table label and its tests but not the
export serializer, which uses a separate formatter. Confirm both claims from source;
if you have not checked the export path, label its impact unknown instead.

## Keep evidence visible

Distinguish live behavior, leftover material, proposed behavior, and unknowns.
A verified statement names what was checked and its actual source or result.
Record first-order affected consumers and exclusions only when supported. Do not
infer all downstream effects from a component's name or a single passing test.

Preserve known failures at an existing incident or pattern owner so later work can
find them. Link to those facts; do not copy behavior into a second authoritative
specification. Unknown external consumers require a focused question, not an
unbounded search of private files.

## Choose a proportionate record

If an existing architecture record already answers the question, use it and skip
a new template. Otherwise keep the useful facts in the current task. A reusable
component record becomes worthwhile when several changes need the same information.
When that need is concrete, consult [the small form](_templates/change-impact.md)
and [the filled example](examples/change-impact.md). More records cost maintenance;
a stale map can mislead the next agent.

Stop at one sufficient record. Separate objects, processes, or effects only when
actual read or ownership needs justify them. This guide does not authorize writing
a new map, repairing the component, or claiming a general quality improvement.
