import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import vet_poses as P  # noqa: E402
import vetpixel as V  # noqa: E402
import cards  # noqa: E402

PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
EXPECTED_FRAMES = {'idle': 5, 'move': 6, 'tell': 4, 'fire': 4, 'intro': 8, 'die': 8}
STANDING = ('idle', 'move', 'tell', 'fire', 'intro')
GUN_KEYS = set('&%#k>*/K')     # steel, glass and vaccine: the syringe pistol, not the sleeve or hand


def opaque(rows):
    return {(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != '.'}


def luma(key):
    r, g, b, _ = V.PALETTE[key]
    return 0.299 * r + 0.587 * g + 0.114 * b


class VetTests(unittest.TestCase):
    def test_clip_set(self):
        self.assertEqual(list(P.CLIPS), ['idle', 'move', 'tell', 'fire', 'intro', 'die'])
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
                self.assertEqual({ch for row in f for ch in row} - set(V.PALETTE), set(), (clip, i))
                V.image(f)

    def test_no_identical_consecutive_frames(self):
        for clip, frames in P.CLIPS.items():
            loop = clip in ('idle', 'move')
            pairs = list(zip(frames, frames[1:])) + ([(frames[-1], frames[0])] if loop else [])
            for i, (a, b) in enumerate(pairs):
                self.assertNotEqual(a, b, (clip, i))

    def test_feet_on_bottom_row_when_standing(self):
        for clip in STANDING:
            for i, f in enumerate(P.CLIPS[clip]):
                self.assertEqual(V.lowest_opaque_row(f), P.CANVAS[1] - 1, (clip, i))

    def test_die_ends_lying_down(self):
        last = P.CLIPS['die'][-1]
        pts = opaque(last)
        xs, ys = [x for x, _ in pts], [y for _, y in pts]
        self.assertGreater(max(xs) - min(xs), 2 * (max(ys) - min(ys)))  # much wider than tall: lying down
        self.assertEqual(V.lowest_opaque_row(last), P.CANVAS[1] - 1)

    def test_die_frames_keep_the_whole_body(self):
        pixels = len(opaque(P.BASE))
        for i, f in enumerate(P.CLIPS['die']):
            self.assertGreater(len(opaque(f)), pixels * 0.7, ('die', i))  # rotation resamples but must not clip

    def test_fill_keeps_a_margin_for_the_runtime_outline(self):
        w, h = P.CANVAS
        for clip, frames in P.CLIPS.items():
            for i, f in enumerate(frames):
                self.assertTrue(all(row[0] == '.' and row[-1] == '.' for row in f), (clip, i))
                self.assertEqual(f[0], '.' * w, (clip, i))

    def test_no_drawn_outline(self):
        """The game outlines AIActors at runtime: no 'o', and the silhouette edge is not a ring of near-black pixels."""
        w, h = P.CANVAS
        for clip, frames in P.CLIPS.items():
            for i, f in enumerate(frames):
                exported = V.strip_outline(f)
                self.assertEqual(exported, f, (clip, i))                     # nothing to strip: no 'o' at all
                pts = opaque(f)
                edge = [(x, y) for x, y in pts
                        if any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
                dark = [p for p in edge if luma(f[p[1]][p[0]]) < 60]
                self.assertLess(len(dark), 0.5 * len(edge), (clip, i))

    def test_hitbox_covers_the_body_not_the_gun(self):
        w, h = P.CANVAS
        x, y, bw, bh = P.HITBOX
        self.assertTrue(0 <= x and x + bw <= w and 0 <= y and y + bh <= h)
        self.assertEqual(y, 0)                                              # from the shoe soles
        top_row = min(yy for _, yy in opaque(P.BASE))
        self.assertEqual(h - (y + bh), top_row)                             # to the top of the quiff
        inside = lambda px, py: x <= px < x + bw and h - (y + bh) <= py < h - y
        body = opaque(P.BODY) | {(P.BACK_AT[0] + bx, P.BACK_AT[1] + by) for bx, by in opaque(P.BACK_ARM)}
        covered = sum(inside(px, py) for px, py in body)
        self.assertGreater(covered, 0.9 * len(body))                       # the hem flare and the coat edge behind the arm may stick out
        gun = [(P.GUN_AT[0] + gx, P.GUN_AT[1] + gy) for gx, gy in opaque(P.GUN) if P.GUN[gy][gx] in GUN_KEYS]
        self.assertTrue(gun)
        self.assertFalse([p for p in gun if inside(*p)])

    def test_shoot_point_is_the_needle_tip(self):
        w, h = P.CANVAS
        sx, sy = P.SHOOT_POINT
        row = h - 1 - sy                                                    # SHOOT_POINT is measured from the lower-left
        self.assertEqual((sx, row), (P.GUN_AT[0] + P.NEEDLE_TIP[0], P.GUN_AT[1] + P.NEEDLE_TIP[1]))
        self.assertIn(P.BASE[row][sx], '&K')                                # an opaque needle pixel
        self.assertEqual(P.BASE[row].rstrip('.'), P.BASE[row][:sx + 1])     # the rightmost pixel of its row

    def test_write_removes_stale_frames(self):
        with tempfile.TemporaryDirectory() as d:
            stale = os.path.join(d, 'Resources', 'Boss', 'vet', 'idle', 'vet_idle_099.png')
            os.makedirs(os.path.dirname(stale))
            open(stale, 'wb').close()
            paths = P.write(d)
            self.assertFalse(os.path.exists(stale))
            for clip, frames in P.CLIPS.items():
                files = sorted(os.listdir(os.path.join(d, 'Resources', 'Boss', 'vet', clip)))
                self.assertEqual(files, ['vet_%s_%03d.png' % (clip, i) for i in range(1, len(frames) + 1)])
            self.assertEqual(len(paths), sum(EXPECTED_FRAMES.values()))

    def test_legacy_parts_for_the_owner_npc(self):
        for rows in (P.LEGS_A, P.LEGS_B):
            self.assertEqual((len(rows[0]), len(rows)), (32, 8))
        self.assertEqual((P.DX, P.LEG_ROWS), (8, (32, 40)))

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
                         {'vet_syringe_001': (14, 6), 'vet_dart_001': (13, 5), 'vet_vaccine_001': (8, 8), 'vet_droplet_001': (9, 7),
                          'vet_tranq_001': (7, 7), 'vet_pill_001': (10, 6), 'vet_tablet_001': (7, 7), 'vet_scalpel_001': (14, 5),
                          'vet_stitch_001': (9, 9), 'vet_net_001': (14, 14), 'vet_cloud_001': (16, 16)})
        for rows in PR.SPRITES.values():
            V.R(rows)
            V.image(rows)


if __name__ == '__main__':
    unittest.main()
