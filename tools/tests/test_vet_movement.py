"""The Vet's movement and fight phases (0.14.4 fix for "he stays stuck" and "no red light").

Executable tests: the engine-independent helpers (src/MovementPlanner.cs, src/PhaseTracker.cs, src/AttackCoordination.cs) are
compiled with mcs and run with mono, including a several-second simulation of attack selection under a live long-lived hazard
that must keep the Vet acting or moving. Source contracts pin the Unity wiring that cannot run here."""
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'src'
PURE = [SRC / 'MovementPlanner.cs', SRC / 'PhaseTracker.cs', SRC / 'AttackCoordination.cs']


def read(name):
    return (SRC / name).read_text(encoding='utf-8')


HARNESS = r'''
using System;
using PlutoVetVisit;
class Checks {
    static int n;
    static void Check(bool ok, string why) { n++; if (!ok) throw new Exception("check " + n + ": " + why); }
    static float Dist(float ax, float ay, float bx, float by) { return (float)Math.Sqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by)); }

    // An open theatre 36 x 23 tiles (y 40..63) with the table group at (18, 47).
    static bool Open(float x, float y, out bool sees) { sees = true; return x > 1f && x < 35f && y > 40.5f && y < 62f; }

    static void Phases() {
        var p = new PhaseTracker();
        Check(p.Observe(1000f, 1000f) == PhaseEvent.None, "full health: nothing");
        Check(p.Observe(610f, 1000f) == PhaseEvent.None, "61 %: nothing yet");
        Check(p.Observe(600f, 1000f) == PhaseEvent.PhaseTwo, "60 %: phase two");
        Check(p.Observe(590f, 1000f) == PhaseEvent.None, "phase two fires once");
        Check(p.Observe(500f, 1000f) == PhaseEvent.Reinforcements, "50 %: reinforcements");
        Check(p.Observe(251f, 1000f) == PhaseEvent.None, "25.1 %: not the last phase yet");
        Check(p.Observe(250f, 1000f) == PhaseEvent.LastPhase, "exactly 25 %: the last phase (the red room)");
        Check(p.Observe(100f, 1000f) == PhaseEvent.None && p.Observe(900f, 1000f) == PhaseEvent.None, "once only, healing never re-arms it");
        var big = new PhaseTracker();
        Check(big.Observe(200f, 1000f) == (PhaseEvent.PhaseTwo | PhaseEvent.Reinforcements | PhaseEvent.LastPhase), "one big hit crosses every threshold");
        var dead = new PhaseTracker();
        Check(dead.Observe(0f, 1000f) == PhaseEvent.None, "a killing blow from above 25 % is the death flow, not the red room");
        Check(dead.Observe(-5f, 1000f) == PhaseEvent.None && dead.Observe(10f, 0f) == PhaseEvent.None && dead.Observe(float.NaN, 1000f) == PhaseEvent.None, "invalid readings");
        Check(dead.Observe(240f, 1000f) == (PhaseEvent.PhaseTwo | PhaseEvent.Reinforcements | PhaseEvent.LastPhase), "still fires later when alive");
        // Two sources (OnDamaged and the health poll) feeding one tracker never double-fire.
        var both = new PhaseTracker();
        int reds = 0;
        foreach (float hp in new float[] { 400f, 260f, 249f, 249f, 240f, 230f })
            if ((both.Observe(hp, 1000f) & PhaseEvent.LastPhase) != 0) reds++;
        Check(reds == 1, "the red room switches on exactly once");
    }

    static void HopsAreMovement() {
        var hop = new AttackPlan(AttackFamily.Hop, 0f, 0f, 0f, RangeBand.Any);
        var booster = new AttackPlan(AttackFamily.Booster, 0f, 0f, 0f, RangeBand.Mid | RangeBand.Far);
        Check(hop.IsMovement && !booster.IsMovement, "only hops are movement");
        var c = new AttackCoordinator(new DistanceBand(4f, 5.5f, 12f, 10f), new RepeatGuard(2f), new ThreatBudget(3f), 1);
        c.Started(hop, 0f, 0.8f); c.Ended(hop, 0.8f);
        Check(c.Veto(hop, 8f, 0.9f) == null, "a double hop is not blocked by the repeat guard");
        c.Started(booster, 1f, 0.5f); c.Ended(booster, 1.5f);
        c.Started(hop, 1.6f, 0.8f); c.Ended(hop, 2.4f);
        Check(c.Veto(booster, 8f, 2.5f) == "repeat", "a hop in between does not erase the booster's repeat window");
        Check(c.Veto(booster, 8f, 3.6f) == null, "the booster window still ends on time");
        string s = c.DrainSummary();
        Check(s != null && s.Contains("repeat 1") && s.Contains("started 3"), "summary counts vetoes and starts: " + s);
        Check(c.DrainSummary() == null, "summary resets");
    }

    static void Planner() {
        bool threw = false;
        try { new OrbitPlanner(9f, 5f, 0.8f); } catch (ArgumentException) { threw = true; }
        Check(threw, "band must be ordered");
        var p = new OrbitPlanner(5.5f, 9f, 0.8f) { HasAnchor = true, AnchorX = 18f, AnchorY = 47f, AnchorKeepOut = 2.5f };
        MoveOrder o = p.Tick(0f, 18f, 52f, 18f, 44f, true, true, Open);
        Check(o.Kind == MoveKind.PathTo && o.Reason == "start", "the first tick issues a leg");
        float r = Dist(o.X, o.Y, 18f, 44f);
        Check(r >= 5.5f - 1e-3f && r <= 9f + 1e-3f, "the leg ends inside the preferred band: " + r);
        Check(Dist(o.X, o.Y, 18f, 47f) >= 2.5f, "never onto the table group");
        Check(Dist(o.X, o.Y, 18f, 52f) >= 1.5f, "a real step, not a shuffle");
        Check(p.Tick(0.1f, 18.3f, 51.9f, 18f, 44f, false, true, Open).Kind == MoveKind.Hold, "following a fresh leg: hold");
        // The path is cleared (an attack stopped him): a new leg as soon as movement ticks again.
        o = p.Tick(0.9f, 19f, 51.5f, 18f, 44f, true, true, Open);
        Check(o.Kind == MoveKind.PathTo && o.Reason == "arrived", "a cleared path starts the next leg: " + o.Reason);
        // No progress for IdleLimit: stalled, and the orbit turns round.
        int sign = p.OrbitSign;
        p.Tick(1.0f, 19f, 51.5f, 18f, 44f, false, true, Open);
        o = p.Tick(1.75f, 19f, 51.5f, 18f, 44f, false, true, Open);
        Check(o.Kind == MoveKind.PathTo && o.Reason == "stalled" && p.Stalls == 1, "stalled after IdleLimit: " + o.Reason);
        Check(p.OrbitSign == -sign || p.Legs > 0, "stall flips the orbit");
        // The engine could not path there: forget it and pick again next tick.
        p.Rejected();
        o = p.Tick(1.8f, 19f, 51.5f, 18f, 44f, false, true, Open);
        Check(o.Kind == MoveKind.PathTo && o.Reason == "start", "a rejected leg is replaced on the next tick");
        // Too close: the leg moves him back out to the band.
        var close = new OrbitPlanner(5.5f, 9f, 0.8f);
        o = close.Tick(0f, 18f, 46f, 18f, 44f, true, true, Open);
        Check(Dist(o.X, o.Y, 18f, 44f) >= 5.5f - 1e-3f, "hugged: step back out to the band");
        // No line to Pluto: a spot that sees him wins even against the orbit direction.
        SpotCheck oneSide = delegate(float x, float y, out bool sees) { sees = x < 18f; return x > 1f && x < 35f && y > 40.5f; };
        var los = new OrbitPlanner(5.5f, 9f, 0.8f);
        o = los.Tick(0f, 18f, 52f, 18f, 44f, true, false, oneSide);
        Check(o.X < 18f, "no line: pick a spot with a line");
        // Boxed in: the ring is blocked, the escape step still moves him.
        SpotCheck corner = delegate(float x, float y, out bool sees) { sees = false; return Dist(x, y, 3f, 60f) <= 2.6f; };
        var boxed = new OrbitPlanner(5.5f, 9f, 0.8f);
        o = boxed.Tick(0f, 3f, 60f, 18f, 44f, true, true, corner);
        Check(o.Kind == MoveKind.PathTo, "the escape step when the ring is blocked");
        SpotCheck wall = delegate(float x, float y, out bool sees) { sees = false; return false; };
        Check(boxed.Tick(5f, 3f, 60f, 18f, 44f, true, true, wall).Kind == MoveKind.Hold && boxed.Tick(5.1f, 3f, 60f, 18f, 44f, true, true, wall).Reason == "boxed", "fully boxed: hold, and retry every tick");
    }

    // Six seconds of the Vet's selection at the speculator's 0.1 s tick, with the Nurse's anesthesia cloud (cost 2) live for
    // the whole window and a heavy wall just finished (recovery). Heavy plans are vetoed throughout; the booster runs only every
    // few seconds. Between attacks the planner must keep him moving: he may never stand still for more than 1 s outside an
    // attack. A prop (the table group's trolleys) blocks every step further left than x = 17 on the side his first orbit leg
    // heads for, so the path is accepted but he makes no progress: only turning round on a stall keeps him under 1 s (a leg
    // timeout alone would leave him standing for LegSeconds).
    static void Simulation() {
        var shared = new ThreatBudget(3f);
        shared.Acquire(2, 2f, 0f, 1000f);   // the long-lived hazard: its token outlives the simulation
        var vet = new AttackCoordinator(new DistanceBand(4f, 5.5f, 12f, 10f), new RepeatGuard(2f), shared, 1);
        var wall = new AttackPlan(AttackFamily.Wall, 2f, 1.8f, 1.2f, RangeBand.Mid | RangeBand.Far);
        var ring = new AttackPlan(AttackFamily.Ring, 2f, 1.6f, 1.2f, RangeBand.Any);
        var course = new AttackPlan(AttackFamily.Course, 3f, 1.8f, 2.0f, RangeBand.Mid | RangeBand.Far);
        var booster = new AttackPlan(AttackFamily.Booster, 0f, 0f, 0f, RangeBand.Mid | RangeBand.Far);
        vet.Started(wall, -1.5f, 1.4f); vet.Ended(wall, -0.1f);   // recovery and the repeat window are live at t = 0
        var plans = new AttackPlan[] { wall, ring, course, booster };
        float[] cooldownUntil = new float[plans.Length];
        var planner = new OrbitPlanner(5.5f, 9f, 0.8f) { HasAnchor = true, AnchorX = 18f, AnchorY = 47f, AnchorKeepOut = 2.5f };
        float x = 18f, y = 52f, tx = 18f, ty = 43f, speed = 3f, dt = 0.1f;
        float busyUntil = -1f, lastActive = 0f, worstIdle = 0f, travelled = 0f;
        bool hasPath = false; float gx = 0f, gy = 0f;
        int attacks = 0, heavyStarts = 0, stalledTicks = 0;
        for (int i = 0; i <= 60; i++) {
            float t = i * dt;
            tx = 18f + 3f * (float)Math.Sin(t * 0.7f);   // Pluto strafes too
            if (t < busyUntil) { lastActive = t; continue; }
            bool attacked = false;
            for (int k = 0; k < plans.Length && !attacked; k++) {
                if (t < cooldownUntil[k]) continue;
                if (vet.Veto(plans[k], Dist(x, y, tx, ty), t) != null) continue;
                vet.Started(plans[k], t, 0.6f); vet.Ended(plans[k], t + 0.6f);
                cooldownUntil[k] = t + 2.5f;
                busyUntil = t + 0.6f; lastActive = t; attacked = true; attacks++;
                if (plans[k].IsHeavy) heavyStarts++;
                hasPath = false;   // ShootBehavior clears the path
            }
            if (attacked) continue;
            MoveOrder o = planner.Tick(t, x, y, tx, ty, !hasPath, true, Open);
            if (o.Kind == MoveKind.PathTo) { hasPath = true; gx = o.X; gy = o.Y; }
            if (hasPath) {
                float d = Dist(x, y, gx, gy), stepLen = Math.Min(d, speed * dt);
                float nx = d > 1e-4f ? x + (gx - x) / d * stepLen : x, ny = d > 1e-4f ? y + (gy - y) / d * stepLen : y;
                if (nx < 17f && nx < x) { nx = x; ny = y; stalledTicks++; }   // the prop: no progress this way
                float moved = Dist(x, y, nx, ny);
                x = nx; y = ny; travelled += moved;
                if (moved > 0.01f) lastActive = t;
                if (Dist(x, y, gx, gy) < 0.05f) hasPath = false;
            }
            worstIdle = Math.Max(worstIdle, t - lastActive);
        }
        Check(heavyStarts == 0, "the hazard keeps every heavy pattern vetoed (fairness holds)");
        Check(attacks >= 1, "the light booster still fires");
        Check(worstIdle <= 1.0f + 1e-3f, "never idle more than 1 s outside attacks: worst " + worstIdle);
        Check(travelled >= 6f, "he keeps repositioning: travelled " + travelled);
        Check(planner.Legs >= 3, "several legs: " + planner.Legs);
        Check(stalledTicks > 0 && planner.Stalls >= 1, "the prop really blocked a leg and the planner turned round: ticks " + stalledTicks + ", stalls " + planner.Stalls);
    }

    static void Main() {
        Phases(); HopsAreMovement(); Planner(); Simulation();
        Console.WriteLine("ok " + n);
    }
}'''


