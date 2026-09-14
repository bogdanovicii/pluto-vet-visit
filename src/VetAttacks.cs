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
}
