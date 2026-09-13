using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Alexandria.EnemyAPI;
using Alexandria.ItemAPI;
using DirType = DirectionalAnimation.DirectionType;
using FlipType = DirectionalAnimation.FlipType;

namespace PlutoVetVisit
{
    /// <summary>
    /// The Vet, built with Alexandria's BossBuilder plus the three fixes its 0.5.10 template needs:
    /// real health (it starts at 15000), a hurtbox on EnemyHitBox (the builder only makes a body collider),
    /// and a fresh attack list (the Fungun template's attacks survive otherwise).
    /// </summary>
    public static class VetBoss
    {
        public const string GUID = "bogdan.pluto.thevet";
        public const string CONSOLE_ID = "pluto:the_vet";
        public const string ROOT = "PlutoVetVisit/Resources/Boss/vet";
        public const string CARD = "PlutoVetVisit/Resources/Boss/vet_bosscard.png";
        private const string BULLET_KIN = "01972dee89fc4404a5c408d50007dad5";

        public static GameObject Prefab;

        public static void Init()
        {
            if (Prefab != null) return;
            if (BossBuilder.Dictionary.ContainsKey(GUID)) { Prefab = BossBuilder.Dictionary[GUID]; return; }
            Assembly asm = typeof(PastPlugin).Assembly;

            // Hitbox arguments are pixels from the sprite's lower-left (48x40 canvas, body at columns 16-30).
            Prefab = BossBuilder.BuildPrefab("The Vet", GUID, ROOT + "/idle/vet_idle_001", new IntVector2(16, 0), new IntVector2(14, 36), false);
            if (Prefab == null) throw new Exception("BossBuilder.BuildPrefab returned null");
            AIActor actor = Prefab.GetComponent<AIActor>();
            HealthHaver hh = actor.healthHaver;
            AIAnimator anim = actor.aiAnimator;
            BehaviorSpeculator bs = Prefab.GetComponent<BehaviorSpeculator>();

            hh.ForceSetCurrentHealth(PastConfig.BossHealth);
            hh.SetHealthMaximum(PastConfig.BossHealth);
            hh.overrideBossName = "The Vet";
            hh.bossHealthBar = HealthHaver.BossBarType.MainBar; // boss bar, kill cam, boss damage rules
            hh.overrideDeathAnimation = "die";
            actor.MovementSpeed = 3f;
            actor.CollisionDamage = 1f;
            actor.CollisionKnockbackStrength = 5f;
            actor.knockbackDoer.weight = 200f;
            actor.IgnoreForRoomClear = false;
            actor.PreventFallingInPitsEver = true;
            actor.CanDropCurrency = false;
            actor.procedurallyOutlined = true;
            actor.specRigidbody.CollideWithOthers = true;
            actor.specRigidbody.CollideWithTileMap = true;
            actor.specRigidbody.PixelColliders.Add(new PixelCollider
            {
                ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
                CollisionLayer = CollisionLayer.EnemyHitBox,
                IsTrigger = false,
                ManualOffsetX = 16, ManualOffsetY = 0, ManualWidth = 14, ManualHeight = 36,
            });

            Clip(anim, "idle", 6, asm, tk2dSpriteAnimationClip.WrapMode.Loop);
            Clip(anim, "move", 8, asm, tk2dSpriteAnimationClip.WrapMode.Loop);
            Clip(anim, "tell", 8, asm, tk2dSpriteAnimationClip.WrapMode.Once);
            Clip(anim, "fire", 12, asm, tk2dSpriteAnimationClip.WrapMode.Once);
            Clip(anim, "intro", 8, asm, tk2dSpriteAnimationClip.WrapMode.Once);
            Clip(anim, "die", 8, asm, tk2dSpriteAnimationClip.WrapMode.Once);
            anim.IdleAnimation = TwoWay("vet_idle");
            anim.MoveAnimation = TwoWay("vet_move");
            anim.HitReactChance = 0f;
            Directional(anim, "tell");
            Directional(anim, "fire");
            Directional(anim, "intro");
            Directional(anim, "die");

            AIBulletBank bank = Prefab.GetComponent<AIBulletBank>();
            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).bulletBank.GetBullet("default");
            bank.Bullets.Add(EnemyBuildingTools.CopyBulletBankEntry(kin, "syringe", "DNC"));
            bank.Bullets.Add(EnemyBuildingTools.CopyBulletBankEntry(kin, "droplet", "DNC"));

