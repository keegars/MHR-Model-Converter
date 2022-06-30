using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using MHR_Model_Converter.Helper;
using MHR_Model_Converter.Helpers;
using static MHR_Model_Converter.Chain.ChainEnums;

namespace MHR_Model_Converter.Chain
{
    public class Chain
    {
        private byte[] _FileBytes;
        private string _FilePath;
        private int _Position = 0;
        private ChainVersion _Version;

        public int ChainDataSize { get; private set; }
        public int ChainSettingSize { get; private set; }
        public int CollisionSize { get; private set; }
        public int ChainGroupSize { get; private set; }
        public int ChainNodeSize { get; private set; }
        public int WindSettingSize { get; private set; }

        public ChainData ChainData { get; set; }
        public List<ChainSetting> ChainSettings { get; set; }
        public List<Collision> Collisions { get; set; }
        public List<ChainGroup> ChainGroups { get; set; }
        public WindSetting WindSetting { get; set; }

        public Chain(string filePath, ChainVersion version, bool createNewFile = false)
        {
            _Version = version;
            _FilePath = filePath;
            var fileInfo = new FileInfo(_FilePath);

            if (createNewFile)
            {
                if (fileInfo.Exists)
                {
                    fileInfo.Delete();
                }

                fileInfo.Create();
                fileInfo.Refresh();
            }

            if (!fileInfo.Exists)
            {
                throw new Exception("File does not exist!");
            }

            using (var br = PathHelper.OpenFile(filePath))
            using (var ms = new MemoryStream())
            {
                br.BaseStream.CopyTo(ms);
                _FileBytes = ms.ToArray();
            }

            UpdateVersion(version);
        }

        public void Populate()
        {
            PopulateChainData();
            PopulateChainSettings();
            PopulateCollisions();
            PopulateChainGroups();
            PopulateWindSettings();
        }

        public byte[] Export(ChainVersion version)
        {
            UpdateVersion(version);

            var bytes = new List<byte>();

            //Export each section in order
            var chainDataBytes = ChainData.ExportSection(ChainDataSize, version);
            var chainSettingsBytes = ChainSettings.Select(z => z.ExportSection(ChainSettingSize, version)).ToList();
            var collisionBytes = Collisions.Select(z => z.ExportSection(CollisionSize, version)).ToList();
            var chainGroupBytes = ChainGroups.Select(z => z.ExportSection(ChainGroupSize, version)).ToList();
            var chainNodesDataBytes = ChainGroups.Select(z => new
            {
                TerminalNodeName = z.GetTerminalNodeName(),
                ChainNodeBytes = z.ChainNodesData.Select(y => y.ExportSection(ChainNodeSize, version))
            }).ToList();
            var windSettingBytes = WindSetting?.ExportSection(WindSettingSize, version) ?? new byte[0];

            ////Generate offset pointers
            //Update chain data offsets
            var chainDataOffset = 0;
            var settingOffset = chainDataBytes.Length;
            var collisionOffset = settingOffset + chainSettingsBytes.Sum(z => z.Length);
            var groupTableOffset = collisionOffset + collisionBytes.Sum(z => z.Length);
            var nodeTableOffset = groupTableOffset + chainGroupBytes.Sum(z => z.Length);
            var windOffset = nodeTableOffset + chainNodesDataBytes.Sum(z =>
                    z.TerminalNodeName.Length
                    + z.ChainNodeBytes.Sum(y => y.Length)
                );

            ChainData.SettingTablePointer = Convert.ToUInt64(settingOffset);
            ChainData.ModelCollisionTable = Convert.ToUInt64(collisionOffset);
            ChainData.GroupTablePointer = Convert.ToUInt64(groupTableOffset);
            ChainData.WindSettingTablePointer = Convert.ToUInt64(windOffset);

            //Update chain group node offsets
            var offset = nodeTableOffset;
            for (var i = 0; i < ChainGroups.Count; i++)
            {
                var chainGroup = ChainGroups[i];

                chainGroup.TerminalNodeNameOffset = Convert.ToUInt64(offset);
                offset += chainGroup.GetTerminalNodeName().Length;
                chainGroup.NodeTableOffset = Convert.ToUInt64(offset);
                offset += ChainNodeSize * chainGroup.ChainNodesData.Count;

                //Update chain group node - next chain name offset
                if (i != 0)
                {
                    var lastChainGroup = ChainGroups[i - 1];
                    lastChainGroup.NextChainNameOffset1 = chainGroup.TerminalNodeNameOffset;
                }
            }

            //Regenerate each section that was modified
            chainDataBytes = ChainData.ExportSection(ChainDataSize, version);
            chainGroupBytes = ChainGroups.Select(z => z.ExportSection(ChainGroupSize, version)).ToList();

            //Add them to bytes list
            bytes.AddRange(chainDataBytes);
            chainSettingsBytes.ForEach(z => bytes.AddRange(z));
            collisionBytes.ForEach(z => bytes.AddRange(z));
            chainGroupBytes.ForEach(z => bytes.AddRange(z));
            chainNodesDataBytes.ForEach(z => bytes.AddRange(z.TerminalNodeName.Concat(z.ChainNodeBytes.SelectMany(y => y).ToArray()).ToArray()));
            bytes.AddRange(windSettingBytes);

            //Return byte array
            return bytes.ToArray();
        }

