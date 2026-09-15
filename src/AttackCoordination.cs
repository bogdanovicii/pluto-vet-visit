using System;
using System.Collections.Generic;

namespace PlutoVetVisit
{
    // Engine-independent attack selection for the Vet, the Nurse and the Techs (tools/tests/test_vet_brain.py runs this file
    // with mono). No UnityEngine here: callers pass distances in tiles and times in seconds. VetAttackBrain.cs is the wiring.

    /// <summary>Threat families the player learns to read; each has one preparation cue (ThreatReadability.CueSchedule).</summary>
    public enum AttackFamily { None, Booster, Spray, Pill, Ring, Spiral, Wall, Stitches, Anesthesia, Hop, Leap, Course }

    [Flags]
    public enum RangeBand { None = 0, Close = 1, Mid = 2, Far = 4, Any = 7 }

    /// <summary>Close / mid / far with separate enter and exit distances, so an attack gated on range does not flicker on and off
    /// while Pluto hovers on a boundary (the old MinRange 4 / Range 8 gates did).</summary>
    public sealed class DistanceBand
    {
        private readonly float closeEnter, closeExit, farEnter, farExit;
        public RangeBand Current { get; private set; }

        public DistanceBand(float closeEnter, float closeExit, float farEnter, float farExit)
        {
            if (!(closeEnter < closeExit && closeExit <= farExit && farExit < farEnter))
                throw new ArgumentException("need closeEnter < closeExit <= farExit < farEnter");
            this.closeEnter = closeEnter; this.closeExit = closeExit; this.farEnter = farEnter; this.farExit = farExit;
            Current = RangeBand.Mid;
        }

        public RangeBand Update(float distance)
        {
            if (distance < closeEnter) Current = RangeBand.Close;
            else if (distance > farEnter) Current = RangeBand.Far;
            else if (Current == RangeBand.Close && distance > closeExit) Current = distance > farEnter ? RangeBand.Far : RangeBand.Mid;
            else if (Current == RangeBand.Far && distance < farExit) Current = distance < closeEnter ? RangeBand.Close : RangeBand.Mid;
            return Current;
        }
    }

    /// <summary>The same family never runs back to back: blocked while it runs and for a window after it ends.</summary>
    public sealed class RepeatGuard
    {
        private readonly float window;
        private AttackFamily last = AttackFamily.None;
        private bool running;
        private float endedAt = float.NegativeInfinity;

        public RepeatGuard(float window) { this.window = window; }

        public void Started(AttackFamily family) { last = family; running = true; }

        public void Ended(AttackFamily family, float now)
        {
            if (family != last) return;
            running = false;
            endedAt = now;
        }

        public bool Allows(AttackFamily family, float now)
        {
            if (family == AttackFamily.None || family != last) return true;
            return !running && now >= endedAt + window - 1e-4f;
        }
    }

    /// <summary>A breather after a heavy pattern: only light attacks until it runs out. A new recovery never shortens a longer one.</summary>
    public sealed class RecoveryTimer
    {
        private float until = float.NegativeInfinity;

        public void Begin(float now, float seconds) { until = Math.Max(until, now + seconds); }
        public bool Active(float now) { return now < until - 1e-4f; }
        public float Remaining(float now) { return Math.Max(0f, until - now); }
    }

    /// <summary>Simultaneous threat shared by every coordinated actor in the encounter. Each owner holds at most one token (cost,
    /// live until). A new pattern waits while the live load plus its cost exceeds the capacity; an empty board always admits one,
    /// so an oversized pattern can never deadlock.</summary>
    public sealed class ThreatBudget
    {
        private struct Token { public float Cost, Until; }

        private readonly float capacity;
        private readonly Dictionary<int, Token> tokens = new Dictionary<int, Token>();

        public ThreatBudget(float capacity) { this.capacity = capacity; }

        public float Load(float now)
        {
            float sum = 0f;
            foreach (Token t in tokens.Values) if (t.Until > now + 1e-4f) sum += t.Cost;
            return sum;
        }

        public bool CanAfford(float cost, float now)
        {
            if (cost <= 0f) return true;
            float load = Load(now);
            return load <= 1e-4f || load + cost <= capacity + 1e-4f;
        }

        public bool Acquire(int owner, float cost, float now, float until)
        {
            Token prior;
            bool had = tokens.TryGetValue(owner, out prior);
            if (had) tokens.Remove(owner);   // one token per owner: its own replaced pattern does not count against it
            if (!CanAfford(cost, now))
            {
                if (had) tokens[owner] = prior;
                return false;
            }
            tokens[owner] = new Token { Cost = cost, Until = until };
            return true;
        }

        /// <summary>The pattern's script ended: its bullets stay dangerous for linger seconds more.</summary>
        public void Settle(int owner, float now, float linger)
        {
            Token t;
            if (!tokens.TryGetValue(owner, out t)) return;
            t.Until = now + Math.Max(0f, linger);
            tokens[owner] = t;
        }

