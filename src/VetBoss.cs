using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Brave.BulletScript;
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

            // Hitbox arguments are pixels from the sprite's lower-left; tools/vet_poses.py owns them (HITBOX, SHOOT_POINT).
            Prefab = BossBuilder.BuildPrefab("The Vet", GUID, ROOT + "/idle/vet_idle_001",
                new IntVector2(CastLayout.VET_HIT_X, CastLayout.VET_HIT_Y), new IntVector2(CastLayout.VET_HIT_W, CastLayout.VET_HIT_H), false);
            if (Prefab == null) throw new Exception("BossBuilder.BuildPrefab returned null");
            AIActor actor = Prefab.GetComponent<AIActor>();
            HealthHaver hh = actor.healthHaver;
            AIAnimator anim = actor.aiAnimator;
            BehaviorSpeculator bs = Prefab.GetComponent<BehaviorSpeculator>();

            hh.ForceSetCurrentHealth(PastConfig.BossHealth);
            hh.SetHealthMaximum(PastConfig.BossHealth);
            // Boss card, boss bar and actor name all go through StringTableManager.GetEnemiesString, so the
            // names must be string-table KEYS (a raw name shows as an error). MtG API lets us add keys.
            ETGMod.Databases.Strings.Enemies.Set(NAME_KEY, "THE VET");   // capitals: the boss card title font has no glyphs for some lowercase letters ("Te Vet" in 0.11.1)
            ETGMod.Databases.Strings.Enemies.Set(SUBTITLE_KEY, "DOCTOR'S ORDERS!");
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
            // BossBuilder turns the shadow off; DashBehavior (his hops) reads ShadowObject every tick, and AIActor.Start
            // only makes one when HasShadow is on.
            actor.HasShadow = true;
            try
            {
                AIActor kinActor = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN);
                GameObject shadow = kinActor != null ? (kinActor.ShadowPrefab != null ? kinActor.ShadowPrefab : kinActor.ShadowObject) : null;
                if (shadow != null) EnemyBuildingTools.AddShadowToAIActor(actor, shadow, new Vector2((CastLayout.VET_HIT_X + CastLayout.VET_HIT_W / 2f) / 16f, 0f), "shadow");
            }
            catch (Exception e) { PastPlugin.Log("no borrowed shadow for the Vet (the default blob is used): " + e.Message); }
            actor.specRigidbody.CollideWithOthers = true;
            actor.specRigidbody.CollideWithTileMap = true;
            actor.specRigidbody.PixelColliders.Add(new PixelCollider
            {
                ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
                CollisionLayer = CollisionLayer.EnemyHitBox,
                IsTrigger = false,
                ManualOffsetX = CastLayout.VET_HIT_X, ManualOffsetY = CastLayout.VET_HIT_Y, ManualWidth = CastLayout.VET_HIT_W, ManualHeight = CastLayout.VET_HIT_H,
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
            VetMask.Available = VetMask.ClipsPresent(asm);
            if (VetMask.Available)
            {
                Clip(anim, "mask_on", 10, asm, tk2dSpriteAnimationClip.WrapMode.Once);
                Clip(anim, "mask_idle", 6, asm, tk2dSpriteAnimationClip.WrapMode.Loop);
                Clip(anim, "mask_move", 8, asm, tk2dSpriteAnimationClip.WrapMode.Loop);
                Clip(anim, "mask_tell", 8, asm, tk2dSpriteAnimationClip.WrapMode.Once);
                Clip(anim, "mask_fire", 12, asm, tk2dSpriteAnimationClip.WrapMode.Once);
                Clip(anim, "mask_die", 8, asm, tk2dSpriteAnimationClip.WrapMode.Once);
                foreach (string clip in CastLayout.VET_MASK_CLIPS) Directional(anim, clip);
            }
            PastPlugin.Log("mask clips " + (VetMask.Available ? "loaded" : "not embedded yet"));

            AIBulletBank bank = Prefab.GetComponent<AIBulletBank>();
            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).bulletBank.GetBullet("default");
            // name, sprite, sprite size, hitbox size, points along travel: tools/projectiles.py BANK owns these (test_projectiles checks)
            bank.Bullets.Add(Entry(kin, "syringe", "vet_syringe_001", 14, 6, 10, 4, true));
            bank.Bullets.Add(Entry(kin, "vaccine", "vet_vaccine_001", 8, 8, 6, 6, false));
            bank.Bullets.Add(Entry(kin, "droplet", "vet_droplet_001", 9, 7, 7, 5, true));
            bank.Bullets.Add(Entry(kin, "pill", "vet_pill_001", 10, 6, 8, 4, true));
            bank.Bullets.Add(Entry(kin, "tablet", "vet_tablet_001", 7, 7, 5, 5, false));
            bank.Bullets.Add(Entry(kin, "scalpel", "vet_scalpel_001", 14, 5, 10, 3, true));
            bank.Bullets.Add(Entry(kin, "stitch", "vet_stitch_001", 9, 9, 5, 5, false));
            bank.Bullets.Add(Entry(kin, "cloud", "vet_cloud_001", 16, 16, 12, 12, false));

            GameObject shootPoint = VetTech.ShootPoint(Prefab, actor, CastLayout.VET_SHOOT_X, CastLayout.VET_SHOOT_Y, CastLayout.VET_W, CastLayout.VET_H, "syringe_tip"); // the needle tip
            bs.TargetBehaviors = new List<TargetBehaviorBase>
            {
                new TargetPlayerBehavior { Radius = 35f, LineOfSight = false, ObjectPermanence = true, SearchInterval = 0.25f, PauseOnTargetSwitch = false, PauseTime = 0.25f }
            };
            // Vanilla floor bosses move with a Seek leash only (Beholster 10 tiles). The 0.10 FleeTargetBehavior fired on every
            // hit and, with interruptible attacks, cancelled his tells: every shot Pluto landed stopped the pattern. Now: close
            // to 10 tiles, then strafe to random cells on his side of Pluto; the hops in the attack table do the repositioning.
            bs.MovementBehaviors = new List<MovementBehaviorBase>
            {
                new SeekTargetBehavior { StopWhenInRange = true, CustomRange = 10f, LineOfSight = false, ReturnToSpawn = false, PathInterval = 0.5f },
                new MoveErraticallyBehavior { PathInterval = 0.5f, PointReachedPauseTime = 0.25f, PreventFiringWhileMoving = false, InitialDelay = 0f, StayOnScreen = true, AvoidTarget = true, UseTargetsRoom = true },
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
        private class BulletRecipe { public string Sprite; public int W, H, HitW, HitH; public bool Rotates; public GameObject Object; }
        private static readonly Dictionary<string, BulletRecipe> Recipes = new Dictionary<string, BulletRecipe>();

        /// <summary>A copy of a vanilla bullet-bank entry whose projectile prefab wears one of our sprites.
        /// CopyBulletBankEntry already instantiates a private copy of the projectile, marks it a fake prefab and
        /// switches it off. Up to 0.10.0 we cloned that copy again with FakePrefab.Clone, and Alexandria's own
        /// Instantiate hook re-activates any clone of a fake prefab: the second copy was a live projectile in the
        /// world that flew out of range and destroyed itself, leaving BulletObject null. AIBulletBank.
        /// CreateProjectileFromBank then falls back to aiShooter.CurrentGun, and our actors have no AIShooter:
        /// the NullReferenceException on every enemy shot since 0.3.0. So: one copy, kept inactive.</summary>
        public static AIBulletBank.Entry Entry(AIBulletBank.Entry template, string name, string sprite, int w, int h, int hitW, int hitH, bool pointsAlongTravel)
        {
            AIBulletBank.Entry e = EnemyBuildingTools.CopyBulletBankEntry(template, name, "DNC");
            // The Bullet Kin's entry ships with PlayAudio off; the King's banks set the magnum shot on theirs.
            e.PlayAudio = true;
            e.AudioEvent = "Play_WPN_Magnum_shot_01";
            e.AudioLimitOncePerFrame = true;
            GameObject bullet = e.BulletObject;
            bullet.SetActive(false);
            FakePrefab.MarkAsFakePrefab(bullet);
            // One name per copy: the pool keys its name dictionary by GameObject name ("Duplicate prefab name" otherwise).
            bullet.name = "PlutoVet_" + name + "_" + (bulletCopyCount++);
            Projectile p = bullet.GetComponent<Projectile>();
            if (ETGMod.Databases.Items.ProjectileCollection.inst.GetSpriteIdByName(sprite, -1) < 0)
                PastPlugin.Log("warning: projectile sprite '" + sprite + "' is not in ProjectileCollection; keeping the vanilla look for " + name);
            else
                p.SetProjectileSpriteRight(sprite, w, h, false, tk2dBaseSprite.Anchor.MiddleCenter, w, h);
            // SetProjectileSpriteRight moves the sprite into ETGMod's ProjectileCollection. The vanilla bullet builds its
            // hitbox as a BagelCollider from the frame "10x10_projectile_dubred_dark_001" of its OWN collection; that
            // lookup now fails and PixelCollider.RegenerateEmptyCollider makes it 0x0: the 0.10.1 bullets flew through
            // Pluto. Give every copy a manual box sized to our sprite, centred on the projectile (sprite anchored middle).
            ManualHitbox(p, hitW, hitH);
            // Long sprites (needle, dart, scalpel, droplet, pill) are drawn facing right: the bank spawns them rotated to their
            // direction (AIBulletBank: Quaternion.Euler(0, 0, direction)), and a Manual collider regenerates with the transform's
            // rotation, so the box turns with the art. Round sprites keep the template's setting.
            if (pointsAlongTravel) p.shouldRotate = true;
            p.collidesWithPlayer = true;
            p.collidesWithEnemies = false;
            p.collidesWithProjectiles = false;
            p.baseData.damage = 0.5f;   // every vanilla enemy bullet takes half a heart
            e.preloadCount = 0;   // AIBulletBank.Awake preloads BulletObject when this is > 0; nothing to preload
            BulletRecipe prior;
            if (Recipes.TryGetValue(name, out prior) && (prior.Sprite != sprite || prior.W != w || prior.H != h || prior.HitW != hitW || prior.HitH != hitH))
                PastPlugin.Log("warning: bank name '" + name + "' is built with two different sprites; one name must mean one sprite, or a repair picks the last");
            Recipes[name] = new BulletRecipe { Sprite = sprite, W = w, H = h, HitW = hitW, HitH = hitH, Rotates = pointsAlongTravel, Object = bullet };
            LogBullet("bank " + name, p);
            return e;
        }

        private static int bulletCopyCount;

        /// <summary>A manual box collider on the Projectile layer of hw x hh pixels, centred on the projectile position. The sizes
        /// come from tools/projectiles.py BANK: a little smaller than the art (vanilla hitboxes sit inside the sprite).</summary>
        public static void ManualHitbox(Projectile p, int hw, int hh)
        {
            SpeculativeRigidbody body = p != null ? p.specRigidbody : null;
            if (body == null || body.PixelColliders == null) { PastPlugin.Log("warning: projectile without a rigidbody, cannot set its hitbox"); return; }
            foreach (PixelCollider pc in body.PixelColliders)
            {
                pc.ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual;
                pc.CollisionLayer = CollisionLayer.Projectile;
                pc.IsTrigger = false;
                pc.Enabled = true;
                pc.BagleUseFirstFrameOnly = false;
                pc.SpecifyBagelFrame = string.Empty;
                pc.ManualWidth = hw;
                pc.ManualHeight = hh;
                pc.ManualOffsetX = -hw / 2;
                pc.ManualOffsetY = -hh / 2;
            }
        }

        /// <summary>One line per projectile: name, sprite, flags, damage and every collider (mode, layer, manual size, and the
        /// built Dimensions, which are only real once a live copy has initialised its rigidbody).</summary>
        public static void LogBullet(string label, Projectile p)
        {
            try
            {
                if (p == null) { PastPlugin.Log(label + ": no projectile"); return; }
                SpeculativeRigidbody b = p.specRigidbody;
                tk2dBaseSprite s = p.sprite;
                tk2dSpriteDefinition def = s != null ? s.GetCurrentSpriteDef() : null;
                string line = label + ": go " + p.gameObject.name + ", active " + p.gameObject.activeSelf
                    + ", sprite " + (def != null ? def.name : "none")
                    + ", hitsPlayer " + p.collidesWithPlayer + ", hitsEnemies " + p.collidesWithEnemies
                    + ", damage " + p.baseData.damage + ", speed " + p.baseData.speed
                    + ", colliders " + (b != null && b.PixelColliders != null ? b.PixelColliders.Count : -1);
                if (b != null && b.PixelColliders != null)
                    foreach (PixelCollider pc in b.PixelColliders)
                        line += " [" + pc.CollisionLayer + " " + pc.ColliderGenerationMode + " manual " + pc.ManualWidth + "x" + pc.ManualHeight
                            + " at " + pc.ManualOffsetX + "," + pc.ManualOffsetY + " built " + pc.Dimensions.x + "x" + pc.Dimensions.y + " trigger " + pc.IsTrigger + "]";
                PastPlugin.Log(line);
            }
            catch (Exception ex) { PastPlugin.Log(label + ": bullet log threw: " + ex.Message); }
        }

        /// <summary>Logs an actor's first live projectile two frames after it spawns, when its collider has been built.</summary>
        public static void WatchFirstShot(AIActor a)
        {
            if (a == null || a.bulletBank == null) return;
            string who = a.GetActorName();
            bool logged = false;
            a.bulletBank.OnBulletSpawned += delegate (Bullet bullet, Projectile projectile)
            {
                if (logged || projectile == null || GameManager.Instance == null) return;
                logged = true;
                GameManager.Instance.StartCoroutine(LogLater(who + " first shot", projectile));
            };
        }

        private static IEnumerator LogLater(string label, Projectile p)
        {
            yield return null;
            yield return null;
            if (p != null) LogBullet(label, p);
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
                            Entry(kin, e.Name, r.Sprite, r.W, r.H, r.HitW, r.HitH, r.Rotates);
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
                // Phase 1, 100-60 %: "Consultation". Aimed bursts (he plants for the tell, moves while firing), fans, slow
                // pills, and a sidestep hop between attacks. About one pattern every 2.5 s.
                Item("booster shot", 1.2f, Aimed(Shoot(typeof(BoosterShotScript), shootPoint, 1.6f * c, 0.6f, 1f, minRange: 4f, attackCooldown: 0.5f))),
                Item("spray bottle", 1.2f, Shoot(typeof(SprayBottleScript), shootPoint, 2.4f * c, 0.6f, 1f, range: 8f, attackCooldown: 0.6f)),
                Item("pill time", 0.8f, Shoot(typeof(PillTimeScript), shootPoint, 3.5f * c, 0.6f, 1f, attackCooldown: 0.8f, initialCooldown: 4f)),
                Item("hop 1", 1.0f, BossHop(PastConfig.BossHopCooldown * 1.35f * c, 0.6f, 1f, 0f)),
                // Phase 2, 60-25 %: "Treatment". Quicker bursts, the droplet wall, the spiral, the cone, stitches that hang and
                // re-aim, the scalpel ring with its gap, anesthesia clouds, and the leap-in ring.
                Item("booster shot 2", 1.2f, Aimed(Shoot(typeof(BoosterShotScript), shootPoint, 1.1f * c, 0.25f, 0.6f, minRange: 4f, attackCooldown: 0.5f))),
                Item("spray bottle 2", 1.0f, Shoot(typeof(SprayBottleScript), shootPoint, 1.5f * c, 0.25f, 0.6f, range: 8f, attackCooldown: 0.6f)),
                Item("droplet wall", 1.0f, Shoot(typeof(DropletWallScript), shootPoint, 3.0f * c, 0.25f, 0.6f, minRange: 5f, attackCooldown: 0.8f)),
                Item("vaccination spiral", 0.7f, Shoot(typeof(VaccinationSpiralScript), shootPoint, 5.0f * c, 0.25f, 0.6f, attackCooldown: 1.0f, initialCooldown: 3f)),
                Item("cone of shame", 0.8f, Shoot(typeof(ConeOfShameScript), shootPoint, 3.5f * c, 0.25f, 0.6f, attackCooldown: 0.8f)),
                Item("stitches", 0.9f, Shoot(typeof(StitchesScript), shootPoint, 5.0f * c, 0.25f, 0.6f, attackCooldown: 1.0f, initialCooldown: 2f)),
                Item("scalpel ring", 0.9f, Shoot(typeof(ScalpelRingScript), shootPoint, 3.5f * c, 0.25f, 0.6f, attackCooldown: 0.8f)),
                Item("anesthesia", 0.6f, Shoot(typeof(AnesthesiaCloudScript), shootPoint, 6.0f * c, 0.25f, 0.6f, attackCooldown: 1.0f, initialCooldown: 3f)),
                Item("hop 2", 1.2f, BossHop(PastConfig.BossHopCooldown * c, 0.25f, 0.6f, 0f)),
                Item("leap and ring", 0.6f, LeapRing(shootPoint, 7f * c, 0f, 0.6f)),
                // Phase 3, last quarter: "Just a little snip". Fast leading bursts, the hard wall, the full course (wall then
                // spiral back to back), quicker stitches and rings, clouds, double hops.
                Item("snip time", 1.5f, Aimed(Shoot(typeof(SnipTimeScript), shootPoint, 1.4f * c, 0f, 0.25f, attackCooldown: 0.5f, masked: VetMask.Available))),
                Item("cone of shame 3", 0.8f, Shoot(typeof(ConeOfShameScript), shootPoint, 3.0f * c, 0f, 0.25f, attackCooldown: 0.8f, masked: VetMask.Available)),
                Item("droplet wall 3", 1.0f, Shoot(typeof(DropletWallHardScript), shootPoint, 2.6f * c, 0f, 0.25f, minRange: 5f, attackCooldown: 0.8f, masked: VetMask.Available)),
                Item("stitches 3", 0.9f, Shoot(typeof(StitchesScript), shootPoint, 3.5f * c, 0f, 0.25f, attackCooldown: 1.0f, masked: VetMask.Available)),
                Item("scalpel ring 3", 0.9f, Shoot(typeof(ScalpelRingScript), shootPoint, 3.0f * c, 0f, 0.25f, attackCooldown: 0.8f, masked: VetMask.Available)),
                Item("anesthesia 3", 0.6f, Shoot(typeof(AnesthesiaCloudScript), shootPoint, 5.0f * c, 0f, 0.25f, attackCooldown: 1.0f, masked: VetMask.Available)),
                Item("hop 3", 1.5f, BossHop(PastConfig.BossHopCooldown * 0.7f * c, 0f, 0.25f, 0.35f)),
                new AttackBehaviorGroup.AttackGroupItem
                {
                    NickName = "full course",
                    Probability = 1.0f,
                    Behavior = new SequentialAttackBehaviorGroup
                    {
                        RunInClass = false,
                        AttackBehaviors = new List<AttackBehaviorBase>
                        {
                            Shoot(typeof(DropletWallScript), shootPoint, 4.0f * c, 0f, 0.25f, minRange: 5f, attackCooldown: 1.0f, masked: VetMask.Available),
                            Shoot(typeof(VaccinationSpiralScript), shootPoint, 4.0f * c, 0f, 0.25f, attackCooldown: 1.0f, masked: VetMask.Available),
                        },
                        OverrideCooldowns = new List<float> { 0.4f },
                    }
                },
            };
        }

        /// <summary>An aimed pattern: he stops for the tell, then keeps moving while the bullets go out (vanilla quickshots).</summary>
        private static ShootBehavior Aimed(ShootBehavior shoot)
        {
            shoot.StopDuring = ShootBehavior.StopType.TellOnly;
            return shoot;
        }

        /// <summary>A four-tile hop to Pluto's side, never toward him, between patterns (the Gun Cultist's roll without a clip).</summary>
        private static DashBehavior BossHop(float cooldown, float minHealth, float maxHealth, float doubleChance)
        {
            DashBehavior hop = VetTech.Hop(DashBehavior.DashDirection.PerpendicularToTarget, 4f, 0.3f, cooldown, 1f, 1.5f, 0f, true);
            hop.MinHealthThreshold = minHealth;
            hop.MaxHealthThreshold = maxHealth;
            hop.doubleDashChance = doubleChance;
            hop.AttackCooldown = 0.2f;
            return hop;
        }

        /// <summary>A five-tile leap in, then the scalpel ring from where he lands.</summary>
        private static SequentialAttackBehaviorGroup LeapRing(GameObject shootPoint, float cooldown, float minHealth, float maxHealth)
        {
            DashBehavior leap = VetTech.Hop(DashBehavior.DashDirection.KindaTowardTarget, 5f, 0.35f, cooldown, 1f, 4f, 0f, false);
            leap.MinHealthThreshold = minHealth;
            leap.MaxHealthThreshold = maxHealth;
            return new SequentialAttackBehaviorGroup
            {
                RunInClass = false,
                AttackBehaviors = new List<AttackBehaviorBase> { leap, Shoot(typeof(ScalpelRingScript), shootPoint, 0f, minHealth, maxHealth, attackCooldown: 0.8f) },
                OverrideCooldowns = new List<float> { 0.2f },
            };
        }

        public static AttackBehaviorGroup.AttackGroupItem Item(string nick, float probability, AttackBehaviorBase behavior)
        {
            return new AttackBehaviorGroup.AttackGroupItem { NickName = nick, Probability = probability, Behavior = behavior };
        }

        /// <summary>An attack usable while health is between minHealth and maxHealth (fractions of max).</summary>
        public static ShootBehavior Shoot(Type script, GameObject shootPoint, float cooldown, float minHealth, float maxHealth, float minRange = 0f, float range = 40f, float attackCooldown = 0.4f, float initialCooldown = 1f, bool masked = false)
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
                Uninterruptible = true,   // vanilla bosses and adds finish a pattern once it starts; a hit never cancels a tell
                TellAnimation = masked ? "mask_tell" : "tell",
                FireAnimation = masked ? "mask_fire" : "fire",
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
        private bool called, lastFifth, phaseTwo;

        private void Start()
        {
            if (healthHaver != null) healthHaver.OnDamaged += OnDamaged;
        }

        private void OnDamaged(float resultValue, float maxValue, CoreDamageTypes damageTypes, DamageCategory damageCategory, Vector2 damageDirection)
        {
            if (maxValue <= 0f || VetVisitController.Instance == null) return;
            if (!phaseTwo && resultValue <= maxValue * 0.6f)
            {
                phaseTwo = true;
                VetVisitController.Instance.PhaseLine(PastConfig.FightPhase2);
            }
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
