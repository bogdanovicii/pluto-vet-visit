import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import cast_layout as L  # noqa: E402
import clinic_room as C  # noqa: E402
import tech_poses as T  # noqa: E402
import nurse_poses as N  # noqa: E402
import npc_poses as NP  # noqa: E402


class CastLayoutTests(unittest.TestCase):
    def test_room_places_every_npc_object(self):
        self.assertEqual([n for n, _ in C.NPCS], list(L.NPC_OBJECTS))
        for who in L.NPC_OBJECTS.values():
            self.assertIn(who, NP.NPCS)
            self.assertTrue(list(NP.NPCS[who]['clips']), who)        # the first clip is the rest pose (Grandma: loaf)

    def test_enemy_facts_reach_the_cs(self):
        cs = L.layout_cs()
        for prefix, mod in (('TECH', T), ('NURSE', N)):
            self.assertIn('%s_W = %d, %s_H = %d' % (prefix, mod.CANVAS[0], prefix, mod.CANVAS[1]), cs)
            self.assertIn('%s_HIT_X = %d' % (prefix, mod.HITBOX[0]), cs)
            self.assertIn('%s_SHOOT_X = %d' % (prefix, mod.SHOOT_POINT[0]), cs)
            for clip in mod.CLIPS:
                self.assertIn('"%s"' % clip, cs)
        self.assertIn('new NpcSpec("pluto_npc_owner", "owner"', cs)

    def test_enemies_have_the_clips_the_brain_plays(self):
        for mod in (T, N):
            for clip in ('idle', 'move', 'tell', 'fire', 'die'):
                self.assertIn(clip, mod.CLIPS)
        self.assertIn('net', N.CLIPS)                        # the Nurse's net throw is her FireAnimation
        for who, clips in (('owner', ('idle', 'walk', 'walk_free')), ('receptionist', ('idle', 'talk')), ('rex', ('idle',)), ('grandma', ('loaf',))):
            for clip in clips:
                self.assertIn(clip, NP.NPCS[who]['clips'], who)


if __name__ == '__main__':
    unittest.main()
