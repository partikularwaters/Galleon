# Work item: correct the displayed date label

Parent plan: the project's agreed formatter-fix task record.

Purpose: display the agreed date label without changing timezone behavior.

Ready when: the expected examples are confirmed in the task record.

Inputs: that record, `src/date-label.ts`, and `tests/date-label.test.ts`.

Allowed changes: those two source and test files only. Preserve configuration,
timezone conversion, and unrelated formatting.

Checks: run the project's focused date-label test command; require the recorded
examples and existing timezone cases to pass. If no such command exists, report
that gap rather than inventing a successful test run.

Stop when: examples conflict, another file needs changing, or a check fails.

Result home and handoff: append actual changes, check outcomes, and the next
review action to the existing task record.

This is a complete illustrative handoff. The named paths are synthetic, and this
example does not claim that its dependencies exist in a real project.