        public byte[] GetOriginalBytes()
        {
            return _FileBytes;
        }

        private void UpdateVersion(ChainVersion version)
        {
            if (version == ChainVersion.v35)
            {
                ChainDataSize = 112;        //70
                ChainSettingSize = 160;     //A0
                CollisionSize = 72;         //48
                ChainGroupSize = 80;        //50
                ChainNodeSize = 80;        //50
                WindSettingSize = 184;      //B8
            }
            else if (version == ChainVersion.v48)
            {
                ChainDataSize = 112;        //70
                ChainSettingSize = 176;     //B0
                CollisionSize = 80;         //50
                ChainGroupSize = 112;       //70
                ChainNodeSize = 80;         //70
                WindSettingSize = 184;      //B8
            }
            else
            {
                throw new Exception("Chain version not supported");
            }
        }

        private void PopulateChainData()
        {
            //Create new chain data
            ChainData = new ChainData();
            var chainData = ChainData;

            //Populate
            chainData.Version = TakeBytes<uint>();
            chainData.Magic = TakeBytes<uint>();
            chainData.ErrFlags = TakeBytes<uint>();
            chainData.MasterSize = TakeBytes<uint>();
            chainData.CollisionAttrAssetOffset = TakeBytes<ulong>();
            chainData.ModelCollisionTable = TakeBytes<ulong>();
            chainData.ExtraDataOffset = TakeBytes<ulong>();
            chainData.GroupTablePointer = TakeBytes<ulong>();
            chainData.LinkTablePointer = TakeBytes<ulong>();
            chainData.SettingTablePointer = TakeBytes<ulong>();
            chainData.WindSettingTablePointer = TakeBytes<ulong>();
            chainData.GroupCount = TakeBytes<int>();
            chainData.SettingCount = TakeBytes<int>();
            chainData.ModelCollisionCount = TakeBytes<int>();
            chainData.WindSettingCount = TakeBytes<int>();
            chainData.LinkCount = TakeBytes<int>();
            chainData.RotationOrder = TakeBytes<int>();
            chainData.DefaultSettingIndex = TakeBytes<int>();
            chainData.CalculationMode = TakeBytes<int>();
            chainData.ChainAttrFlags = TakeBytes<uint>();
            chainData.ChainParamFlags = TakeBytes<uint>();
            chainData.CalculateStepTime = TakeBytes<float>();
            chainData.ModelCollisionSearch = TakeBytes<bool>();
            chainData.LegacyVersion = TakeBytes<int>();
            TakeBytes(2); //Read 2 bytes
            chainData.CollisionFilterHits = TakeBytes<ulong>();
            TakeBytes(8); //Read 8 bytes

            //Check that the data sizes match
            if (_Position != ChainDataSize)
            {
                throw new Exception($"Position {_Position} in byte array is not the same as the chain data size {ChainDataSize}.");
            }
        }

