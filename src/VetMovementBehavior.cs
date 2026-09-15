using System;
using Dungeonator;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>The Vet's only movement behaviour: OrbitPlanner (MovementPlanner.cs) decides, this issues the paths. It replaces
    /// SeekTargetBehavior + MoveErraticallyBehavior, whose ClearPath-every-tick conflict kept him standing still inside 10 tiles.
    /// Config fields are public so the BehaviorSpeculator serializer copies them to every spawned Vet; the planner is private
    /// running state and starts fresh. Attacks still stop him (ShootBehavior clears the path and the speculator runs no movement
    /// during a pattern); the planner starts a new leg as soon as movement ticks again.</summary>
    public class OrbitTargetBehavior : MovementBehaviorBase
    {
        public float PreferredMin = 5.5f, PreferredMax = 9f, IdleLimit = 0.8f;
        /// <summary>The operating-table group in room cells (ClinicLayout.Table) and how far legs stay from its centre.</summary>
        public float AnchorCellX, AnchorCellY, AnchorKeepOut = 2.5f;
        /// <summary>Legs stay above this room row (ClinicLayout.THEATRE_MIN_Y): the Vet never walks out through the theatre door.</summary>
        public float MinCellY = -1f;
        public float CloudRadius = 1.1f;
        public const float LogEvery = 4f;

        private OrbitPlanner planner;
        private float nextLog;
        private int loggedLegs, loggedStalls, loggedRejected, loggedBoxed;
        private static bool loggedFailure;

        public override float DesiredCombatDistance { get { return PreferredMax; } }

        private Vector2 RoomOrigin()
        {
            if (VetVisitController.Instance != null) return VetVisitController.Instance.World(Vector2.zero);
            RoomHandler room = m_aiActor != null ? m_aiActor.ParentRoom : null;
            return room != null ? room.area.basePosition.ToVector2() : Vector2.zero;
        }

        private OrbitPlanner Planner
        {
            get
            {
                if (planner == null)
                {
                    Vector2 anchor = RoomOrigin() + new Vector2(AnchorCellX, AnchorCellY);
                    planner = new OrbitPlanner(PreferredMin, PreferredMax, IdleLimit)
                    {
                        HasAnchor = AnchorKeepOut > 0f, AnchorX = anchor.x, AnchorY = anchor.y, AnchorKeepOut = AnchorKeepOut,
                    };
                }
                return planner;
            }
        }

        public override BehaviorResult Update()
        {
            BehaviorResult result = base.Update();
            if (result != BehaviorResult.Continue) return result;
            SpeculativeRigidbody target = m_aiActor != null ? m_aiActor.TargetRigidbody : null;
            if (target == null || m_aiActor.specRigidbody == null) return BehaviorResult.Continue;
            try
            {
                float now = Time.time;
                Vector2 pos = m_aiActor.specRigidbody.UnitCenter, t = target.UnitCenter;
                OrbitPlanner p = Planner;
                MoveOrder order = p.Tick(now, pos.x, pos.y, t.x, t.y, m_aiActor.PathComplete, m_aiActor.HasLineOfSightToTarget, Spot);
                if (order.Kind == MoveKind.PathTo && !m_aiActor.PathfindToPosition(new Vector2(order.X, order.Y))) p.Rejected();
                if (now >= nextLog) Report(p, now, pos, t);
            }
            catch (Exception e)
            {
                if (!loggedFailure) { loggedFailure = true; PastPlugin.Log("vet move threw (he stands until the next tick): " + e); }
                return BehaviorResult.Continue;
            }
            return BehaviorResult.SkipRemainingClassBehaviors;
        }

        /// <summary>Floor the Vet can stand and path on, inside his room and the theatre, clear of lingering clouds.</summary>
        private bool Spot(float x, float y, out bool seesTarget)
        {
            seesTarget = false;
            Vector2 point = new Vector2(x, y);
            if (MinCellY >= 0f && y < RoomOrigin().y + MinCellY + 0.5f) return false;
            Dungeon dungeon = GameManager.Instance != null ? GameManager.Instance.Dungeon : null;
            if (dungeon == null || dungeon.data == null) return false;
            IntVector2 cell = point.ToIntVector2(VectorConversions.Floor);
            if (!dungeon.data.CheckInBoundsAndValid(cell)) return false;
            CellData data = dungeon.data[cell];
            if (data == null || data.isExitCell || data.parentRoom != m_aiActor.ParentRoom) return false;
            if (Pathfinding.Pathfinder.Instance == null || !Pathfinding.Pathfinder.Instance.IsPassable(cell, m_aiActor.Clearance, m_aiActor.PathableTiles)) return false;
            if (LingeringHazards.Blocks(point, CloudRadius)) return false;
            SpeculativeRigidbody target = m_aiActor.TargetRigidbody;
            if (target != null)
            {
                Vector2 to = target.UnitCenter - point;
                RaycastResult hit;
                int mask = CollisionMask.LayerToMask(CollisionLayer.HighObstacle, CollisionLayer.BulletBlocker);
                bool blocked = PhysicsEngine.Instance.Raycast(point, to, to.magnitude, out hit, true, true, mask, null, false, null, m_aiActor.specRigidbody);
                RaycastResult.Pool.Free(ref hit);
                seesTarget = !blocked;
            }
            return true;
        }

        /// <summary>One throttled line per LogEvery seconds while he fights: what the planner did since the last line.</summary>
        private void Report(OrbitPlanner p, float now, Vector2 pos, Vector2 target)
        {
            nextLog = now + LogEvery;
            PastPlugin.Log("vet move: legs +" + (p.Legs - loggedLegs) + ", stalls +" + (p.Stalls - loggedStalls) + ", rejected +" + (p.Rejections - loggedRejected)
                + ", boxed +" + (p.Boxed - loggedBoxed) + ", last '" + p.LastReason + "', dist " + Vector2.Distance(pos, target).ToString("0.0")
                + ", idle " + p.IdleFor(now).ToString("0.0") + " s, orbit " + (p.OrbitSign > 0 ? "ccw" : "cw")
                + ", @" + (pos - RoomOrigin()).ToString() + (p.HasDestination ? " -> " + (new Vector2(p.DestinationX, p.DestinationY) - RoomOrigin()).ToString() : ""));
            loggedLegs = p.Legs; loggedStalls = p.Stalls; loggedRejected = p.Rejections; loggedBoxed = p.Boxed;
        }
    }
}
