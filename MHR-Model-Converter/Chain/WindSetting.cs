using System;
using System.Collections.Generic;
using MHR_Model_Converter.Helper;
using static MHR_Model_Converter.Chain.ChainEnums;

namespace MHR_Model_Converter.Chain
{
    public class WindSetting
    {
        public uint Id { get; set; }
        public int WindDirection { get; set; }
        public int WindCount { get; set; }
        public int WindType { get; set; }
        public float RandomDamping { get; set; }
        public float RandomDampingCycle { get; set; }
        public float RandomCycleScaling { get; set; }

        public float Direction0X { get; set; }
        public float Direction0Y { get; set; }
        public float Direction0Z { get; set; }
        public float Direction1X { get; set; }
        public float Direction1Y { get; set; }
        public float Direction1Z { get; set; }
        public float Direction2X { get; set; }
        public float Direction2Y { get; set; }
        public float Direction2Z { get; set; }
        public float Direction3X { get; set; }
        public float Direction3Y { get; set; }
        public float Direction3Z { get; set; }
        public float Direction4X { get; set; }
        public float Direction4Y { get; set; }
        public float Direction4Z { get; set; }

        public float MinBuffer0 { get; set; }
        public float MinBuffer1 { get; set; }
        public float MinBuffer2 { get; set; }
        public float MinBuffer3 { get; set; }
        public float MinBuffer4 { get; set; }

        public float MaxBuffer0 { get; set; }
        public float MaxBuffer1 { get; set; }
        public float MaxBuffer2 { get; set; }
        public float MaxBuffer3 { get; set; }
        public float MaxBuffer4 { get; set; }

        public float PhaseShiftBuffer0 { get; set; }
        public float PhaseShiftBuffer1 { get; set; }
        public float PhaseShiftBuffer2 { get; set; }
        public float PhaseShiftBuffer3 { get; set; }
        public float PhaseShiftBuffer4 { get; set; }

        public float CycleBuffer0 { get; set; }
        public float CycleBuffer1 { get; set; }
        public float CycleBuffer2 { get; set; }
        public float CycleBuffer3 { get; set; }
        public float CycleBuffer4 { get; set; }

        public float IntervalBuffer0 { get; set; }
        public float IntervalBuffer1 { get; set; }
        public float IntervalBuffer2 { get; set; }
        public float IntervalBuffer3 { get; set; }
        public float IntervalBuffer4 { get; set; }

        public byte[] ExportSection(int size, ChainVersion version)
        {
            var bytesList = new List<byte>();

            //Add any specific chain version amendments here
            bytesList.AddRange(Id.ToBytes());
            bytesList.AddRange(WindDirection.ToBytes());
            bytesList.AddRange(WindCount.ToBytes());
            bytesList.AddRange(WindType.ToBytes());
            bytesList.AddRange(ByteHelper.EmptyBytes(1));
            bytesList.AddRange(RandomDamping.ToBytes());
            bytesList.AddRange(RandomDampingCycle.ToBytes());
            bytesList.AddRange(RandomCycleScaling.ToBytes());
            bytesList.AddRange(ByteHelper.EmptyBytes(4));
            bytesList.AddRange(Direction0X.ToBytes());
            bytesList.AddRange(Direction0Y.ToBytes());
            bytesList.AddRange(Direction0Z.ToBytes());
            bytesList.AddRange(Direction1X.ToBytes());
            bytesList.AddRange(Direction1Y.ToBytes());
            bytesList.AddRange(Direction1Z.ToBytes());
            bytesList.AddRange(Direction2X.ToBytes());
            bytesList.AddRange(Direction2Y.ToBytes());
            bytesList.AddRange(Direction2Z.ToBytes());
            bytesList.AddRange(Direction3X.ToBytes());
            bytesList.AddRange(Direction3Y.ToBytes());
            bytesList.AddRange(Direction3Z.ToBytes());
            bytesList.AddRange(Direction4X.ToBytes());
            bytesList.AddRange(Direction4Y.ToBytes());
            bytesList.AddRange(Direction4Z.ToBytes());

            bytesList.AddRange(MinBuffer0.ToBytes());
            bytesList.AddRange(MinBuffer1.ToBytes());
            bytesList.AddRange(MinBuffer2.ToBytes());
            bytesList.AddRange(MinBuffer3.ToBytes());
            bytesList.AddRange(MinBuffer4.ToBytes());

            bytesList.AddRange(MaxBuffer0.ToBytes());
            bytesList.AddRange(MaxBuffer1.ToBytes());
            bytesList.AddRange(MaxBuffer2.ToBytes());
            bytesList.AddRange(MaxBuffer3.ToBytes());
            bytesList.AddRange(MaxBuffer4.ToBytes());

            bytesList.AddRange(PhaseShiftBuffer0.ToBytes());
            bytesList.AddRange(PhaseShiftBuffer1.ToBytes());
            bytesList.AddRange(PhaseShiftBuffer2.ToBytes());
            bytesList.AddRange(PhaseShiftBuffer3.ToBytes());
            bytesList.AddRange(PhaseShiftBuffer4.ToBytes());

            bytesList.AddRange(CycleBuffer0.ToBytes());
            bytesList.AddRange(CycleBuffer1.ToBytes());
            bytesList.AddRange(CycleBuffer2.ToBytes());
            bytesList.AddRange(CycleBuffer3.ToBytes());
            bytesList.AddRange(CycleBuffer4.ToBytes());

            bytesList.AddRange(IntervalBuffer0.ToBytes());
            bytesList.AddRange(IntervalBuffer1.ToBytes());
            bytesList.AddRange(IntervalBuffer2.ToBytes());
            bytesList.AddRange(IntervalBuffer3.ToBytes());
            bytesList.AddRange(IntervalBuffer4.ToBytes());

            if (size != bytesList.Count)
            {
                throw new Exception($"Byte size {bytesList.Count} is not equal to expected size {size}");
            }

            return bytesList.ToArray();
        }
    }
}