using System.Collections;
using UnityEngine;
using Dungeonator;

namespace PlutoVetVisit
{
    /// <summary>
    /// Placed in the clinic room by name (ClinicLayout.CONTROLLER_OBJECT). Runs the past: fade-in, dialogue,
    /// the boss, and the ending. Modelled on the vanilla PastLabMarineController / PilotPastController.
    /// </summary>
    public class VetVisitController : MonoBehaviour
    {
        public static VetVisitController Instance;

        private RoomHandler room;
        private Vector2 origin; // world position of room cell (0, 0)
        private bool ending;

        private IEnumerator Start()
        {
            Instance = this;
            while (Dungeon.IsGenerating) yield return null;
            yield return null;
            room = ((Vector2)transform.position).GetAbsoluteRoom();
            origin = (Vector2)transform.position - ClinicLayout.Controller;
            PastPlugin.Log("clinic ready, origin " + origin + ", room " + (room != null ? room.GetRoomName() : "null"));

            // The Ark wrote a FINALGEON mid-game save before loading us; the game cannot resume it for a
            // custom character, so remove it (the win page deletes it in vanilla too).
            SaveManager.DeleteCurrentSlotMidGameSave();

            PlayerController player = GameManager.Instance.PrimaryPlayer;
            Place(player, ClinicLayout.Spawn);
            if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER)
                Place(GameManager.Instance.SecondaryPlayer, ClinicLayout.Spawn + new Vector2(1.5f, 0f));
            Pixelator.Instance.TriggerPastFadeIn();
            yield return new WaitForSeconds(0.5f);
            if (!PastConfig.SkipIntro) yield return StartCoroutine(Dialogue(player));

            if (PastConfig.DebugEndAfterSeconds > 0f)
            {
                PastPlugin.Log("debug: ending the past in " + PastConfig.DebugEndAfterSeconds + " s");
                yield return new WaitForSeconds(PastConfig.DebugEndAfterSeconds);
                OnBossDied();
            }
        }

        public Vector2 World(Vector2 cell)
        {
            return origin + cell;
        }

        private void Place(PlayerController p, Vector2 cell)
        {
            if (p == null) return;
            Vector2 w = World(cell);
            p.transform.position = new Vector3(w.x, w.y, w.y);
            p.specRigidbody.Reinitialize();
            p.sprite.UpdateZDepth();
        }

        private GameObject speaker;

        /// <summary>Where the Vet's lines come from. Task 10 returns the spawned boss; until then a point behind the table.</summary>
        protected virtual Transform SpeakerTransform()
        {
            if (speaker == null)
            {
                speaker = new GameObject("VetSpeaker");
                Vector2 w = World(ClinicLayout.Vet);
                speaker.transform.position = new Vector3(w.x, w.y, w.y);
            }
            return speaker.transform;
        }

        private IEnumerator Dialogue(PlayerController player)
        {
            bool coop = GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER;
            player.SetInputOverride("past");
            if (coop) GameManager.Instance.SecondaryPlayer.SetInputOverride("past");
            PastCameraUtility.LockConversation(World(ClinicLayout.CameraFocus));
            yield return new WaitForSeconds(0.8f);
            Transform who = SpeakerTransform();
            yield return StartCoroutine(Say(who, PastConfig.Line1, 2.5f));
            yield return StartCoroutine(Say(who, PastConfig.Line2, 3.5f));
            yield return StartCoroutine(Say(player.transform, PastConfig.Line3, 1.5f));
            PastCameraUtility.UnlockConversation();
            player.ClearInputOverride("past");
            if (coop) GameManager.Instance.SecondaryPlayer.ClearInputOverride("past");
        }

        private IEnumerator Say(Transform who, string text, float seconds)
        {
            if (string.IsNullOrEmpty(text)) yield break;
            Vector3 pos = who.position + new Vector3(0f, 2.25f, 0f);
            TextBoxManager.ShowTextBox(pos, who, seconds, text, string.Empty, false, TextBoxManager.BoxSlideOrientation.NO_ADJUSTMENT, false, false);
            yield return new WaitForSeconds(seconds + 0.3f);
            TextBoxManager.ClearTextBox(who);
        }

        public void OnBossDied()
        {
            if (ending) return;
            ending = true;
            StartCoroutine(EndPast());
        }

        /// <summary>The five things every vanilla past controller does after its boss dies.</summary>
        private IEnumerator EndPast()
        {
            // Flag first: the credits tube shows the "past complete" panel only if it is already set.
            GameStatsManager.Instance.SetCharacterSpecificFlag(PlutoLink.Identity, CharacterSpecificGungeonFlags.KILLED_PAST, true);
            GameStatsManager.Instance.RegisterStatChange(TrackedStats.TIMES_KILLED_PAST, 1f);
            PastPlugin.Log("past killed: KILLED_PAST set for identity " + (int)PlutoLink.Identity);
            yield return new WaitForSeconds(3.5f);

            PlayerController p = GameManager.Instance.PrimaryPlayer;
            PastCameraUtility.LockConversation(p.CenterPosition);
            GameManager.Instance.MainCameraController.OverridePosition = p.CenterPosition;
            yield return new WaitForSeconds(0.5f);

            Pixelator.Instance.FreezeFrame();
            BraveTime.RegisterTimeScaleMultiplier(0f, gameObject);
            float elapsed = 0f;
            while (elapsed < ConvictPastController.FREEZE_FRAME_DURATION)
            {
                elapsed += GameManager.INVARIANT_DELTA_TIME;
                yield return null;
            }
            BraveTime.ClearMultiplier(gameObject);

            TimeTubeCreditsController credits = new TimeTubeCreditsController();
            credits.ClearDebris();
            yield return StartCoroutine(credits.HandleTimeTubeCredits(p.sprite.WorldCenter, false, null, -1));
            AmmonomiconController.Instance.OpenAmmonomicon(true, true);
        }
    }
}
