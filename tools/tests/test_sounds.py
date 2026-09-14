import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sounds as S  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src')


class SoundTests(unittest.TestCase):
    def test_every_played_event_is_allowed(self):
        used = S.used_in_source()
        self.assertTrue(used, 'no ClinicSound.Play calls found')
        self.assertEqual(sorted(used - set(S.ALLOWED)), [])

    def test_the_design_moments_are_wired(self):
        used = S.used_in_source()
        for ev in ('Play_OBJ_door_open_01', 'Play_UI_menu_confirm_01', 'Play_UI_cooldown_ready_01',
                   'Play_OBJ_glassbottle_shatter_01', 'Play_OBJ_item_spawn_01', 'Play_ENM_deathray_charge_01'):
            self.assertIn(ev, used)

    def test_nothing_bypasses_clinic_sound(self):
        for name in os.listdir(SRC):
            if not name.endswith('.cs') or name == 'ClinicSound.cs':
                continue
            text = open(os.path.join(SRC, name), encoding='utf-8').read()
            self.assertIsNone(re.search(r'AkSoundEngine\.PostEvent\(\s*"', text), name)
