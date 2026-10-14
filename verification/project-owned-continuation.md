# Project-owned discovery and continuation

- Observation date: 2026-10-14, Asia/Manila.
- Report type: maintainer-operated, assistant-assisted observation.
- Scope: three completed CLI trials against disposable copies of one adapted project.
- Test condition: lighter models with no visible procedural-skills catalog.

Project names, personal paths, product-specific records, and transcripts are
omitted. The observations are real; the public descriptions are sanitized.

**All three setups supported plain-language entry, a bounded readiness review, and
fresh-session recovery of the review result without a visible procedural-skills
catalog.** All three also left a stale preparation-manifest reference in their
continuation records. Recovery succeeded despite that capture defect. Evidence
quality varied, so successful navigation did not establish reliable conclusions
or fully correct record maintenance.

This supports a limited part of Galleon's durability narrative: adopted project
records can carry useful procedures and state across sessions without installed
skills. It does not establish that the shipped skills reliably create those
records, that the project is fully mature, or that every agent will follow them.

## Contents

- [Question and project conditions](#question-and-project-conditions)
- [Runtimes, models, and isolation](#runtimes-models-and-isolation)
- [Task sequence and evaluation](#task-sequence-and-evaluation)
- [Expected behavior](#expected-behavior)
- [Evidence sources](#evidence-sources)
- [Observed results](#observed-results)
- [Observed gaps and attribution](#observed-gaps-and-attribution)
- [Evidence limits and supported conclusion](#evidence-limits-and-supported-conclusion)

## Question and project conditions

The question was whether fresh agents could find the project's authority, task
router, local procedures, current state, and next action from a plain request, then
perform authorized work and leave enough context for another fresh session.

The source was an existing application undergoing a documented migration. Its
records already contained root authority, context routers, review and capture
procedures, plans, historical evidence, and a continuation note. Preparation
manually replaced external skill invocations with project-owned procedure text.
This was an adapted project, not an unfamiliar operator building a project from
scratch with the distributed Galleon kit.

Each completed trial started from the same revised baseline: 667 project files
with matching bytes and modes, the same source HEAD, and preserved staged,
unstaged, and untracked work. The worktree was deliberately dirty. A project-owned
helper compared selected file identities and Git context; a matching manifest
did not mean the worktree was clean or that the application worked.

The environment was a local macOS 26.7 machine. Copies had no remotes, installed
application dependencies, environment files, or available external source
repositories. Live database records and external asset libraries were unavailable.
Historical application tests were preserved as records, not rerun by these trials.
The subjects were told that they were working in disposable copies.

Galleon's repository HEAD during this work was
`cf0d811720f71c31f07cf93768382627ad5f204e`, with uncommitted lifecycle documentation
changes. That identifies the development context, not a tested release or a
bootstrap artifact. The subjects operated on the adapted project's own records.

## Runtimes, models, and isolation

The selection of lighter models was intentional. We chose Luna, Haiku, and Flash
to observe whether project-owned routing could support useful discovery and
continuation with these configurations. All three found the relevant procedures
and recovered the current work. In these tested conditions, smart discovery was
therefore demonstrated with lighter models. The trials do not establish parity
with heavier models or compare their reliability.

Model labels below identify the requested configurations. Launch arguments, user
reports, and generated attribution supplied model evidence; no provider-side
attestation of the actual serving model was collected. Runtime versions are
included where retained. These are different runtime/model combinations, not a
controlled model comparison.

### OpenAI Codex CLI: Luna

- Requested model: `gpt-6-luna`.
- Runtime: locally installed Codex CLI. Its exact version was not retained in the
  completed trial evidence.
- Skill control: invocation-only disable entries naming individual `SKILL.md`
  files. A local runtime probe reported zero enabled skills; the successful
  startup response reported no available-skills catalog.
- Memory control: runtime settings disabled memory use and generation. The
  successful startup reported no automatic-memory content.
- Remaining context: global working instructions and the project's `AGENTS.md`.
  A standing reference to a commit skill remained, but no skill invocation was
  observed in the task traces.
- Setup interventions: earlier startup checks exposed a catalog, including newly
  installed plugin skills. The disable list was updated and a fresh session was
  checked before beginning the counted task run. Those checks were setup attempts,
  not additional completed trials.

### Claude Code CLI: Haiku 5.5

- Requested model: `claude-haiku-5-5`.
- Recorded runtime version: Claude Code 2.1.270.
- Skill control: `--disable-slash-commands`; the startup response reported no
  available-skills catalog.
- Memory control: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and
  `autoMemoryEnabled=false`. The startup reported no automatic-memory content.
- Other invocation controls: project/local settings only, hooks disabled, an
  empty explicit MCP configuration, and Chrome integration disabled.
- Remaining context: native system instructions, standing attribution rules, and
  the project's `CLAUDE.md`, which imported `AGENTS.md`. Native deferred tools and
  agent types remained available; those were not an external skills catalog.
- Setup intervention: the operator restarted with direct CLI commands after an
  initial launch did not establish the intended model selection.

### Antigravity CLI: Gemini 3.8 Flash Medium

- Requested model: `gemini-3.8-flash-medium`.
- Recorded runtime version: Antigravity CLI 1.3.5.
- Skill control: the operator authorized temporary renaming of both the global
  and built-in skill directories. The CLI's read-only skill inventory then
  returned an empty list, with zero model turns and zero tokens used by that
  inventory check. The fresh startup also reported no catalog.
- Memory and prior context: the startup reported no automatic-memory content or
  prior-project conversation facts. A separate memory-disable switch was not
  established, so this is a context observation rather than a verified global
  memory configuration.
- Remaining context: global working instructions, project `AGENTS.md`, and native
  slash commands and subagent definitions. A standing commit-skill reference
  remained, but no procedural skill reads appeared in the supplied task traces.
- Setup intervention: a High configuration was used for startup inspection only.
  It exposed 13 skills and was excluded from the completed task results. Medium
  started in a separate pristine copy after skill isolation.

The directory renames affected new Antigravity sessions globally, rather than
only this test. They were restored after the final observation, with saved file
fingerprints checked. This was a disclosed operator intervention, not a portable
isolation feature or a recommended installation procedure.

## Task sequence and evaluation

### Expected behavior

The criteria were concrete behaviors under the project-owned agreements:

1. Discover the local authority, router, and relevant procedure from the plain
   request and native project entry, without operator routing hints or procedural
   skill reads.
2. Restore the objective, current file and Git state, open decisions, missing
   inputs, and next action, distinguishing recorded history from fresh checks.
3. Perform the readiness review within the four-record write boundary and
   preserve unrelated work.
4. Separate settled decisions, proposals, current observations, historical
   results, and unavailable evidence; support findings with scoped identities and
   resolving evidence links.
5. Capture the actual result and executable next action, with a current identity
   that clearly supersedes earlier preparation state.
6. In a separate fresh session, detect relevant drift, recover the latest result
   and its limits, and preserve the read-only boundary without corrective hints.

Each counted run followed the same sequence:

1. Check startup context without tools or file reads.
2. Send the plain resume request below, keeping the first step read-only.
3. In that session, request a bounded readiness review of a proposal before schema
   and UI implementation. Require separation of settled decisions, proposals,
   current facts, historical results, and missing evidence.
4. Permit only four output records: a new review report, its evidence manifest,
   the verification index, and the continuation note. Prohibit application,
   schema, product-contract, acceptance, dependency, and external-system changes.
5. Preserve the first review result, then start a separate fresh session in the
   same post-review copy and repeat the plain resume request without corrective
   feedback or a hint about which manifest to use.

The resume request was:

> Resume this project. Keep this first step read-only. Report the current objective,
> verified state, unresolved issues, and next action.

The review request was more detailed. It supplied the job, reporting requirements,
write boundary, and exclusions, while leaving discovery of the governing owners
and procedures to the project. The experiment therefore tested plain-language
operation with explicit scope, not unlimited autonomous work from a vague request.

The evaluator checked actual output files against the baseline, reviewed claims
against local source records, checked manifests and links, and preserved output
snapshots before fresh restoration. Evaluator notes, prior errors, and operator
preparation records stayed outside the subject's authorized reading set.

### Evidence sources

- **Supplied reports and action traces:** the operator provided startup responses,
  task traces, and final responses. These support observations about routing,
  reads, reported context, model attribution, and recovered state. Compressed or
  omitted command output limits what can be inferred from a trace alone.
- **Direct evaluator inspection:** the evaluator read the actual project records
  and outputs, compared file bytes and modes against preparation and post-review
  snapshots, checked selected manifests and links, and compared claims with local
  source evidence. File counts, write boundaries, hash matches, and unchanged
  post-review files come from these checks, rather than agent summaries alone.
- **Prepared baseline and historical records:** disposable copies supplied the
  shared starting conditions. Earlier application-test results and external
  specifications were historical inputs; their presence did not establish fresh
  execution or current external behavior.
- **Unavailable evidence:** live database rows, external assets, provider-side
  serving-model verification, and a complete runtime activity audit were not
  available. No successful check is inferred for those boundaries.

## Observed results

### Shared successes

All three counted runs found the root router and relevant local procedures,
recovered the current objective and missing inputs, and reached the supported
readiness verdict: the proposal was **not ready for schema or UI implementation**.
That verdict was a correct outcome for the available evidence, not a failed task.

Each review changed only the four authorized records. Filesystem comparisons
confirmed preservation of unrelated project files. Each produced a supporting
manifest that matched its selected boundary, and the checked local link targets
resolved. Manifest scopes differed, so these checks were not equivalent coverage
of all current records.

Each separate fresh session detected that the preparation manifest no longer
matched the changed continuation and index, followed the newer review evidence,
and recovered the latest readiness finding. Independent comparisons found all
669 post-review project files unchanged after each read-only restoration. No
application implementation or phase acceptance was observed.

### Codex Luna observations

The review distinguished the limited owner-confirmed choices from detailed
unaccepted policy proposals. It used local source behavior and historical external
specifications to narrow the unresolved questions, while treating historical
application checks as historical. Its 23-file review manifest included the report,
index, and continuation; 36 checked local file links resolved.

Capture still left the preparation manifest labeled as the current identity at
the top of the continuation. The fresh session recovered the newer review despite
that stale reference. This demonstrates recovery, but not correct reconciliation
of superseded state.

### Claude Haiku observations

The review inspected relevant source rules and migration history, identified a
live-data gap, and separated missing external inputs from local inspection. Its
14-file manifest covered reviewed inputs but excluded the new output records;
31 checked local links resolved.

Several claims needed correction. The report incorrectly attributed authorship of
the earlier proposal to the same session. It overstated what could not be checked
without external source code, although archived specifications supported some of
those historical claims. It also suggested that one external export would resolve
an unrelated missing-source issue. A reported Git-context result differed from
the evaluator's check, although the selected file hashes matched.

The fresh session recovered the review and identified the stale preparation
manifest. Its use of file modification times to explain the changes was weaker
evidence than explicit content provenance, and its input-only review manifest did
not establish the changed continuation and index identities.

### Antigravity Gemini observations

The review found the relevant owners, reached the supported stopping verdict, and
kept its writes scoped. Its 12-file manifest covered reviewed inputs and the report;
all 11 hashes printed in the report matched, and 31 checked local links resolved.

The report presented historical type-check, lint, and unit-test passes as current
application verification without rerunning them. It also classified some proposed
policies as settled, blurred synthetic planning fixtures with representative real
records, and omitted replayable check commands and output evidence from the durable
report even though its final response described checks.

Fresh restoration detected the stale preparation identity and recovered the new
review. It described application checks as recorded results in that response, but
called a selected 12-file manifest match an exact working-tree match. It also
carried forward the saved fixture ambiguity. Successful restoration can preserve
an erroneous recommendation as well as a sound one.

## Observed gaps and attribution

The repeated stale-manifest capture is an observed gap worth investigating. The
local contract already required current identity checks, but did not specify an
exact operation for reconciling a broad preparation inventory with a later scoped
review manifest. That leaves a possible contract-clarity issue alongside incomplete
execution. These runs do not determine how much either contributed.

Historical/current evidence confusion occurred despite explicit local instructions
to keep those categories separate. It cannot be attributed simply to an absent
router or missing review contract. Underlying causes remain unresolved. One run
per runtime/model combination cannot establish failure rates or comparative model
capability. No controlled latency, cost, or throughput benchmark was run.

## Evidence limits and supported conclusion

The private evidence includes operator-supplied action traces, preparation
inventories, output snapshots, and evaluator comparisons. Some traces compress
commands or omit outputs. Session IDs and serving-model verification were not
uniformly retained. Startup self-reports support the stated context conditions but
are not a complete audit of runtime memory, account activity, or tool access.
Public readers cannot reproduce the original private case from this summary alone.

This was one deliberately prepared project on one operating system, with explicit
scope and unavailable live inputs. It did not exercise application execution,
deployment, production data access, arbitrary interruption, or a deliberately
planted product-file change. There was no full end-to-end observation of the
shipped skills taking an immature project through all three lifecycle phases.

The supported result is useful but narrow: **project-owned records enabled three
tested CLI setups to navigate, perform a bounded review, and recover the latest
work without a visible external skills catalog.** Those records did not enforce
evidence discipline or guarantee correct capture. Galleon's skills can help build
the ship, but the durability of the resulting project still depends on the quality
of its contracts, records, agent execution, and human review.

The next useful experiment is to clarify superseded current identities in a
separate baseline variant, then observe fresh capture and restoration without
coaching. A distinct bootstrap trial should test an unfamiliar operator using the
distributed skills before handing the adopted project to an agent without them.

See the [verification guide](../docs/verification.md) and
[observation form](../docs/independent-verification.md) for the broader release
limits and a way to report another scoped trial.
