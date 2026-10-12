---
name: charter
description: Think through a build, feature, solution, or project structure with the human and produce a decision-ready plan with an explicit execution handoff, without implementation.
---

# Charter

One job: Turn a request into a reviewable plan, thinking it through with the human.

First read the project's entry instructions and relevant records. Find the owner
of this job and inspect the current files; check Git status when Git is available.
Read only what the task needs. Existing project rules and human authorization govern
scope. A skill invocation is not permission to overwrite files or invent approval.

## Follow the ask

The request decides which guidance to load. Read only the selected one.

| The human is asking to plan | Read | Result |
| --- | --- | --- |
| A build, feature, fix, or solution | [Build planning](build.md) and [build handoff](build-handoff.md) | Agreed language, decisions, assumptions, and a route to implementation. |
| Structure: where context, plans, memory, or responsibilities should live | [Structure guidance](guide.md), relevant section only, and [structure handoff](structure-handoff.md) | The smallest justified arrangement, one useful alternative, its tradeoff, and how to apply it. |

When the ask is unclear, infer from the request and say which path you took; ask
only if the two readings would produce different plans. A build plan can reveal a
missing boundary. Propose it from structure guidance then, without switching away
from the build. Read the structure handoff only for the resulting structural
steps, then return to the build handoff. Structure is never a prerequisite for
planning a build.

Throughout, keep proposed behavior, observed checks, and accepted work distinct.
Do not stop repeatedly for decisions the current agreement already covers. Resolve
unclear authority before consequential writes. A template does not authorize its
application.

Boundaries: Implementation, applying a structural mapping, accepting results, or launching other sessions.

## Make continuation part of the plan

Use only the selected handoff from the table above. Read selected downstream skill
contracts through the runtime's available catalog or project-declared paths before
assigning a step. Use actual installed names, including an explicitly chosen prefix.
Load only references relevant to that step, and resolve required inputs while
planning. Name the method, project authority, dependencies, permitted changes,
result home, checks, and stopping condition. Keep adequate existing structure.

If a selected skill is unavailable, disclose that its contract was not read and
use an explicit project procedure when one covers the operation. Otherwise name
the unresolved execution choice. The local handoff still supports planning; do
not claim an unavailable invocation or silently install a bundle.

Finish with the concrete next action, who carries it out, and what authorization
it needs. When the human authorizes execution, the same agent can leave Charter
and continue under the named methods. Follow existing authorization without
asking again; planning itself does not perform those steps.
At execution, recheck current inputs and destinations under the selected method.
Return to planning for a scope change, conflicting authority, or an unmet boundary.

## Conditional resources

Use the project's existing contracts and planning form first. When they cover the
job, do not load Galleon's alternatives.

| When | Read | Use it to |
| --- | --- | --- |
| An edit's consumers or failure patterns are unclear | [Change-impact guidance](change-impact.md) | Identify real consumers, failure patterns, and evidence limits before planning writes. |
| Session work needs a durable route, and existing rules do not supply it | [Memory guidance](memory-guide.md), relevant form or split section | Compare compact, linked, and separated forms and show the recommended procedure. |
| File reading cost is a relevant migration factor, and no project command suffices | [Optional estimator](token-count.md) | Measure explicit files without inferring a split or model-exact count. |
| A local plan form is missing or explicitly requested | [Plan form](_templates/plan.md) | Adapt a useful blank into the project's selected home or a chat draft. |

Do not read every example, all reference topics, or unrelated UI rules by default.
Read one relevant example when a concrete illustration helps the human choose.
The guides name the local examples and templates. Source citations are optional
background, not instructions to research ICM or install another skill.

## What this session is not

Keep the conversation bounded. Ask what matters, present the plan and execution
handoff, and resolve the project's required decision.
