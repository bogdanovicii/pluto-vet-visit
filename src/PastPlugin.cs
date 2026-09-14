using System;
using System.Collections;
using BepInEx;
using HarmonyLib;
using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoVetVisit
{
    /// <summary>
    /// BepInEx entry point for Pluto's past. Loads after Pluto the Cat (BepInDependency) and only
    /// registers things once Alexandria has built Pluto. Every load step is isolated by Step().
    /// </summary>
    [BepInDependency(ETGModMainBehaviour.GUID)]
    [BepInDependency(Alexandria.Alexandria.GUID)]
    [BepInDependency(PLUTO_GUID)]
    [BepInPlugin(GUID, NAME, VERSION)]
    public class PastPlugin : BaseUnityPlugin
    {
        public const string GUID = "bogdan.etg.plutovetvisit";
        public const string NAME = "Pluto The Cat - The Vet Visit";
        public const string VERSION = "0.11.0";
        public const string PLUTO_GUID = "bogdan.etg.plutothecat";

        private Harmony harmony;

        public void Start()
        {
            PastConfig.Bind(Config);   // BepInEx/config/bogdan.etg.plutovetvisit.cfg
            if (!PastConfig.Enabled) { Log("disabled by config"); return; }
            harmony = new Harmony(GUID);
            ETGModMainBehaviour.WaitForGameManagerStart(GMStart);
        }

        public void GMStart(GameManager gameManager)
        {
            StartCoroutine(InitWhenPlutoReady());
        }

        /// <summary>Pluto's plugin registers its GameManager callback first, but wait a little anyway.</summary>
        private IEnumerator InitWhenPlutoReady()
        {
            float waited = 0f;
            while (!PlutoLink.Find() && waited < 15f)
            {
                waited += Time.unscaledDeltaTime;
                yield return null;
            }
            if (!PlutoLink.Found)
            {
                Log("Pluto the Cat not found after 15 s (is Pluto_The_Cat installed and did it build?). The Vet Visit is disabled.");
                yield break;
            }
            Log("found " + PlutoLink.Data.nameShort + " after " + waited.ToString("0.0") + " s");
            Init();
        }

        private void Init()
        {
            bool ok = true;
            ok &= Step("harmony", () => harmony.PatchAll(typeof(PastPlugin).Assembly));
            ok &= Step("objects", ClinicObjects.Init);
            ok &= Step("room", ClinicRoom.Load);
            ok &= Step("level", PastLevel.Register);
            ok &= Step("sprites", () => ETGMod.Assets.SetupSpritesFromAssembly(typeof(PastPlugin).Assembly, "PlutoVetVisit/Resources/SpriteRoot"));
            ok &= Step("boss", VetBoss.Init);
            Step("vet tech", VetTech.Init);   // the cast is optional: a failure costs the waves their Techs, not the past
            Step("nurse", Nurse.Init);
            Step("syringe tech", SyringeTech.Init);
            if (!ok) { Log("The Vet Visit is NOT attached to Pluto because a step failed (see above)."); return; }
            Step("attach", () => PlutoLink.AttachPast(PastLevel.SCENE_NAME,
                ResourceExtractor.GetTextureFromResource("PlutoVetVisit/Resources/past_win_pic.png", typeof(PastPlugin).Assembly)));
            Step("console loadout", () => ETGModConsole.Commands.AddUnit("vet_loadout", args =>
            {
                if (VetVisitController.Instance != null) VetVisitController.Instance.ConsoleLoadout();
                else Log("not in the past");
            }));
            Step("console", () => ETGModConsole.Commands.AddUnit("vet_visit", args =>
            {
                Log("loading " + PastLevel.SCENE_NAME + " from the console");
                GameManager.Instance.LoadCustomLevel(PastLevel.SCENE_NAME);
            }));
            Log("The Vet Visit is ready. Pluto's past: " + PastLevel.SCENE_NAME);
        }

        /// <summary>Runs one load step in isolation so one broken feature cannot take the rest down.</summary>
        public static bool Step(string name, Action action)
        {
            try { action(); return true; }
            catch (Exception e)
            {
                Log("step \"" + name + "\" failed: " + e);
                Debug.LogError(e);
                return false;
            }
        }

        public static void Log(string text)
        {
            ETGModConsole.Log("[VetVisit] " + text);
        }
    }
}
