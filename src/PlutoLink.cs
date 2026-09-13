using System;
using UnityEngine;
using Alexandria.CharacterAPI;

namespace PlutoVetVisit
{
    /// <summary>
    /// Finds Pluto through Alexandria's character registry (no compile-time reference to PlutoTheCat.dll)
    /// and attaches the past to his prefab. Alexandria reads CustomCharacter.past lazily at Ark time, and
    /// CustomCharacterData.hasPast every time the Blacksmith spawns, so setting them after the character
    /// was built is enough.
    /// </summary>
    public static class PlutoLink
    {
        public const string STORED_KEY = "playerpluto"; // ("Player" + nameShort).ToLower()

        public static CustomCharacterData Data;
        public static GameObject Prefab;
        public static PlayableCharacters Identity;

        public static bool Found { get { return Data != null && Prefab != null; } }

        public static bool Find()
        {
            if (Found) return true;
            if (CharacterBuilder.storedCharacters == null) return false;
            Tuple<CustomCharacterData, GameObject> stored;
            if (!CharacterBuilder.storedCharacters.TryGetValue(STORED_KEY, out stored) || stored == null) return false;
            if (stored.First == null || stored.Second == null) return false;
            Data = stored.First;
            Prefab = stored.Second;
            Identity = Data.identity;
            return true;
        }

        public static void AttachPast(string levelName, Texture2D winPic)
        {
            if (!Found) throw new InvalidOperationException("Pluto not found");
            CustomCharacter cc = Prefab.GetComponent<CustomCharacter>();
            if (cc == null) throw new InvalidOperationException("Pluto's prefab has no CustomCharacter component");
            cc.past = levelName;
            cc.hasPast = true;
            Data.hasPast = true;
            if (winPic != null) Data.pastWinPic = winPic;
            PastPlugin.Log("attached past \"" + levelName + "\" to " + Data.nameShort + " (identity " + (int)Identity + ")");
        }

        public static bool IsPluto(PlayerController player)
        {
            return player != null && Found && player.characterIdentity == Identity;
        }
    }
}
