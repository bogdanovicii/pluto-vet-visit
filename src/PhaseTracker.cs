using System;

namespace PlutoVetVisit
{
    // Engine-independent fight phases (tools/tests/test_vet_movement.py runs this file with mono). VetReinforcements (VetBoss.cs)
    // feeds it from HealthHaver.OnDamaged and from a 0.25 s health poll, so a damage path that never raises OnDamaged still
    // reaches the last phase; each event fires exactly once whichever source sees it first.

    [Flags]
    public enum PhaseEvent { None = 0, PhaseTwo = 1, Reinforcements = 2, LastPhase = 4 }

    public sealed class PhaseTracker
    {
        public const float PhaseTwoAt = 0.6f, ReinforcementsAt = 0.5f, LastPhaseAt = 0.25f;

        private PhaseEvent fired;

        public PhaseEvent Fired { get { return fired; } }

        /// <summary>The events newly reached at current / max health. A big hit can cross several thresholds at once. Nothing fires
        /// for a dead or invalid reading: a killing blow from above 25 % goes to the death flow, not to the red room and the last
        /// reinforcements.</summary>
        public PhaseEvent Observe(float current, float max)
        {
            if (!(max > 0f) || !(current > 0f)) return PhaseEvent.None;
            float f = current / max;
            PhaseEvent reached = PhaseEvent.None;
            if (f <= PhaseTwoAt + 1e-4f) reached |= PhaseEvent.PhaseTwo;
            if (f <= ReinforcementsAt + 1e-4f) reached |= PhaseEvent.Reinforcements;
            if (f <= LastPhaseAt + 1e-4f) reached |= PhaseEvent.LastPhase;
            PhaseEvent fresh = reached & ~fired;
            fired |= fresh;
            return fresh;
        }
    }
}
