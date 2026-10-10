# Compact job

Use this when one bounded task has few inputs and one person directs it. A task
record may hold the agreement, result, and next action in separate sections.

```text
project/
  AGENTS.md
  tasks/
    fix-date-label.md
  src/
```

For example, `fix-date-label.md` says: "Correct the displayed date label. Change
only the formatter and its focused test. Preserve timezone behavior. Check the
known date examples. Next: review the formatter diff."

Benefit: the work is understandable with very little navigation.
Cost: a long-running record may become crowded as unrelated jobs accumulate.
Use a smaller form when a read-only answer needs no durable handoff. Separate
records only when repeated work or distinct owners make that useful.
