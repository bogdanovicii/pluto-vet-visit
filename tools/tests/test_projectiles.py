"""0.12 projectile design rules: vanilla-sized, outlined, one sprite per family, hitboxes inside the art, and the C# bank
entries in src/*.cs matching tools/projectiles.py BANK exactly."""
import glob
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import projectiles as PR  # noqa: E402
import vetpixel as V  # noqa: E402

PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
ENTRY_RE = re.compile(r'VetBoss\.Entry\(kin, "(\w+)", "(\w+)", (\d+), (\d+), (\d+), (\d+), (true|false)\)|'
                      r'\bEntry\(kin, "(\w+)", "(\w+)", (\d+), (\d+), (\d+), (\d+), (true|false)\)')


def cs_entries():
    found = []
    for path in glob.glob(os.path.join(PROJECT, 'src', '*.cs')):
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
        for m in ENTRY_RE.finditer(text):
            g = [x for x in m.groups() if x is not None]
            found.append((os.path.basename(path), g[0], g[1], int(g[2]), int(g[3]), int(g[4]), int(g[5]), g[6] == 'true'))
    return found


class ProjectileArtTests(unittest.TestCase):
    def test_every_sprite_has_a_bank_name(self):
        self.assertEqual(sorted(s for s, _, _, _ in PR.BANK.values()), sorted(PR.SPRITES))

    def test_vanilla_sized(self):
        for name, rows in PR.SPRITES.items():
            w, h = len(rows[0]), len(rows)
            self.assertTrue(5 <= min(w, h) and max(w, h) <= 16, '%s is %dx%d' % (name, w, h))

    def test_outlined_with_a_bright_core(self):
        bright = {'K', 'W', '>', ']', '`', '&', '<'}
        for name, rows in PR.SPRITES.items():
            chars = {c for r in rows for c in r}
            self.assertIn('o', chars, name + ' has no outline')
            self.assertTrue(chars & bright, name + ' has no bright core')
            self.assertEqual(chars - set(V.PALETTE), set(), name)
            # every opaque edge pixel of the canvas is outline: nothing bleeds without a dark rim
            w, h = len(rows[0]), len(rows)
            for x in range(w):
                for y in (0, h - 1):
                    self.assertIn(rows[y][x], '.o', '%s edge pixel %d,%d' % (name, x, y))
            for y in range(h):
                for x in (0, w - 1):
                    self.assertIn(rows[y][x], '.o', '%s edge pixel %d,%d' % (name, x, y))

    def test_one_sprite_per_family(self):
        seen = {}
        for bank, (sprite, _, _, _) in PR.BANK.items():
            self.assertNotIn(sprite, seen, '%s and %s share %s' % (bank, seen.get(sprite), sprite))
            seen[sprite] = bank

    def test_hitbox_inside_the_art(self):
        for bank, (sprite, hw, hh, rotates) in PR.BANK.items():
            w, h = PR.size(sprite)
            self.assertTrue(3 <= hw < w and 3 <= hh <= h, '%s hitbox %dx%d vs sprite %dx%d' % (bank, hw, hh, w, h))
            if rotates:
                self.assertGreaterEqual(w, h, bank + ' points along travel, so it must be drawn facing right')

    def test_preview_sheet(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = PR.preview(tmp)
            self.assertTrue(os.path.exists(path))


class BankEntryTests(unittest.TestCase):
    def test_cs_entries_match_bank(self):
        entries = cs_entries()
        self.assertTrue(entries, 'no VetBoss.Entry calls found in src/*.cs')
        for f, bank, sprite, w, h, hw, hh, rotates in entries:
            self.assertIn(bank, PR.BANK, '%s: unknown bank %s' % (f, bank))
            self.assertEqual((sprite, hw, hh, rotates), PR.BANK[bank], '%s: bank %s' % (f, bank))
            self.assertEqual((w, h), PR.size(sprite), '%s: bank %s sprite size' % (f, bank))

    def test_every_bank_name_is_registered(self):
        self.assertEqual({e[1] for e in cs_entries()}, set(PR.BANK))

    def test_scripts_only_use_registered_banks(self):
        with open(os.path.join(PROJECT, 'src', 'VetAttacks.cs'), encoding='utf-8') as fh:
            src = fh.read()
        used = set(re.findall(r'base\("(\w+)", false, false, false\)', src))
        self.assertTrue(used)
        self.assertEqual(used - set(PR.BANK), set())
        self.assertEqual(set(PR.BANK) - used, set(), 'bank names no script fires')


if __name__ == '__main__':
    unittest.main()
