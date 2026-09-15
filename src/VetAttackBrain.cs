using System;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>
    /// The attack brain on the Vet and the Nurse: the engine side of AttackCoordination.cs. AttackBehaviorGroup only picks items
    /// whose IsReady() is true, so the coordinated behaviours below add the policy veto to IsReady (range band with hysteresis,
    /// repeat avoidance, recovery after heavy patterns, the threat budget shared by everyone in the encounter), tell the policy
    /// when a pattern starts and ends, and play the family's preparation cue: a tint rhythm over the existing tell / mask_tell
    /// clip (CueSchedule), the deathray charge for rings and the leap, a purple poof for the anesthesia canister. No new art.
    /// Techs have no brain component: their behaviours stay plain, and a coordinated behaviour without a brain acts as its base.
    /// </summary>
    public class AttackBrain : BraveBehaviour
    {
        /// <summary>Heavy patterns cost 2 (walls, rings, spiral, stitches, clouds, the leap ring), the full course 3, area pressure
        /// (the Vet's spray and pills, the Nurse's hose and IV line) 1: a heavy wall and one area attack fit, two heavy walls wait.</summary>
        public const float ThreatCapacity = 3f;
        public static readonly ThreatBudget SharedBudget = new ThreatBudget(ThreatCapacity);
        private const string CueSource = "pluto_attack_cue";

        public float CloseEnter = 4f, CloseExit = 5.5f, FarEnter = 12f, FarExit = 10f, RepeatWindow = 2f;

        private AttackCoordinator coordinator;
        private CueStyle cueStyle = CueStyle.None;
        private AttackFamily cueFamily = AttackFamily.None;
        private float cueStart;
        private int cuePhase;
        private static bool loggedFailure;

        public static float Now { get { return Time.time; } }

        public static AttackBrain For(AIActor actor) { return actor != null ? actor.GetComponent<AttackBrain>() : null; }

        private AttackCoordinator Coordinator
        {
            get
            {
                if (coordinator == null)
                    coordinator = new AttackCoordinator(new DistanceBand(CloseEnter, CloseExit, FarEnter, FarExit), new RepeatGuard(RepeatWindow), SharedBudget, GetInstanceID());
                return coordinator;
            }
        }

        /// <summary>Tiles from this actor to its target, or -1 without one.</summary>
        private float TargetDistance()
        {
            AIActor a = aiActor;
            SpeculativeRigidbody target = a != null && a.behaviorSpeculator != null ? a.behaviorSpeculator.TargetRigidbody : null;
            return target != null ? Vector2.Distance(a.CenterPosition, target.UnitCenter) : -1f;
        }

        public static bool Allows(AIActor actor, AttackPlan plan)
        {
            AttackBrain brain = For(actor);
            if (brain == null) return true;
            try { return brain.Coordinator.Veto(plan, brain.TargetDistance(), Now) == null; }
            catch (Exception e) { Fail(e); return true; }
        }

        public static void Began(AIActor actor, AttackPlan plan, float expectedSeconds, GameObject at)
        {
            AttackBrain brain = For(actor);
            if (brain == null) return;
            try
            {
                brain.Coordinator.Started(plan, Now, expectedSeconds);
                brain.PlayCue(plan.Family, at != null ? (Vector2)at.transform.position : actor.CenterPosition);
            }
            catch (Exception e) { Fail(e); }
        }

        public static void Finished(AIActor actor, AttackPlan plan)
        {
            AttackBrain brain = For(actor);
            if (brain == null) return;
            try
            {
                brain.Coordinator.Ended(plan, Now);
                brain.StopCue();
            }
            catch (Exception e) { Fail(e); }
        }

        private static void Fail(Exception e)
        {
            if (loggedFailure) return;
            loggedFailure = true;
            PastPlugin.Log("attack brain threw (attacks fall back to their plain behaviour): " + e);
        }

        private void PlayCue(AttackFamily family, Vector2 at)
        {
            StopCue();
            cueFamily = family;
            cueStyle = CueSchedule.StyleFor(family);
            cueStart = Now;
            if (family == AttackFamily.Ring || family == AttackFamily.Leap) ClinicSound.Play("Play_ENM_deathray_charge_01", gameObject);
            if (family == AttackFamily.Anesthesia) LootEngine.DoDefaultPurplePoof(at);   // the canister vents: the clouds are coming
            ApplyCue();
        }

        private void Update()
        {
            if (cueStyle != CueStyle.None) ApplyCue();
        }

        private void ApplyCue()
        {
            float t = Now - cueStart;
            int phase = CueSchedule.Phase(cueStyle, t);
            if (phase != cuePhase && aiActor != null)
            {
                if (cuePhase != 0) aiActor.DeregisterOverrideColor(CueSource);
                if (phase != 0) aiActor.RegisterOverrideColor(CueColor(cueFamily, phase), CueSource);
                cuePhase = phase;
            }
            if (t >= CueSchedule.Duration(cueStyle)) StopCue();
        }

        private void StopCue()
        {
            if (cuePhase != 0 && aiActor != null) aiActor.DeregisterOverrideColor(CueSource);
            cuePhase = 0;
            cueStyle = CueStyle.None;
        }

        /// <summary>Family colours follow the projectile sheet (tools/projectiles.py): steel glint for syringes and hops, teal for
        /// droplets, red and white for the capsule, vaccine blue for rings, suture red, plum for the anesthesia rim. Alpha is the
        /// override-colour blend strength.</summary>
        public static Color CueColor(AttackFamily family, int phase)
        {
            switch (family)
            {
                case AttackFamily.Booster:
                case AttackFamily.Hop: return new Color(1f, 1f, 1f, 0.55f);
                case AttackFamily.Spray:
                case AttackFamily.Wall: return new Color(0.25f, 0.85f, 0.8f, 0.5f);
                case AttackFamily.Pill: return phase == 2 ? new Color(1f, 1f, 1f, 0.5f) : new Color(0.95f, 0.2f, 0.2f, 0.5f);
                case AttackFamily.Stitches: return new Color(0.85f, 0.1f, 0.25f, 0.55f);
                case AttackFamily.Anesthesia: return new Color(0.6f, 0.35f, 0.7f, 0.5f);
                case AttackFamily.Leap: return new Color(0.8f, 0.9f, 1f, 0.5f);
                default: return new Color(0.3f, 0.55f, 1f, 0.5f);   // rings, spiral, the full course
            }
        }

        public override void OnDestroy()
        {
            StopCue();
            if (coordinator != null) coordinator.Forget();
            base.OnDestroy();
        }
    }

    /// <summary>A ShootBehavior with an AttackPlan. Plan fields are public so the BehaviorSpeculator serializer copies them to
    /// every spawned Vet; running state is private and starts fresh.</summary>
    public class CoordinatedShoot : ShootBehavior
    {
        public AttackFamily Family = AttackFamily.None;
        public float ThreatCost, ThreatLinger, Recovery, ExpectedSeconds = 1f;
        public RangeBand Bands = RangeBand.Any;
        private bool running;

        public AttackPlan GetPlan() { return new AttackPlan(Family, ThreatCost, ThreatLinger, Recovery, Bands); }

        public override bool IsReady() { return base.IsReady() && AttackBrain.Allows(m_aiActor, GetPlan()); }

        public override BehaviorResult Update()
        {
            BehaviorResult result = base.Update();
            if (!running && result != BehaviorResult.Continue)
            {
                running = true;
                AttackBrain.Began(m_aiActor, GetPlan(), ExpectedSeconds, ShootPoint);
            }
            return result;
        }

        public override void EndContinuousUpdate()
        {
            base.EndContinuousUpdate();
            Finish();
        }

        public override void OnActorPreDeath()
        {
            Finish();
            base.OnActorPreDeath();
        }

        private void Finish()
        {
            if (!running) return;
            running = false;
            AttackBrain.Finished(m_aiActor, GetPlan());
        }
    }

    /// <summary>A hop with anticipation (VetTech.Hop's chargeAnim plays the tell first) and a landing: the roll-landing dust-up
    /// where he comes down, then the AttackCooldown the builder sets is his recovery before the next pattern.</summary>
    public class CoordinatedHop : DashBehavior
    {
        public AttackFamily Family = AttackFamily.Hop;
        public float ExpectedSeconds = 1f;
        public RangeBand Bands = RangeBand.Any;
        private bool running;

        public AttackPlan GetPlan() { return new AttackPlan(Family, 0f, 0f, 0f, Bands); }

        public override bool IsReady() { return base.IsReady() && AttackBrain.Allows(m_aiActor, GetPlan()); }

        public override BehaviorResult Update()
        {
            BehaviorResult result = base.Update();
            if (!running && result != BehaviorResult.Continue)
            {
                running = true;
                AttackBrain.Began(m_aiActor, GetPlan(), ExpectedSeconds, null);
            }
            return result;
        }

        public override void EndContinuousUpdate()
        {
            base.EndContinuousUpdate();
            if (running) Land(m_aiActor);
            Finish();
        }

        public override void OnActorPreDeath()
        {
            Finish();
            base.OnActorPreDeath();
        }

        private void Finish()
        {
            if (!running) return;
            running = false;
            AttackBrain.Finished(m_aiActor, GetPlan());
        }

        public static void Land(AIActor actor)
        {
            try
            {
                if (actor == null || actor.healthHaver == null || actor.healthHaver.IsDead || actor.specRigidbody == null) return;
                Dungeonator.Dungeon d = GameManager.HasInstance ? GameManager.Instance.Dungeon : null;
                GameObject dust = d != null && d.dungeonDustups != null ? d.dungeonDustups.rollLandDustup : null;
                if (dust != null) SpawnManager.SpawnVFX(dust, actor.specRigidbody.UnitBottomCenter, Quaternion.identity);
            }
            catch (Exception e) { PastPlugin.Log("hop landing dust: " + e.Message); }
        }
    }

    /// <summary>A sequence (the leap ring, the full course) coordinated as one heavy pattern; its children stay plain so the
    /// policy can never stall a sequence halfway.</summary>
    public class CoordinatedSequence : SequentialAttackBehaviorGroup
    {
        public AttackFamily Family = AttackFamily.Course;
        public float ThreatCost, ThreatLinger, Recovery, ExpectedSeconds = 2f;
        public RangeBand Bands = RangeBand.Any;
        private bool running;

        public AttackPlan GetPlan() { return new AttackPlan(Family, ThreatCost, ThreatLinger, Recovery, Bands); }

        public override bool IsReady() { return base.IsReady() && AttackBrain.Allows(m_aiActor, GetPlan()); }

        public override BehaviorResult Update()
        {
            BehaviorResult result = base.Update();
            if (!running && result != BehaviorResult.Continue)
            {
                running = true;
                AttackBrain.Began(m_aiActor, GetPlan(), ExpectedSeconds, null);
            }
            return result;
        }

        public override void EndContinuousUpdate()
        {
            base.EndContinuousUpdate();
            Finish();
        }

        public override void OnActorPreDeath()
        {
            Finish();
            base.OnActorPreDeath();
        }

        private void Finish()
        {
            if (!running) return;
            running = false;
            AttackBrain.Finished(m_aiActor, GetPlan());
        }
    }
}