            GameObject shootPoint = EnemyBuildingTools.GenerateShootPoint(Prefab, actor.sprite.WorldCenter + new Vector2(0.9f, 0.4f), "syringe_tip");
            bs.TargetBehaviors = new List<TargetBehaviorBase>
            {
                new TargetPlayerBehavior { Radius = 35f, LineOfSight = false, ObjectPermanence = true, SearchInterval = 0.25f, PauseOnTargetSwitch = false, PauseTime = 0.25f }
            };
            bs.MovementBehaviors = new List<MovementBehaviorBase>
            {
                new MoveErraticallyBehavior { PathInterval = 0.35f, PointReachedPauseTime = 0.4f, PreventFiringWhileMoving = false, InitialDelay = 0.5f, StayOnScreen = true, AvoidTarget = false, UseTargetsRoom = true }
            };
            bs.AttackBehaviors = new List<AttackBehaviorBase>
            {
                new AttackBehaviorGroup { ShareCooldowns = false, AttackBehaviors = BuildAttacks(shootPoint) }
            };
            bs.InstantFirstTick = false;
            bs.TickInterval = 0.1f;
            bs.PostAwakenDelay = 0.5f;
            bs.RemoveDelayOnReinforce = false;
            bs.OverrideStartingFacingDirection = false;
            bs.StartingFacingDirection = -90f;
            bs.SkipTimingDifferentiator = false;

            GenericIntroDoer intro = Prefab.AddComponent<GenericIntroDoer>();
            intro.triggerType = GenericIntroDoer.TriggerType.BossTriggerZone; // never auto-triggers; the controller calls TriggerSequence
            intro.initialDelay = 0.15f;
            intro.cameraMoveSpeed = 14f;
            intro.specifyIntroAiAnimator = null;
            intro.BossMusicEvent = PastConfig.BossMusic;
            intro.PreventBossMusic = false;
            intro.InvisibleBeforeIntroAnim = false;
            intro.preIntroAnim = string.Empty;
            intro.preIntroDirectionalAnim = string.Empty;
            intro.introAnim = "vet_intro";
            intro.introDirectionalAnim = string.Empty;
            intro.continueAnimDuringOutro = false;
            intro.cameraFocus = null;
            intro.roomPositionCameraFocus = Vector2.zero;
            intro.restrictPlayerMotionToRoom = false;
            intro.fusebombLock = false;
            intro.AdditionalHeightOffset = 0f;
            intro.HideGunAndHand = false;
            intro.SkipBossCard = false;
            intro.portraitSlideSettings = new PortraitSlideSettings
            {
                bossNameString = "The Vet",
                bossSubtitleString = "Doctor's Orders",
                bossQuoteString = string.Empty,
                bossArtSprite = ResourceExtractor.GetTextureFromResource(CARD, asm),
                bossSpritePxOffset = IntVector2.Zero,
                topLeftTextPxOffset = IntVector2.Zero,
                bottomRightTextPxOffset = IntVector2.Zero,
                bgColor = new Color(0.17f, 0.45f, 0.40f),
            };
            intro.SkipFinalizeAnimation = true;

            ExplodeOnDeath boom = Prefab.AddComponent<ExplodeOnDeath>();
            boom.deathType = OnDeathBehavior.DeathType.Death;
            boom.immuneToIBombApp = true;
            boom.explosionData = new ExplosionData
            {
                useDefaultExplosion = true, doDamage = false, damage = 0f, damageToPlayer = 0f, damageRadius = 3f,
                doForce = true, pushRadius = 4f, force = 40f, debrisForce = 20f, preventPlayerForce = false,
                doDestroyProjectiles = true, breakSecretWalls = false, explosionDelay = 0f,
                doScreenShake = true, doStickyFriction = true, doExplosionRing = true, playDefaultSFX = true, isFreezeExplosion = false,
            };
            Gun rpg = PickupObjectDatabase.GetById(19) as Gun; // borrow the RPG's explosion look when available
            ExplosiveModifier rpgBoom = rpg != null && rpg.DefaultModule.projectiles.Count > 0 ? rpg.DefaultModule.projectiles[0].GetComponent<ExplosiveModifier>() : null;
            if (rpgBoom != null && rpgBoom.explosionData != null)
            {
                boom.explosionData.useDefaultExplosion = false;
                boom.explosionData.effect = rpgBoom.explosionData.effect;
                boom.explosionData.ss = rpgBoom.explosionData.ss;
            }
            Prefab.AddComponent<VetDeathHandler>();