        private void PopulateChainSettings()
        {
            ChainSettings = new List<ChainSetting>();

            var chainCount = ChainData.SettingCount;
            for (var i = 0; i < chainCount; i++)
            {
                //Create new chain setting
                var chainSetting = new ChainSetting();

                //Populate
                chainSetting.ColliderFilterInfoPathOffset = TakeBytes<ulong>();
                chainSetting.SprayParameterArc = TakeBytes<float>();
                chainSetting.SprayParameterFrequency = TakeBytes<float>();
                chainSetting.SprayParameterCurve1 = TakeBytes<float>();
                chainSetting.SprayParameterCurve2 = TakeBytes<float>();
                chainSetting.Id = TakeBytes<uint>();
                chainSetting.ChainType = TakeBytes<int>();
                chainSetting.SettingAttrFlags = TakeBytes<int>();
                chainSetting.MuzzleDirection = TakeBytes<int>();
                chainSetting.WindDirection = TakeBytes<int>();
                chainSetting.GravityX = TakeBytes<float>();
                chainSetting.GravityY = TakeBytes<float>();
                chainSetting.GravityZ = TakeBytes<float>();
                chainSetting.MuzzleVelocityX = TakeBytes<float>();
                chainSetting.MuzzleVelocityY = TakeBytes<float>();
                chainSetting.MuzzleVelocityZ = TakeBytes<float>();
                chainSetting.Damping = TakeBytes<float>();
                chainSetting.SecondDamping = TakeBytes<float>();
                chainSetting.SecondDampingSpeed = TakeBytes<float>();
                chainSetting.MinDamping = TakeBytes<float>();
                chainSetting.SecondMinDamping = TakeBytes<float>();
                chainSetting.DampingPOW = TakeBytes<float>();
                chainSetting.SecondDampingPOW = TakeBytes<float>();
                chainSetting.CollideMaxVelocity = TakeBytes<float>();
                chainSetting.SpringForce = TakeBytes<float>();
                chainSetting.SpringLimitRate = TakeBytes<float>();
                chainSetting.SpringMaxVelocity = TakeBytes<float>();
                chainSetting.SpringCalcType = TakeBytes<uint>();
                chainSetting.ReduceSelfDistanceRate = TakeBytes<float>();
                chainSetting.SecondReduceSelfDistanceRate = TakeBytes<float>();
                chainSetting.SecondReduceSelfDistanceSpeed = TakeBytes<float>();
                chainSetting.Friction = TakeBytes<float>();
                chainSetting.ShockAbsorptionRate = TakeBytes<float>();
                chainSetting.CoEfOfElasticity = TakeBytes<float>();
                chainSetting.CoEfOfExternalForces = TakeBytes<float>();
                chainSetting.StretchInterationRatio = TakeBytes<float>();
                chainSetting.AngleLimitInterationRatio = TakeBytes<float>();
                chainSetting.ShootingElasticLimitRate = TakeBytes<float>();
                chainSetting.GroupDefaultAttr = TakeBytes<uint>();
                chainSetting.WindEffectCoEf = TakeBytes<float>();
                chainSetting.VelocityLimit = TakeBytes<float>();
                chainSetting.Hardness = TakeBytes<float>();

                if (_Version == ChainVersion.v48)
                {
                    chainSetting.Unknown0 = TakeBytes<float>();
                    chainSetting.Unknown1 = TakeBytes<float>();
                    TakeBytes(16);
                }

                //Check that the data sizes match
                var size = ChainDataSize + (ChainSettingSize * (i + 1));

                if (_Position != size)
                {
                    throw new Exception($"Position {_Position} in byte array is not the same as the chain data size {ChainSettingSize}.");
                }

                //Add chain to list
                ChainSettings.Add(chainSetting);
            }
        }

