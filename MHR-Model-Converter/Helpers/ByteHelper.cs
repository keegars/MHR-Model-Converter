using System;

namespace MHR_Model_Converter.Helper
{
    public static class ByteHelper
    {
        public static int GetInt(this byte[] bytes)
        {
            if (bytes.Length != 1)
            {
                throw new Exception("Bytes must be length of 1 to convert to int");
            }

            return bytes[0];
        }

        public static UInt32 GetUint32(this byte[] bytes)
        {
            if (bytes.Length != 4)
            {
                throw new Exception("Bytes must be length of 4 to convert to Uint32");
            }

            return BitConverter.ToUInt32(bytes, 0);
        }

        public static UInt64 GetUint64(this byte[] bytes)
        {
            if (bytes.Length != 8)
            {
                throw new Exception("Bytes must be length of 8 to convert to Uint64");
            }

            return BitConverter.ToUInt64(bytes, 0);
        }

        public static float GetFloat(this byte[] bytes)
        {
            if (bytes.Length != 4)
            {
                throw new Exception("Bytes must be length of 4 to convert to float");
            }

            return BitConverter.ToSingle(bytes, 0);
        }

        public static bool GetBoolean(this byte[] bytes)
        {
            if (bytes.Length != 1)
            {
                throw new Exception("Bytes must be length of 1 to convert to boolean");
            }

            return BitConverter.ToBoolean(bytes, 0);
        }

        public static byte[] ToBytes(this UInt32 value)
        {
            return BitConverter.GetBytes(value);
        }

        public static byte[] ToBytes(this UInt64 value)
        {
            return BitConverter.GetBytes(value);
        }

        public static byte[] ToBytes(this float value)
        {
            return BitConverter.GetBytes(value);
        }

        public static byte[] ToBytes(this bool value)
        {
            return BitConverter.GetBytes(value);
        }

        public static byte[] ToBytes(this int value)
        {
            if (value < 0 && value > 255)
            {
                throw new Exception("Int must be between 0 and 255");
            }

            return new byte[1] { (byte)value };
        }

        public static byte[] EmptyBytes(int howMany)
        {
            return new byte[howMany];
        }
    }
}