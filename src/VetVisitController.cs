using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Dungeonator;
using Gungeon;

namespace PlutoVetVisit
{
    /// <summary>
    /// Placed in the clinic room by name (ClinicLayout.CONTROLLER_OBJECT). Runs the past through its three zones:
    /// the waiting room (no combat), the ward (two waves behind a sealed door), the operating theatre (dialogue,
    /// the boss) and the ending. Modelled on the vanilla PastLabMarineController / PilotPastController.
    /// </summary>
    public class VetVisitController : MonoBehaviour
    {
        public static VetVisitController Instance;

        private RoomHandler room;
        private Vector2 origin; // world position of room cell (0, 0)
        private bool ending;
        private AIActor vet;
        private ClinicDoor wardDoor, theatreDoor;

        private IEnumerator Start()
        {
            Instance = this;
            while (Dungeon.IsGenerating) yield return null;
            yield return null;
            room = ((Vector2)transform.position).GetAbsoluteRoom();
            origin = (Vector2)transform.position - ClinicLayout.Controller;
            PastPlugin.Log("clinic ready, origin " + origin + ", room " + (room != null ? room.GetRoomName() : "null"));

            // The Ark wrote a FINALGEON mid-game save before loading us; the game cannot resume it for a
            // custom character, so remove it (the win page deletes it in vanilla too).
            SaveManager.DeleteCurrentSlotMidGameSave();

            PlayerController player = GameManager.Instance.PrimaryPlayer;
            Place(player, ClinicLayout.Spawn);
            EnsureLoadout(player, "on arrival");
            if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER)
            {
                Place(GameManager.Instance.SecondaryPlayer, ClinicLayout.Spawn + new Vector2(1.5f, 0f));
                EnsureLoadout(GameManager.Instance.SecondaryPlayer, "on arrival");
            }
            StartCoroutine(LoadoutWatchdog());
            Pixelator.Instance.TriggerPastFadeIn();
            yield return new WaitForSeconds(0.5f);
            if (PastConfig.DebugEndAfterSeconds > 0f) StartCoroutine(DebugEnding());
            FindDoors();
            yield return StartCoroutine(RunZones(player));
        }

        // ------------------------------------------------------------------ zones and gates

        /// <summary>The two placed door clones, told apart by height: the ward door is the lower one.</summary>
        private void FindDoors()
        {
            List<ClinicDoor> doors = new List<ClinicDoor>(ClinicDoor.All);
            doors.RemoveAll(d => d == null);
            doors.Sort((a, b) => a.transform.position.y.CompareTo(b.transform.position.y));
            if (doors.Count >= 1) wardDoor = doors[0];
            if (doors.Count >= 2) theatreDoor = doors[1];
            PastPlugin.Log("doors found: " + doors.Count + " (expected 2)");
        }

        private static void SetDoor(ClinicDoor door, bool open, string what)
        {
            if (door == null) { PastPlugin.Log(what + ": no door prop, nothing to " + (open ? "open" : "close")); return; }
            door.SetOpen(open);
            try { AkSoundEngine.PostEvent(open ? "Play_OBJ_door_open_01" : "Play_OBJ_door_close_01", door.gameObject); } catch (Exception) { }
            PastPlugin.Log(what);
        }

