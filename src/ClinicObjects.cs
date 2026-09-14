using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Alexandria.DungeonAPI;
using Alexandria.ItemAPI;
using Dungeonator;

namespace PlutoVetVisit
{
    /// <summary>Prefabs the room places by name through StaticReferences.customObjects.</summary>
    public static class ClinicObjects
    {
        public const string OBJECT_ROOT = "PlutoVetVisit/Resources/Objects";

        public static void Init()
        {
            Assembly asm = typeof(PastPlugin).Assembly;
            Register(ClinicLayout.CONTROLLER_OBJECT, BuildController());
            foreach (ObjectSpec spec in ClinicLayout.OBJECTS)
                Register(spec.Name, BuildProp(spec, asm));
            foreach (NpcSpec spec in CastLayout.NPCS)
                Register(spec.Name, ClinicNpc.Build(spec, asm));
            int animated = 0, examinable = 0;
            foreach (ObjectSpec spec in ClinicLayout.OBJECTS)
            {
                if (spec.Frames > 1) animated++;
                if (!string.IsNullOrEmpty(PastConfig.PropComment(spec.Name))) examinable++;
            }
            PastPlugin.Log("registered " + (ClinicLayout.OBJECTS.Length + CastLayout.NPCS.Length + 1) + " custom objects (" + animated + " animated, " + examinable + " examinable)");
        }

        private static GameObject BuildController()
        {
            GameObject go = new GameObject(ClinicLayout.CONTROLLER_OBJECT);
            go.AddComponent<VetVisitController>();
            return go;
        }

        private static GameObject BuildProp(ObjectSpec spec, Assembly asm)
        {
            GameObject go = SpriteBuilder.SpriteFromResource(OBJECT_ROOT + "/" + spec.Png + ".png", new GameObject(spec.Name), asm);
            ClinicProp prop = go.AddComponent<ClinicProp>();
            prop.heightOffGround = spec.HeightOffGround;
            // Standing (perpendicular) is its own flag since 0.10.1: the wall faces and the decor hung on them stand
            // without a collider, or the tileset's standing wall face draws over them.
            prop.perpendicular = spec.Perpendicular;
            prop.kind = spec.Png.StartsWith("floor_") ? ClinicProp.Kind.Floor : spec.Png.StartsWith("wall_face") ? ClinicProp.Kind.WallFace : ClinicProp.Kind.Prop;
            if (spec.Collider != ObjectSpec.Layer.None)
            {
                CollisionLayer layer = spec.Collider == ObjectSpec.Layer.High ? CollisionLayer.HighObstacle : CollisionLayer.LowObstacle;
                AddCollider(go, layer, spec.OffX, spec.OffY, spec.W, spec.H);
                // 0.12.1: footprints one rectangle cannot cover (the reception counter's ends, a kennel's open door)
                foreach (ColliderRect r in ClinicLayout.EXTRA_COLLIDERS)
                    if (r.Name == spec.Name) AddCollider(go, layer, r.OffX, r.OffY, r.W, r.H);
            }
            if (spec.Name == ClinicLayout.DOOR_OBJECT) AddDoor(go, asm);
            if (spec.Frames > 1) AddLoop(go, spec, asm);
            if (!string.IsNullOrEmpty(PastConfig.PropComment(spec.Name))) go.AddComponent<ClinicExaminable>().propName = spec.Name;
            return go;
        }

        /// <summary>An animated prop: frame 1 is the placed sprite, frames 2..n (`png_f2.png` ...) join its collection, one looping clip.</summary>
        private static void AddLoop(GameObject go, ObjectSpec spec, Assembly asm)
        {
            tk2dSprite sprite = go.GetComponent<tk2dSprite>();
            List<int> ids = new List<int> { sprite.spriteId };
            for (int i = 2; i <= spec.Frames; i++)
            {
                string path = OBJECT_ROOT + "/" + spec.Png + "_f" + i + ".png";
                // SpriteBuilder.AddSpriteToCollection dereferences the texture: a missing frame would throw and take the
                // whole "objects" step (and with it the past) down. Check first, skip what is missing.
                if (ResourceExtractor.GetTextureFromResource(path, asm) == null)
                {
                    PastPlugin.Log("animated prop " + spec.Name + ": frame " + i + " missing (" + path + "), skipped");
                    continue;
                }
                ids.Add(SpriteBuilder.AddSpriteToCollection(path, sprite.Collection, asm));
            }
            if (ids.Count < 2) return;
            tk2dSpriteAnimator animator = go.AddComponent<tk2dSpriteAnimator>();
            animator.Library = go.AddComponent<tk2dSpriteAnimation>();
            tk2dSpriteAnimationClip clip = new tk2dSpriteAnimationClip
            {
                name = spec.Png + "_loop",
                fps = spec.Fps > 0f ? spec.Fps : 6f,
                wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop,
                frames = new tk2dSpriteAnimationFrame[ids.Count],
            };
            for (int i = 0; i < ids.Count; i++)
                clip.frames[i] = new tk2dSpriteAnimationFrame { spriteCollection = sprite.Collection, spriteId = ids[i] };
            animator.Library.clips = new[] { clip };
            animator.playAutomatically = false;   // ClinicProp.Start plays it once the clone is placed
        }

        /// <summary>The zone door: the open frame joins the closed sprite's collection so ClinicDoor can swap them.</summary>
        private static void AddDoor(GameObject go, Assembly asm)
        {
            tk2dSprite sprite = go.GetComponent<tk2dSprite>();
            ClinicDoor door = go.AddComponent<ClinicDoor>();
            door.closedId = sprite.spriteId;
            door.openId = SpriteBuilder.AddSpriteToCollection(OBJECT_ROOT + "/clinic_door_open.png", sprite.Collection, asm);
            PastPlugin.Log("clinic door: closed sprite " + door.closedId + ", open sprite " + door.openId);
        }

