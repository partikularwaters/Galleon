# Verification and limits

## Earlier engineering evidence

The earlier implementation recorded 99 passing automated tests spanning contract
parsing, preservation, guarded operations, packaging, and installer behavior.
Recorded platform exercises included macOS Codex discovery and native Windows
PowerShell installation checks. Those are different observations: native Windows
launcher success did not establish Windows Codex discovery.

That implementation also recorded bounded pilot work and restoration observations.
The full working histories remain outside this public product. Selected synthetic
examples are in [verification samples](../verification/samples.md).

## This edition

The skills have been rewritten to follow project-owned agreements without requiring
the old engine. Earlier results do not automatically qualify these revisions or a
new installation route. This edition is unversioned and has not completed an
independent unfamiliar-reader trial. No universal agent or operating-system support
is claimed. Named tools in the README illustrate the use case.

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

## Independent trial before v1

Before a v1 decision, identify an exact commit and observe installation, discovery,
resource loading, a bounded real job, and continuation. Use the [trial record](friend-trial.md)
and disclose failures and interventions. Any executable installer introduced later
needs its own appropriate checks. Do not infer human acceptance from passing tests.
