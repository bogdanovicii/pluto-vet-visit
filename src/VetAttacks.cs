using System.Collections;
using Brave.BulletScript;

namespace PlutoVetVisit
{
    // Bullet scripts run at 60 frames per second: Wait(8) is eight frames. Speeds are tiles per second.
    // Bank names must exist on the boss's AIBulletBank (VetBoss adds "syringe", "droplet" and "pill").

    public class SyringeBullet : Bullet
    {
        public SyringeBullet() : base("syringe", false, false, false) { }
    }

    public class DropletBullet : Bullet
    {
        public DropletBullet() : base("droplet", false, false, false) { }
    }

    public class NetBullet : Bullet
    {
        public NetBullet() : base("net", false, false, false) { }
    }

    /// <summary>Vet Tech: one aimed syringe with a little lead, like a Bullet Kin's shot but slower.</summary>
    public class TechShotScript : Script
    {
        // Three-round burst, five frames apart, like the Hegemony soldiers of the Convict's past; the first
        // shot leads Pluto, the others go where he is, so a strafe dodges some but not all.
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int i = 0; i < 3; i++)
            {
                float aim = GetAimDirection(i == 0 ? 0.5f : 0f, 9f) + UnityEngine.Random.Range(-3f, 3f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(9f, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(5);
            }
        }
    }

    /// <summary>The Nurse's shotgun syringe: one fan of seven droplets over 50 degrees, pumped twice.</summary>
    public class NurseFanScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int pump = 0; pump < 2; pump++)
            {
                float aim = GetAimDirection(0f, 8f);
                for (int i = 0; i < 7; i++)
                    Fire(new Direction(SubdivideArc(aim - 25f, 50f, 7, i, pump == 1), DirectionType.Absolute), new Speed(8f, SpeedType.Absolute), new DropletBullet());
                yield return Wait(18);
            }
        }
    }

    /// <summary>The net: one big slow projectile lobbed at Pluto; easy to see, awkward to sidestep up close.</summary>
    public class NetThrowScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            yield return Wait(10);
            Fire(new Direction(GetAimDirection(0.8f, 5f), DirectionType.Absolute), new Speed(5f, SpeedType.Absolute), new NetBullet());
        }
    }

    /// <summary>Booster Shot: three syringes that lead Pluto (aimed where he will be), six frames apart, with a
    /// little scatter so a straight strafe does not dodge all three.</summary>
    public class BoosterShotScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int i = 0; i < 3; i++)
            {
                float aim = GetAimDirection(i == 1 ? 0f : 0.7f, 10f) + UnityEngine.Random.Range(-3f, 3f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(10f, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(6);
            }
        }
    }

    /// <summary>Spray Bottle: two fans of nine droplets over 80 degrees centred on Pluto, the second offset by half a step.</summary>
    public class SprayBottleScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int wave = 0; wave < 2; wave++)
            {
                float aim = GetAimDirection(0f, 7f);
                for (int i = 0; i < 9; i++)
                    Fire(new Direction(SubdivideArc(aim - 40f, 80f, 9, i, wave == 1), DirectionType.Absolute), new Speed(7f, SpeedType.Absolute), new DropletBullet());
                yield return Wait(22);
            }
        }
    }

    /// <summary>A pill drifts for 40 frames, then bursts into six droplets and vanishes.</summary>
    public class PillBullet : Bullet
    {
        public PillBullet() : base("pill", false, false, false) { }

        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            yield return Wait(40);
            float start = GetAimDirection(0f, 6f);   // one droplet of the burst always heads for Pluto
            for (int i = 0; i < 6; i++)
                Fire(new Direction(SubdivideCircle(start, 6, i), DirectionType.Absolute), new Speed(6f, SpeedType.Absolute), new DropletBullet());
            Vanish(false);
        }
    }

    /// <summary>Pill Time: four slow pills in a narrow fan; each bursts (PillBullet).</summary>
    public class PillTimeScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            float aim = GetAimDirection(0f, 4f);
            for (int i = 0; i < 4; i++)
            {
                Fire(new Direction(SubdivideArc(aim - 30f, 60f, 4, i), DirectionType.Absolute), new Speed(4f, SpeedType.Absolute), new PillBullet());
                yield return Wait(6);
            }
            yield return Wait(20);
        }
    }

    /// <summary>Cone of Shame (below half health): a ring of sixteen syringes, then a second ring offset by half a step.</summary>
    public class ConeOfShameScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int ring = 0; ring < 2; ring++)
            {
                for (int i = 0; i < 16; i++)
                    Fire(new Direction(SubdivideCircle(0f, 16, i, 1f, ring == 1), DirectionType.Absolute), new Speed(5.5f, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(24);
            }
        }
    }

    /// <summary>Droplet Wall (phase 2+): a 130-degree curtain of droplets with a two-droplet gap that opens
    /// somewhere in it, twice. Read the gap and step through it.</summary>
    public class DropletWallScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int wave = 0; wave < 2; wave++)
            {
                float aim = GetAimDirection(0.3f, 6f);
                int gap = UnityEngine.Random.Range(3, 11);          // of 15 slots, never at the very edge
                for (int i = 0; i < 15; i++)
                {
                    if (i == gap || i == gap + 1) continue;
                    Fire(new Direction(SubdivideArc(aim - 65f, 130f, 15, i), DirectionType.Absolute), new Speed(6f, SpeedType.Absolute), new DropletBullet());
                }
                yield return Wait(30);
            }
        }
    }

    /// <summary>Vaccination Spiral (phase 2+): four arms of syringes rotating for two seconds. Walk around it.</summary>
    public class VaccinationSpiralScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            float start = RandomAngle();
            int dir = UnityEngine.Random.value < 0.5f ? 1 : -1;
            for (int t = 0; t < 24; t++)
            {
                for (int arm = 0; arm < 4; arm++)
                    Fire(new Direction(start + dir * t * 11f + arm * 90f, DirectionType.Absolute), new Speed(5f, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(4);
            }
        }
    }

    /// <summary>Snip Time (last fifth of his health): five fast leading syringes, then a ring of droplets.</summary>
    public class SnipTimeScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int i = 0; i < 5; i++)
            {
                float aim = GetAimDirection(0.8f, 13f) + UnityEngine.Random.Range(-4f, 4f);
                Fire(new Direction(aim, DirectionType.Absolute), new Speed(13f, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(4);
            }
            yield return Wait(10);
            float ring = RandomAngle();
            for (int i = 0; i < 12; i++)
                Fire(new Direction(SubdivideCircle(ring, 12, i), DirectionType.Absolute), new Speed(6f, SpeedType.Absolute), new DropletBullet());
        }
    }
}
