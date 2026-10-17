"""Bounded inventory process checks using disposable files, without third-party packages."""
import hashlib
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

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/audit/scripts/file_inventory.py'


class FileInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / 'one.bin').write_bytes(b'\x00\xffold\n')
        (self.root / 'empty').write_bytes(b'')

    def tool(self, command, *args, json_output=True):
        env = dict(os.environ, PYTHONIOENCODING='cp1252:strict')
        call = [sys.executable, '-B', str(SCRIPT), command, '--root', str(self.root)]
        if json_output:
            call.append('--json')
        return subprocess.run(call + list(args), capture_output=True, env=env, timeout=15)

    def report(self, run, code=0):
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        self.assertEqual(run.stderr, b'')
        self.assertTrue(run.stdout.isascii())
        return json.loads(run.stdout)

    def saved(self, *names):
        data = self.report(self.tool('capture', *names))
        (self.root / 'baseline.json').write_text(json.dumps(data, ensure_ascii=True), encoding='utf-8')
        return data

    def helper(self):
        spec = importlib.util.spec_from_file_location('inventory_under_test', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_capture_compare_binary_empty_and_exact_duplicate_roundtrip(self):
        data = self.saved('one.bin', 'empty', 'one.bin')
        self.assertEqual(data['format'], 'named-file-inventory')
        self.assertEqual([x['path'] for x in data['files']], ['empty', 'one.bin'])
        self.assertEqual(data['files'][1]['sha256'], hashlib.sha256(b'\x00\xffold\n').hexdigest())
        result = self.report(self.tool('compare', '--baseline', 'baseline.json'))
        self.assertTrue(result['complete'])
        self.assertEqual(result['checked'], 2)
        self.assertEqual((result['changed'], result['missing'], result['unsafe']), ([], [], []))
        (self.root / 'sample.exe').write_bytes(b'executable-named bytes')
        executable = self.report(self.tool('capture', 'sample.exe'))
        self.assertEqual(executable['files'][0]['sha256'], hashlib.sha256(b'executable-named bytes').hexdigest())

    def test_same_length_and_size_changes_are_detected(self):
        self.saved('one.bin', 'empty')
        (self.root / 'one.bin').write_bytes(b'\x00\xffnew\n')
        (self.root / 'empty').write_bytes(b'new bytes')
        result = self.report(self.tool('compare', '--baseline', 'baseline.json'), 1)
        self.assertTrue(result['complete'])
        self.assertEqual(result['changed'], ['empty', 'one.bin'])

    def test_missing_files_and_unlisted_additions_do_not_refresh_baseline(self):
        self.saved('one.bin', 'empty')
        before = (self.root / 'baseline.json').read_bytes()
        (self.root / 'one.bin').unlink()
        (self.root / 'unlisted.txt').write_text('not in scope', encoding='utf-8')
        result = self.report(self.tool('compare', '--baseline', 'baseline.json'), 1)
        self.assertEqual(result['missing'], ['one.bin'])
        self.assertEqual(result['changed'], [])
        self.assertTrue(result['complete'])
        self.assertEqual(before, (self.root / 'baseline.json').read_bytes())

    def test_unicode_transport_and_hardlinks_retain_separate_path_identities(self):
        name = 'space ñ 文.bin'
        (self.root / name).write_bytes(b'contents')
        os.link(self.root / name, self.root / 'alias.bin')
        data = self.saved(name, 'alias.bin', name)
        self.assertEqual(len(data['files']), 2)
        self.assertEqual(data['files'][1]['path'], name)
        self.assertEqual(data['files'][0]['sha256'], data['files'][1]['sha256'])
        self.report(self.tool('compare', '--baseline', 'baseline.json'))
        text = self.tool('capture', name, json_output=False)
        self.assertEqual(text.returncode, 0)
        self.assertTrue(text.stdout.isascii())

    def test_malformed_duplicate_empty_or_foreign_baselines_are_rejected(self):
        valid = self.saved('one.bin')
        variants = []
        for key, value in [('format', 'foreign'), ('version', True), ('version', 2), ('files', [])]:
            variant = dict(valid, **{key: value})
            variants.append(json.dumps(variant))
        variants.append(json.dumps(dict(valid, approval='not a supported field')))
        variants.append(json.dumps(dict(valid, files=valid['files'] * 2)))
        for key, value in [('size', True), ('size', -1), ('sha256', 'not-a-digest'),
                           ('path', '../outside'), ('path', '.git/config'), ('path', 'bad\ud800')]:
            entry = dict(valid['files'][0], **{key: value})
            variants.append(json.dumps(dict(valid, files=[entry])))
        variants.extend(['{"format":"x","format":"y"}', '{"version":NaN}',
                         '{"version":' + ('1' * 1000) + '}', '[]', '{', 'null'])
        for raw in variants:
            with self.subTest(raw=raw[:70]):
                (self.root / 'baseline.json').write_text(raw, encoding='utf-8')
                run = self.tool('compare', '--baseline', 'baseline.json')
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, b'')
                self.assertTrue(run.stderr.startswith(b'INCOMPLETE:'))

    def test_invalid_capture_inputs_do_not_print_partial_baselines(self):
        (self.root / 'dir').mkdir()
        for name in ('missing', 'dir', './one.bin', '../outside', 'a//b', '.git/config',
                     'nested/.GIT/config', str(self.root / 'one.bin'), 'C:/file', 'a\\b'):
            with self.subTest(name=name):
                run = self.tool('capture', 'empty', name)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, b'')
                self.assertTrue(run.stderr.isascii())
                self.assertNotIn(str(self.root).encode(), run.stderr)

    def test_symlink_and_nonregular_comparisons_are_incomplete(self):
        self.saved('one.bin')
        (self.root / 'one.bin').unlink()
        (self.root / 'one.bin').mkdir()
        report = self.report(self.tool('compare', '--baseline', 'baseline.json'), 2)
        self.assertFalse(report['complete'])
        self.assertEqual(report['unsafe'][0]['path'], 'one.bin')
        (self.root / 'one.bin').rmdir()
        try:
            (self.root / 'one.bin').symlink_to(self.root / 'empty')
            (self.root / 'parent').symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlink creation unavailable')
        report = self.report(self.tool('compare', '--baseline', 'baseline.json'), 2)
        self.assertFalse(report['complete'])
        self.assertEqual(self.tool('capture', 'parent/empty').returncode, 2)
        self.assertEqual(self.tool('compare', '--baseline', 'parent/baseline.json').returncode, 2)

    def test_work_bounds_cover_file_baseline_selection_and_shared_read_budget(self):
        large = self.root / 'large'
        with large.open('wb') as stream:
            stream.truncate(64 * 1024 * 1024 + 1)
        self.assertEqual(self.tool('capture', 'large').returncode, 2)
        self.assertEqual(self.tool('capture', *(['empty'] * 257)).returncode, 2)
        (self.root / 'baseline.json').write_bytes(b' ' * (4 * 1024 * 1024 + 1))
        self.assertEqual(self.tool('compare', '--baseline', 'baseline.json').returncode, 2)
        helper = self.helper()
        with patch.object(helper, 'MAX_TOTAL_BYTES', 5):
            with self.assertRaises(helper.CheckError):
                helper.capture(self.root, ['one.bin'])
        budget = {'remaining': 10}
        helper.read(self.root, 'one.bin', 64, budget)
        self.assertEqual(budget['remaining'], 4)
        with self.assertRaises(helper.CheckError):
            helper.read(self.root, 'one.bin', 64, budget)

    def test_detected_external_change_is_incomplete_and_consumes_read_budget(self):
        helper = self.helper()
        fstat, calls = os.fstat, 0

        def intervene(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                (self.root / 'one.bin').write_bytes(b'externally changed')
            return fstat(descriptor)

        budget = {'remaining': 100}
        with patch.object(helper.os, 'fstat', side_effect=intervene):
            with self.assertRaises(helper.CheckError):
                helper.read(self.root, 'one.bin', 64, budget)
        self.assertEqual(budget['remaining'], 94)

    def test_success_and_failure_preserve_inputs_baseline_modes_and_layout(self):
        self.saved('one.bin', 'empty')
        def inventory():
            return {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.root.iterdir()}
        before = inventory()
        self.report(self.tool('capture', 'one.bin', 'empty'))
        self.report(self.tool('compare', '--baseline', 'baseline.json'))
        self.assertEqual(self.tool('capture', 'empty', 'absent').returncode, 2)
        self.assertEqual(before, inventory())
        self.assertFalse((SCRIPT.parent / '__pycache__').exists())

    def test_baseline_path_remains_inside_explicit_root(self):
        self.saved('one.bin')
        for name in ('../baseline.json', str(self.root / 'baseline.json'), '.git/baseline.json'):
            self.assertEqual(self.tool('compare', '--baseline', name).returncode, 2)

    def test_copied_script_runs_without_other_skills_or_runtime_package(self):
        copied = self.root / 'copy/file_inventory.py'
        copied.parent.mkdir()
        shutil.copy2(SCRIPT, copied)
        run = subprocess.run([sys.executable, '-B', str(copied), 'capture', '--root', str(self.root),
                              '--json', 'one.bin'], capture_output=True, timeout=15)
        self.assertEqual(self.report(run)['files'][0]['path'], 'one.bin')


if __name__ == '__main__':
    unittest.main()