        public void ReleaseOwner(int owner) { tokens.Remove(owner); }
        public void Clear() { tokens.Clear(); }
    }

    /// <summary>One coordinated attack: its family, threat cost, how long its bullets linger after the script ends, the breather
    /// it earns and the distance bands it may start from.</summary>
    public struct AttackPlan
    {
        public AttackFamily Family;
        public float Cost, Linger, Recovery;
        public RangeBand Bands;

        public AttackPlan(AttackFamily family, float cost, float linger, float recovery, RangeBand bands)
        {
            Family = family; Cost = cost; Linger = linger; Recovery = recovery; Bands = bands;
        }

        public bool IsHeavy { get { return Cost >= AttackCoordinator.HeavyCost; } }

        /// <summary>Hops reposition the Vet: they are movement, not a threat family. The repeat guard never blocks them (a blocked
        /// hop is a Vet standing still, and it cancelled DashBehavior's double hop) and a hop never overwrites the guard's memory
        /// of the last real attack (booster, hop, booster would otherwise pass).</summary>
        public bool IsMovement { get { return Family == AttackFamily.Hop; } }
    }

    /// <summary>Per-actor selection policy: range band, repeat avoidance, recovery after heavy patterns, shared threat budget.</summary>
    public sealed class AttackCoordinator
    {
        public const float HeavyCost = 2f;
        /// <summary>A token is never held longer than this past its expected end, even if the end notification is lost.</summary>
        public const float SafetySeconds = 6f;

        private readonly DistanceBand band;
        private readonly RepeatGuard repeat;
        private readonly RecoveryTimer recovery = new RecoveryTimer();
        private readonly ThreatBudget shared;
        private readonly int owner;
        private bool running;
        private AttackFamily runningFamily;
        private float giveUpAt;

        public AttackCoordinator(DistanceBand band, RepeatGuard repeat, ThreatBudget shared, int owner)
        {
            this.band = band; this.repeat = repeat; this.shared = shared; this.owner = owner;
        }

        /// <summary>Null when the plan may start now, otherwise the reason ("band", "repeat", "recovery", "budget").
        /// A negative distance means no target: the band does not veto (RequiresTarget already does).</summary>
        public string Veto(AttackPlan plan, float distance, float now)
        {
            if (running && now > giveUpAt)
            {
                running = false;   // the end notification was lost (an interrupt): never block that family forever
                repeat.Ended(runningFamily, giveUpAt);
            }
            string reason = null;
            if (distance >= 0f && (band.Update(distance) & plan.Bands) == 0) reason = "band";
            else if (!plan.IsMovement && !repeat.Allows(plan.Family, now)) reason = "repeat";
            else if (plan.IsHeavy && recovery.Active(now)) reason = "recovery";
            else if (shared != null && !shared.CanAfford(plan.Cost, now)) reason = "budget";
            Count(reason);
            return reason;
        }

        // Diagnostics: how often each gate said no since the last summary (IsReady asks several times a tick, so read the
        // proportions, not the absolute numbers).
        private int vetoBand, vetoRepeat, vetoRecovery, vetoBudget, allowed, starts;

        private void Count(string reason)
        {
            if (reason == null) allowed++;
            else if (reason == "band") vetoBand++;
            else if (reason == "repeat") vetoRepeat++;
            else if (reason == "recovery") vetoRecovery++;
            else vetoBudget++;
        }

        /// <summary>"asked N: allowed a, band b, repeat r, recovery c, budget d; started s" since the last call, then resets;
        /// null when nothing was asked.</summary>
        public string DrainSummary()
        {
            int asked = allowed + vetoBand + vetoRepeat + vetoRecovery + vetoBudget;
            if (asked == 0 && starts == 0) return null;
            string s = "asked " + asked + ": allowed " + allowed + ", band " + vetoBand + ", repeat " + vetoRepeat + ", recovery " + vetoRecovery
                + ", budget " + vetoBudget + "; started " + starts;
            allowed = vetoBand = vetoRepeat = vetoRecovery = vetoBudget = starts = 0;
            return s;
        }

        public void Started(AttackPlan plan, float now, float expectedSeconds)
        {
            starts++;
            if (plan.IsMovement) return;   // hops: no repeat memory, no budget, no recovery
            repeat.Started(plan.Family);
            running = true;
            runningFamily = plan.Family;
            giveUpAt = now + Math.Max(0f, expectedSeconds) + SafetySeconds;
            if (shared != null && plan.Cost > 0f)
                shared.Acquire(owner, plan.Cost, now, now + Math.Max(0f, expectedSeconds) + plan.Linger + SafetySeconds);
        }

        public void Ended(AttackPlan plan, float now)
        {
            if (plan.IsMovement) return;
            running = false;
            repeat.Ended(plan.Family, now);
            if (shared != null && plan.Cost > 0f) shared.Settle(owner, now, plan.Linger);
            if (plan.Recovery > 0f) recovery.Begin(now, plan.Recovery);
        }

        public void Forget() { if (shared != null) shared.ReleaseOwner(owner); }
    }
}
