# Contributing to Galleon

Help make Galleon useful to someone who did not help build it. Contributions can
include independent verification, reproducible bug reports, clearer instructions,
practical examples, and focused improvements to the skills or installation process.

Galleon helps projects define their own working agreements and preserve useful
context. Contributions should make that easier without imposing a universal folder
structure or adding unnecessary approval steps.

Read the [README](README.md) for the purpose and [repository context](CONTEXT.md)
for the relevant records.

## Contents

- [Priority: independent verification](#priority-independent-verification)
- [Bug reports and evidence](#bug-reports-and-evidence)
- [Documentation, templates, and skill changes](#documentation-templates-and-skill-changes)
- [Pull requests](#pull-requests)
- [Commit messages and AI assistance](#commit-messages-and-ai-assistance)

## Priority: independent verification

The most useful contribution now is an unfamiliar reader trying the instructions
on a small real job. Earlier engineering results inform this edition, but they do
not establish that its rewritten skills are easy to install and use independently.
This unversioned edition still needs that observation before a v1 decision.

Use a disposable project and identify the exact Git commit you tested. You do not
need to run a large audit or publish a full conversation. A compact account of what
worked, what failed, and what required help is enough to start.

| Try | Tell us |
| --- | --- |
| Install and discover the skills | Did the guide make sense? Were the intended skills and linked resources available? Did existing names cause a collision? |
| Plan one bounded job | Did the agent find existing rules, or explain a missing boundary with a useful example? Did it avoid unnecessary structure? |
| Save and resume work | Could a fresh session recover the current job and next action from project records? Disclose prior context, outside memory, and coaching. |
| Check a skill's boundary | Did it preserve unrelated work and stay within its stated role? For example, did Survey report a defect without silently repairing it? |
| Try another runtime or platform | Which environment and actions actually worked? Report failures and limits rather than generalizing to every agent. |

Choose the checks relevant to your trial; you do not need to perform every row.
Follow [getting started](docs/getting-started.md), then use the
[compact verification record](docs/independent-verification.md). An agent can help run checks and draft
the report, but the unfamiliar reader's experience must be their own. Maintainers
review the evidence and determine the supported scope; a favorable report does not
supply universal compatibility or automatically establish release readiness.

## Bug reports and evidence

Submit an issue or pull request with the commit, environment, actual steps,
expected behavior, observed behavior, and any intervention. Name the specific skill,
instruction, or promise involved. Include short relevant output when it explains
the problem, and say which checks you did not perform.

Keep failed attempts distinguishable from successful retries. Use synthetic or
redacted examples instead of private project content. Exclude credentials, personal
paths, approval conversations, and full chat exports. Do not plant mistakes in an
original project or alter a live installation merely to demonstrate a failure.

## Documentation, templates, and skill changes

The [resource catalog](docs/resources.md) identifies the owning skill for each form
and guide. Propose changes at that owner; keep installed resource links local.

Use the [contents-list guidance](skills/charter/guide.md#contents-lists) when sections
need independent selection. Keep that guidance at its owner.

Use plain language, small examples, and explained benefits. An illustrative layout
is an option, not a mandatory skeleton. Templates should help a project adapt its
own agreement, and their resources must remain accessible when a skill is copied
independently. Preserve the distinction between proposals, observations, and actual
authorization.

For a documentation change, check affected links and examples. For a skill change,
exercise the relevant behavior in a disposable project and disclose what remains
unverified. Discuss changes to a skill's role, naming, or preservation guarantees
before broad implementation. Any executable installer or recovery tooling added
later needs focused normal, failure, and recovery checks.

## Pull requests

Describe the problem, resulting behavior, scope, and meaningful validation. Link a
relevant issue when one exists. Keep unrelated cleanup separate from behavioral
fixes, and preserve user-owned work and previous evidence. Maintainers own
integration and release decisions.

Preserve the MIT license and original notices. Identify sources and licenses for
reused material. [ICM](https://arxiv.org/html/2603.16021v2) is Galleon's conceptual
precedent; do not present Galleon's adaptations as requirements imposed by ICM.

## Commit messages and AI assistance

Use a brief conventional subject such as `fix: preserve existing skill names` or
`docs: clarify project-owned contracts`. Add a short body when it explains a material
reason or compatibility detail. Describe the project change, not the assistant's
activity or the conversation that produced it.

Keep the configured human Git identity as author. When AI materially shapes code,
documentation, architecture, or analysis embodied in a commit, append:

```text
Assisted-by: <product> (<model, if known>)
```

For example:

```text
Assisted-by: OpenAI Codex (GPT-6.1)
Assisted-by: Meta Muse (Muse Spark 1.3)
```

Name only actual contributing products and models. If the model is unknown, name
the product only. Repeat the trailer for multiple material contributors. Do not
invent an AI email address or use `Co-authored-by` without an explicit owner request
and a verifiable identity.
