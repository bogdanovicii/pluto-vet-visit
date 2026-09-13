using System;
using Alexandria.DungeonAPI;

namespace PlutoVetVisit
{
    /// <summary>Loads the generated clinic room and forces the flags the flow needs.</summary>
    public static class ClinicRoom
    {
        public const string RESOURCE = "PlutoVetVisit/Resources/Rooms/vet_clinic.newroom";
        public static PrototypeDungeonRoom Room;

        public static void Load()
        {
            // RoomFactory.Build swallows exceptions and returns a 12x12 fallback, so check the size.
            RoomFactory.RoomData data = RoomFactory.BuildNewRoomFromResource(RESOURCE, typeof(PastPlugin).Assembly);
            if (data.room == null) throw new Exception("RoomFactory returned no room for " + RESOURCE);
            if (data.room.Width != ClinicLayout.WIDTH || data.room.Height != ClinicLayout.HEIGHT)
                throw new Exception("clinic room is " + data.room.Width + "x" + data.room.Height + ", expected " + ClinicLayout.WIDTH + "x" + ClinicLayout.HEIGHT + " (RoomFactory failed, see the Alexandria error above)");
            Room = data.room;
            Room.category = PrototypeDungeonRoom.RoomCategory.ENTRANCE; // the flow's first node must be an entrance (set in code, per the guide)
            Room.name = "pluto_vet_clinic";
            if (PastConfig.RoomVisualSubtype >= 0)
            {
                Room.overrideRoomVisualType = PastConfig.RoomVisualSubtype;
                Room.overrideRoomVisualTypeForSecretRooms = true;
            }
            PastPlugin.Log("clinic room " + Room.Width + "x" + Room.Height + ", " + Room.placedObjects.Count + " placed objects, " + Room.exitData.exits.Count + " exits");
        }
    }
}