        /// <summary>Act 1 (walk), act 2 (two waves behind the sealed ward door), act 3 (the Vet).</summary>
        private IEnumerator RunZones(PlayerController player)
        {
            // Act 1: the waiting room. The Owner checks Pluto in and leaves; the intercom calls; the ward door opens.
            if (!PastConfig.SkipIntro) yield return StartCoroutine(Intro(player));
            else HideOwner();
            SpawnCritters();
            SetDoor(wardDoor, true, "the ward door opens");
            yield return StartCoroutine(WaitForZone(ClinicLayout.WARD_MIN_Y + 1.5f));

            // Act 2: the ward. Sealed behind Pluto; two waves; the theatre door opens when the second is dead.
            SetDoor(wardDoor, false, "the ward door closes behind Pluto");
            if (PastConfig.SkipWaves) PastPlugin.Log("debug: waves skipped");
            else
            {
                if (!PastConfig.SkipIntro) yield return StartCoroutine(WardGreeting(player));
                yield return StartCoroutine(RunWave("wave 1", PastConfig.Wave1, ClinicLayout.Wave1Spawns));
                if (wave1Extra != null && wave1Extra.healthHaver != null && !wave1Extra.healthHaver.IsDead)
                {
                    while (wave1Extra != null && wave1Extra.healthHaver != null && !wave1Extra.healthHaver.IsDead) yield return null;
                }
                Bubble(Intercom(), PastConfig.Ward4, 2.2f);
                yield return StartCoroutine(RunWave("wave 2", PastConfig.Wave2, ClinicLayout.Wave2Spawns));
                SpawnHearts();
            }
            Bubble(Intercom(), PastConfig.Ward5, 3f);
            SetDoor(theatreDoor, true, "the theatre door opens");
            yield return StartCoroutine(WaitForZone(ClinicLayout.THEATRE_MIN_Y + 1.5f));

            // Act 3: the operating theatre.
            SetDoor(theatreDoor, false, "the theatre door closes behind Pluto");
            vet = SpawnVet();
            if (!PastConfig.SkipIntro) yield return StartCoroutine(Dialogue(player));
            StartFight(player);
        }

