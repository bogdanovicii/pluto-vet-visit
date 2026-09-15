using System;
using System.Collections.Generic;
using Brave.BulletScript;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>Lingering anesthesia clouds, so ring and wall openings are not placed inside one.</summary>
    public static class LingeringHazards
    {
        private static readonly List<Bullet> Clouds = new List<Bullet>();

        public static void Add(Bullet cloud) { if (cloud != null && !Clouds.Contains(cloud)) Clouds.Add(cloud); }
        public static void Remove(Bullet cloud) { Clouds.Remove(cloud); }

        public static bool Blocks(Vector2 point, float radius)
        {
            for (int i = Clouds.Count - 1; i >= 0; i--)
            {
                Bullet c = Clouds[i];
                if (c == null || c.Destroyed || c.Projectile == null || !c.Projectile.gameObject.activeInHierarchy) { Clouds.RemoveAt(i); continue; }
                if ((c.Position - point).sqrMagnitude <= radius * radius) return true;
            }
            return false;
        }
    }

    /// <summary>Scores ring and wall openings against the real floor (GapScorer does the math): walks each opening's direction
    /// from the script in half-tile steps until a wall tile or a lingering cloud, and asks whether Pluto can walk to it before
    /// the bullets arrive. Only tiles and clouds are seen; props with colliders are not (an in-game check).</summary>
    public static class ArenaProbe
    {
        /// <summary>A conservative walking speed for Pluto in tiles per second (the Gungeoneers walk about 7).</summary>
        public const float PlutoSpeed = 6f;
        private const float Step = 0.5f, CloudRadius = 0.9f;
        private static bool loggedFailure;

        public static float Clearance(Bullet script, Vector2 origin, float angle, float max)
        {
            Vector2 dir = new Vector2(Mathf.Cos(angle * Mathf.Deg2Rad), Mathf.Sin(angle * Mathf.Deg2Rad));
            for (float d = Step; d <= max + 1e-3f; d += Step)
            {
                Vector2 p = origin + dir * d;
                if (script.IsPointInTile(p) || LingeringHazards.Blocks(p, CloudRadius)) return d - Step;
            }
            return max;
        }

        /// <summary>Index of the best opening among centre angles (degrees), or -1 when the arena cannot be read (callers then
        /// keep their old random choice).</summary>
        public static int PickGap(Bullet script, float[] centres, float bulletSpeed)
        {
            try
            {
                if (script == null || centres == null || centres.Length == 0) return -1;
                Vector2 origin = script.Position;
                Vector2 toPluto = script.GetPredictedTargetPosition(0f, bulletSpeed) - origin;
                float distance = toPluto.magnitude;
                float plutoAngle = Mathf.Atan2(toPluto.y, toPluto.x) * Mathf.Rad2Deg;
                float need = GapScorer.Need(distance), reach = GapScorer.Reach(distance, bulletSpeed, 0f, PlutoSpeed);
                float[] scores = new float[centres.Length];
                for (int i = 0; i < centres.Length; i++)
                    scores[i] = GapScorer.Score(Clearance(script, origin, centres[i], need), need, Mathf.DeltaAngle(plutoAngle, centres[i]), distance, reach);
                return GapScorer.Pick(scores, UnityEngine.Random.value, 0.1f);
            }
            catch (Exception e)
            {
                if (!loggedFailure) { loggedFailure = true; PastPlugin.Log("gap probe failed (random openings): " + e.Message); }
                return -1;
            }
        }
    }

    /// <summary>Visual pulses on live projectiles. Pools are per bank prefab, so a pill object is only ever reused by a pill:
    /// every bullet resets its look when its Top starts and when it is destroyed. The unpulsed scale comes from the bank's
    /// inactive prefab, which is never pulsed.</summary>
    public static class ProjectileLook
    {
        public static void SetScale(Projectile p, string bank, float factor)
        {
            tk2dBaseSprite s = p != null ? p.sprite : null;
            if (s == null) return;
            Vector3 target = BaseScale(bank) * factor;
            if (s.scale != target) s.scale = target;
        }

        public static void SetVisible(Projectile p, bool visible)
        {
            Renderer r = p != null && p.sprite != null ? p.sprite.GetComponent<Renderer>() : null;
            if (r != null && r.enabled != visible) r.enabled = visible;
        }

        public static void Reset(Projectile p, string bank)
        {
            SetScale(p, bank, 1f);
            SetVisible(p, true);
        }

        private static Vector3 BaseScale(string bank)
        {
            Projectile proto = VetBoss.BankProjectile(bank);
            return proto != null && proto.sprite != null ? proto.sprite.scale : Vector3.one;
        }
    }

    /// <summary>The explicit half of the pill contract: a player shot touching a pill this frame (swept over the shot's last
    /// frame of travel, so fast shots cannot skip it). Bank projectiles keep collidesWithProjectiles off; the pill looks.</summary>
    public static class ShotProbe
    {
        public const float PillRadius = 0.35f, ShotRadius = 0.25f;

        public static Projectile PlayerShotTouching(Vector2 centre, float radius)
        {
            var all = StaticReferenceManager.AllProjectiles;
            if (all == null) return null;
            float dt = BraveTime.DeltaTime;
            foreach (Projectile shot in all)
            {
                if (shot == null || !shot.isActiveAndEnabled || !(shot.Owner is PlayerController)) continue;
                Vector2 b = shot.specRigidbody != null ? shot.specRigidbody.UnitCenter : (Vector2)shot.transform.position;
                Vector2 a = b - shot.Direction.normalized * shot.Speed * dt;
                if (PillContract.SegmentHits(a.x - centre.x, a.y - centre.y, b.x - centre.x, b.y - centre.y, radius, ShotRadius)) return shot;
            }
            return null;
        }
    }
}
