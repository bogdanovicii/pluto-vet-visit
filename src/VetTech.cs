using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Alexandria.EnemyAPI;
using DirType = DirectionalAnimation.DirectionType;
using FlipType = DirectionalAnimation.FlipType;

namespace PlutoVetVisit
{
    /// <summary>
    /// The Vet Tech: the ward's rifle grunt. It closes to mid range with line of sight (Bullet Kin 7, Veteran Kin 11), then
    /// strafes to random cells on its side of Pluto while it fires Hegemony-soldier bursts, side-steps like a Gun Cultist,
    /// takes a long-tell dart shot from range and now and then lunges in. Built with EnemyBuilder plus the fixes its template
    /// needs (real health, an EnemyHitBox, a shadow). The Syringe Tech and the Nurse reuse the same helpers.
    /// </summary>
    public static class VetTech
    {
        public const string GUID = "bogdan.pluto.vettech";
        public const string CONSOLE_ID = "pluto:vet_tech";
        public const string NAME_KEY = "#PLUTO_VET_TECH";
        public const string BULLET_KIN = "01972dee89fc4404a5c408d50007dad5";
        public static GameObject Prefab;

        public static void Init()
        {
            if (Prefab != null) return;
            if (EnemyBuilder.Dictionary.ContainsKey(GUID)) { Prefab = EnemyBuilder.Dictionary[GUID]; return; }
            Assembly asm = typeof(PastPlugin).Assembly;
            Prefab = EnemyBuilder.BuildPrefab("Vet Tech", GUID, CastLayout.TECH_ROOT + "/idle/tech_idle_001",
                new IntVector2(CastLayout.TECH_HIT_X, CastLayout.TECH_HIT_Y), new IntVector2(CastLayout.TECH_HIT_W, CastLayout.TECH_HIT_H), false);
            if (Prefab == null) throw new Exception("EnemyBuilder.BuildPrefab returned null for the Vet Tech");
            AIActor actor = Prefab.GetComponent<AIActor>();
            ETGMod.Databases.Strings.Enemies.Set(NAME_KEY, "Vet Tech");
            Body(actor, PastConfig.TechHealth, PastConfig.TechSpeed, 60f, NAME_KEY, CastLayout.TECH_HIT_X, CastLayout.TECH_HIT_Y, CastLayout.TECH_HIT_W, CastLayout.TECH_HIT_H);
            Clips(actor.aiAnimator, "tech", CastLayout.TECH_ROOT, CastLayout.TECH_CLIPS, asm);

            AIBulletBank bank = Prefab.GetComponent<AIBulletBank>();
            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).bulletBank.GetBullet("default");
            bank.Bullets.Add(VetBoss.Entry(kin, "syringe", "vet_syringe_001", 14, 6, 10, 4, true));
            bank.Bullets.Add(VetBoss.Entry(kin, "dart", "vet_dart_001", 13, 5, 9, 3, true));

            GameObject shootPoint = ShootPoint(Prefab, actor, CastLayout.TECH_SHOOT_X, CastLayout.TECH_SHOOT_Y, CastLayout.TECH_W, CastLayout.TECH_H, "syringe_tip");
            BehaviorSpeculator bs = Prefab.GetComponent<BehaviorSpeculator>();
            Brain(bs, PastConfig.TechRange, true, 0.35f);

