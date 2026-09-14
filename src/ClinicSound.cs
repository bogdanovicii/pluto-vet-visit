using System;
using System.Collections.Generic;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>Built-in game sound events for the clinic (spec A5). An unknown event is silent, so each name is logged the
    /// first time it plays; the tester reports which ones are heard. tools/sounds.py lists the allowed names.</summary>
    public static class ClinicSound
    {
        private static readonly HashSet<string> Logged = new HashSet<string>();

        public static void Play(string eventName, GameObject source)
        {
            if (!PastConfig.ClinicSounds || source == null || string.IsNullOrEmpty(eventName)) return;
            try
            {
                AkSoundEngine.PostEvent(eventName, source);
                if (Logged.Add(eventName)) PastPlugin.Log("sound " + eventName);
            }
            catch (Exception e) { PastPlugin.Log("sound " + eventName + " failed: " + e.Message); }
        }
    }
}
