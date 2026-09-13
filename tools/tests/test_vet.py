import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import vet_poses as P  # noqa: E402
import vetpixel as V  # noqa: E402
import cards  # noqa: E402

PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
EXPECTED_FRAMES = {'idle': 4, 'move': 6, 'tell': 3, 'fire': 3, 'intro': 8, 'die': 8}


class VetTests(unittest.TestCase):
    def test_clip_set(self):
        self.assertEqual(dict((k, len(v)) for k, v in P.CLIPS.items()), EXPECTED_FRAMES)

    def test_no_clip_name_is_a_prefix_of_another(self):
        names = list(P.CLIPS)
        for a in names:
            for b in names:
                self.assertFalse(a != b and b.startswith(a), (a, b))

    def test_frames_share_canvas_and_palette(self):
        for clip, frames in P.CLIPS.items():
            for i, f in enumerate(frames):
                V.R(f)
                self.assertEqual((len(f[0]), len(f)), P.CANVAS, (clip, i))
                V.image(f)

    def test_feet_on_bottom_row_when_standing(self):
        for clip in ('idle', 'move', 'tell', 'fire', 'intro'):
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
            self.assertGreater(got, pixels * 0.85, ('die', i))  # rotation resamples but must not clip

    def test_hitbox_matches_body(self):
        cols = [x for row in P.BASE for x, ch in enumerate(row) if ch != '.']
        self.assertLessEqual(P.HITBOX[0], min(cols) + 2)

    def test_cards(self):
        self.assertEqual(cards.boss_card(PROJECT).size, (427, 240))
        self.assertEqual(cards.win_pic(PROJECT).size, (115, 71))


if __name__ == '__main__':
    unittest.main()
