"""Parity checks: the Node.js fallbacks must match the Python helpers.

Each case runs the Python helper and the Node.js fallback on identical disposable inputs, then
compares exit status and standard output byte for byte. Failure messages are compared by their
leading label only. Parity is defined against Python 3.14; Python 3.11 is the oldest version
checked, and argument edge cases that changed in argparse after 3.11 run only on 3.14 or later.
A missing Node.js is skipped, not treated as passing.

Randomized cases use a fixed seed. Set GALLEON_PARITY_SEED to explore other inputs and
GALLEON_PARITY_ROUNDS to run more of them; a failure message names the seed to reproduce it.
"""
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPERS = {
    'inventory': ROOT / 'skills/audit/scripts/file_inventory',
    'tokens': ROOT / 'skills/charter/scripts/count_tokens',
    'collisions': ROOT / 'skills/scaffold/scripts/check_collisions',
    'links': ROOT / 'skills/sync/scripts/check_links',
}
NODE = shutil.which('node')
ARGPARSE_314 = sys.version_info >= (3, 14)
SEED = int(os.environ.get('GALLEON_PARITY_SEED', '1789'))
ROUNDS = int(os.environ.get('GALLEON_PARITY_ROUNDS', '1'))
# Long-assigned letters (Unicode 8 or earlier), so Unicode-version differences between Python
# and Node.js cannot cause failures; the folding of newer characters is a documented limit.
LETTERS = ''.join(chr(c) for start, end in (
    (0x41, 0x5a), (0x61, 0x7a), (0xc0, 0x24f), (0x370, 0x3ff), (0x400, 0x4ff), (0x531, 0x587),
    (0x10a0, 0x10c5), (0x13a0, 0x13f5), (0x13f8, 0x13fd), (0x1e00, 0x1fbc), (0x2160, 0x2188),
    (0x24b6, 0x24e9), (0xab70, 0xabbf), (0xfb00, 0xfb06), (0xff21, 0xff5a), (0x10400, 0x1044f))
    for c in range(start, end + 1) if chr(c).isprintable())
ENVIRONMENT = {k: v for k, v in os.environ.items() if k not in ('COLUMNS', 'FORCE_COLOR')}


def setUpModule():
    if sys.version_info < (3, 11):
        raise unittest.SkipTest('parity is checked on Python 3.11 or later')
    if not NODE:
        raise unittest.SkipTest('node is not installed')


def launchers(kind):
    base = HELPERS[kind]
    return {'python': [sys.executable, '-B', str(base) + '.py'], 'node': [NODE, str(base) + '.mjs']}


def symlink_or_skip(test, link, target, directory=False):
    try:
        link.symlink_to(target, target_is_directory=directory)
    except (OSError, NotImplementedError) as error:
        test.skipTest('symlinks are unavailable: ' + type(error).__name__)


class ParityCase(unittest.TestCase):
    kind = None

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def run_all(self, *args, cwd=None, help_text=False):
        """Run both runtimes, assert agreement with Python, and return Python's result."""
        results = {}
        for name, call in launchers(self.kind).items():
            results[name] = subprocess.run(call + [str(a) for a in args], capture_output=True,
                                           cwd=cwd or self.root, timeout=90, env=ENVIRONMENT)
        python, node = results['python'], results['node']
        expected = python.stdout
        if help_text:
            name = HELPERS[self.kind].name
            expected = expected.replace(name.encode() + b'.py', name.encode() + b'.mjs')
        with self.subTest(runtime='node', seed=SEED, args=[str(a)[:40] for a in args][:6]):
            self.assertEqual(node.returncode, python.returncode, (node.stdout, node.stderr))
            self.assertEqual(node.stdout, expected)
            self.assertTrue(node.stderr.isascii())
            # Error details differ, but their line endings must follow Python's platform.
            if os.name == 'nt':
                self.assertNotIn(b'\n', node.stderr.replace(b'\r\n', b''))
            else:
                self.assertNotIn(b'\r\n', node.stderr)
            self.assertEqual(node.stderr.split(b':')[0], python.stderr.split(b':')[0])
        return python


ARGUMENT_WORDS = ['--json', '--js', '--j', '--', '-', '', '-h', '--help', '--he', '-hh', '-hx', '-h=x',
                  '--json=1', '--parent', '--par', '--parent=', '--root', '--ro', '--root=.', '--baseline',
                  '--base', 'capture', 'compare', 'cap', 'x', 'a b', '-x', '-x y', '-1', '-1.5', '-.5',
                  '-1e3', '-1x', '-\u0663', '--=x', '-=x', '---', '--bogus', '-j', '--jsonx', '.', 'good.md']


