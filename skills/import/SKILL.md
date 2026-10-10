---
name: import
description: Apply an agreed mapping of existing project context while preserving content and references.
---

# Import

One job: Reorganize existing context according to an agreed mapping.

First read the project's entry instructions and relevant records. Find the owner
of this job and inspect the current files; check Git status when Git is available.
Read only what the task needs. Existing project rules and human authorization govern
scope. A skill invocation is not permission to overwrite files or invent approval.

If an important boundary is missing, explain it in plain language, give a small
concrete example, describe the benefit and tradeoff, and offer proportionate choices.
Use existing homes and rules when they suffice. Do not stop repeatedly for decisions
already covered by the current agreement. Resolve unclear authority before consequential
writes. Keep proposed behavior, observed checks, and accepted work distinct.

1. List source-to-destination mappings, owners, affected links, allowed edits, and preservation checks. Obtain required agreement before applying them.
2. Preserve the current dirty work and a recoverable baseline appropriate to the operation. Check destinations and external references known to the project; do not search unrelated private folders.
3. Copy and verify before retiring sources. Preserve meaningful content and ownership, not just file counts. Do not move application code to fit a generic skeleton.
4. After interruption, inspect partial changes and later edits. Do not guess a rollback or overwrite new work. Report the result, checks, and recovery limits.

Boundaries: Redesigning the mapping during execution, changing application behavior, deleting unrelated work, or accepting its own result.

## Project inputs and conditional resources

Always resolve the agreed mapping, source and destination owners, existing content, affected references, baseline, and preservation/recovery rules.
Use the project's existing contract and forms first. If they adequately cover the
job, skip Galleon's alternative templates and work within those boundaries.

| When | Read | Use it to |
| --- | --- | --- |
| A mapping needs a starting form and none is owned locally | [mapping](_templates/mapping.md) | Make content, owners, consumers, collisions, and recovery explicit before application. |

Do not load every project topic, redesign the mapping, or infer safe retirement from file counts.
Read only relevant sections and examples. Adapt optional forms at existing owners;
a bundled resource does not grant write authority or replace a project agreement.
