using System.Collections;
using Brave.BulletScript;
using UnityEngine;

namespace PlutoVetVisit
{
    // Bullet scripts run at 60 frames per second: Wait(8) is eight frames. Speeds are tiles per second and
    // are scaled by PastConfig.BulletSpeedScale (1 = the numbers below, which sit in the vanilla floor-boss
    // band: slow rings 5-6, spirals 7, aimed bursts 10-12; Bullet King quickshots are 12, Gorgun's scream 7).
    // Every enemy projectile does half a heart, as in vanilla.
    //
    // 0.12 readability rules, one per pattern family:
    // - one sprite per family (tools/projectiles.py BANK): syringes are aimed and fast, vaccine orbs are rings and spirals,
    //   teal droplets are fans and walls, green tranq is the Nurse's hose, scalpels are the scalpel ring, stitches hang;
    // - dense patterns (rings, walls, spirals, point-blank fans) wait PastConfig.PatternLeadIn frames after the tell, so a
    //   pattern never starts on top of Pluto the instant the tell ends (the Bullet King's Wait(10) before its bursts);
    // - every ring and wall leaves a guaranteed gap (RingGapSlots, WallGapSlots, ScalpelGapDegrees), and the gap is placed
    //   where the arena has open floor Pluto can reach in time (ArenaProbe + GapScorer), not only by the numbers;
    // - aimed fast shots are narrow (3 bullets, a few degrees of jitter), wide patterns are slow;
    // - projectiles that change behaviour say so: the pill pulses before it bursts, a stitch pulls before it re-aims and
    //   pops as it releases, a cloud blinks before it expires (ThreatReadability.FusePulse, existing sprites only).
    //
    // Blank and death contract (tools/tests/test_vet_brain.py pins it):
    // - every Script sets EndOnBlank = true before its first yield: a blank ends the pattern, so no later wave, pump or
    //   follow-up burst of that script fires after it (single-volley scripts set it too, so the rule has no exceptions);
    // - bullets with their own Top (pill, stitch, cloud, curl, net) are ordinary projectiles to a blank: it destroys them with
    //   spawning forbidden, and PillBullet only bursts when PillContract.Bursts allows it (never when preventSpawningProjectiles);
    // - when the Vet dies or the encounter ends, VetVisitController.StopCombat force-stops every owner's BulletScriptSource
    //   first and then kills their projectiles with DieInAir(allowProjectileSpawns: false): no script continues, no pill bursts.
    // The numbers are knobs in PastConfig ([Balance]); tools/tests/test_projectiles.py checks bank names against the art.

    public static class Pace
    {
        public static float S(float tilesPerSecond) { return tilesPerSecond * PastConfig.BulletSpeedScale; }
        public static float Rand(float a, float b) { return Random.Range(a, b); }
        public static int LeadIn { get { return Mathf.Max(0, PastConfig.PatternLeadIn); } }
        /// <summary>Fire direction of slot i of an arc of n bullets centred on aim (n = 1: straight on aim).</summary>
        public static float Arc(float aim, float spread, int n, int i) { return n <= 1 ? aim : aim - spread / 2f + spread * i / (n - 1); }
    }

    public class SyringeBullet : Bullet { public SyringeBullet() : base("syringe", false, false, false) { } }
    public class DartBullet : Bullet { public DartBullet() : base("dart", false, false, false) { } }
    public class VaccineBullet : Bullet { public VaccineBullet() : base("vaccine", false, false, false) { } }
    public class DropletBullet : Bullet { public DropletBullet() : base("droplet", false, false, false) { } }
    public class TranqBullet : Bullet { public TranqBullet() : base("tranq", false, false, false) { } }
    public class TabletBullet : Bullet { public TabletBullet() : base("tablet", false, false, false) { } }
    public class ScalpelBullet : Bullet { public ScalpelBullet() : base("scalpel", false, false, false) { } }

