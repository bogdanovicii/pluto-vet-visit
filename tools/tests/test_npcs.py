import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import npc_poses as N  # noqa: E402
import vetpixel as V  # noqa: E402

EXPECTED = {
    'bogdan': ((48, 40), {'idle': 2, 'walk': 6, 'walk_free': 6}),
    'bianca': ((48, 40), {'idle': 2, 'walk': 6, 'wave': 4}),
    'receptionist': ((32, 40), {'idle': 2, 'talk': 2}),
    'rex': ((24, 24), {'idle': 2}),
    'grandma': ((24, 24), {'loaf': 2}),
}


def count(frame, keys):
    return sum(ch in keys for r in frame for ch in r)


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

    def test_frames_keep_their_outline_and_a_margin(self):
        for who, spec in N.NPCS.items():
            w, _ = spec['canvas']
            for clip, frames in spec['clips'].items():
                for i, f in enumerate(frames):
                    self.assertTrue(any('o' in row for row in f), (who, clip, i))
                    self.assertTrue(all(r[0] == '.' and r[w - 1] == '.' for r in f), (who, clip, i))

    def test_no_accidental_consecutive_duplicates(self):
        for who, spec in N.NPCS.items():
            for clip, frames in spec['clips'].items():
                for i in range(1, len(frames)):
                    self.assertNotEqual(frames[i - 1], frames[i], (who, clip, i))

    def test_bogdan_carries_the_carrier_in_and_walks_out_empty_handed(self):
        walk, free = N.CLIPS_BOGDAN['walk'], N.CLIPS_BOGDAN['walk_free']
        for a, b in zip(walk, free):
            self.assertNotEqual(a, b)
            self.assertLess(count(b, '|'), count(a, '|'))
            self.assertEqual(count(a, '_'), count(N.CARRIER, '_'))     # the carrier's barred door is whole in every frame
            self.assertEqual(count(b, '_'), 0)

    def test_the_owners_read_as_described(self):
        bogdan, bianca = N.BOGDAN_BASE, N.BIANCA_BASE
        self.assertGreater(count(bogdan, 'O"\''), 150)             # navy hoodie
        self.assertGreater(count(bogdan, '|/2'), 50)               # jeans
        self.assertGreater(count(bogdan, 'X@'), 30)                # dark brown hair
        self.assertEqual(count(bogdan, ':Aa'), 0)
        self.assertGreater(count(bianca, ':Aa'), 110)              # yellow sweater dress
        self.assertGreater(count(bianca, 'M'), 10)                 # the highlight in her hair
        self.assertEqual(count(bianca, 'O"\''), 0)
        hair_rows = [y for y, r in enumerate(bianca) if 'm' in r]
        self.assertGreater(max(hair_rows), 18)                     # long: past the shoulders (row 14)

    def test_bianca_waves_towards_pluto(self):
        # she stands right of Pluto: the wave faces left (mirrored), the walk and idle face right like everyone else
        for f in N.CLIPS_BIANCA['wave']:
            self.assertEqual(f, N.mirror(N.mirror(f)))
            eye_cols = [x for x, ch in enumerate(f[9]) if ch == 'K']
            face_cols = [x for x, ch in enumerate(f[9]) if ch != '.']
            self.assertLess(sum(eye_cols) / len(eye_cols), sum(face_cols) / len(face_cols))
            self.assertGreater(sum(r.count('=') for r in f[3:9]), 4)   # the raised hand is above her eyes
        right = N.BIANCA_BASE[9]
        self.assertGreater(right.index('K'), (right.index('o') + right.rindex('o')) / 2)

    def test_write_paths(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            paths = N.write(d)
        self.assertEqual(len(paths), sum(n for _, clips in EXPECTED.values() for n in clips.values()))
        rel = [os.path.relpath(p, d) for p in paths]
        self.assertIn(os.path.join('Resources', 'Npcs', 'bogdan', 'walk', 'bogdan_walk_001.png'), rel)
        self.assertIn(os.path.join('Resources', 'Npcs', 'bianca', 'wave', 'bianca_wave_004.png'), rel)
        self.assertIn(os.path.join('Resources', 'Npcs', 'grandma', 'loaf', 'grandma_loaf_002.png'), rel)


if __name__ == '__main__':
    unittest.main()
