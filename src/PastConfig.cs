using BepInEx.Configuration;

namespace PlutoVetVisit
{
    /// <summary>Tunables in BepInEx/config/bogdan.etg.plutovetvisit.cfg. Read once at load.</summary>
    public static class PastConfig
    {
        public static bool Enabled = true;
        public static bool GuaranteePastAccess = true;
        public static float BossHealth = 800f;
        public static float BossDpsCap = -1f;
        public static string BossMusic = "Play_MUS_Boss_Theme_Beholster";
        public static int RoomVisualSubtype = -1;
        public static bool SkipIntro = false;
        public static bool SkipWaves = false;
        public static string Wave1 = "vet_tech,vet_tech,vet_tech";
        public static string Wave2 = "vet_tech,vet_tech,mutant_bullet_kin,rat,parrot";
        public static float WaveTimeoutSeconds = 90f;
        public static float DebugEndAfterSeconds = 0f;
        public static float TechHealth = 18f;
        public static float NurseHealth = 150f;
        public static bool BossReinforcements = true;
        public static string Line1 = "Right on time, Pluto.";
        public static string Line2 = "Just a little snip. You won't feel a thing.";
        public static string Line3 = "HSSSSSSS!";
        public static string Intro1 = "Name?";
        public static string Intro2 = "Pluto. Here for the... procedure.";
        public static string Intro3 = "Take a seat.";
        public static string Intro4 = "They said it wouldn't hurt.";
        public static string Intro5 = "It didn't. Not for long.";
        public static string Intro6 = "Pluto?";
        public static string Intro7 = "Be good.";
        public static string Epilogue = "Pluto was never taken to the vet again. He is still on Sterilised 37.";
        public static string Ward1 = "Pluto? The doctor is through the far door.";
        public static string Ward2 = "First, hold still. Just something to calm you down.";
        public static string Ward3 = "Hsss.";
        public static string Ward4 = "Tech to the ward. The patient is loose.";
        public static string Ward5 = "The doctor will see you now.";
        public static string Fight1 = "Nurse! Hold him down!";
        public static string Fight2 = "Coming, doctor.";
        public static string Fight3 = "Grab him!";
        public static string Fight4 = "Just... a little... snip!";
        public static string Fight5 = "About time, Nurse.";
        public static string DoorRex = "Don't go in there!";
        public static string DoorGrandma = "Chin up, kitten.";
        public static bool FloorTiles = true;
        public static bool WallFaces = true;
        public static float AmbientR = 0.96f, AmbientG = 0.84f, AmbientB = 0.84f;
        // Balance knobs (tune without a rebuild). Speeds in tiles per second; scales multiply the values in the code.
        public static float BulletSpeedScale = 1f;
        public static float BossCooldownScale = 1f;
        public static float BossSpeed = 3f;
        public static float TechSpeed = 4.5f;
        public static float NurseSpeed = 3.2f;
        public static float TechCooldown = 1.8f;
        public static float NurseFanCooldown = 2.2f;
        public static float NurseNetCooldown = 4.5f;
        public static string CommentOwner = "...";
        public static string CommentReceptionist = "The doctor will see you now.";
        public static string CommentRex = "Don't let them take you in the back.";
        public static string CommentGrandma = "Hmph. In my day we bit them.";

        public static string Comment(string who)
        {
            switch (who)
            {
                case "owner": return CommentOwner;
                case "receptionist": return CommentReceptionist;
                case "rex": return CommentRex;
                case "grandma": return CommentGrandma;
                default: return string.Empty;
            }
        }

