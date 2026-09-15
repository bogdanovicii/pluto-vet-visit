using System;

namespace PlutoVetVisit
{
    // Engine-independent movement decisions for the Vet (tools/tests/test_vet_movement.py runs this file with mono). No UnityEngine
    // here: callers pass positions in tiles and times in seconds; VetMovementBehavior.cs asks the floor and issues the paths.
    //
    // Why it exists (0.14.3 "he stays stuck"): the Vet moved with SeekTargetBehavior (stop inside 10 tiles) followed by
    // MoveErraticallyBehavior. Inside 10 tiles SeekTargetBehavior calls AIActor.ClearPath() on every speculator tick (0.1 s) and
    // returns Continue, while MoveErraticallyBehavior only issues a path every PathInterval (0.5 s); the next tick clears that path,
    // PathComplete reads true, and MoveErratically takes it as "point reached" and pauses. In range he walked about 0.1 s in every
    // 0.5-0.75 s. Only the hops and attacks moved him, so the combat pass (crouch before hops, landing pause, recovery and budget
    // windows) left long stretches of a Vet standing still. One behaviour now owns movement and never clears its own path.

    public enum MoveKind { Hold, PathTo }

    public struct MoveOrder
    {
        public MoveKind Kind;
        public float X, Y;
        public string Reason;

        public static MoveOrder Hold(string reason) { return new MoveOrder { Kind = MoveKind.Hold, Reason = reason }; }
        public static MoveOrder PathTo(float x, float y, string reason) { return new MoveOrder { Kind = MoveKind.PathTo, X = x, Y = y, Reason = reason }; }
    }

    /// <summary>Can the Vet stand at (x, y) (floor he can path to, in the theatre, not inside a lingering cloud)? seesTarget: a
    /// clear line from there to Pluto.</summary>
    public delegate bool SpotCheck(float x, float y, out bool seesTarget);

    /// <summary>Strafes around the target at a preferred distance: each leg is a point on the ring around Pluto a little further
    /// along the current orbit direction, clamped into the band, kept off the operating-table group. A new leg starts when he
    /// arrives, when his path ends (an attack cleared it), when a leg runs long, when he has no line to Pluto, when the target has
    /// left the band, or when he has not moved for IdleLimit (then the orbit turns round). Never more than IdleLimit without a new
    /// order while he can move at all.</summary>
    public sealed class OrbitPlanner
    {
        public readonly float PreferredMin, PreferredMax, IdleLimit;
        public float AnchorX, AnchorY, AnchorKeepOut;
        public bool HasAnchor;
        public float LegSeconds = 2.2f, ArriveDistance = 0.6f, ProgressStep = 0.2f, MinLeg = 1.5f, EscapeDistance = 2.5f;

        public int OrbitSign { get; private set; }
        public int Legs, Stalls, Rejections, Boxed;
        public string LastReason = "none";

        private static readonly float[] Steps = { 45f, 70f, 25f, 100f };
        private bool hasDest, sampled;
        private float destX, destY, legStart, lastProgress, sampleX, sampleY;

        public OrbitPlanner(float preferredMin, float preferredMax, float idleLimit)
        {
            if (!(preferredMin > 0f && preferredMax > preferredMin && idleLimit > 0f))
                throw new ArgumentException("need 0 < preferredMin < preferredMax and idleLimit > 0");
            PreferredMin = preferredMin; PreferredMax = preferredMax; IdleLimit = idleLimit;
            OrbitSign = 1;
        }

        public bool HasDestination { get { return hasDest; } }
        public float DestinationX { get { return destX; } }
        public float DestinationY { get { return destY; } }

        /// <summary>Seconds since the Vet last moved ProgressStep tiles (0 before the first tick).</summary>
        public float IdleFor(float now) { return sampled ? Math.Max(0f, now - lastProgress) : 0f; }

