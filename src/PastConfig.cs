using BepInEx.Configuration;

namespace PlutoVetVisit
{
    /// <summary>Tunables in BepInEx/config/bogdan.etg.plutovetvisit.cfg. Read once at load.</summary>
    public static class PastConfig
    {
        public static bool Enabled = true;
        public static bool GuaranteePastAccess = true;
        public static float BossHealth = 1200f;
        public static float BossDpsCap = -1f;
        public static string BossMusic = "Play_MUS_Boss_Theme_Beholster";
        public static int RoomVisualSubtype = -1;
        public static bool SkipIntro = false;
        public static float DebugEndAfterSeconds = 0f;
        public static string Line1 = "Right on time, Pluto.";
        public static string Line2 = "Just a little snip. You won't feel a thing.";
        public static string Line3 = "HSSSSSSS!";

        public static void Bind(ConfigFile cfg)
        {
            Enabled = cfg.Bind("General", "Enabled", Enabled, "Attach The Vet Visit to Pluto.").Value;
            GuaranteePastAccess = cfg.Bind("General", "GuaranteePastAccess", GuaranteePastAccess, "When Pluto takes the Bullet That Can Kill The Past from the Blacksmith, set the flag the Ark needs so his past opens (vanilla flow otherwise).").Value;
            BossHealth = cfg.Bind("Boss", "BossHealth", BossHealth, "The Vet's health.").Value;
            BossDpsCap = cfg.Bind("Boss", "BossDpsCap", BossDpsCap, "Boss damage-per-second cap for the past level (-1 = none, vanilla pasts use -1).").Value;
            BossMusic = cfg.Bind("Boss", "BossMusic", BossMusic, "Wwise event played during the fight.").Value;
            RoomVisualSubtype = cfg.Bind("Room", "RoomVisualSubtype", RoomVisualSubtype, "Override the room's visual subtype in the lab tileset (-1 = default).").Value;
            SkipIntro = cfg.Bind("Debug", "SkipIntro", SkipIntro, "Skip the dialogue before the fight.").Value;
            DebugEndAfterSeconds = cfg.Bind("Debug", "DebugEndAfterSeconds", DebugEndAfterSeconds, "If > 0, the past ends by itself after this many seconds (tests the ending without a boss).").Value;
            Line1 = cfg.Bind("Story", "Line1", Line1, "The Vet's first line.").Value;
            Line2 = cfg.Bind("Story", "Line2", Line2, "The Vet's second line.").Value;
            Line3 = cfg.Bind("Story", "Line3", Line3, "Pluto's answer.").Value;
        }
    }
}
