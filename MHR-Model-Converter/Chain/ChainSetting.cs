using System;
using System.Collections.Generic;
using MHR_Model_Converter.Helper;
using static MHR_Model_Converter.Chain.ChainEnums;

namespace MHR_Model_Converter.Chain
{
    public class ChainSetting
    {
        public ulong ColliderFilterInfoPathOffset { get; set; }
        public float SprayParameterArc { get; set; }
        public float SprayParameterFrequency { get; set; }
        public float SprayParameterCurve1 { get; set; }
        public float SprayParameterCurve2 { get; set; }
        public uint Id { get; set; }
        public int ChainType { get; set; }
        public int SettingAttrFlags { get; set; }
        public int MuzzleDirection { get; set; }
        public int WindDirection { get; set; }
        public float GravityX { get; set; }
        public float GravityY { get; set; }
        public float GravityZ { get; set; }
        public float MuzzleVelocityX { get; set; }
        public float MuzzleVelocityY { get; set; }
        public float MuzzleVelocityZ { get; set; }
        public float Damping { get; set; }
        public float SecondDamping { get; set; }
        public float SecondDampingSpeed { get; set; }
        public float MinDamping { get; set; }
        public float SecondMinDamping { get; set; }
        public float DampingPOW { get; set; }
        public float SecondDampingPOW { get; set; }
        public float CollideMaxVelocity { get; set; }
        public float SpringForce { get; set; }
        public float SpringLimitRate { get; set; }
        public float SpringMaxVelocity { get; set; }
        public uint SpringCalcType { get; set; }
        public float ReduceSelfDistanceRate { get; set; }
        public float SecondReduceSelfDistanceRate { get; set; }
        public float SecondReduceSelfDistanceSpeed { get; set; }
        public float Friction { get; set; }
        public float ShockAbsorptionRate { get; set; }
        public float CoEfOfElasticity { get; set; }
        public float CoEfOfExternalForces { get; set; }
        public float StretchInterationRatio { get; set; }
        public float AngleLimitInterationRatio { get; set; }
        public float ShootingElasticLimitRate { get; set; }
        public uint GroupDefaultAttr { get; set; }
        public float WindEffectCoEf { get; set; }
        public float VelocityLimit { get; set; }
        public float Hardness { get; set; }
        public float Unknown0 { get; set; } = 0;
        public float Unknown1 { get; set; } = 0.1f;

        public byte[] ExportSection(int size, ChainVersion version)
        {
            var bytesList = new List<byte>();

            //Add any specific chain version amendments here
            bytesList.AddRange(ColliderFilterInfoPathOffset.ToBytes());
            bytesList.AddRange(SprayParameterArc.ToBytes());
            bytesList.AddRange(SprayParameterFrequency.ToBytes());
            bytesList.AddRange(SprayParameterCurve1.ToBytes());
            bytesList.AddRange(SprayParameterCurve2.ToBytes());
            bytesList.AddRange(Id.ToBytes());
            bytesList.AddRange(ChainType.ToBytes());
            bytesList.AddRange(SettingAttrFlags.ToBytes());
            bytesList.AddRange(MuzzleDirection.ToBytes());
            bytesList.AddRange(WindDirection.ToBytes());
            bytesList.AddRange(GravityX.ToBytes());
            bytesList.AddRange(GravityY.ToBytes());
            bytesList.AddRange(GravityZ.ToBytes());
            bytesList.AddRange(MuzzleVelocityX.ToBytes());
            bytesList.AddRange(MuzzleVelocityY.ToBytes());
            bytesList.AddRange(MuzzleVelocityZ.ToBytes());
            bytesList.AddRange(Damping.ToBytes());
            bytesList.AddRange(SecondDamping.ToBytes());
            bytesList.AddRange(SecondDampingSpeed.ToBytes());
            bytesList.AddRange(MinDamping.ToBytes());
            bytesList.AddRange(SecondMinDamping.ToBytes());
            bytesList.AddRange(DampingPOW.ToBytes());
            bytesList.AddRange(SecondDampingPOW.ToBytes());
            bytesList.AddRange(CollideMaxVelocity.ToBytes());
            bytesList.AddRange(SpringForce.ToBytes());
            bytesList.AddRange(SpringLimitRate.ToBytes());
            bytesList.AddRange(SpringMaxVelocity.ToBytes());
            bytesList.AddRange(SpringCalcType.ToBytes());
            bytesList.AddRange(ReduceSelfDistanceRate.ToBytes());
            bytesList.AddRange(SecondReduceSelfDistanceRate.ToBytes());
            bytesList.AddRange(SecondReduceSelfDistanceSpeed.ToBytes());
            bytesList.AddRange(Friction.ToBytes());
            bytesList.AddRange(ShockAbsorptionRate.ToBytes());
            bytesList.AddRange(CoEfOfElasticity.ToBytes());
            bytesList.AddRange(CoEfOfExternalForces.ToBytes());
            bytesList.AddRange(StretchInterationRatio.ToBytes());
            bytesList.AddRange(AngleLimitInterationRatio.ToBytes());
            bytesList.AddRange(ShootingElasticLimitRate.ToBytes());
            bytesList.AddRange(GroupDefaultAttr.ToBytes());
            bytesList.AddRange(WindEffectCoEf.ToBytes());
            bytesList.AddRange(VelocityLimit.ToBytes());
            bytesList.AddRange(Hardness.ToBytes());

            if (version == ChainVersion.v48)
            {
                bytesList.AddRange(Unknown0.ToBytes());
                bytesList.AddRange(Unknown1.ToBytes());
                bytesList.AddRange(ByteHelper.EmptyBytes(8));
            }

            if (size != bytesList.Count)
            {
                throw new Exception($"Byte size {bytesList.Count} is not equal to expected size {size}");
            }

            return bytesList.ToArray();
        }
    }
}