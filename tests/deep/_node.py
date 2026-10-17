"""Shared setup for the opt-in deep checks: load Node.js helper functions without running them."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
NODE = shutil.which('node')
ENTRY = 'process.exitCode = main(process.argv.slice(2));'


def require_deep(test):
    if os.environ.get('GALLEON_DEEP') != '1':
        raise unittest.SkipTest('deep checks run only with GALLEON_DEEP=1')
    if not NODE:
        raise unittest.SkipTest('node is not installed')


def run_node(script, exports, body, data):
    """Import names from a helper script into a Node.js program, feed it JSON, and return JSON."""
    source = (ROOT / script).read_text(encoding='utf-8')
    if source.count(ENTRY) != 1:
        raise AssertionError(f'{script} no longer ends with its expected entry line')
    with tempfile.TemporaryDirectory() as temp:
        module = Path(temp, 'helper.mjs')
        module.write_text(source.replace(ENTRY, 'export { ' + ', '.join(exports) + ' };'), encoding='utf-8')
        program = Path(temp, 'run.mjs')
        program.write_text('import fs from "node:fs";\n'
                           f'import {{ {", ".join(exports)} }} from "./helper.mjs";\n'
                           'const data = JSON.parse(fs.readFileSync(0, "utf8"));\n'
                           + body, encoding='utf-8')
        run = subprocess.run([NODE, str(program)], input=json.dumps(data), capture_output=True,
                             text=True, encoding='utf-8', timeout=600)
    if run.returncode:
        raise AssertionError(run.stderr)
    return json.loads(run.stdout)
