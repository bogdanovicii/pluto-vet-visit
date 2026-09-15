using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Brave.BulletScript;

namespace PlutoVetVisit
{
    public partial class VetVisitController
    {
        private readonly Dictionary<AIActor, SpeculativeRigidbody> fallbackTargets = new Dictionary<AIActor, SpeculativeRigidbody>();

        private void ClearFallbackTargets()
        {
            foreach (var pair in fallbackTargets)
                if (pair.Key != null && pair.Key.OverrideTarget == pair.Value) pair.Key.OverrideTarget = null;
            fallbackTargets.Clear();
        }

        private static PlayerController LivingPlayer()
        {
            if (GameManager.Instance == null) return null;
            foreach (PlayerController p in GameManager.Instance.AllPlayers)
                if (p != null && p.healthHaver != null && !p.healthHaver.IsDead) return p;
            return null;
        }

        private IEnumerator ReleaseFallbackTarget(AIActor actor, SpeculativeRigidbody target)
        {
            yield return new WaitForSeconds(1f);
            if (actor != null && actor.OverrideTarget == target) actor.OverrideTarget = null;
            if (!ReferenceEquals(actor, null)) fallbackTargets.Remove(actor);
        }

        private static void RetireActor(AIActor actor)
        {
            if (actor == null) return;
            try
            {
                if (actor.behaviorSpeculator != null)
                {
                    actor.behaviorSpeculator.Interrupt();
                    actor.behaviorSpeculator.enabled = false;
                }
                foreach (BulletScriptSource source in actor.GetComponentsInChildren<BulletScriptSource>()) source.ForceStop();
                actor.EraseFromExistence(true);
            }
            catch (Exception e) { PastPlugin.Log("encounter retirement: " + e.Message); }
        }

        /// <summary>Stop producers before removing bullets, with child spawning suppressed. Friendly shots are untouched.</summary>
        private void StopCombat()
        {
            ClearFallbackTargets();
            List<AIActor> actors = encounter.Snapshot();
            foreach (AIActor actor in actors)
            {
                if (actor == null) continue;
                try
                {
                    if (actor.behaviorSpeculator != null)
                    {
                        actor.behaviorSpeculator.Interrupt();
                        actor.behaviorSpeculator.enabled = false;
                    }
                    foreach (BulletScriptSource source in actor.GetComponentsInChildren<BulletScriptSource>()) source.ForceStop();
                }
                catch (Exception e) { PastPlugin.Log("stop attack: " + e.Message); }
            }
            var shots = StaticReferenceManager.AllProjectiles != null ? new List<Projectile>(StaticReferenceManager.AllProjectiles) : null;
            if (shots != null)
                for (int i = shots.Count - 1; i >= 0; i--)
                {
                    Projectile shot = shots[i];
                    if (shot == null || shot.Owner is PlayerController) continue;
                    AIActor owner = shot.Owner as AIActor;
                    if (ReferenceEquals(owner, null) || !encounter.Contains(owner)) continue;
                    shot.DieInAir(true, false, false, true);
                }
            foreach (AIActor actor in actors)
                if (actor != null && actor != vet) RetireActor(actor);
        }

        private void OnDestroy()
        {
            ending = true;
            encounter.End();
            ClearFallbackTargets();
            if (GameManager.HasInstance)
            {
                // No global override or time-scale resets: release only state owned by this controller.
                if (cutscene)
                    foreach (PlayerController p in GameManager.Instance.AllPlayers)
                        if (p != null) p.ClearInputOverride("past");
                BraveTime.ClearMultiplier(gameObject);
            }
            if (Instance == this) Instance = null;
        }
    }
}
