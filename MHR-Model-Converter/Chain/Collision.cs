using System;
using System.Collections.Generic;
using MHR_Model_Converter.Helper;
using static MHR_Model_Converter.Chain.ChainEnums;

namespace MHR_Model_Converter.Chain
{
    public class Collision
    {
        public ulong SubDataTable { get; set; }
        public float PosX { get; set; }
        public float PosY { get; set; }
        public float PosZ { get; set; }
        public float PairPosX { get; set; }
        public float PairPosY { get; set; }
        public float PairPosZ { get; set; }
        public float RotOffsetX { get; set; }
        public float RotOffsetY { get; set; }
        public float RotOffsetZ { get; set; }
        public float RotOffsetW { get; set; }
        public uint RotationOrder { get; set; } = 0;
        public uint JointNameHash { get; set; }
        public uint PairJointNameHash { get; set; }
        public float Radius { get; set; }
        public float Lerp { get; set; }
        public int Shape { get; set; }
        public int Div { get; set; }
        public int SubDataCount { get; set; }
        public uint CollisionFilterFlags { get; set; }

        public byte[] ExportSection(int size, ChainVersion version)
        {
            var bytesList = new List<byte>();

            //Add any specific chain version amendments here
            bytesList.AddRange(SubDataTable.ToBytes());
            bytesList.AddRange(PosX.ToBytes());
            bytesList.AddRange(PosY.ToBytes());
            bytesList.AddRange(PosZ.ToBytes());
            bytesList.AddRange(PairPosX.ToBytes());
            bytesList.AddRange(PairPosY.ToBytes());
            bytesList.AddRange(PairPosZ.ToBytes());
            bytesList.AddRange(RotOffsetX.ToBytes());
            bytesList.AddRange(RotOffsetY.ToBytes());
            bytesList.AddRange(RotOffsetZ.ToBytes());
            bytesList.AddRange(RotOffsetW.ToBytes());

            if (version == ChainVersion.v48)
            {
                bytesList.AddRange(RotationOrder.ToBytes());
            }

            bytesList.AddRange(JointNameHash.ToBytes());
            bytesList.AddRange(PairJointNameHash.ToBytes());
            bytesList.AddRange(Radius.ToBytes());
            bytesList.AddRange(Lerp.ToBytes());
            bytesList.AddRange(Shape.ToBytes());
            bytesList.AddRange(Div.ToBytes());
            bytesList.AddRange(SubDataCount.ToBytes());
            bytesList.AddRange(ByteHelper.EmptyBytes(1));
            bytesList.AddRange(CollisionFilterFlags.ToBytes());

            if (version == ChainVersion.v48)
            {
                bytesList.AddRange(ByteHelper.EmptyBytes(4));
            }

            if (size != bytesList.Count)
            {
                throw new Exception($"Byte size {bytesList.Count} is not equal to expected size {size}");
            }

            return bytesList.ToArray();
        }
    }
}