# Verification and limits

## Earlier engineering evidence

The earlier implementation recorded 99 passing automated tests spanning contract
parsing, preservation, guarded operations, packaging, and installer behavior.
Recorded platform exercises included macOS Codex discovery and native Windows
PowerShell installation checks. Those are different observations: native Windows
launcher success did not establish Windows Codex discovery.

That implementation also recorded bounded pilot work and restoration observations.
The full working histories remain outside this public product. Selected,
sanitized [observed results](../verification/samples.md) retain the check, outcome,
environment, and limits without publishing personal paths or project contents.
Earlier implementation results and lean-edition checks are listed separately.

## This edition

The skills have been rewritten to follow project-owned agreements without requiring
the old engine. Earlier results do not automatically qualify these revisions or a
new installation route. This edition is unversioned and has not completed an
independent unfamiliar-reader trial. No universal agent or operating-system support
is claimed. Named tools in the README illustrate the use case.

The skills instruct the agent to follow the project's agreements and perform
appropriate checks. Optional helpers estimate reading cost, check named local link
targets, compare selected file bytes, and preview sibling-name collisions. They do
not approve work or control edits. Projects can require checks in their own
agreements, but following those rules still depends on agent behavior and human
review. The earlier guarded workflow engine is not bundled.

## Local checks of this edition

The optional reading-cost helper passed seven focused process tests on macOS with
Python 3.9.6. They cover approximate outputs, input preservation, duplicate files,
Unicode paths under restrictive output encoding, invalid inputs, and read bounds.
The [public regression tests](../tests/test_token_count.py) let contributors reproduce
these mechanics. The same seven checks also passed with Python 3.11.17 and 3.14.7
on 18 October 2026. The restrictive-encoding exercise is not native Windows evidence.

Local resource checks covered links and independently copied plain-name and
prefixed skill directories. Two synthetic explicit phase reading sets also measured
successfully without changing their input bytes. These checks support resource
availability and the helper's bounded behavior; they do not demonstrate automatic
skill discovery or progressive loading by a fresh agent in this edition.

The reading-cost routine remains optional, and its estimates are approximate.
No net token savings, automatic prevention of file bloat, or content-integrity
validation is claimed. Existing project procedures determine when it is useful.

## Optional local link helper

The [link helper](../skills/sync/link-checking.md) passed 13 focused checks on macOS
with Python 3.9.6. They cover real and missing targets, Unicode and space paths,
directory targets, path escape and symlinks, code examples, unsupported syntax,
coverage counts, resource bounds, detected input changes, no-write behavior, and
standalone execution. The [public tests](../tests/test_link_checking.py) reproduce
these checks. The same 13 checks also passed with Python 3.11.17 and 3.14.7 on
18 October 2026. The backtick-destination regression ensures literal path text is not
hidden by treating it as a code example.

This is a limited local-path checker, not a Markdown renderer or navigation audit.
Fragments, query behavior, external URLs, descriptions, and authority remain
unchecked. Unsupported constructs produce an incomplete result. Native Windows
and independent fresh-agent use of this helper are not established.

## Optional named-file inventory helper

The [inventory helper](../skills/audit/file-inventories.md) passed 12 focused checks
on macOS with Python 3.9.6. They cover capture/compare round trips, equal-length and
size changes, deletion, unlisted additions, duplicate and malformed baselines,
canonical path rules, symlinks, work bounds, controlled external changes, Unicode
output, separate hard-link identities, preservation, and standalone execution.
The [public tests](../tests/test_file_inventory.py) reproduce these mechanics.
The same 12 checks also passed with Python 3.11.17 and 3.14.7 on 18 October 2026.

Matching hashes establish only the listed bytes at observation time. Extra files,
file modes, Git state, meaning, and baseline provenance are not compared. The
helper does not save or refresh the baseline, restore files, or accept a result.
Unsafe or unreadable entries make comparison incomplete. Native Windows and an
independent fresh-agent exercise of this helper are not established.

