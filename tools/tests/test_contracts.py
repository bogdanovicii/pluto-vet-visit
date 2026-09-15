"""Source contracts for C# behaviour that has no C# test runner: each test pins the wiring the design needs, so a refactor
cannot silently drop it. The Steam tester confirms the behaviour in game through the named log lines."""
import os
import unittest

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src')


def src(name):
    import pathlib
    root = pathlib.Path(SRC)
    if name == 'VetVisitController.cs':
        return '\n'.join(p.read_text(encoding='utf-8') for p in sorted(root.glob('VetVisitController*.cs')))
    return (root / name).read_text(encoding='utf-8')


class ContractTests(unittest.TestCase):
    def has(self, needle, text, where=''):
        self.assertTrue(needle in text, 'missing in %s: %s' % (where, needle))

    def test_past_rearms_the_costume_guns(self):
        c = src('VetVisitController.cs')
        self.has('LoadoutChoice.UseAlternate(p)', c, 'VetVisitController.cs')
        self.has('foreach (int id in p.startingAlternateGunIds) GiveGunById(p, id);', c, 'VetVisitController.cs')
        self.has('LoadoutChoice.Describe(p)', c, 'VetVisitController.cs')
        self.has('p.IsUsingAlternateCostume', src('LoadoutChoice.cs'), 'LoadoutChoice.cs')

    def test_past_kill_writes_the_progress_file(self):
        c = src('VetVisitController.cs')
        i = c.index('CharacterSpecificGungeonFlags.KILLED_PAST, true);')
        self.has('VetProgress.MarkBeaten();', c[i:i + 400], 'EndPast')
        self.has('bogdan.etg.plutovetvisit.progress', src('VetProgress.cs'), 'VetProgress.cs')
        self.has('VetBeaten=true', src('VetProgress.cs'), 'VetProgress.cs')

    def test_trophy_needs_both_flags_and_hooks_the_breach(self):
        t = src('BreachTrophy.cs')
        self.has('[HarmonyPatch(typeof(Foyer), "Awake")]', t, 'BreachTrophy.cs')
        self.has('CharacterSpecificGungeonFlags.KILLED_PAST', t, 'BreachTrophy.cs')
        self.has('VetProgress.Beaten()', t, 'BreachTrophy.cs')
        self.has('"vet_trophy_here"', src('PastPlugin.cs'), 'PastPlugin.cs')

    def test_theatre_mood_hooks(self):
        c = src('VetVisitController.cs')
        self.has('TheatreMood.LampOn(this, World(ClinicLayout.Table));', c, 'VetVisitController.cs')
        self.has('TheatreMood.Red(room);', c, 'VetVisitController.cs')
        self.has('TheatreMood.Restore(room);', c, 'VetVisitController.cs')
        m = src('TheatreMood.cs')
        self.has('AdditionalBraveLight', m, 'TheatreMood.cs')
        self.has('lamp.Initialize();', m, 'TheatreMood.cs')
        self.has('ClinicProp.Show("pluto_lamp_pool")', m, 'TheatreMood.cs')

    def test_kennels_rattle_in_waves(self):
        c = src('VetVisitController.cs')
        self.assertGreaterEqual(c.count('KennelCritter.RattleAll();'), 2)
        self.has('go.AddComponent<KennelCritter>()', src('ClinicObjects.cs'), 'ClinicObjects.cs')

    def test_mask_applies_at_the_last_phase(self):
        self.has('VetMask.Apply(vet);', src('VetVisitController.cs'), 'VetVisitController.cs')
        self.has('masked: VetMask.Available', src('VetBoss.cs'), 'VetBoss.cs')
        self.has('overrideDeathAnimation = "mask_die"', src('VetMask.cs'), 'VetMask.cs')

    def test_pick_up_ending(self):
        c = src('VetVisitController.cs')
        e = c.index('private IEnumerator EndPast()')
        self.has('yield return StartCoroutine(PickUpEnding(p));', c[e:], 'EndPast')
        self.assertLess(c.index('PickUpEnding(p));', e), c.index('Pixelator.Instance.FreezeFrame();', e))
        self.has('if (ending) return;', c[c.index('private void EnsureLoadout('):], 'EnsureLoadout')
        self.has('public void Show(Vector2 at)', src('ClinicNpc.cs'), 'ClinicNpc.cs')

    def test_reset_past_command(self):
        r = src('PastReset.cs')
        self.has('CharacterSpecificGungeonFlags.KILLED_PAST, false', r, 'PastReset.cs')
        self.has('CharacterSpecificGungeonFlags.KILLED_PAST_ALTERNATE_COSTUME, false', r, 'PastReset.cs')
        self.has('GameStatsManager.Save()', r, 'PastReset.cs')
        self.has('SwapToAlternateCostume()', r, 'PastReset.cs')
        self.has('VetProgress.Forget();', r, 'PastReset.cs')
        self.has('BreachTrophy.Remove();', r, 'PastReset.cs')
        self.assertLess(r.index('SwapToAlternateCostume()'), r.index('KILLED_PAST, false'))   # leave the costume first
        self.has('"vet_reset_past"', src('PastPlugin.cs'), 'PastPlugin.cs')

    def test_coop_partner_is_brought_through_before_doors_seal(self):
        c = src('VetVisitController.cs')
        self.assertLess(c.index('BringPartnersThrough(ClinicLayout.WARD_MIN_Y + 1.5f, "ward");'), c.index('SetDoor(wardDoor, false'))
        self.assertLess(c.index('BringPartnersThrough(ClinicLayout.THEATRE_MIN_Y + 1.5f, "theatre");'), c.index('SetDoor(theatreDoor, false'))
        self.has('p.WarpToPoint(World(cell), true, false);', c, 'VetVisitController.cs')

    def test_rescue_scene_runs_before_the_owners(self):
        c = src('VetVisitController.cs')
        e = c.index('private IEnumerator EndPast()')
        self.assertLess(c.index('StartCoroutine(RescueAnimals(p));', e), c.index('StartCoroutine(PickUpEnding(p));', e))
        self.has('FreedAnimal a = k.Free();', c, 'VetVisitController.cs')
        self.has('return FreedAnimal.Spawn(kind,', src('KennelCritter.cs'), 'KennelCritter.cs')
