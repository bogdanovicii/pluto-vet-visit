using System;
using System.Collections.Generic;
using Alexandria.DungeonAPI;
using Dungeonator;

namespace PlutoVetVisit
{
    /// <summary>One-node flow: the clinic is the entrance room and the only room.</summary>
    public static class VetFlow
    {
        public static DungeonFlow Create(Dungeon template)
        {
            if (ClinicRoom.Room == null) throw new InvalidOperationException("ClinicRoom.Load() must run first");
            DungeonFlow flow = SampleFlow.CreateNewFlow(template); // borrows the template's fallback tables, empty injections, Initialize()
            flow.name = "pluto_vet_visit_flow";
            DungeonFlowNode node = GenerateDefaultNode(flow, PrototypeDungeonRoom.RoomCategory.ENTRANCE, ClinicRoom.Room);
            flow.AddNodeToFlow(node, null);
            flow.FirstNode = node;
            return flow;
        }

        /// <summary>The helper every floor mod copies (ExpandTheGungeon / Modular / Planetside); Alexandria does not ship it.</summary>
        public static DungeonFlowNode GenerateDefaultNode(DungeonFlow targetflow, PrototypeDungeonRoom.RoomCategory roomType, PrototypeDungeonRoom overrideRoom = null,
            GenericRoomTable overrideTable = null, bool oneWayLoopTarget = false, bool isWarpWingNode = false, string nodeGUID = null,
            DungeonFlowNode.NodePriority priority = DungeonFlowNode.NodePriority.MANDATORY, float percentChance = 1f, bool handlesOwnWarping = true)
        {
            if (string.IsNullOrEmpty(nodeGUID)) nodeGUID = Guid.NewGuid().ToString();
            return new DungeonFlowNode(targetflow)
            {
                isSubchainStandin = false,
                nodeType = DungeonFlowNode.ControlNodeType.ROOM,
                roomCategory = roomType,
                percentChance = percentChance,
                priority = priority,
                overrideExactRoom = overrideRoom,
                overrideRoomTable = overrideTable,
                capSubchain = false,
                subchainIdentifier = string.Empty,
                limitedCopiesOfSubchain = false,
                maxCopiesOfSubchain = 1,
                subchainIdentifiers = new List<string>(0),
                receivesCaps = false,
                isWarpWingEntrance = isWarpWingNode,
                handlesOwnWarping = handlesOwnWarping,
                forcedDoorType = DungeonFlowNode.ForcedDoorType.NONE,
                loopForcedDoorType = DungeonFlowNode.ForcedDoorType.NONE,
                nodeExpands = false,
                initialChainPrototype = "n",
                chainRules = new List<ChainRule>(0),
                minChainLength = 3,
                maxChainLength = 8,
                minChildrenToBuild = 1,
                maxChildrenToBuild = 1,
                canBuildDuplicateChildren = false,
                guidAsString = nodeGUID,
                parentNodeGuid = string.Empty,
                childNodeGuids = new List<string>(0),
                loopTargetNodeGuid = string.Empty,
                loopTargetIsOneWay = oneWayLoopTarget,
                flow = targetflow,
            };
        }
    }
}