    /// <summary>The net: lobbed, then slows to a drifting zone for three seconds, like the Bullet King's goblet.</summary>
    public class NetBullet : Bullet
    {
        public NetBullet() : base("net", false, false, false) { }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ChangeSpeed(new Speed(Pace.S(2.5f), SpeedType.Absolute), 30);
            yield return Wait(180);
            Vanish(false);
        }
    }

    // ------------------------------------------------------------------ the helpers

    /// <summary>Vet Tech: the Hegemony soldier's three-round burst (Convict's past): 12 frames between rounds, TechBurstSpeed (9),
    /// the first round leads Pluto a little, the others go where he is.</summary>
    public class TechShotScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float speed = Pace.S(PastConfig.TechBurstSpeed);
            for (int i = 0; i < 3; i++)
            {
                float aim = GetAimDirection(i == 0 ? 0.5f : 0f, speed) + Pace.Rand(-3f, 3f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(12);
            }
        }
    }

    /// <summary>Vet Tech: the dart rifle. One fast dart that leads Pluto fully, then an unled one twelve frames later: a straight
    /// strafe eats the first, stopping eats the second.</summary>
    public class DartRifleScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float speed = Pace.S(PastConfig.TechDartSpeed);
            Fire(new Direction(GetAimDirection(1f, speed), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new DartBullet());
            yield return Wait(12);
            Fire(new Direction(GetAimDirection(0f, speed), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new DartBullet());
        }
    }

    /// <summary>Syringe Tech: the syringe shotgun. Five syringes over SyringeFanSpread (40 degrees, 10 apart) at SyringeFanSpeed (8),
    /// then four slower ones in the gaps 24 frames later (the Blue Shotgun Kin's re-pump). It also fires on landing from a lunge,
    /// so it waits the lead-in first: never a point-blank shotgun the frame he lands.</summary>
    public class SyringeShotgunScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            yield return Wait(Pace.LeadIn);
            float spread = PastConfig.SyringeFanSpread, speed = Pace.S(PastConfig.SyringeFanSpeed);
            float aim = GetAimDirection(0f, speed);
            for (int i = 0; i < 5; i++)
                Fire(new Direction(Pace.Arc(aim, spread, 5, i), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new SyringeBullet());
            yield return Wait(24);
            float step = spread / 4f;
            for (int i = 0; i < 4; i++)
                Fire(new Direction(aim - spread / 2f + step / 2f + step * i, DirectionType.Absolute), new Speed(speed * 0.75f, SpeedType.Absolute), new SyringeBullet());
        }
    }

    /// <summary>The Nurse's shotgun syringe: six droplets over NurseFanSpread (60 degrees, 12 apart) at NurseFanSpeed (7), then
    /// five in the gaps 32 frames later: two readable volleys instead of one wall.</summary>
    public class NurseFanScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float spread = PastConfig.NurseFanSpread, speed = Pace.S(PastConfig.NurseFanSpeed);
            float aim = GetAimDirection(0f, speed);
            float step = spread / 5f;
            for (int i = 0; i < 6; i++)
                Fire(new Direction(Pace.Arc(aim, spread, 6, i), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new DropletBullet());
            yield return Wait(32);
            aim = GetAimDirection(0f, speed);   // the second pump re-aims, so standing still is not safe either
            for (int i = 0; i < 5; i++)
                Fire(new Direction(aim - spread / 2f + step / 2f + step * i, DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new DropletBullet());
        }
    }

    /// <summary>The net: a ten-frame wind-up, then one big slow projectile lobbed ahead of Pluto at NurseNetSpeed (6).</summary>
    public class NetThrowScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            yield return Wait(10);
            float speed = Pace.S(PastConfig.NurseNetSpeed);
            Fire(new Direction(GetAimDirection(0.8f, speed), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new NetBullet());
        }
    }

    /// <summary>The Nurse: a tranquilizer hose, twelve green bubbles one every four frames sweeping 80 degrees through Pluto at
    /// NurseSpraySpeed (9, the Gatling Gull's fan spray is 12); the sweep direction is random.</summary>
    public class TranquilizerSprayScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            yield return Wait(Pace.LeadIn);
            float speed = Pace.S(PastConfig.NurseSpraySpeed);
            float aim = GetAimDirection(0f, speed);
            int dir = Random.value < 0.5f ? 1 : -1;
            for (int i = 0; i < 12; i++)
            {
                Fire(new Direction(aim + dir * Pace.Arc(0f, 80f, 12, i), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new TranqBullet());
                yield return Wait(4);
            }
        }
    }

    /// <summary>The Nurse below half health: the IV line. Twelve tranq bubbles five frames apart, alternately 35 degrees either side,
    /// each curling back onto the aim line over half a second at IVLineSpeed (6.5): a braided stream. Step sideways.</summary>
    public class IVLineScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float speed = Pace.S(PastConfig.IVLineSpeed);
            float aim = GetAimDirection(0f, speed);
            for (int i = 0; i < 12; i++)
            {
                Fire(new Direction(aim + (i % 2 == 0 ? 35f : -35f), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new CurlBullet(aim));
                yield return Wait(5);
            }
        }
    }

    public class CurlBullet : Bullet
    {
        private readonly float line;

        public CurlBullet(float line) : base("tranq", false, false, false) { this.line = line; }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ChangeDirection(new Direction(line, DirectionType.Absolute), 30);
            yield return Wait(300);
            Vanish(false);
        }
    }

    // ------------------------------------------------------------------ The Vet, phase 1 (100-60 %): "Consultation"

    /// <summary>Booster Shot: three syringes seven frames apart at BoosterSpeed (11); the first and third lead Pluto (aimed
    /// where he will be), the middle one goes where he is, so a straight strafe does not dodge all three.
    /// Vanilla parallel: the Bullet King's quickshots (speed 12, 6 frames apart).</summary>
    public class BoosterShotScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float speed = Pace.S(PastConfig.BoosterSpeed);
            for (int i = 0; i < 3; i++)
            {
                float aim = GetAimDirection(i == 1 ? 0f : 0.7f, speed) + Pace.Rand(-3f, 3f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(7);
            }
        }
    }

    /// <summary>Spray Bottle (used within 8 tiles): seven teal droplets over SprayBottleSpread (84 degrees, 14 apart) at
    /// SprayBottleSpeed (7), then six slower ones (x0.75) in its gaps 24 frames later, after the lead-in. Two layers at two
    /// speeds: slip through a gap of the first, the second is slower and offset.</summary>
    public class SprayBottleScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            yield return Wait(Pace.LeadIn);
            float spread = PastConfig.SprayBottleSpread, speed = Pace.S(PastConfig.SprayBottleSpeed);
            float aim = GetAimDirection(0f, speed);
            float step = spread / 6f;
            for (int i = 0; i < 7; i++)
                Fire(new Direction(Pace.Arc(aim, spread, 7, i), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new DropletBullet());
            yield return Wait(24);
            for (int i = 0; i < 6; i++)
                Fire(new Direction(aim - spread / 2f + step / 2f + step * i, DirectionType.Absolute), new Speed(speed * 0.75f, SpeedType.Absolute), new DropletBullet());
        }
    }

    /// <summary>A pill drifts for 50 frames (about three tiles), then bursts into six tablets at PillBurstSpeed (5.5), one heading
    /// for Pluto, 60 degrees apart. For its last 24 frames it pulses (the fuse). Shooting it pops it early: a player shot that
    /// touches it (ShotProbe, swept over the shot's last frame) bursts it where it is, the same choice the Bullet King's big
    /// bullet offers, and the shot is spent unless it pierces. A blank, the Vet's death or the encounter clearing it forbid
    /// spawns, and then it never bursts (PillContract).</summary>
    public class PillBullet : Bullet
    {
        public const int Fuse = 50, FuseWarn = 24, FusePeriod = 8;
        private bool burst;

        public PillBullet() : base("pill", false, false, false) { }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ProjectileLook.Reset(Projectile, "pill");
            for (int left = Fuse; left > 0; left--)
            {
                if (PlayerShotTouches())
                {
                    if (PillContract.Bursts(PillEnd.PlayerShot, false)) Burst();
                    Vanish(false);
                    yield break;
                }
                ProjectileLook.SetScale(Projectile, "pill", FusePulse.Flash(left, FuseWarn, FusePeriod) ? 1.3f : 1f);
                yield return Wait(1);
            }
            ProjectileLook.SetScale(Projectile, "pill", 1f);
            if (PillContract.Bursts(PillEnd.Fuse, false)) Burst();
            Vanish(false);
        }

        public override void OnBulletDestruction(DestroyType destroyType, SpeculativeRigidbody hitRigidbody, bool preventSpawningProjectiles)
        {
            ProjectileLook.Reset(Projectile, "pill");
            if (PillContract.Bursts(PillEnd.Destroyed, preventSpawningProjectiles)) Burst();
        }

        private bool PlayerShotTouches()
        {
            if (Projectile == null) return false;
            Projectile shot = ShotProbe.PlayerShotTouching(Position, ShotProbe.PillRadius);
            if (shot == null) return false;
            if (shot.GetComponent<PierceProjModifier>() == null) shot.DieInAir(false, true, true, false);
            return true;
        }

        private void Burst()
        {
            if (burst) return;
            burst = true;
            float speed = Pace.S(PastConfig.PillBurstSpeed);
            float start = GetAimDirection(0f, speed);
            for (int i = 0; i < 6; i++)
                Fire(new Direction(SubdivideCircle(start, 6, i), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new TabletBullet());
        }
    }

    /// <summary>Pill Time: four slow pills (speed 4) in a 60-degree fan, one every eight frames; each bursts (PillBullet).</summary>
    public class PillTimeScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float aim = GetAimDirection(0f, Pace.S(4f));
            for (int i = 0; i < 4; i++)
            {
                Fire(new Direction(Pace.Arc(aim, 60f, 4, i), DirectionType.Absolute), new Speed(Pace.S(4f), SpeedType.Absolute), new PillBullet());
                yield return Wait(8);
            }
            yield return Wait(20);
        }
    }

    // ------------------------------------------------------------------ phase 2 (60-25 %): "Treatment"

    /// <summary>Rings with a hole: slots [gap, gap + gapSlots) of an n-bullet ring are skipped.</summary>
    public static class Ring
    {
        public static int GapSlots(int n) { return Mathf.Clamp(PastConfig.RingGapSlots, 1, n / 2); }
        public static bool InGap(int i, int gap, int slots, int n) { return ((i - gap) % n + n) % n < slots; }

        /// <summary>The centre angle of every possible hole (index = its first skipped slot) of a ring fired with SubdivideCircle.</summary>
        public static float[] GapCentres(float start, int n, int slots)
        {
            float[] centres = new float[n];
            for (int g = 0; g < n; g++) centres[g] = start + (g + (slots - 1) / 2f) * 360f / n;
            return centres;
        }

        /// <summary>A scored hole, or a random one when the arena cannot be read.</summary>
        public static int PickGap(Bullet script, float start, int n, int slots, float speed)
        {
            int gap = ArenaProbe.PickGap(script, GapCentres(start, n, slots), speed);
            return gap >= 0 ? gap : Random.Range(0, n);
        }
    }

    /// <summary>Cone of Shame: after the lead-in, a ring of twenty vaccine orbs with a RingGapSlots (3 = 54 degrees) hole, then a
    /// second ring offset by half a step through the same hole, 28 frames apart at RingSpeed (5.5). The hole opens where there is
    /// open floor Pluto can reach in time (ArenaProbe.PickGap), at random among the good ones.
    /// Vanilla rings run 18 to 36 bullets at 5 to 8. Ends on a blank, like every vanilla ring.</summary>
    public class ConeOfShameScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            yield return Wait(Pace.LeadIn);
            const int n = 20;
            float start = RandomAngle(), speed = Pace.S(PastConfig.RingSpeed);
            int slots = Ring.GapSlots(n), gap = Ring.PickGap(this, start, n, slots, speed);   // ArenaProbe.PickGap inside
            for (int ring = 0; ring < 2; ring++)
            {
                for (int i = 0; i < n; i++)
                    if (!Ring.InGap(i, gap, slots, n))
                        Fire(new Direction(SubdivideCircle(start, n, i, 1f, ring == 1), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new VaccineBullet());
                yield return Wait(28);
            }
        }
    }

    /// <summary>Droplet Wall: a 130-degree curtain of fifteen teal slots at WallSpeed (6) with a WallGapSlots (3, about 28 degrees)
    /// hole. The hole opens near Pluto (of the three slots around him, the one with the most open floor) and walks two slots for
    /// the second wave, 34 frames later: find the hole, then follow it (the Gorgun's scream rule).</summary>
    public class DropletWallScript : Script
    {
        protected virtual float SpeedBonus { get { return 0f; } }
        protected virtual int WaveGap { get { return 34; } }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            if (SpeedBonus > 0f && BulletBank != null) ClinicSound.Play("Play_ENM_deathray_charge_01", BulletBank.gameObject);   // the phase-3 wall charges up
            yield return Wait(Pace.LeadIn);
            float speed = Pace.S(PastConfig.WallSpeed + SpeedBonus);
            float aim = GetAimDirection(0.3f, speed);
            int slots = Mathf.Clamp(PastConfig.WallGapSlots, 2, 6);
            int centred = 7 - slots / 2;
            int[] options = { Mathf.Clamp(centred - 1, 1, 14 - slots), Mathf.Clamp(centred, 1, 14 - slots), Mathf.Clamp(centred + 1, 1, 14 - slots) };
            float[] centres = new float[options.Length];
            for (int k = 0; k < options.Length; k++) centres[k] = aim - 65f + 130f * (options[k] + (slots - 1) / 2f) / 14f;
            int pick = ArenaProbe.PickGap(this, centres, speed);
            int gap = pick >= 0 ? options[pick] : Mathf.Clamp(centred + Random.Range(-1, 2), 1, 14 - slots);   // centred on Pluto, give or take one slot
            int walk = Random.value < 0.5f ? -2 : 2;
            for (int wave = 0; wave < 2; wave++)
            {
                for (int i = 0; i < 15; i++)
                {
                    if (i >= gap && i < gap + slots) continue;
                    Fire(new Direction(Pace.Arc(aim, 130f, 15, i), DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new DropletBullet());
                }
                gap = Mathf.Clamp(gap + walk, 1, 14 - slots);
                yield return Wait(WaveGap);
            }
        }
    }

    /// <summary>Phase-3 wall: the same curtain one tile a second faster and 28 frames between waves (vanilla "hard" variants add +1).</summary>
    public class DropletWallHardScript : DropletWallScript
    {
        protected override float SpeedBonus { get { return 1f; } }
        protected override int WaveGap { get { return 28; } }
    }

    /// <summary>Vaccination Spiral: four arms of vaccine orbs rotating 11 degrees a wave, four frames apart, for 24 waves (1.6 s) at
    /// SpiralSpeed (5.5). Gentler than the King's six-arm spiral (37 degrees, speed 7); the arms stay 90 degrees apart, so the
    /// lanes are wide. The arms start 1.2 tiles out so they do not clip the Vet's own sprite. Walk around it.</summary>
    public class VaccinationSpiralScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            if (BulletBank != null) ClinicSound.Play("Play_ENM_deathray_charge_01", BulletBank.gameObject);
            yield return Wait(Pace.LeadIn);
            float start = RandomAngle(), speed = Pace.S(PastConfig.SpiralSpeed);
            int dir = Random.value < 0.5f ? 1 : -1;
            for (int t = 0; t < 24; t++)
            {
                for (int arm = 0; arm < 4; arm++)
                {
                    float a = start + dir * t * 11f + arm * 90f;
                    Fire(new Offset(1.2f, 0f, a, string.Empty), new Direction(a, DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new VaccineBullet());
                }
                yield return Wait(4);
            }
        }
    }

    /// <summary>The Vet: the scalpel ring. After the lead-in, twenty-four scalpels (15 degrees apart) at ScalpelSpeed (6) with a
    /// ScalpelGapDegrees (60) hole placed 45-90 degrees off Pluto (never on him: walk to it; of the eight candidate openings the
    /// one with open floor he can reach), then three aimed syringes at BoosterSpeed - 1 (10).</summary>
    public class ScalpelRingScript : Script
    {
        private static readonly float[] Offsets = { 45f, 60f, 75f, 90f, -45f, -60f, -75f, -90f };

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            yield return Wait(Pace.LeadIn);
            float speed = Pace.S(PastConfig.ScalpelSpeed);
            float aim = GetAimDirection(0f, speed);
            float[] centres = new float[Offsets.Length];
            for (int k = 0; k < Offsets.Length; k++) centres[k] = aim + Offsets[k];
            int pick = ArenaProbe.PickGap(this, centres, speed);
            float gapCentre = pick >= 0 ? centres[pick] : aim + (Random.value < 0.5f ? 1f : -1f) * Random.Range(45f, 90f);
            float half = Mathf.Clamp(PastConfig.ScalpelGapDegrees, 20f, 120f) / 2f;
            for (int i = 0; i < 24; i++)
            {
                float a = aim + i * 15f;
                if (Mathf.Abs(Mathf.DeltaAngle(a, gapCentre)) < half) continue;
                Fire(new Direction(a, DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new ScalpelBullet());
            }
            yield return Wait(30);
            float aimed = Pace.S(PastConfig.BoosterSpeed - 1f);
            for (int i = 0; i < 3; i++)
            {
                Fire(new Direction(GetAimDirection(0.5f, aimed), DirectionType.Absolute), new Speed(aimed, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(7);
            }
        }
    }

    /// <summary>A suture that stops, hangs where Pluto can see it, then re-aims at him at StitchSpeed (9). For the last PullWindow
    /// frames of the hang it pulses (the needle pulls), and it pops as it releases: the release rhythm is readable per stitch.</summary>
    public class StitchBullet : Bullet
    {
        public const int PullWindow = 12, PullPeriod = 6, ReleasePop = 8;
        private readonly int hold;

        public StitchBullet(int hold) : base("stitch", false, false, false) { this.hold = hold; }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ProjectileLook.Reset(Projectile, "stitch");
            ChangeSpeed(new Speed(0f, SpeedType.Absolute), 20);
            int hang = 20 + hold;
            for (int f = 0; f < hang; f++)
            {
                ProjectileLook.SetScale(Projectile, "stitch", FusePulse.Flash(hang - f, PullWindow, PullPeriod) ? 1.2f : 1f);
                yield return Wait(1);
            }
            ChangeDirection(new Direction(0f, DirectionType.Aim), 1);
            ChangeSpeed(new Speed(Pace.S(PastConfig.StitchSpeed), SpeedType.Absolute), 12);
            for (int f = 0; f < ReleasePop; f++)
            {
                ProjectileLook.SetScale(Projectile, "stitch", FusePulse.Pop(f, ReleasePop, 1.5f));
                yield return Wait(1);
            }
            ProjectileLook.SetScale(Projectile, "stitch", 1f);
            yield return Wait(240 - ReleasePop);
            Vanish(false);
        }

        public override void OnBulletDestruction(DestroyType destroyType, SpeculativeRigidbody hitRigidbody, bool preventSpawningProjectiles)
        {
            ProjectileLook.Reset(Projectile, "stitch");
        }
    }

    /// <summary>The Vet: stitches. Eight sutures in a 110-degree fan at 10 stop, hang half a second, then re-aim one by one six
    /// frames apart (a readable ripple, not a volley).</summary>
    public class StitchesScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float aim = GetAimDirection(0f, Pace.S(10f));
            for (int i = 0; i < 8; i++)
                Fire(new Direction(Pace.Arc(aim, 110f, 8, i), DirectionType.Absolute), new Speed(Pace.S(10f), SpeedType.Absolute), new StitchBullet(30 + 6 * i));
            yield return Wait(100);
        }
    }

    /// <summary>A big slow cloud that drifts to a near stop and lingers four seconds. It blinks (mostly visible, it still hurts)
    /// for its last ExpiryWindow frames, and ring and wall openings avoid it while it lives (LingeringHazards).</summary>
    public class CloudBullet : Bullet
    {
        public const int Life = 240, ExpiryWindow = 45;

        public CloudBullet() : base("cloud", false, false, false) { }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ProjectileLook.Reset(Projectile, "cloud");
            LingeringHazards.Add(this);
            ChangeSpeed(new Speed(Pace.S(0.6f), SpeedType.Absolute), 60);
            for (int left = Life; left > 0; left--)
            {
                ProjectileLook.SetVisible(Projectile, FusePulse.Visible(left, ExpiryWindow, 5, 2));
                yield return Wait(1);
            }
            LingeringHazards.Remove(this);
            ProjectileLook.SetVisible(Projectile, true);
            Vanish(false);
        }

        public override void OnBulletDestruction(DestroyType destroyType, SpeculativeRigidbody hitRigidbody, bool preventSpawningProjectiles)
        {
            LingeringHazards.Remove(this);
            ProjectileLook.Reset(Projectile, "cloud");
        }
    }

    /// <summary>The Vet: anesthesia. Seven clouds in a 120-degree arc at 4 that settle and linger (they shape the arena, they
    /// do not snipe), then a three-syringe booster at BoosterSpeed - 1 (10).</summary>
    public class AnesthesiaCloudScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float aim = GetAimDirection(0f, Pace.S(4f));
            for (int i = 0; i < 7; i++)
                Fire(new Direction(Pace.Arc(aim, 120f, 7, i), DirectionType.Absolute), new Speed(Pace.S(4f), SpeedType.Absolute), new CloudBullet());
            yield return Wait(40);
            float aimed = Pace.S(PastConfig.BoosterSpeed - 1f);
            for (int i = 0; i < 3; i++)
            {
                Fire(new Direction(GetAimDirection(i == 1 ? 0f : 0.7f, aimed), DirectionType.Absolute), new Speed(aimed, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(7);
            }
        }
    }

    // ------------------------------------------------------------------ phase 3 (last quarter): "Just a little snip"

    /// <summary>Snip Time: five fast leading syringes six frames apart at SnipSpeed (12, the King's quickshot speed), then, fourteen
    /// frames later, a ring of sixteen vaccine orbs at RingSpeed + 0.5 with a RingGapSlots hole on open floor.</summary>
    public class SnipTimeScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float speed = Pace.S(PastConfig.SnipSpeed);
            for (int i = 0; i < 5; i++)
            {
                float aim = GetAimDirection(0.8f, speed) + Pace.Rand(-4f, 4f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(speed, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(6);
            }
            yield return Wait(14);
            const int n = 16;
            float ring = RandomAngle(), ringSpeed = Pace.S(PastConfig.RingSpeed + 0.5f);
            int slots = Ring.GapSlots(n), gap = Ring.PickGap(this, ring, n, slots, ringSpeed);   // ArenaProbe.PickGap inside
            for (int i = 0; i < n; i++)
                if (!Ring.InGap(i, gap, slots, n))
                    Fire(new Direction(SubdivideCircle(ring, n, i), DirectionType.Absolute), new Speed(ringSpeed, SpeedType.Absolute), new VaccineBullet());
        }
    }
}
