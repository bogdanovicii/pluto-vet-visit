using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using Alexandria.ItemAPI;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>0.14.2 rescue: a cat, dog or cone patient let out of its kennel, hopping along a path to the theatre.</summary>
    public class FreedAnimal : BraveBehaviour
    {
        public static FreedAnimal Spawn(string kind, Vector2 at)
        {
            Assembly asm = typeof(PastPlugin).Assembly;
            string f1 = ClinicObjects.OBJECT_ROOT + "/freed_" + kind + "_f1.png";
            if (ResourceExtractor.GetTextureFromResource(f1, asm) == null) { PastPlugin.Log("rescue: no art for " + kind); return null; }
            GameObject go = SpriteBuilder.SpriteFromResource(f1, new GameObject("freed_" + kind), asm);
            tk2dSprite s = go.GetComponent<tk2dSprite>();
            List<int> ids = new List<int> { s.spriteId };
            string f2 = ClinicObjects.OBJECT_ROOT + "/freed_" + kind + "_f2.png";
            if (ResourceExtractor.GetTextureFromResource(f2, asm) != null) ids.Add(SpriteBuilder.AddSpriteToCollection(f2, s.Collection, asm));
            tk2dSpriteAnimator animator = go.AddComponent<tk2dSpriteAnimator>();
            animator.Library = go.AddComponent<tk2dSpriteAnimation>();
            tk2dSpriteAnimationClip clip = new tk2dSpriteAnimationClip
            {
                name = "run",
                fps = 8f,
                wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop,
                frames = new tk2dSpriteAnimationFrame[ids.Count],
            };
            for (int i = 0; i < ids.Count; i++) clip.frames[i] = new tk2dSpriteAnimationFrame { spriteCollection = s.Collection, spriteId = ids[i] };
            animator.Library.clips = new[] { clip };
            animator.playAutomatically = false;
            go.transform.position = new Vector3(at.x, at.y, at.y);
            s.IsPerpendicular = true;
            s.HeightOffGround = -0.5f;
            s.UpdateZDepth();
            FreedAnimal a = go.AddComponent<FreedAnimal>();
            animator.Play("run");
            return a;
        }

        /// <summary>Hops through the points at the given speed (tiles per second), then stops animating.</summary>
        public IEnumerator RunPath(Vector2[] points, float speed)
        {
            foreach (Vector2 target in points)
            {
                Vector2 start = transform.position;
                float dist = Vector2.Distance(start, target);
                if (sprite != null) sprite.FlipX = target.x > start.x;       // the art faces left
                float t = 0f;
                while (dist > 0.01f && t < 1f)
                {
                    t += BraveTime.DeltaTime * speed / dist;
                    Vector2 p = Vector2.Lerp(start, target, Mathf.Clamp01(t));
                    float hop = Mathf.Abs(Mathf.Sin(t * dist * 5f)) * 0.2f;
                    transform.position = new Vector3(p.x, p.y + hop, p.y);
                    if (sprite != null) sprite.UpdateZDepth();
                    yield return null;
                }
            }
            if (spriteAnimator != null) spriteAnimator.Stop();
        }
    }
}
