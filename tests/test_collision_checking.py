"""Focused collision preview checks on disposable siblings, without external packages."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/scaffold/scripts/check_collisions.py'


class CollisionCheckingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.parent = self.root / 'siblings'
        self.parent.mkdir()

    def tool(self, *names, parent=None, json_output=True):
        command = [sys.executable, '-B', str(SCRIPT), '--parent', str(parent if parent is not None else self.parent)]
        if json_output:
            command.append('--json')
        return subprocess.run(command + list(names), capture_output=True,
                              env=dict(os.environ, PYTHONIOENCODING='cp1252:strict'), timeout=15)

    def report(self, run, code=0):
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        self.assertEqual(run.stderr, b'')
        self.assertTrue(run.stdout.isascii())
        result = json.loads(run.stdout)
        self.assertNotIn(str(self.root), json.dumps(result))
        return result

    def helper(self):
        spec = importlib.util.spec_from_file_location('collision_under_test', SCRIPT)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        return helper

    def test_clean_existing_and_missing_parents_are_read_only(self):
        report = self.report(self.tool('new-record.md', 'memory'))
        self.assertTrue(report['complete'])
        self.assertTrue(report['parent_exists'])
        self.assertEqual(report['siblings_checked'], 0)
        absent = self.root / 'new-parent/deeper'
        report = self.report(self.tool('work.md', parent=absent))
        self.assertFalse(report['parent_exists'])
        self.assertFalse(absent.parent.exists())
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_existing_files_and_directories_are_occupied(self):
        (self.parent / 'work.md').write_bytes(b'owned elsewhere')
        (self.parent / 'memory').mkdir()
        report = self.report(self.tool('work.md', 'memory'), 1)
        self.assertTrue(report['complete'])
        self.assertEqual(len(report['occupied']), 2)
        self.assertTrue(all(item['kind'] == 'exact' for item in report['occupied']))

    def test_case_and_unicode_equivalent_names_are_disclosed(self):
        (self.parent / 'Readme.md').write_bytes(b'one')
        (self.parent / 'café').write_bytes(b'two')
        report = self.report(self.tool('README.md', 'cafe\u0301'), 1)
        self.assertEqual(len(report['occupied']), 2)
        self.assertTrue(all(item['kind'] == 'equivalent' for item in report['occupied']))
        self.assertIn('NFC', report['policy'])

    def test_duplicate_proposals_are_findings_even_when_parent_is_absent(self):
        for names in (('work.md', 'work.md'), ('Memory', 'memory'), ('Straße', 'STRASSE')):
            with self.subTest(names=names):
                report = self.report(self.tool(*names, parent=self.root / 'absent'), 1)
                self.assertEqual(len(report['duplicates']), 1)
                self.assertEqual(report['occupied'], [])

    def test_portable_invalid_names_make_the_check_incomplete(self):
        names = ('a/b', 'a\\b', '.', '..', 'trailing.', 'trailing ', 'CON', 'nul.txt',
                 'Com1.log', 'LPT³', 'a:b', 'a?', 'a*', 'a"b', 'a|b', '<a>', '\x01bad')
        for name in names:
            with self.subTest(name=name):
                report = self.report(self.tool(name), 2)
                self.assertFalse(report['complete'])
                self.assertEqual(report['invalid'][0]['name'], name)
        helper = self.helper()
        for name in ('', 'nul\x00name', 'bad\ud800'):
            self.assertFalse(helper.check(str(self.parent), [name])['complete'])

    def test_dangling_sibling_is_occupied_but_parent_links_are_incomplete(self):
        try:
            (self.parent / 'dangling').symlink_to(self.root / 'absent')
            (self.root / 'linked-parent').symlink_to(self.parent, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlink creation unavailable')
        report = self.report(self.tool('dangling'), 1)
        self.assertEqual(report['occupied'][0]['kind'], 'exact')
        report = self.report(self.tool('new', parent=self.root / 'linked-parent'), 2)
        self.assertFalse(report['complete'])

    def test_non_directory_ancestors_and_dotdot_are_incomplete(self):
        file = self.root / 'file'
        file.write_bytes(b'not a directory')
        for parent in (file, file / 'child', self.parent / '..' / 'other'):
            with self.subTest(parent=str(parent)):
                report = self.report(self.tool('new', parent=parent), 2)
                self.assertFalse(report['complete'])

    def test_inaccessible_listing_and_work_bounds_are_incomplete(self):
        helper = self.helper()
        with patch.object(helper.os, 'scandir', side_effect=PermissionError('fixture')):
            report = helper.check(str(self.parent), ['new'])
        self.assertFalse(report['complete'])
        self.assertIn('could not be read', report['errors'][0])
        for index in range(3):
            (self.parent / str(index)).write_bytes(b'')
        with patch.object(helper, 'MAX_SIBLINGS', 2):
            self.assertFalse(helper.check(str(self.parent), ['new'])['complete'])
        self.report(self.tool(*(['new'] * 257)), 2)

    def test_detected_listing_change_is_incomplete(self):
        helper = self.helper()
        actual = os.scandir

        class ChangingListing:
            def __enter__(self):
                self.listing = actual(self.parent)
                return self

            def __iter__(self):
                yield from self.listing
                (self.parent / 'external-addition').write_bytes(b'outside intervention')

            def __exit__(self, *args):
                self.listing.close()

        fixture = ChangingListing()
        fixture.parent = self.parent
        with patch.object(helper.os, 'scandir', return_value=fixture):
            report = helper.check(str(self.parent), ['new'])
        self.assertFalse(report['complete'])
        self.assertIn('changed', report['errors'][0])

    def test_unicode_outputs_and_input_layout_are_preserved(self):
        name = 'space ñ 文'
        (self.parent / name).write_bytes(b'preserve')
        before = {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.parent.iterdir()}
        report = self.report(self.tool(name), 1)
        self.assertEqual(report['occupied'][0]['name'], name)
        text = self.tool(name, json_output=False)
        self.assertEqual(text.returncode, 1)
        self.assertTrue(text.stdout.isascii())
        self.report(self.tool('new-name'), 0)
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.parent.iterdir()})
        self.assertFalse((SCRIPT.parent / '__pycache__').exists())

    def test_copied_script_has_no_other_skill_or_runtime_dependency(self):
        copied = self.root / 'copy/check_collisions.py'
        copied.parent.mkdir()
        shutil.copy2(SCRIPT, copied)
        run = subprocess.run([sys.executable, '-B', str(copied), '--parent', str(self.parent),
                              '--json', 'new-name'], capture_output=True, timeout=15)
        self.assertTrue(self.report(run)['complete'])


if __name__ == '__main__':
    unittest.main()
