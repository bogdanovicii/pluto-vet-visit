using System.Collections.Generic;

namespace PlutoVetVisit
{
    /// <summary>Owns encounter actors even after death, until their remaining projectiles have been retired.</summary>
    public sealed class EncounterRoster<T> where T : class
    {
        private readonly List<T> actors = new List<T>();
        public bool IsEnded { get; private set; }

        public bool Track(T actor)
        {
            if (IsEnded || actor == null || actors.Contains(actor)) return false;
            actors.Add(actor);
            return true;
        }

        public bool Contains(T actor) { return actors.Contains(actor); }
        public List<T> Snapshot() { return new List<T>(actors); }

        public bool End()
        {
            if (IsEnded) return false;
            IsEnded = true;
            return true;
        }
    }
}
