# Optional sibling-name preview

Before creating `memory/` or registering a skill named `charter`, check whether that
name is already occupied. A similarly spelled name may also collide on a different
filesystem. This helper previews those facts without creating or replacing anything.

Use an adequate project command first. Otherwise, this optional Python 3.9+
standard-library script, with a Node.js fallback, is available beside Scaffold. It reads one selected parent
and explicit proposed names. It does not inspect ownership records, adopt existing
files, choose a prefix, install skills, initialize Git, or grant permission to write.
Core Galleon skills do not require it.

## Without Python

`scripts/check_collisions.mjs` (Node.js 22+) takes the same arguments, returns the same
exit codes, and prints the same report as the Python script under Python 3.14. Prefer
Python, then Node.js; install nothing just to run a preview. For example,
`node skills/scaffold/scripts/check_collisions.mjs --parent .agents/skills --json charter scaffold`.
Case folding is reproduced from Python's, not independently specified, and each runtime
uses its own Unicode data. Python 3.14 uses Unicode 16, while Node.js 22.23.3 uses
Unicode 17, so a character assigned after Unicode 16 may compare differently. Node.js
cannot see the original bytes of an argument that is not valid UTF-8, so it stops with
status 2 for any argument containing U+FFFD. If no runtime exists, list the parent with
the agent's own file tools and compare names by eye, saying that the check was manual
and did not apply the folding policy. PowerShell versions are planned but not yet available.

## Select a parent and names

From the source repository, for example:

```sh
python3 skills/scaffold/scripts/check_collisions.py --parent .agents/skills --json charter scaffold
```

Use the script's actual installed location after installation. The parent can be an
absolute path or a path relative to the current directory. Use a canonical location
without `..`, symlink, or reparse ancestry. If a platform alias points somewhere
else, choose its canonical destination explicitly. A non-directory ancestor or an
inaccessible listing makes the check incomplete.

Proposed names are simple siblings, such as `work-contract.md` or `memory`. Nested
paths like `memory/state.md` are not accepted by this preview. The project determines
which names to propose and whether their creation is authorized; the script does
not infer Galleon's nine names or any required project structure.

An absent parent is reported as absent when its existing ancestry is safe. The
helper does not create it. This is useful for a proposed new collection, but it
does not establish that its location or contents have been agreed.

## Interpret the report

A shortened illustrative report for an existing conflicting name:

```json
{
  "method": "sibling-name-preview-v1",
  "complete": true,
  "parent_exists": true,
  "proposed_count": 1,
  "siblings_checked": 3,
  "occupied": [
    {"name": "charter", "existing": "Charter", "kind": "equivalent"}
  ],
  "duplicates": [],
  "invalid": [],
  "errors": []
}
```

`occupied` identifies exact matches and potential equivalent spellings. Any existing
file, directory, or link is occupied, including a dangling link. Similar contents
do not authorize adoption. `duplicates` identifies repeated or equivalent proposed
names even when the parent is absent. `invalid` lists names rejected by the portable
policy; `errors` describes an incomplete inspection.

The report omits the selected machine path and does not publish the whole sibling
listing. Names in findings may still be sensitive, so review them before sharing.
JSON escapes Unicode for reliable transport; parsing restores the original names.

| Exit | Meaning | Agent response |
| --- | --- | --- |
| 0 | Inspection completed without collisions | Report the bounded preview; recheck before actual authorized creation. |
| 1 | Existing or duplicate proposed names conflict | Explain the findings and let the project's rules determine the response. Do not overwrite or select a fallback automatically. |
| 2 | Invalid names or incomplete inspection | Report the limitation and use an appropriate narrower check or project command. Do not treat it as clear. |

## Portable comparison policy

The helper compares Unicode NFC-normalized names after case folding. For example,
`Charter` and `charter` are potential equivalents, as are composed and decomposed
spellings of `café`. This conservative policy helps spot portability problems;
it does not emulate every filesystem. Some systems permit distinct names that it
flags. Explain that distinction and follow the project's naming policy.

Portable mode rejects separators, control and surrogate characters, Windows-reserved
punctuation, trailing spaces or dots, and device names such as `CON`, `NUL.txt`,
`COM1`, and `LPT³`. The policy also excludes console device spellings. It is an
explicit tool policy, not a guarantee that every permitted name works everywhere.

At most 256 proposed names and 4,096 existing siblings are inspected. These are
work limits, not acceptance thresholds. Directory stability checks are best-effort;
the preview is not an atomic reservation, filesystem sandbox, or installer safety
guarantee. Someone can create a conflicting name afterward.

On native Windows, the directory-stability signatures in both runtimes compare
device/file identity, size, and modification time. They omit mode and change time
to use the same Windows metadata rule as the file-reading helpers. This is weaker
than the unchanged Linux/macOS comparison; a listing change that preserves those
fields may escape detection. Directory-type and symlink checks still apply.

The observed tests cover local macOS behavior. Portable comparison rules,
reparse-point handling, and ASCII-safe output do not establish native Windows
execution. If another comparison policy or a deeper structural mapping is needed,
use or adapt a project-owned command rather than treating this preview as universal.
