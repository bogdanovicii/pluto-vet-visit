using System.Collections;
using System.Reflection;
using Alexandria.ItemAPI;
using HarmonyLib;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>Spec A6: the Vet's broken syringe on a pedestal in the Breach once the past is beaten (KILLED_PAST for Pluto and
    /// the progress file). Its spot comes from the config; stand there and type vet_trophy_here to set it.</summary>
    public static class BreachTrophy
    {
        public const string OBJECT = "pluto_breach_trophy";
        private static GameObject placed;

        public static bool Unlocked()
        {
            if (PastConfig.ForceTrophy) return true;
            return PlutoLink.Found && GameStatsManager.HasInstance
                && GameStatsManager.Instance.GetCharacterSpecificFlag(PlutoLink.Identity, CharacterSpecificGungeonFlags.KILLED_PAST)
                && VetProgress.Beaten();
        }

        public static IEnumerator PlaceLater()
        {
            yield return null;
            while (GameManager.Instance == null || GameManager.Instance.IsLoadingLevel || Dungeonator.Dungeon.IsGenerating) yield return null;
            if (PastConfig.TrophyX == 0f && PastConfig.TrophyY == 0f)
            {
                PastPlugin.Log("breach trophy: no position yet; stand where it should go and type vet_trophy_here");
                yield break;
            }
            Place(new Vector2(PastConfig.TrophyX, PastConfig.TrophyY));
        }

        public static void Place(Vector2 at)
        {
            if (!Unlocked()) { PastPlugin.Log("breach trophy: locked (beat the Vet first)"); return; }
            Assembly asm = typeof(PastPlugin).Assembly;
            string path = ClinicObjects.OBJECT_ROOT + "/breach_trophy.png";
            if (ResourceExtractor.GetTextureFromResource(path, asm) == null) { PastPlugin.Log("breach trophy: art missing (" + path + ")"); return; }
            if (placed != null) Object.Destroy(placed);
            placed = SpriteBuilder.SpriteFromResource(path, new GameObject(OBJECT), asm);
            placed.transform.position = new Vector3(at.x, at.y, at.y);
            ClinicObjects.AddCollider(placed, CollisionLayer.LowObstacle, 8, 0, 16, 8);
            tk2dSprite s = placed.GetComponent<tk2dSprite>();
            s.IsPerpendicular = true;
            s.HeightOffGround = -0.5f;
            s.UpdateZDepth();
            placed.AddComponent<ClinicExaminable>().propName = OBJECT;
            PastPlugin.Log("breach trophy placed at " + at);
        }
    }

    [HarmonyPatch(typeof(Foyer), "Awake")]
    internal static class BreachTrophyPatch
    {
        private static void Postfix(Foyer __instance)
        {
            if (__instance != null) __instance.StartCoroutine(BreachTrophy.PlaceLater());
        }
    }
}
