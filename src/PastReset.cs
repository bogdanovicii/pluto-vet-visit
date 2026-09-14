using System;
using System.IO;
using HarmonyLib;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>0.14.1: console command vet_reset_past. Makes the game forget that Pluto beat his past, so the samurai costume,
    /// the kimono stand and the Breach trophy lock again: Pluto leaves the costume, KILLED_PAST and KILLED_PAST_ALTERNATE_COSTUME
    /// are cleared for his identity and saved, the progress file is deleted, the trophy is removed and a stand already shown in
    /// this Breach is hidden. Type it in the Breach.</summary>
    public static class PastReset
    {
        public static void Run()
        {
            if (!PlutoLink.Found || !GameStatsManager.HasInstance) { PastPlugin.Log("vet_reset_past: Pluto or the game stats are not loaded"); return; }
            int changed = 0;
            foreach (PlayerController p in GameManager.Instance.AllPlayers)
            {
                if (!PlutoLink.IsPluto(p) || !p.IsUsingAlternateCostume) continue;
                try { p.SwapToAlternateCostume(); changed++; PastPlugin.Log("vet_reset_past: Pluto left the samurai costume"); }
                catch (Exception e) { PastPlugin.Log("vet_reset_past: costume swap failed: " + e.Message); }
            }
            GameStatsManager.Instance.SetCharacterSpecificFlag(PlutoLink.Identity, CharacterSpecificGungeonFlags.KILLED_PAST, false);
            GameStatsManager.Instance.SetCharacterSpecificFlag(PlutoLink.Identity, CharacterSpecificGungeonFlags.KILLED_PAST_ALTERNATE_COSTUME, false);
            bool saved = false;
            try { saved = GameStatsManager.Save(); } catch (Exception e) { PastPlugin.Log("vet_reset_past: save failed: " + e.Message); }
            VetProgress.Forget();
            BreachTrophy.Remove();
            int stands = HideStands();
            PastPlugin.Log("vet_reset_past: KILLED_PAST cleared for identity " + (int)PlutoLink.Identity + ", saved " + saved
                + ", costume swaps " + changed + ", stands hidden " + stands);
            if (DebugUnlockStillOn())
                PastPlugin.Log("vet_reset_past: WARNING UnlockSamuraiCostume = true in bogdan.etg.plutothecat.cfg sets the flag again on the next launch; set it to false");
        }

        private static int HideStands()
        {
            int hidden = 0;
            foreach (CharacterCostumeSwapper sw in UnityEngine.Object.FindObjectsOfType<CharacterCostumeSwapper>())
            {
                if (sw == null || sw.TargetCharacter != PlutoLink.Identity) continue;
                AccessTools.Field(typeof(CharacterCostumeSwapper), "m_active").SetValue(sw, false);
                if (sw.CostumeSprite != null) sw.CostumeSprite.renderer.enabled = false;
                if (sw.AlternateCostumeSprite != null) sw.AlternateCostumeSprite.renderer.enabled = false;
                hidden++;
            }
            return hidden;
        }

        private static bool DebugUnlockStillOn()
        {
            try
            {
                string path = Path.Combine(BepInEx.Paths.ConfigPath, "bogdan.etg.plutothecat.cfg");
                if (!File.Exists(path)) return false;
                foreach (string line in File.ReadAllLines(path))
                {
                    string t = line.Replace(" ", string.Empty).ToLowerInvariant();
                    if (t.StartsWith("unlocksamuraicostume=")) return t.EndsWith("=true");
                }
            }
            catch (Exception) { }
            return false;
        }
    }
}