        public MoveOrder Tick(float now, float x, float y, float tx, float ty, bool pathComplete, bool hasLine, SpotCheck check)
        {
            if (!sampled || Dist(x, y, sampleX, sampleY) >= ProgressStep)
            {
                sampled = true;
                sampleX = x; sampleY = y;
                lastProgress = now;
            }
            string reason = Reason(now, x, y, tx, ty, pathComplete, hasLine);
            if (reason == null) return MoveOrder.Hold("following");
            if (reason == "stalled")
            {
                Stalls++;
                OrbitSign = -OrbitSign;   // something is in the way on this side: go round the other way
            }
            LastReason = reason;
            float px, py;
            if (check == null || !Choose(x, y, tx, ty, hasLine, check, out px, out py))
            {
                Boxed++;
                hasDest = false;   // retried on the next tick
                return MoveOrder.Hold("boxed");
            }
            hasDest = true;
            destX = px; destY = py;
            legStart = now;
            Legs++;
            return MoveOrder.PathTo(px, py, reason);
        }

        /// <summary>The engine could not path to the last order: forget it and turn the orbit round; the next tick picks again.</summary>
        public void Rejected()
        {
            Rejections++;
            hasDest = false;
            OrbitSign = -OrbitSign;
        }

        private string Reason(float now, float x, float y, float tx, float ty, bool pathComplete, bool hasLine)
        {
            if (!hasDest) return "start";
            float leg = now - legStart;
            if (now - lastProgress >= IdleLimit && leg >= IdleLimit * 0.5f) return "stalled";
            if (Dist(x, y, destX, destY) <= ArriveDistance) return "arrived";
            if (pathComplete && leg >= 0.3f) return "arrived";   // the path ended early or an attack cleared it
            if (leg >= LegSeconds) return "leg";
            if (!hasLine && leg >= 0.6f) return "no line";
            float d = Dist(x, y, tx, ty), dd = Dist(destX, destY, tx, ty);
            if ((d < PreferredMin - 1.5f && dd < PreferredMin) || (d > PreferredMax + 3f && dd > PreferredMax + 1f)) return "range";
            return null;
        }

        private bool Choose(float x, float y, float tx, float ty, bool hasLine, SpotCheck check, out float bestX, out float bestY)
        {
            bestX = bestY = 0f;
            float d = Dist(x, y, tx, ty);
            float bearing = (float)(Math.Atan2(y - ty, x - tx) * 180.0 / Math.PI);
            float r = Math.Min(PreferredMax, Math.Max(PreferredMin, d));
            float mid = (PreferredMin + PreferredMax) / 2f;
            float best = float.NegativeInfinity;
            int bestSign = OrbitSign;
            int[] signs = { OrbitSign, -OrbitSign };
            float[] radii = { r, mid };
            foreach (int sign in signs)
                foreach (float step in Steps)
                    foreach (float radius in radii)
                    {
                        double a = (bearing + sign * step) * Math.PI / 180.0;
                        float px = tx + radius * (float)Math.Cos(a), py = ty + radius * (float)Math.Sin(a);
                        if (Dist(px, py, x, y) < MinLeg) continue;
                        if (HasAnchor && Dist(px, py, AnchorX, AnchorY) < AnchorKeepOut) continue;
                        bool sees;
                        if (!check(px, py, out sees)) continue;
                        float score = (sign == OrbitSign ? 1f : 0f) + (sees ? (hasLine ? 1f : 3f) : 0f) - step / 200f - Math.Abs(radius - mid) * 0.1f;
                        if (score > best) { best = score; bestX = px; bestY = py; bestSign = sign; }
                    }
            if (best > float.NegativeInfinity)
            {
                OrbitSign = bestSign;
                return true;
            }
            // Nothing on the ring (a corner, the table, clouds): step away in whichever direction keeps him closest to the band.
            for (int k = 0; k < 8; k++)
            {
                double a = k * Math.PI / 4.0;
                float px = x + EscapeDistance * (float)Math.Cos(a), py = y + EscapeDistance * (float)Math.Sin(a);
                bool sees;
                if (!check(px, py, out sees)) continue;
                float score = -Math.Abs(Dist(px, py, tx, ty) - mid) + (sees ? 0.5f : 0f);
                if (score > best) { best = score; bestX = px; bestY = py; }
            }
            return best > float.NegativeInfinity;
        }

        private static float Dist(float ax, float ay, float bx, float by)
        {
            float dx = ax - bx, dy = ay - by;
            return (float)Math.Sqrt(dx * dx + dy * dy);
        }
    }
}
