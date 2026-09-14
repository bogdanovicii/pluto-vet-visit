import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import nurse_poses as N  # noqa: E402
import vet_poses as P  # noqa: E402
import vetpixel as V  # noqa: E402

EXPECTED_FRAMES = {'idle': 4, 'move': 6, 'tell': 3, 'fire': 3, 'net': 4, 'die': 8}
STANDING = ('idle', 'move', 'tell', 'fire', 'net')


def opaque_cols(rows):
    return [x for row in rows for x, ch in enumerate(row) if ch != '.']


class NurseTests(unittest.TestCase):
    def test_clip_set(self):
        self.assertEqual(list(N.CLIPS), list(EXPECTED_FRAMES))
        self.assertEqual(dict((k, len(v)) for k, v in N.CLIPS.items()), EXPECTED_FRAMES)

    def test_no_clip_name_is_a_prefix_of_another(self):
        names = list(N.CLIPS)
        for a in names:
            for b in names:
                self.assertFalse(a != b and b.startswith(a), (a, b))

    def test_frames_share_canvas_and_palette(self):
        self.assertEqual(N.CANVAS, P.CANVAS)
        for clip, frames in N.CLIPS.items():
            for i, f in enumerate(frames):
                V.R(f)
                self.assertEqual((len(f[0]), len(f)), N.CANVAS, (clip, i))
                self.assertTrue(all(ch in V.PALETTE for row in f for ch in row), (clip, i))
                V.image(f)

    def test_feet_on_bottom_row_when_standing(self):
        for clip in STANDING:
            for i, f in enumerate(N.CLIPS[clip]):
                self.assertEqual(V.lowest_opaque_row(f), N.CANVAS[1] - 1, (clip, i))

    def test_die_ends_lying_down(self):
        last = N.CLIPS['die'][-1]
        ys = [y for y, row in enumerate(last) if any(ch != '.' for ch in row)]
        xs = opaque_cols(last)
        self.assertGreater(max(xs) - min(xs), max(ys) - min(ys))  # wider than tall: lying down
        self.assertEqual(V.lowest_opaque_row(last), N.CANVAS[1] - 1)

    def test_fall_frames_keep_the_whole_body(self):
        pixels = sum(ch != '.' for row in N.BASE for ch in row)
        for i, f in enumerate(N.CLIPS['die']):
            got = sum(ch != '.' for row in f for ch in row)
            self.assertGreater(got, pixels * 0.85, ('die', i))  # rotation resamples but must not clip

    def test_hitbox_within_body_columns(self):
        x, y, w, h = N.HITBOX
        body = opaque_cols(V.strip_outline(N.BODY))       # the body column, not the syringe or the net
        self.assertGreaterEqual(x, min(body))
        self.assertLessEqual(x + w, max(body) + 1)
        self.assertGreater(w, 0)
        self.assertGreater(h, 0)
        self.assertEqual(y, 0)
        self.assertLessEqual(y + h, N.CANVAS[1])

    def test_shoot_point_is_the_needle_tip_right_of_the_hitbox(self):
        sx, sy = N.SHOOT_POINT
        self.assertTrue(0 <= sx < N.CANVAS[0] and 0 <= sy < N.CANVAS[1])
        self.assertGreater(sx, N.HITBOX[0] + N.HITBOX[2])
        row = N.CANVAS[1] - 1 - sy                        # SHOOT_POINT is measured from the lower-left
        self.assertEqual(N.BASE[row][sx], '%')            # steel needle
        self.assertTrue(all(ch in '.o' for ch in N.BASE[row][sx + 1:]))  # nothing drawn beyond the tip

    def test_exported_frames_have_no_outline(self):
        for clip, frames in N.CLIPS.items():
            for f in frames:
                self.assertNotIn('o', ''.join(V.strip_outline(f)), clip)


if __name__ == '__main__':
    unittest.main()
