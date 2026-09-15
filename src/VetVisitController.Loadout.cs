using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Dungeonator;
using Gungeon;

namespace PlutoVetVisit
{
    public partial class VetVisitController
    {
        private static readonly string[] STARTING_GUNS = { "pluto:kibble_sack" };
        private static readonly string[] STARTING_ITEMS = { "pluto:wet_food_can", "pluto:squeaky_toy", "pluto:nine_lives", "pluto:coco_blue", "pluto:puffed_up" };

        /// <summary>True while one of our own cutscenes holds the "past" input override; the watchdog leaves input alone then.</summary>
        private bool cutscene;
        private bool arrivedFromFoyer;

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

        /// <summary>Routine checks restore missing items only. Broad control repair is reserved for the explicit console command.</summary>
        private void EnsureLoadout(PlayerController p, string when, bool full, bool emergency = false)
        {
            if (ending) return;   // the ending hides Pluto in Bianca's arms; never show him again
            if (p == null || p.inventory == null || p.healthHaver == null || p.healthHaver.IsDead) return;
            try
            {
                if (full) PastPlugin.Log("loadout " + when + ": " + LoadoutChoice.Describe(p));
                string before = Snapshot(p);
                List<string> did = new List<string>();
                bool leavingFoyer = full && when == "on arrival" && arrivedFromFoyer;
                bool mayEquip = !cutscene && !GameManager.IsBossIntro && !p.IsInputOverridden
                    && !p.IsDodgeRolling && !p.IsStealthed && !p.inventory.ForceNoGun
                    && !p.inventory.GunLocked.Value && !p.IsGunLocked;
                // 1. guns present
                if (p.inventory.AllGuns == null || p.inventory.AllGuns.Count == 0)
                {
                    if (p.startingGunIds != null && p.startingGunIds.Count > 0)
                    {
                        try { p.ReinitializeGuns(); did.Add("ReinitializeGuns"); } catch (Exception e) { PastPlugin.Log("ReinitializeGuns failed: " + e.Message); }
                    }
                    if (p.inventory.AllGuns == null || p.inventory.AllGuns.Count == 0)
                    {
                        if (LoadoutChoice.UseAlternate(p))
                        {
                            foreach (int id in p.startingAlternateGunIds) GiveGunById(p, id);
                            did.Add("gave the costume's starting guns");
                        }
                        else
                        {
                            foreach (string id in STARTING_GUNS) GiveGun(p, id);
                            did.Add("gave the starting gun");
                        }
                    }
                }
                if (full) foreach (string id in STARTING_ITEMS) Give(p, id);
                // Console starts from the Breach need its specific departure state cleared once.
                if (leavingFoyer)
                {
                    GameManager.Instance.IsFoyer = false;
                    p.inventory.ForceNoGun = false;
                    p.ClearOverrideShader();
                    mayEquip = !p.IsInputOverridden && !p.inventory.GunLocked.Value && !p.IsGunLocked;
                    did.Add("left Breach state");
                }
                if (emergency)
                {
                    if (cutscene || GameManager.IsBossIntro)
                    {
                        PastPlugin.Log("emergency repair deferred until conversation/boss intro finishes");
                        return;
                    }
                    p.inventory.ForceNoGun = false;
                    p.inventory.GunLocked.ClearOverrides();
                    p.IsGunLocked = false;
                    p.IsVisible = true;
                    p.ToggleGunRenderers(true, string.Empty);
                    p.ToggleHandRenderers(true, string.Empty);
                    p.ClearAllInputOverrides();
                    GameManager.Instance.PreventPausing = false;
                    mayEquip = true;
                    did.Add("explicit emergency control repair");
                }
                if (mayEquip && p.CurrentGun == null && p.inventory.AllGuns != null && p.inventory.AllGuns.Count > 0)
                {
                    p.inventory.ChangeGun(0, true, true);
                    did.Add("selected a gun");
                }
                Gun current = p.CurrentGun;
                if (mayEquip && current != null && !current.gameObject.activeSelf)
                {
                    current.gameObject.SetActive(true);
                    p.ProcessHandAttachment();
                    did.Add("gun object switched on");
                }
                string after = Snapshot(p);
                if (did.Count > 0 || when == "on arrival" || when == "console")
                    PastPlugin.Log("loadout " + when + ": " + (did.Count > 0 ? string.Join("; ", did.ToArray()) : "nothing to repair")
                        + " before[" + before + "] after[" + after + "]");
            }
            catch (Exception e) { PastPlugin.Log("loadout check failed (" + when + "): " + e); }
        }

        private readonly StuckControlPolicy stuckControls = new StuckControlPolicy();

        /// <summary>Routine repair every tick; the broad emergency repair only after the policy sees a persistent, unexplained lock.</summary>
        private void WatchdogCheck(PlayerController p, int slot)
        {
            EnsureLoadout(p, "watchdog", false);
            if (ending || p == null || p.inventory == null || p.healthHaver == null || p.healthHaver.IsDead) { stuckControls.Observe(slot, false, true); return; }
            Gun g = p.CurrentGun;
            bool cannotFire = p.IsInputOverridden || p.inventory.ForceNoGun || p.inventory.GunLocked.Value || p.IsGunLocked
                || g == null || !g.gameObject.activeSelf || (g.sprite != null && g.sprite.renderer != null && !g.sprite.renderer.enabled);
            bool excused = cutscene || GameManager.IsBossIntro || p.IsDodgeRolling || p.IsStealthed || p.IsFalling;
            if (stuckControls.Observe(slot, cannotFire, excused))
            {
                PastPlugin.Log("watchdog: player " + (slot + 1) + " unable to fire for " + (StuckControlPolicy.TicksBeforeRepair * 3) + " s with no reason in sight; emergency repair");
                EnsureLoadout(p, "watchdog escalation", true, true);
            }
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
                    WatchdogCheck(p, 0);
                    if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER) WatchdogCheck(GameManager.Instance.SecondaryPlayer, 1);
                    // It logs a full snapshot only when it had to change something; this line proves it is running.
                    if (ticks % 5 == 0 && p != null)
                        PastPlugin.Log("watchdog " + (ticks * 3) + " s: gun " + (p.CurrentGun != null ? p.CurrentGun.name + " active " + p.CurrentGun.gameObject.activeSelf : "none")
                            + ", input " + p.CurrentInputState + ", nonMotion " + p.AcceptingNonMotionInput + ", isFoyer " + GameManager.Instance.IsFoyer);
                }
                yield return null;
            }
        }

        /// <summary>The game's own path: AddGunToInventory takes the prefab and instantiates it itself.</summary>
        private static void GiveGunById(PlayerController p, int pickupId)
        {
            try
            {
                Gun prefab = PickupObjectDatabase.GetById(pickupId) as Gun;
                if (prefab == null) { PastPlugin.Log("costume gun id " + pickupId + " is not a gun"); return; }
                if (p.inventory.ContainsGun(pickupId)) return;
                Gun given = p.inventory.AddGunToInventory(prefab, true);
                PastPlugin.Log("gave costume gun #" + pickupId + " -> " + (given != null ? given.name : "null"));
            }
            catch (Exception e) { PastPlugin.Log("could not give costume gun #" + pickupId + ": " + e.Message); }
        }

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
            foreach (PlayerController p in GameManager.Instance.AllPlayers)
                EnsureLoadout(p, "console", true, true);
        }

    }
}