            Gungeon.Game.Enemies.Add(CONSOLE_ID, actor); // console: spawn pluto:the_vet
            PastPlugin.Log("The Vet built: " + PastConfig.BossHealth + " HP, console id " + CONSOLE_ID);
        }

        private static void Clip(AIAnimator anim, string clip, int fps, Assembly asm, tk2dSpriteAnimationClip.WrapMode wrap)
        {
            // One folder per clip; every PNG under it, in sorted name order, becomes a frame (hence zero padding).
            tk2dSpriteAnimationClip c = EnemyBuilder.BuildAnimation(anim, "vet_" + clip, ROOT + "/" + clip, fps, asm);
            if (c == null) throw new Exception("no frames found for clip " + clip + " under " + ROOT + "/" + clip);
            c.wrapMode = wrap;
        }

        private static DirectionalAnimation TwoWay(string clip)
        {
            // Right, then left; the left copy is the right clip mirrored.
            return new DirectionalAnimation { Type = DirType.TwoWayHorizontal, Prefix = clip, AnimNames = new[] { clip, clip }, Flipped = new[] { FlipType.None, FlipType.Flip } };
        }

        private static void Directional(AIAnimator anim, string name)
        {
            EnemyBuildingTools.AddNewDirectionAnimation(anim, name, new[] { "vet_" + name, "vet_" + name }, new[] { FlipType.None, FlipType.Flip }, DirType.TwoWayHorizontal);
        }

        private static List<AttackBehaviorGroup.AttackGroupItem> BuildAttacks(GameObject shootPoint)
        {
            return new List<AttackBehaviorGroup.AttackGroupItem>
            {
                Item("booster shot", 1f, Shoot(typeof(BoosterShotScript), shootPoint, 1.6f, 0f, 1f)),
                Item("spray bottle", 1f, Shoot(typeof(SprayBottleScript), shootPoint, 2.2f, 0f, 1f)),
            };
        }

        public static AttackBehaviorGroup.AttackGroupItem Item(string nick, float probability, AttackBehaviorBase behavior)
        {
            return new AttackBehaviorGroup.AttackGroupItem { NickName = nick, Probability = probability, Behavior = behavior };
        }

        /// <summary>An attack usable while health is between minHealth and maxHealth (fractions of max).</summary>
        public static ShootBehavior Shoot(Type script, GameObject shootPoint, float cooldown, float minHealth, float maxHealth)
        {
            return new ShootBehavior
            {
                ShootPoint = shootPoint,
                BulletScript = new CustomBulletScriptSelector(script),
                LeadAmount = 0f,
                StopDuring = ShootBehavior.StopType.Attack,
                ImmobileDuringStop = true,
                LockFacingDirection = false,
                ContinueAimingDuringTell = true,
                ReaimOnFire = false,
                RequiresTarget = true,
                PreventTargetSwitching = true,
                Uninterruptible = false,
                TellAnimation = "tell",
                FireAnimation = "fire",
                HideGun = false,
                UseVfx = false,
                Cooldown = cooldown,
                CooldownVariance = 0.25f,
                AttackCooldown = 0.4f,
                GlobalCooldown = 0f,
                InitialCooldown = 1f,
                InitialCooldownVariance = 0f,
                GroupName = null,
                GroupCooldown = 0f,
                MinRange = 0f,
                Range = 40f,
                MinWallDistance = 0f,
                MaxEnemiesInRoom = 0f,
                MinHealthThreshold = minHealth,
                MaxHealthThreshold = maxHealth,
                HealthThresholds = new float[0],
                AccumulateHealthThresholds = true,
                targetAreaStyle = null,
                IsBlackPhantom = false,
                resetCooldownOnDamage = null,
                RequiresLineOfSight = false,
                MaxUsages = 0,
            };
        }
    }

    /// <summary>Lives on the spawned boss. HealthHaver events are per instance, so subscribe in Start().</summary>
    public class VetDeathHandler : BraveBehaviour
    {
        private void Start()
        {
            if (healthHaver != null) healthHaver.OnPreDeath += OnPreDeath;
        }

        private void OnPreDeath(Vector2 direction)
        {
            healthHaver.OnPreDeath -= OnPreDeath;
            PastPlugin.Log("The Vet is down");
            if (VetVisitController.Instance != null) VetVisitController.Instance.OnBossDied();
        }
    }
}
