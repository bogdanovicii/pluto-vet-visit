using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>Spec A2: a caged animal that loops idle, reacts when a player comes close (dogs bark) and rattles its door
    /// when a wave starts. A missing clip falls back to a short jitter so nothing breaks before the art lands.</summary>
    public class KennelCritter : BraveBehaviour
    {
        public static readonly List<KennelCritter> All = new List<KennelCritter>();
        public string stem;
        public bool dog;
        public string kind = "cat";          // which animal runs out when freed (cat, dog, cone)
        public Vector2 animalLocal;          // where it sits in the kennel, from the sprite's lower-left (tiles)
        public bool freed;
        private float nextPoll, quietUntil;

        private void Start() { All.Add(this); }

        public override void OnDestroy()
        {
            All.Remove(this);
            base.OnDestroy();
        }

        private void Update()
        {
            if (freed || Time.time < nextPoll) return;
            nextPoll = Time.time + 0.25f;
            if (Time.time < quietUntil || sprite == null || GameManager.Instance == null) return;
            PlayerController p = GameManager.Instance.PrimaryPlayer;
            if (p == null || Vector2.Distance(sprite.WorldCenter, p.CenterPosition) > PastConfig.KennelReactRadius) return;
            quietUntil = Time.time + 8f;
            PlayOnce("react");
            if (dog) ClinicSound.Play("Play_PET_dog_bark_02", gameObject);
        }

        public void PlayOnce(string clip)
        {
            string name = stem + "_" + clip;
            if (spriteAnimator == null || spriteAnimator.GetClipByName(name) == null) { StartCoroutine(Jitter()); return; }
            spriteAnimator.AnimationCompleted = BackToIdle;
            spriteAnimator.Play(name);
        }

        private void BackToIdle(tk2dSpriteAnimator animator, tk2dSpriteAnimationClip clip)
        {
            animator.AnimationCompleted = null;
            string idle = stem + "_idle";
            if (animator.GetClipByName(idle) != null) animator.Play(idle);
        }

        private IEnumerator Jitter()
        {
            Vector3 home = transform.position;
            for (int i = 0; i < 4; i++)
            {
                transform.position = home + new Vector3((i % 2 == 0 ? 1f : -1f) / 16f, 0f, 0f);
                yield return new WaitForSeconds(0.05f);
            }
            transform.position = home;
        }

        /// <summary>0.14.2 rescue: the door flies open (freed clip), and the animal is spawned running free.</summary>
        public FreedAnimal Free()
        {
            if (freed) return null;
            freed = true;
            string name = stem + "_freed";
            if (spriteAnimator != null && spriteAnimator.GetClipByName(name) != null)
            {
                spriteAnimator.AnimationCompleted = null;
                spriteAnimator.Play(name);
            }
            ClinicSound.Play("Play_OBJ_door_open_01", gameObject);
            if (dog) ClinicSound.Play("Play_PET_dog_bark_02", gameObject);
            return FreedAnimal.Spawn(kind, (Vector2)transform.position + animalLocal);
        }

        public static void RattleAll()
        {
            foreach (KennelCritter k in All.ToArray()) if (k != null && !k.freed) k.PlayOnce("rattle");
        }
    }
}