@unittest.skipUnless(ARGPARSE_314, 'argument edge cases follow Python 3.14 argparse')
class ArgumentParity(ParityCase):
    """Command lines parse as Python 3.14 argparse parses them, including help and errors."""

    def setUp(self):
        super().setUp()
        (self.root / 'good.md').write_text('one two\n', encoding='utf-8')
        (self.root / 'x').write_text('x\n', encoding='utf-8')

    def check_all(self, kind, *args):
        self.kind = kind
        return self.run_all(*args, help_text=True)

    def test_help_abbreviations_and_dash_names(self):
        for args in (('-h',), ('--help',), ('--he',), ('-hx',), ('-h=x',), ('--js', 'good.md'),
                     ('--', '-h'), ('-1', 'good.md'), ('-x y',), ('--json', '-1x'), ('--bogus', '-h')):
            self.check_all('tokens', *args)
        for args in (('--par', '.', '--js', 'new'), ('--parent', '.', '-1'), ('--parent', '-x', 'new'),
                     ('--parent', '.', 'a', '--json', 'b'), ('--parent=', 'new'), ('--parent', '.', '--', '-h'),
                     ('--parent', '.', '-x y'), ('-hh',), ('--parent', '-1', 'new')):
            self.check_all('collisions', *args)
        for args in (('--ro', '.', 'good.md'), ('--root', '.', '-1'), ('--root=.', '--', '--json', 'good.md'),
                     ('good.md', '--root', '.', 'x')):
            self.check_all('links', *args)
        for args in (('-h',), ('capture', '-h'), ('compare', '--help'), ('cap', '--root', '.', 'x'),
                     ('capture', '--ro', '.', '--js', 'x'), ('--', 'capture', '--root', '.', 'x'),
                     ('compare', '--root', '.', '--base', 'b.json', 'extra'), ('--bogus', 'capture', '-h'),
                     ('capture', '--root', '.', '--', '--json')):
            self.check_all('inventory', *args)

    def test_random_command_lines(self):
        rng = random.Random(SEED)
        for kind in HELPERS:
            for _ in range(8 * ROUNDS):
                args = [rng.choice(ARGUMENT_WORDS) for _ in range(rng.randint(0, 6))]
                if kind == 'inventory' and rng.random() < 0.7:
                    args.insert(0, rng.choice(['capture', 'compare']))
                self.check_all(kind, *args)


class UnrecoverableArgumentBytes(unittest.TestCase):
    """Node.js cannot see invalid UTF-8 argument bytes, so it must refuse instead of guessing."""

    @unittest.skipIf(os.name == 'nt', 'POSIX argument bytes')
    def test_invalid_utf8_arguments_never_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            for kind, args in (('collisions', [b'--parent', b'.', b'\xff']), ('links', [b'--root', b'.', b'\xff.md']),
                               ('tokens', [b'\xff']), ('inventory', [b'capture', b'--root', b'.', b'\xff'])):
                run = subprocess.run(launchers(kind)['node'] + args, capture_output=True, cwd=temp, timeout=30)
                self.assertEqual((run.returncode, run.stdout), (2, b''), kind)
                self.assertIn(b'U+FFFD', run.stderr)
                python = subprocess.run(launchers(kind)['python'] + args, capture_output=True, cwd=temp, timeout=30)
                self.assertNotEqual(python.returncode, 0, kind)


