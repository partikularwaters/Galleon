"""Drift checks: public records match the repository they describe.

Links in every tracked Markdown file resolve, tracked files carry no machine paths or real
email addresses, and the check counts quoted in docs/verification.md match the test suite.
These run only in a Git checkout, because the tracked-file list comes from Git.
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which('git')
NUMBERS = {'two': 2, 'seven': 7}
PERSONAL = [re.compile(p) for p in (r'/Users/[^/\s]+/', r'/home/[a-z][^/\s]*/', r'/root/',
                                     r'[A-Za-z]:[\\/]Users[\\/]')]
EMAIL = re.compile(r'(?<![\w.%+-])[A-Za-z][A-Za-z0-9._%+-]*@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b')
# Synthetic domains, Git remote addresses, and image-scale names such as icon@2x.png are not personal.
SYNTHETIC = re.compile(r'@(?:[A-Za-z0-9-]+\.)*(?:invalid|example\.(?:com|org|net))$|^git@|@\dx\.')


def tracked(pattern=None):
    args = [GIT, 'ls-files', '-z'] + ([pattern] if pattern else [])
    run = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=60)
    if run.returncode:
        raise unittest.SkipTest('not a Git checkout')
    return [name for name in run.stdout.decode('utf-8').split('\0') if name]


def count(name):
    """Count the tests in a module, or in one of its classes when named as module.Class."""
    module, _, cls = name.partition('.')
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=module + '.py')

    def tests(item):
        if isinstance(item, unittest.TestSuite):
            for child in item:
                yield from tests(child)
        else:
            yield item
    return sum(1 for test in tests(suite) if not cls or type(test).__name__ == cls)


def number(word):
    return int(word) if word.isdigit() else NUMBERS[word.lower()]


@unittest.skipUnless(GIT, 'git is not installed')
class RepositoryConsistency(unittest.TestCase):
    def test_tracked_markdown_links_resolve(self):
        files = tracked('*.md')
        run = subprocess.run([sys.executable, '-B', str(ROOT / 'skills/sync/scripts/check_links.py'),
                              '--root', str(ROOT), *files], capture_output=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stdout.decode('utf-8', 'replace'))

    def test_tracked_files_carry_no_machine_paths_or_real_email_addresses(self):
        found = []
        for name in tracked():
            if name == Path(__file__).relative_to(ROOT).as_posix():
                continue
            try:
                text = (ROOT / name).read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue
            for number_, line in enumerate(text.splitlines(), 1):
                if any(p.search(line) for p in PERSONAL):
                    found.append(f'{name}:{number_}: machine path')
                for match in EMAIL.finditer(line):
                    if not SYNTHETIC.search(match.group(0)):
                        found.append(f'{name}:{number_}: email address')
        self.assertEqual(found, [])

    def test_verification_counts_match_the_tests(self):
        text = ' '.join((ROOT / 'docs/verification.md').read_text(encoding='utf-8').split())
        helpers = {'reading-cost': 'test_token_count', 'link': 'test_link_checking',
                   'inventory': 'test_file_inventory', 'collision': 'test_collision_checking'}
        helper_counts = {label: count(module) for label, module in helpers.items()}
        quoted = re.findall(r'(?:optional reading-cost helper|\[(link|inventory|collision) helper\]\([^)]*\)) '
                            r'passed (\w+) focused', text)
        self.assertEqual({label or 'reading-cost': number(n) for label, n in quoted}, helper_counts)
        same = [number(n) for n in re.findall(r'The same (\w+) checks also passed', text)]
        self.assertEqual(same, list(helper_counts.values()))
        parity = {label: count('test_fallback_parity.' + name) for label, name in (
            ('reading-cost', 'TokenParity'), ('link', 'LinkParity'), ('inventory', 'InventoryParity'),
            ('collision', 'CollisionParity'))}
        quoted = dict(re.findall(r'The (reading-cost|link|inventory|collision) fallback passed (\d+) parity', text))
        collision_skips = number(re.search(r'collision fallback passed \d+ parity checks with all three '
                                           r'versions\. (\w+) more skip', text).group(1))
        quoted = {label: int(n) + (collision_skips if label == 'collision' else 0) for label, n in quoted.items()}
        self.assertEqual(quoted, parity)
        arguments = int(re.search(r'Command-line parsing passed (\d+) parity', text).group(1))
        self.assertEqual(arguments, count('test_fallback_parity.ArgumentParity'))
        totals = re.search(r'contains (\d+) Python helper checks and (\d+) Node\.js parity checks', text)
        self.assertEqual((int(totals.group(1)), int(totals.group(2))),
                         (sum(helper_counts.values()), count('test_fallback_parity')))


if __name__ == '__main__':
    unittest.main()
