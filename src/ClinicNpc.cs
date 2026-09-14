using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Alexandria.ItemAPI;
using Dungeonator;

namespace PlutoVetVisit
{
    /// <summary>
    /// A placed, animated, talk-to-able bystander (the Owner, the Receptionist, Rex, Grandma Cat). Not an AIActor:
    /// it has no health, no brain, and its outline is baked into the art. The controller drives the intro
    /// (Play, Say, Walk, Hide); afterwards Pluto can interact for one line. Modelled on the IPlayerInteractable
    /// pattern the research found in OMITB and Modular, on top of the prop pipeline of ClinicObjects.
    /// </summary>
    public class ClinicNpc : BraveBehaviour, IPlayerInteractable
    {
        public static readonly List<ClinicNpc> All = new List<ClinicNpc>();

        public string who;                 // art folder: owner, receptionist, rex, grandma
        public string idleClip = "idle";   // the first clip of the spec: Grandma rests in "loaf"
        public string comment = string.Empty;
        public Transform talkPoint;
        private RoomHandler room;
        private bool hidden;

        public static ClinicNpc Find(string who)
        {
            foreach (ClinicNpc n in All) if (n != null && n.who == who && !n.hidden) return n;
            return null;
        }

        private void Start()
        {
            if (!All.Contains(this)) All.Add(this);
            if (sprite != null)
            {
                sprite.IsPerpendicular = true;
                sprite.HeightOffGround = 0f;
                sprite.UpdateZDepth();
            }
            if (talkPoint == null)
            {
                GameObject tp = new GameObject("talkpoint");
                tp.transform.parent = transform;
                tp.transform.localPosition = new Vector3(sprite != null ? sprite.GetBounds().size.x / 2f : 0.75f, (sprite != null ? sprite.GetBounds().size.y : 2f) + 0.5f, 0f);
                talkPoint = tp.transform;
            }
            StartCoroutine(RegisterWhenReady());
            Play(idleClip);
        }

        private IEnumerator RegisterWhenReady()
        {
            while (Dungeon.IsGenerating) yield return null;
            yield return null;
            room = ((Vector2)transform.position).GetAbsoluteRoom();
            if (room != null) room.RegisterInteractable(this);
        }

        public override void OnDestroy()
        {
            All.Remove(this);
            if (room != null) room.DeregisterInteractable(this);
            base.OnDestroy();
        }

        // ------------------------------------------------------------------ driven by the controller

        /// <summary>Plays a clip by exact name; a clip the character lacks (Rex has no "talk") falls back to its rest clip.</summary>
        public void Play(string clip)
        {
            if (spriteAnimator == null) return;
            string name = who + "_" + clip;
            if (spriteAnimator.GetClipByName(name) == null) name = who + "_" + idleClip;
            if (spriteAnimator.GetClipByName(name) != null && !spriteAnimator.IsPlaying(name)) spriteAnimator.Play(name);
        }

        /// <summary>Moves at a steady pace to a world point (a plain tween, like the player's Place), playing a clip.</summary>
        public IEnumerator Walk(Vector2 target, float unitsPerSecond, string clip)
        {
            Play(clip);
            Vector2 start = transform.position;
            float dist = Vector2.Distance(start, target);
            float t = 0f;
            while (t < 1f && dist > 0f)
            {
                t += BraveTime.DeltaTime * unitsPerSecond / dist;
                Vector2 p = Vector2.Lerp(start, target, Mathf.Clamp01(t));
                transform.position = new Vector3(p.x, p.y, p.y);
                if (sprite != null) sprite.UpdateZDepth();
                yield return null;
            }
            transform.position = new Vector3(target.x, target.y, target.y);
            Play(idleClip);
        }

        public void Face(bool right)
        {
            if (sprite != null) sprite.FlipX = !right;
        }

        public void Hide()
        {
            hidden = true;
            if (room != null) room.DeregisterInteractable(this);
            gameObject.SetActive(false);
        }

        // ------------------------------------------------------------------ IPlayerInteractable

