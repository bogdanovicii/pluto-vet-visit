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
        public const string NAME_KEY = "#PLUTO_THE_VET";
        public const string SUBTITLE_KEY = "#PLUTO_THE_VET_SUBTITLE";
        public const string QUOTE_KEY = "#PLUTO_THE_VET_QUOTE";

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
            // Boss card, boss bar and actor name all go through StringTableManager.GetEnemiesString, so the
            // names must be string-table KEYS (a raw name shows as an error). MtG API lets us add keys.
            ETGMod.Databases.Strings.Enemies.Set(NAME_KEY, "The Vet");
            ETGMod.Databases.Strings.Enemies.Set(SUBTITLE_KEY, "Doctor's Orders");
            ETGMod.Databases.Strings.Enemies.Set(QUOTE_KEY, "Just a little snip.");
            hh.overrideBossName = NAME_KEY;
            actor.OverrideDisplayName = NAME_KEY;
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
            bank.Bullets.Add(Entry(kin, "syringe", "vet_syringe_001", 12, 4));
            bank.Bullets.Add(Entry(kin, "droplet", "vet_droplet_001", 5, 5));
            bank.Bullets.Add(Entry(kin, "pill", "vet_pill_001", 8, 4));

            GameObject shootPoint = EnemyBuildingTools.GenerateShootPoint(Prefab, actor.sprite.WorldCenter + new Vector2(0.9f, 0.4f), "syringe_tip");
            bs.TargetBehaviors = new List<TargetBehaviorBase>
            {
                new TargetPlayerBehavior { Radius = 35f, LineOfSight = false, ObjectPermanence = true, SearchInterval = 0.25f, PauseOnTargetSwitch = false, PauseTime = 0.25f }
            };
            // Movement stack, first match wins each tick: back off when Pluto gets close, close in when he is
            // far, otherwise strafe around him unpredictably. Keeps the fight at syringe range.
            bs.MovementBehaviors = new List<MovementBehaviorBase>
            {
                new FleeTargetBehavior { TooCloseDistance = 3.5f, TooCloseLOS = false, CloseDistance = 5f, CloseTime = 2f, DesiredDistance = 7f, CanAttackWhileMoving = true, PathInterval = 0.25f },
                new SeekTargetBehavior { StopWhenInRange = true, CustomRange = 8.5f, LineOfSight = false, ReturnToSpawn = false, PathInterval = 0.3f },
                new MoveErraticallyBehavior { PathInterval = 0.35f, PointReachedPauseTime = 0.3f, PreventFiringWhileMoving = false, InitialDelay = 0.5f, StayOnScreen = true, AvoidTarget = true, UseTargetsRoom = true }
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
            intro.introAnim = string.Empty;
            intro.introDirectionalAnim = "intro";      // directional: mirrors to face Pluto
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
                bossNameString = NAME_KEY,
                bossSubtitleString = SUBTITLE_KEY,
                bossQuoteString = QUOTE_KEY,
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
            ExplosiveModifier rpgBoom = rpg != null && rpg.DefaultModule != null && rpg.DefaultModule.projectiles != null && rpg.DefaultModule.projectiles.Count > 0 ? rpg.DefaultModule.projectiles[0].GetComponent<ExplosiveModifier>() : null;
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

        /// <summary>A copy of a vanilla bullet-bank entry whose projectile prefab wears one of our sprites.</summary>
        public static AIBulletBank.Entry Entry(AIBulletBank.Entry template, string name, string sprite, int w, int h)
        {
            AIBulletBank.Entry e = EnemyBuildingTools.CopyBulletBankEntry(template, name, "DNC");
            GameObject clone = FakePrefab.Clone(e.BulletObject);
            Projectile p = clone.GetComponent<Projectile>();
            p.SetProjectileSpriteRight(sprite, w, h, false, tk2dBaseSprite.Anchor.MiddleCenter, w, h);
            e.BulletObject = clone;
            return e;
        }

        private static List<AttackBehaviorGroup.AttackGroupItem> BuildAttacks(GameObject shootPoint)
        {
            // Three phases by health. Attacks are range-gated so the Vet uses the right tool for the
            // distance: syringes lead the target at range, the spray bottle punishes hugging him.
            return new List<AttackBehaviorGroup.AttackGroupItem>
            {
                // Phase 1 (above half health)
                Item("booster shot", 1.2f, Shoot(typeof(BoosterShotScript), shootPoint, 1.6f, 0.5f, 1f, minRange: 4f)),
                Item("spray bottle", 1.2f, Shoot(typeof(SprayBottleScript), shootPoint, 2.0f, 0.5f, 1f, range: 8f)),
                Item("pill time", 0.8f, Shoot(typeof(PillTimeScript), shootPoint, 3.0f, 0.5f, 1f)),
                // Phase 2 (half to a fifth): quicker, plus the droplet wall, the vaccination spiral and the Cone of Shame
                Item("booster shot 2", 1.2f, Shoot(typeof(BoosterShotScript), shootPoint, 1.1f, 0.2f, 0.5f, minRange: 4f)),
                Item("spray bottle 2", 1.2f, Shoot(typeof(SprayBottleScript), shootPoint, 1.5f, 0.2f, 0.5f, range: 8f)),
                Item("pill time 2", 0.7f, Shoot(typeof(PillTimeScript), shootPoint, 2.4f, 0.2f, 0.5f)),
                Item("droplet wall", 1.0f, Shoot(typeof(DropletWallScript), shootPoint, 3.0f, 0.2f, 0.5f, minRange: 5f)),
                Item("vaccination spiral", 0.8f, Shoot(typeof(VaccinationSpiralScript), shootPoint, 4.0f, 0.2f, 0.5f)),
                Item("cone of shame", 1.0f, Shoot(typeof(ConeOfShameScript), shootPoint, 3.5f, 0.2f, 0.5f)),
                // Phase 3 (last fifth): "just a little snip"
                Item("snip time", 1.5f, Shoot(typeof(SnipTimeScript), shootPoint, 1.4f, 0f, 0.2f)),
                Item("vaccination spiral 3", 1.0f, Shoot(typeof(VaccinationSpiralScript), shootPoint, 3.5f, 0f, 0.2f)),
                Item("cone of shame 3", 1.0f, Shoot(typeof(ConeOfShameScript), shootPoint, 3.0f, 0f, 0.2f)),
                Item("droplet wall 3", 1.0f, Shoot(typeof(DropletWallScript), shootPoint, 2.6f, 0f, 0.2f, minRange: 5f)),
            };
        }

        public static AttackBehaviorGroup.AttackGroupItem Item(string nick, float probability, AttackBehaviorBase behavior)
        {
            return new AttackBehaviorGroup.AttackGroupItem { NickName = nick, Probability = probability, Behavior = behavior };
        }

        /// <summary>An attack usable while health is between minHealth and maxHealth (fractions of max).</summary>
        public static ShootBehavior Shoot(Type script, GameObject shootPoint, float cooldown, float minHealth, float maxHealth, float minRange = 0f, float range = 40f)
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
                MinRange = minRange,
                Range = range,
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
