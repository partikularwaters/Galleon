"""Deep checks: the collision fallback folds names and decodes name bytes as Python does."""
import os
import random
import unicodedata
import unittest

from _node import require_deep, run_node

SCRIPT = 'skills/scaffold/scripts/check_collisions.mjs'
SEED = int(os.environ.get('GALLEON_PARITY_SEED', '1789'))


class UnicodeAndBytesDeep(unittest.TestCase):
    def setUp(self):
        require_deep(self)

    def test_folding_key_matches_casefold_for_characters_both_runtimes_assign(self):
        points = [c for c in range(0x110000)
                  if not 0xd800 <= c <= 0xdfff and unicodedata.category(chr(c)) != 'Cn']
        body = '''
const keep = data.filter((c) => !/\\p{Cn}/u.test(String.fromCodePoint(c)));
process.stdout.write(JSON.stringify(keep.map((c) => [c, key(String.fromCodePoint(c))])));
'''
        pairs = run_node(SCRIPT, ['key'], body, points)
        self.assertGreater(len(pairs), 280000)
        differ = [hex(c) for c, got in pairs if got != unicodedata.normalize('NFC', chr(c)).casefold()]
        self.assertEqual(differ, [], f'Python Unicode {unicodedata.unidata_version}')

    def test_name_bytes_decode_as_python_surrogate_escapes(self):
        rng = random.Random(SEED)
        pool = [0x41, 0x7f, 0x80, 0xbf, 0xc0, 0xc1, 0xc2, 0xdf, 0xe0, 0xed, 0xef, 0xf0, 0xf4, 0xf5, 0xff,
                0x9f, 0xa0, 0x8f, 0x90]
        cases = [bytes(rng.choice(pool + [rng.randrange(256)]) for _ in range(rng.randint(0, 12)))
                 for _ in range(200000)]
        cases += [chr(c).encode('utf-8', 'surrogatepass') for c in range(0, 0x110000, 7)]
        body = '''
process.stdout.write(JSON.stringify(data.map((hex) => fsDecode(Buffer.from(hex, "hex")))));
'''
        decoded = run_node(SCRIPT, ['fsDecode'], body, [c.hex() for c in cases])
        differ = [c.hex() for c, got in zip(cases, decoded) if got != c.decode('utf-8', 'surrogateescape')]
        self.assertEqual(differ[:10], [])


if __name__ == '__main__':
    unittest.main()
