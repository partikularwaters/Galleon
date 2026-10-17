"""Deep check: random command lines parse the same in Python argparse and the Node.js ports."""
import sys

sys.dont_write_bytecode = True  # Importing the helpers must not leave bytecode in skills/.

import argparse
import contextlib
import importlib.util
import io
import os
import random
import unittest

from _node import ROOT, require_deep, run_node

HELPERS = {'tokens': 'skills/charter/scripts/count_tokens', 'collisions': 'skills/scaffold/scripts/check_collisions',
           'links': 'skills/sync/scripts/check_links', 'inventory': 'skills/audit/scripts/file_inventory'}
WORDS = ['--json', '--js', '--j', '--', '-', '', '-h', '--help', '--he', '--h', '-hh', '-hx', '-h=x', '-hjson',
         '--json=1', '--json=', '--parent', '--par', '--p', '--parent=', '--parent=x', '--pa=y', '--root', '--ro',
         '--r', '--root=z', '--baseline', '--base', '--b', '--b=q', 'capture', 'compare', 'cap', 'x', 'y', 'a b',
         '-x', '-x y', '-1', '-1.5', '-.5', '-1e3', '-1x', '-٣', '--=x', '-=x', '---', '--bogus', '--bogus=1',
         '-j', '-p', '--jsonx', '- x', '-h-', '--x y', '-hh=x', '-h-x', 'x=y', '-r', '--c']
WORDS += ['x', 'y', 'z w', 'b.md'] * 8 + ['--root', '--parent', '--json', '--baseline', '--ro', '--par'] * 4
CASES = int(os.environ.get('GALLEON_DEEP_CASES', '20000'))
SEED = int(os.environ.get('GALLEON_PARITY_SEED', '1789'))
NODE_BODY = '''
const out = data.map((argv) => {
  try {
    const values = parseArguments(argv);
    for (const key of Object.keys(values)) if (values[key] === null) delete values[key];
    return ["ok", values];
  } catch (error) {
    if (error instanceof HelpRequest) return ["help", error.message];
    if (error instanceof UsageError) return ["error"];
    throw error;
  }
});
process.stdout.write(JSON.stringify(out));
'''


class Done(Exception):
    pass


def python_outcome(module, argv, name):
    original = argparse.ArgumentParser.parse_args

    def stop(self, args=None, namespace=None):
        raise Done(vars(original(self, args, namespace)))
    argparse.ArgumentParser.parse_args = stop
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            module.main(argv)
    except Done as done:
        return ['ok', {k: v for k, v in done.args[0].items() if v is not None}]
    except SystemExit as exit:
        return ['help', out.getvalue().replace(name + '.py', name + '.mjs')] if exit.code == 0 else ['error']
    finally:
        argparse.ArgumentParser.parse_args = original
    raise AssertionError('main returned without parsing arguments')


@unittest.skipUnless(sys.version_info >= (3, 14), 'command-line parity follows Python 3.14 argparse')
class ArgumentParsingDeep(unittest.TestCase):
    def setUp(self):
        require_deep(self)
        self.columns = os.environ.pop('COLUMNS', None)
        self.addCleanup(lambda: self.columns is None or os.environ.__setitem__('COLUMNS', self.columns))

    def test_random_command_lines_parse_identically(self):
        rng = random.Random(SEED)
        for kind, base in HELPERS.items():
            with self.subTest(helper=kind, seed=SEED):
                path = ROOT / (base + '.py')
                spec = importlib.util.spec_from_file_location('deep_' + kind, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                saved, sys.argv[0] = sys.argv[0], str(path)
                try:
                    cases = [[rng.choice(WORDS) for _ in range(rng.randint(0, 7))] for _ in range(CASES)]
                    if kind == 'inventory':
                        cases = [([rng.choice(['capture', 'compare'])] if rng.random() < 0.7 else []) + c for c in cases]
                    expected = [python_outcome(module, case, path.stem) for case in cases]
                finally:
                    sys.argv[0] = saved
                actual = run_node(base + '.mjs', ['parseArguments', 'HelpRequest', 'UsageError'], NODE_BODY, cases)
                for case, want, got in zip(cases, expected, actual):
                    if want[0] == 'ok':
                        want[1].setdefault('json', False)
                        if kind == 'inventory':
                            want[1].setdefault('files', [])
                    self.assertEqual(got, want, case)


if __name__ == '__main__':
    unittest.main()
