using System.Collections.Generic;
using HarmonyLib;
using UnityEngine;
using Dungeonator;

namespace PlutoVetVisit
{
    /// <summary>
    /// The past as a named level. GameManager.LoadCustomLevel("tt_pluto_past") (called by Alexandria's Ark hook)
    /// looks the name up in customFloors, then DungeonDatabase.GetOrLoadByName("base_pluto_past") is intercepted
    /// below and returns the Marine lab past prefab with our one-room flow. Modular and Enter the Beyond use the
    /// same three pieces (definition + GetOrLoadByName hook + LoadCustomLevel re-registration).
    /// </summary>
    public static class PastLevel
    {
        public const string SCENE_NAME = "tt_pluto_past";
        public const string PREFAB_PATH = "base_pluto_past";
        public const string TEMPLATE = "FinalScenario_Soldier"; // Primerdyne lab: white tiles, CHARACTER_PAST, FINALGEON

        public static GameLevelDefinition Definition;

        // The template prefab is a shared asset (playing the Marine past later in the session must still work),
        // so everything we change on it is saved here and restored by the postfix below.
        private static List<DungeonFlow> savedFlows;
        private static string savedShortName, savedFloorName, savedOverrideText;

        public static void Register()
        {
            Definition = new GameLevelDefinition
            {
                dungeonSceneName = SCENE_NAME,
                dungeonPrefabPath = PREFAB_PATH,
                priceMultiplier = 1f,
                secretDoorHealthMultiplier = 1f,
                enemyHealthMultiplier = 1f,
                damageCap = -1f,
                bossDpsCap = PastConfig.BossDpsCap,
                flowEntries = new List<DungeonFlowLevelEntry>(),
                predefinedSeeds = new List<int>(),
            };
            AddTo(GameManager.Instance.customFloors);
            // A fresh GameManager (after returning to the Breach) copies its lists from this prefab.
            GameObject gmPrefab = ResourceManager.LoadAssetBundle("brave_resources_001").LoadAsset<GameObject>("_GameManager");
            if (gmPrefab != null) AddTo(gmPrefab.GetComponent<GameManager>().customFloors);
            PastPlugin.Log("registered level " + SCENE_NAME + " -> " + PREFAB_PATH + " (template " + TEMPLATE + ")");
        }

        public static void AddTo(List<GameLevelDefinition> floors)
        {
            if (floors == null || Definition == null) return;
            for (int i = 0; i < floors.Count; i++)
                if (floors[i] != null && floors[i].dungeonSceneName == SCENE_NAME) return;
            floors.Add(Definition);
        }

        public static Dungeon BuildDungeon(Dungeon template)
        {
            if (savedFlows == null)
            {
                savedFlows = template.PatternSettings.flows;
                savedShortName = template.DungeonShortName;
                savedFloorName = template.DungeonFloorName;
                savedOverrideText = template.DungeonFloorLevelTextOverride;
            }
            template.PatternSettings.flows = new List<DungeonFlow> { VetFlow.Create(template) };
            template.DungeonShortName = "The Vet Visit";
            template.DungeonFloorName = "Pluto's Past";
            template.DungeonFloorLevelTextOverride = "The Vet Visit";
            template.LevelOverrideType = GameManager.LevelOverrideState.CHARACTER_PAST;
            template.BossMasteryTokenItemId = -1;
            template.PrefabsToAutoSpawn = new GameObject[0];
            PastPlugin.Log("built past dungeon from " + TEMPLATE + " (tileset " + template.tileIndices.tilesetId + ")");
            return template;
        }

        public static void RestoreTemplate(Dungeon template)
        {
            if (savedFlows == null) return;
            template.PatternSettings.flows = savedFlows;
            template.DungeonShortName = savedShortName;
            template.DungeonFloorName = savedFloorName;
            template.DungeonFloorLevelTextOverride = savedOverrideText;
            savedFlows = null;
            PastPlugin.Log("restored the " + TEMPLATE + " template");
        }
    }

    [HarmonyPatch(typeof(DungeonDatabase), nameof(DungeonDatabase.GetOrLoadByName))]
    internal static class GetOrLoadByNamePatch
    {
        static bool Prefix(string name, ref Dungeon __result)
        {
            if (name == null || name.ToLower() != PastLevel.PREFAB_PATH) return true;
            PastLevel.AddTo(GameManager.Instance.customFloors);
            // Re-enters this patch with the template name: Prefix passes, the original loads, Postfix restores.
            Dungeon template = DungeonDatabase.GetOrLoadByName(PastLevel.TEMPLATE);
            __result = PastLevel.BuildDungeon(template);
            return false;
        }

        static void Postfix(string name, Dungeon __result)
        {
            if (name != null && __result != null && name.ToLower() == PastLevel.TEMPLATE.ToLower())
                PastLevel.RestoreTemplate(__result);
        }
    }

    [HarmonyPatch(typeof(GameManager), nameof(GameManager.LoadCustomLevel))]
    internal static class LoadCustomLevelPatch
    {
        static void Prefix(string custom)
        {
            if (custom == PastLevel.SCENE_NAME) PastLevel.AddTo(GameManager.Instance.customFloors);
        }
    }
}