@unittest.skipUnless(shutil.which('mcs') and shutil.which('mono'), 'needs mcs and mono')
class ExecutableMovementTests(unittest.TestCase):
    def test_planner_phases_and_simulation(self):
        with tempfile.TemporaryDirectory() as tmp:
            cs = pathlib.Path(tmp) / 'check.cs'
            exe = pathlib.Path(tmp) / 'check.exe'
            cs.write_text(HARNESS)
            built = subprocess.run(['mcs', '-out:' + str(exe)] + [str(p) for p in PURE] + [str(cs)], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            ran = subprocess.run(['mono', str(exe)], capture_output=True, text=True)
            self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
            self.assertTrue(ran.stdout.startswith('ok '), ran.stdout)


class MovementSourceContracts(unittest.TestCase):
    def test_pure_helpers_do_not_touch_the_engine(self):
        engine = re.compile(r'using (UnityEngine|Brave|Dungeonator)|\b(UnityEngine|Brave|Dungeonator)\.|\bMathf\b|\bVector[23]\b')
        for p in PURE:
            self.assertIsNone(engine.search(p.read_text(encoding='utf-8')), p.name)

    def test_vet_moves_with_one_behaviour(self):
        boss = read('VetBoss.cs')
        moves = boss[boss.index('bs.MovementBehaviors ='):boss.index('bs.AttackBehaviors =')]
        self.assertIn('new OrbitTargetBehavior', moves)
        self.assertNotIn('new SeekTargetBehavior', moves, 'Seek clears the path every tick inside its range')
        self.assertNotIn('new MoveErraticallyBehavior', moves)
        self.assertIn('ClinicLayout.Table', moves)
        self.assertIn('ClinicLayout.THEATRE_MIN_Y', moves)

    def test_movement_behaviour_never_clears_its_own_path(self):
        b = read('VetMovementBehavior.cs')
        self.assertIn('class OrbitTargetBehavior : MovementBehaviorBase', b)
        self.assertNotIn('ClearPath()', b)
        self.assertIn('PathfindToPosition', b)
        self.assertIn('p.Rejected()', b)
        self.assertIn('LingeringHazards.Blocks', b)
        self.assertIn('"vet move: legs +"', b)
        self.assertIn('LogEvery', b)

    def test_phases_fire_from_damage_and_poll(self):
        boss = read('VetBoss.cs')
        r = boss[boss.index('public class VetReinforcements'):boss.index('public class VetDeathHandler')]
        self.assertIn('new PhaseTracker()', r)
        self.assertIn('OnDamaged', r)
        self.assertIn('private void Update()', r)
        self.assertIn('c.LastFifth()', r)
        self.assertIn('"vet phase: "', r)
        self.assertNotIn('0.25f)', r.replace('nextPoll = Time.time + 0.25f', ''), 'thresholds live in PhaseTracker')

    def test_red_room_uses_the_ambient_override(self):
        m = read('TheatreMood.cs')
        self.assertIn('OverrideAmbientLight = true', m)
        self.assertIn('OverrideAmbientColor', m)
        self.assertIn('PastConfig.LastPhaseR', m)
        self.assertIn('lamp.LightColor', m)
        self.assertIn('"mood: last phase red"', m)
        self.assertIn('" reached: override "', m)
        self.assertIn('TheatreMood.Release();', read('VetVisitController.Combat.cs'))
        cfg = read('PastConfig.cs')
        self.assertIn('"LastPhaseG"', cfg)
        self.assertNotIn('MoodRedG', cfg)

    def test_brain_logs_are_throttled(self):
        b = read('VetAttackBrain.cs')
        self.assertIn('DrainSummary()', b)
        self.assertIn('nextSummary = Now + 4f', b)


if __name__ == '__main__':
    unittest.main()
