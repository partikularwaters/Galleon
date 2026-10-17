# Optional named-file inventories

After a job, a project may need to know whether selected inputs stayed unchanged.
On resume, it may need to compare current files with an earlier byte record before
relying on remembered state. This helper performs that comparison without reading
file bodies into the agent's response.

Use an adequate project command first. Otherwise, this optional Python 3.9+
standard-library helper, with a Node.js fallback, is available beside Audit. It reads named files and prints
results. It does not scan a repository, write a baseline, restore files, approve
work, or save project memory. Core skills remain usable without it.

## Without Python

`scripts/file_inventory.mjs` (Node.js 22+) takes the same command line, returns the
same exit codes, and prints the same output as the Python script under Python 3.14.
Prefer Python, then Node.js; install nothing just to run a check. Run it with the
arguments shown below, for example
`node skills/audit/scripts/file_inventory.mjs capture --root . --json README.md`.
A baseline captured by one runtime compares under the other. Node.js cannot see the
original bytes of an argument that is not valid UTF-8, so it stops with status 2 for any
argument containing U+FFFD. If neither runtime exists, compare the few named files with
the agent's own file tools and report that this was a manual check, not a hash
comparison. PowerShell versions are planned but not yet available.

## Choose what to check

The project chooses the files relevant to a named preservation or drift question.
For example, a job's agreement might require preserving `architecture/decisions.md`
and `rules/pricing.py`. Capture those two files before work and compare them later.
Do not automatically include all files, dependencies, Git metadata, or historical
records merely because they exist.

Use the project's own inventory or restoration command when it already suffices.
This helper's report format is optional interchange, not a new project contract or
mandatory memory schema. Do not silently convert an existing snapshot or replace
its authoritative owner. A project-specific adaptation may be the better choice.

## Capture selected bytes

From the source repository, for example:

```sh
python3 skills/audit/scripts/file_inventory.py capture --root . --json README.md CONTEXT.md
```

Use the script's actual installed location after installation. File names must be
canonical paths relative to the selected root, such as `docs/setup.md`. Absolute
paths, `./` prefixes, `..`, repeated separators, backslashes, and Git-internal paths
are rejected. Symlinks and Windows reparse points below the root are refused.
The selected root itself may resolve through a normal platform alias.

The baseline format has exactly these fields. This illustration describes one
empty file; it is not an observed project result:

```json
{
  "format": "named-file-inventory",
  "version": 1,
  "files": [
    {
      "path": "architecture/decisions.md",
      "size": 0,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ]
}
```

Capture reads binary bytes, including empty files, and streams SHA-256 hashes.
Repeated identical input paths are counted once. Different paths stay separate
even when they are hard links to the same file. JSON escapes Unicode for reliable
transport; parsing restores the original names. There is no absolute root, approval,
task status, timestamp, or restoration claim in the baseline.

The script only prints output. Save successful JSON at a new agreed project-owned
location, or replace a record only under existing authorization. The baseline must
be inside the selected root when this helper compares it. Do not redirect output
onto a named input or an existing authoritative baseline: a shell can truncate that
file before the helper runs. Failed capture prints no partial baseline.

## Compare the same named set

After saving a successful baseline as `work/files-baseline.json`, for example:

```sh
python3 skills/audit/scripts/file_inventory.py compare --root . --baseline work/files-baseline.json --json
```

Comparison validates the whole baseline before inspecting its named files. The
document must be UTF-8 JSON with unique fields, the supported format/version, a
nonempty list of unique canonical paths, integer byte sizes, and lowercase SHA-256
digests. Foreign schemas, extra fields, duplicate entries, and malformed records
are refused. The script never refreshes the baseline after comparison.

The report lists `changed`, `missing`, and `unsafe` entries. `checked` counts files
successfully hashed, so it excludes missing and unsafe files. `complete` is false
if an unsafe path, unreadable file, detected change during reading, or work bound
prevents checking a listed entry. Already inspected entries remain partial evidence.
An invalid baseline or input instead returns exit 2 with an error and no stdout.

| Exit | Meaning | Agent response |
| --- | --- | --- |
| 0 | Capture succeeded, or all listed comparison bytes match | Report the bounded result; apply the project's rule for what comes next. |
| 1 | Comparison completed and found changed or missing files | Explain the discrepancy before relying on the affected remembered state. |
| 2 | Invalid input or incomplete comparison | Report the limitation; do not treat partial evidence as a clean result. |

A size change counts as changed. Equal-size edits are also detected by hashing.
Extra files outside the baseline's list are not discovered, so a match does not
mean the whole project is unchanged. File modes, timestamps, symlink targets, Git
state, meaning, and baseline provenance are not compared. A hash does not establish
who created or accepted a baseline.

## Bounds and interpretation

The helper accepts at most 256 named paths, 64 MiB per hashed file, 4 MiB for the
baseline document, and 256 MiB of reads per run, including the baseline. These are
tool work limits, not acceptance thresholds. A project can use a different command
for larger work. Read-stability checks are best-effort; the report is not an atomic
snapshot or protection against later edits. Normal access-time bookkeeping may occur.

On native Windows, both runtimes compare device/file identity, size, and modification
time for read stability. Mode and change time are excluded because Python's path
and open-handle metadata can disagree. Type and symlink checks still apply. This
Windows stability check is weaker than the unchanged Linux/macOS check: an equal-size
edit preserving modification time may escape detection during reading. A later
inventory comparison still hashes the listed bytes and compares them with the baseline.

Reports disclose selected filenames and byte identities, so review them before
sharing. The helper prints no file bodies or automatic machine-path inventory.
Process and parity suites passed on macOS, Linux, and native Windows. The Windows
run used Server 2025, Python 3.11.9 and 3.14.8, and Node.js 22.23.3 and 24.21.0.
These checks do not qualify every reparse-point type, skill discovery, or fresh-agent
use.

If the project wants the result saved for a later session, use its existing evidence
or memory owner and record the selection and interpretation. Matching bytes are
mechanical evidence, not a decision to proceed or a replacement for project review.
