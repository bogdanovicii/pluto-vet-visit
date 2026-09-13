using System.Collections;
using Brave.BulletScript;

namespace PlutoVetVisit
{
    // Bullet scripts run at 60 frames per second: Wait(8) is eight frames. Speeds are tiles per second.
    // Bank names must exist on the boss's AIBulletBank (VetBoss adds "syringe" and "droplet").

    public class SyringeBullet : Bullet
    {
        public SyringeBullet() : base("syringe", false, false, false) { }
    }

    public class DropletBullet : Bullet
    {
        public DropletBullet() : base("droplet", false, false, false) { }
    }

    /// <summary>Booster Shot: three syringes straight at Pluto, eight frames apart.</summary>
    public class BoosterShotScript : Script
    {
        public override IEnumerator Top() // Bullet.Top is protected in the game but public in the publicized reference assembly
        {
            for (int i = 0; i < 3; i++)
            {
                Fire(new Direction(0f, DirectionType.Aim), new Speed(10f, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(8);
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
}