class InventoryParity(ParityCase):
    kind = 'inventory'

    def setUp(self):
        super().setUp()
        (self.root / 'one.bin').write_bytes(b'\x00\xffold\n')
        (self.root / 'empty').write_bytes(b'')

    def baseline(self, *names):
        run = self.run_all('capture', '--root', self.root, '--json', *names)
        self.assertEqual(run.returncode, 0, run.stderr)
        (self.root / 'baseline.json').write_bytes(run.stdout)
        return json.loads(run.stdout)

    def test_capture_json_and_text_are_identical_with_duplicates_sorted_by_code_point(self):
        astral, bmp = '\U0001f600.txt', '\uff5e.txt'
        for name in (astral, bmp, 'space ñ 文.bin'):
            (self.root / name).write_bytes(b'x')
        data = self.baseline('one.bin', 'empty', 'one.bin', astral, bmp, 'space ñ 文.bin')
        self.assertEqual([f['path'] for f in data['files']],
                         ['empty', 'one.bin', 'space ñ 文.bin', bmp, astral])
        self.assertTrue(self.run_all('capture', '--root', self.root, 'one.bin', 'empty').stdout.isascii())

    def test_compare_reports_unchanged_changed_and_missing(self):
        self.baseline('one.bin', 'empty')
        self.assertEqual(self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json').returncode, 0)
        (self.root / 'one.bin').write_bytes(b'\x00\xffnew\n')
        (self.root / 'empty').unlink()
        run = self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json', '--json')
        self.assertEqual(run.returncode, 1)
        report = json.loads(run.stdout)
        self.assertEqual((report['changed'], report['missing']), (['one.bin'], ['empty']))
        self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json')

    def test_malformed_foreign_and_oversized_baselines_are_rejected(self):
        valid = self.baseline('one.bin')
        entry = valid['files'][0]
        variants = [dict(valid, **{k: v}) for k, v in
                    (('format', 'foreign'), ('version', True), ('version', 2), ('version', 1.0),
                     ('files', []), ('approval', 'x'))]
        variants += [dict(valid, files=valid['files'] * 2)]
        for key, value in (('size', True), ('size', -1), ('size', 1.5), ('sha256', 'nope'),
                           ('path', '../outside'), ('path', '.git/config'), ('path', 'bad\ud800')):
            variants.append(dict(valid, files=[dict(entry, **{key: value})]))
        raw = [json.dumps(v) for v in variants]
        raw += ['{"format":"x","format":"y"}', '{"version":NaN}', '{"version":' + '1' * 1000 + '}',
                '[]', '{', 'null', '', '\ufeff' + json.dumps(valid) + ' x']
        for text in raw:
            (self.root / 'baseline.json').write_text(text, encoding='utf-8')
            run = self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json')
            self.assertEqual((run.returncode, run.stdout), (2, b''), text[:60])
        (self.root / 'baseline.json').write_bytes(b'\xff\xfe')
        self.assertEqual(self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json').returncode, 2)
        (self.root / 'baseline.json').write_bytes(b' ' * (4 * 1024 * 1024 + 1))
        self.assertEqual(self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json').returncode, 2)

    def test_valid_baseline_with_bom_and_escaped_path_is_accepted(self):
        data = self.baseline('one.bin')
        text = json.dumps(data, indent=2)
        (self.root / 'baseline.json').write_text('\ufeff' + text, encoding='utf-8')
        self.assertEqual(self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json').returncode, 0)

    def test_invalid_capture_inputs_print_nothing_on_stdout(self):
        (self.root / 'dir').mkdir()
        for name in ('missing', 'dir', './one.bin', '../outside', 'a//b', '.git/config', 'nested/.GIT/config',
                     str(self.root / 'one.bin'), 'C:/file', 'a\\b'):
            run = self.run_all('capture', '--root', self.root, 'empty', name)
            self.assertEqual((run.returncode, run.stdout), (2, b''), name)
        self.assertEqual(self.run_all('capture', '--root', self.root / 'absent', 'empty').returncode, 2)

    def test_usage_errors_exit_two(self):
        for args in ((), ('bogus',), ('capture',), ('capture', '--root', self.root),
                     ('compare', '--root', self.root), ('capture', '--root', self.root, '--nope', 'empty'),
                     ('compare', '--root', self.root, '--baseline', 'b.json', 'extra')):
            self.assertEqual(self.run_all(*args).returncode, 2, args)

    def test_symlink_and_nonregular_files_are_incomplete(self):
        self.baseline('one.bin')
        (self.root / 'one.bin').unlink()
        (self.root / 'one.bin').mkdir()
        report = json.loads(self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json', '--json').stdout)
        self.assertFalse(report['complete'])
        (self.root / 'one.bin').rmdir()
        symlink_or_skip(self, self.root / 'one.bin', self.root / 'empty')
        symlink_or_skip(self, self.root / 'parent', self.root, directory=True)
        self.assertEqual(self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json').returncode, 2)
        self.assertEqual(self.run_all('capture', '--root', self.root, 'parent/empty').returncode, 2)
        self.assertEqual(self.run_all('compare', '--root', self.root, '--baseline', 'parent/baseline.json').returncode, 2)

    def test_work_bounds(self):
        with (self.root / 'large').open('wb') as stream:
            stream.truncate(64 * 1024 * 1024 + 1)
        self.assertEqual(self.run_all('capture', '--root', self.root, 'large').returncode, 2)
        self.assertEqual(self.run_all('capture', '--root', self.root, *(['empty'] * 257)).returncode, 2)
        names = []
        for number in range(257):
            (self.root / f'f{number}').write_bytes(b'')
            names.append(f'f{number}')
        self.assertEqual(self.run_all('capture', '--root', self.root, *names[:256]).returncode, 0)
        self.assertEqual(self.run_all('capture', '--root', self.root, *names).returncode, 2)

    def test_runs_leave_inputs_and_layout_unchanged(self):
        self.baseline('one.bin', 'empty')
        before = {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.root.iterdir()}
        self.run_all('capture', '--root', self.root, 'one.bin', 'empty')
        self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json')
        self.run_all('capture', '--root', self.root, 'empty', 'absent')
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.root.iterdir()})

    def test_random_names_capture_and_compare_identically(self):
        rng = random.Random(SEED)
        for _ in range(ROUNDS):
            names = []
            for _ in range(rng.randint(1, 256)):
                name = ''.join(rng.choice(LETTERS + ' -_.~') for _ in range(rng.randint(1, 6)))
                if name.strip('.') and name.casefold() != '.git' and '/' not in name:
                    (self.root / name).write_bytes(name.encode())
                    names.append(name)
            names = names or ['one.bin']
            data = self.baseline(*names)
            for name in rng.sample(names, min(5, len(names))):
                target = self.root / name
                if target.exists():
                    target.write_bytes(b'changed') if rng.random() < 0.5 else target.unlink()
            self.run_all('compare', '--root', self.root, '--baseline', 'baseline.json', '--json')
            for item in data['files']:
                (self.root / item['path']).unlink(missing_ok=True)

    def test_relative_root_resolves_against_working_directory(self):
        (self.root / 'sub').mkdir()
        (self.root / 'sub/f').write_bytes(b'data')
        run = self.run_all('capture', '--root', 'sub', '--json', 'f')
        self.assertEqual(json.loads(run.stdout)['files'][0]['path'], 'f')


class TokenParity(ParityCase):
    kind = 'tokens'

    def file(self, name, data):
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_reports_match_for_ordinary_empty_and_unicode_whitespace_files(self):
        files = [self.file('ordinary.md', b'one two three\n'), self.file('empty.md', b''),
                 self.file('space ñ 文.md', 'hello café\n'.encode()),
                 self.file('ws.md', 'a\xa0b\u3000c\x1dd\x85e\ufefff g\u2028h\n'.encode()),
                 self.file('bom.md', b'\xef\xbb\xbfone two\n'), self.file('only-bom.md', b'\xef\xbb\xbf')]
        for flag in ([], ['--json']):
            run = self.run_all(*flag, *files)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(run.stdout.isascii())
        report = json.loads(self.run_all('--json', *files).stdout)
        self.assertEqual([x['words'] for x in report['files']], [3, 0, 2, 7, 2, 0])
        self.assertIn('Not a model tokenizer', report['limitation'])

    def test_repeated_paths_are_not_double_counted(self):
        path = self.file('one.md', b'one two\n')
        report = json.loads(self.run_all('--json', path, path, path).stdout)
        self.assertEqual((len(report['files']), report['duplicate_paths_skipped']), (1, 2))

    def test_node_also_skips_hardlinked_aliases_like_python(self):
        path = self.file('one.md', b'one two\n')
        alias = self.root / 'alias.md'
        os.link(path, alias)
        call = launchers('tokens')['node'] + ['--json', str(path), str(alias)]
        report = json.loads(subprocess.run(call, capture_output=True, timeout=30).stdout)
        self.assertEqual(report['duplicate_paths_skipped'], 1)

    def test_failures_print_nothing_on_stdout(self):
        good = self.file('good.md', b'one\n')
        binary = self.file('bad.md', b'\xff\xfe')
        big = self.file('large.md', b'a' * (4 * 1024 * 1024 + 1))
        link = self.root / 'link.md'
        symlink_or_skip(self, link, good)
        for args in (('--json', good, self.root / 'missing.md'), ('--json', self.root), ('--json', binary),
                     (big,), (link,), tuple([good] * 33), (), ('--bogus', good)):
            run = self.run_all(*args)
            self.assertEqual((run.returncode, run.stdout), (2, b''), args)

    def test_size_bound_is_inclusive(self):
        exact = self.file('exact.md', b'a ' * (2 * 1024 * 1024))
        self.assertEqual(self.run_all('--json', exact).returncode, 0)
        self.assertEqual(self.run_all(*([exact] * 32)).returncode, 0)

    def test_random_text_counts_identically(self):
        pieces = ['word', 'é', '文字', '😀', ' ', '\t', '\n', '\r\n', '\x0b', '\x0c', '\x1c', '\x1f', '\x85',
                  '\xa0', '\u1680', '\u180e', '\u2000', '\u200a', '\u200b', '\u2028', '\u202f', '\u205f',
                  '\u3000', '\ufeff', '\x00', 'x-y']
        rng = random.Random(SEED)
        for round_number in range(ROUNDS):
            files = [self.file(f'r{round_number}-{n}.md',
                               ''.join(rng.choice(pieces) for _ in range(rng.randint(0, 60))).encode())
                     for n in range(32)]
            self.run_all('--json', *files)

    def test_inputs_are_preserved(self):
        path = self.file('state.md', b'work remains pending\n')
        before = (path.read_bytes(), path.stat().st_mode, sorted(self.root.iterdir()))
        self.run_all(path)
        self.assertEqual(before, (path.read_bytes(), path.stat().st_mode, sorted(self.root.iterdir())))


class CollisionParity(ParityCase):
    kind = 'collisions'

    def setUp(self):
        super().setUp()
        self.parent = self.root / 'siblings'
        self.parent.mkdir()

    def check(self, *names, parent=None, flags=('--json',), cwd=None):
        target = self.parent if parent is None else parent
        return self.run_all('--parent', target, *flags, *names, cwd=cwd)

    def test_clean_existing_and_absent_parents_match_and_stay_read_only(self):
        self.assertEqual(self.check('new-record.md', 'memory').returncode, 0)
        absent = self.root / 'new-parent/deeper'
        self.assertEqual(json.loads(self.check('work.md', parent=absent).stdout)['parent_exists'], False)
        self.assertFalse(absent.parent.exists())
        self.assertEqual(list(self.parent.iterdir()), [])
        self.check('work.md', parent=absent, flags=())

    def test_exact_equivalent_and_dangling_names_are_occupied(self):
        (self.parent / 'work.md').write_bytes(b'x')
        (self.parent / 'memory').mkdir()
        (self.parent / 'Readme.md').write_bytes(b'x')
        (self.parent / 'café').write_bytes(b'x')
        symlink_or_skip(self, self.parent / 'dangling', self.root / 'absent')
        run = self.check('work.md', 'memory', 'README.md', 'cafe\u0301', 'dangling', 'new')
        self.assertEqual(run.returncode, 1)
        kinds = [item['kind'] for item in json.loads(run.stdout)['occupied']]
        self.assertEqual(kinds, ['exact', 'exact', 'equivalent', 'equivalent', 'exact'])
        self.check('work.md', 'README.md', flags=())

    def test_multiple_equivalent_siblings_keep_code_point_order(self):
        for name in ('README.MD', 'Readme.md'):
            (self.parent / name).write_bytes(b'x')
        if len(list(self.parent.iterdir())) < 2:
            self.skipTest('case-insensitive filesystem')
        self.check('readme.md')

    def test_duplicate_proposals_in_every_folding_family(self):
        groups = [('work.md', 'work.md'), ('Memory', 'memory'), ('Straße', 'STRASSE'), ('Straẞe', 'strasse'),
                  ('ﬁle', 'FILE'), ('ǰ', 'j\u030c'), ('ΑΣ', 'ασ', 'ας'), ('ı', 'I'), ('ı', 'ı'),
                  ('İ', 'i\u0307'), ('Ꭰ', 'ꭰ'), ('\U00010400', '\U00010428'), ('K', 'k'),
                  ('\u200b.x', '.x'), ('ŉ', '\u02bcn')]
        for names in groups:
            with self.subTest(names=names):
                self.check(*names, parent=self.root / 'absent')

    def test_every_multi_character_fold_matches_python(self):
        sources = [chr(c) for c in range(0x80, 0x1fff0) if not 0xd800 <= c <= 0xdfff
                   and len(chr(c).casefold()) > 1 and chr(c).strip(' .') == chr(c)]
        names = []
        for char in sources:
            names += [char, char.casefold()]
        run = self.check(*names[:256], parent=self.root / 'absent')
        self.assertEqual(run.returncode, 1)
        self.assertGreater(len(json.loads(run.stdout)['duplicates']), 50)

    def test_cherokee_and_mixed_duplicate_groups_keep_python_order(self):
        self.check('ꭰ', 'Ꭰ', 'ᏸ', 'Ᏸ', 'a', 'A', 'ǅ', 'ǆ', 'Ω', 'ω', 'Ω', parent=self.root / 'absent')

    def test_random_names_and_siblings_match(self):
        rng = random.Random(SEED)
        alphabet = LETTERS + ' .-_~\u0301\u0307'
        for round_number in range(ROUNDS):
            parent = self.root / f'random{round_number}'
            parent.mkdir()
            for _ in range(rng.randint(0, 64)):
                name = ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 4)))
                try:
                    with open(parent / name, 'xb'):
                        pass
                except OSError:
                    pass
            names = [''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 4))) for _ in range(256)]
            self.check(*names, parent=parent)
            valid = [n for n in names if n.strip(' .') == n and n not in ('.', '..')]
            self.check(*valid[:256], parent=parent)

    @unittest.skipIf(os.name == 'nt', 'POSIX file-name bytes')
    def test_undecodable_sibling_names_match_python(self):
        try:
            with open(os.path.join(os.fsencode(self.parent), b'bad\xff'), 'xb'):
                pass
        except OSError:
            self.skipTest('this filesystem rejects names that are not valid UTF-8')
        self.check('new', 'bad')

    def test_portable_invalid_names_make_the_check_incomplete(self):
        names = ('a/b', 'a\\b', '.', '..', 'trailing.', 'trailing ', 'CON', 'nul.txt', 'Com1.log', 'LPT³',
                 'conin$', 'CONOUT$.txt', 'a:b', 'a?', 'a*', 'a"b', 'a|b', '<a>', '\x01bad', '', 'con .txt')
        for name in names:
            run = self.check(name)
            self.assertEqual(run.returncode, 2, name)
            self.assertFalse(json.loads(run.stdout)['complete'])
        for ok in ('com0', 'COM10', 'lpt', 'x.con', 'del\x7f'):
            self.assertEqual(self.check(ok).returncode, 0, ok)
        self.check('ok', 'a/b', 'CON')

    def test_unsafe_parents_are_incomplete(self):
        (self.root / 'file').write_bytes(b'x')
        symlink_or_skip(self, self.root / 'linked', self.parent, directory=True)
        for parent in (self.root / 'file', self.root / 'file/child', self.parent / '..' / 'other',
                       self.root / 'linked', self.root / 'linked/deeper', ''):
            self.assertEqual(self.check('new', parent=parent).returncode, 2, str(parent))

    def test_work_bounds_and_sibling_listing_limit(self):
        self.assertEqual(self.check(*(['new'] * 257)).returncode, 2)
        self.assertEqual(self.check(*[f'n{i}' for i in range(256)]).returncode, 0)
        for number in range(4096):
            (self.parent / f's{number}').write_bytes(b'')
        run = self.check('new')
        self.assertEqual((run.returncode, json.loads(run.stdout)['siblings_checked']), (0, 4096))
        (self.parent / 'one-more').write_bytes(b'')
        self.assertEqual(self.check('new').returncode, 2)

    def test_relative_parent_equals_form_and_text_output(self):
        (self.parent / 'space ñ 文').write_bytes(b'x')
        run = self.run_all('--parent', 'siblings', 'space ñ 文', cwd=self.root)
        self.assertEqual(run.returncode, 1)
        self.assertTrue(run.stdout.isascii())
        self.run_all('--parent=siblings', '--json', 'space ñ 文', cwd=self.root)
        self.run_all('--json', '--parent', 'siblings', 'new', 'space ñ 文', cwd=self.root)

    def test_usage_errors_exit_two_and_inputs_are_preserved(self):
        for args in ((), ('--json', 'x'), ('--parent', str(self.parent)), ('--parent',),
                     ('--parent', str(self.parent), '--nope', 'x')):
            self.assertEqual(self.run_all(*args).returncode, 2, args)
        (self.parent / 'kept').write_bytes(b'data')
        before = {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.parent.iterdir()}
        self.check('kept', 'new')
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mode) for p in self.parent.iterdir()})


