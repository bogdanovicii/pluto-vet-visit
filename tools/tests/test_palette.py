import inspect
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import cards  # noqa: E402
import clinic_objects as CO  # noqa: E402
import projectiles as PR  # noqa: E402
import vet_poses as VP  # noqa: E402
import vetpixel as V  # noqa: E402

# cards.py has no ASCII map of its own, but it indexes V.PALETTE directly (e.g. V.PALETTE['_']).
_CARDS_PALETTE_KEY_RE = re.compile(r"""V\.PALETTE(?:\.get)?\[?\(?['"](.)['"]""")


def _add_chars(rows, keys):
    for row in rows:
        for ch in row:
            if ch != '.':
                keys.add(ch)


def used_keys():
    """Every non-'.' palette key referenced by an ASCII map in vet_poses.py, clinic_objects.py,
    projectiles.py or cards.py. Kept as a live scan (not a hardcoded list) so a future sprite that
    introduces a new key is caught by test_every_used_key_is_defined below."""
    keys = set()
    for name in ('POSE', 'LEGS_A', 'LEGS_B', 'BASE'):
        _add_chars(getattr(VP, name), keys)
    for frames in VP.CLIPS.values():
        for frame in frames:
            _add_chars(frame, keys)
    for obj in CO.OBJECTS:
        _add_chars(obj.rows, keys)
    if hasattr(CO, 'CUP'):
        _add_chars(CO.CUP, keys)
    for rows in PR.SPRITES.values():
        _add_chars(rows, keys)
    for match in _CARDS_PALETTE_KEY_RE.finditer(inspect.getsource(cards)):
        keys.add(match.group(1))
    return keys


class PaletteTests(unittest.TestCase):
    def test_every_used_key_is_defined(self):
        """Guards against art that references a palette key nobody defined (a typo, or a new
        sprite that forgot to add its key to vetpixel.PALETTE)."""
        missing = sorted(k for k in used_keys() if k not in V.PALETTE)
        self.assertEqual(missing, [],
                          'ASCII art uses palette key(s) missing from vetpixel.PALETTE: %r' % missing)

    def test_shared_keys_match_upstream_pixel_palette(self):
        """Guards against silent art drift: vetpixel.PALETTE is a deliberate snapshot of the main
        mod's ../tools/pixel.py palette (see the comment in vetpixel.py). If the main mod edits a
        shared key, our committed PNGs must NOT silently re-render; this test should fail instead,
        so a maintainer copies the new value over on purpose (or restores the old one upstream)."""
        main_tools = os.path.join(os.path.dirname(V.PROJECT), 'tools')
        if main_tools not in sys.path:
            sys.path.insert(0, main_tools)
        try:
            import pixel
        except ImportError:
            raise unittest.SkipTest('../tools/pixel.py is not importable (main mod not checked out here)')

        drifted = []
        for key in sorted(set(V.PALETTE) & set(pixel.PALETTE)):
            ours, theirs = V.PALETTE[key], pixel.PALETTE[key]
            if ours != theirs:
                drifted.append('%r: vetpixel.PALETTE=%r, pixel.PALETTE=%r' % (key, ours, theirs))
        self.assertEqual(drifted, [],
                          'vetpixel.PALETTE has drifted from ../tools/pixel.py:\n' + '\n'.join(drifted))


if __name__ == '__main__':
    unittest.main()
