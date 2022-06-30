using System;
using System.IO;

namespace MHR_Model_Converter.Helpers
{
    public static class ErrorHelper
    {
        public static string ConversionFolder { get; set; }

        public static void Log(string error)
        {
            File.AppendAllText(GetErrorLog(), error);
            File.AppendAllText(GetErrorLog(), Environment.NewLine);
        }

        private static string GetErrorLog()
        {
            return Path.Combine(ConversionFolder, "errorlog.txt");
        }
    }
}