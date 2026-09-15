namespace PlutoVetVisit
{
    /// <summary>
    /// Decides when the loadout watchdog may escalate to the broad emergency repair on its own.
    /// Foreign locks are respected at first; only a "cannot fire" state that persists for several
    /// consecutive checks, with no legitimate reason in sight, earns the repair (the 0.10.0 in-game bug).
    /// </summary>
    public sealed class StuckControlPolicy
    {
        public const int TicksBeforeRepair = 3;   // watchdog checks every 3 s, so about 9 s stuck
        private readonly int[] stuckTicks = new int[2];

        /// <summary>Record one watchdog check for player slot 0 or 1; true when the emergency repair should run now.</summary>
        public bool Observe(int slot, bool cannotFire, bool excused)
        {
            if (slot < 0 || slot >= stuckTicks.Length) return false;
            if (!cannotFire || excused) { stuckTicks[slot] = 0; return false; }
            if (++stuckTicks[slot] < TicksBeforeRepair) return false;
            stuckTicks[slot] = 0;
            return true;
        }

        public int StuckTicks(int slot) { return slot >= 0 && slot < stuckTicks.Length ? stuckTicks[slot] : 0; }
        public void Reset() { stuckTicks[0] = 0; stuckTicks[1] = 0; }
    }
}