## Optional Node.js fallbacks

Every helper also ships as a Node.js script. Parity is defined against Python 3.14. The
[parity tests](../tests/test_fallback_parity.py) run the Python helper and the Node.js
script on identical disposable inputs and require the same exit status and
byte-identical standard output; error text is compared by its leading label only. They
cover capture and compare round trips, malformed and oversized baselines, path rules,
symlinks, work bounds, Unicode and whitespace handling, occupied and duplicate names
across case-folding families, the 4,096-sibling limit, fenced and inline code, line
separators, percent-encoding, scheme-like and unusual URL targets, unsupported syntax,
input preservation, and command-line parsing: abbreviated options, dash-prefixed names,
`--`, help, and usage errors. Seeded randomized cases also generate command lines,
Markdown documents, text, file names, and sibling names. `GALLEON_PARITY_SEED` and
`GALLEON_PARITY_ROUNDS` explore more of them.

Observed on 18 October 2026, on macOS 26.7 with Node.js 22.23.3:

- The reading-cost fallback passed 7 parity checks with Python 3.14.7, 3.11.17, and
  3.9.6.
- The link fallback passed 14 parity checks with Python 3.14.7 and 3.11.17. With
  Python 3.9.6, 11 passed and 3 failed. Five of the failing cases were spellings that
  3.9.6's URL splitting handles differently: a leading space inside an angle
  destination, and bracketed hosts after a single-letter scheme, such as `a://[bad]/x`.
  The two failing randomized-document cases were not traced.
- The inventory fallback passed 11 parity checks with all three versions.
- The collision fallback passed 11 parity checks with all three versions. Two more
  skip on macOS, because the filesystem is case-insensitive and rejects names that are
  not valid UTF-8.
- Command-line parsing passed 2 parity checks with Python 3.14.7. They skip on 3.11.17
  and 3.9.6, because argparse changed after 3.11. For example, `-1x` is an unknown
  option in 3.11 and a name in 3.14.
- Node.js refused invalid UTF-8 arguments with all three versions.
- A deeper run with 25 rounds and another seed passed with Python 3.14.7.

The shipped parity tests skip entirely below Python 3.11. The Python 3.9.6 results come
from a one-off run with that gate removed.

Deep checks, shipped as opt-in [tests](../tests/deep/), are configured to run weekly in
continuous integration and on demand. Normal test discovery skips them. Run them locally
with `GALLEON_DEEP=1 python3 -B -m unittest discover -s tests/deep`:

- Random command lines parse identically under Python 3.14 argparse and the Node.js
  parsers: 20,000 for each of the four helpers by default, set by `GALLEON_DEEP_CASES`. Under Python 3.11, a
  one-off run found about 1% of 20,000 such command lines differed.
- Name folding matches Python `casefold` for every code point both runtimes assign:
  292,531 with Python 3.14 and Node.js 22.23.3.
- Folder-name byte decoding matches Python's for 359,159 byte strings.

Each deep check failed when the fix it covers was deliberately broken.

One-off checks that are not shipped:

- Link reports were identical for the 68 tracked Markdown files in this repository.
- Deliberately breaking each of five fixes made the parity tests fail.

Known limits:

- Each runtime uses its own Unicode data. Python 3.14 uses Unicode 16, and Node.js
  22.23.3 uses Unicode 17. Name folding differed for 56 code points, each involving a
  character new in Unicode 17.
- Node.js cannot see the original bytes of an argument that is not valid UTF-8. It stops
  with status 2 and prints nothing to standard output for any argument containing
  U+FFFD, including a valid one that Python would accept.
- Help output matches apart from the program name only when standard output is not a
  terminal and `COLUMNS` is unset. In a terminal, Python 3.14 colors its help, and it
  wraps help to `COLUMNS`; Node.js does neither. Operating-system error details are not
  reproduced.