        /// <summary>One manual pixel collider (pixels from the sprite's lower-left), the way the floor-making guide does it.</summary>
        public static SpeculativeRigidbody AddCollider(GameObject go, CollisionLayer layer, int offX, int offY, int w, int h)
        {
            SpeculativeRigidbody body = go.GetOrAddComponent<SpeculativeRigidbody>();
            body.CollideWithOthers = true;
            body.CollideWithTileMap = false;
            body.Velocity = Vector2.zero;
            body.MaxVelocity = Vector2.zero;
            body.ForceAlwaysUpdate = false;
            body.CanPush = false;
            body.CanBePushed = false;
            body.PushSpeedModifier = 1f;
            body.CanCarry = false;
            body.CanBeCarried = false;
            body.PreventPiercing = false;
            body.SkipEmptyColliders = false;
            body.RecheckTriggers = false;
            body.UpdateCollidersOnRotation = false;
            body.UpdateCollidersOnScale = false;
            // 0.12.1: appends, so a prop can carry several rectangles (ObjectSpec plus ClinicLayout.EXTRA_COLLIDERS)
            if (body.PixelColliders == null) body.PixelColliders = new List<PixelCollider>();
            body.PixelColliders.Add(
                new PixelCollider
                {
                    ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
                    CollisionLayer = layer,
                    IsTrigger = false,
                    BagleUseFirstFrameOnly = false,
                    SpecifyBagelFrame = string.Empty,
                    BagelColliderNumber = 0,
                    ManualOffsetX = offX,
                    ManualOffsetY = offY,
                    ManualWidth = w,
                    ManualHeight = h,
                    ManualDiameter = 0,
                    ManualLeftX = 0, ManualLeftY = 0, ManualRightX = 0, ManualRightY = 0,
                });
            return body;
        }

        /// <summary>Fake prefab: inactive and kept across scenes; Alexandria re-activates the placed clone.</summary>
        public static void Register(string name, GameObject go)
        {
            FakePrefab.MakeFakePrefab(go);
            StaticReferences.customObjects[name] = go;
        }
    }

    /// <summary>Depth sorting for placed props: furniture stands up (perpendicular), decor lies under actors.
    /// A flat sprite's z grows with its own height (tk2dBaseSprite tilts flat sprites away from the camera), so
    /// the zone floors at HeightOffGround -4 sort behind every actor at every pixel; the wall faces at +0.5 draw
    /// over the tileset's wall face and behind anyone standing south of them. Both can be switched off in the config.</summary>
    public class ClinicProp : BraveBehaviour
    {
        public enum Kind { Prop, Floor, WallFace }
        public float heightOffGround;
        public bool perpendicular;
        public Kind kind = Kind.Prop;

        private void Start()
        {
            if (sprite == null) return;
            if ((kind == Kind.Floor && !PastConfig.FloorTiles) || (kind == Kind.WallFace && !PastConfig.WallFaces))
            {
                sprite.renderer.enabled = false;
                return;
            }
            sprite.IsPerpendicular = perpendicular;
            sprite.HeightOffGround = heightOffGround;
            sprite.UpdateZDepth();
            if (spriteAnimator != null && spriteAnimator.Library != null && spriteAnimator.Library.clips != null && spriteAnimator.Library.clips.Length > 0)
                spriteAnimator.Play(spriteAnimator.Library.clips[0].name);
        }
    }

    /// <summary>
    /// A prop Pluto can examine, the vanilla PlayerCommentInteractable way: a white outline while he is in range, and on
    /// interact a thought bubble over Pluto with the prop's line from the config ([Props] Comment_...). Advance closes it.
    /// </summary>
    public class ClinicExaminable : BraveBehaviour, IPlayerInteractable
    {
        public string propName;
        private RoomHandler room;
        private bool busy;

        private IEnumerator Start()
        {
            while (Dungeon.IsGenerating) yield return null;
            yield return null;
            room = ((Vector2)transform.position).GetAbsoluteRoom();
            if (room != null) room.RegisterInteractable(this);
        }

        public override void OnDestroy()
        {
            if (room != null) room.DeregisterInteractable(this);
            base.OnDestroy();
        }

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

        public void Interact(PlayerController interactor)
        {
            string text = PastConfig.PropComment(propName);
            if (busy || interactor == null || string.IsNullOrEmpty(text) || TextBoxManager.HasTextBox(interactor.transform)) return;
            StartCoroutine(Think(interactor, text));
        }

        private IEnumerator Think(PlayerController p, string text)
        {
            busy = true;
            TextBoxManager.ShowThoughtBubble(p.transform.position + new Vector3(0.75f, 1.5f, 0f), p.transform, -1f, text, false, false, string.Empty);
            float t = 0f;
            yield return null;
            while (t < 3.5f && p != null)
            {
                t += BraveTime.DeltaTime;
                BraveInput input = BraveInput.GetInstanceForPlayer(0);
                if (t > 0.4f && input != null && input.WasAdvanceDialoguePressed()) break;
                yield return null;
            }
            if (p != null) TextBoxManager.ClearTextBox(p.transform);
            busy = false;
        }

        public string GetAnimationState(PlayerController interactor, out bool shouldBeFlipped)
        {
            shouldBeFlipped = false;
            return string.Empty;
        }
    }
}