class LinkParity(ParityCase):
    kind = 'links'

    def setUp(self):
        super().setUp()
        (self.root / 'docs').mkdir()
        (self.root / 'good.md').write_text('target\n', encoding='utf-8')
        (self.root / 'space ñ 文.md').write_text('target', encoding='utf-8')

    def doc(self, text, name='docs/routes.md'):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode('utf-8'))
        return name

    def links(self, *names, flags=('--json',)):
        return self.run_all('--root', self.root, *flags, *names)

    def report(self, text, code=None, name='docs/routes.md'):
        run = self.links(self.doc(text, name))
        if code is not None:
            self.assertEqual(run.returncode, code, run.stdout)
        return json.loads(run.stdout)

    def test_existing_targets_titles_and_duplicate_normalized_inputs(self):
        doc = self.doc('[file](../good.md)\n[dir](.)\n![image](<../space ñ 文.md>)\n'
                       '[encoded](../space%20%C3%B1%20%E6%96%87.md "title")\n[quoted](../good.md \'title\')\n'
                       '[self]()\n[up](../docs/./routes.md)\n')
        run = self.links(doc, doc, 'docs/../docs/routes.md')
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertEqual(json.loads(run.stdout)['files'], [doc])

    def test_title_separators_follow_python_whitespace_not_javascript(self):
        for sep in ('\x1c', '\x85', '\xa0', '\u2003', '\u3000', '\ufeff', ' \t '):
            self.report(f'[x](../good.md{sep}"title")\n', name='docs/ws.md')
            self.report(f'[x](<../good.md>{sep}"title")\n', name='docs/ws.md')
            self.report(f'[x]({sep}../good.md{sep})\n', name='docs/ws.md')

    def test_fences_inline_code_and_line_separators(self):
        texts = ['```md\n[m](absent.md)\n```\n[r](../good.md)\n', '~~~\n[m](absent.md)\n~~~\n',
                 '````\n```\n[m](absent.md)\n````\n[later](absent.md)\n', '   ```\n[m](absent.md)\n   ```\n',
                 '    ```\n[m](absent.md)\n', '```\n[m](absent.md)\n', '``` info\n[m](a.md)\n```\n[x](b.md)\n',
                 '```\n[m](a.md)\n``` trailing\n[x](b.md)\n```\n', '`[m](absent.md)` and `` `[m](absent.md)` ``\n[r](../good.md)\n',
                 '[literal](`missing.md`)\n[later](absent.md)\n`[example](ignored.md)`\n',
                 '```\r\n[m](a.md)\r\n```\r\n[x](b.md)\r\n', 'a\x0b```\n[m](a.md)\n```\n[x](b.md)\n',
                 '[a](b.md)\x0c[c](d.md)\n[e](f.md)\u2028[g](h.md)\x85[i](j.md)\r[k](l.md)\n',
                 '``unclosed [x](a.md)\n[y](b.md)\n', '```not a fence`\n[x](a.md)\n']
        for text in texts:
            with self.subTest(text=text[:40]):
                self.report(text)

    def test_missing_targets_report_line_source_and_destination(self):
        run = self.report('# Routes\n\n[missing](<absent ñ 文.md>)\n', 1)
        self.assertEqual((run['issues'][0]['line'], run['issues'][0]['kind']), (3, 'missing'))
        self.links(self.doc('[missing](absent.md)\n'), flags=())
        self.report('[a](x.md)\r\n[b](y.md)\r\n\r\n[c](z.md)\n')

    def test_fragments_queries_external_urls_and_scheme_like_targets(self):
        targets = ['#missing', 'https://example.invalid', 'mailto:example@example.invalid', '//example.invalid/path',
                   '../good.md?download=1#absent', '?x', '#', 'a:b', 'ab:c', 'a:../good.md', '1a:b', ':x', 'a://x/y',
                   'a://[::1]/x', 'a://[bad]/x', 'a://[x/y', 'a://x]/y', 'a://[v1.x]/y', 'a://u@[::1]:80/y',
                   'a://[::1%a%b]/x', 'a://[::1%25z]/x', 'a://[::1%]/x', 'a://[fe80::1%eth0]/x', 'a://[1.2.3.4]/x',
                   'a://\u2100/x', 'a://ex\uff0fample/x', '../good.md#a#b', '../good.md?a?b#c', '../good.md/', '../good.md/x',
                   'C:/good.md', 'c:\\good.md', 'HTTP://x', 'x+y.z-w:rest', '.', './', '..', '../docs']
        for target in targets:
            with self.subTest(target=target):
                self.report(f'[x](<{target}>)\n')
        self.report('\n'.join(f'[x]({t})' for t in ('#a', 'https://x.invalid', 'mailto:a@b', '../good.md?q#f')) + '\n')
        run = self.links(self.doc('No link destinations.\n', 'empty.md'), flags=())
        self.assertIn(b'No local path targets were checked', run.stdout)

    def test_percent_encoding_and_hidden_traversal(self):
        targets = ['../space%20%C3%B1%20%E6%96%87.md', '%2e%2e/good.md', '%2e%2e/%2e%2e/outside.md', '..%2fgood.md',
                   '../bad%ZZ.md', '../bad%.md', '../bad%2.md', '../%FF.md', '../%C3.md', '%C3é.md', '../a%00b.md',
                   '/good.md', '%2Fgood.md', '../../outside.md', '../good.md%20', '../%e6%96%87.md', '%']
        for target in targets:
            with self.subTest(target=target):
                self.report(f'[x](<{target}>)\n')
        unsafe = ('../good.md%20', '../good.md.', '../docs%20/routes.md', '../docs./routes.md',
                  '../docs./../good.md', '../absent./../good.md', './:x', '../a%3Ab',
                  '../a%3Fb', '../a%2Ab', '../a%22b', '../a%7Cb', '../%3Ca%3E')
        if os.name != 'nt':
            for name in ('good.md ', 'good.md.', 'a:b', 'a?b', 'a*b', 'a"b', 'a|b', '<a>'):
                (self.root / name).write_bytes(b'target')
        for target in unsafe:
            with self.subTest(unsafe=target):
                report = self.report(f'[x](<{target}>)\n', 2)
                self.assertFalse(report['complete'])
                self.assertEqual(report['issues'][0]['kind'], 'unsafe')
                self.assertEqual(report['issues'][0]['reason'], 'unsafe path spelling')

    def test_url_whitespace_control_characters_and_bare_destinations(self):
        for text in ('[x](<\t../good.md>)\n', '[x](<../go\rod.md>)\n', '[x](< ../good.md>)\n', '[x](<../good.md >)\n',
                     '[x](../good.md)', '[x](../good.md "a (b")\n', '[x](<../a(b).md>)\n', '[x](<>)\n', '[x]()\n',
                     '[x]( )\n', '[x](../good.md "t" extra)\n', '[x](../good.md"t")\n', '[x]("t")\n'):
            with self.subTest(text=text):
                self.report(text)

    def test_symlinks_and_unsafe_ancestry(self):
        symlink_or_skip(self, self.root / 'link', self.root / 'docs', directory=True)
        symlink_or_skip(self, self.root / 'dangling', self.root / 'absent')
        (self.root / 'plain').write_bytes(b'file')
        for target in ('../link', '../dangling', '../link/../good.md', '../plain/child', '../plain/..', '../good.md/..'):
            with self.subTest(target=target):
                self.report(f'[bad]({target})\n', name='docs/routes.md')
        self.doc('[real](../good.md)\n')
        self.assertEqual(self.links('link/routes.md').returncode, 2)
        self.assertEqual(self.links('dangling').returncode, 2)

    def test_unsupported_forms_cannot_report_a_complete_pass(self):
        forms = ['[ref][owner]\n[owner]: ../good.md\n', '[shortcut]\n', '[nested](../some(file).md)\n',
                 '[escaped](../good\\.md)\n', '[bad](../bad%ZZ.md)\n', '[nested [label]](../good.md)\n',
                 '[multiline](\n../good.md)\n', '    [indented](../good.md)\n', '\t[indented](../good.md)\n',
                 '<a href="../good.md">link</a>\n', '<https://example.invalid>\n', '<user@example.invalid>\n',
                 '<img src="x">\n', '</a>\n', '<abbr>x</abbr> [ok](../good.md)\n', '<aé> [ok](../good.md)\n',
                 '<imgé> [ok](../good.md)\n', '<a_b> [ok](../good.md)\n', '<a1> [ok](../good.md)\n', '<a-> [ok](../good.md)\n',
                 '1 < 2 and [ok](../good.md)\n', '<unclosed [x](../good.md)\n', '[unclosed\n', '\\[escaped](../good.md)\n',
                 '[label\nsplit](../good.md)\n', '[x](../good.md\n', '[x](<../good.md)\n']
        for text in forms:
            with self.subTest(text=text[:40]):
                self.report(text)

    def test_document_input_errors(self):
        (self.root / 'bad.md').write_bytes(b'\xff')
        (self.root / 'empty.md').write_bytes(b'')
        (self.root / 'bom.md').write_bytes(b'\xef\xbb\xbf[x](good.md)\n')
        symlink_or_skip(self, self.root / 'link', self.root / 'good.md')
        for name in ('missing.md', 'bad.md', 'docs', '.', './good.md', str(self.root / 'good.md'), '../outside.md',
                     'C:/x.md', 'a\\b.md', 'link', 'good.md/child', 'empty.md', 'bom.md', 'docs/../good.md', '',
                     'good.md ', 'good.md.', 'docs./routes.md', 'a:b', 'a?b', 'a*b', 'a"b', 'a|b', '<a>'):
            with self.subTest(name=name):
                self.links(name)
        self.links('good.md', 'missing.md', 'good.md', flags=())

    def test_bounds(self):
        with (self.root / 'large.md').open('wb') as stream:
            stream.truncate(4 * 1024 * 1024 + 1)
        self.assertEqual(self.links('large.md').returncode, 2)
        self.assertEqual(self.links(*(['good.md'] * 257)).returncode, 2)
        self.assertEqual(self.links(*(['good.md'] * 256)).returncode, 0)
        doc = self.doc('[file](../good.md)\n' * 4097)
        self.assertEqual(json.loads(self.links(doc).stdout)['checked'], 4096)
        self.report('[file](../good.md)\n' * 4096)
        self.report('[x](a.md)\n' * 3000 + '[bad nested [x]](a.md)\n' * 1200)
        self.report('[x\n' * 5000)
        two = [self.doc('[file](../good.md)\n' * 3000, f'docs/m{n}.md') for n in range(2)]
        self.links(*two)

    def test_root_errors_usage_errors_and_text_output(self):
        for root in (self.root / 'absent', self.root / 'good.md'):
            self.assertEqual(self.run_all('--root', root, '--json', 'good.md').returncode, 2)
        self.assertEqual(self.run_all('--root', '', '--json', 'good.md').returncode, 0)  # '' is the working directory
        self.assertEqual(self.run_all('--root', 'docs', '--json', 'routes.md', cwd=self.root).returncode, 2)
        self.doc('[x](../good.md)\n[y](absent.md)\n')
        self.run_all('--root=' + str(self.root), '--json', 'docs/routes.md')
        self.run_all('--root', 'docs', '--json', 'routes.md', cwd=self.root)
        for args in ((), ('--json', 'a.md'), ('--root', str(self.root)), ('--root',),
                     ('--root', str(self.root), '--nope', 'a.md')):
            self.assertEqual(self.run_all(*args).returncode, 2, args)

    def test_random_documents_report_identically(self):
        pieces = ['[x](', '[x]', '](', ')', '(', '<', '>', '`', '``', '```', '~~~', '\n', '\r\n', '\r', ' ', '    ',
                  '\t', '"t"', "'t'", '../good.md', 'absent.md', '../space ñ 文.md', '#f', '?q', '%20', '%ZZ', '%2e',
                  'a://[::1]/x', '\\', '[', ']', '\xa0', '\u2028', '\x85', '\x0b', 'é', '😀', 'http://x', '//x',
                  'C:/x', '/abs', '..', '.', '/', 'a:b', '<a href="x">', '<x@y>', '<https://x>', '!', '*']
        rng = random.Random(SEED)
        for round_number in range(ROUNDS):
            names = []
            for n in range(64):
                text = ''.join(rng.choice(pieces) for _ in range(rng.randint(0, 40)))
                text += ''.join(f'[l](<{rng.choice(pieces)}{rng.choice(pieces)}> "t")\n' for _ in range(3))
                names.append(self.doc(text, f'docs/r{round_number}-{n}.md'))
            self.links(*names)
            self.links(*names[:8], flags=())

    def test_inputs_are_preserved(self):
        doc = self.doc('[good](../good.md)\n')
        before = {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mode)
                  for p in self.root.rglob('*') if p.is_file()}
        self.links(doc)
        self.links(doc, 'absent.md')
        self.assertEqual(before, {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mode)
                                  for p in self.root.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
