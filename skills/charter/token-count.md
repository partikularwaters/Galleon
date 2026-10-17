# Optional file reading-cost estimate

Use this helper only when file size matters to a proposed reading or migration
change, and the project has no adequate command already. Do not run it for every
plan or use a count to override project contracts. It needs an existing Python 3.9+
or Node.js 22+ runtime; the core skills need neither. Do not install dependencies just
to obtain a count.

From the repository root, for example:

```sh
python3 -B skills/charter/scripts/count_tokens.py architecture.md
```

If Python is absent, `scripts/count_tokens.mjs` (Node.js 22+) takes the same arguments
and prints the same report as the Python script under Python 3.14, for example
`node skills/charter/scripts/count_tokens.mjs architecture.md`. Node.js cannot see the
original bytes of an argument that is not valid UTF-8, so it stops with status 2 for any
argument containing U+FFFD. With no runtime, estimate by hand from the file sizes and
say so. PowerShell versions are planned but not yet available.

In an installed skill, use its local [script](scripts/count_tokens.py) path instead.
Pass only explicitly selected files. Quote paths with spaces. On Windows, use your
existing Python command and the corresponding script path; native Windows execution
of this helper passed process and parity suites on Windows Server 2025 with Python
3.11.9 and 3.14.8 and Node.js 22.23.3 and 24.21.0. This covers the tested helper
behavior, not skill discovery or fresh-agent use.

## What it measures

The method is whitespace-separated word count multiplied by 1.3, rounded up. UTF-8
with an optional byte-order mark is supported. This is a rough comparison aid, not
an exact tokenizer count. Code, minified content, languages without spaces, and
formatting can differ greatly. It does not measure total prompt cost or token savings.

The output lists each file, a sum for the unique declared read set, and the limitation.
Duplicate paths and hard-link aliases count once. `--json` gives machine-readable
output. Output escapes non-ASCII paths for transport; JSON parsing recovers them.
It does not print file contents or save a report.

Exit 0 means a measurement was produced, not that the structure is good. Exit 2 means
an input was missing, unreadable, invalid UTF-8, nonregular, changed during the read,
or outside a read bound. No partial success report is printed. At most 32 named paths
and 4 MiB per file are supported. These are tool bounds, not migration thresholds.
Final symlink inputs are rejected; this helper is not a filesystem sandbox and cannot
guarantee detection of every concurrent edit. It reads metadata and bytes only;
normal filesystem access-time bookkeeping may still occur.

On native Windows, both runtimes compare device/file identity, size, and modification
time for read stability. They omit change time because Python's path and open-handle
metadata can disagree. This is weaker than the check on Linux and macOS, which is
unchanged. The regular-file checks still apply; equal-size edits that also preserve
modification time may escape the Windows stability check.

## What to propose next

For example: "Only the storage section is relevant to this job. We can read that
section instead of the whole architecture file. If different readers repeatedly
need separate topics, we can propose a small router and topic files."

Combine the estimate with actual read frequency, relevant sections, distinct owners,
current routes, and migration cost. A large cohesive file can stay intact, and a
small file can need separation for ownership reasons. No universal threshold, automatic
ranking, or structural edit is performed. Partial-section counts are not supported
in this first helper; do not report whole-file estimates as measured section costs.

## Why and when a project might use it

Routine context can grow until each session reads more than its job needs. This
helper makes that cost visible, so a project can keep agents focused and support
progressive reading: load the entry and active work first, then follow relevant
references. It helps identify unnecessary reading; it does not prevent file bloat
or judge the quality of a contract.

A project may adopt checks at session start, after a completed phase, and during
closing capture. The [memory guide](memory-guide.md#optional-reading-cost-routine)
explains that optional routine. Follow an adequate existing project procedure
instead of loading or adopting an alternative.

The project declares the files, timing, and summary owner. Resolve that reading set
into explicit command arguments; this helper does not interpret phase contracts or
discover files. For example, from a Galleon checkout with a synthetic project at
../timer, its declared set could be measured with:

```sh
python3 -B skills/charter/scripts/count_tokens.py --json ../timer/AGENTS.md ../timer/memory/CONTEXT.md ../timer/memory/state.md ../timer/tasks/quiet-mode.md
```

This example assumes those files exist; adapt the paths to the real project and
installed helper. The command prints output only. Capture can save its concise
interpretation at the project's existing owner when authorized. At resume, label
saved measurements accurately and remeasure only as the project directs. A different
reading set needs its own label, and equal counts do not prove unchanged contents.
