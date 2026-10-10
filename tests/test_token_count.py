"""Process checks for the public read-only estimator; no third-party packages."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/charter/scripts/count_tokens.py"


class TokenCountChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def file(self, name, data):
        path = self.root / name
        path.write_bytes(data)
        return path

    def run_tool(self, *args, restrictive=False):
        env = dict(os.environ)
        if restrictive:
            env["PYTHONIOENCODING"] = "cp1252:strict"
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

    def test_report_labels_estimate_and_handles_empty_file(self):
        ordinary = self.file("ordinary.md", b"one two three\n")
        empty = self.file("empty.md", b"")
        result = self.run_tool("--json", ordinary, empty)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual([x["estimated_tokens"] for x in report["files"]], [4, 0])
        self.assertEqual(report["read_set_estimated_tokens"], 4)
        self.assertIn("Not a model tokenizer", report["limitation"])

    def test_input_bytes_modes_and_directory_contents_are_preserved(self):
        path = self.file("state.md", b"work remains pending\n")
        before = (path.read_bytes(), path.stat().st_mode, sorted(self.root.iterdir()))
        result = self.run_tool(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, (path.read_bytes(), path.stat().st_mode, sorted(self.root.iterdir())))
        self.assertFalse((SCRIPT.parent / "__pycache__").exists())

    def test_duplicates_and_hardlinks_are_not_double_counted(self):
        path = self.file("one.md", b"one two\n")
        alias = self.root / "alias.md"
        os.link(path, alias)
        result = self.run_tool("--json", path, path, alias)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(len(report["files"]), 1)
        self.assertEqual(report["duplicate_paths_skipped"], 2)

    def test_unicode_path_roundtrips_under_restrictive_output(self):
        path = self.file("space ñ 文.md", "hello café\n".encode("utf-8"))
        result = self.run_tool("--json", path, restrictive=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["files"][0]["path"], str(path))
        self.assertTrue(result.stdout.isascii())
        self.assertEqual(self.run_tool(path, restrictive=True).returncode, 0)

    def test_missing_file_does_not_print_partial_success(self):
        path = self.file("good.md", b"one\n")
        result = self.run_tool("--json", path, self.root / "missing.md")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr.startswith(b"ERROR:"))

    def test_nonregular_and_invalid_inputs_are_rejected(self):
        binary = self.file("bad.md", b"\xff\xfe")
        for target in (self.root, binary):
            with self.subTest(target=target.name):
                result = self.run_tool("--json", target)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
        link = self.root / "link.md"
        try:
            link.symlink_to(binary)
        except (OSError, NotImplementedError):
            return
        self.assertEqual(self.run_tool(link).returncode, 2)

    def test_file_and_path_count_bounds_are_errors_not_migration_gates(self):
        big = self.file("large.md", b"a" * (4 * 1024 * 1024 + 1))
        self.assertEqual(self.run_tool(big).returncode, 2)
        small = self.file("small.md", b"one\n")
        self.assertEqual(self.run_tool(*([small] * 33)).returncode, 2)
        self.assertEqual(self.run_tool().returncode, 2)


if __name__ == "__main__":
    unittest.main()