        public float GetDistanceToPoint(Vector2 point)
        {
            if (sprite == null) return 1000f;
            Bounds b = sprite.GetBounds();
            Vector2 lower = (Vector2)transform.position + (Vector2)b.min;
            return Vector2.Distance(point, BraveMathCollege.ClosestPointOnRectangle(point, lower, b.size)) / 1.5f;
        }

        public float GetOverrideMaxDistance() { return -1f; }

        public void OnEnteredRange(PlayerController interactor)
        {
            if (sprite != null) SpriteOutlineManager.AddOutlineToSprite(sprite, Color.white);
        }

        public void OnExitRange(PlayerController interactor)
        {
            if (sprite != null) SpriteOutlineManager.RemoveOutlineFromSprite(sprite);
        }

        private int commentIndex;

        /// <summary>One of the character's lines per interaction, in turn ("line|line|line" in the config).</summary>
        public void Interact(PlayerController interactor)
        {
            if (string.IsNullOrEmpty(comment) || TextBoxManager.HasTextBox(transform)) return;
            string[] lines = comment.Split('|');
            string line = lines[commentIndex++ % lines.Length].Trim();
            if (line.Length > 0) StartCoroutine(SayComment(line));
        }

        private IEnumerator SayComment(string line)
        {
            Play("talk");
            PastTalk.Bubble(this, transform, line, 2.8f, false);
            yield return new WaitForSeconds(2.9f);
            Play(idleClip);
        }

        public string GetAnimationState(PlayerController interactor, out bool shouldBeFlipped)
        {
            shouldBeFlipped = false;
            return string.Empty;
        }

        // ------------------------------------------------------------------ building

        /// <summary>Sprite from the first idle frame; every clip's frames join its collection; an animator plays them.</summary>
        public static GameObject Build(NpcSpec spec, Assembly asm)
        {
            string rest = spec.Clips[0];
            string first = CastLayout.NPC_ROOT + "/" + spec.Folder + "/" + rest + "/" + spec.Folder + "_" + rest + "_001.png";
            GameObject go = SpriteBuilder.SpriteFromResource(first, new GameObject(spec.Name), asm);
            tk2dSprite sprite = go.GetComponent<tk2dSprite>();
            tk2dSpriteAnimator animator = go.AddComponent<tk2dSpriteAnimator>();
            animator.Library = go.AddComponent<tk2dSpriteAnimation>();
            List<tk2dSpriteAnimationClip> clips = new List<tk2dSpriteAnimationClip>();
            for (int c = 0; c < spec.Clips.Length; c++)
            {
                string clip = spec.Clips[c];
                List<int> ids = new List<int>();
                for (int i = 1; i <= spec.Frames[c]; i++)
                {
                    string path = CastLayout.NPC_ROOT + "/" + spec.Folder + "/" + clip + "/" + spec.Folder + "_" + clip + "_" + i.ToString("000") + ".png";
                    ids.Add(clip == rest && i == 1 ? sprite.spriteId : SpriteBuilder.AddSpriteToCollection(path, sprite.Collection, asm));
                }
                tk2dSpriteAnimationClip k = new tk2dSpriteAnimationClip { name = spec.Folder + "_" + clip, fps = Fps(clip), wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop };
                k.frames = new tk2dSpriteAnimationFrame[ids.Count];
                for (int i = 0; i < ids.Count; i++) k.frames[i] = new tk2dSpriteAnimationFrame { spriteCollection = sprite.Collection, spriteId = ids[i] };
                clips.Add(k);
            }
            animator.Library.clips = clips.ToArray();
            animator.playAutomatically = false;
            ClinicNpc npc = go.AddComponent<ClinicNpc>();
            npc.who = spec.Folder;
            npc.idleClip = rest;
            npc.comment = PastConfig.Comment(spec.Folder);
            return go;
        }

        private static float Fps(string clip)
        {
            switch (clip)
            {
                case "walk": case "walk_free": return 8f;
                case "talk": return 6f;
                case "loaf": return 2f;
                default: return 4f;
            }
        }
    }
}
