using System;
using System.Collections;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>
    /// Dialogue that stays on screen. The game never keeps a TextBox or ThoughtBubble inside the view (their prefabs have
    /// fitToScreen off), a cutscene's letterbox leaves only about 70 % of the height visible, and up to 0.10.1 our lines also
    /// sat 2.25 units above the NPC talk points while the camera stayed put: the Receptionist, Grandma, the intercom and the
    /// Vet spoke off screen. Every line here anchors at the speaker's head (the NPC talk point, the body sprite's top otherwise),
    /// picks the slide from where the speaker is relative to the view, measures its own box once it has scaled in, and during a
    /// cutscene pans the locked camera the least distance that shows the box and the speaker; outside a cutscene it nudges the
    /// box inside the view instead. Advance: the first press finishes the text, the second closes it. A line only ever closes
    /// the box it opened.
    /// </summary>
    public static class PastTalk
    {
        private const float Margin = 0.5f;
        private const float LetterboxBand = 0.7f;   // LockConversation letterboxes to 0.35: about 70 % of the height stays visible
        private const float ScaleInSeconds = 0.1f;  // TextBoxManager scales a new box up over 0.06 s
        private static Transform voice;            // the intercom's anchor over Pluto (a letterbox line, which the game keeps on screen)

        private static CameraController Cam
        {
            get { return GameManager.Instance != null ? GameManager.Instance.MainCameraController : null; }
        }

        /// <summary>The speaker's body sprite: a GameActor's own sprite (not its shadow or gun), else the first sprite below.</summary>
        private static tk2dBaseSprite Body(Transform who)
        {
            if (who == null) return null;
            GameActor actor = who.GetComponent<GameActor>();
            if (actor != null && actor.sprite != null) return actor.sprite;
            return who.GetComponentInChildren<tk2dBaseSprite>();
        }

        /// <summary>Where a speaker's box starts: an NPC's talk point, the top of the body sprite, else above the transform.</summary>
        public static Vector3 Head(Transform who)
        {
            if (who == null) return Vector3.zero;
            ClinicNpc npc = who.GetComponent<ClinicNpc>();
            if (npc != null && npc.talkPoint != null) return npc.talkPoint.position;
            tk2dBaseSprite s = Body(who);
            Vector2 p = s != null ? s.WorldTopCenter + new Vector2(0f, 0.25f) : (Vector2)who.position + new Vector2(0.75f, 1.5f);
            return new Vector3(p.x, p.y, who.position.z);
        }

        private static Vector2 Feet(Transform who)
        {
            tk2dBaseSprite s = Body(who);
            return s != null ? s.WorldBottomCenter : (who != null ? (Vector2)who.position : Vector2.zero);
        }

        private static Vector2 Center()
        {
            CameraController cam = Cam;
            if (cam == null) return Vector2.zero;
            return cam.ManualControl ? (Vector2)cam.OverridePosition : (Vector2)cam.transform.position;
        }

        private static Vector2 ViewSize(bool letterboxed)
        {
            CameraController cam = Cam;
            Vector2 size = cam != null ? cam.MaxVisiblePoint - cam.MinVisiblePoint : Vector2.zero;
            if (size.x < 1f) size = new Vector2(30f, 16.875f) / (cam != null && cam.CurrentZoomScale > 0.01f ? cam.CurrentZoomScale : 1f);
            if (letterboxed) size.y *= LetterboxBand;
            return size;
        }

        /// <summary>A speaker left of the view grows the box to the right, right of it to the left (TextBoxManager's slide).</summary>
        public static TextBoxManager.BoxSlideOrientation Slide(float headX, float centerX)
        {
            if (headX < centerX - 4f) return TextBoxManager.BoxSlideOrientation.FORCE_RIGHT;
            if (headX > centerX + 4f) return TextBoxManager.BoxSlideOrientation.FORCE_LEFT;
            return TextBoxManager.BoxSlideOrientation.NO_ADJUSTMENT;
        }

        /// <summary>Shows the line and returns the box it created (null if it cannot be told apart from boxes already there).</summary>
        private static TextBoxManager Show(Transform who, Vector3 head, string text, bool thought, Vector2 center)
        {
            TextBoxManager[] before = who.GetComponentsInChildren<TextBoxManager>(true);
            if (thought) TextBoxManager.ShowThoughtBubble(head, who, -1f, text, false, false, string.Empty);
            else TextBoxManager.ShowTextBox(head, who, -1f, text, string.Empty, false, Slide(head.x, center.x), true, false);
            return NewBox(who, before);
        }

        private static TextBoxManager NewBox(Transform who, TextBoxManager[] before)
        {
            if (who == null) return null;
            foreach (TextBoxManager b in who.GetComponentsInChildren<TextBoxManager>(true))
                if (Array.IndexOf(before, b) < 0) return b;
            return null;
        }

        /// <summary>Close the speaker's box only if no newer line has replaced ours in the meantime.</summary>
        private static void ClearMine(Transform who, TextBoxManager mine, TextBoxManager[] beforeMine)
        {
            if (who == null || !TextBoxManager.HasTextBox(who)) return;
            foreach (TextBoxManager b in who.GetComponentsInChildren<TextBoxManager>(true))
                if (b != null && b != mine && Array.IndexOf(beforeMine, b) < 0) return;   // someone else's newer box is up
            TextBoxManager.ClearTextBox(who);
        }

        /// <summary>The world rectangle of a box from its frame's renderer (world space: includes the box's scale and anchor).</summary>
        private static bool Measure(TextBoxManager box, out Rect rect)
        {
            rect = new Rect();
            if (box == null) return false;
            tk2dSlicedSprite frame = box.GetComponentInChildren<tk2dSlicedSprite>();
            Renderer r = frame != null ? frame.GetComponent<Renderer>() : null;
            if (r == null) return false;
            Bounds b = r.bounds;
            rect = new Rect((Vector2)b.min, (Vector2)b.size);
            return rect.width > 0.5f && rect.height > 0.5f;
        }

        /// <summary>A rough box from TextBoxManager's word wrap when the frame cannot be measured.</summary>
        private static Rect Estimate(Vector3 head, string text, Vector2 center)
        {
            float wrap = text.Length < 25 ? 250f : 200f + (text.Length - 25) / 4f;
            float w = Mathf.Clamp(Mathf.Min(text.Length * 6f, wrap) / 16f + 1f, 3f, 12f);
            int lines = Mathf.Max(1, Mathf.CeilToInt(text.Length * 6f / wrap));
            float h = 1f + 0.7f * lines;
            float left = head.x <= center.x ? head.x - w / 3f : head.x - 2f * w / 3f;
            return new Rect(left, head.y + 0.1875f, w, h);
        }

        /// <summary>The view centre closest to the current one that shows the whole box and the speaker's feet; the box wins if both cannot fit.</summary>
        private static Vector2 FitFocus(Vector2 center, Rect box, Vector2 feet, Vector2 view)
        {
            float minY = box.yMax + Margin - view.y / 2f;
            float maxY = Mathf.Min(box.yMin, feet.y) - Margin + view.y / 2f;
            float minX = box.xMax + Margin - view.x / 2f;
            float maxX = box.xMin - Margin + view.x / 2f;
            Vector2 f = center;
            f.y = minY <= maxY ? Mathf.Clamp(f.y, minY, maxY) : minY;
            f.x = minX <= maxX ? Mathf.Clamp(f.x, minX, maxX) : box.center.x;
            return f;
        }

        private static void Nudge(TextBoxManager box, Rect rect, Vector2 center, Vector2 view)
        {
            if (box == null) return;
            Rect v = new Rect(center - view / 2f, view);
            float dx = 0f, dy = 0f;
            if (rect.xMin < v.xMin + Margin) dx = v.xMin + Margin - rect.xMin;
            else if (rect.xMax > v.xMax - Margin) dx = v.xMax - Margin - rect.xMax;
            if (rect.yMax > v.yMax - Margin) dy = v.yMax - Margin - rect.yMax;
            else if (rect.yMin < v.yMin + Margin) dy = v.yMin + Margin - rect.yMin;
            if (dx != 0f || dy != 0f) box.transform.position += new Vector3(dx, dy, 0f);
        }

        private static IEnumerator WaitScaleIn()
        {
            float t = 0f;
            while (t < ScaleInSeconds)
            {
                t += GameManager.INVARIANT_DELTA_TIME;
                yield return null;
            }
            yield return null;
        }

        /// <summary>Smoothly moves a locked (manual) camera; does nothing when the camera follows the player.</summary>
        public static IEnumerator PanTo(Vector2 target, float seconds)
        {
            CameraController cam = Cam;
            if (cam == null || !cam.ManualControl) yield break;
            Vector3 from = cam.OverridePosition;
            float t = 0f;
            while (t < seconds && cam != null)
            {
                t += GameManager.INVARIANT_DELTA_TIME;
                float k = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(t / seconds));
                cam.OverridePosition = new Vector3(Mathf.Lerp(from.x, target.x, k), Mathf.Lerp(from.y, target.y, k), from.z);
                yield return null;
            }
            if (cam != null) cam.OverridePosition = new Vector3(target.x, target.y, from.z);
        }

        /// <summary>A blocking line (cutscenes). locked = the camera is held by a cutscene and may be panned.</summary>
        public static IEnumerator Say(MonoBehaviour host, Transform who, string text, float seconds, bool thought, bool locked)
        {
            if (host == null || who == null || string.IsNullOrEmpty(text)) yield break;
            Vector3 head = Head(who);
            Vector2 center = Center();
            TextBoxManager[] before = who.GetComponentsInChildren<TextBoxManager>(true);
            TextBoxManager mine;
            try { mine = Show(who, head, text, thought, center); }
            catch (Exception e) { PastPlugin.Log("line failed: " + e.Message); yield break; }
            yield return host.StartCoroutine(WaitScaleIn());
            if (who == null) yield break;
            Rect box;
            if (!Measure(mine, out box)) box = Estimate(head, text, center);
            Vector2 view = ViewSize(locked);
            if (locked)
            {
                Vector2 focus = FitFocus(center, box, Feet(who), view);
                if ((focus - center).sqrMagnitude > 0.04f)
                {
                    yield return host.StartCoroutine(PanTo(focus, 0.4f));
                    center = focus;
                }
            }
            Nudge(mine, box, center, view);
            yield return host.StartCoroutine(WaitAdvance(who, seconds, text));
            ClearMine(who, mine, before);
        }

        /// <summary>A line that does not block (fights, ambient chatter): shown, kept inside the view, cleared after its time.</summary>
        public static void Bubble(MonoBehaviour host, Transform who, string text, float seconds, bool thought)
        {
            if (host == null || who == null || string.IsNullOrEmpty(text)) return;
            host.StartCoroutine(BubbleCR(who, text, seconds, thought));
        }

        private static IEnumerator BubbleCR(Transform who, string text, float seconds, bool thought)
        {
            if (TextBoxManager.HasTextBox(who)) yield break;   // never cut a line that is already up
            Vector3 head = Head(who);
            Vector2 center = Center();
            TextBoxManager[] before = who.GetComponentsInChildren<TextBoxManager>(true);
            TextBoxManager mine;
            try { mine = Show(who, head, text, thought, center); }
            catch (Exception e) { PastPlugin.Log("bubble failed: " + e.Message); yield break; }
            float t = 0f;
            while (t < ScaleInSeconds && who != null)
            {
                t += BraveTime.DeltaTime;
                yield return null;
            }
            Rect box;
            if (who != null && Measure(mine, out box)) Nudge(mine, box, center, ViewSize(Cam != null && Cam.ManualControl));
            float limit = Mathf.Min(Mathf.Max(seconds, TextBoxManager.GetEstimatedReadingTime(text)), seconds + 3f);
            while (t < limit && who != null)
            {
                t += BraveTime.DeltaTime;
                yield return null;
            }
            ClearMine(who, mine, before);
        }

        /// <summary>The intercom: a letterbox line over the listener's head, which the game itself keeps on screen. The anchor
        /// follows the listener without being parented to it, so Pluto's own lines never find the intercom's box.</summary>
        public static void Announce(MonoBehaviour host, Transform listener, string text, float seconds)
        {
            if (host == null || listener == null || string.IsNullOrEmpty(text)) return;
            host.StartCoroutine(AnnounceCR(listener, text, seconds));
        }

        private static IEnumerator AnnounceCR(Transform listener, string text, float seconds)
        {
            if (voice == null) voice = new GameObject("VetIntercomVoice").transform;
            Vector3 offset = new Vector3(0.75f, 3.25f, 0f);
            voice.position = listener.position + offset;
            if (TextBoxManager.HasTextBox(voice)) TextBoxManager.ClearTextBoxImmediate(voice);
            TextBoxManager[] before = voice.GetComponentsInChildren<TextBoxManager>(true);
            try { TextBoxManager.ShowLetterBox(voice.position, voice, -1f, text, false, false); }
            catch (Exception e) { PastPlugin.Log("intercom failed: " + e.Message); yield break; }
            TextBoxManager mine = NewBox(voice, before);
            float t = 0f, limit = Mathf.Max(seconds, TextBoxManager.GetEstimatedReadingTime(text));
            while (t < limit && voice != null && listener != null)
            {
                t += BraveTime.DeltaTime;
                voice.position = listener.position + offset;
                yield return null;
            }
            if (voice != null) ClearMine(voice, mine, before);
        }

        /// <summary>Vanilla-like advance: the first press finishes the typewriter, the second closes the line; lines also close on their own.</summary>
        private static IEnumerator WaitAdvance(Transform who, float seconds, string text)
        {
            float limit = Mathf.Min(Mathf.Max(seconds, TextBoxManager.GetEstimatedReadingTime(text)), seconds + 4f);
            float t = 0f;
            while (t < limit && who != null)
            {
                t += GameManager.INVARIANT_DELTA_TIME;
                if (t > 0.2f && Pressed())
                {
                    if (TextBoxManager.TextBoxCanBeAdvanced(who)) TextBoxManager.AdvanceTextBox(who);
                    else break;
                }
                yield return null;
            }
        }

        private static bool Pressed()
        {
            PlayerController[] players = GameManager.Instance != null ? GameManager.Instance.AllPlayers : null;
            int n = players != null && players.Length > 0 ? players.Length : 1;
            for (int i = 0; i < n; i++)
            {
                BraveInput input = BraveInput.GetInstanceForPlayer(i);
                if (input != null && input.WasAdvanceDialoguePressed()) return true;
            }
            return false;
        }
    }
}
