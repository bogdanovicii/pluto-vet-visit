using System.Reflection;
using Alexandria.ItemAPI;

namespace PlutoVetVisit
{
    /// <summary>Spec A4: in his last quarter the Vet snaps on gloves and a surgical mask; idle, move, tell, fire and death use the
    /// mask_* clips (named mask_* because EnemyBuilder matches clip folders by resource-path prefix). Available only when every
    /// mask clip's first frame is embedded (approved art from reference/art).</summary>
    public static class VetMask
    {
        public static bool Available;

        public static bool ClipsPresent(Assembly asm)
        {
            foreach (string clip in CastLayout.VET_MASK_CLIPS)
                if (ResourceExtractor.GetTextureFromResource(VetBoss.ROOT + "/" + clip + "/vet_" + clip + "_001.png", asm) == null) return false;
            return true;
        }

        public static void Apply(AIActor vet)
        {
            if (!Available || vet == null || vet.aiAnimator == null) return;
            vet.aiAnimator.PlayUntilFinished("mask_on");
            vet.aiAnimator.OverrideIdleAnimation = "mask_idle";
            vet.aiAnimator.OverrideMoveAnimation = "mask_move";
            if (vet.healthHaver != null) vet.healthHaver.overrideDeathAnimation = "mask_die";
            PastPlugin.Log("the Vet puts on the mask");
        }
    }
}
