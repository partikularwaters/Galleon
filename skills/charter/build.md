# Plan a build, feature, or solution

Think alongside the human the way a senior engineer would before anyone writes code.
This is a thinking session, not an interrogation: ask what changes the result,
confirm the plan, then get out of the way.

## 1. Take stock

Read the request, the project's relevant records, and any existing code in the area.
If the project keeps a scope or roadmap record, note where this work fits. Build a
clear picture of what must be built and what already exists. Do not ask about
anything the project's records already answer.

## 2. Align on language

Find the few terms in the request that could reasonably mean more than one thing.
State what you understand each to mean and ask for confirmation:

- **"Archive"**: I understand this as hiding a record from default lists while keeping it restorable. Is that right?

Skip this step when the terms are clear. If the human corrects a term, update your
understanding before continuing.

## 3. Think through the decisions together

Before raising decisions, apply only the perspectives this job calls for. They are
temporary lenses, not extra stages or separate reviews:

| Perspective | When | Ask |
| --- | --- | --- |
| Outcome owner | Always | Is this the right problem and the most direct route? Does the request combine unrelated work? If scope is questionable, recommend holding, reducing, expanding, or splitting it, and wait for agreement. |
| Roadmap fit | The project has a roadmap or scope record | Does this belong to a named phase? If not, offer a deliberate exception, deferral, or roadmap amendment. An unplanned fix may stay unplanned. |
| User | Someone completes a recurring workflow | What must they accomplish end to end? Where could friction or a silent failure appear? |
| Builder | Architecture, data flow, or a technical boundary changes | What must be decided now so implementation does not invent the design later? |
| Maintainer | The result is durable or cross-cutting | What would a future session need made explicit to change it safely? |
| Risk owner | The work is sensitive, irreversible, production-facing, or externally dependent | What unacceptable failure is possible, and what prevents, recovers from, or explicitly accepts it? |

Translate what a perspective exposes into decisions, assumptions, checks, or scope.
A perspective never authorizes silent scope expansion.

Raise only decisions that would meaningfully change what gets built, in order of
impact, one at a time:

> **Decision:** Should archived records still appear in search?
>
> **My thinking:** No by default, with an "include archived" filter. Search results
> stay relevant, and nothing becomes unreachable.
>
> Does that work for you, or do you see it differently?

When an answer makes a later decision irrelevant, skip it. When an edit's consumers
or failure patterns are unclear, consult [change-impact guidance](change-impact.md)
before deciding scope. When planning reveals a missing working boundary, such as an
unowned decision, no place for the plan, or no agreed checks, propose it using
[structure guidance](guide.md), relevant section only.

## 4. Know when you are done

Stop when every decision that would change the implementation is resolved, not
when every possible question is answered. Use the input coverage test rather than
intuition: list every value the build must produce, compute, or display. For each,
does the plan name its source, whether a stated input, an agreed decision, or a
named default? A required value without a source is an open decision. Raise it
before declaring the plan ready.

## 5. Present the plan

Use the project's planning form when one exists. Otherwise adapt the
[plan form](_templates/plan.md), keeping only the fields that add value. Explain any
new concept in plain language before relying on it. Check the plan against the
project's standing rules and name any conflict instead of quietly working around it.

Use [build handoff guidance](build-handoff.md) to name the development workflow or
implementation skill, permitted code changes, tests, and first eligible step.
Resolve its required inputs before calling the plan ready. Read structure handoff
guidance only when the build needs structural operations, and keep those dependencies
distinct from implementation. Name how the executor continues after authorization.

Present the plan and wait for the project's required confirmation. Save it only at
an agreed home; otherwise leave it in conversation. When execution is authorized,
Charter ends and the named execution method begins.
