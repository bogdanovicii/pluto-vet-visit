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

    def test_boss_card_is_a_cut_out_in_the_right_half(self):
        # The game draws the player's card over the whole screen on top of the boss card: ours must leave the left empty.
        alpha = cards.boss_card(PROJECT).getchannel('A')
        self.assertIsNone(alpha.crop((0, 0, 190, 240)).getbbox())
        box = alpha.getbbox()
        self.assertIsNotNone(box)
        self.assertGreater(box[0], 190)                                 # the figure starts right of x 190
        self.assertGreaterEqual(box[3] - box[1], 180)                   # a large portrait, like the vanilla cards
        self.assertGreater(alpha.histogram()[0], 0.5 * 427 * 240)       # mostly transparent

    def test_boss_card_portrait_rows(self):
        import vet_card as VC
        rows = VC.PORTRAIT
        self.assertTrue(rows)
        self.assertEqual({len(r) for r in rows}, {len(rows[0])})       # rectangular
        unknown = {ch for r in rows for ch in r} - set(V.PALETTE)
        self.assertEqual(unknown, set())                                # palette keys only
        self.assertLessEqual(VC.ORIGIN[0] + len(rows[0]), 427)
        self.assertLessEqual(VC.ORIGIN[1] + len(rows), 240)

    def test_cards_do_not_use_gemini_images(self):
        import inspect
        self.assertNotIn('gemini', inspect.getsource(cards).split('"""', 2)[2].lower())

    def test_projectile_sprites(self):
        import projectiles as PR
        self.assertEqual({k: (len(v[0]), len(v)) for k, v in PR.SPRITES.items()},
                         {'vet_syringe_001': (12, 4), 'vet_droplet_001': (5, 5), 'vet_pill_001': (8, 4), 'vet_net_001': (12, 12),
                          'vet_cloud_001': (14, 14)})
        for rows in PR.SPRITES.values():
            V.R(rows)
            V.image(rows)


if __name__ == '__main__':
    unittest.main()
