import os
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import art_sources as A  # noqa: E402


def _img(path, size, colour=(10, 20, 30, 255), alpha=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    for x in range(size[0] // 2, size[0]):
        for y in range(size[1]):
            im.putpixel((x, y), colour if alpha is None else colour[:3] + (alpha,))
    im.save(path)


class ArtSourcesTests(unittest.TestCase):
    def test_every_piece_installs_under_resources(self):
        for name, p in A.PIECES.items():
            self.assertTrue(p['dest'].startswith('Resources/'), name)
            self.assertIn(p['kind'], ('sprite', 'card', 'picture'), name)
            self.assertEqual(len(A.source_paths(name)), p['frames'] or 1, name)

    def test_expected_pieces(self):
        for name in ('vet_bosscard', 'past_win_pic', 'breach_trophy', 'bianca_kneel', 'bianca_carry',
                     'bianca_carry_walk', 'bogdan_pat', 'vet_mask_on', 'vet_mask_idle', 'vet_mask_move',
                     'vet_mask_tell', 'vet_mask_fire', 'vet_mask_die', 'kennel_cat_idle', 'kennel_dog_react',
                     'kennel_open_l_rattle'):
            self.assertIn(name, A.PIECES)

    def test_check_passes_a_good_sprite_and_install_copies_it(self):
        with tempfile.TemporaryDirectory() as root:
            piece = 'breach_trophy'
            for src in A.source_paths(piece):
                _img(os.path.join(root, src), A.PIECES[piece]['canvas'])
            self.assertEqual(A.check(piece, root), [])
            written = A.install(root)
            self.assertTrue(all(os.path.exists(p) for p in A.dest_paths(root, piece)))
            self.assertTrue(any(p.endswith('breach_trophy.png') for p in written))

    def test_check_rejects_semi_transparent_pixels(self):
        with tempfile.TemporaryDirectory() as root:
            piece = 'breach_trophy'
            _img(os.path.join(root, A.source_paths(piece)[0]), A.PIECES[piece]['canvas'], alpha=128)
            self.assertTrue(any('alpha' in p for p in A.check(piece, root)))

    def test_check_rejects_wrong_canvas(self):
        with tempfile.TemporaryDirectory() as root:
            piece = 'breach_trophy'
            _img(os.path.join(root, A.source_paths(piece)[0]), (7, 7))
            self.assertTrue(any('canvas' in p for p in A.check(piece, root)))

    def test_card_left_of_x190_must_be_transparent(self):
        with tempfile.TemporaryDirectory() as root:
            piece = 'vet_bosscard'
            path = os.path.join(root, A.source_paths(piece)[0])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im = Image.new('RGBA', A.PIECES[piece]['canvas'], (0, 0, 0, 0))
            im.putpixel((10, 10), (255, 0, 0, 255))
            im.save(path)
            self.assertTrue(any('x < 190' in p for p in A.check(piece, root)))

    def test_picture_must_be_opaque(self):
        with tempfile.TemporaryDirectory() as root:
            piece = 'past_win_pic'
            _img(os.path.join(root, A.source_paths(piece)[0]), A.PIECES[piece]['canvas'])
            self.assertTrue(any('opaque' in p for p in A.check(piece, root)))

    def test_missing_sources_are_skipped_by_install(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(A.install(root), [])
            self.assertTrue(len(A.missing(root)) > 0)
