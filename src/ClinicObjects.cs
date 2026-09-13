using UnityEngine;
using Alexandria.DungeonAPI;
using Alexandria.ItemAPI;

namespace PlutoVetVisit
{
    /// <summary>Prefabs the room places by name through StaticReferences.customObjects.</summary>
    public static class ClinicObjects
    {
        public static void Init()
        {
            Register(ClinicLayout.CONTROLLER_OBJECT, BuildController());
            PastPlugin.Log("registered " + StaticReferences.customObjects.Count + " custom objects");
        }

        private static GameObject BuildController()
        {
            GameObject go = new GameObject(ClinicLayout.CONTROLLER_OBJECT);
            go.AddComponent<VetVisitController>();
            return go;
        }

        /// <summary>Fake prefab: inactive and kept across scenes; Alexandria re-activates the placed clone.</summary>
        public static void Register(string name, GameObject go)
        {
            FakePrefab.MakeFakePrefab(go);
            StaticReferences.customObjects[name] = go;
        }
    }
}
