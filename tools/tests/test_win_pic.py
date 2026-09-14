"""The past's win picture (tools/win_pic.py): a hand-drawn happy ending at the vanilla photo size."""
import inspect
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import cards  # noqa: E402
import vetpixel as V  # noqa: E402
import win_pic as WP  # noqa: E402

PROJECT = os.path.dirname(os.path.dirname(HERE))


class WinPicTests(unittest.TestCase):
    def test_vanilla_photo_size_and_fully_opaque(self):
        # Alexandria's SetWinPic postfix only swaps photoSprite.Texture: the page scales a 115x71 photo.
        im = WP.image()
        self.assertEqual(im.size, (115, 71))
        self.assertEqual(im.getchannel('A').getextrema(), (255, 255))
        self.assertEqual(cards.win_pic(PROJECT).tobytes(), im.tobytes())

    def test_every_key_is_defined(self):
        rows = WP.scene()
        self.assertEqual({len(r) for r in rows}, {115})
        missing = sorted({ch for r in rows for ch in r if ch not in V.PALETTE})
        self.assertEqual(missing, [])

    def test_the_cast_is_in_the_picture(self):
        keys = {ch for r in WP.scene() for ch in r}
        for key, who in (('G', "Pluto's green eyes"), ('b', "Pluto's tail rings"), ('O', "Bogdan's navy hoodie"),
                         ('|', "Bogdan's jeans"), (':', "Bianca's yellow dress"), ('m', "Bianca's hair"),
                         ('$', "the Vet's scrubs"), ('H', 'hearts'), ('8', 'the lit doorway')):
            self.assertIn(key, keys, who)

    def test_hand_drawn_only(self):
        # no fallback ellipse / rectangle placeholders, no import of the main mod's character art at build time
        for module in (cards, WP):
            src = inspect.getsource(module)
            self.assertNotIn('character_anims', src)
            self.assertNotIn('ellipse(', src)
        self.assertNotIn('rectangle(', inspect.getsource(cards.win_pic))

    def test_corners_stay_quiet_under_the_tape(self):
        # the Ammonomicon tapes the photo's corners: no outline in the 4x4 corner squares
        rows = WP.scene()
        for x0, y0 in ((0, 0), (111, 0), (0, 67), (111, 67)):
            block = [rows[y][x] for y in range(y0, y0 + 4) for x in range(x0, x0 + 4)]
            self.assertNotIn('o', block, 'corner at (%d, %d)' % (x0, y0))


if __name__ == '__main__':
    unittest.main()
