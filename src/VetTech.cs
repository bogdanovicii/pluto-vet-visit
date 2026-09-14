using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Alexandria.EnemyAPI;
using DirType = DirectionalAnimation.DirectionType;
using FlipType = DirectionalAnimation.FlipType;

namespace PlutoVetVisit
{
    /// <summary>
    /// The Vet Tech: a regular enemy on the Bullet Kin plan (seek, then an aimed syringe from a pistol).
    /// Built with EnemyBuilder plus the fixes its template needs (real health, an EnemyHitBox, a shadow).
    /// The Nurse reuses the same helpers at twice the size.
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
            Body(actor, PastConfig.TechHealth, 4.5f, 60f, NAME_KEY, CastLayout.TECH_HIT_X, CastLayout.TECH_HIT_Y, CastLayout.TECH_HIT_W, CastLayout.TECH_HIT_H);
            Clips(actor.aiAnimator, "tech", CastLayout.TECH_ROOT, CastLayout.TECH_CLIPS, asm);

            AIBulletBank bank = Prefab.GetComponent<AIBulletBank>();
            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).bulletBank.GetBullet("default");
            bank.Bullets.Add(VetBoss.Entry(kin, "syringe", "vet_syringe_001", 12, 4));

            GameObject shootPoint = ShootPoint(Prefab, actor, CastLayout.TECH_SHOOT_X, CastLayout.TECH_SHOOT_Y, CastLayout.TECH_W, CastLayout.TECH_H, "syringe_tip");
            BehaviorSpeculator bs = Prefab.GetComponent<BehaviorSpeculator>();
            Brain(bs, 7f);
            bs.AttackBehaviors = new List<AttackBehaviorBase>
            {
                VetBoss.Shoot(typeof(TechShotScript), shootPoint, 2.2f, 0f, 1f, 0f, 14f)
            };
            Gungeon.Game.Enemies.Add(CONSOLE_ID, actor);
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
            actor.CollisionDamage = 1f;
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
            try
            {
                AIActor kin = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN);
                if (kin != null && kin.ShadowObject != null)
                    EnemyBuildingTools.AddShadowToAIActor(actor, kin.ShadowObject, new Vector2(hw / 32f, 0f), "shadow");
                if (kin != null) actor.CorpseObject = kin.CorpseObject;
            }
            catch (Exception e) { PastPlugin.Log("no shadow for " + nameKey + ": " + e.Message); }
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

        /// <summary>Bullet-Kin brain: find Pluto, close to range, keep no line-of-sight requirement (the ward has cover).</summary>
        public static void Brain(BehaviorSpeculator bs, float range)
        {
            bs.TargetBehaviors = new List<TargetBehaviorBase>
            {
                new TargetPlayerBehavior { Radius = 35f, LineOfSight = false, ObjectPermanence = true, SearchInterval = 0.25f, PauseOnTargetSwitch = false, PauseTime = 0.25f }
            };
            bs.MovementBehaviors = new List<MovementBehaviorBase>
            {
                new SeekTargetBehavior { StopWhenInRange = true, CustomRange = range, LineOfSight = false, ReturnToSpawn = false, PathInterval = 0.5f }
            };
            bs.InstantFirstTick = false;
            bs.TickInterval = 0.1f;
            bs.PostAwakenDelay = 0.5f;
            bs.RemoveDelayOnReinforce = false;
            bs.OverrideStartingFacingDirection = false;
            bs.StartingFacingDirection = -90f;
            bs.SkipTimingDifferentiator = false;
        }
    }

    /// <summary>
    /// The Nurse: the Tech's plan at boss scale. Two attacks: a fan of droplets from the shotgun syringe, and the
    /// net, a slow wide projectile that is easy to see and hard to sidestep at close range.
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
            VetTech.Body(actor, PastConfig.NurseHealth, 3.2f, 150f, NAME_KEY, CastLayout.NURSE_HIT_X, CastLayout.NURSE_HIT_Y, CastLayout.NURSE_HIT_W, CastLayout.NURSE_HIT_H);
            VetTech.Clips(actor.aiAnimator, "nurse", CastLayout.NURSE_ROOT, CastLayout.NURSE_CLIPS, asm);

            AIBulletBank bank = Prefab.GetComponent<AIBulletBank>();
            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(VetTech.BULLET_KIN).bulletBank.GetBullet("default");
            bank.Bullets.Add(VetBoss.Entry(kin, "droplet", "vet_droplet_001", 5, 5));
            bank.Bullets.Add(VetBoss.Entry(kin, "net", "vet_net_001", 12, 12));

            GameObject shootPoint = VetTech.ShootPoint(Prefab, actor, CastLayout.NURSE_SHOOT_X, CastLayout.NURSE_SHOOT_Y, CastLayout.NURSE_W, CastLayout.NURSE_H, "syringe_tip");
            BehaviorSpeculator bs = Prefab.GetComponent<BehaviorSpeculator>();
            VetTech.Brain(bs, 6f);
            ShootBehavior net = VetBoss.Shoot(typeof(NetThrowScript), shootPoint, 4.5f, 0f, 1f, 0f, 7f);
            net.TellAnimation = string.Empty;
            net.FireAnimation = "net";
            bs.AttackBehaviors = new List<AttackBehaviorBase>
            {
                new AttackBehaviorGroup
                {
                    ShareCooldowns = false,
                    AttackBehaviors = new List<AttackBehaviorGroup.AttackGroupItem>
                    {
                        VetBoss.Item("droplet fan", 1.2f, VetBoss.Shoot(typeof(NurseFanScript), shootPoint, 2.2f, 0f, 1f, 0f, 12f)),
                        VetBoss.Item("net throw", 0.8f, net),
                    }
                }
            };
            Gungeon.Game.Enemies.Add(CONSOLE_ID, actor);
            PastPlugin.Log("The Nurse built: " + PastConfig.NurseHealth + " HP, console id " + CONSOLE_ID);
        }
    }
}
