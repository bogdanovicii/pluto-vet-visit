using System;

namespace PlutoVetVisit
{
    // Engine-independent readability math (tools/tests/test_vet_brain.py runs this file with mono): where a ring or wall opens
    // its gap, how an attack family's preparation cue is timed, and the projectile countdown / release / expiry pulses.
    // No UnityEngine here; VetAttacks.cs and VetAttackBrain.cs apply the results with existing clips, tints and effects.

    /// <summary>Ring and wall openings scored against the real arena: an opening facing a wall, the table or a lingering cloud,
    /// or one Pluto cannot reach before the bullets arrive, is not a safe route.</summary>
    public static class GapScorer
    {
        /// <summary>Tiles Pluto walks around the Vet to move angleDegrees at radius tiles.</summary>
        public static float ArcTiles(float angleDegrees, float radius)
        {
            return (float)(Math.Abs(angleDegrees) * Math.PI / 180.0) * Math.Max(0f, radius);
        }

        /// <summary>How far Pluto can walk before a pattern leaving the Vet reaches him.</summary>
        public static float Reach(float playerDistance, float bulletSpeed, float leadSeconds, float playerSpeed)
        {
            return playerSpeed * (Math.Max(0f, playerDistance) / Math.Max(0.1f, bulletSpeed) + Math.Max(0f, leadSeconds));
        }

        /// <summary>Open floor an opening needs along its direction: out to Pluto's radius (capped) plus room to stand in it.</summary>
        public static float Need(float playerDistance) { return Math.Min(Math.Max(0f, playerDistance), 6f) + 1.5f; }

        /// <summary>-1 when unreachable; otherwise the open fraction of the needed lane (0..1) minus a small travel penalty.</summary>
        public static float Score(float clearance, float need, float arcDegrees, float playerDistance, float reach)
        {
            float arc = ArcTiles(arcDegrees, playerDistance);
            if (arc > reach + 1e-4f) return -1f;
            float open = Math.Min(1f, Math.Max(0f, clearance) / Math.Max(0.1f, need));
            return open - 0.25f * arc / Math.Max(0.001f, reach);
        }

        /// <summary>Picks uniformly (random01 in [0, 1]) among candidates within tolerance of the best score; -1 when empty.
        /// Keeps the pattern unpredictable while never choosing a clearly worse opening.</summary>
        public static int Pick(float[] scores, float random01, float tolerance)
        {
            if (scores == null || scores.Length == 0) return -1;
            float best = float.NegativeInfinity;
            foreach (float s in scores) best = Math.Max(best, s);
            int count = 0;
            foreach (float s in scores) if (s >= best - tolerance) count++;
            int k = Math.Min(count - 1, Math.Max(0, (int)(random01 * count)));
            for (int i = 0; i < scores.Length; i++)
                if (scores[i] >= best - tolerance && k-- == 0) return i;
            return -1;
        }
    }

    public enum CueStyle { None, Glint, Steady, Alternate, DoubleBlink }

    /// <summary>The tint rhythm on the attacker while a family prepares, on top of the existing tell / mask_tell clip.
    /// Phase 0 = no tint, 1 = the family colour, 2 = the secondary colour (pill: white).</summary>
    public static class CueSchedule
    {
        public static CueStyle StyleFor(AttackFamily family)
        {
            switch (family)
            {
                case AttackFamily.Booster: return CueStyle.Glint;        // aim commitment: a short glint
                case AttackFamily.Hop: return CueStyle.Glint;
                case AttackFamily.Pill: return CueStyle.Alternate;       // red and white, the capsule
                case AttackFamily.Stitches: return CueStyle.DoubleBlink; // the release rhythm
                case AttackFamily.None: return CueStyle.None;
                default: return CueStyle.Steady;                         // spray, walls, rings, spiral, clouds, leap, full course
            }
        }

        public static float Duration(CueStyle style)
        {
            switch (style)
            {
                case CueStyle.Glint: return 0.15f;
                case CueStyle.Steady: return 0.45f;
                case CueStyle.Alternate: return 0.5f;
                case CueStyle.DoubleBlink: return 0.5f;
                default: return 0f;
            }
        }

        public static int Phase(CueStyle style, float t)
        {
            if (t < 0f || t >= Duration(style)) return 0;
            switch (style)
            {
                case CueStyle.Glint:
                case CueStyle.Steady: return 1;
                case CueStyle.Alternate: return ((int)(t / 0.1f)) % 2 == 0 ? 1 : 2;
                case CueStyle.DoubleBlink: return (t < 0.12f || (t >= 0.24f && t < 0.36f)) ? 1 : 0;
                default: return 0;
            }
        }
    }

    /// <summary>Frame-based projectile cues (bullet scripts tick at 60 frames per second).</summary>
    public static class FusePulse
    {
        /// <summary>Pill countdown: in the last window frames, on for the first half of every period.</summary>
        public static bool Flash(int framesLeft, int window, int period)
        {
            if (framesLeft <= 0 || framesLeft > window || period <= 1) return false;
            return (window - framesLeft) % period < period / 2;
        }

        /// <summary>Stitch release: a scale pop that decays from peak to 1 over length frames.</summary>
        public static float Pop(int framesSince, int length, float peak)
        {
            if (framesSince < 0 || framesSince >= length || length <= 0) return 1f;
            return 1f + (peak - 1f) * (1f - (float)framesSince / length);
        }

        /// <summary>Cloud expiry: steady until the last window frames, then a blink that stays visible most of the time
        /// (the cloud still hurts while it blinks).</summary>
        public static bool Visible(int framesLeft, int window, int onFrames, int offFrames)
        {
            if (framesLeft > window || framesLeft <= 0) return true;
            return (window - framesLeft) % Math.Max(1, onFrames + offFrames) < onFrames;
        }
    }

    public enum PillEnd { Fuse, PlayerShot, Destroyed }

    /// <summary>The pill contract. A pill bursts into its tablets when its fuse runs out, when a player shot touches it, or when it
    /// is destroyed by hitting something; never when the destruction forbids spawns (blanks, the boss dying, the encounter
    /// retiring its hazards), so clearing a pill never creates replacement hazards.</summary>
    public static class PillContract
    {
        public static bool Bursts(PillEnd end, bool preventSpawningProjectiles) { return !preventSpawningProjectiles; }

        /// <summary>dx, dy: shot centre minus pill centre in tiles; circles of the two radii touch.</summary>
        public static bool ShotHits(float dx, float dy, float pillRadius, float shotRadius)
        {
            float r = pillRadius + shotRadius;
            return dx * dx + dy * dy <= r * r + 1e-5f;
        }

        /// <summary>The shot moved from a to b (relative to the pill centre) this frame: does that segment pass within reach?</summary>
        public static bool SegmentHits(float ax, float ay, float bx, float by, float pillRadius, float shotRadius)
        {
            float vx = bx - ax, vy = by - ay, len2 = vx * vx + vy * vy;
            float t = len2 <= 1e-8f ? 0f : Math.Max(0f, Math.Min(1f, -(ax * vx + ay * vy) / len2));
            return ShotHits(ax + vx * t, ay + vy * t, pillRadius, shotRadius);
        }
    }
}
