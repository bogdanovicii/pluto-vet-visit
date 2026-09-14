import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import npc_poses as N  # noqa: E402
import vetpixel as V  # noqa: E402

EXPECTED = {
    'owner': ((48, 40), {'idle': 2, 'walk': 6, 'walk_free': 6}),
    'receptionist': ((32, 40), {'idle': 2, 'talk': 2}),
    'rex': ((24, 24), {'idle': 2}),
    'grandma': ((24, 24), {'loaf': 2}),
}


class NpcTests(unittest.TestCase):
    def test_cast_and_clip_sets(self):
        self.assertEqual(list(N.NPCS), list(EXPECTED))
        for who, spec in N.NPCS.items():
            canvas, clips = EXPECTED[who]
            self.assertEqual(spec['canvas'], canvas, who)
            self.assertEqual(dict((k, len(v)) for k, v in spec['clips'].items()), clips, who)

    def test_frames_share_canvas_and_palette(self):
        for who, spec in N.NPCS.items():
            w, h = spec['canvas']
            for clip, frames in spec['clips'].items():
                for i, f in enumerate(frames):
                    V.R(f)
                    self.assertEqual((len(f[0]), len(f)), (w, h), (who, clip, i))
                    V.image(f)  # raises KeyError on an unknown palette key

    def test_feet_on_bottom_row(self):
        for who, spec in N.NPCS.items():
            for clip, frames in spec['clips'].items():
                for i, f in enumerate(frames):
                    self.assertEqual(V.lowest_opaque_row(f), spec['canvas'][1] - 1, (who, clip, i))

    def test_frames_keep_their_outline(self):
        for who, spec in N.NPCS.items():
            for clip, frames in spec['clips'].items():
                for i, f in enumerate(frames):
                    self.assertTrue(any('o' in row for row in f), (who, clip, i))

    def test_walk_carries_the_carrier_and_walk_free_does_not(self):
        walk, free = N.CLIPS_OWNER['walk'], N.CLIPS_OWNER['walk_free']
        for a, b in zip(walk, free):
            self.assertNotEqual(a, b)
            self.assertLess(sum(ch == '|' for r in b for ch in r), sum(ch == '|' for r in a for ch in r))

    def test_write_paths(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            paths = N.write(d)
        self.assertEqual(len(paths), sum(n for _, clips in EXPECTED.values() for n in clips.values()))
        rel = [os.path.relpath(p, d) for p in paths]
        self.assertIn(os.path.join('Resources', 'Npcs', 'owner', 'walk', 'owner_walk_001.png'), rel)
        self.assertIn(os.path.join('Resources', 'Npcs', 'grandma', 'loaf', 'grandma_loaf_002.png'), rel)


if __name__ == '__main__':
    unittest.main()
