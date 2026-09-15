"""The Vet's attack brain and projectile readability.

Executable tests: the engine-independent C# helpers (src/AttackCoordination.cs, src/ThreatReadability.cs) are compiled with
mcs and run with mono, like test_encounter_lifecycle.test_roster_executable. Source contracts pin the Unity wiring that
cannot run here (the game is not installed on the build Mac)."""
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'src'
PURE = [SRC / 'AttackCoordination.cs', SRC / 'ThreatReadability.cs']


def read(name):
    return (SRC / name).read_text(encoding='utf-8')


def body(text, start):
    begin = text.index('{', start)
    depth, end = 1, begin + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[begin:end]


HARNESS = r'''
using System;
using PlutoVetVisit;
class Checks {
    static int n;
    static void Check(bool ok, string why) { n++; if (!ok) throw new Exception("check " + n + ": " + why); }
    static bool Near(float a, float b) { return Math.Abs(a - b) < 1e-3f; }

    static void Band() {
        var b = new DistanceBand(4f, 5.5f, 12f, 10f);
        Check(b.Update(8f) == RangeBand.Mid, "starts mid");
        Check(b.Update(4.5f) == RangeBand.Mid, "4.5 is not yet close (enter at 4)");
        Check(b.Update(3.9f) == RangeBand.Close, "enter close below 4");
        Check(b.Update(5.0f) == RangeBand.Close, "stay close until 5.5 (hysteresis)");
        Check(b.Update(5.6f) == RangeBand.Mid, "exit close above 5.5");
        Check(b.Update(11.5f) == RangeBand.Mid, "11.5 is not yet far (enter at 12)");
        Check(b.Update(12.5f) == RangeBand.Far, "enter far above 12");
        Check(b.Update(10.5f) == RangeBand.Far, "stay far until 10 (hysteresis)");
        Check(b.Update(9.9f) == RangeBand.Mid, "exit far below 10");
        Check(b.Update(2f) == RangeBand.Close, "a jump straight to close");
        Check(b.Update(20f) == RangeBand.Far, "a jump straight to far");
        bool threw = false;
        try { new DistanceBand(6f, 5f, 12f, 10f); } catch (ArgumentException) { threw = true; }
        Check(threw, "exit must be wider than enter");
        Check((RangeBand.Any & RangeBand.Close) != 0 && (RangeBand.Any & RangeBand.Far) != 0, "Any covers every band");
    }

    static void Repeat() {
        var r = new RepeatGuard(2f);
        Check(r.Allows(AttackFamily.Ring, 0f), "nothing used yet");
        r.Started(AttackFamily.Ring);
        Check(!r.Allows(AttackFamily.Ring, 0.5f), "no repeat while it runs");
        Check(r.Allows(AttackFamily.Booster, 0.5f), "another family is fine");
        r.Ended(AttackFamily.Ring, 1f);
        Check(!r.Allows(AttackFamily.Ring, 2.9f), "no repeat inside the window after it ended");
        Check(r.Allows(AttackFamily.Ring, 3.0f), "allowed once the window has passed");
        r.Started(AttackFamily.Booster); r.Ended(AttackFamily.Booster, 3.2f);
        Check(r.Allows(AttackFamily.Ring, 3.3f), "only the last family is guarded");
        Check(r.Allows(AttackFamily.None, 3.3f), "uncoordinated attacks are never guarded");
    }

    static void Recovery() {
        var t = new RecoveryTimer();
        Check(!t.Active(0f), "idle");
        t.Begin(1f, 1.5f);
        Check(t.Active(2.4f) && !t.Active(2.5f), "active for its duration");
        t.Begin(2f, 0.1f);
        Check(t.Active(2.4f), "a shorter recovery never cuts a longer one");
        Check(Near(t.Remaining(2f), 0.5f), "remaining time");
    }

    static void Budget() {
        var b = new ThreatBudget(3f);
        Check(b.CanAfford(2f, 0f), "empty");
        Check(b.Acquire(1, 2f, 0f, 10f), "the Vet's wall");
        Check(b.CanAfford(1f, 0.5f), "the Nurse's hose fits beside it");
        Check(!b.CanAfford(2f, 0.5f), "a second heavy wall waits while the first is live");
        Check(!b.Acquire(2, 2f, 0.5f, 10f), "acquire refuses too");
        Check(b.Acquire(2, 1f, 0.5f, 10f), "nurse hose");
        Check(Near(b.Load(0.6f), 3f), "load sums live tokens");
        b.Settle(1, 2f, 1.5f);
        Check(!b.CanAfford(2f, 3.4f), "the wall's bullets are still in the air");
        Check(Near(b.Load(3.5f), 1f), "the wall's token expired at 3.5");
        Check(b.CanAfford(2f, 3.5f), "nurse (1) + a new wall (2) = 3 fits once the first wall expired");
        b.ReleaseOwner(2);
        Check(Near(b.Load(3.6f), 0f), "released");
        Check(b.CanAfford(9f, 3.6f), "an oversized pattern may start on an empty board (no deadlock)");
        Check(b.Acquire(1, 1f, 4f, 5f) && b.Acquire(1, 2f, 4f, 6f) && Near(b.Load(4f), 2f), "one token per owner: the new one replaces");
        Check(b.CanAfford(0f, 4f), "free attacks always fit");
        b.Clear();
        Check(Near(b.Load(4f), 0f), "clear");
        Check(b.Acquire(3, 2f, 0f, 1f) && Near(b.Load(1f), 0f), "tokens expire at their until time");
    }

    static void Coordinator() {
        var shared = new ThreatBudget(3f);
        var vet = new AttackCoordinator(new DistanceBand(4f, 5.5f, 12f, 10f), new RepeatGuard(2f), shared, 1);
        var nurse = new AttackCoordinator(new DistanceBand(3f, 4f, 11f, 9f), new RepeatGuard(1.5f), shared, 2);
        var wall = new AttackPlan(AttackFamily.Wall, 2f, 1.5f, 1.2f, RangeBand.Mid | RangeBand.Far);
        var ring = new AttackPlan(AttackFamily.Ring, 2f, 1.5f, 1.2f, RangeBand.Any);
        var booster = new AttackPlan(AttackFamily.Booster, 0f, 0f, 0f, RangeBand.Mid | RangeBand.Far);
        var spray = new AttackPlan(AttackFamily.Spray, 1f, 0.8f, 0f, RangeBand.Close | RangeBand.Mid);
        var hose = new AttackPlan(AttackFamily.Spray, 1f, 0.8f, 0f, RangeBand.Any);
        Check(wall.IsHeavy && !spray.IsHeavy && !booster.IsHeavy, "heavy is cost 2 and up");
        Check(vet.Veto(wall, 3f, 0f) == "band", "no wall point blank");
        Check(vet.Veto(spray, 3f, 0f) == null, "spray point blank");
        Check(vet.Veto(wall, 8f, 0f) == null, "wall at mid range");
        Check(vet.Veto(booster, -1f, 0f) == null, "no target distance: the band does not veto");
        vet.Started(wall, 0f, 1.2f);
        Check(nurse.Veto(hose, 6f, 0.5f) == null, "nurse area pressure beside a live wall");
        nurse.Started(hose, 0.5f, 1f);
        vet.Ended(wall, 1.2f);
        Check(vet.Veto(ring, 8f, 1.3f) == "recovery", "recovery after a heavy pattern");
        Check(vet.Veto(booster, 8f, 1.3f) == null, "light attacks during recovery");
        Check(vet.Veto(wall, 8f, 3.1f) == "repeat", "no back-to-back wall inside the repeat window");
        Check(vet.Veto(ring, 8f, 2.5f) == "budget", "the wall is still live (until 2.7) with the hose: another heavy waits");
        nurse.Ended(hose, 1.5f);
        Check(vet.Veto(ring, 8f, 2.8f) == null, "lanes open again");
        vet.Started(booster, 3f, 0.3f); vet.Ended(booster, 3.3f);
        Check(vet.Veto(wall, 8f, 3.4f) == null, "wall allowed once another family ran and the window passed");
        vet.Forget();
        Check(Near(shared.Load(3.4f), 0f), "forget releases the owner's budget");
        var lost = new AttackCoordinator(new DistanceBand(4f, 5.5f, 12f, 10f), new RepeatGuard(2f), null, 9);
        lost.Started(ring, 0f, 1f);
        Check(lost.Veto(ring, 8f, 5f) == "repeat", "still running inside expected + safety");
        Check(lost.Veto(ring, 8f, 1f + AttackCoordinator.SafetySeconds + 2.01f) == null, "a lost end notification never blocks a family forever");
    }

    static void Gaps() {
        Check(Near(GapScorer.ArcTiles(90f, 4f), (float)(Math.PI * 2f)), "quarter circle at radius 4");
        Check(Near(GapScorer.ArcTiles(-90f, 4f), (float)(Math.PI * 2f)), "arc is unsigned");
        float reach = GapScorer.Reach(6f, 6f, 0.2f, 5f);
        Check(Near(reach, 6f), "5 tiles/s for 1.2 s");
        float need = GapScorer.Need(6f);
        Check(Near(need, 7.5f) && Near(GapScorer.Need(20f), 7.5f) && Near(GapScorer.Need(2f), 3.5f), "need = min(d, 6) + 1.5");
        float open = GapScorer.Score(10f, need, 30f, 6f, reach);
        float walled = GapScorer.Score(2f, need, 30f, 6f, reach);
        float far = GapScorer.Score(10f, need, 80f, 6f, reach);
        Check(open > walled, "a gap into a wall scores lower than an open one");
        Check(far < 0f, "a gap Pluto cannot reach in time is unreachable");
        Check(GapScorer.Score(10f, need, 10f, 6f, reach) > open, "closer gaps score higher among open ones");
        var scores = new float[] { 0.2f, 0.95f, -1f, 0.9f };
        Check(GapScorer.Pick(scores, 0f, 0.1f) == 1 && GapScorer.Pick(scores, 0.99f, 0.1f) == 3, "random among the near-best");
        Check(GapScorer.Pick(new float[] { -1f, -0.5f }, 0.3f, 0.1f) == 1, "nothing reachable: still the best");
        Check(GapScorer.Pick(new float[0], 0.5f, 0.1f) == -1, "no candidates");
        Check(GapScorer.Pick(new float[] { 0.5f }, 1f, 0.1f) == 0, "random 1.0 is clamped");
    }

    static void Cues() {
        Check(CueSchedule.StyleFor(AttackFamily.Booster) == CueStyle.Glint, "booster glints");
        Check(CueSchedule.StyleFor(AttackFamily.Pill) == CueStyle.Alternate, "pill alternates red and white");
        Check(CueSchedule.StyleFor(AttackFamily.Stitches) == CueStyle.DoubleBlink, "stitches pulse twice");
        Check(CueSchedule.StyleFor(AttackFamily.Ring) == CueStyle.Steady && CueSchedule.StyleFor(AttackFamily.Anesthesia) == CueStyle.Steady, "rings and clouds hold");
        Check(CueSchedule.StyleFor(AttackFamily.None) == CueStyle.None, "uncoordinated: nothing");
        var fams = new AttackFamily[] { AttackFamily.Booster, AttackFamily.Spray, AttackFamily.Pill, AttackFamily.Ring, AttackFamily.Spiral, AttackFamily.Wall, AttackFamily.Stitches, AttackFamily.Anesthesia, AttackFamily.Hop, AttackFamily.Leap, AttackFamily.Course };
        foreach (var f in fams) Check(CueSchedule.StyleFor(f) != CueStyle.None, "every family has a cue: " + f);
        Check(CueSchedule.Phase(CueStyle.Glint, 0.05f) == 1 && CueSchedule.Phase(CueStyle.Glint, 0.2f) == 0, "glint is short");
        Check(CueSchedule.Phase(CueStyle.Alternate, 0.05f) == 1 && CueSchedule.Phase(CueStyle.Alternate, 0.15f) == 2, "alternate swaps colour");
        Check(CueSchedule.Phase(CueStyle.DoubleBlink, 0.05f) == 1 && CueSchedule.Phase(CueStyle.DoubleBlink, 0.18f) == 0 && CueSchedule.Phase(CueStyle.DoubleBlink, 0.3f) == 1, "two blinks");
        foreach (CueStyle s in Enum.GetValues(typeof(CueStyle)))
        {
            Check(CueSchedule.Phase(s, CueSchedule.Duration(s) + 0.01f) == 0, "every cue ends: " + s);
            Check(CueSchedule.Phase(s, -0.1f) == 0, "nothing before it starts: " + s);
        }
    }

    static void Pulses() {
        Check(!FusePulse.Flash(40, 24, 8), "no flash before the warning window");
        Check(FusePulse.Flash(24, 24, 8) && FusePulse.Flash(21, 24, 8) && !FusePulse.Flash(20, 24, 8) && FusePulse.Flash(16, 24, 8), "on half of each period");
        Check(!FusePulse.Flash(0, 24, 8), "done");
        Check(Near(FusePulse.Pop(0, 6, 1.5f), 1.5f) && Near(FusePulse.Pop(3, 6, 1.5f), 1.25f) && Near(FusePulse.Pop(6, 6, 1.5f), 1f) && Near(FusePulse.Pop(-1, 6, 1.5f), 1f), "pop decays");
        Check(FusePulse.Visible(100, 45, 5, 2), "steady before expiry window");
        Check(FusePulse.Visible(45, 45, 5, 2) && !FusePulse.Visible(40, 45, 5, 2) && FusePulse.Visible(38, 45, 5, 2), "blinks mostly visible");
        int hidden = 0; for (int f = 1; f <= 45; f++) if (!FusePulse.Visible(f, 45, 5, 2)) hidden++;
        Check(hidden * 2 < 45, "a damaging cloud is never hidden most of the time");
    }

    static void Pills() {
        Check(PillContract.Bursts(PillEnd.Fuse, false), "fuse");
        Check(PillContract.Bursts(PillEnd.PlayerShot, false), "shot pops into its burst");
        Check(!PillContract.Bursts(PillEnd.Destroyed, true), "blank / boss death / clear: no replacement hazards");
        Check(PillContract.Bursts(PillEnd.Destroyed, false), "hitting a wall or Pluto still bursts");
        Check(!PillContract.Bursts(PillEnd.PlayerShot, true), "prevent always wins");
        Check(PillContract.ShotHits(0.5f, 0f, 0.35f, 0.3f), "overlap");
        Check(!PillContract.ShotHits(0.66f, 0f, 0.35f, 0.3f), "miss");
        Check(PillContract.ShotHits(0f, 0.59f, 0.35f, 0.25f) && !PillContract.ShotHits(0f, 0.61f, 0.35f, 0.25f), "distance along the other axis");
        Check(PillContract.ShotHits(0.3f, 0.3f, 0.35f, 0.25f) && !PillContract.ShotHits(0.45f, 0.45f, 0.35f, 0.25f), "diagonal uses the true distance");
        Check(PillContract.SegmentHits(-2f, 0.2f, 2f, 0.2f, 0.35f, 0.25f), "a fast shot that jumped over the pill this frame still pops it");
        Check(!PillContract.SegmentHits(-2f, 1f, 2f, 1f, 0.35f, 0.25f), "a shot passing a tile away misses");
        Check(PillContract.SegmentHits(0.5f, 0f, 0.5f, 0f, 0.35f, 0.25f), "a still shot is a point test");
        Check(!PillContract.SegmentHits(1f, 0f, 3f, 0f, 0.35f, 0.25f), "a shot moving away beyond reach misses");
    }

    static void Main() {
        Band(); Repeat(); Recovery(); Budget(); Coordinator(); Gaps(); Cues(); Pulses(); Pills();
        Console.WriteLine("ok " + n);
    }
}'''


@unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'needs mcs and mono')
class ExecutableBrainTests(unittest.TestCase):
    def test_pure_helpers(self):
        for p in PURE:
            self.assertTrue(p.exists(), '%s must exist' % p.name)
        with tempfile.TemporaryDirectory() as tmp:
            cs = pathlib.Path(tmp) / 'check.cs'
            exe = pathlib.Path(tmp) / 'check.exe'
            cs.write_text(HARNESS)
            built = subprocess.run(['mcs', '-out:' + str(exe)] + [str(p) for p in PURE] + [str(cs)], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            ran = subprocess.run(['mono', str(exe)], capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
            self.assertTrue(ran.stdout.startswith('ok '), ran.stdout)


class BrainSourceContracts(unittest.TestCase):
    def test_pure_helpers_do_not_touch_the_engine(self):
        engine = re.compile(r'using (UnityEngine|Brave|Dungeonator)|\b(UnityEngine|Brave|Dungeonator)\.|\bMathf\b|\bVector[23]\b')
        for p in PURE:
            text = p.read_text(encoding='utf-8')
            self.assertIsNone(engine.search(text), p.name)

    def test_every_script_states_its_blank_contract(self):
        text = read('VetAttacks.cs')
        scripts = re.findall(r'class (\w+) : (?:Script|DropletWallScript)\b', text)
        self.assertGreater(len(scripts), 15)
        for name in scripts:
            if name == 'DropletWallHardScript':
                continue   # inherits DropletWallScript.Top
            start = text.index('class %s ' % name)
            top = body(text, text.index('Top()', start))
            first_yield = top.find('yield')
            self.assertIn('EndOnBlank = true;', top, name)
            self.assertLess(top.index('EndOnBlank = true;'), first_yield if first_yield >= 0 else len(top), name)

    def test_pill_is_shootable_and_blank_safe(self):
        text = read('VetAttacks.cs')
        pill = body(text, text.index('class PillBullet'))
        self.assertIn('PillContract.Bursts(PillEnd.Destroyed, preventSpawningProjectiles)', pill)
        self.assertIn('PlayerShotTouches', pill)
        self.assertIn('PillEnd.PlayerShot', pill)
        self.assertIn('FusePulse.Flash', pill)
        self.assertIn('pops it', text[text.rindex('///', 0, text.index('class PillBullet')) - 400:text.index('class PillBullet')])

    def test_stitches_and_clouds_have_cues(self):
        text = read('VetAttacks.cs')
        self.assertIn('FusePulse.Pop', body(text, text.index('class StitchBullet')))
        cloud = body(text, text.index('class CloudBullet'))
        self.assertIn('FusePulse.Visible', cloud)
        self.assertIn('LingeringHazards', cloud)

    def test_rings_and_walls_score_their_gaps(self):
        text = read('VetAttacks.cs')
        for name in ('ConeOfShameScript', 'DropletWallScript', 'ScalpelRingScript', 'SnipTimeScript'):
            self.assertIn('ArenaProbe.', body(text, text.index('class %s ' % name)), name)

    def test_hops_have_anticipation_and_recovery(self):
        tech = read('VetTech.cs')
        hop = tech[tech.index('public static DashBehavior Hop('):]
        self.assertIn('string chargeAnim', hop[:hop.index(')')])
        self.assertIn('chargeAnim = chargeAnim', body(hop, 0))
        boss = read('VetBoss.cs')
        self.assertIn('VetMask.Available ? "mask_tell" : "tell"', boss)
        self.assertIn('CoordinatedHop', boss)
        self.assertIn('rollLandDustup', read('VetAttackBrain.cs'))

    def test_coordination_is_wired(self):
        boss = read('VetBoss.cs')
        for fam in ('Booster', 'Spray', 'Pill', 'Ring', 'Spiral', 'Wall', 'Stitches', 'Anesthesia', 'Leap', 'Course'):
            self.assertIn('AttackFamily.' + fam, boss, fam)
        self.assertIn('CoordinatedSequence', boss)
        self.assertIn('AddComponent<AttackBrain>()', boss)
        nurse = read('VetTech.cs')
        n = nurse[nurse.index('public static class Nurse'):]
        self.assertIn('AddComponent<AttackBrain>()', n)
        self.assertIn('AttackFamily.', n)
        brain = read('VetAttackBrain.cs')
        self.assertIn('base.IsReady()', brain)
        self.assertIn('DeregisterOverrideColor', brain)
        self.assertIn('OnActorPreDeath', brain)

    def test_damage_defaults_unchanged(self):
        self.assertIn('p.baseData.damage = 0.5f;', read('VetBoss.cs'))
        self.assertIn('masked: VetMask.Available', read('VetBoss.cs'))


if __name__ == '__main__':
    unittest.main()