        /// <summary>Waits until any player's centre is past the given room-cell height.</summary>
        private IEnumerator WaitForZone(float cellY)
        {
            while (true)
            {
                if (PlayerPast(GameManager.Instance.PrimaryPlayer, cellY)) yield break;
                if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER && PlayerPast(GameManager.Instance.SecondaryPlayer, cellY)) yield break;
                yield return null;
            }
        }

        private bool PlayerPast(PlayerController p, float cellY)
        {
            return p != null && p.healthHaver != null && !p.healthHaver.IsDead && p.CenterPosition.y - origin.y >= cellY;
        }

        // ------------------------------------------------------------------ act 1: the intro

        private Transform intercom;

        private Transform Intercom()
        {
            if (intercom == null)
            {
                GameObject go = new GameObject("VetIntercom");
                Vector2 w = World(ClinicLayout.Intercom);
                go.transform.position = new Vector3(w.x, w.y, w.y);
                intercom = go.transform;
            }
            return intercom;
        }

        /// <summary>Check-in at the desk, two patients' warnings, the intercom, the Owner leaves. Any line can be skipped.</summary>
        private IEnumerator Intro(PlayerController player)
        {
            ClinicNpc owner = ClinicNpc.Find("owner"), desk = ClinicNpc.Find("receptionist"), rex = ClinicNpc.Find("rex"), grandma = ClinicNpc.Find("grandma");
            PastPlugin.Log("intro: owner " + (owner != null) + ", receptionist " + (desk != null) + ", rex " + (rex != null) + ", grandma " + (grandma != null));
            bool coop = GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER;
            player.SetInputOverride("past");
            if (coop && GameManager.Instance.SecondaryPlayer != null) GameManager.Instance.SecondaryPlayer.SetInputOverride("past");
            PastCameraUtility.LockConversation(World(ClinicLayout.IntroFocus));
            try
            {
                yield return new WaitForSeconds(0.8f);
                if (owner != null) owner.Face(true);
                yield return StartCoroutine(Line(desk, PastConfig.Intro1, 1.8f));
                yield return StartCoroutine(Line(owner, PastConfig.Intro2, 3f));
                yield return StartCoroutine(Line(desk, PastConfig.Intro3, 1.8f));
                yield return new WaitForSeconds(0.4f);
                yield return StartCoroutine(Line(rex, PastConfig.Intro4, 2.5f));
                yield return StartCoroutine(Line(grandma, PastConfig.Intro5, 2.5f));
                yield return new WaitForSeconds(0.4f);
                yield return StartCoroutine(Say(Intercom(), PastConfig.Intro6, 1.6f));
                yield return StartCoroutine(Line(owner, PastConfig.Intro7, 2f));
                if (owner != null)
                {
                    owner.Face(false);
                    yield return StartCoroutine(owner.Walk(World(ClinicLayout.OwnerExit), 4.5f, "walk_free"));
                    owner.Hide();
                }
            }
            finally
            {
                PastCameraUtility.UnlockConversation();
                player.ClearInputOverride("past");
                if (coop && GameManager.Instance.SecondaryPlayer != null) GameManager.Instance.SecondaryPlayer.ClearInputOverride("past");
            }
        }

        private void HideOwner()
        {
            ClinicNpc owner = ClinicNpc.Find("owner");
            if (owner != null) owner.Hide();
        }

        /// <summary>A bystander's line: talk clip while the box shows; the box can be advanced with the interact key.</summary>
        private IEnumerator Line(ClinicNpc who, string text, float seconds)
        {
            if (who == null) yield break;
            who.Play("talk");
            yield return StartCoroutine(Say(who.talkPoint, text, seconds));
            who.Play(who.idleClip);
        }

        // The waiting room's loose critters: vanilla chick, rabbit and squirrel, harmless, left to wander.
        private static readonly string[] CRITTERS = { "chick", "rabbit", "squirrel" };

        private void SpawnCritters()
        {
            for (int i = 0; i < CRITTERS.Length; i++)
            {
                try
                {
                    AIActor prefab = ResolveEnemy(CRITTERS[i]);
                    if (prefab == null) continue;
                    Vector2 cell = new Vector2(8f + 4f * i, 5f + (i % 2) * 2f);
                    AIActor a = AIActor.Spawn(prefab, World(cell), room, true, AIActor.AwakenAnimationType.Default, true);
                    if (a != null) { a.IgnoreForRoomClear = true; a.CanDropCurrency = false; }
                }
                catch (Exception e) { PastPlugin.Log("no " + CRITTERS[i] + ": " + e.Message); }
            }
        }

        /// <summary>Two hearts on the nurse station once the ward is clear (the v2 design's "cat-bowl hearts").</summary>
        private void SpawnHearts()
        {
            try
            {
                PickupObject heart = PickupObjectDatabase.GetById(85);   // Heart
                if (heart == null) return;
                LootEngine.SpawnItem(heart.gameObject, World(new Vector2(14.5f, 24.6f)), Vector2.zero, 0f, true, false, false);
                LootEngine.SpawnItem(heart.gameObject, World(new Vector2(16.5f, 24.6f)), Vector2.zero, 0f, true, false, false);
                PastPlugin.Log("hearts on the nurse station");
            }
            catch (Exception e) { PastPlugin.Log("no hearts: " + e.Message); }
        }

        // ------------------------------------------------------------------ act 3: reinforcements

        private bool reinforced;

        /// <summary>Called by the Vet (VetReinforcements) below half health: the Nurse and two Techs from the east door.</summary>
        public void CallReinforcements()
        {
            if (reinforced || ending) return;
            reinforced = true;
            if (vet != null) Bubble(vet.transform, PastConfig.Fight1, 2.5f);
            StartCoroutine(Reinforce());
            PastPlugin.Log("the Vet calls the Nurse");
        }

        private IEnumerator Reinforce()
        {
            yield return new WaitForSeconds(1.2f);
            List<AIActor> adds = SpawnWave("reinforcements", "nurse,vet_tech,vet_tech", ClinicLayout.TheatreSpawns);
            foreach (AIActor a in adds)
            {
                if (a == null) continue;
                bool nurse = a.GetActorName() == "The Nurse" || a.name.Contains("Nurse");
                Bubble(a.transform, nurse ? PastConfig.Fight2 : PastConfig.Fight3, 2f);
                break;   // one arrival line is enough
            }
            if (adds.Count > 0) StartCoroutine(Heartbeat("reinforcements", adds));
        }

        /// <summary>The Vet's last-fifth line (VetReinforcements calls it once).</summary>
        public void LastFifth()
        {
            if (vet != null && !ending) Bubble(vet.transform, PastConfig.Fight4, 2.5f);
        }

        // ------------------------------------------------------------------ waves

        // Console names the config accepts without a GUID (vanilla enemies used by the v2 design).
        private static readonly Dictionary<string, string> ENEMY_GUIDS = new Dictionary<string, string>
        {
            { "vet_tech", VetTech.GUID },
            { "nurse", Nurse.GUID },
            { "rat", "6ad1cafc268f4214a101dca7af61bc91" },
            { "parrot", "4b21a913e8c54056bc05cafecf9da880" },
            { "mutant_bullet_kin", "d4a9836f8ab14f3fadd0f597438b1f1f" },
            { "bullet_kin", "01972dee89fc4404a5c408d50007dad5" },
            { "chick", "95ea1a31fc9e4415a5f271b9aedf9b15" },
            { "rabbit", "42432592685e47c9941e339879379d3a" },
            { "squirrel", "4254a93fc3c84c0dbe0a8f0dddf48a5a" },
        };

        private static AIActor ResolveEnemy(string token)
        {
            token = token.Trim();
            if (token.Length == 0) return null;
            string guid;
            if (!ENEMY_GUIDS.TryGetValue(token, out guid)) guid = token;
            try { return EnemyDatabase.GetOrLoadByGuid(guid); }
            catch (Exception e) { PastPlugin.Log("unknown enemy '" + token + "': " + e.Message); return null; }
        }

        /// <summary>Spawns one wave at the given cells and waits until every actor of it is dead.</summary>
        private IEnumerator RunWave(string label, string list, Vector2[] cells)
        {
            List<AIActor> alive = SpawnWave(label, list, cells);
            if (alive.Count == 0) yield break;
            StartCoroutine(Heartbeat(label, alive));
            float waited = 0f;
            while (true)
            {
                alive.RemoveAll(a => a == null || a.healthHaver == null || a.healthHaver.IsDead);
                if (alive.Count == 0) break;
                waited += BraveTime.DeltaTime;
                if (PastConfig.WaveTimeoutSeconds > 0f && waited > PastConfig.WaveTimeoutSeconds)
                {
                    PastPlugin.Log(label + ": " + alive.Count + " still alive after " + PastConfig.WaveTimeoutSeconds + " s; putting them down");
                    foreach (AIActor a in alive)
                        try { a.healthHaver.ApplyDamage(1e6f, Vector2.zero, "vetvisit", CoreDamageTypes.None, DamageCategory.Unstoppable, true, null, true); }
                        catch (Exception e) { PastPlugin.Log("could not put down " + a.name + ": " + e.Message); }
                    break;
                }
                yield return null;
            }
            PastPlugin.Log(label + " cleared");
            yield return new WaitForSeconds(0.75f);
        }

        private List<AIActor> SpawnWave(string label, string list, Vector2[] cells)
        {
            List<AIActor> alive = new List<AIActor>();
            string[] tokens = (list ?? string.Empty).Split(',');
            int i = 0;
            foreach (string token in tokens)
            {
                AIActor prefab = ResolveEnemy(token);
                if (prefab == null || cells == null || cells.Length == 0) continue;
                Vector2 cell = cells[i % cells.Length];
                i++;
                try
                {
                    AIActor a = AIActor.Spawn(prefab, World(cell), room, true, AIActor.AwakenAnimationType.Default, true);
                    if (a == null) continue;
                    a.IgnoreForRoomClear = true;    // the room's own clear bookkeeping (rewards, unseal) stays out of it
                    Engage(a);
                    alive.Add(a);
                }
                catch (Exception e) { PastPlugin.Log(label + ": could not spawn " + token + ": " + e.Message); }
            }
            PastPlugin.Log(label + ": " + alive.Count + " enemies");
            return alive;
        }

        /// <summary>Everything a spawned actor needs to actually fight in a room the player is already inside:
        /// engaged, awake, brain on, damage allowed. The player-entered-the-room trigger never fires for them.</summary>
        public static void Engage(AIActor a)
        {
            if (a == null) return;
            try
            {
                a.HasBeenEngaged = true;
                a.State = AIActor.ActorState.Normal;
                if (a.behaviorSpeculator != null) a.behaviorSpeculator.enabled = true;
                if (a.healthHaver != null) a.healthHaver.PreventAllDamage = false;
                if (a.specRigidbody != null) a.specRigidbody.enabled = true;
            }
            catch (Exception e) { PastPlugin.Log("engage failed for " + a.name + ": " + e.Message); }
        }

        /// <summary>Logs each wave actor's state at 2 s and 8 s and forces a target on anyone still idle.</summary>
        private IEnumerator Heartbeat(string label, List<AIActor> actors)
        {
            foreach (float delay in new[] { 2f, 6f })
            {
                yield return new WaitForSeconds(delay);
                PlayerController target = GameManager.Instance.PrimaryPlayer;
                foreach (AIActor a in actors)
                {
                    if (a == null || a.healthHaver == null || a.healthHaver.IsDead) continue;
                    bool hasTarget = a.TargetRigidbody != null;
                    PastPlugin.Log(label + " " + a.GetActorName() + ": state " + a.State + ", brain " + (a.behaviorSpeculator != null && a.behaviorSpeculator.enabled)
                        + ", engaged " + a.HasBeenEngaged + ", target " + hasTarget + ", gone " + a.IsGone);
                    if (!hasTarget && target != null && target.specRigidbody != null)
                    {
                        a.OverrideTarget = target.specRigidbody;   // the same hook Coco's decoy uses: a target the brain cannot miss
                        PastPlugin.Log(label + " " + a.GetActorName() + ": no target after " + delay + " s, forcing Pluto");
                    }
                }
            }
        }

        // ------------------------------------------------------------------ talk: timed bubbles over actors

        /// <summary>A timed speech bubble that does not block (the fight goes on): shouts, taunts, arrivals.</summary>
        public void Bubble(Transform who, string text, float seconds)
        {
            if (who == null || string.IsNullOrEmpty(text)) return;
            StartCoroutine(BubbleCR(who, text, seconds));
        }

        private IEnumerator BubbleCR(Transform who, string text, float seconds)
        {
            Vector3 pos = who.position + new Vector3(0f, 2.0f, 0f);
            try { TextBoxManager.ShowTextBox(pos, who, seconds, text, string.Empty, false, TextBoxManager.BoxSlideOrientation.NO_ADJUSTMENT, false, false); }
            catch (Exception e) { PastPlugin.Log("bubble failed: " + e.Message); yield break; }
            yield return new WaitForSeconds(seconds + 0.1f);
            if (who != null) TextBoxManager.ClearTextBox(who);
        }

        /// <summary>Act 2 greeting: one Tech steps out, hails Pluto, then the wave attacks (vanilla pasts talk before they shoot).</summary>
        private IEnumerator WardGreeting(PlayerController player)
        {
            AIActor prefab = ResolveEnemy("vet_tech");
            if (prefab == null) yield break;
            AIActor greeter = null;
            try
            {
                greeter = AIActor.Spawn(prefab, World(ClinicLayout.GreeterSpot), room, true, AIActor.AwakenAnimationType.Default, false);
                if (greeter != null)
                {
                    greeter.IgnoreForRoomClear = true;
                    greeter.healthHaver.PreventAllDamage = true;
                    if (greeter.behaviorSpeculator != null) greeter.behaviorSpeculator.enabled = false;
                }
            }
            catch (Exception e) { PastPlugin.Log("greeter: " + e.Message); }
            if (greeter == null) yield break;
            bool coop = GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER;
            player.SetInputOverride("past");
            if (coop && GameManager.Instance.SecondaryPlayer != null) GameManager.Instance.SecondaryPlayer.SetInputOverride("past");
            PastCameraUtility.LockConversation(World(ClinicLayout.GreeterSpot) + new Vector2(0f, -1.5f));
            try
            {
                yield return new WaitForSeconds(0.6f);
                yield return StartCoroutine(Say(greeter.transform, PastConfig.Ward1, 2.4f));
                yield return StartCoroutine(Say(greeter.transform, PastConfig.Ward2, 2.6f));
                yield return StartCoroutine(Say(player.transform, PastConfig.Ward3, 1.4f));
            }
            finally
            {
                PastCameraUtility.UnlockConversation();
                player.ClearInputOverride("past");
                if (coop && GameManager.Instance.SecondaryPlayer != null) GameManager.Instance.SecondaryPlayer.ClearInputOverride("past");
            }
            Engage(greeter);
            wave1Extra = greeter;
        }

        private AIActor wave1Extra;

        private IEnumerator DebugEnding()
        {
            PastPlugin.Log("debug: ending the past in " + PastConfig.DebugEndAfterSeconds + " s");
            yield return new WaitForSeconds(PastConfig.DebugEndAfterSeconds);
            OnBossDied();
        }

        /// <summary>The Vet stands behind the table, visible but inert, until the intro finishes.</summary>
        private AIActor SpawnVet()
        {
            if (room == null)
            {
                PastPlugin.Log("no room for the Vet; the fight cannot start");
                return null;
            }
            if (VetBoss.Prefab == null)
            {
                PastPlugin.Log("no boss prefab; the clinic stays empty");
                return null;
            }
            AIActor prefab = VetBoss.Prefab.GetComponent<AIActor>();
            AIActor a = AIActor.Spawn(prefab, World(ClinicLayout.Vet), room, true, AIActor.AwakenAnimationType.Default, false);
            a.gameObject.name = "The Vet";
            a.behaviorSpeculator.enabled = false;
            a.healthHaver.PreventAllDamage = true;
            PastPlugin.Log("The Vet spawned at " + World(ClinicLayout.Vet));
            return a;
        }

        // Pluto's starting loadout (console ids). Vanilla pasts strip the run's items and hand the
        // Gungeoneer their starting gear back; a custom character's lists can come through empty.
        private static readonly string[] STARTING_GUNS = { "pluto:kibble_sack" };
        private static readonly string[] STARTING_ITEMS = { "pluto:wet_food_can", "pluto:squeaky_toy", "pluto:nine_lives", "pluto:coco_blue", "pluto:puffed_up" };

        /// <summary>Make sure Pluto arrives armed. The Ark resets every player with ResetToFactorySettings
        /// (guns destroyed, starting guns re-added from startingGunIds); if that list came through empty or
        /// the gun did not stick, give the sack by id through the same call the game uses, then the loot
        /// engine as a fallback. Logs every step so a test run tells us which path fired.</summary>
        private void EnsureLoadout(PlayerController p, string when)
        {
            if (p == null || p.inventory == null) return;
            try
            {
                int before = p.inventory.AllGuns != null ? p.inventory.AllGuns.Count : 0;
                if (before == 0)
                {
                    PastPlugin.Log("loadout " + when + ": no guns (startingGunIds " + (p.startingGunIds != null ? p.startingGunIds.Count : -1) + ")");
                    if (p.startingGunIds != null && p.startingGunIds.Count > 0)
                    {
                        try { p.ReinitializeGuns(); } catch (Exception e) { PastPlugin.Log("ReinitializeGuns failed: " + e.Message); }
                    }
                }
                if (p.inventory.AllGuns == null || p.inventory.AllGuns.Count == 0)
                    foreach (string id in STARTING_GUNS) GiveGun(p, id);
                foreach (string id in STARTING_ITEMS) Give(p, id);
                if (p.inventory.AllGuns != null && p.inventory.AllGuns.Count > 0)
                {
                    if (p.inventory.GunLocked != null && p.inventory.GunLocked.Value) PastPlugin.Log("warning: the inventory reports GunLocked");
                    if (p.CurrentGun == null) p.inventory.ChangeGun(1);
                }
                p.ToggleGunRenderers(true, "vetvisit");
                p.ToggleHandRenderers(true, "vetvisit");
                int after = p.inventory.AllGuns != null ? p.inventory.AllGuns.Count : 0;
                if (after != before || when == "on arrival")
                    PastPlugin.Log("loadout " + when + ": " + after + " gun(s), current " + (p.CurrentGun != null ? p.CurrentGun.EncounterNameOrDisplayName : "none")
                        + ", input " + p.CurrentInputState + ", overrides " + (p.IsInputOverridden ? "yes" : "no"));
            }
            catch (Exception e) { PastPlugin.Log("loadout check failed: " + e.Message); }
        }

        /// <summary>Re-checks the guns during the first minute: whatever strips them after our Start gets undone.</summary>
        private IEnumerator LoadoutWatchdog()
        {
            float[] at = { 1f, 3f, 6f, 10f, 20f, 40f, 60f };
            float t = 0f;
            int i = 0;
            while (i < at.Length && !ending)
            {
                t += BraveTime.DeltaTime;
                if (t >= at[i])
                {
                    EnsureLoadout(GameManager.Instance.PrimaryPlayer, "at " + at[i] + " s");
                    if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER) EnsureLoadout(GameManager.Instance.SecondaryPlayer, "at " + at[i] + " s");
                    i++;
                }
                yield return null;
            }
        }

        /// <summary>The game's own path first (PickupObjectDatabase + AddGunToInventory), the loot engine second.</summary>
        private static void GiveGun(PlayerController p, string id)
        {
            try
            {
                if (!Game.Items.ContainsID(id)) { PastPlugin.Log("gun id not registered: " + id); return; }
                PickupObject item = Game.Items[id];
                if (item == null) { PastPlugin.Log("gun prefab null: " + id); return; }
                if (p.HasPickupID(item.PickupObjectId)) return;
                Gun gun = PickupObjectDatabase.GetById(item.PickupObjectId) as Gun;
                if (gun != null)
                {
                    p.inventory.AddGunToInventory(gun, true);
                    PastPlugin.Log("gave gun " + id + " via AddGunToInventory");
                }
                if (!p.HasPickupID(item.PickupObjectId))
                {
                    LootEngine.GivePrefabToPlayer(item.gameObject, p);
                    PastPlugin.Log("gave gun " + id + " via LootEngine");
                }
            }
            catch (Exception e) { PastPlugin.Log("could not give gun " + id + ": " + e.Message); }
        }

        private static void Give(PlayerController p, string id)
        {
            try
            {
                if (!Game.Items.ContainsID(id)) return;
                PickupObject item = Game.Items[id];
                if (item == null || p.HasPickupID(item.PickupObjectId)) return;
                LootEngine.GivePrefabToPlayer(item.gameObject, p);
                PastPlugin.Log("gave " + id);
            }
            catch (Exception e) { PastPlugin.Log("could not give " + id + ": " + e.Message); }
        }

        /// <summary>Console: vet_loadout re-runs the loadout check by hand.</summary>
        public void ConsoleLoadout()
        {
            EnsureLoadout(GameManager.Instance.PrimaryPlayer, "console");
        }

        private bool woken;

        private void StartFight(PlayerController player)
        {
            if (vet == null) return;
            if (room == null)
            {
                PastPlugin.Log("no room for the Vet; the fight cannot start");
                return;
            }
            GenericIntroDoer intro = vet.GetComponent<GenericIntroDoer>();
            if (intro == null)
            {
                Wake();
                return;
            }
            intro.ConfigureOnPlacement(room);
            intro.OnIntroFinished = Wake;
            intro.TriggerSequence(player); // walk-in, boss card, health bar, boss music
            StartCoroutine(FightWatchdog(14f));
        }

        /// <summary>If the intro never reports back (a missing clip, a skipped callback), start the fight anyway.</summary>
        private IEnumerator FightWatchdog(float seconds)
        {
            yield return new WaitForSeconds(seconds);
            if (!woken)
            {
                PastPlugin.Log("intro did not finish after " + seconds + " s; starting the fight anyway");
                Wake();
            }
        }

        private void Wake()
        {
            if (vet == null || woken) return;
            woken = true;
            Engage(vet);
            StartCoroutine(Heartbeat("the Vet", new List<AIActor> { vet }));
            PastPlugin.Log("fight started");
        }

        public Vector2 World(Vector2 cell)
        {
            return origin + cell;
        }

        private void Place(PlayerController p, Vector2 cell)
        {
            if (p == null) return;
            Vector2 w = World(cell);
            p.transform.position = new Vector3(w.x, w.y, w.y);
            p.specRigidbody.Reinitialize();
            p.sprite.UpdateZDepth();
        }

        private GameObject speaker;

        protected virtual Transform SpeakerTransform()
        {
            if (vet != null) return vet.transform;
            if (speaker == null)
            {
                speaker = new GameObject("VetSpeaker");
                Vector2 w = World(ClinicLayout.Vet);
                speaker.transform.position = new Vector3(w.x, w.y, w.y);
            }
            return speaker.transform;
        }

        private IEnumerator Dialogue(PlayerController player)
        {
            bool coop = GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER;
            player.SetInputOverride("past");
            if (coop && GameManager.Instance.SecondaryPlayer != null) GameManager.Instance.SecondaryPlayer.SetInputOverride("past");
            PastCameraUtility.LockConversation(World(ClinicLayout.CameraFocus));
            try
            {
                yield return new WaitForSeconds(0.8f);
                Transform who = SpeakerTransform();
                yield return StartCoroutine(Say(who, PastConfig.Line1, 2.5f));
                yield return StartCoroutine(Say(who, PastConfig.Line2, 3.5f));
                yield return StartCoroutine(Say(player.transform, PastConfig.Line3, 1.5f));
            }
            finally
            {
                PastCameraUtility.UnlockConversation();
                player.ClearInputOverride("past");
                if (coop && GameManager.Instance.SecondaryPlayer != null) GameManager.Instance.SecondaryPlayer.ClearInputOverride("past");
            }
        }

        private IEnumerator Say(Transform who, string text, float seconds)
        {
            if (string.IsNullOrEmpty(text)) yield break;
            Vector3 pos = who.position + new Vector3(0f, 2.25f, 0f);
            TextBoxManager.ShowTextBox(pos, who, -1f, text, string.Empty, false, TextBoxManager.BoxSlideOrientation.NO_ADJUSTMENT, true, false);
            float t = 0f;
            yield return null;
            while (t < seconds + 0.3f)
            {
                t += BraveTime.DeltaTime;
                if (t > 0.5f && BraveInput.GetInstanceForPlayer(0) != null && BraveInput.GetInstanceForPlayer(0).WasAdvanceDialoguePressed()) break;
                yield return null;
            }
            TextBoxManager.ClearTextBox(who);
        }

        public void OnBossDied()
        {
            if (ending) return;
            ending = true;
            StartCoroutine(EndPast());
        }

        /// <summary>The five things every vanilla past controller does after its boss dies.</summary>
        private IEnumerator EndPast()
        {
            // Flag first: the credits tube shows the "past complete" panel only if it is already set.
            GameStatsManager.Instance.SetCharacterSpecificFlag(PlutoLink.Identity, CharacterSpecificGungeonFlags.KILLED_PAST, true);
            GameStatsManager.Instance.RegisterStatChange(TrackedStats.TIMES_KILLED_PAST, 1f);
            PastPlugin.Log("past killed: KILLED_PAST set for identity " + (int)PlutoLink.Identity);
            if (vet != null && vet.healthHaver != null) vet.healthHaver.PreventAllDamage = true;
            yield return new WaitForSeconds(3.5f);

            PlayerController p = GameManager.Instance.PrimaryPlayer;
            PastCameraUtility.LockConversation(p.CenterPosition);
            GameManager.Instance.MainCameraController.OverridePosition = p.CenterPosition;
            yield return new WaitForSeconds(0.5f);

            if (!string.IsNullOrEmpty(PastConfig.Epilogue))
            {
                TextBoxManager.ShowLetterBox(p.CenterPosition + new Vector2(0f, 2.5f), p.transform, 4.5f, PastConfig.Epilogue, false, false);
                yield return new WaitForSeconds(4.8f);
                TextBoxManager.ClearTextBox(p.transform);
            }
            Pixelator.Instance.FreezeFrame();
            BraveTime.RegisterTimeScaleMultiplier(0f, gameObject);
            float elapsed = 0f;
            while (elapsed < ConvictPastController.FREEZE_FRAME_DURATION)
            {
                elapsed += GameManager.INVARIANT_DELTA_TIME;
                yield return null;
            }
            BraveTime.ClearMultiplier(gameObject);

            TimeTubeCreditsController credits = new TimeTubeCreditsController();
            credits.ClearDebris();
            yield return StartCoroutine(credits.HandleTimeTubeCredits(p.sprite.WorldCenter, false, null, -1));
            AmmonomiconController.Instance.OpenAmmonomicon(true, true);
        }
    }
}
