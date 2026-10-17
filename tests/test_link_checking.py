"""Focused process checks for optional local Markdown path evidence."""
import json
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "skills/sync/scripts/check_links.py"


class LinkCheckingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "docs").mkdir()
        (self.root / "good.md").write_text("target\n", encoding="utf-8")

    def document(self, text, name="docs/routes.md"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path.relative_to(self.root).as_posix()

    def run_tool(self, *names, json_output=True):
        env = dict(os.environ, PYTHONIOENCODING="cp1252:strict")
        args = [sys.executable, "-B", str(SCRIPT), "--root", str(self.root)]
        if json_output:
            args.append("--json")
        return subprocess.run(args + list(names), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=env, timeout=15)

    def report(self, result, expected):
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        self.assertTrue(result.stdout.isascii())
        self.assertEqual(result.stderr, b"")
        return json.loads(result.stdout)

    def test_existing_file_directory_parent_and_unicode_targets(self):
        (self.root / "space ñ 文.md").write_text("target", encoding="utf-8")
        doc = self.document('[file](../good.md)\n[dir](.)\n![image](<../space ñ 文.md>)\n'
                            '[encoded](../space%20%C3%B1%20%E6%96%87.md "title")\n'
                            "[quoted](../good.md 'title')\n")
        report = self.report(self.run_tool(doc, doc), 0)
        self.assertEqual(report["checked"], 5)
        self.assertEqual(report["files"], [doc])
        self.assertTrue(report["complete"])
        self.assertNotIn(str(self.root), json.dumps(report))

    def test_fenced_and_inline_code_are_excluded(self):
        doc = self.document('```md\n[missing](absent.md)\n```\n'
                            '~~~\n[missing](absent.md)\n~~~\n'
                            '`[missing](absent.md)` and `` `[missing](absent.md)` ``\n'
                            '[real](../good.md)\n')
        report = self.report(self.run_tool(doc), 0)
        self.assertEqual(report["checked"], 1)
        self.assertEqual(report["links_found"], 1)

    def test_backticks_in_destinations_do_not_hide_missing_paths_or_later_links(self):
        doc = self.document('[literal](`missing.md`)\n[later](absent.md)\n'
                            '`[example](ignored.md)`\n')
        report = self.report(self.run_tool(doc), 1)
        self.assertEqual(report["checked"], 2)
        self.assertEqual([x["destination"] for x in report["issues"]], ['`missing.md`', 'absent.md'])

    def test_fragments_queries_external_urls_and_zero_path_scope_are_explicit(self):
        doc = self.document('[heading](#missing)\n[web](https://example.invalid)\n'
                            '[mail](mailto:example@example.invalid)\n'
                            '[network](//example.invalid/path)\n'
                            '[file](../good.md?download=1#absent)\n')
        report = self.report(self.run_tool(doc), 0)
        self.assertEqual(report["checked"], 1)
        self.assertEqual(report["unverified_fragments"], 2)
        self.assertEqual(report["unverified_queries"], 1)
        self.assertEqual(report["skipped_external"], 3)
        empty = self.document("No link destinations.\n", "empty.md")
        output = self.run_tool(empty, json_output=False)
        self.assertEqual(output.returncode, 0)
        self.assertIn(b"No local path targets were checked", output.stdout)

    def test_missing_target_is_a_completed_finding_with_location(self):
        doc = self.document('# Routes\n\n[missing](<absent ñ 文.md>)\n')
        report = self.report(self.run_tool(doc), 1)
        self.assertTrue(report["complete"])
        self.assertEqual(report["checked"], 1)
        issue = report["issues"][0]
        self.assertEqual((issue["source"], issue["line"], issue["destination"]),
                         (doc, 3, 'absent ñ 文.md'))
        self.assertEqual(issue["kind"], "missing")
        output = self.run_tool(doc, json_output=False)
        self.assertEqual(output.returncode, 1)
        self.assertTrue(output.stdout.isascii())

    def test_outside_root_absolute_and_encoded_traversal_are_incomplete(self):
        targets = ('../../outside.md', '%2e%2e/%2e%2e/outside.md', '/good.md', 'C:/good.md',
                   '../good.md%20', '../good.md.', '../docs%20/routes.md', '../docs./routes.md',
                   '../docs./../good.md', '../absent./../good.md', './:x', '../a%3Ab',
                   '../a%3Fb', '../a%2Ab', '../a%22b', '../a%7Cb', '../%3Ca%3E')
        # These files really exist on POSIX; the policy must reject their spelling anyway.
        if os.name != 'nt':
            for name in ('good.md ', 'good.md.', 'a:b', 'a?b', 'a*b', 'a"b', 'a|b', '<a>'):
                (self.root / name).write_bytes(b'target')
        for target in targets:
            with self.subTest(target=target):
                doc = self.document('[bad](' + target + ')\n')
                report = self.report(self.run_tool(doc), 2)
                self.assertFalse(report["complete"])
                self.assertEqual(report["issues"][0]["kind"], "unsafe")

    def test_symlinks_and_hidden_parent_traversal_are_incomplete(self):
        try:
            (self.root / "link").symlink_to(self.root / "docs", target_is_directory=True)
            (self.root / "dangling").symlink_to(self.root / "absent")
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        for target in ('../link', '../dangling', '../link/../good.md'):
            with self.subTest(target=target):
                doc = self.document('[bad](' + target + ')\n')
                self.assertFalse(self.report(self.run_tool(doc), 2)["complete"])
        self.document('[real](../good.md)\n')
        self.assertFalse(self.report(self.run_tool('link/routes.md'), 2)["complete"])

    def test_unsupported_forms_cannot_report_a_complete_pass(self):
        forms = ('[ref][owner]\n[owner]: ../good.md\n', '[shortcut]\n',
                 '[nested](../some(file).md)\n', '[escaped](../good\\.md)\n',
                 '[bad](../bad%ZZ.md)\n', '[nested [label]](../good.md)\n',
                 '[multiline](\n../good.md)\n', '    [indented](../good.md)\n',
                 '<a href="../good.md">link</a>\n', '<https://example.invalid>\n')
        for text in forms:
            with self.subTest(text=text):
                report = self.report(self.run_tool(self.document(text)), 2)
                self.assertFalse(report["complete"])
                self.assertGreater(report["unsupported"], 0)

    def test_invalid_missing_nonregular_and_absolute_document_inputs(self):
        (self.root / "bad.md").write_bytes(b'\xff')
        for name in ('missing.md', 'bad.md', 'docs', str(self.root / 'good.md'), '../outside.md',
                     'good.md ', 'good.md.', 'docs./routes.md', 'a:b', 'a?b', 'a*b', 'a"b', 'a|b', '<a>'):
            with self.subTest(name=name):
                report = self.report(self.run_tool(name), 2)
                self.assertFalse(report["complete"])
                self.assertEqual(report["issues"][0]["kind"], "input")
                self.assertNotIn(str(self.root), json.dumps(report))

    def test_read_and_input_count_and_link_candidate_bounds(self):
        path = self.root / 'large.md'
        with path.open('wb') as stream:
            stream.truncate(4 * 1024 * 1024 + 1)
        self.report(self.run_tool('large.md'), 2)
        self.report(self.run_tool(*(['good.md'] * 257)), 2)
        doc = self.document('[file](../good.md)\n' * 4097)
        report = self.report(self.run_tool(doc), 2)
        self.assertFalse(report['complete'])
        self.assertEqual(report['checked'], 4096)

    def test_success_and_failure_preserve_files_modes_and_directory_contents(self):
        def inventory():
            return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mode)
                    for p in self.root.rglob('*') if p.is_file()}
        doc = self.document('[good](../good.md)\n')
        before = inventory()
        directories = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*'))
        self.report(self.run_tool(doc), 0)
        self.report(self.run_tool(doc, 'absent.md'), 2)
        self.assertEqual(before, inventory())
        self.assertEqual(directories, sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*')))
        self.assertFalse((SCRIPT.parent / '__pycache__').exists())

    def test_standalone_copy_has_no_other_skill_or_runtime_dependency(self):
        copied = self.root / 'standalone/check_links.py'
        copied.parent.mkdir()
        shutil.copy2(SCRIPT, copied)
        doc = self.document('[good](../good.md)\n')
        result = subprocess.run([sys.executable, '-B', str(copied), '--root', str(self.root), '--json', doc],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        self.assertEqual(self.report(result, 0)['checked'], 1)

    def test_document_change_during_read_is_incomplete(self):
        spec = importlib.util.spec_from_file_location('link_helper_under_test', SCRIPT)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        doc = self.document('[good](../good.md)\n')
        actual_fstat = os.fstat
        calls = 0

        def intervene(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                (self.root / doc).write_text('externally changed during reading\n', encoding='utf-8')
            return actual_fstat(descriptor)

        with patch.object(helper.os, 'fstat', side_effect=intervene):
            report = helper.check(str(self.root), [doc])
        self.assertFalse(report['complete'])
        self.assertEqual(report['issues'][0]['kind'], 'input')
        self.assertIn('changed', report['issues'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
