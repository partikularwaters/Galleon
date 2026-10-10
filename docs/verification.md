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
these mechanics. The restrictive-encoding exercise is not native Windows evidence.

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
these checks. The backtick-destination regression ensures literal path text is not
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

Matching hashes establish only the listed bytes at observation time. Extra files,
file modes, Git state, meaning, and baseline provenance are not compared. The
helper does not save or refresh the baseline, restore files, or accept a result.
Unsafe or unreadable entries make comparison incomplete. Native Windows and an
independent fresh-agent exercise of this helper are not established.

## Optional sibling-name collision helper

The [collision helper](../skills/scaffold/collision-checking.md) passed 11 focused
checks on macOS with Python 3.9.6. They cover clean and absent parents, occupied
files/directories/dangling links, case and Unicode equivalents, duplicate proposals,
portable invalid names, unsafe ancestry, simulated inaccessible listings, work
bounds, detected listing changes, preservation, ASCII-safe output, and standalone
execution. The [public tests](../tests/test_collision_checking.py) reproduce these
checks. The current product suite contains 43 passing checks across four helpers.

The NFC-and-case-folding policy is conservative, not a filesystem emulator. A clear
preview neither reserves names nor establishes ownership or write safety. Recheck
before authorized creation. Native Windows execution and independent fresh-agent
use of this helper remain unverified.

## Independent trial before v1

Before a v1 decision, identify an exact commit and observe installation, discovery,
resource loading, a bounded real job, and continuation. Use the [verification record](independent-verification.md)
and disclose failures and interventions. Any executable installer introduced later
needs its own appropriate checks. Do not infer human acceptance from passing tests.