        private void PopulateCollisions()
        {
            Collisions = new List<Collision>();

            var collisionCount = ChainData.ModelCollisionCount;
            for (var i = 0; i < collisionCount; i++)
            {
                //Create new collision
                var collision = new Collision();

                //Populate
                collision.SubDataTable = TakeBytes<ulong>();
                collision.PosX = TakeBytes<float>();
                collision.PosY = TakeBytes<float>();
                collision.PosZ = TakeBytes<float>();
                collision.PairPosX = TakeBytes<float>();
                collision.PairPosY = TakeBytes<float>();
                collision.PairPosZ = TakeBytes<float>();
                collision.RotOffsetX = TakeBytes<float>();
                collision.RotOffsetY = TakeBytes<float>();
                collision.RotOffsetZ = TakeBytes<float>();
                collision.RotOffsetW = TakeBytes<float>();

                if (_Version == ChainVersion.v48)
                {
                    collision.RotationOrder = TakeBytes<uint>();
                }

                collision.JointNameHash = TakeBytes<uint>();
                collision.PairJointNameHash = TakeBytes<uint>();
                collision.Radius = TakeBytes<float>();
                collision.Lerp = TakeBytes<float>();
                collision.Shape = TakeBytes<int>();
                collision.Div = TakeBytes<int>();
                collision.SubDataCount = TakeBytes<int>();
                TakeBytes(1);
                collision.CollisionFilterFlags = TakeBytes<uint>();

                if (_Version == ChainVersion.v48)
                {
                    TakeBytes(4);
                }

                //Check that the data sizes match
                var size = ChainDataSize + (ChainSettingSize * ChainData.SettingCount) + (CollisionSize * (i + 1));

                if (_Position != size)
                {
                    throw new Exception($"Position {_Position} in byte array is not the same as the chain data size {CollisionSize}.");
                }

                //Add collision to list
                Collisions.Add(collision);
            }
        }

