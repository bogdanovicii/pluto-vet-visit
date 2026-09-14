using System;
using System.IO;

namespace PlutoVetVisit
{
    /// <summary>Spec C2: a small file both DLLs can read without referencing each other, proof that the Vet was really beaten
    /// (Pluto the Cat forced KILLED_PAST on every load before 2.16.0).</summary>
    public static class VetProgress
    {
        public static string PathName
        {
            get { return Path.Combine(BepInEx.Paths.ConfigPath, "bogdan.etg.plutovetvisit.progress"); }
        }

        public static void MarkBeaten()
        {
            try
            {
                File.WriteAllText(PathName, "VetBeaten=true\nDate=" + DateTime.UtcNow.ToString("yyyy-MM-dd") + "\n");
                PastPlugin.Log("progress file written: " + PathName);
            }
            catch (Exception e) { PastPlugin.Log("progress file failed: " + e.Message); }
        }

        public static bool Beaten()
        {
            try { return File.Exists(PathName) && File.ReadAllText(PathName).Contains("VetBeaten=true"); }
            catch (Exception) { return false; }
        }
    }
}
