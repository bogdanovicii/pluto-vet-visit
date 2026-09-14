using System.Collections;
using Brave.BulletScript;
using UnityEngine;

namespace PlutoVetVisit
{
    // Bullet scripts run at 60 frames per second: Wait(8) is eight frames. Speeds are tiles per second and
    // are scaled by PastConfig.BulletSpeedScale (1 = the numbers below, which sit in the vanilla floor-boss
    // band: slow rings 5-6, spirals 7, aimed bursts 10-12; Bullet King quickshots are 12, Gorgun's scream 7).
    // Bank names must exist on the actor's AIBulletBank (VetBoss adds "syringe", "droplet", "pill"; the Nurse
    // "droplet" and "net"; the Tech "syringe"). Every enemy projectile does half a heart, as in vanilla.

    public static class Pace
    {
        public static float S(float tilesPerSecond) { return tilesPerSecond * PastConfig.BulletSpeedScale; }
        public static float Rand(float a, float b) { return Random.Range(a, b); }
    }

    public class SyringeBullet : Bullet
    {
        public SyringeBullet() : base("syringe", false, false, false) { }
    }

    public class DropletBullet : Bullet
    {
        public DropletBullet() : base("droplet", false, false, false) { }
    }

    /// <summary>The net: lobbed, then slows to a drifting zone for three seconds, like the Bullet King's goblet.</summary>
    public class NetBullet : Bullet
    {
        public NetBullet() : base("net", false, false, false) { }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ChangeSpeed(new Speed(Pace.S(3.5f), SpeedType.Absolute), 30);
            yield return Wait(180);
            Vanish(false);
        }
    }

    /// <summary>Vet Tech: the Hegemony soldier's three-round burst (Convict's past): 12 frames between rounds,
    /// speed 8, the first round leads Pluto a little, the others go where he is.</summary>
    public class TechShotScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int i = 0; i < 3; i++)
            {
                float aim = GetAimDirection(i == 0 ? 0.5f : 0f, Pace.S(8f)) + Pace.Rand(-3f, 3f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(Pace.S(8f), SpeedType.Absolute), new SyringeBullet());
                yield return Wait(12);
            }
        }
    }

    /// <summary>The Nurse's shotgun syringe: a fan of seven droplets over 50 degrees, pumped twice half a step
    /// apart (the Blue Shotgun Kin's two volleys), 30 frames between pumps.</summary>
    public class NurseFanScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int pump = 0; pump < 2; pump++)
            {
                float aim = GetAimDirection(0f, Pace.S(8f));
                float start = aim - 25f - (pump == 1 ? 50f / 7f / 2f : 0f);   // half a step, fan stays centred on Pluto
                for (int i = 0; i < 7; i++)
                    Fire(new Direction(SubdivideArc(start, 50f, 7, i), DirectionType.Absolute), new Speed(Pace.S(8f), SpeedType.Absolute), new DropletBullet());
                yield return Wait(30);
            }
        }
    }

    /// <summary>The net: a ten-frame wind-up, then one big slow projectile lobbed ahead of Pluto.</summary>
    public class NetThrowScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            yield return Wait(10);
            Fire(new Direction(GetAimDirection(0.8f, Pace.S(5f)), DirectionType.Absolute), new Speed(Pace.S(5f), SpeedType.Absolute), new NetBullet());
        }
    }

    // ------------------------------------------------------------------ The Vet, phase 1 (100-60 %): "Consultation"

    /// <summary>Booster Shot: three syringes six frames apart at speed 10; the first and third lead Pluto (aimed
    /// where he will be), the middle one goes where he is, so a straight strafe does not dodge all three.
    /// Vanilla parallel: the Bullet King's quickshots (speed 12, 6 frames apart).</summary>
    public class BoosterShotScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int i = 0; i < 3; i++)
            {
                float aim = GetAimDirection(i == 1 ? 0f : 0.7f, Pace.S(10f)) + Pace.Rand(-3f, 3f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(Pace.S(10f), SpeedType.Absolute), new SyringeBullet());
                yield return Wait(6);
            }
        }
    }

    /// <summary>Spray Bottle: two fans of nine droplets over 80 degrees (10 degrees apart, Beholster uses 20 for
    /// seven) centred on Pluto, the second shifted half a step so it fills the first's gaps; 22 frames apart, speed 7.</summary>
    public class SprayBottleScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int wave = 0; wave < 2; wave++)
            {
                float aim = GetAimDirection(0f, Pace.S(7f));
                float start = aim - 40f - (wave == 1 ? 5f : 0f);
                for (int i = 0; i < 9; i++)
                    Fire(new Direction(SubdivideArc(start, 80f, 9, i), DirectionType.Absolute), new Speed(Pace.S(7f), SpeedType.Absolute), new DropletBullet());
                yield return Wait(22);
            }
        }
    }

    /// <summary>A pill drifts for 40 frames, then bursts into six droplets (one always heads for Pluto). Shooting it
    /// pops it early, the same choice the Bullet King's big bullet offers.</summary>
    public class PillBullet : Bullet
    {
        private bool burst;

        public PillBullet() : base("pill", false, false, false) { }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            yield return Wait(40);
            Burst();
            Vanish(false);
        }

        public override void OnBulletDestruction(DestroyType destroyType, SpeculativeRigidbody hitRigidbody, bool preventSpawningProjectiles)
        {
            if (!preventSpawningProjectiles) Burst();
        }

        private void Burst()
        {
            if (burst) return;
            burst = true;
            float start = GetAimDirection(0f, Pace.S(6f));
            for (int i = 0; i < 6; i++)
                Fire(new Direction(SubdivideCircle(start, 6, i), DirectionType.Absolute), new Speed(Pace.S(6f), SpeedType.Absolute), new DropletBullet());
        }
    }

    /// <summary>Pill Time: four slow pills in a 60-degree fan, one every six frames; each bursts (PillBullet).</summary>
    public class PillTimeScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            float aim = GetAimDirection(0f, Pace.S(4f));
            for (int i = 0; i < 4; i++)
            {
                Fire(new Direction(SubdivideArc(aim - 30f, 60f, 4, i), DirectionType.Absolute), new Speed(Pace.S(4f), SpeedType.Absolute), new PillBullet());
                yield return Wait(6);
            }
            yield return Wait(20);
        }
    }

    // ------------------------------------------------------------------ phase 2 (60-25 %): "Treatment"

    /// <summary>Cone of Shame: a ring of sixteen syringes, then a second ring offset by half a step, 24 frames
    /// apart at speed 5.5 (vanilla rings run 18 to 36 bullets at 5 to 8). Ends on a blank, like every vanilla ring.</summary>
    public class ConeOfShameScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float start = RandomAngle();
            for (int ring = 0; ring < 2; ring++)
            {
                for (int i = 0; i < 16; i++)
                    Fire(new Direction(SubdivideCircle(start, 16, i, 1f, ring == 1), DirectionType.Absolute), new Speed(Pace.S(5.5f), SpeedType.Absolute), new SyringeBullet());
                yield return Wait(24);
            }
        }
    }

    /// <summary>Droplet Wall: a 130-degree curtain of fifteen slots at speed 6 with a three-slot gap (about 28
    /// degrees). The gap opens near Pluto and walks two slots for the second wave: find the hole, then follow it,
    /// the Gorgun's scream rule (its gaps start at the player's angle and drift each wave).</summary>
    public class DropletWallScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float aim = GetAimDirection(0.3f, Pace.S(6f));
            int gap = 6 + Random.Range(-1, 2);             // slots 5..7 of 0..14: on Pluto, give or take one
            int walk = Random.value < 0.5f ? -2 : 2;
            for (int wave = 0; wave < 2; wave++)
            {
                for (int i = 0; i < 15; i++)
                {
                    if (i >= gap && i < gap + 3) continue;
                    Fire(new Direction(SubdivideArc(aim - 65f, 130f, 15, i), DirectionType.Absolute), new Speed(Pace.S(6f), SpeedType.Absolute), new DropletBullet());
                }
                gap = Mathf.Clamp(gap + walk, 1, 11);
                yield return Wait(30);
            }
        }
    }

    /// <summary>Vaccination Spiral: four arms of syringes rotating 11 degrees a wave, four frames apart, for 24
    /// waves (1.6 s) at speed 5. Gentler than the King's six-arm spiral (37 degrees, speed 7). The arms start
    /// 1.2 tiles out so they do not clip the Vet's own sprite. Walk around it.</summary>
    public class VaccinationSpiralScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float start = RandomAngle();
            int dir = Random.value < 0.5f ? 1 : -1;
            for (int t = 0; t < 24; t++)
            {
                for (int arm = 0; arm < 4; arm++)
                {
                    float a = start + dir * t * 11f + arm * 90f;
                    Fire(new Offset(1.2f, 0f, a, string.Empty), new Direction(a, DirectionType.Absolute), new Speed(Pace.S(5f), SpeedType.Absolute), new SyringeBullet());
                }
                yield return Wait(4);
            }
        }
    }

    // ------------------------------------------------------------------ phase 3 (last quarter): "Just a little snip"

    /// <summary>Snip Time: five fast leading syringes five frames apart at speed 12 (the King's quickshot speed),
    /// then, ten frames later, a ring of twelve droplets at 6.</summary>
    public class SnipTimeScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int i = 0; i < 5; i++)
            {
                float aim = GetAimDirection(0.8f, Pace.S(12f)) + Pace.Rand(-4f, 4f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(Pace.S(12f), SpeedType.Absolute), new SyringeBullet());
                yield return Wait(5);
            }
            yield return Wait(10);
            float ring = RandomAngle();
            for (int i = 0; i < 12; i++)
                Fire(new Direction(SubdivideCircle(ring, 12, i), DirectionType.Absolute), new Speed(Pace.S(6f), SpeedType.Absolute), new DropletBullet());
        }
    }

    /// <summary>Phase-3 wall: the same curtain one tile a second faster (vanilla "hard" variants add +1 speed).</summary>
    public class DropletWallHardScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float aim = GetAimDirection(0.3f, Pace.S(7f));
            int gap = 6 + Random.Range(-1, 2);
            int walk = Random.value < 0.5f ? -2 : 2;
            for (int wave = 0; wave < 2; wave++)
            {
                for (int i = 0; i < 15; i++)
                {
                    if (i >= gap && i < gap + 3) continue;
                    Fire(new Direction(SubdivideArc(aim - 65f, 130f, 15, i), DirectionType.Absolute), new Speed(Pace.S(7f), SpeedType.Absolute), new DropletBullet());
                }
                gap = Mathf.Clamp(gap + walk, 1, 11);
                yield return Wait(26);
            }
        }
    }

    // ------------------------------------------------------------------ 0.11: weapon-like helpers and the Vet's surgery set

    /// <summary>Syringe Tech: the syringe shotgun. Five syringes over 36 degrees at 9, then four at 7 in the gaps 20 frames
    /// later (the Blue Shotgun Kin's re-pump).</summary>
    public class SyringeShotgunScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            float aim = GetAimDirection(0f, Pace.S(9f));
            for (int i = 0; i < 5; i++)
                Fire(new Direction(SubdivideArc(aim - 18f, 36f, 5, i), DirectionType.Absolute), new Speed(Pace.S(9f), SpeedType.Absolute), new SyringeBullet());
            yield return Wait(20);
            for (int i = 0; i < 4; i++)
                Fire(new Direction(aim - 13.5f + 9f * i, DirectionType.Absolute), new Speed(Pace.S(7f), SpeedType.Absolute), new SyringeBullet());
        }
    }

    /// <summary>Vet Tech: the dart rifle. One fast dart that leads Pluto fully, then an unled one eight frames later: a straight
    /// strafe eats the first, stopping eats the second.</summary>
    public class DartRifleScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            Fire(new Direction(GetAimDirection(1f, Pace.S(12f)), DirectionType.Absolute), new Speed(Pace.S(12f), SpeedType.Absolute), new SyringeBullet());
            yield return Wait(8);
            Fire(new Direction(GetAimDirection(0f, Pace.S(12f)), DirectionType.Absolute), new Speed(Pace.S(12f), SpeedType.Absolute), new SyringeBullet());
        }
    }

    /// <summary>The Nurse: a tranquilizer hose, fourteen droplets one every three frames sweeping 70 degrees through Pluto at 8
    /// (the Gatling Gull's fan spray); the sweep direction is random.</summary>
    public class TranquilizerSprayScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            float aim = GetAimDirection(0f, Pace.S(8f));
            int dir = Random.value < 0.5f ? 1 : -1;
            for (int i = 0; i < 14; i++)
            {
                Fire(new Direction(aim + dir * (-35f + 70f * i / 13f), DirectionType.Absolute), new Speed(Pace.S(8f), SpeedType.Absolute), new DropletBullet());
                yield return Wait(3);
            }
        }
    }

    /// <summary>The Nurse below half health: the IV line. Twelve droplets five frames apart, alternately 35 degrees either side,
    /// each curling back onto the aim line over half a second: a braided stream. Step sideways.</summary>
    public class IVLineScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            float aim = GetAimDirection(0f, Pace.S(7f));
            for (int i = 0; i < 12; i++)
            {
                Fire(new Direction(aim + (i % 2 == 0 ? 35f : -35f), DirectionType.Absolute), new Speed(Pace.S(7f), SpeedType.Absolute), new CurlBullet(aim));
                yield return Wait(5);
            }
        }
    }

    public class CurlBullet : Bullet
    {
        private readonly float line;

        public CurlBullet(float line) : base("droplet", false, false, false) { this.line = line; }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ChangeDirection(new Direction(line, DirectionType.Absolute), 30);
            yield return Wait(300);
            Vanish(false);
        }
    }

    /// <summary>The Vet: the scalpel ring. Twenty-four syringes at 6 with a 60-degree gap placed 45-90 degrees off Pluto (never
    /// on him), then three aimed syringes at 10.</summary>
    public class ScalpelRingScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float aim = GetAimDirection(0f, Pace.S(6f));
            float gapCentre = aim + (Random.value < 0.5f ? 1f : -1f) * Random.Range(45f, 90f);
            for (int i = 0; i < 24; i++)
            {
                float a = aim + i * 15f;
                if (Mathf.Abs(Mathf.DeltaAngle(a, gapCentre)) < 30f) continue;
                Fire(new Direction(a, DirectionType.Absolute), new Speed(Pace.S(6f), SpeedType.Absolute), new SyringeBullet());
            }
            yield return Wait(30);
            for (int i = 0; i < 3; i++)
            {
                Fire(new Direction(GetAimDirection(0.5f, Pace.S(10f)), DirectionType.Absolute), new Speed(Pace.S(10f), SpeedType.Absolute), new SyringeBullet());
                yield return Wait(6);
            }
        }
    }

    /// <summary>A syringe that stops, hangs where Pluto can see it, then re-aims at him.</summary>
    public class StitchBullet : Bullet
    {
        private readonly int hold;

        public StitchBullet(int hold) : base("syringe", false, false, false) { this.hold = hold; }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ChangeSpeed(new Speed(0f, SpeedType.Absolute), 20);
            yield return Wait(20 + hold);
            ChangeDirection(new Direction(0f, DirectionType.Aim), 1);
            ChangeSpeed(new Speed(Pace.S(9f), SpeedType.Absolute), 12);
            yield return Wait(240);
            Vanish(false);
        }
    }

    /// <summary>The Vet: stitches. Eight syringes in a 100-degree fan at 10 stop, hang half a second, then re-aim one by one
    /// five frames apart.</summary>
    public class StitchesScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float aim = GetAimDirection(0f, Pace.S(10f));
            for (int i = 0; i < 8; i++)
                Fire(new Direction(SubdivideArc(aim - 50f, 100f, 8, i), DirectionType.Absolute), new Speed(Pace.S(10f), SpeedType.Absolute), new StitchBullet(30 + 5 * i));
            yield return Wait(90);
        }
    }

    /// <summary>A big slow cloud that drifts to a near stop and lingers four seconds.</summary>
    public class CloudBullet : Bullet
    {
        public CloudBullet() : base("cloud", false, false, false) { }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            ChangeSpeed(new Speed(Pace.S(0.6f), SpeedType.Absolute), 60);
            yield return Wait(240);
            Vanish(false);
        }
    }

    /// <summary>The Vet: anesthesia. Seven clouds in a 120-degree arc at 4 that settle and linger (they shape the arena, they
    /// do not snipe), then a three-syringe booster.</summary>
    public class AnesthesiaCloudScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            EndOnBlank = true;
            float aim = GetAimDirection(0f, Pace.S(4f));
            for (int i = 0; i < 7; i++)
                Fire(new Direction(SubdivideArc(aim - 60f, 120f, 7, i), DirectionType.Absolute), new Speed(Pace.S(4f), SpeedType.Absolute), new CloudBullet());
            yield return Wait(40);
            for (int i = 0; i < 3; i++)
            {
                Fire(new Direction(GetAimDirection(i == 1 ? 0f : 0.7f, Pace.S(10f)), DirectionType.Absolute), new Speed(Pace.S(10f), SpeedType.Absolute), new SyringeBullet());
                yield return Wait(6);
            }
        }
    }
}
