using System;
using BepInEx;
using UnityEngine;

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
        public const string VERSION = "0.1.0";
        public const string PLUTO_GUID = "bogdan.etg.plutothecat";

        public void Start()
        {
            ETGModMainBehaviour.WaitForGameManagerStart(GMStart);
        }

        public void GMStart(GameManager gameManager)
        {
            Log("plugin " + VERSION + " loaded (nothing registered yet)");
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
