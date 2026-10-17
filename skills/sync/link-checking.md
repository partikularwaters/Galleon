# Optional local link checking

A route such as `[setup](docs/setup.md)` is useful only if its target still exists.
This helper checks that mechanical fact so the agent can focus on whether the route
also points to the right owner and explains the right next action.

Use the project's existing command when it already does the job. Otherwise, this
small Python 3.9+ helper, with a Node.js fallback, is available beside Sync. It reads explicitly named UTF-8
Markdown documents and inspects their local targets; it never repairs links, scans
the whole repository, fetches URLs, or approves work. Core Galleon skills do not
require Python or this helper.

## Without Python

`scripts/check_links.mjs` (Node.js 22+) takes the same arguments, returns the same exit
codes, and prints the same report as the Python script under Python 3.14. Prefer Python,
then Node.js; install nothing just to run a check. For example,
`node skills/sync/scripts/check_links.mjs --root . CONTEXT.md`. It reproduces Python's
whitespace, line-splitting, and Python 3.14 URL-splitting rules by hand, because
JavaScript defines those differently. Python's own URL parsing has changed between
releases: Python 3.9.6, for example, reports `[x](< ../good.md>)` and `a://[bad]/x`
differently. Node.js cannot see the original bytes of an argument that is not valid
UTF-8, so it stops with status 2 for any argument containing U+FFFD. With no runtime,
open each named document with the agent's own file tools, confirm its local targets
exist, and report that this was a manual check that applied none of the parser's rules.
PowerShell versions are planned but not yet available.

## Choose the scope

The project decides which records matter. For example, after moving a setup guide,
check the entry router and the installation page that refer to it. At a new session,
use a declared reading set if the project wants this check. Do not run it against
every file merely because a skill is available.

Run the script at its actual installed location. From the source repository:

```sh
python3 skills/sync/scripts/check_links.py --root . CONTEXT.md docs/getting-started.md
```

For structured output:

```sh
python3 skills/sync/scripts/check_links.py --root . --json CONTEXT.md docs/getting-started.md
```

The selected root is the boundary. Input document names are relative to it. A link
is resolved relative to its source document, so `../architecture.md` is allowed
when it stays inside the root. Symlinks and Windows reparse points below that root
are refused, even when their targets remain inside it. A selected root itself may
resolve through a normal platform alias. Existing files and directories can be
targets; the script does not read their contents just to confirm existence.

Both runtimes apply a portable spelling policy on every operating system. Local
path components ending in a space or dot, or containing any of `<>:"|?*`, are
unsafe. This includes percent-decoded spellings such as `good.md%20` and
`folder%3F/guide.md`, and components later removed by `..`. The same rule applies
to named input documents. The navigation components `.` and `..` remain allowed
within the selected root. Unsafe targets make the check incomplete with exit 2,
even on Linux or macOS where a file with that spelling may exist. This policy
covers these spellings only; it does not implement the collision helper's full
portable name policy, such as its Windows device-name exclusions.

## Read the result

A shortened illustrative JSON report looks like this:

```json
{
  "method": "local-markdown-paths-v1",
  "complete": true,
  "files": ["CONTEXT.md"],
  "checked": 3,
  "skipped_external": 1,
  "unverified_fragments": 1,
  "unverified_queries": 0,
  "links_found": 4,
  "unsupported": 0,
  "issues": []
}
```

`complete` means the selected, supported path check completed. It does not mean
all navigation is correct. `checked` counts local path checks, including missing
targets. `links_found` counts parsed inline links and images; it excludes unsupported
constructs. External URLs are skipped. Fragments and query strings are reported as
unverified; a fragment-only link does not count as a checked local path.

Each issue includes its source, line, destination when parsed, kind, and reason.
Missing targets use kind `missing`; unsafe targets, invalid inputs, and unsupported
syntax make the run incomplete. JSON output escapes Unicode for reliable transport,
but parsing restores the original names. Reports can disclose filenames, so review
them before sharing. The script does not print the selected root or document bodies.

| Exit | Meaning | Agent response |
| --- | --- | --- |
| 0 | Supported checks completed without findings | Report the bounded result; inspect descriptions and ownership separately. |
| 1 | Checks completed and found missing local targets | Explain the findings and correct only navigation already authorized by the project. |
| 2 | Invalid input, unsafe scope, unsupported syntax, a read bound, or detected change prevented completion | Report the incomplete scope and choose an adequate project command or a narrower check. Do not treat partial results as a pass. |

If no local targets were checked, the text report says so. An empty reading set,
or a page containing only external links, supplies no meaningful local navigation
evidence. The script requires at least one named input document.

## Supported syntax and limits

The first version handles ordinary single-line inline links and images, angle-bracket
destinations with spaces, percent-encoded local paths, and optional single- or
double-quoted titles. Fenced code and matched inline code spans are excluded.

Reference-style links, standalone bracket constructs, nested or multiline labels,
unquoted nested destination parentheses, backslash escapes, indented link constructs,
autolinks, and HTML link/image tags are reported as unsupported. Use fenced blocks
for code examples. This is a deliberately limited parser, not a complete CommonMark
renderer. It does not validate Markdown outside the supported link constructs.

The helper checks the path portion only. It does not validate heading anchors,
external availability, URL query behavior, descriptions, ownership, or approval.
It reads at most 256 named inputs, 4 MiB per document, 256 MiB total, and 4,096 link
candidates per run. Duplicate normalized input paths are checked once. These are
tool work limits, not acceptance thresholds.

Read-stability checks are best-effort. Files and targets can change afterward, and
the helper is not an atomic snapshot or filesystem sandbox. Local tests qualify
the observed macOS execution only; Windows reparse handling and ASCII-safe output
do not by themselves establish native Windows execution.

If the project needs a different syntax, scope, or policy, use its own tool or adapt
this helper explicitly. A passing report provides evidence; the project's contract
still determines what to do with it.
