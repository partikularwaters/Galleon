# Getting started

The core is nine self-contained Markdown skills. They teach a project how to
discover, structure, and explain itself to coding agents.

Galleon guides [three phases of project maturity](../README.md#how-a-project-matures):
discovery and scaffolding, project-owned self-explanation, and durable operation
with the skills stepping back. Before the project owns adequate procedures, the
relevant skills supply guidance it still needs. Particular templates remain
optional because existing agreements may already cover the job.

Start from a real need, such as a workflow you repeatedly explain in sessions.
Ask: “Should there be a contract here?” Charter helps plan the missing boundary
and routes the agreed work to the relevant methods. As rules, routes, contracts,
and continuation procedures become project-owned records, ordinary requests can
follow them. The aim is for those records to support routine work even in a fresh
environment without Galleon skills installed. Check that behavior for the work and
environment you rely on; adopting files alone does not demonstrate it.

## Install in one project first

1. Obtain this repository and read its README.
2. Identify your coding agent's supported skill directory for that project. Common
   locations include `.agents/skills/` and `.claude/skills/`, but verify your runtime's
   current support. A directory name alone does not establish compatibility.
3. Preview copying each complete directory from `skills/` into that destination.
   Check all nine destination names first, including case-insensitive collisions.
   If any target exists, stop before copying anything. Do not overwrite unrelated skills.
4. After the preview is approved, copy the directories with their local resources.
   Preserve source files and stop on an error; report any partial copy before retrying.
5. Open a fresh session rooted at the project. Ask it to list the discovered Galleon
   skills and load Charter's linked guide. Missing entries or resources need diagnosis,
   not a claim of successful installation.

You can ask an agent to perform these steps with local file access. This is currently
an agent-assisted or manual installation, not a tested one-command installer.
Generic unattended skill installers may overwrite collisions, so this guide does
not recommend using one without checking its behavior.

## Names and fallback

Default names: `charter`, `scaffold`, `import`, `delegate`, `survey`, `remember`,
`sync`, `audit`, and `diagnose`.

If those names collide, offer an explicit `gal-` installation. With the user's
choice, copy to names such as `gal-charter` and change each copied SKILL.md frontmatter
`name` to match. Keep the remainder of the skill and its relative resource paths
unchanged. Preview every prefixed destination too. Do not switch names silently.
The new edition has no automated installer yet; this fallback is a documented manual
or agent-assisted procedure, not a verified new installer feature.

## First useful job

Ask: "Use charter to plan one small job. Find this project's existing rules first.
If something important is missing, show me a short contract example and its benefit."

Review the proposed scope and checks. For low-impact work, an explicit instruction
may suffice. For structural changes, agree on targets, preservation, and recovery
before writing. Existing project approval rules govern every choice.

Charter's plan should include an execution handoff: the responsible methods,
prepared inputs, allowed changes, checks, and first next action. For example,
Scaffold creates agreed missing files, Import applies an existing-context mapping,
and Sync corrects navigation from established facts. Charter reads the relevant
available contracts while planning and discloses any unavailable method.

When you authorize execution, the same agent can continue under the selected
handoff. For example: "Approved, proceed with the handoff." The
[build handoff](../skills/charter/build-handoff.md) follows your project's development
workflow for application code. The [structure handoff](../skills/charter/structure-handoff.md)
assigns exact file-tree and context operations to the relevant Galleon methods.
A build reads structural guidance only when it needs that work; the job does not
require every Galleon skill.

## Continue later

Ask Remember to save verified state at the project's existing owner, then begin a
fresh session with a plain resume request. Check what that session actually recovered.
Capture alone does not prove successful restoration.

To assess independence from Galleon, use an agreed disposable copy and a fresh
session without Galleon skills or prior conversation context. Ask it to continue
from the project entry. Observe whether it finds the relevant rules, contract,
current state, and authorized next action without coaching. When appropriate,
authorize one bounded task under those records and observe the result. Record
available skills, interventions, and limits in the
[verification record](independent-verification.md). This is a scoped observation,
not a required ceremony after every save or proof of universal agent support.

When a single state file mixes unrelated readers, consider splitting records:
- **Active implementation versus review**: An engineer or agent doing daily work
  needs immediate continuation context (`memory/session.md`), while a reviewer or
  release manager only needs settled architectural choices (`memory/decisions.md`)
  and verification proof (`evidence.md`).
- **Accumulating history**: In projects running sequential jobs, moving completed
  records into an append-only collection keeps active session notes compact and fast
  for fresh agents to read.

## Optional verification helpers

When Python 3 is available, projects can run Galleon's deterministic read-only
helpers directly without installing external packages:

- **Check Markdown local links**:
  `python3 skills/sync/scripts/check_links.py --root . <files>`
- **Preview sibling name collisions**:
  `python3 skills/scaffold/scripts/check_collisions.py <target-dir> <proposed-names>`
- **Capture or compare file SHA-256 inventories**:
  `python3 skills/audit/scripts/file_inventory.py compare <manifest.json> <files>`
- **Estimate file reading cost**:
  `python3 skills/charter/scripts/count_tokens.py <files>`

If Python 3 is unavailable, agents perform equivalent checks using standard shell
commands (`ls`, `grep`, `shasum`) or direct file inspection.

## Removal

Remove only the copied Galleon directories whose identity you have checked. If they
contain subsequent edits, preserve them before removal. Do not delete a shared skill
directory or unrelated registrations.

## Forms when you need them

The [resource catalog](resources.md) shows available guides, blanks, and filled
examples. Skills use existing project contracts and forms first. When those cover
the task, they skip alternative templates. For a missing boundary, the relevant
skill shows a concrete proposal and tradeoff before structural application.
Adapted records belong to your project and should remain intelligible without
Galleon. You do not need to research ICM or install ICM Architect to use these forms.