- Not established: Linux, where names that are not valid UTF-8 can exist; native
  Windows, where Python also detects reparse points other than symbolic links; Node.js
  24 and 26; and fresh-agent use. Node.js 18 and 20 are past end of life and not
  supported.
- PowerShell versions are planned but not yet available.

## Optional sibling-name collision helper

The [collision helper](../skills/scaffold/collision-checking.md) passed 11 focused
checks on macOS with Python 3.9.6. They cover clean and absent parents, occupied
files/directories/dangling links, case and Unicode equivalents, duplicate proposals,
portable invalid names, unsafe ancestry, simulated inaccessible listings, work
bounds, detected listing changes, preservation, ASCII-safe output, and standalone
execution. The [public tests](../tests/test_collision_checking.py) reproduce these
checks. The same 11 checks also passed with Python 3.11.17 and 3.14.7 on 18 October
2026. The product suite contains 43 Python helper checks and 48 Node.js parity checks
across the four helpers.

The NFC-and-case-folding policy is conservative, not a filesystem emulator. A clear
preview neither reserves names nor establishes ownership or write safety. Recheck
before authorized creation. Native Windows execution and independent fresh-agent
use of this helper remain unverified.

## Native Windows repair checks

The first CI run on commit `d92be57` passed all nine non-Windows jobs but failed
all four native Windows jobs. Branch diagnostics then identified two metadata
differences in Python: change time can disagree between a path lookup and an open
file on Python 3.14, and `.exe` paths can have different mode bits from their open
handles. The repair compares device/file identity, size, and modification time on
Windows in both runtimes. It retains regular-file, directory, symlink, and read-bound
checks, but the Windows stability comparison is weaker. Equal-size edits preserving
modification time may escape detection; Linux and macOS keep their existing checks.

The Node.js helpers now use Windows line endings for stdout and stderr on Windows.
Both link checkers reject trailing spaces or dots and reserved punctuation in local
path components on every platform, as the [link guide](../skills/sync/link-checking.md)
explains. The Node.js link checker also matches Python's Windows rejection of control
characters. These are bounded helper policies, not a complete filesystem emulator.

The repaired branch still needs a passing native Windows run. Current implementation
and local checks do not yet establish Windows support. The helper guides retain their
earlier observed-platform limits until the repaired suites pass in CI. In particular,
Python's reparse-point handling does not establish equivalent Node.js handling of
every reparse-point type, and automated helper tests do not establish skill discovery
or fresh-agent use.

## Independent trial before v1

Before a v1 decision, identify an exact commit and observe installation, discovery,
resource loading, a bounded real job, and continuation. Use the [verification record](independent-verification.md)
and disclose failures and interventions. Any executable installer introduced later
needs its own appropriate checks. Do not infer human acceptance from passing tests.

## Durability without installed skills

The three-phase lifecycle describes the intended transfer of procedural guidance
into project-owned records. Existing link checks and fresh-session continuation
claims do not by themselves establish operation without Galleon installed.

A [maintainer-operated observation across three CLI setups](../verification/project-owned-continuation.md)
recorded plain-language restoration, a bounded readiness review, and separate
fresh-session recovery in copies of one manually adapted project without a visible
skills catalog. All three recovered the latest review, but all left stale
preparation-manifest references, and some reports overstated evidence. The report
discloses runtime controls, requested models, setup interventions, and limits.
It supports the exercised project-owned continuation route, not the full bootstrap
lifecycle, universal compatibility, or the independent unfamiliar-reader trial.

The [verification record](independent-verification.md#optional-observation-of-operation-without-galleon)
provides a scoped observation for a fresh session without Galleon skills or prior
conversation context. Report navigation separately from any authorized bounded
task execution, disclose interventions, and limit claims to the exercised job and
environment. This observation is useful when independence matters, not a mandatory
ceremony for every project or save.
