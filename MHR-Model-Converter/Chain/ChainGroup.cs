using System;
using System.Collections.Generic;
using System.Linq;
using MHR_Model_Converter.Helper;
using static MHR_Model_Converter.Chain.ChainEnums;

namespace MHR_Model_Converter.Chain
{
    public class ChainGroup
    {
        public ulong TerminalNodeNameOffset { get; set; }
        public ulong NodeTableOffset { get; set; }
        public uint SettingId { get; set; }
        public int NodeCount { get; set; }
        public int ExecOrder { get; set; }
        public int AutoBlendCheckNodeNo { get; set; }
        public int WindId { get; set; }
        public uint TerminalNameHash { get; set; }
        public uint AttrFlags { get; set; }
        public uint CollisionFilterFlags { get; set; }
        public uint ExtraNodeLocalPosX { get; set; }
        public uint ExtraNodeLocalPosY { get; set; }
        public uint ExtraNodeLocalPosZ { get; set; }
        public uint Tags1 { get; set; }
        public uint Tags2 { get; set; }
        public uint Tags3 { get; set; }
        public uint Tags4 { get; set; }
        public float DampingNoise0 { get; set; }
        public float DampingNoise1 { get; set; }
        public float EndRotConstMax { get; set; }
        public int TagCount { get; set; }
        public int AngleLimitDirectionMode { get; set; }

        public ulong NextChainNameOffset0 { get; set; } = 0; //Can be empty
        public uint UnknownBoneHash { get; set; } = 0; //Can be 0
        public uint Unknown { get; set; } = 0; //Can be 0
        public ulong Unknown64 { get; set; } = 0; //Can be 0
        public ulong NextChainNameOffset1 { get; set; } = 0; //Set to the next chain offset

        public List<ulong> TerminalNodeNameList { get; set; } 

        public List<ChainNodeData> ChainNodesData { get; set; }

        public byte[] GetTerminalNodeName()
        {
            return TerminalNodeNameList.SelectMany(z => z.ToBytes()).ToArray();
        }

        public byte[] ExportSection(int size, ChainVersion version)
        {
            var bytesList = new List<byte>();

            //Add any specific chain version amendments here
            bytesList.AddRange(TerminalNodeNameOffset.ToBytes());
            bytesList.AddRange(NodeTableOffset.ToBytes());
            bytesList.AddRange(SettingId.ToBytes());
            bytesList.AddRange(NodeCount.ToBytes());
            bytesList.AddRange(ExecOrder.ToBytes());
            bytesList.AddRange(AutoBlendCheckNodeNo.ToBytes());
            bytesList.AddRange(WindId.ToBytes());
            bytesList.AddRange(TerminalNameHash.ToBytes());
            bytesList.AddRange(AttrFlags.ToBytes());
            bytesList.AddRange(CollisionFilterFlags.ToBytes());
            bytesList.AddRange(ExtraNodeLocalPosX.ToBytes());
            bytesList.AddRange(ExtraNodeLocalPosY.ToBytes());
            bytesList.AddRange(ExtraNodeLocalPosZ.ToBytes());
            bytesList.AddRange(Tags1.ToBytes());
            bytesList.AddRange(Tags2.ToBytes());
            bytesList.AddRange(Tags3.ToBytes());
            bytesList.AddRange(Tags4.ToBytes());
            bytesList.AddRange(DampingNoise0.ToBytes());
            bytesList.AddRange(DampingNoise1.ToBytes());
            bytesList.AddRange(EndRotConstMax.ToBytes());
            bytesList.AddRange(TagCount.ToBytes());
            bytesList.AddRange(AngleLimitDirectionMode.ToBytes());
            bytesList.AddRange(ByteHelper.EmptyBytes(2));

            if (version == ChainVersion.v48)
            {
                bytesList.AddRange(NextChainNameOffset0.ToBytes());
                bytesList.AddRange(UnknownBoneHash.ToBytes());
                bytesList.AddRange(Unknown.ToBytes());
                bytesList.AddRange(Unknown64.ToBytes());
                bytesList.AddRange(NextChainNameOffset1.ToBytes());
            }

            if (size != bytesList.Count)
            {
                throw new Exception($"Byte size {bytesList.Count} is not equal to expected size {size}");
            }

            return bytesList.ToArray();
        }
    }
}