            // Plants for the tell, keeps strafing while the three rounds go out; the variance desyncs a wave.
            ShootBehavior burst = VetBoss.Shoot(typeof(TechShotScript), shootPoint, PastConfig.TechCooldown, 0f, 1f, 0f, 14f, 0.3f, 0.8f);
            burst.StopDuring = ShootBehavior.StopType.TellOnly;
            burst.RequiresLineOfSight = true;
            burst.InitialCooldownVariance = 0.8f;
            ShootBehavior dart = VetBoss.Shoot(typeof(DartRifleScript), shootPoint, PastConfig.TechDartCooldown, 0f, 1f, 6f, 16f, 0.6f, 3f);
            dart.RequiresLineOfSight = true;
            bs.AttackBehaviors = new List<AttackBehaviorBase>
            {
                new AttackBehaviorGroup
                {
                    ShareCooldowns = false,
                    AttackBehaviors = new List<AttackBehaviorGroup.AttackGroupItem>
                    {
                        VetBoss.Item("burst", 1.0f, burst),
                        VetBoss.Item("dart rifle", 0.6f, dart),
                        VetBoss.Item("sidestep", 0.5f, Hop(DashBehavior.DashDirection.PerpendicularToTarget, 3f, 0.3f, 4f, 1.5f, 2f, 0f, true)),
                        VetBoss.Item("lunge", 0.3f, Hop(DashBehavior.DashDirection.KindaTowardTarget, 3.5f, 0.35f, 7f, 2f, 5f, 8f, false, "tell")),   // crouches (tell) before it lunges; the sidestep stays an instant dodge
                    }
                }
            };
            Prefab.AddComponent<SelfEngage>();
            Gungeon.Game.Enemies.Add(CONSOLE_ID, actor);
            VetBoss.CheckBank(actor, "Vet Tech prefab");
            PastPlugin.Log("Vet Tech built: " + PastConfig.TechHealth + " HP, console id " + CONSOLE_ID);
        }

