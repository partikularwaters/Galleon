# Numbered memory-history rollover

Purpose: keep current continuation concise while preserving settled work.
Authority: {existing memory contract and record owners}
Selected record: {current session or progress record}
History destination: {its agreed history/ or completed/ directory}
Index: {index.md inside that directory, or an existing adequate index}
Trigger: {settled thread, completed milestone, or another project-defined boundary}
Permitted writes: {current record, next numbered historical file, and index;
only locations already authorized by the project's capture procedure}

This is an optional procedure proposal. Establishing new record owners or changing
the layout needs the project's structural agreement first. Routine rollover can
then occur during capture within that agreement; restoration remains read-only.
A count can prompt review, but does not authorize a move or declare completion.

## Select what can move

1. Check actual results and the project's status definitions. Select a coherent
   settled thread or completed milestone; preserve meaningful scope and evidence.
2. Keep current blockers, unfinished work, live decisions, and the next action
   visible at their existing owners. When a historical thread has an unresolved
   consequence, carry its actionable summary forward with a link.
3. Keep decisions and detailed evidence at their existing owners. Session history
   preserves useful continuity; completed progress preserves outcomes and status.
   Link between them rather than copying the same narrative.

## Preserve and index

1. Choose the next unused zero-padded sequence within this collection and a clear
   kebab-case topic, such as 03-animation-work.md. Never overwrite an existing
   number. Session and completed-work sequences are independent; the prefix records
   archive order, not dependency, approval, version, or necessarily event chronology.
2. Prepare the historical record with its subject, coverage or date span, links to
   actual evidence and decisions, and any limits. Preserve facts without copying
   unnecessary personal details or a full conversation. Identify deliberate summaries
   rather than presenting them as verbatim evidence.
3. Add a real relative link in the collection's index.md, with a brief coverage
   label. Keep the index inside the folder it lists. Link to that index from the
   parent memory entry; do not maintain a duplicate listing outside the folder.
4. Only after checking the destination, remove the moved detail from the current
   record and retain a concise continuation summary or historical pointer. Update
   links affected by the move. Do not erase facts that still govern current work.
5. Verify preservation, current unresolved items, numbering, links, and the actual
   writes. Stop on unexpected concurrent changes or conflicting owners; preserve
   partial work and report it rather than deleting records to make the move fit.

## Reading and maintenance

Restore reads current records first. Read an index and selected historical record
only when the present job needs them; do not load every archive. Keep indices short,
with facts and rationale at the records they point to. Stable numbers need no
renumbering. Corrections follow project rules and do not silently rewrite historical
outcomes. Folder-specific contracts use CONTEXT.md only when distinct rules earn it;
a contents list alone belongs in index.md.

Handoff: {what moved, retained open work, index location, verified limits, and next
useful action; rollover itself supplies no acceptance or readiness claim}