        public static void Bind(ConfigFile cfg)
        {
            Enabled = cfg.Bind("General", "Enabled", Enabled, "Attach The Vet Visit to Pluto.").Value;
            GuaranteePastAccess = cfg.Bind("General", "GuaranteePastAccess", GuaranteePastAccess, "When Pluto takes the Bullet That Can Kill The Past from the Blacksmith, set the flag the Ark needs so his past opens (vanilla flow otherwise).").Value;
            BossHealth = cfg.Bind("Boss", "BossHealth", BossHealth, "The Vet's health.").Value;
            BossDpsCap = cfg.Bind("Boss", "BossDpsCap", BossDpsCap, "Boss damage-per-second cap for the past level (-1 = none, vanilla pasts use -1).").Value;
            BossMusic = cfg.Bind("Boss", "BossMusic", BossMusic, "Wwise event played during the fight.").Value;
            RoomVisualSubtype = cfg.Bind("Room", "RoomVisualSubtype", RoomVisualSubtype, "Override the room's visual subtype in the lab tileset (-1 = default).").Value;
            SkipIntro = cfg.Bind("Debug", "SkipIntro", SkipIntro, "Skip the dialogue before the fight.").Value;
            SkipWaves = cfg.Bind("Debug", "SkipWaves", SkipWaves, "Open the ward without spawning its two waves (tests the walk and the doors).").Value;
            Wave1 = cfg.Bind("Waves", "Wave1", Wave1, "Ward wave 1: comma-separated enemy names (vet_tech, nurse, rat, parrot, mutant_bullet_kin, bullet_kin) or GUIDs. Spawned at the side doors.").Value;
            Wave2 = cfg.Bind("Waves", "Wave2", Wave2, "Ward wave 2: same format. Spawned at the kennels.").Value;
            WaveTimeoutSeconds = cfg.Bind("Waves", "WaveTimeoutSeconds", WaveTimeoutSeconds, "If a wave is still alive after this many seconds it is put down so the past cannot get stuck.").Value;
            DebugEndAfterSeconds = cfg.Bind("Debug", "DebugEndAfterSeconds", DebugEndAfterSeconds, "If > 0, the past ends by itself after this many seconds (tests the ending without a boss).").Value;
            Line1 = cfg.Bind("Story", "Line1", Line1, "The Vet's first line.").Value;
            Line2 = cfg.Bind("Story", "Line2", Line2, "The Vet's second line.").Value;
            Line3 = cfg.Bind("Story", "Line3", Line3, "Pluto's answer.").Value;
            TechHealth = cfg.Bind("Cast", "TechHealth", TechHealth, "A Vet Tech's health.").Value;
            NurseHealth = cfg.Bind("Cast", "NurseHealth", NurseHealth, "The Nurse's health.").Value;
            BossReinforcements = cfg.Bind("Cast", "BossReinforcements", BossReinforcements, "Below half health the Vet calls the Nurse and two Techs.").Value;
            Intro1 = cfg.Bind("Story", "Intro1", Intro1, "Receptionist, at the desk.").Value;
            Intro2 = cfg.Bind("Story", "Intro2", Intro2, "The Owner's answer.").Value;
            Intro3 = cfg.Bind("Story", "Intro3", Intro3, "Receptionist.").Value;
            Intro4 = cfg.Bind("Story", "Intro4", Intro4, "Rex, on his chair.").Value;
            Intro5 = cfg.Bind("Story", "Intro5", Intro5, "Grandma Cat.").Value;
            Intro6 = cfg.Bind("Story", "Intro6", Intro6, "The intercom.").Value;
            Intro7 = cfg.Bind("Story", "Intro7", Intro7, "The Owner, opening the carrier before he leaves.").Value;
            Epilogue = cfg.Bind("Story", "Epilogue", Epilogue, "Shown after the Vet falls, before the credits.").Value;
            Ward1 = cfg.Bind("Story", "Ward1", Ward1, "The Vet Tech who greets Pluto in the ward.").Value;
            Ward2 = cfg.Bind("Story", "Ward2", Ward2, "The Tech's second line, before the wave attacks.").Value;
            Ward3 = cfg.Bind("Story", "Ward3", Ward3, "Pluto's answer in the ward.").Value;
            Ward4 = cfg.Bind("Story", "Ward4", Ward4, "The intercom when wave 1 is down.").Value;
            Ward5 = cfg.Bind("Story", "Ward5", Ward5, "The intercom when the ward is clear and the theatre opens.").Value;
            Fight1 = cfg.Bind("Story", "Fight1", Fight1, "The Vet at half health.").Value;
            Fight2 = cfg.Bind("Story", "Fight2", Fight2, "The Nurse arriving.").Value;
            Fight3 = cfg.Bind("Story", "Fight3", Fight3, "A Tech arriving (if no Nurse).").Value;
            Fight4 = cfg.Bind("Story", "Fight4", Fight4, "The Vet at a quarter of his health.").Value;
            Fight5 = cfg.Bind("Story", "Fight5", Fight5, "The Vet when the Nurse comes in.").Value;
            DoorRex = cfg.Bind("Story", "DoorRex", DoorRex, "Rex when the ward door opens.").Value;
            DoorGrandma = cfg.Bind("Story", "DoorGrandma", DoorGrandma, "Grandma Cat when the ward door opens.").Value;
            FloorTiles = cfg.Bind("Room", "FloorTiles", FloorTiles, "Lay the white clinic floor tiles over the past tileset (turn off if they draw over Pluto).").Value;
            WallFaces = cfg.Bind("Room", "WallFaces", WallFaces, "Draw the clinic's white-and-teal wall faces over the lab tileset's walls (turn off if they flicker or draw over Pluto).").Value;
            AmbientR = cfg.Bind("Room", "AmbientR", AmbientR, "Ambient light red (the lab template is 0.91/0.64/0.64; 1/1/1 is neutral).").Value;
            AmbientG = cfg.Bind("Room", "AmbientG", AmbientG, "Ambient light green.").Value;
            AmbientB = cfg.Bind("Room", "AmbientB", AmbientB, "Ambient light blue.").Value;
            BulletSpeedScale = cfg.Bind("Balance", "BulletSpeedScale", BulletSpeedScale, "Multiplies every enemy bullet speed in the past (1 = vanilla band; 0.8 easier, 1.2 harder).").Value;
            BossCooldownScale = cfg.Bind("Balance", "BossCooldownScale", BossCooldownScale, "Multiplies the Vet's attack cooldowns (1.3 = slower fight, 0.8 = faster).").Value;
            BossSpeed = cfg.Bind("Balance", "BossSpeed", BossSpeed, "The Vet's walking speed.").Value;
            TechSpeed = cfg.Bind("Balance", "TechSpeed", TechSpeed, "A Vet Tech's walking speed.").Value;
            NurseSpeed = cfg.Bind("Balance", "NurseSpeed", NurseSpeed, "The Nurse's walking speed.").Value;
            TechCooldown = cfg.Bind("Balance", "TechCooldown", TechCooldown, "Seconds between a Tech's three-round bursts (Hegemony soldiers: about 1.8).").Value;
            NurseFanCooldown = cfg.Bind("Balance", "NurseFanCooldown", NurseFanCooldown, "Seconds between the Nurse's droplet fans.").Value;
            NurseNetCooldown = cfg.Bind("Balance", "NurseNetCooldown", NurseNetCooldown, "Seconds between the Nurse's net throws.").Value;
            CommentOwner = cfg.Bind("Story", "CommentOwner", CommentOwner, "What the Owner says when Pluto talks to him (he leaves in the intro, so rarely seen).").Value;
            CommentReceptionist = cfg.Bind("Story", "CommentReceptionist", CommentReceptionist, "Receptionist's line when Pluto talks to her.").Value;
            CommentRex = cfg.Bind("Story", "CommentRex", CommentRex, "Rex's line when Pluto talks to him.").Value;
            CommentGrandma = cfg.Bind("Story", "CommentGrandma", CommentGrandma, "Grandma Cat's line when Pluto talks to her.").Value;
        }
    }
}
