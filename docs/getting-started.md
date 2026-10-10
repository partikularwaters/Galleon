# Getting started

The core is nine self-contained Markdown skills. No Python, acceptance database,
or hash manifest is required to use them. Their instructions guide the agent;
they do not intercept arbitrary edits or authenticate approval.

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

## Continue later

Ask Remember to save verified state at the project's existing owner, then begin a
fresh session with a plain resume request. Check what that session actually recovered.
Capture alone does not prove successful restoration.

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
