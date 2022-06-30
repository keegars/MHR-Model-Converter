using System.IO;

namespace MHR_Model_Converter.Helpers
{
    public static class ErrorHelper
    {
        public static string ConversionFolder { get; set; }

        public static void Log(string error)
        {
            File.AppendAllText(Path.Combine(ConversionFolder, "errorlog.txt"), error);
        }
    }
}