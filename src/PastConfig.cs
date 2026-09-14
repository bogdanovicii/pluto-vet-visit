using System.Collections.Generic;
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
        public static string Wave1 = "vet_tech,vet_tech,syringe_tech";
        public static string Wave2 = "mutant_shotgun_kin,mutant_bullet_kin,shroomer,poisbulon,creech,syringe_tech";
        public static float WaveTimeoutSeconds = 90f;
        public static float DebugEndAfterSeconds = 0f;
        public static float TechHealth = 20f;
        public static float NurseHealth = 160f;
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
        public static string Intro7 = "Be good, Pluto. We'll be right back.";
        public static string IntroBianca = "He's a good boy. Mostly.";
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
        public static string FightPhase2 = "Hold STILL.";
        public static string NurseBarks = "Open wide!|Bad kitty!|Hold him, doctor!";
        public static string NurseDown = "NURSE! ...Fine. I'll do it myself.";
        public static string IntroRex2 = "Psst. New guy. You know what a procedure is?";
        public static string IntroThink1 = "Food?";
        public static string IntroGrandma2 = "Oh, kitten.";
        public static string IntroThink2 = "Traitor.";
        public static string WaitingChatter = "receptionist:Please hold.|rex:I can hear the clippers.|grandma:Zzz...|receptionist:The doctor is ready for you, Pluto.|rex:Is it hot in here? It's hot in here.|grandma:Nine lives. Spend them wisely.";
        public static string TechBarkStart = "He's loose! Get him!";
        public static string TechBarks = "Man down!|Watch the claws!|Where's the net?|He bit me!|Corner him!";
        public static string WardThink = "Not if I see him first.";
        public static string DoorRex = "Don't go in there!";
        public static string DoorGrandma = "Chin up, kitten.";
        public static bool FloorTiles = true;
        public static bool WallFaces = true;
        public static bool ClinicSounds = true;
        public static float LampIntensity = 2.5f, LampRadius = 6f, MoodRedR = 1f, MoodRedG = 0.55f, MoodRedB = 0.55f;
        public static float TrophyX = 0f, TrophyY = 0f;
        public static bool ForceTrophy = false;
        public static string CommentTrophy = "The Vet's syringe. He won't need it.|Still sharp. Still mine.|No procedure today.";
        private static ConfigEntry<float> trophyXEntry, trophyYEntry;
        public static float AmbientR = 0.96f, AmbientG = 0.84f, AmbientB = 0.84f;
        // Balance knobs (tune without a rebuild). Speeds in tiles per second; scales multiply the values in the code.
        public static float BulletSpeedScale = 1f;
        public static float BossCooldownScale = 1f;
        public static float BossSpeed = 3f;
        public static float TechSpeed = 4.5f;
        public static float NurseSpeed = 3.2f;
        public static float TechCooldown = 2.0f;
        public static float TechRange = 9f;
        public static float TechDartCooldown = 5.5f;
        public static float SyringeTechHealth = 25f;
        public static float SyringeTechSpeed = 5f;
        public static float SyringeTechRange = 4.5f;
        public static float SyringeFanCooldown = 2.4f;
        public static float NurseSprayCooldown = 4f;
        public static float NurseIVCooldown = 5f;
        public static float BossHopCooldown = 2.6f;
        public static string Reinforce2 = "nurse,syringe_tech";
        public static string Reinforce3 = "poisbulon,fungun";
        public static float NurseFanCooldown = 2.2f;
        public static float NurseNetCooldown = 4.5f;
        // 0.12 pattern knobs: bullet speeds (tiles per second, before BulletSpeedScale), spreads (degrees) and gaps
        public static int PatternLeadIn = 8;
        public static float TechBurstSpeed = 9f;
        public static float TechDartSpeed = 12f;
        public static float SyringeFanSpeed = 8f;
        public static float SyringeFanSpread = 40f;
        public static float NurseFanSpeed = 7f;
        public static float NurseFanSpread = 60f;
        public static float NurseSpraySpeed = 9f;
        public static float NurseNetSpeed = 6f;
        public static float IVLineSpeed = 6.5f;
        public static float BoosterSpeed = 11f;
        public static float SprayBottleSpeed = 7f;
        public static float SprayBottleSpread = 84f;
        public static float PillBurstSpeed = 5.5f;
        public static float RingSpeed = 5.5f;
        public static int RingGapSlots = 3;
        public static float WallSpeed = 6f;
        public static int WallGapSlots = 3;
        public static float SpiralSpeed = 5.5f;
        public static float SnipSpeed = 12f;
        public static float ScalpelSpeed = 6f;
        public static float ScalpelGapDegrees = 60f;
        public static float StitchSpeed = 9f;
        public static string CommentBogdan = "Don't look at me like that. It's for your own good.|We'll get you a treat after.|It was Bianca's idea.";
        public static string CommentBianca = "Who's a brave boy?|We'll be right back, I promise.|Bogdan, he's giving me the look again.";
        public static string CommentReceptionist = "The doctor will see you now.|Please fill in the form. With your paw.|No, you cannot have a treat.";
        public static string CommentRex = "Don't let them take you in the back.|I went in a dog. I came out a dog. A quieter dog.|Is that a cone? Tell me that's not a cone.";
        public static string CommentGrandma = "Hmph. In my day we bit them.|Nine lives, kitten. I'm on my twelfth.|Zzz...";

        // What Pluto thinks when he examines a prop; defaults come from the generated ClinicLayout (tools/clinic_objects.py).
        private static readonly Dictionary<string, string> propComments = new Dictionary<string, string>();

        public static void SaveTrophyPosition(UnityEngine.Vector2 at)
        {
            TrophyX = at.x;
            TrophyY = at.y;
            if (trophyXEntry != null) trophyXEntry.Value = at.x;
            if (trophyYEntry != null) trophyYEntry.Value = at.y;
        }

        public static string PropComment(string propName)
        {
            if (propName == BreachTrophy.OBJECT) return CommentTrophy;
            string text;
            return propName != null && propComments.TryGetValue(propName, out text) ? text : string.Empty;
        }

        public static string Comment(string who)
        {
            switch (who)
            {
                case "bogdan": return CommentBogdan;
                case "bianca": return CommentBianca;
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
            Wave1 = cfg.Bind("Waves", "Wave1", Wave1, "Ward wave 1: comma-separated enemy names or GUIDs. Names: vet_tech, syringe_tech, nurse, bullet_kin, veteran_bullet_kin, mutant_bullet_kin, mutant_shotgun_kin, red_shotgun_kin, blue_shotgun_kin, shroomer, fungun, poisbulon, shotgrub, creech, misfire_beast, parrot. Spawned by the kennel banks.").Value;
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
            Intro2 = cfg.Bind("Story", "Intro2", Intro2, "Bogdan's answer at the desk (he brought Pluto in).").Value;
            IntroBianca = cfg.Bind("Story", "IntroBianca", IntroBianca, "Bianca, right after Bogdan checks Pluto in.").Value;
            Intro3 = cfg.Bind("Story", "Intro3", Intro3, "Receptionist.").Value;
            Intro4 = cfg.Bind("Story", "Intro4", Intro4, "Rex, on his chair.").Value;
            Intro5 = cfg.Bind("Story", "Intro5", Intro5, "Grandma Cat.").Value;
            Intro6 = cfg.Bind("Story", "Intro6", Intro6, "The intercom.").Value;
            Intro7 = cfg.Bind("Story", "Intro7", Intro7, "Bianca, waving goodbye to Pluto before she and Bogdan leave.").Value;
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
            FightPhase2 = cfg.Bind("Story", "FightPhase2", FightPhase2, "The Vet at 60 % health (phase two).").Value;
            NurseBarks = cfg.Bind("Story", "NurseBarks", NurseBarks, "The Nurse's shouts during the fight, every 7-10 s (separate lines with |).").Value;
            NurseDown = cfg.Bind("Story", "NurseDown", NurseDown, "The Vet when the Nurse falls.").Value;
            IntroRex2 = cfg.Bind("Story", "IntroRex2", IntroRex2, "Rex's second line in the intro.").Value;
            IntroThink1 = cfg.Bind("Story", "IntroThink1", IntroThink1, "Pluto's thought after Rex's question.").Value;
            IntroGrandma2 = cfg.Bind("Story", "IntroGrandma2", IntroGrandma2, "Grandma Cat's answer to Pluto's thought.").Value;
            IntroThink2 = cfg.Bind("Story", "IntroThink2", IntroThink2, "Pluto's thought as Bogdan and Bianca walk out.").Value;
            WaitingChatter = cfg.Bind("Story", "WaitingChatter", WaitingChatter, "Bystander chatter while Pluto is in the waiting room: who:line|who:line (who = receptionist, rex, grandma).").Value;
            TechBarkStart = cfg.Bind("Story", "TechBarkStart", TechBarkStart, "A Vet Tech when a ward wave or the reinforcements start.").Value;
            TechBarks = cfg.Bind("Story", "TechBarks", TechBarks, "What a surviving Tech sometimes shouts when a crewmate falls (separate lines with |).").Value;
            WardThink = cfg.Bind("Story", "WardThink", WardThink, "Pluto's thought after the intercom calls him to the doctor.").Value;
            foreach (ObjectSpec spec in ClinicLayout.OBJECTS)
                if (!string.IsNullOrEmpty(spec.Comment))
                    propComments[spec.Name] = cfg.Bind("Props", "Comment_" + spec.Name.Replace("pluto_", string.Empty), spec.Comment,
                        "What Pluto thinks when he examines this prop (empty = not examinable).").Value;
            trophyXEntry = cfg.Bind("Breach", "TrophyX", TrophyX, "Breach trophy position (world x). 0,0 = not set: stand where it should go and type vet_trophy_here.");
            trophyYEntry = cfg.Bind("Breach", "TrophyY", TrophyY, "Breach trophy position (world y).");
            TrophyX = trophyXEntry.Value;
            TrophyY = trophyYEntry.Value;
            ForceTrophy = cfg.Bind("Debug", "ForceTrophy", ForceTrophy, "Show the Breach trophy without beating the past (testing).").Value;
            CommentTrophy = cfg.Bind("Breach", "CommentTrophy", CommentTrophy, "What Pluto thinks when he examines the trophy (one per interaction; separate lines with |).").Value;
            LampIntensity = cfg.Bind("Mood", "LampIntensity", LampIntensity, "Operating lamp light intensity when the fight starts.").Value;
            LampRadius = cfg.Bind("Mood", "LampRadius", LampRadius, "Operating lamp light radius in tiles.").Value;
            MoodRedR = cfg.Bind("Mood", "MoodRedR", MoodRedR, "Theatre ambient in the Vet's last phase (red).").Value;
            MoodRedG = cfg.Bind("Mood", "MoodRedG", MoodRedG, "Theatre ambient in the Vet's last phase (green).").Value;
            MoodRedB = cfg.Bind("Mood", "MoodRedB", MoodRedB, "Theatre ambient in the Vet's last phase (blue).").Value;
            ClinicSounds = cfg.Bind("Mood", "ClinicSounds", ClinicSounds, "Play the clinic's built-in sound events (kennel barks, intercom chime, heart monitor, lamp, tray crash, ending).").Value;
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
            TechRange = cfg.Bind("Balance", "TechRange", TechRange, "How close a Vet Tech comes before it strafes (tiles; Bullet Kin 7, Veteran Kin 11).").Value;
            TechDartCooldown = cfg.Bind("Balance", "TechDartCooldown", TechDartCooldown, "Seconds between a Vet Tech's dart-rifle shots.").Value;
            SyringeTechHealth = cfg.Bind("Balance", "SyringeTechHealth", SyringeTechHealth, "A Syringe Tech's health.").Value;
            SyringeTechSpeed = cfg.Bind("Balance", "SyringeTechSpeed", SyringeTechSpeed, "A Syringe Tech's walking speed.").Value;
            SyringeTechRange = cfg.Bind("Balance", "SyringeTechRange", SyringeTechRange, "How close a Syringe Tech comes before it circles (tiles).").Value;
            SyringeFanCooldown = cfg.Bind("Balance", "SyringeFanCooldown", SyringeFanCooldown, "Seconds between the syringe-shotgun fans (Red Shotgun Kin 3.5).").Value;
            NurseSprayCooldown = cfg.Bind("Balance", "NurseSprayCooldown", NurseSprayCooldown, "Seconds between the Nurse's tranquilizer sprays.").Value;
            NurseIVCooldown = cfg.Bind("Balance", "NurseIVCooldown", NurseIVCooldown, "Seconds between the Nurse's IV lines (below half health).").Value;
            PatternLeadIn = cfg.Bind("Patterns", "PatternLeadIn", PatternLeadIn, "Frames (60 = 1 s) a dense pattern (ring, wall, spiral, close fan, tranquilizer hose) waits after its tell, so nothing starts point-blank.").Value;
            TechBurstSpeed = cfg.Bind("Patterns", "TechBurstSpeed", TechBurstSpeed, "Vet Tech three-round syringe burst speed (Hegemony soldier 8).").Value;
            TechDartSpeed = cfg.Bind("Patterns", "TechDartSpeed", TechDartSpeed, "Vet Tech dart rifle speed (two darts: one leading, one direct).").Value;
            SyringeFanSpeed = cfg.Bind("Patterns", "SyringeFanSpeed", SyringeFanSpeed, "Syringe Tech shotgun speed (the re-pump in the gaps flies at 3/4).").Value;
            SyringeFanSpread = cfg.Bind("Patterns", "SyringeFanSpread", SyringeFanSpread, "Syringe Tech shotgun spread in degrees (5 syringes).").Value;
            NurseFanSpeed = cfg.Bind("Patterns", "NurseFanSpeed", NurseFanSpeed, "The Nurse's droplet fan speed.").Value;
            NurseFanSpread = cfg.Bind("Patterns", "NurseFanSpread", NurseFanSpread, "The Nurse's droplet fan spread in degrees (6 droplets, then 5 in the gaps).").Value;
            NurseSpraySpeed = cfg.Bind("Patterns", "NurseSpraySpeed", NurseSpraySpeed, "The Nurse's tranquilizer hose speed (12 bubbles sweeping 80 degrees).").Value;
            NurseNetSpeed = cfg.Bind("Patterns", "NurseNetSpeed", NurseNetSpeed, "The Nurse's net throw speed (it slows to a drifting zone).").Value;
            IVLineSpeed = cfg.Bind("Patterns", "IVLineSpeed", IVLineSpeed, "The Nurse's IV line speed (curling bubbles).").Value;
            BoosterSpeed = cfg.Bind("Patterns", "BoosterSpeed", BoosterSpeed, "The Vet's aimed syringe bursts (Booster Shot; the follow-ups after the scalpel ring and clouds fly at this - 1).").Value;
            SprayBottleSpeed = cfg.Bind("Patterns", "SprayBottleSpeed", SprayBottleSpeed, "The Vet's close-range spray bottle speed (second layer at 3/4).").Value;
            SprayBottleSpread = cfg.Bind("Patterns", "SprayBottleSpread", SprayBottleSpread, "The Vet's spray bottle spread in degrees (7 droplets, then 6 in the gaps).").Value;
            PillBurstSpeed = cfg.Bind("Patterns", "PillBurstSpeed", PillBurstSpeed, "Speed of the six tablets a pill bursts into.").Value;
            RingSpeed = cfg.Bind("Patterns", "RingSpeed", RingSpeed, "Cone of Shame ring speed (Snip Time's ring is this + 0.5).").Value;
            RingGapSlots = cfg.Bind("Patterns", "RingGapSlots", RingGapSlots, "Missing bullets in each Cone of Shame / Snip Time ring (the hole to stand in; 3 of 20 = 54 degrees).").Value;
            WallSpeed = cfg.Bind("Patterns", "WallSpeed", WallSpeed, "Droplet wall speed (phase-three wall is this + 1).").Value;
            WallGapSlots = cfg.Bind("Patterns", "WallGapSlots", WallGapSlots, "Missing slots in each droplet wall wave (2-6 of 15; 3 = about 28 degrees).").Value;
            SpiralSpeed = cfg.Bind("Patterns", "SpiralSpeed", SpiralSpeed, "Vaccination spiral speed (4 arms).").Value;
            SnipSpeed = cfg.Bind("Patterns", "SnipSpeed", SnipSpeed, "Phase-three Snip Time syringe speed (5 leading syringes).").Value;
            ScalpelSpeed = cfg.Bind("Patterns", "ScalpelSpeed", ScalpelSpeed, "Scalpel ring speed.").Value;
            ScalpelGapDegrees = cfg.Bind("Patterns", "ScalpelGapDegrees", ScalpelGapDegrees, "Width of the scalpel ring's hole in degrees (placed 45-90 degrees off Pluto).").Value;
            StitchSpeed = cfg.Bind("Patterns", "StitchSpeed", StitchSpeed, "Speed of a suture when it re-aims after hanging.").Value;
            BossHopCooldown = cfg.Bind("Balance", "BossHopCooldown", BossHopCooldown, "Seconds between the Vet's sidestep hops in phase two (phase one x1.35, phase three x0.7).").Value;
            Reinforce2 = cfg.Bind("Waves", "Reinforce2", Reinforce2, "Who comes in when the Vet drops to half health (same names as the waves).").Value;
            Reinforce3 = cfg.Bind("Waves", "Reinforce3", Reinforce3, "Who comes in at a quarter of his health (empty = nobody).").Value;
            CommentBogdan = cfg.Bind("Story", "CommentBogdan", CommentBogdan, "Bogdan's lines when Pluto talks to him (one per interaction; separate lines with |; he leaves in the intro, so rarely seen).").Value;
            CommentBianca = cfg.Bind("Story", "CommentBianca", CommentBianca, "Bianca's lines when Pluto talks to her (one per interaction; separate lines with |; she leaves in the intro, so rarely seen).").Value;
            CommentReceptionist = cfg.Bind("Story", "CommentReceptionist", CommentReceptionist, "Receptionist's lines when Pluto talks to her (one per interaction; separate lines with |).").Value;
            CommentRex = cfg.Bind("Story", "CommentRex", CommentRex, "Rex's lines when Pluto talks to him (one per interaction; separate lines with |).").Value;
            CommentGrandma = cfg.Bind("Story", "CommentGrandma", CommentGrandma, "Grandma Cat's lines when Pluto talks to her (one per interaction; separate lines with |).").Value;
        }
    }
}
