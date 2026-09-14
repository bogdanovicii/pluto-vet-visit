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
            actor.MovementSpeed = PastConfig.BossSpeed;
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

            GameObject shootPoint = EnemyBuildingTools.GenerateShootPoint(Prefab, actor.sprite.WorldCenter + new Vector2(1.2f, 0.0f), "syringe_tip"); // the needle of the vaccine gun
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
                new InitialAttackDelayBehavior { Time = 2f },   // every vanilla floor boss walks for 2 s before the first tell
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
            Prefab.AddComponent<VetReinforcements>();

            Gungeon.Game.Enemies.Add(CONSOLE_ID, actor); // console: spawn pluto:the_vet
            CheckBank(actor, "The Vet prefab");
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

        /// <summary>The sprite recipe and the live projectile object per bank name, so a broken entry can be rebuilt.</summary>
        private class BulletRecipe { public string Sprite; public int W, H; public GameObject Object; }
        private static readonly Dictionary<string, BulletRecipe> Recipes = new Dictionary<string, BulletRecipe>();

        /// <summary>A copy of a vanilla bullet-bank entry whose projectile prefab wears one of our sprites.
        /// CopyBulletBankEntry already instantiates a private copy of the projectile, marks it a fake prefab and
        /// switches it off. Up to 0.10.0 we cloned that copy again with FakePrefab.Clone, and Alexandria's own
        /// Instantiate hook re-activates any clone of a fake prefab: the second copy was a live projectile in the
        /// world that flew out of range and destroyed itself, leaving BulletObject null. AIBulletBank.
        /// CreateProjectileFromBank then falls back to aiShooter.CurrentGun, and our actors have no AIShooter:
        /// the NullReferenceException on every enemy shot since 0.3.0. So: one copy, kept inactive.</summary>
        public static AIBulletBank.Entry Entry(AIBulletBank.Entry template, string name, string sprite, int w, int h)
        {
            AIBulletBank.Entry e = EnemyBuildingTools.CopyBulletBankEntry(template, name, "DNC");
            // The Bullet Kin's entry ships with PlayAudio off; the King's banks set the magnum shot on theirs.
            e.PlayAudio = true;
            e.AudioEvent = "Play_WPN_Magnum_shot_01";
            e.AudioLimitOncePerFrame = true;
            GameObject bullet = e.BulletObject;
            bullet.SetActive(false);
            FakePrefab.MarkAsFakePrefab(bullet);
            Projectile p = bullet.GetComponent<Projectile>();
            p.SetProjectileSpriteRight(sprite, w, h, false, tk2dBaseSprite.Anchor.MiddleCenter, w, h);
            e.preloadCount = 0;   // AIBulletBank.Awake preloads BulletObject when this is > 0; nothing to preload
            BulletRecipe prior;
            if (Recipes.TryGetValue(name, out prior) && (prior.Sprite != sprite || prior.W != w || prior.H != h))
                PastPlugin.Log("warning: bank name '" + name + "' is built with two different sprites; one name must mean one sprite, or a repair picks the last");
            Recipes[name] = new BulletRecipe { Sprite = sprite, W = w, H = h, Object = bullet };
            return e;
        }

        private static bool Usable(AIBulletBank.Entry e)
        {
            return e != null && e.BulletObject != null && e.BulletObject.GetComponent<Projectile>() != null;
        }

        /// <summary>A repaired entry is also written back to the actor's prefab, matched by bank name.</summary>
        private static void WriteBackToPrefab(AIActor a, string name, GameObject bullet)
        {
            if (a == null) return;
            GameObject prefab = a.EnemyGuid == GUID ? Prefab : a.EnemyGuid == VetTech.GUID ? VetTech.Prefab : a.EnemyGuid == Nurse.GUID ? Nurse.Prefab : null;
            AIBulletBank bank = prefab != null ? prefab.GetComponent<AIBulletBank>() : null;
            if (bank == null || bank.Bullets == null || bank == a.bulletBank) return;
            foreach (AIBulletBank.Entry pe in bank.Bullets)
                if (pe != null && string.Equals(pe.Name, name, StringComparison.OrdinalIgnoreCase)) pe.BulletObject = bullet;
        }

        /// <summary>Short bank state for the per-actor diagnostic line: "ok 1" or "BROKEN syringe".</summary>
        public static string BankState(AIActor a)
        {
            AIBulletBank bank = a != null ? a.bulletBank : null;
            if (bank == null || bank.Bullets == null) return "none";
            List<string> broken = new List<string>();
            foreach (AIBulletBank.Entry e in bank.Bullets) if (!Usable(e)) broken.Add(e != null ? e.Name : "null");
            return broken.Count == 0 ? "ok " + bank.Bullets.Count : "BROKEN " + string.Join("/", broken.ToArray());
        }

        /// <summary>Logs every bank entry of an actor (name, usable, active) and rebuilds any entry whose projectile
        /// object is gone, so one lost prefab can never again cost every shot of the past.</summary>
        public static void CheckBank(AIActor a, string label)
        {
            try
            {
                AIBulletBank bank = a != null ? a.bulletBank : null;
                if (bank == null || bank.Bullets == null) { PastPlugin.Log(label + " bank: no AIBulletBank"); return; }
                List<string> parts = new List<string>();
                foreach (AIBulletBank.Entry e in bank.Bullets)
                {
                    if (e == null) { parts.Add("null entry"); continue; }
                    string note = "ok";
                    BulletRecipe r;
                    if (!Usable(e) && Recipes.TryGetValue(e.Name, out r))
                    {
                        if (r.Object == null || r.Object.GetComponent<Projectile>() == null)
                        {
                            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).bulletBank.GetBullet("default");
                            Entry(kin, e.Name, r.Sprite, r.W, r.H);
                            r = Recipes[e.Name];
                        }
                        e.BulletObject = r.Object;
                        WriteBackToPrefab(a, e.Name, r.Object);   // so the next spawn starts with a usable entry
                        note = Usable(e) ? "REPAIRED" : "BROKEN (repair failed)";
                    }
                    else if (!Usable(e)) note = "BROKEN (no recipe)";
                    parts.Add(e.Name + " " + note + (e.BulletObject != null ? (e.BulletObject.activeSelf ? " active!" : " inactive") : " null"));
                }
                PastPlugin.Log(label + " bank: " + string.Join(", ", parts.ToArray()));
            }
            catch (Exception ex) { PastPlugin.Log(label + " bank check threw: " + ex); }
        }

        /// <summary>Three phases by health, shaped like the vanilla floor bosses the research measured (Bullet King,
        /// Gorgun, Beholster, Gatling Gull): bread-and-butter attacks every 1.5-2.5 s, signature patterns on 3.5-5 s
        /// cooldowns with a longer breather (AttackCooldown) after them, a 2 s walk before the first tell, and the
        /// heavy patterns held back for the first seconds (InitialCooldown). Attacks are range-gated so the Vet uses
        /// the right tool for the distance: syringes lead the target at range, the spray bottle punishes hugging him.</summary>
        private static List<AttackBehaviorGroup.AttackGroupItem> BuildAttacks(GameObject shootPoint)
        {
            float c = PastConfig.BossCooldownScale;
            return new List<AttackBehaviorGroup.AttackGroupItem>
            {
                // Phase 1, 100-60 %: "Consultation". Aimed bursts, fans, slow pills. About one attack every 2.5 s.
                Item("booster shot", 1.2f, Shoot(typeof(BoosterShotScript), shootPoint, 1.6f * c, 0.6f, 1f, minRange: 4f, attackCooldown: 0.5f)),
                Item("spray bottle", 1.2f, Shoot(typeof(SprayBottleScript), shootPoint, 2.4f * c, 0.6f, 1f, range: 8f, attackCooldown: 0.6f)),
                Item("pill time", 0.8f, Shoot(typeof(PillTimeScript), shootPoint, 3.5f * c, 0.6f, 1f, attackCooldown: 0.8f, initialCooldown: 4f)),
                // Phase 2, 60-25 %: "Treatment". Quicker bursts, the droplet wall (find the gap, follow it), the spiral, the cone.
                Item("booster shot 2", 1.2f, Shoot(typeof(BoosterShotScript), shootPoint, 1.1f * c, 0.25f, 0.6f, minRange: 4f, attackCooldown: 0.5f)),
                Item("spray bottle 2", 1.0f, Shoot(typeof(SprayBottleScript), shootPoint, 1.5f * c, 0.25f, 0.6f, range: 8f, attackCooldown: 0.6f)),
                Item("droplet wall", 1.0f, Shoot(typeof(DropletWallScript), shootPoint, 3.0f * c, 0.25f, 0.6f, minRange: 5f, attackCooldown: 0.8f)),
                Item("vaccination spiral", 0.8f, Shoot(typeof(VaccinationSpiralScript), shootPoint, 5.0f * c, 0.25f, 0.6f, attackCooldown: 1.0f, initialCooldown: 3f)),
                Item("cone of shame", 1.0f, Shoot(typeof(ConeOfShameScript), shootPoint, 3.5f * c, 0.25f, 0.6f, attackCooldown: 0.8f)),
                // Phase 3, last quarter: "Just a little snip". Fast leading bursts, the hard wall, and the full course
                // (wall then spiral back to back, the way the Gorgun chains her two uzi hoses).
                Item("snip time", 1.5f, Shoot(typeof(SnipTimeScript), shootPoint, 1.4f * c, 0f, 0.25f, attackCooldown: 0.5f)),
                Item("cone of shame 3", 1.0f, Shoot(typeof(ConeOfShameScript), shootPoint, 3.0f * c, 0f, 0.25f, attackCooldown: 0.8f)),
                Item("droplet wall 3", 1.0f, Shoot(typeof(DropletWallHardScript), shootPoint, 2.6f * c, 0f, 0.25f, minRange: 5f, attackCooldown: 0.8f)),
                new AttackBehaviorGroup.AttackGroupItem
                {
                    NickName = "full course",
                    Probability = 1.0f,
                    Behavior = new SequentialAttackBehaviorGroup
                    {
                        RunInClass = false,
                        AttackBehaviors = new List<AttackBehaviorBase>
                        {
                            Shoot(typeof(DropletWallScript), shootPoint, 4.0f * c, 0f, 0.25f, minRange: 5f, attackCooldown: 1.0f),
                            Shoot(typeof(VaccinationSpiralScript), shootPoint, 4.0f * c, 0f, 0.25f, attackCooldown: 1.0f),
                        },
                        OverrideCooldowns = new List<float> { 0.4f },
                    }
                },
            };
        }

        public static AttackBehaviorGroup.AttackGroupItem Item(string nick, float probability, AttackBehaviorBase behavior)
        {
            return new AttackBehaviorGroup.AttackGroupItem { NickName = nick, Probability = probability, Behavior = behavior };
        }

        /// <summary>An attack usable while health is between minHealth and maxHealth (fractions of max).</summary>
        public static ShootBehavior Shoot(Type script, GameObject shootPoint, float cooldown, float minHealth, float maxHealth, float minRange = 0f, float range = 40f, float attackCooldown = 0.4f, float initialCooldown = 1f)
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
                AttackCooldown = attackCooldown,
                GlobalCooldown = 0f,
                InitialCooldown = initialCooldown,
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

    /// <summary>Below half health the Vet calls the Nurse and two Techs, once (v2 design, act 3).</summary>
    public class VetReinforcements : BraveBehaviour
    {
        private bool called, lastFifth;

        private void Start()
        {
            if (healthHaver != null) healthHaver.OnDamaged += OnDamaged;
        }

        private void OnDamaged(float resultValue, float maxValue, CoreDamageTypes damageTypes, DamageCategory damageCategory, Vector2 damageDirection)
        {
            if (maxValue <= 0f || VetVisitController.Instance == null) return;
            if (!called && PastConfig.BossReinforcements && resultValue <= maxValue * 0.5f)
            {
                called = true;
                VetVisitController.Instance.CallReinforcements();
            }
            if (!lastFifth && resultValue <= maxValue * 0.25f)
            {
                lastFifth = true;
                VetVisitController.Instance.LastFifth();
                healthHaver.OnDamaged -= OnDamaged;
            }
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
