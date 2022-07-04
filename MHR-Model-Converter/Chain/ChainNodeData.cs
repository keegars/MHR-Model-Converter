using System;
using System.Collections.Generic;
using MHR_Model_Converter.Helper;
using static MHR_Model_Converter.Chain.ChainEnums;

namespace MHR_Model_Converter.Chain
{
    public class ChainNodeData
    {
        public float AngleLimitDirectionX { get; set; }
        public float AngleLimitDirectionY { get; set; }
        public float AngleLimitDirectionZ { get; set; }
        public float AngleLimitDirectionW { get; set; }
        public float AngleLimitRad { get; set; }
        public float AngleLimitDistance { get; set; }
        public float AngleLimitRestitution { get; set; }
        public float AngleLimitRestitutionStopSpeed { get; set; }
        public float CollisionRadius { get; set; }
        public uint CollisionFilterFlags { get; set; }
        public float CapsuleStretchRate0 { get; set; }
        public float CapsuleStretchRate1 { get; set; }
        public uint AttributeFlag { get; set; }
        public uint ConstraintJntNameHash { get; set; }
        public float WindCoEf { get; set; }
        public int AngleMode { get; set; }
        public int CollisionShape { get; set; }
        public int AttachType { get; set; }
        public int RotationType { get; set; }
        public ulong JiggleData { get; set; }

        public byte[] ExportSection(int size, ChainVersion version)
        {
            var bytesList = new List<byte>();

            //Add any specific chain version amendments here
            bytesList.AddRange(AngleLimitDirectionX.ToBytes());
            bytesList.AddRange(AngleLimitDirectionY.ToBytes());
            bytesList.AddRange(AngleLimitDirectionZ.ToBytes());
            bytesList.AddRange(AngleLimitDirectionW.ToBytes());
            bytesList.AddRange(AngleLimitRad.ToBytes());
            bytesList.AddRange(AngleLimitDistance.ToBytes());
            bytesList.AddRange(AngleLimitRestitution.ToBytes());
            bytesList.AddRange(AngleLimitRestitutionStopSpeed.ToBytes());
            bytesList.AddRange(CollisionRadius.ToBytes());
            bytesList.AddRange(CollisionFilterFlags.ToBytes());
            bytesList.AddRange(CapsuleStretchRate0.ToBytes());
            bytesList.AddRange(CapsuleStretchRate1.ToBytes());
            bytesList.AddRange(AttributeFlag.ToBytes());
            bytesList.AddRange(ConstraintJntNameHash.ToBytes());
            bytesList.AddRange(WindCoEf.ToBytes());
            bytesList.AddRange(AngleMode.ToBytes());
            bytesList.AddRange(CollisionShape.ToBytes());
            bytesList.AddRange(AttachType.ToBytes());
            bytesList.AddRange(RotationType.ToBytes());
            bytesList.AddRange(JiggleData.ToBytes());
            bytesList.AddRange(new List<byte> { 0, 0, 128, 63 }); //Add 00 00 80 3F
            bytesList.AddRange(ByteHelper.EmptyBytes(4));

            if (size != bytesList.Count)
            {
                throw new Exception($"Byte size {bytesList.Count} is not equal to expected size {size}");
            }

            return bytesList.ToArray();
        }
    }
}