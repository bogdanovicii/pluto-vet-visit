using System.Collections.Generic;
using UnityEngine;

namespace PlutoVetVisit
{
    /// <summary>
    /// The sliding clinic door that seals a zone. One prop, two sprites: closed (the placed sprite, with a
    /// HighObstacle collider) and open (the frame only, collider off). The vanilla pasts gate the same way: a
    /// SpeculativeRigidbody blocker toggled on and off (PastLabMarineController.AreaDoor, ConvictPastController.MainDoorBlocker).
    /// Placed clones register in All; the controller sorts them by height to tell the ward door from the theatre door.
    /// </summary>
    public class ClinicDoor : BraveBehaviour
    {
        public static readonly List<ClinicDoor> All = new List<ClinicDoor>();

        public int closedId = -1;
        public int openId = -1;
        public bool IsOpen;

        private void Start()
        {
            if (!All.Contains(this)) All.Add(this);
            Apply();
        }

        public override void OnDestroy()
        {
            All.Remove(this);
            base.OnDestroy();
        }

        public void SetOpen(bool open)
        {
            if (IsOpen == open) return;
            IsOpen = open;
            Apply();
        }

        private void Apply()
        {
            if (sprite != null && closedId >= 0 && openId >= 0) sprite.SetSprite(IsOpen ? openId : closedId);
            if (specRigidbody != null) specRigidbody.enabled = !IsOpen;
            if (sprite != null) sprite.UpdateZDepth();
        }
    }
}
