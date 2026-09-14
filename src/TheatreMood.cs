using System.Collections;
using Dungeonator;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>Spec A3. The operating lamp switches on when the fight starts (an AdditionalBraveLight, which registers itself
    /// with Pixelator in Initialize, plus the lamp's floor pool sprite as the visible fallback). In the last phase the room eases
    /// to red: PlayerController moves RenderSettings.ambientLight toward the room's runtime customAmbient at 0.35 per second.</summary>
    public static class TheatreMood
    {
        private static AdditionalBraveLight lamp;

        public static void LampOn(MonoBehaviour host, Vector2 worldTable)
        {
            ClinicProp.Show("pluto_lamp_pool");
            try
            {
                GameObject go = new GameObject("VetLampLight");
                go.transform.position = worldTable + new Vector2(0f, 1.5f);
                lamp = go.AddComponent<AdditionalBraveLight>();
                lamp.LightColor = new Color(1f, 0.96f, 0.85f, 1f);
                lamp.LightRadius = PastConfig.LampRadius;
                lamp.LightIntensity = 0f;
                lamp.Initialize();
                host.StartCoroutine(Ramp(lamp, PastConfig.LampIntensity, 0.5f));
                ClinicSound.Play("Play_ENM_lighten_world_01", go);
                PastPlugin.Log("mood: lamp on");
            }
            catch (System.Exception e) { PastPlugin.Log("mood: lamp light failed (" + e.Message + "), floor pool only"); }
        }

        private static IEnumerator Ramp(AdditionalBraveLight light, float target, float seconds)
        {
            float t = 0f;
            while (light != null && t < seconds)
            {
                t += BraveTime.DeltaTime;
                light.LightIntensity = Mathf.Lerp(0f, target, t / seconds);
                yield return null;
            }
            if (light != null) light.LightIntensity = target;
        }

        public static void Red(RoomHandler room)
        {
            if (!SetAmbient(room, new Color(PastConfig.MoodRedR, PastConfig.MoodRedG, PastConfig.MoodRedB, 1f))) return;
            if (lamp != null) ClinicSound.Play("Play_ENM_darken_world_01", lamp.gameObject);
            PastPlugin.Log("mood: last phase red");
        }

        public static void Restore(RoomHandler room)
        {
            if (SetAmbient(room, new Color(PastConfig.AmbientR, PastConfig.AmbientG, PastConfig.AmbientB, 1f))) PastPlugin.Log("mood: calm again");
        }

        private static bool SetAmbient(RoomHandler room, Color c)
        {
            if (room == null || room.area == null || room.area.runtimePrototypeData == null) { PastPlugin.Log("mood: no room data"); return false; }
            room.area.runtimePrototypeData.usesCustomAmbient = true;
            room.area.runtimePrototypeData.customAmbient = c;
            room.area.runtimePrototypeData.usesDifferentCustomAmbientLowQuality = false;
            room.area.runtimePrototypeData.customAmbientLowQuality = c;
            return true;
        }
    }
}
