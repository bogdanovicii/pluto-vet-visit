import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import tech_poses as P  # noqa: E402
import vetpixel as V  # noqa: E402

EXPECTED_FRAMES = {'idle': 4, 'move': 6, 'tell': 3, 'fire': 3, 'die': 6}
STANDING = ('idle', 'move', 'tell', 'fire')


class TechTests(unittest.TestCase):
    def test_clip_set(self):
        self.assertEqual(list(P.CLIPS), ['idle', 'move', 'tell', 'fire', 'die'])
        self.assertEqual(dict((k, len(v)) for k, v in P.CLIPS.items()), EXPECTED_FRAMES)

    def test_no_clip_name_is_a_prefix_of_another(self):
        names = list(P.CLIPS)
        for a in names:
            for b in names:
                self.assertFalse(a != b and b.startswith(a), (a, b))

    def test_frames_share_canvas_and_palette(self):
        self.assertEqual(P.CANVAS, (32, 32))
        for clip, frames in P.CLIPS.items():
            for i, f in enumerate(frames):
                V.R(f)
                self.assertEqual((len(f[0]), len(f)), P.CANVAS, (clip, i))
                for row in f:
                    self.assertTrue(set(row) <= set(V.PALETTE), (clip, i, row))
                V.image(f)

    def test_feet_on_bottom_row_when_standing(self):
        for clip in STANDING:
            for i, f in enumerate(P.CLIPS[clip]):
                self.assertEqual(V.lowest_opaque_row(f), P.CANVAS[1] - 1, (clip, i))

    def test_die_ends_lying_down(self):
        last = P.CLIPS['die'][-1]
        ys = [y for y, row in enumerate(last) if any(ch != '.' for ch in row)]
        xs = [x for row in last for x, ch in enumerate(row) if ch != '.']
        self.assertGreater(max(xs) - min(xs), max(ys) - min(ys))  # wider than tall: lying down
        self.assertEqual(V.lowest_opaque_row(last), P.CANVAS[1] - 1)

    def test_fall_frames_keep_the_whole_body(self):
        pixels = sum(ch != '.' for row in P.BASE for ch in row)
        for i, f in enumerate(P.CLIPS['die']):
            got = sum(ch != '.' for row in f for ch in row)
            self.assertGreaterEqual(got, pixels * 0.85, ('die', i))  # rotation resamples but must not clip

    def test_hitbox_inside_body_columns(self):
        x, y, w, h = P.HITBOX
        body = P.region(P.BASE, 0, 0, P.ARM_BOX[0], P.CANVAS[1])  # the body column without the arm + syringe
        cols = [c for row in body for c, ch in enumerate(row) if ch != '.']
        rows = [r for r, row in enumerate(body) if any(ch != '.' for ch in row)]
        self.assertGreaterEqual(x, min(cols))
        self.assertLessEqual(x + w, max(cols) + 1)
        self.assertEqual(y, 0)
        self.assertLessEqual(h, P.CANVAS[1] - min(rows))

    def test_shoot_point_inside_canvas_right_of_hitbox(self):
        sx, sy = P.SHOOT_POINT
        self.assertTrue(0 <= sx < P.CANVAS[0] and 0 <= sy < P.CANVAS[1])
        self.assertGreater(sx, P.HITBOX[0] + P.HITBOX[2])
        self.assertNotEqual(P.BASE[P.CANVAS[1] - 1 - sy][sx], '.')  # the needle tip is a drawn pixel


if __name__ == '__main__':
    unittest.main()
