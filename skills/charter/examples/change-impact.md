# Change-impact illustration: date label formatter

This is a synthetic, filled explanation of how to label evidence. The example's
source paths are imaginary; no checks are claimed to have run in a real project.

Actual source in the scenario: `src/date-label.ts`, function `formatLabel`.

Live behavior in the scenario: the table reads this formatter for display labels.
Proposed behavior: add a short-month option. Do not describe it as implemented.

Affected consumers in the scenario: `src/date-table.ts` and the focused formatter
cases. A real proposal must inspect those call sites before treating this as fact.

Does not affect: unknown until the export serializer's call path is checked.
A separate serializer name is insufficient evidence of independence.

Known failures: link to an existing date/time incident if the project has one.
Do not invent an incident or duplicate its explanation here.

Verification basis: scenario assumptions only; no actual runtime verification.

Next check: inspect callers and exports, then agree on the change scope and tests.

Benefit: the human sees both the proposed change and uncertainty about its effects.
Cost: a persistent component card must be maintained. Keep these facts in the task
record unless repeated changes justify a dedicated owner.