        /// <summary>Health, hitbox, movement, shadow: what EnemyBuilder's Rubber Kin template leaves unset.</summary>
        public static void Body(AIActor actor, float health, float speed, float weight, string nameKey, int hx, int hy, int hw, int hh)
        {
            HealthHaver haver = actor.healthHaver;
            haver.SetHealthMaximum(health);
            haver.ForceSetCurrentHealth(health);
            haver.overrideDeathAnimation = "die";
            actor.OverrideDisplayName = nameKey;
            actor.ActorName = nameKey;
            actor.MovementSpeed = speed;
            actor.CollisionDamage = 0.5f;   // vanilla grunts bump for half a heart
            actor.CollisionKnockbackStrength = 5f;
            actor.knockbackDoer.weight = weight;
            actor.PreventFallingInPitsEver = true;
            actor.CanDropCurrency = false;
            actor.procedurallyOutlined = true;
            actor.EnemySwitchState = "Metal_Bullet_Man";
            actor.specRigidbody.CollideWithOthers = true;
            actor.specRigidbody.CollideWithTileMap = true;
            actor.specRigidbody.PixelColliders.Add(new PixelCollider
            {
                ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
                CollisionLayer = CollisionLayer.EnemyHitBox,
                IsTrigger = false,
                ManualOffsetX = hx, ManualOffsetY = hy, ManualWidth = hw, ManualHeight = hh,
            });
            // DashBehavior reads ShadowObject on every tick; AIActor.Start generates the blob shadow whenever HasShadow
            // is on, so keep it on even if the Bullet Kin's shadow prefab cannot be borrowed.
            actor.HasShadow = true;
            try
            {
                AIActor kin = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN);
                GameObject shadow = kin != null ? (kin.ShadowPrefab != null ? kin.ShadowPrefab : kin.ShadowObject) : null;
                if (shadow != null) EnemyBuildingTools.AddShadowToAIActor(actor, shadow, new Vector2(hw / 32f, 0f), "shadow");
                if (kin != null) actor.CorpseObject = kin.CorpseObject;
            }
            catch (Exception e) { PastPlugin.Log("no borrowed shadow for " + nameKey + " (the default blob is used): " + e.Message); }
        }

        /// <summary>One folder per clip under root; idle and move are the mandatory two-way animations, the rest directional.</summary>
        public static void Clips(AIAnimator anim, string prefix, string root, string[] clips, Assembly asm)
        {
            foreach (string clip in clips)
            {
                int fps = clip == "idle" ? 6 : clip == "move" ? 10 : clip == "fire" ? 12 : 8;
                tk2dSpriteAnimationClip c = EnemyBuilder.BuildAnimation(anim, prefix + "_" + clip, root + "/" + clip, fps, asm);
                if (c == null) throw new Exception("no frames for clip " + clip + " under " + root);
                c.wrapMode = clip == "idle" || clip == "move" ? tk2dSpriteAnimationClip.WrapMode.Loop : tk2dSpriteAnimationClip.WrapMode.Once;
                if (clip == "idle") anim.IdleAnimation = TwoWay(prefix + "_idle");
                else if (clip == "move") anim.MoveAnimation = TwoWay(prefix + "_move");
                else EnemyBuildingTools.AddNewDirectionAnimation(anim, clip, new[] { prefix + "_" + clip, prefix + "_" + clip }, new[] { FlipType.None, FlipType.Flip }, DirType.TwoWayHorizontal);
            }
            anim.HitReactChance = 0f;
        }

        private static DirectionalAnimation TwoWay(string clip)
        {
            return new DirectionalAnimation { Type = DirType.TwoWayHorizontal, Prefix = clip, AnimNames = new[] { clip, clip }, Flipped = new[] { FlipType.None, FlipType.Flip } };
        }

        /// <summary>A shoot point at a canvas pixel (from the sprite's lower-left), placed relative to the sprite centre.</summary>
        public static GameObject ShootPoint(GameObject prefab, AIActor actor, int px, int py, int w, int h, string name)
        {
            Vector2 offset = new Vector2((px - w / 2f) / 16f, (py - h / 2f) / 16f);
            return EnemyBuildingTools.GenerateShootPoint(prefab, actor.sprite.WorldCenter + offset, name);
        }

        /// <summary>The ward brain: find Pluto; close in until within range (with line of sight when asked); inside the
        /// range walk to random cells on this side of him instead of standing still, firing on the move.</summary>
        public static void Brain(BehaviorSpeculator bs, float range, bool lineOfSight, float pause)
        {
            bs.TargetBehaviors = new List<TargetBehaviorBase>
            {
                new TargetPlayerBehavior { Radius = 35f, LineOfSight = false, ObjectPermanence = true, SearchInterval = 0.25f, PauseOnTargetSwitch = false, PauseTime = 0.25f }
            };
            bs.MovementBehaviors = new List<MovementBehaviorBase>
            {
                new SeekTargetBehavior { StopWhenInRange = true, CustomRange = range, LineOfSight = lineOfSight, ReturnToSpawn = false, PathInterval = 0.25f },
                new MoveErraticallyBehavior { PathInterval = 0.45f, PointReachedPauseTime = pause, PreventFiringWhileMoving = false, InitialDelay = 0f, StayOnScreen = true, AvoidTarget = true, UseTargetsRoom = true },
            };
            bs.InstantFirstTick = false;
            bs.TickInterval = 0.1f;
            bs.PostAwakenDelay = 0.5f;
            bs.RemoveDelayOnReinforce = false;
            bs.OverrideStartingFacingDirection = false;
            bs.StartingFacingDirection = -90f;
            // Several same-GUID actors get a random 0-4 s first-attack hold-off (the TimingDifferentiator); a
            // three-Tech wave reads as idle with it, so skip it, like bosses do.
            bs.SkipTimingDifferentiator = true;
        }

        /// <summary>A quick hop (DashBehavior, the Gun Cultist's dodge roll without its clip). range 0 = any distance;
        /// avoidTarget keeps the hop from heading at Pluto. Needs the actor's shadow (Body turns HasShadow on).
        /// chargeAnim: an existing clip (tell / mask_tell) DashBehavior plays to the end before it moves, the crouch that
        /// announces a lunge; null keeps an instant dodge. into: a DashBehavior subclass to fill (CoordinatedHop).</summary>
        public static DashBehavior Hop(DashBehavior.DashDirection direction, float distance, float time, float cooldown, float variance, float initial, float range, bool avoidTarget, string chargeAnim = null, DashBehavior into = null)
        {
            DashBehavior d = into ?? new DashBehavior();
            d.dashDirection = direction;
            d.quantizeDirection = avoidTarget ? 0f : 25f;
            d.dashDistance = distance;
            d.dashTime = time;
            d.postDashSpeed = 0f;
            d.doubleDashChance = 0f;
            d.avoidTarget = avoidTarget;
            d.stopOnCollision = true;
            d.chargeAnim = chargeAnim;
            d.dashAnim = null;
            d.warpDashAnimLength = true;
            d.doDodgeDustUp = true;
            d.hideShadow = false;
            d.hideGun = false;
            d.toggleTrailRenderer = false;
            d.enableShadowTrail = false;
            d.Cooldown = cooldown;
            d.CooldownVariance = variance;
            d.InitialCooldown = initial;
            d.AttackCooldown = 0.15f;
            d.Range = range;
            d.MinHealthThreshold = 0f;
            d.MaxHealthThreshold = 1f;
            d.RequiresLineOfSight = false;
            return d;
        }
    }

    /// <summary>
    /// The Syringe Tech: a close-range flanker. It closes to shotgun range, circles on its side of Pluto, fires the syringe
    /// shotgun (five syringes in a fan, then four in the gaps), lunges in with a fan at the end of the lunge, and rolls to
    /// his flank. Plum scrubs and a two-needle pump syringe (tools/tech_poses.py STECH_*).
    /// </summary>
    public static class SyringeTech
    {
        public const string GUID = "bogdan.pluto.syringetech";
        public const string CONSOLE_ID = "pluto:syringe_tech";
        public const string NAME_KEY = "#PLUTO_SYRINGE_TECH";
        public static GameObject Prefab;

        public static void Init()
        {
            if (Prefab != null) return;
            if (EnemyBuilder.Dictionary.ContainsKey(GUID)) { Prefab = EnemyBuilder.Dictionary[GUID]; return; }
            Assembly asm = typeof(PastPlugin).Assembly;
            string root = CastLayout.STECH_ROOT;
            Prefab = EnemyBuilder.BuildPrefab("Syringe Tech", GUID, root + "/idle/stech_idle_001",
                new IntVector2(CastLayout.STECH_HIT_X, CastLayout.STECH_HIT_Y), new IntVector2(CastLayout.STECH_HIT_W, CastLayout.STECH_HIT_H), false);
            if (Prefab == null) throw new Exception("EnemyBuilder.BuildPrefab returned null for the Syringe Tech");
            AIActor actor = Prefab.GetComponent<AIActor>();
            ETGMod.Databases.Strings.Enemies.Set(NAME_KEY, "Syringe Tech");
            VetTech.Body(actor, PastConfig.SyringeTechHealth, PastConfig.SyringeTechSpeed, 60f, NAME_KEY, CastLayout.STECH_HIT_X, CastLayout.STECH_HIT_Y, CastLayout.STECH_HIT_W, CastLayout.STECH_HIT_H);
            VetTech.Clips(actor.aiAnimator, "stech", root, CastLayout.STECH_CLIPS, asm);

            AIBulletBank bank = Prefab.GetComponent<AIBulletBank>();
            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(VetTech.BULLET_KIN).bulletBank.GetBullet("default");
            bank.Bullets.Add(VetBoss.Entry(kin, "syringe", "vet_syringe_001", 14, 6, 10, 4, true));

            GameObject shootPoint = VetTech.ShootPoint(Prefab, actor, CastLayout.STECH_SHOOT_X, CastLayout.STECH_SHOOT_Y, CastLayout.STECH_W, CastLayout.STECH_H, "syringe_tip");
            BehaviorSpeculator bs = Prefab.GetComponent<BehaviorSpeculator>();
            VetTech.Brain(bs, PastConfig.SyringeTechRange, true, 0.15f);

            ShootBehavior fan = VetBoss.Shoot(typeof(SyringeShotgunScript), shootPoint, PastConfig.SyringeFanCooldown, 0f, 1f, 0f, 7f, 0.5f, 1.2f);
            fan.StopDuring = ShootBehavior.StopType.Tell;
            fan.RequiresLineOfSight = true;
            // A dash's own bulletScript is started and force-stopped in the same DashBehavior.EndState call, before the script
            // ticks: nothing fires at 60 fps. So the lunge and the fan are two steps of a sequence, like the Vet's leap and ring.
            DashBehavior lunge = VetTech.Hop(DashBehavior.DashDirection.KindaTowardTarget, 4f, 0.35f, 5f, 1.5f, 3f, 10f, false, "tell");
            ShootBehavior landingFan = VetBoss.Shoot(typeof(SyringeShotgunScript), shootPoint, 0f, 0f, 1f, 0f, 10f, 0.8f, 0f);
            bs.AttackBehaviors = new List<AttackBehaviorBase>
            {
                new AttackBehaviorGroup
                {
                    ShareCooldowns = false,
                    AttackBehaviors = new List<AttackBehaviorGroup.AttackGroupItem>
                    {
                        VetBoss.Item("syringe shotgun", 1.0f, fan),
                        VetBoss.Item("lunge and fan", 0.5f, new SequentialAttackBehaviorGroup
                        {
                            RunInClass = false,
                            AttackBehaviors = new List<AttackBehaviorBase> { lunge, landingFan },
                            OverrideCooldowns = new List<float> { 0.05f },
                        }),
                        VetBoss.Item("flank roll", 0.6f, VetTech.Hop(DashBehavior.DashDirection.PerpendicularToTarget, 3.5f, 0.3f, 3f, 1f, 1.5f, 8f, true)),
                    }
                }
            };
            Prefab.AddComponent<SelfEngage>();
            Gungeon.Game.Enemies.Add(CONSOLE_ID, actor);
            VetBoss.CheckBank(actor, "Syringe Tech prefab");
            PastPlugin.Log("Syringe Tech built: " + PastConfig.SyringeTechHealth + " HP, console id " + CONSOLE_ID);
        }
    }

    /// <summary>
    /// EnemyBuilder strips the ObjectVisibilityManager that wakes a vanilla enemy when its room becomes visible,
    /// so a clone of ours is born AIActor.State Inactive and its BehaviorSpeculator never ticks (0.8.0's
    /// "staff do nothing"). This wakes the actor itself a moment after it appears unless the controller asked
    /// it to hold (the greeter talks before it fights). Makes `spawn pluto:vet_tech` in a normal room fight too.
    /// The same idea as Once More Into The Breach's EngageLate.
    /// </summary>
    public class SelfEngage : BraveBehaviour
    {
        public bool hold;

        private IEnumerator Start()
        {
            yield return null;
            if (aiActor != null) VetBoss.CheckBank(aiActor, aiActor.GetActorName() + " spawned,");
            if (aiActor != null) VetBoss.WatchFirstShot(aiActor);
            yield return new WaitForSeconds(0.15f);
            if (hold || aiActor == null) yield break;
            if (!aiActor.HasBeenAwoken)
            {
                VetVisitController.Engage(aiActor);
                PastPlugin.Log(aiActor.GetActorName() + " engaged itself (state was Inactive)");
            }
        }
    }

    /// <summary>
    /// The Nurse, mini-boss: closes in and sprays the shotgun syringe, hops back and throws the net when Pluto gets close,
    /// sweeps a tranquilizer spray from mid range, and below half health adds the IV line (a braided stream of droplets).
    /// </summary>
    public static class Nurse
    {
        public const string GUID = "bogdan.pluto.nurse";
        public const string CONSOLE_ID = "pluto:nurse";
        public const string NAME_KEY = "#PLUTO_NURSE";
        public static GameObject Prefab;

        public static void Init()
        {
            if (Prefab != null) return;
            if (EnemyBuilder.Dictionary.ContainsKey(GUID)) { Prefab = EnemyBuilder.Dictionary[GUID]; return; }
            Assembly asm = typeof(PastPlugin).Assembly;
            Prefab = EnemyBuilder.BuildPrefab("The Nurse", GUID, CastLayout.NURSE_ROOT + "/idle/nurse_idle_001",
                new IntVector2(CastLayout.NURSE_HIT_X, CastLayout.NURSE_HIT_Y), new IntVector2(CastLayout.NURSE_HIT_W, CastLayout.NURSE_HIT_H), false);
            if (Prefab == null) throw new Exception("EnemyBuilder.BuildPrefab returned null for the Nurse");
            AIActor actor = Prefab.GetComponent<AIActor>();
            ETGMod.Databases.Strings.Enemies.Set(NAME_KEY, "The Nurse");
            VetTech.Body(actor, PastConfig.NurseHealth, PastConfig.NurseSpeed, 150f, NAME_KEY, CastLayout.NURSE_HIT_X, CastLayout.NURSE_HIT_Y, CastLayout.NURSE_HIT_W, CastLayout.NURSE_HIT_H);
            VetTech.Clips(actor.aiAnimator, "nurse", CastLayout.NURSE_ROOT, CastLayout.NURSE_CLIPS, asm);

            AIBulletBank bank = Prefab.GetComponent<AIBulletBank>();
            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(VetTech.BULLET_KIN).bulletBank.GetBullet("default");
            bank.Bullets.Add(VetBoss.Entry(kin, "droplet", "vet_droplet_001", 9, 7, 7, 5, true));
            bank.Bullets.Add(VetBoss.Entry(kin, "tranq", "vet_tranq_001", 7, 7, 5, 5, false));
            bank.Bullets.Add(VetBoss.Entry(kin, "net", "vet_net_001", 14, 14, 10, 10, false));

            GameObject shootPoint = VetTech.ShootPoint(Prefab, actor, CastLayout.NURSE_SHOOT_X, CastLayout.NURSE_SHOOT_Y, CastLayout.NURSE_W, CastLayout.NURSE_H, "syringe_tip");
            BehaviorSpeculator bs = Prefab.GetComponent<BehaviorSpeculator>();
            VetTech.Brain(bs, 6f, false, 0.3f);

            ShootBehavior spray = VetBoss.Shoot(typeof(NurseFanScript), shootPoint, PastConfig.NurseFanCooldown, 0f, 1f, 0f, 7f, 0.5f, 1f);
            // Hop back (never toward Pluto, only when he is within 5 tiles), then the net.
            DashBehavior backOff = VetTech.Hop(DashBehavior.DashDirection.Random, 4.5f, 0.4f, PastConfig.NurseNetCooldown, 0.5f, 2f, 5f, true);
            ShootBehavior closeNet = VetBoss.Shoot(typeof(NetThrowScript), shootPoint, 0f, 0f, 1f, 0f, 14f, 0.8f, 0f);
            closeNet.TellAnimation = string.Empty;
            closeNet.FireAnimation = "net";
            ShootBehavior farNet = VetBoss.Shoot(typeof(NetThrowScript), shootPoint, PastConfig.NurseNetCooldown, 0f, 1f, 5f, 14f, 0.8f, 2f);
            farNet.TellAnimation = string.Empty;
            farNet.FireAnimation = "net";
            // Area pressure shares the encounter's threat budget with the Vet (AttackBrain): the hose and the IV line wait while
            // his full course is live, and the Vet's next heavy wall waits for them. Same family, so they alternate.
            ShootBehavior tranquilizer = VetBoss.Shoot(typeof(TranquilizerSprayScript), shootPoint, PastConfig.NurseSprayCooldown, 0f, 1f, 3f, 11f, 0.6f, 3f,
                into: VetBoss.Plan(AttackFamily.Spray, 1f, 0.8f, 0f, 1.4f, RangeBand.Any));
            ShootBehavior ivLine = VetBoss.Shoot(typeof(IVLineScript), shootPoint, PastConfig.NurseIVCooldown, 0f, 0.5f, 4f, 40f, 0.8f, 1f,
                into: VetBoss.Plan(AttackFamily.Spray, 1f, 1.2f, 0f, 1.5f, RangeBand.Any));
            bs.AttackBehaviors = new List<AttackBehaviorBase>
            {
                new AttackBehaviorGroup
                {
                    ShareCooldowns = false,
                    AttackBehaviors = new List<AttackBehaviorGroup.AttackGroupItem>
                    {
                        VetBoss.Item("shotgun syringe", 1.2f, spray),
                        VetBoss.Item("hop back and net", 0.8f, new SequentialAttackBehaviorGroup
                        {
                            RunInClass = false,
                            AttackBehaviors = new List<AttackBehaviorBase> { backOff, closeNet },
                            OverrideCooldowns = new List<float> { 0.1f },
                        }),
                        VetBoss.Item("net throw", 0.5f, farNet),
                        VetBoss.Item("tranquilizer spray", 0.8f, tranquilizer),
                        VetBoss.Item("IV line", 0.6f, ivLine),
                    }
                }
            };
            Prefab.AddComponent<SelfEngage>();
            Prefab.AddComponent<AttackBrain>();
            Gungeon.Game.Enemies.Add(CONSOLE_ID, actor);
            VetBoss.CheckBank(actor, "The Nurse prefab");
            PastPlugin.Log("The Nurse built: " + PastConfig.NurseHealth + " HP, console id " + CONSOLE_ID);
        }
    }
}
