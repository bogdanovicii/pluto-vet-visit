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
            SettleAmbientLight();

            PlayerController player = GameManager.Instance.PrimaryPlayer;
            Place(player, ClinicLayout.Spawn);
            if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER)
                Place(GameManager.Instance.SecondaryPlayer, ClinicLayout.Spawn + new Vector2(1.5f, 0f));
            Pixelator.Instance.TriggerPastFadeIn();
            // The level load ends with the player's fall-spawn (NoInput, renderers hidden, then AllInput and shown);
            // repair the loadout only after that has run, or its last frame overwrites ours.
            while (GameManager.Instance.IsLoadingLevel) yield return null;
            yield return new WaitForSeconds(0.5f);
            EnsureLoadout(player, "on arrival", true);
            if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER) EnsureLoadout(GameManager.Instance.SecondaryPlayer, "on arrival", true);
            StartCoroutine(LoadoutWatchdog());
            if (PastConfig.DebugEndAfterSeconds > 0f) StartCoroutine(DebugEnding());
            FindDoors();
            yield return StartCoroutine(RunZones(player));
        }

        /// <summary>The Marine's LabAmbientLightController (if the template carries it) forces a pulsing red every frame
        /// through Dungeon.OverrideAmbientLight; switch it off so the room's own pale ambient (config) applies.</summary>
        private void SettleAmbientLight()
        {
            try
            {
                LabAmbientLightController[] labs = FindObjectsOfType<LabAmbientLightController>();
                foreach (LabAmbientLightController lab in labs) lab.enabled = false;
                if (GameManager.Instance.Dungeon != null) GameManager.Instance.Dungeon.OverrideAmbientLight = false;
                PastPlugin.Log("ambient light: " + labs.Length + " lab controller(s) disabled, room ambient " + PastConfig.AmbientR + "/" + PastConfig.AmbientG + "/" + PastConfig.AmbientB
                    + ", floor tiles " + PastConfig.FloorTiles + ", wall faces " + PastConfig.WallFaces);
            }
            catch (Exception e) { PastPlugin.Log("ambient light: " + e.Message); }
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
            // Act 1: the waiting room. Bogdan and Bianca check Pluto in and leave; the intercom calls; the ward door opens.
            if (!PastConfig.SkipIntro) yield return StartCoroutine(Intro(player));
            else HideOwners();
            SpawnCritters();
            StartCoroutine(WaitingChatter());
            SetDoor(wardDoor, true, "the ward door opens");
            ReactToDoor();
            yield return StartCoroutine(WaitForZone(ClinicLayout.WARD_MIN_Y + 1.5f));
            inWaitingRoom = false;

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
                PastTalk.Announce(this, player.transform, PastConfig.Ward4, 3f);
                yield return StartCoroutine(RunWave("wave 2", PastConfig.Wave2, ClinicLayout.Wave2Spawns));
                SpawnHearts();
            }
            PastTalk.Announce(this, player.transform, PastConfig.Ward5, 3f);
            StartCoroutine(ThoughtLater(player, PastConfig.WardThink, 2f, 3.4f));
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

        // ------------------------------------------------------------------ cutscenes: one lock, one unlock, always paired

        /// <summary>What every vanilla past does before a conversation (PastCameraUtility.LockConversation: the "past"
        /// input override on every player, letterbox, HUD off, manual camera at the focus point).</summary>
        private void BeginCutscene(string what, Vector2 focus)
        {
            cutscene = true;
            PastCameraUtility.LockConversation(focus);
            PastPlugin.Log(what + ": camera locked, input overridden");
        }

        /// <summary>The mirror image, run from a finally so a throwing line cannot leave Pluto frozen: unlock the camera,
        /// clear the override, repair the loadout, and log the input state the act ends with.</summary>
        private void EndCutscene(string what, PlayerController player)
        {
            cutscene = false;
            try { PastCameraUtility.UnlockConversation(); } catch (Exception e) { PastPlugin.Log(what + ": unlock failed: " + e.Message); }
            EnsureLoadout(player, "after " + what, true);
            if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER) EnsureLoadout(GameManager.Instance.SecondaryPlayer, "after " + what, true);
            if (player != null)
                PastPlugin.Log(what + " over: input " + player.CurrentInputState + ", nonMotion " + player.AcceptingNonMotionInput + ", overridden " + player.IsInputOverridden
                    + ", gun " + (player.CurrentGun != null ? player.CurrentGun.name : "none"));
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

        /// <summary>Act 1: the check-in at the desk (Bogdan answers, Bianca adds her bit), the patients' warnings, Pluto's first thoughts,
        /// the intercom, Bianca waves goodbye and both owners walk out. The camera pans to every speaker; any line can be advanced.</summary>
        private IEnumerator Intro(PlayerController player)
        {
            ClinicNpc bogdan = ClinicNpc.Find("bogdan"), bianca = ClinicNpc.Find("bianca"), desk = ClinicNpc.Find("receptionist"),
                rex = ClinicNpc.Find("rex"), grandma = ClinicNpc.Find("grandma");
            PastPlugin.Log("intro: bogdan " + (bogdan != null) + ", bianca " + (bianca != null) + ", receptionist " + (desk != null)
                + ", rex " + (rex != null) + ", grandma " + (grandma != null));
            BeginCutscene("intro", World(ClinicLayout.IntroFocus));
            try
            {
                yield return new WaitForSeconds(0.8f);
                yield return StartCoroutine(Line(desk, PastConfig.Intro1, 1.8f));
                yield return StartCoroutine(Line(bogdan, PastConfig.Intro2, 3f));
                yield return StartCoroutine(Line(bianca, PastConfig.IntroBianca, 2.2f));
                yield return StartCoroutine(Line(desk, PastConfig.Intro3, 1.8f));
                yield return new WaitForSeconds(0.3f);
                yield return StartCoroutine(Line(rex, PastConfig.Intro4, 2.5f));
                yield return StartCoroutine(Line(grandma, PastConfig.Intro5, 2.5f));
                yield return StartCoroutine(Line(rex, PastConfig.IntroRex2, 2.5f));
                yield return StartCoroutine(Think(player, PastConfig.IntroThink1, 1.6f));
                yield return StartCoroutine(Line(grandma, PastConfig.IntroGrandma2, 2f));
                yield return new WaitForSeconds(0.3f);
                yield return StartCoroutine(Say(Intercom(), PastConfig.Intro6, 1.6f));
                yield return StartCoroutine(Line(bianca, PastConfig.Intro7, 2.4f, "wave"));
                yield return StartCoroutine(OwnersLeave(player, bogdan, bianca));
                yield return StartCoroutine(PastTalk.PanTo(player.CenterPosition, 0.35f));   // no snap when the camera unlocks
            }
            finally
            {
                EndCutscene("intro", player);
            }
        }

        /// <summary>Both owners walk out together, Bianca on the left and Bogdan (empty-handed) a cell to her right: along the south wall
        /// to the aisle, then down through the south exit. Pluto thinks his thought while they go; then both are hidden.</summary>
        private IEnumerator OwnersLeave(PlayerController player, ClinicNpc bogdan, ClinicNpc bianca)
        {
            int walking = 0;
            if (bianca != null)
            {
                walking++;
                StartCoroutine(WalkOut(bianca, ClinicLayout.BiancaAisle, ClinicLayout.BiancaExit, "walk", delegate { walking--; }));
            }
            if (bogdan != null)
            {
                walking++;
                StartCoroutine(WalkOut(bogdan, ClinicLayout.BogdanAisle, ClinicLayout.BogdanExit, "walk_free", delegate { walking--; }));
            }
            yield return new WaitForSeconds(0.5f);
            yield return StartCoroutine(Think(player, PastConfig.IntroThink2, 1.6f));
            float guard = 8f;                                   // never wait forever on a walk that was cut short
            while (walking > 0 && guard > 0f)
            {
                guard -= BraveTime.DeltaTime;
                yield return null;
            }
            HideOwners();
        }

        private IEnumerator WalkOut(ClinicNpc who, Vector2 aisle, Vector2 exit, string clip, Action done)
        {
            try
            {
                yield return StartCoroutine(who.Walk(World(aisle), 4.5f, clip, false));
                if (who != null) yield return StartCoroutine(who.Walk(World(exit), 4.5f, clip));
            }
            finally
            {
                done();
            }
        }

        // ------------------------------------------------------------------ side characters: chatter and barks

        private bool inWaitingRoom = true;

        /// <summary>While Pluto is still in the waiting room, a bystander says something every 8-12 s ([Story] WaitingChatter, "who:line|who:line").</summary>
        private IEnumerator WaitingChatter()
        {
            string[] entries = (PastConfig.WaitingChatter ?? string.Empty).Split('|');
            int next = 0;
            while (inWaitingRoom && !ending && entries.Length > 0)
            {
                yield return new WaitForSeconds(UnityEngine.Random.Range(8f, 12f));
                if (!inWaitingRoom || cutscene || ending) continue;
                string entry = entries[next++ % entries.Length];
                int colon = entry.IndexOf(':');
                if (colon <= 0) continue;
                ClinicNpc npc = ClinicNpc.Find(entry.Substring(0, colon).Trim());
                if (npc == null) continue;
                npc.Play("talk");
                Bubble(npc.transform, entry.Substring(colon + 1).Trim(), 2.6f);
                StartCoroutine(IdleLater(npc, 2.8f));
            }
        }

        private IEnumerator IdleLater(ClinicNpc npc, float seconds)
        {
            yield return new WaitForSeconds(seconds);
            if (npc != null) npc.Play(npc.idleClip);
        }

        /// <summary>A Tech shouts when a wave starts, and now and then a surviving Tech reacts when a crewmate goes down ([Story] TechBarks).</summary>
        private void WatchBarks(List<AIActor> wave)
        {
            List<AIActor> crew = new List<AIActor>(wave);
            string[] barks = (PastConfig.TechBarks ?? string.Empty).Split('|');
            foreach (AIActor a in crew)
            {
                if (a == null || a.healthHaver == null) continue;
                AIActor fallen = a;
                a.healthHaver.OnPreDeath += delegate (Vector2 direction)
                {
                    if (ending || barks.Length == 0 || UnityEngine.Random.value > 0.45f) return;
                    foreach (AIActor mate in crew)
                        if (mate != null && mate != fallen && mate.healthHaver != null && !mate.healthHaver.IsDead && mate.EnemyGuid == VetTech.GUID)
                        {
                            Bubble(mate.transform, barks[UnityEngine.Random.Range(0, barks.Length)].Trim(), 1.8f);
                            break;
                        }
                };
            }
            foreach (AIActor a in crew)
                if (a != null && a.EnemyGuid == VetTech.GUID)
                {
                    Bubble(a.transform, PastConfig.TechBarkStart, 2f);
                    break;
                }
        }

        private IEnumerator ThoughtLater(PlayerController player, string text, float seconds, float delay)
        {
            yield return new WaitForSeconds(delay);
            if (player != null && !ending) PastTalk.Bubble(this, player.transform, text, seconds, true);
        }

        /// <summary>Rex and Grandma Cat react when the ward door slides open (a bubble each, a beat apart).</summary>
        private void ReactToDoor()
        {
            ClinicNpc rex = ClinicNpc.Find("rex"), grandma = ClinicNpc.Find("grandma");
            if (rex != null) Bubble(rex.transform, PastConfig.DoorRex, 2.2f);
            if (grandma != null) StartCoroutine(BubbleLater(grandma.transform, PastConfig.DoorGrandma, 2.2f, 1.2f));
        }

        private IEnumerator BubbleLater(Transform who, string text, float seconds, float delay)
        {
            yield return new WaitForSeconds(delay);
            Bubble(who, text, seconds);
        }

        private void HideOwners()
        {
            foreach (string who in new[] { "bogdan", "bianca" })
            {
                ClinicNpc owner = ClinicNpc.Find(who);
                if (owner != null) owner.Hide();
            }
        }

        /// <summary>A bystander's line: talk clip (or another, Bianca's wave) while the box shows; the box can be advanced with the interact key.</summary>
        private IEnumerator Line(ClinicNpc who, string text, float seconds, string clip = "talk")
        {
            if (who == null) yield break;
            who.Play(clip);
            yield return StartCoroutine(PastTalk.Say(this, who.transform, text, seconds, false, cutscene));
            who.Play(who.idleClip);
        }

        /// <summary>Pluto's inner voice: a thought bubble over him.</summary>
        private IEnumerator Think(PlayerController player, string text, float seconds)
        {
            if (player == null) yield break;
            yield return StartCoroutine(PastTalk.Say(this, player.transform, text, seconds, true, cutscene));
        }

        // The waiting room's loose critters: vanilla chick, rabbit and squirrel, harmless, left to wander.
        private static readonly string[] CRITTERS = { "chick", "rabbit", "squirrel" };

        private void SpawnCritters()
        {
            for (int i = 0; i < CRITTERS.Length && i < ClinicLayout.CritterSpots.Length; i++)
            {
                try
                {
                    AIActor prefab = ResolveEnemy(CRITTERS[i]);
                    if (prefab == null) continue;
                    Vector2 cell = ClinicLayout.CritterSpots[i];
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
                foreach (Vector2 spot in ClinicLayout.HeartSpots)
                    LootEngine.SpawnItem(heart.gameObject, World(spot), Vector2.zero, 0f, true, false, false);
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
            List<AIActor> adds = SpawnWave("reinforcements", PastConfig.Reinforce2, ClinicLayout.TheatreSpawns);
            foreach (AIActor a in adds)
            {
                if (a == null) continue;
                bool nurse = a.EnemyGuid == Nurse.GUID;
                Bubble(a.transform, nurse ? PastConfig.Fight2 : PastConfig.Fight3, 2f);
                if (nurse && vet != null && !ending) StartCoroutine(BubbleLater(vet.transform, PastConfig.Fight5, 2f, 2.2f));
                break;   // one arrival line is enough
            }
            foreach (AIActor a in adds)
            {
                if (a == null || a.EnemyGuid != Nurse.GUID || a.healthHaver == null) continue;
                AIActor nurseActor = a;
                StartCoroutine(NurseBarks(nurseActor));
                nurseActor.healthHaver.OnPreDeath += delegate (Vector2 direction)
                {
                    if (vet != null && !ending && vet.healthHaver != null && !vet.healthHaver.IsDead) Bubble(vet.transform, PastConfig.NurseDown, 2.6f);
                };
            }
            WatchBarks(adds);
            if (adds.Count > 0) StartCoroutine(Heartbeat("reinforcements", adds));
        }

        private IEnumerator NurseBarks(AIActor nurse)
        {
            string[] barks = (PastConfig.NurseBarks ?? string.Empty).Split('|');
            int i = 0;
            while (!ending && barks.Length > 0 && nurse != null && nurse.healthHaver != null && !nurse.healthHaver.IsDead)
            {
                yield return new WaitForSeconds(UnityEngine.Random.Range(7f, 10f));
                if (!ending && nurse != null && nurse.healthHaver != null && !nurse.healthHaver.IsDead) Bubble(nurse.transform, barks[i++ % barks.Length].Trim(), 1.8f);
            }
        }

        /// <summary>A phase-change line from the Vet (VetReinforcements calls it at 60 % health).</summary>
        public void PhaseLine(string text)
        {
            if (vet != null && !ending) Bubble(vet.transform, text, 2.2f);
        }

        /// <summary>The Vet's last-fifth line (VetReinforcements calls it once).</summary>
        public void LastFifth()
        {
            if (vet != null && !ending) Bubble(vet.transform, PastConfig.Fight4, 2.5f);
            if (ending || !PastConfig.BossReinforcements || string.IsNullOrEmpty(PastConfig.Reinforce3)) return;
            List<AIActor> adds = SpawnWave("last reinforcements", PastConfig.Reinforce3, ClinicLayout.TheatreSpawns);
            if (adds.Count > 0)
            {
                StartCoroutine(Heartbeat("last reinforcements", adds));
                WatchBarks(adds);
            }
        }

        // ------------------------------------------------------------------ waves

        // Console names the config accepts without a GUID (vanilla enemies used by the v2 design).
        // Every GUID below was checked against the prefab's EnemyGuid in the game data and the ETGMod id map (0.11). The
        // 0.10 "rat" (6ad1cafc...) was the harmless Candle Rat: 5 HP, no brain, shown as "Your own slow reflexes".
        private static readonly Dictionary<string, string> ENEMY_GUIDS = new Dictionary<string, string>
        {
            { "vet_tech", VetTech.GUID },
            { "syringe_tech", SyringeTech.GUID },
            { "nurse", Nurse.GUID },
            { "bullet_kin", "01972dee89fc4404a5c408d50007dad5" },
            { "veteran_bullet_kin", "70216cae6c1346309d86d4a0b4603045" },
            { "mutant_bullet_kin", "d4a9836f8ab14f3fadd0f597438b1f1f" },
            { "mutant_shotgun_kin", "7f665bd7151347e298e4d366f8818284" },
            { "red_shotgun_kin", "128db2f0781141bcb505d8f00f9e4d47" },
            { "blue_shotgun_kin", "b54d89f9e802455cbb2b8a96a31e8259" },
            { "shroomer", "e5cffcfabfae489da61062ea20539887" },
            { "fungun", "f905765488874846b7ff257ff81d6d0c" },
            { "poisbulon", "e61cab252cfb435db9172adc96ded75f" },
            { "shotgrub", "044a9f39712f456597b9762893fbc19c" },
            { "creech", "37340393f97f41b2822bc02d14654172" },
            { "misfire_beast", "45192ff6d6cb43ed8f1a874ab6bef316" },
            { "parrot", "ed37fa13e0fa4fcf8239643957c51293" },
            // harmless ambient critters: the waiting room only, never a wave
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
            WatchBarks(alive);
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
                if (prefab.IsHarmlessEnemy) PastPlugin.Log(label + ": warning: '" + token.Trim() + "' is a harmless critter and will not fight (check the config)");
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

        /// <summary>Everything a spawned actor needs to actually fight in a room the player is already inside.
        /// Root cause of the 0.8.0 "staff do nothing": AIActor.State is not carried onto a clone, so every spawned
        /// actor is born Inactive, and BehaviorSpeculator.Update returns before ticking a brain until the actor
        /// has been awoken (State neither Inactive nor Awakening). Vanilla wakes actors through the room's
        /// ObjectVisibilityManager (the only consumer of AIActor.Spawn's autoEngage), which EnemyBuilder strips
        /// from its template; the Vet only worked because GenericIntroDoer.EndSequence sets State = Normal.
        /// HasBeenEngaged = true runs OnEngaged (State Normal, speculator on), the way BecomeHostile does for the
        /// Convict's soldiers. Each step is its own try/catch so one throw cannot leave an actor half-awake.</summary>
        public static void Engage(AIActor a)
        {
            if (a == null) return;
            try { a.HasBeenEngaged = true; } catch (Exception e) { PastPlugin.Log("engage: HasBeenEngaged threw for " + a.name + ": " + e); }
            try { if (a.State != AIActor.ActorState.Normal) a.State = AIActor.ActorState.Normal; } catch (Exception e) { PastPlugin.Log("engage: State threw for " + a.name + ": " + e.Message); }
            try { a.HasDonePlayerEnterCheck = true; } catch (Exception) { }   // no 8-unit teleport if the room's Entered event fires later
            try { a.enabled = true; } catch (Exception) { }
            try
            {
                // Just switch it on: Unity runs a component's Start on its first enable, which initialises every
                // behaviour. RefreshBehaviors (0.10.0) threw for a speculator disabled before its Start: it initialises
                // the behaviours with m_aiActor, which only Start sets, so each one started with a null actor.
                if (a.behaviorSpeculator != null && !a.behaviorSpeculator.enabled) a.behaviorSpeculator.enabled = true;
            }
            catch (Exception e) { PastPlugin.Log("engage: speculator threw for " + a.name + ": " + e.Message); }
            try { if (a.healthHaver != null) { a.healthHaver.PreventAllDamage = false; a.healthHaver.IsVulnerable = true; } } catch (Exception) { }
            try { if (a.specRigidbody != null) a.specRigidbody.enabled = true; } catch (Exception) { }
        }

        /// <summary>One line per actor that says why it does or does not fight: the speculator gate (enabled, awoken,
        /// dead), the target, the path (is its own cell passable, can it path to Pluto), the lists on the clone.</summary>
        private string Describe(AIActor a, PlayerController target)
        {
            BehaviorSpeculator bs = a.behaviorSpeculator;
            string path = "n/a";
            try
            {
                bool passable = Pathfinding.Pathfinder.Instance != null && Pathfinding.Pathfinder.Instance.IsPassable(a.PathTile, a.Clearance, a.PathableTiles);
                bool pathed = target != null && a.PathfindToPosition(target.CenterPosition);
                path = "passable " + passable + ", pathed " + pathed + ", complete " + a.PathComplete;
            }
            catch (Exception e) { path = "path threw: " + e.Message; }
            return a.GetActorName() + " @" + (a.specRigidbody != null ? a.specRigidbody.UnitCenter - origin : (Vector2)a.transform.position - origin)
                + ": state " + a.State + ", awoken " + a.HasBeenAwoken + ", enabled " + a.enabled
                + ", brain " + (bs != null && bs.enabled) + ", engaged " + a.HasBeenEngaged + ", gone " + a.IsGone
                + ", room " + (a.ParentRoom == room) + ", target " + (a.TargetRigidbody != null) + ", dist " + (a.TargetRigidbody != null ? a.DistanceToTarget.ToString("0.0") : "-")
                + ", " + path + ", speed " + a.MovementSpeed + ", vel " + (a.specRigidbody != null ? a.specRigidbody.Velocity.magnitude.ToString("0.0") : "-")
                + ", lists " + (bs != null && bs.TargetBehaviors != null ? bs.TargetBehaviors.Count : -1) + "/" + (bs != null && bs.MovementBehaviors != null ? bs.MovementBehaviors.Count : -1) + "/" + (bs != null && bs.AttackBehaviors != null ? bs.AttackBehaviors.Count : -1)
                + ", hp " + (a.healthHaver != null ? a.healthHaver.GetCurrentHealth() + "/" + a.healthHaver.GetMaxHealth() + " vuln " + a.healthHaver.IsVulnerable + " prevent " + a.healthHaver.PreventAllDamage : "-")
                + ", tell " + (a.aiAnimator != null && a.aiAnimator.IsPlaying("tell")) + ", fire " + (a.aiAnimator != null && a.aiAnimator.IsPlaying("fire"))
                + ", bank " + VetBoss.BankState(a);
        }

        /// <summary>Logs each wave actor at 0.2 s, 2 s and 6 s and re-engages or re-targets anyone still idle.
        /// Reading the line: state Inactive or awoken false = never engaged; target true but passable/pathed false =
        /// a bad spawn cell (the Tech still fires within 20 tiles); everything true and vel 0 = look for an exception.</summary>
        private IEnumerator Heartbeat(string label, List<AIActor> actors)
        {
            foreach (float delay in new[] { 0.2f, 1.8f, 4f })
            {
                yield return new WaitForSeconds(delay);
                PlayerController target = GameManager.Instance.PrimaryPlayer;
                foreach (AIActor a in actors)
                {
                    if (a == null || a.healthHaver == null || a.healthHaver.IsDead) continue;
                    try { PastPlugin.Log(label + " " + Describe(a, target)); } catch (Exception e) { PastPlugin.Log(label + " " + a.name + ": describe threw: " + e.Message); }
                    if (!a.HasBeenAwoken || (a.behaviorSpeculator != null && !a.behaviorSpeculator.enabled))
                    {
                        PastPlugin.Log(label + " " + a.GetActorName() + ": not awake after " + delay + " s, engaging again");
                        Engage(a);
                    }
                    if (delay > 1f && a.TargetRigidbody == null && target != null && target.specRigidbody != null)
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
            PastTalk.Bubble(this, who, text, seconds, false);
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
                    SelfEngage self = greeter.GetComponent<SelfEngage>();
                    if (self != null) self.hold = true;   // he talks first; Engage(greeter) after the lines is the tell
                    greeter.IgnoreForRoomClear = true;
                    greeter.healthHaver.PreventAllDamage = true;
                }
            }
            catch (Exception e) { PastPlugin.Log("greeter: " + e.Message); }
            if (greeter == null) yield break;
            BeginCutscene("ward greeting", World(ClinicLayout.GreeterSpot) + new Vector2(0f, -1.5f));
            try
            {
                yield return new WaitForSeconds(0.6f);
                yield return StartCoroutine(Say(greeter.transform, PastConfig.Ward1, 2.4f));
                yield return StartCoroutine(Say(greeter.transform, PastConfig.Ward2, 2.6f));
                yield return StartCoroutine(Say(player.transform, PastConfig.Ward3, 1.4f));
                yield return StartCoroutine(PastTalk.PanTo(player.CenterPosition, 0.35f));
            }
            finally
            {
                EndCutscene("ward greeting", player);
            }
            Engage(greeter);
            wave1Extra = greeter;
            StartCoroutine(Heartbeat("greeter", new List<AIActor> { greeter }));
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

        /// <summary>True while one of our own cutscenes holds the "past" input override; the watchdog leaves input alone then.</summary>
        private bool cutscene;

        /// <summary>Everything that decides "is there a gun, can it be seen, can it fire" (PlayerController.HandleGunFiringInternal
        /// needs AcceptingNonMotionInput, CurrentGun != null and !IsGunLocked; the boss intro and the time tube set PreventPausing).</summary>
        private static string Snapshot(PlayerController p)
        {
            Gun g = p.CurrentGun;
            GameManager gm = GameManager.Instance;
            return "guns " + (p.inventory.AllGuns != null ? p.inventory.AllGuns.Count : -1)
                + ", current " + (g != null ? g.name + " active=" + g.gameObject.activeSelf + " renderer=" + (g.sprite != null && g.sprite.renderer != null ? g.sprite.renderer.enabled.ToString() : "?") + " ammo=" + g.CurrentAmmo : "none")
                + ", startingGunIds " + (p.startingGunIds != null ? p.startingGunIds.Count : -1)
                + ", finalFightGunIds " + (p.finalFightGunIds != null ? p.finalFightGunIds.Count : -1)
                + ", usingAlt " + p.UsingAlternateStartingGuns + ", randomGuns " + p.CharacterUsesRandomGuns
                + ", forceNoGun " + p.inventory.ForceNoGun + ", gunLocked " + p.inventory.GunLocked.Value + ", isGunLocked " + p.IsGunLocked
                + ", input " + p.CurrentInputState + ", nonMotion " + p.AcceptingNonMotionInput + ", overridden " + p.IsInputOverridden
                + ", preventPausing " + gm.PreventPausing + ", bossIntro " + GameManager.IsBossIntro
                + ", levelState " + gm.CurrentLevelOverrideState
                + ", endTimes " + (gm.Dungeon != null && gm.Dungeon.IsEndTimes) + ", strip " + (gm.Dungeon != null && gm.Dungeon.StripPlayerOnArrival)
                + ", isFoyer " + gm.IsFoyer + ", loading " + gm.IsLoadingLevel + ", visible " + p.IsVisible + ", timeScale " + Time.timeScale;
        }

        // How many consecutive watchdog ticks the gun has been hidden / the input overridden, per player (0 primary, 1 co-op).
        private readonly int[] hiddenTicks = new int[2], overriddenTicks = new int[2];

        /// <summary>Make sure Pluto is armed and can fire, and log exactly what had to be repaired.
        /// The Ark's ResetPlayers hands the starting guns back and clears input before the past loads; the console
        /// start (`vet_visit`) comes straight from the Breach and skips Foyer.OnDepartedFoyer, which leaves IsFoyer set
        /// (input FoyerInputOnly, no firing), ForceNoGun on and the gun object switched off.
        /// full = one of our own moments (arrival, the end of a cutscene, the console): repair everything now.
        /// Otherwise (the 3 s watchdog) presence, the Breach state and a switched-off gun object are repaired at once,
        /// but a hidden gun or an input override only after it persisted for two ticks outside stealth, rolls,
        /// cutscenes and the boss intro, so the watchdog never fights a legitimate short state (the cardboard box,
        /// a dodge roll, a pit, an item).</summary>
        private void EnsureLoadout(PlayerController p, string when, bool full)
        {
            if (p == null || p.inventory == null || p.healthHaver == null || p.healthHaver.IsDead) return;
            try
            {
                string before = Snapshot(p);
                List<string> did = new List<string>();
                int k = p == GameManager.Instance.SecondaryPlayer ? 1 : 0;
                // 1. guns present
                if (p.inventory.AllGuns == null || p.inventory.AllGuns.Count == 0)
                {
                    if (p.startingGunIds != null && p.startingGunIds.Count > 0)
                    {
                        try { p.ReinitializeGuns(); did.Add("ReinitializeGuns"); } catch (Exception e) { PastPlugin.Log("ReinitializeGuns failed: " + e.Message); }
                    }
                    if (p.inventory.AllGuns == null || p.inventory.AllGuns.Count == 0)
                    {
                        foreach (string id in STARTING_GUNS) GiveGun(p, id);
                        did.Add("gave the starting gun");
                    }
                }
                if (full) foreach (string id in STARTING_ITEMS) Give(p, id);
                // 2. the Breach state, replayed the way Foyer.OnDepartedFoyer does it
                if (GameManager.Instance.IsFoyer)
                {
                    GameManager.Instance.IsFoyer = false;
                    try { p.ClearOverrideShader(); } catch (Exception e) { PastPlugin.Log("ClearOverrideShader: " + e.Message); }
                    did.Add("left the Breach state (IsFoyer)");
                }
                if (p.inventory.ForceNoGun)
                {
                    p.inventory.ForceNoGun = false;
                    did.Add("ForceNoGun off");
                }
                // 3. a current gun, and its object switched on (clearing ForceNoGun does not switch it back on)
                bool noCurrent = p.CurrentGun == null && p.inventory.AllGuns != null && p.inventory.AllGuns.Count > 0;
                if (noCurrent || full)
                {
                    if (p.inventory.GunLocked.Value || p.IsGunLocked) did.Add("gun lock cleared");
                    p.inventory.GunLocked.ClearOverrides();
                    p.IsGunLocked = false;
                }
                if (noCurrent)
                {
                    p.inventory.ChangeGun(0, true, true);
                    did.Add("selected a gun");
                }
                Gun current = p.CurrentGun;
                if (current != null && !current.gameObject.activeSelf)
                {
                    current.gameObject.SetActive(true);
                    try { p.ProcessHandAttachment(); } catch (Exception e) { PastPlugin.Log("ProcessHandAttachment: " + e.Message); }
                    did.Add("gun object switched on");
                }
                // 4. renderers (only the empty reason clears every hide key)
                bool calm = !cutscene && !GameManager.IsBossIntro && !p.IsDodgeRolling && !p.IsStealthed && p.IsVisible;
                bool hidden = current != null && current.sprite != null && current.sprite.renderer != null && !current.sprite.renderer.enabled;
                if (full)
                {
                    if (hidden) did.Add("gun renderer shown");
                    p.IsVisible = true;
                    p.ToggleGunRenderers(true, string.Empty);
                    p.ToggleHandRenderers(true, string.Empty);
                    hiddenTicks[k] = 0;
                }
                else
                {
                    hiddenTicks[k] = hidden && calm ? hiddenTicks[k] + 1 : 0;
                    if (hiddenTicks[k] >= 2)
                    {
                        p.ToggleGunRenderers(true, string.Empty);
                        p.ToggleHandRenderers(true, string.Empty);
                        did.Add("gun hidden for two ticks with no reason in sight, shown");
                        hiddenTicks[k] = 0;
                    }
                }
                // 5. input, never inside our own cutscene or the boss intro
                if (!cutscene && !GameManager.IsBossIntro)
                {
                    bool overridden = p.IsInputOverridden || GameManager.Instance.PreventPausing;
                    overriddenTicks[k] = overridden ? overriddenTicks[k] + 1 : 0;
                    if (overridden && (full || overriddenTicks[k] >= 2))
                    {
                        did.Add("input was " + p.CurrentInputState + " (preventPausing " + GameManager.Instance.PreventPausing + "), cleared");
                        GameManager.Instance.PreventPausing = false;
                        p.ClearAllInputOverrides();   // what the Ark does before loading us (ArkController.ResetPlayers)
                        overriddenTicks[k] = 0;
                    }
                }
                else overriddenTicks[k] = 0;
                string after = Snapshot(p);
                if (did.Count > 0 || when == "on arrival" || when == "console")
                    PastPlugin.Log("loadout " + when + ": " + (did.Count > 0 ? string.Join("; ", did.ToArray()) : "nothing to repair")
                        + " before[" + before + "] after[" + after + "]");
            }
            catch (Exception e) { PastPlugin.Log("loadout check failed (" + when + "): " + e); }
        }

        /// <summary>Re-checks every 3 s for the whole past; logs only when something changed.</summary>
        private IEnumerator LoadoutWatchdog()
        {
            float t = 0f;
            int ticks = 0;
            while (!ending)
            {
                t += BraveTime.DeltaTime;
                if (t >= 3f)
                {
                    t = 0f;
                    ticks++;
                    PlayerController p = GameManager.Instance.PrimaryPlayer;
                    EnsureLoadout(p, "watchdog", false);
                    if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER) EnsureLoadout(GameManager.Instance.SecondaryPlayer, "watchdog", false);
                    // It logs a full snapshot only when it had to change something; this line proves it is running.
                    if (ticks % 5 == 0 && p != null)
                        PastPlugin.Log("watchdog " + (ticks * 3) + " s: gun " + (p.CurrentGun != null ? p.CurrentGun.name + " active " + p.CurrentGun.gameObject.activeSelf : "none")
                            + ", input " + p.CurrentInputState + ", nonMotion " + p.AcceptingNonMotionInput + ", isFoyer " + GameManager.Instance.IsFoyer);
                }
                yield return null;
            }
        }

        /// <summary>The game's own path: AddGunToInventory takes the prefab and instantiates it itself.</summary>
        private static void GiveGun(PlayerController p, string id)
        {
            try
            {
                if (!Game.Items.ContainsID(id)) { PastPlugin.Log("gun id not registered: " + id); return; }
                PickupObject item = Game.Items[id];
                Gun prefab = item != null ? PickupObjectDatabase.GetById(item.PickupObjectId) as Gun : null;
                if (prefab == null) { PastPlugin.Log("gun prefab null: " + id); return; }
                if (p.inventory.ContainsGun(prefab.PickupObjectId)) return;
                Gun given = p.inventory.AddGunToInventory(prefab, true);
                PastPlugin.Log("gave gun " + id + " -> " + (given != null ? given.name : "null"));
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

        /// <summary>Console: vet_loadout re-runs the loadout check by hand and prints the full snapshot.</summary>
        public void ConsoleLoadout()
        {
            EnsureLoadout(GameManager.Instance.PrimaryPlayer, "console", true);
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
                // GenericIntroDoer clears these only when its coroutine reaches the end (TriggerSequence -> EndSequence);
                // an intro cut short leaves the players frozen (BossIntro override, PreventPausing, IsBossIntro).
                try
                {
                    GameManager.IsBossIntro = false;
                    GameManager.Instance.PreventPausing = false;
                    foreach (PlayerController p in GameManager.Instance.AllPlayers)
                        if (p != null) p.ClearInputOverride("BossIntro");
                    BraveTime.ClearAllMultipliers();
                }
                catch (Exception e) { PastPlugin.Log("intro cleanup: " + e.Message); }
                Wake();
            }
        }

        private void Wake()
        {
            if (vet == null || woken) return;
            woken = true;
            VetBoss.CheckBank(vet, "the Vet");
            VetBoss.WatchFirstShot(vet);
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
            BeginCutscene("theatre dialogue", World(ClinicLayout.CameraFocus));
            try
            {
                yield return new WaitForSeconds(0.8f);
                Transform who = SpeakerTransform();
                yield return StartCoroutine(Say(who, PastConfig.Line1, 2.5f));
                yield return StartCoroutine(Say(who, PastConfig.Line2, 3.5f));
                yield return StartCoroutine(Say(player.transform, PastConfig.Line3, 1.5f));
                yield return StartCoroutine(PastTalk.PanTo(player.CenterPosition, 0.35f));
            }
            finally
            {
                EndCutscene("theatre dialogue", player);
            }
        }

        private IEnumerator Say(Transform who, string text, float seconds)
        {
            yield return StartCoroutine(PastTalk.Say(this, who, text, seconds, false, cutscene));
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
