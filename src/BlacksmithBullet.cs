using HarmonyLib;

namespace PlutoVetVisit
{
    /// <summary>
    /// Pluto gets his past the vanilla way: the Blacksmith in the Forge (chamber 5) hands him the Bullet
    /// That Can Kill The Past, because Alexandria registers any hasPast character with her PlayMaker FSM and
    /// the mod sets hasPast on Pluto (see PlutoLink.AttachPast).
    ///
    /// The Ark only opens a past when GameStatsManager has GungeonFlags.BLACKSMITH_BULLET_COMPLETE set AND
    /// the run's player has PastAccessible (ArkController.CharacterStoryComplete). Picking the bullet up sets
    /// PastAccessible; this postfix makes sure the flag is set too when PLUTO takes the bullet, so the
    /// Blacksmith route reliably opens his past even if the FSM path for a modded identity does not set the
    /// flag itself. It fires only for Pluto, so no other character's progression changes.
    /// </summary>
    [HarmonyPatch(typeof(BulletThatCanKillThePast), nameof(BulletThatCanKillThePast.Pickup))]
    internal static class BlacksmithBulletPatch
    {
        private static void Postfix(PlayerController player)
        {
            if (!PastConfig.GuaranteePastAccess) return;
            if (!PlutoLink.IsPluto(player)) return;
            if (GameStatsManager.Instance == null) return;
            if (!GameStatsManager.Instance.GetFlag(GungeonFlags.BLACKSMITH_BULLET_COMPLETE))
            {
                GameStatsManager.Instance.SetFlag(GungeonFlags.BLACKSMITH_BULLET_COMPLETE, true);
                PastPlugin.Log("Pluto received the Bullet That Can Kill The Past; his past is now reachable at the Ark.");
            }
        }
    }
}