        private void PopulateChainGroups()
        {
            ChainGroups = new List<ChainGroup>();

            var chainGroupCount = ChainData.GroupCount;
            for (var i = 0; i < chainGroupCount; i++)
            {
                //Create new chain group
                var chainGroup = new ChainGroup();

                //Populate
                chainGroup.TerminalNodeNameOffset = TakeBytes<ulong>();
                chainGroup.NodeTableOffset = TakeBytes<ulong>();
                chainGroup.SettingId = TakeBytes<uint>();
                chainGroup.NodeCount = TakeBytes<int>();
                chainGroup.ExecOrder = TakeBytes<int>();
                chainGroup.AutoBlendCheckNodeNo = TakeBytes<int>();
                chainGroup.WindId = TakeBytes<int>();
                chainGroup.TerminalNameHash = TakeBytes<uint>();
                chainGroup.AttrFlags = TakeBytes<uint>();
                chainGroup.CollisionFilterFlags = TakeBytes<uint>();
                chainGroup.ExtraNodeLocalPosX = TakeBytes<uint>();
                chainGroup.ExtraNodeLocalPosY = TakeBytes<uint>();
                chainGroup.ExtraNodeLocalPosZ = TakeBytes<uint>();
                chainGroup.Tags1 = TakeBytes<uint>();
                chainGroup.Tags2 = TakeBytes<uint>();
                chainGroup.Tags3 = TakeBytes<uint>();
                chainGroup.Tags4 = TakeBytes<uint>();
                chainGroup.DampingNoise0 = TakeBytes<float>();
                chainGroup.DampingNoise1 = TakeBytes<float>();
                chainGroup.EndRotConstMax = TakeBytes<float>();
                chainGroup.TagCount = TakeBytes<int>();
                chainGroup.AngleLimitDirectionMode = TakeBytes<int>();
                TakeBytes(2);

                if (_Version == ChainVersion.v48)
                {
                    chainGroup.NextChainNameOffset0 = TakeBytes<ulong>();
                    chainGroup.UnknownBoneHash = TakeBytes<uint>();
                    chainGroup.Unknown = TakeBytes<uint>();
                    chainGroup.Unknown64 = TakeBytes<ulong>();
                    chainGroup.NextChainNameOffset1 = TakeBytes<ulong>();
                }

                var endPosition = _Position;

                //Populate Chain Node Data
                _Position = Convert.ToInt32(chainGroup.TerminalNodeNameOffset);
                var endOffset = Convert.ToInt32(chainGroup.NodeTableOffset);
                var nameSections = (endOffset - _Position) / 8;

                chainGroup.TerminalNodeNameList = new List<ulong>();
                if (chainGroup.TerminalNodeNameOffset != 0)
                {
                    for (var j = 0; j < nameSections; j++)
                    {
                        var terminalNodeNamePart = TakeBytes<ulong>();
                        chainGroup.TerminalNodeNameList.Add(terminalNodeNamePart);
                    }
                }

                chainGroup.ChainNodesData = new List<ChainNodeData>();

                for (var j = 0; j < chainGroup.NodeCount; j++)
                {
                    var startPos = _Position;

                    var chainNodeData = new ChainNodeData();

                    //Populate
                    chainNodeData.AngleLimitDirectionX = TakeBytes<float>();
                    chainNodeData.AngleLimitDirectionY = TakeBytes<float>();
                    chainNodeData.AngleLimitDirectionZ = TakeBytes<float>();
                    chainNodeData.AngleLimitDirectionW = TakeBytes<float>();
                    chainNodeData.AngleLimitRad = TakeBytes<float>();
                    chainNodeData.AngleLimitDistance = TakeBytes<float>();
                    chainNodeData.AngleLimitRestitution = TakeBytes<float>();
                    chainNodeData.AngleLimitRestitutionStopSpeed = TakeBytes<float>();
                    chainNodeData.CollisionRadius = TakeBytes<float>();
                    chainNodeData.CollisionFilterFlags = TakeBytes<uint>();
                    chainNodeData.CapsuleStretchRate0 = TakeBytes<float>();
                    chainNodeData.CapsuleStretchRate1 = TakeBytes<float>();
                    chainNodeData.AttributeFlag = TakeBytes<uint>();
                    chainNodeData.ConstraintJntNameHash = TakeBytes<uint>();
                    chainNodeData.WindCoEf = TakeBytes<float>();
                    chainNodeData.AngleMode = TakeBytes<int>();
                    chainNodeData.CollisionShape = TakeBytes<int>();
                    chainNodeData.AttachType = TakeBytes<int>();
                    chainNodeData.RotationType = TakeBytes<int>();
                    chainNodeData.JiggleData = TakeBytes<ulong>();
                    TakeBytes(8);

                    if (_Position - ChainNodeSize != startPos)
                    {
                        throw new Exception($"Position {_Position} in byte array is not the same as the chain data size {ChainNodeSize}.");
                    }

                    //Add to chain note data
                    chainGroup.ChainNodesData.Add(chainNodeData);
                }

                _Position = endPosition;

                //Check that the data sizes match
                var size = ChainDataSize + (ChainSettingSize * ChainData.SettingCount) + (CollisionSize * ChainData.ModelCollisionCount) + (ChainGroupSize * (i + 1));

                if (_Position != size)
                {
                    throw new Exception($"Position {_Position} in byte array is not the same as the chain data size {ChainGroupSize}.");
                }

                //Add collision to list
                ChainGroups.Add(chainGroup);
            }
        }

