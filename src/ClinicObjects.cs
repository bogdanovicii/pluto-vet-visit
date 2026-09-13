using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Alexandria.DungeonAPI;
using Alexandria.ItemAPI;

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
            PastPlugin.Log("registered " + (ClinicLayout.OBJECTS.Length + 1) + " custom objects");
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
            prop.perpendicular = spec.Collider != ObjectSpec.Layer.None;
            if (spec.Collider != ObjectSpec.Layer.None)
            {
                CollisionLayer layer = spec.Collider == ObjectSpec.Layer.High ? CollisionLayer.HighObstacle : CollisionLayer.LowObstacle;
                AddCollider(go, layer, spec.OffX, spec.OffY, spec.W, spec.H);
            }
            return go;
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
            body.PixelColliders = new List<PixelCollider>
            {
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
                }
            };
            return body;
        }

        /// <summary>Fake prefab: inactive and kept across scenes; Alexandria re-activates the placed clone.</summary>
        public static void Register(string name, GameObject go)
        {
            FakePrefab.MakeFakePrefab(go);
            StaticReferences.customObjects[name] = go;
        }
    }

    /// <summary>Depth sorting for placed props: furniture stands up (perpendicular), decor lies under actors.</summary>
    public class ClinicProp : BraveBehaviour
    {
        public float heightOffGround;
        public bool perpendicular;

        private void Start()
        {
            if (sprite == null) return;
            sprite.IsPerpendicular = perpendicular;
            sprite.HeightOffGround = heightOffGround;
            sprite.UpdateZDepth();
        }
    }
}
