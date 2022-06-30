using System;
using System.Collections.Generic;
using MHR_Model_Converter.Helper;
using static MHR_Model_Converter.Chain.ChainEnums;

namespace MHR_Model_Converter.Chain
{
    public class ChainData
    {
        public uint Version { get; set; } //Must be 35 or 48
        public uint Magic { get; set; } //Typically 1851877475
        public uint ErrFlags { get; set; }  //Can be 0
        public uint MasterSize { get; set; } //Can be 0
        public ulong CollisionAttrAssetOffset { get; set; } //Can be 0
        public ulong ModelCollisionTable { get; set; } //Collision Table Start Pointer - MUST BE UPDATED IF FILE CHANGES
        public ulong ExtraDataOffset { get; set; } //Can be 0
        public ulong GroupTablePointer { get; set; } //TODO - Check //Grouping Table Start Pointer - MUST BE UPDATED IF FILE CHANGES
        public ulong LinkTablePointer { get; set; } //Can be 0
        public ulong SettingTablePointer { get; set; } //Setting Table Start Pointer - MUST BE UPDATED IF FILE CHANGES
        public ulong WindSettingTablePointer { get; set; } //Wind Setting Table Pointer - MUST BE UPDATED IF FILE CHANGES
        public int GroupCount { get; set; }
        public int SettingCount { get; set; }
        public int ModelCollisionCount { get; set; }
        public int WindSettingCount { get; set; }
        public int LinkCount { get; set; }
        public int RotationOrder { get; set; }
        public int DefaultSettingIndex { get; set; }
        public int CalculationMode { get; set; }
        public uint ChainAttrFlags { get; set; }
        public uint ChainParamFlags { get; set; }
        public float CalculateStepTime { get; set; }
        public bool ModelCollisionSearch { get; set; }
        public int LegacyVersion { get; set; }
        public ulong CollisionFilterHits { get; set; } //TODO - may need to change this to a list of ints, same length as the model collision count!!!

        private ErrFlag _ErrFlags
        {
            get
            {
                try
                {
                    var errFlag = (ErrFlag)ErrFlags;
                    return errFlag;
                }
                catch
                {
                    return ErrFlag.ErrFlags_None;
                }
            }
        }

        public byte[] ExportSection(int size, ChainVersion version)
        {
            var bytesList = new List<byte>();

            if (version == ChainVersion.v35)
            {
                Version = 35;
            }
            else if (version == ChainVersion.v48)
            {
                Version = 48;
            }

            //Add any specific chain version amendments here
            bytesList.AddRange(Version.ToBytes());
            bytesList.AddRange(Magic.ToBytes());
            bytesList.AddRange(ErrFlags.ToBytes());
            bytesList.AddRange(MasterSize.ToBytes());
            bytesList.AddRange(CollisionAttrAssetOffset.ToBytes());
            bytesList.AddRange(ModelCollisionTable.ToBytes());
            bytesList.AddRange(ExtraDataOffset.ToBytes());
            bytesList.AddRange(GroupTablePointer.ToBytes());
            bytesList.AddRange(LinkTablePointer.ToBytes());
            bytesList.AddRange(SettingTablePointer.ToBytes());
            bytesList.AddRange(WindSettingTablePointer.ToBytes());
            bytesList.AddRange(GroupCount.ToBytes());
            bytesList.AddRange(SettingCount.ToBytes());
            bytesList.AddRange(ModelCollisionCount.ToBytes());
            bytesList.AddRange(WindSettingCount.ToBytes());
            bytesList.AddRange(LinkCount.ToBytes());
            bytesList.AddRange(RotationOrder.ToBytes());
            bytesList.AddRange(DefaultSettingIndex.ToBytes());
            bytesList.AddRange(CalculationMode.ToBytes());
            bytesList.AddRange(ChainAttrFlags.ToBytes());
            bytesList.AddRange(ChainParamFlags.ToBytes());
            bytesList.AddRange(CalculateStepTime.ToBytes());
            bytesList.AddRange(ModelCollisionSearch.ToBytes());
            bytesList.AddRange(LegacyVersion.ToBytes());
            bytesList.AddRange(ByteHelper.EmptyBytes(2)); // Add 2 random 0 bytes
            bytesList.AddRange(CollisionFilterHits.ToBytes());
            bytesList.AddRange(ByteHelper.EmptyBytes(8)); // Add 8 random 0 bytes

            if (size != bytesList.Count)
            {
                throw new Exception($"Byte size {bytesList.Count} is not equal to expected size {size}");
            }

            return bytesList.ToArray();
        }
    }
}