        private void PopulateWindSettings()
        {
            if (ChainData.WindSettingCount > 0)
            {
                WindSetting = new WindSetting();
                var windSetting = WindSetting;

                _Position = Convert.ToInt32(ChainData.WindSettingTablePointer);

                //Populate
                windSetting.Id = TakeBytes<uint>();
                windSetting.WindDirection = TakeBytes<int>();
                windSetting.WindCount = TakeBytes<int>();
                windSetting.WindType = TakeBytes<int>();
                TakeBytes(1);
                windSetting.RandomDamping = TakeBytes<float>();
                windSetting.RandomDampingCycle = TakeBytes<float>();
                windSetting.RandomCycleScaling = TakeBytes<float>();
                TakeBytes(4);
                windSetting.Direction0X = TakeBytes<float>();
                windSetting.Direction0Y = TakeBytes<float>();
                windSetting.Direction0Z = TakeBytes<float>();
                windSetting.Direction1X = TakeBytes<float>();
                windSetting.Direction1Y = TakeBytes<float>();
                windSetting.Direction1Z = TakeBytes<float>();
                windSetting.Direction2X = TakeBytes<float>();
                windSetting.Direction2Y = TakeBytes<float>();
                windSetting.Direction2Z = TakeBytes<float>();
                windSetting.Direction3X = TakeBytes<float>();
                windSetting.Direction3Y = TakeBytes<float>();
                windSetting.Direction3Z = TakeBytes<float>();
                windSetting.Direction4X = TakeBytes<float>();
                windSetting.Direction4Y = TakeBytes<float>();
                windSetting.Direction4Z = TakeBytes<float>();

                windSetting.MinBuffer0 = TakeBytes<float>();
                windSetting.MinBuffer1 = TakeBytes<float>();
                windSetting.MinBuffer2 = TakeBytes<float>();
                windSetting.MinBuffer3 = TakeBytes<float>();
                windSetting.MinBuffer4 = TakeBytes<float>();

                windSetting.MaxBuffer0 = TakeBytes<float>();
                windSetting.MaxBuffer1 = TakeBytes<float>();
                windSetting.MaxBuffer2 = TakeBytes<float>();
                windSetting.MaxBuffer3 = TakeBytes<float>();
                windSetting.MaxBuffer4 = TakeBytes<float>();

                windSetting.PhaseShiftBuffer0 = TakeBytes<float>();
                windSetting.PhaseShiftBuffer1 = TakeBytes<float>();
                windSetting.PhaseShiftBuffer2 = TakeBytes<float>();
                windSetting.PhaseShiftBuffer3 = TakeBytes<float>();
                windSetting.PhaseShiftBuffer4 = TakeBytes<float>();

                windSetting.CycleBuffer0 = TakeBytes<float>();
                windSetting.CycleBuffer1 = TakeBytes<float>();
                windSetting.CycleBuffer2 = TakeBytes<float>();
                windSetting.CycleBuffer3 = TakeBytes<float>();
                windSetting.CycleBuffer4 = TakeBytes<float>();

                windSetting.IntervalBuffer0 = TakeBytes<float>();
                windSetting.IntervalBuffer1 = TakeBytes<float>();
                windSetting.IntervalBuffer2 = TakeBytes<float>();
                windSetting.IntervalBuffer3 = TakeBytes<float>();
                windSetting.IntervalBuffer4 = TakeBytes<float>();

                //Check that the data sizes match
                var size = Convert.ToInt32(ChainData.WindSettingTablePointer) + WindSettingSize;

                if (_Position != size)
                {
                    throw new Exception($"Position {_Position} in byte array is not the same as the chain data size {WindSettingSize}.");
                }
            }
        }

        private T TakeBytes<T>()
        {
            var type = typeof(T);

            if (type == typeof(uint))
            {
                return (T)Convert.ChangeType(TakeBytes(4).GetUint32(), typeof(T));
            }
            else if (type == typeof(ulong))
            {
                return (T)Convert.ChangeType(TakeBytes(8).GetUint64(), typeof(T));
            }
            else if (type == typeof(int))
            {
                return (T)Convert.ChangeType(TakeBytes(1).GetInt(), typeof(T));
            }
            else if (type == typeof(float))
            {
                return (T)Convert.ChangeType(TakeBytes(4).GetFloat(), typeof(T));
            }
            else if (type == typeof(bool))
            {
                return (T)Convert.ChangeType(TakeBytes(1).GetBoolean(), typeof(T));
            }
            else
            {
                throw new Exception("Type is not supported");
            }
        }

        private byte[] TakeBytes(int take)
        {
            var tmpBytes = _FileBytes.Skip(_Position).Take(take).ToArray();
            _Position += take;

            return tmpBytes;
        }
    }
}