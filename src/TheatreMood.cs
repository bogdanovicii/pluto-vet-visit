using System.Collections;
using Dungeonator;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>Spec A3. The operating lamp switches on when the fight starts (an AdditionalBraveLight, which registers itself
    /// with Pixelator in Initialize, plus the lamp's floor pool sprite as the visible fallback). In the last phase the theatre fades
    /// to red.
    ///
    /// Up to 0.14.3 Red only changed the room's runtime customAmbient, which PlayerController.HandleCurrentRoomExtraData eases
    /// RenderSettings.ambientLight toward. It was called (nothing in that path changed in the combat pass), but the target was a
    /// small shift (0.96/0.84/0.84 to 1/0.55/0.55) under a 2.5-intensity white lamp that lights the whole fight: not visibly red.
    /// Now it drives Dungeon.OverrideAmbientLight / OverrideAmbientColor, the path the Marine's Primerdyne past uses for its
    /// pulsing red (LabAmbientLightController; PlayerController applies the override every frame), fades to a deep red and tints
    /// the lamp red too, logs the start and the colour actually reached, and gives the override back when calm returns.</summary>
    public static class TheatreMood
    {
        private static AdditionalBraveLight lamp;
        private static readonly Color LampCalm = new Color(1f, 0.96f, 0.85f, 1f);
        private static int fadeId;
        private static bool overriding;

        public static void LampOn(MonoBehaviour host, Vector2 worldTable)
        {
            ClinicProp.Show("pluto_lamp_pool");
            try
            {
                GameObject go = new GameObject("VetLampLight");
                go.transform.position = worldTable + new Vector2(0f, 1.5f);
                lamp = go.AddComponent<AdditionalBraveLight>();
                lamp.LightColor = LampCalm;
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
            Color red = new Color(PastConfig.LastPhaseR, PastConfig.LastPhaseG, PastConfig.LastPhaseB, 1f);
            SetAmbient(room, red);   // the room's own target too, so the red survives if anything else drops the override
            Color lampRed = new Color(PastConfig.LastPhaseLampR, PastConfig.LastPhaseLampG, PastConfig.LastPhaseLampB, 1f);
            if (!Fade(red, lampRed, true, "mood: last phase red")) return;
            if (lamp != null) ClinicSound.Play("Play_ENM_darken_world_01", lamp.gameObject);
        }

        public static void Restore(RoomHandler room)
        {
            Color calm = new Color(PastConfig.AmbientR, PastConfig.AmbientG, PastConfig.AmbientB, 1f);
            SetAmbient(room, calm);
            if (overriding) Fade(calm, LampCalm, false, "mood: calm again");
            else PastPlugin.Log("mood: calm again (the room was never red)");
        }

        /// <summary>The controller is going away: stop any fade and give the ambient override back.</summary>
        public static void Release()
        {
            fadeId++;
            if (!overriding) return;
            overriding = false;
            if (GameManager.HasInstance && GameManager.Instance.Dungeon != null) GameManager.Instance.Dungeon.OverrideAmbientLight = false;
        }

        private static bool Fade(Color target, Color lampTarget, bool keepOverride, string label)
        {
            Dungeon d = GameManager.HasInstance ? GameManager.Instance.Dungeon : null;
            if (d == null) { PastPlugin.Log(label + ": no dungeon, the ambient cannot change"); return false; }
            int id = ++fadeId;
            Color from = d.OverrideAmbientLight ? d.OverrideAmbientColor : RenderSettings.ambientLight;
            Color lampFrom = lamp != null ? lamp.LightColor : LampCalm;
            d.OverrideAmbientColor = from;
            d.OverrideAmbientLight = true;
            overriding = true;
            float seconds = Mathf.Max(0.05f, PastConfig.MoodFadeSeconds);
            PastPlugin.Log(label + ": ambient " + Rgb(from) + " -> " + Rgb(target) + " over " + seconds.ToString("0.0") + " s via Dungeon.OverrideAmbientLight, lamp "
                + (lamp != null ? Rgb(lampFrom) + " -> " + Rgb(lampTarget) : "none"));
            GameManager.Instance.StartCoroutine(FadeRoutine(id, d, from, target, lampFrom, lampTarget, seconds, keepOverride, label));
            return true;
        }

        private static IEnumerator FadeRoutine(int id, Dungeon d, Color from, Color target, Color lampFrom, Color lampTarget, float seconds, bool keepOverride, string label)
        {
            float t = 0f;
            while (t < seconds)
            {
                if (id != fadeId || d == null) yield break;
                t += BraveTime.DeltaTime;
                float k = Mathf.SmoothStep(0f, 1f, t / seconds);
                d.OverrideAmbientColor = Color.Lerp(from, target, k);
                if (lamp != null) lamp.LightColor = Color.Lerp(lampFrom, lampTarget, k);
                yield return null;
            }
            if (id != fadeId || d == null) yield break;
            d.OverrideAmbientColor = target;
            if (lamp != null) lamp.LightColor = lampTarget;
            yield return null;
            yield return null;   // PlayerController has copied the override into RenderSettings by now
            PastPlugin.Log(label + " reached: override " + d.OverrideAmbientLight + ", RenderSettings.ambientLight " + Rgb(RenderSettings.ambientLight)
                + (keepOverride ? "" : ", override released"));
            if (!keepOverride && id == fadeId)
            {
                d.OverrideAmbientLight = false;
                overriding = false;
            }
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

        private static string Rgb(Color c) { return c.r.ToString("0.00") + "/" + c.g.ToString("0.00") + "/" + c.b.ToString("0.00"); }
    }
}
