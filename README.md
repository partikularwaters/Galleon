# Galleon

**Your project should explain itself.**

To the human directing it. To the coding agent working in it. To whoever picks it up next.

Galleon helps a project propose its own working contracts and organize them into a readable file architecture. Purpose, context, decisions, boundaries, and current work become part of the project, available beyond the conversation that created them.

[Start using Galleon →](#start-using-galleon)

## The problem: every new session starts behind

Coding agents such as Codex, Claude Code, and Antigravity can help people work on a project. But the project can still lose its working understanding between sessions.

When decisions remain in chat histories and important instructions live in someone's memory, a new agent must reconstruct what matters, what is settled, and what it may change. As a result, the human becomes the recurring source of context.

Installing another capability or product, such as a testing skill, a plugin, or an agentic framework, can help with a task. But the project still needs a coherent account of its purpose, decisions, and working process. Without that account, each new session spends effort rebuilding understanding that should already belong to the project.

## Let the project own its operating model

Galleon guides a project toward its own contracts: where context belongs, who owns a decision, what a job may change, what counts as evidence, and how work continues.

Those contracts live alongside the work, in meaningful folders and readable files.

**The project's file architecture is the agentic framework.**

A folder gives a responsibility a home, while its contract explains the work that belongs there. Routes connect those homes, and plans, results, and state records make decisions and handoffs visible. Together, they give the project a working architecture that both readers can inspect.

```text
Human:        find the work → inspect/edit its artifacts → decide what proceeds
                                   │
                          Project-owned records
                                   │
Coding agent: find the owner → read its contract/context → perform bounded work
```

Galleon's conceptual foundation is [Interpretable Context Methodology (ICM)](https://arxiv.org/html/2603.16021v2), by Jake Van Clief and David McDermott: filesystem structure, local contracts, and readable handoffs can organize sequential, human-reviewed agent work.

The structure grows from the project's actual needs. A small job may need only a plan and a state record. An existing project may already have useful context owners. Repeated handoffs may justify a pipeline. Galleon helps discover the smallest arrangement that works and preserve what already does.

## How it works

Start with a real job. Find its inputs and existing owners. Propose any missing boundaries. Review them. Perform the work. Preserve the result and the next action.

```text
Find the job and existing rules
  → explain missing boundaries with a small example
  → agree on the work and checks
  → perform authorized work
  → review the result
  → preserve the next useful starting point
```

For a small, read-only job, your instruction may already provide enough direction.
When the work expands or crosses an unclear boundary, Galleon explains the gap,
shows a short template, and asks for the decision that matters. It does not require
an approval ceremony at every step. Your project's existing requirements still apply.


The files make this process inspectable. For a read-only snapshot checker, the plan names its input format, files it may create, no-write behavior, and tests. The human can review those boundaries before implementation. Code and evidence then provide a concrete result to assess; recorded decisions and state tell the next session where to continue.

An illustrative small project could look like this:

```text
project/
  AGENTS.md             constraints and working agreement
  CONTEXT.md            routes to the relevant owners
  work/
    plan.md             current job, scope, and checks
    CONTEXT.md          inputs, outputs, and permitted writes
    result.md           result and evidence
  memory/
    CONTEXT.md          capture/resume procedure and record owners
    state.md            decisions, current state, and next action
  src/                  native application code
  tests/                native tests
```

These names are examples. Existing homes can remain authoritative; useful routing does not require competing copies or a universal skeleton.

### Nine skills, bounded methods

Galleon provides nine skills. Each implements a bounded method for working with the project's context. The project's declared contracts define the applicable inputs, owners, allowed changes, outputs, and checks. Installing a skill does not authorize a change; a missing boundary calls for a proposal or a stop.

| Skill | Method and boundary |
| --- | --- |
| `charter` | Propose a job or missing working contract; produce a decision-ready plan, without implementation. |
| `scaffold` | Establish accepted missing structure through declared creations, without overwrite. |
| `import` | Apply an accepted existing-context mapping while preserving content, ownership, and references. |
| `delegate` | Turn an accepted larger plan into written work items; no model selection or chat dispatch. |
| `survey` | Evaluate a named result against its plan; report evidence without repair or acceptance. |
| `remember` | Capture verified state at existing owners; no restoration or restructuring. |
| `sync` | Correct navigation from authoritative facts; no new rules or owners. |
| `audit` | Test whether a context harness supports its promised job; findings and scoped evidence, without live repair. |
| `diagnose` | Explain an observed failure and propose a bounded response; no repair or reset. |

Use the methods the job needs. They are not a mandatory nine-stage pipeline. Passing checks supplies evidence; human acceptance remains a separate decision. Capture records verified state; restoration follows the project's own procedure.

## A plain request or a skill invocation

Once the project explains its working process, a person can ask for work in ordinary language or invoke a relevant skill. Either path should lead to the project's records and applicable contracts.

```text
“Continue this project.” ───┐
                           ├─→ project records and contracts
“Use charter to plan…” ─────┘        → scoped work and review
```

A testing skill can help an agent write test cases, while a plugin might give it access to an issue tracker. But the project's purpose and working agreement need a durable home as those capabilities change. Galleon helps establish that home in the project's own records.

With a skill invocation, the agent brings a reusable method to the job. With an ordinary request, it can follow the project's own instructions without the person remembering every external skill's name. Either way, the project supplies the applicable context and boundaries.

Both paths draw on the same visible authority. The human can inspect and revise it. A capable coding agent can navigate it. That shared operating model gives each new session a starting point it can verify.

## Built to outlast the current tool

As models, runtime products, and agentic frameworks change, a project with readable contracts, clear ownership, and recorded state gives new tools something coherent to inherit.

The folders and files remain the project's authoritative record of its work. They can be maintained, reviewed, and carried into another tool. The operating model stays available for humans and agents to understand and adapt.

That is the durability Galleon works toward: a project that can carry its understanding forward, with less dependence on any one conversation or product. It still needs human judgment and maintenance, so its structure must make that work visible.

**Let tools evolve. Keep the project intelligible.**


## Start using Galleon

This is an unversioned early-development edition, not a v1 release. The core skills
are Markdown files; they do not require Python or the previous guarded workflow engine.

Clone or download this repository. Then ask your coding agent:

```text
Read docs/getting-started.md. Preview installing Galleon's nine skills in this
project's supported skill directory. Stop on existing names, do not replace them,
and offer the gal- prefix if needed. After installation, show what was installed
and how to start a fresh session that can discover it.
```

The [getting-started guide](docs/getting-started.md) explains installation,
plain names and the explicit `gal-` fallback, and a first task. Agent-assisted
installation still needs your review of the proposed destination and any permissions.

Browse the [forms and guidance](docs/resources.md) when your project needs a
starting point. Existing project agreements remain authoritative; the templates
are optional resources, not a required file tree.

## Help strengthen Galleon

Try one small job, report what happened, or improve a guide or template.
[CONTRIBUTING.md](CONTRIBUTING.md) explains how to help, including independent verification.

The [verification summary](docs/verification.md) separates earlier engineering evidence
from this edition's pending independent trial. [Selected, sanitized results](verification/samples.md)
report observed checks and their limits without publishing working histories or personal paths.

Original work is [MIT licensed](LICENSE). ICM is the conceptual precedent, not a claim
of universal runtime compatibility. No version tag or release archive has been published
for this edition.
