using System.Diagnostics;
using System.IO;

namespace MHR_Model_Converter.Helpers
{
    public static class CMDHelper
    {
        public static void OpenExplorerLocation(string path)
        {
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                Arguments = path,
                FileName = "explorer.exe"
            };

            Process.Start(startInfo);
        }

        public static int RunCMDCommand(this string path, string command)
        {
            //Create bat file, convert and then delete bat
            var noesisBatFile = Path.Combine(path, "Conversion.bat");

            File.WriteAllText(noesisBatFile, command);
            var exitCode = ExecuteBatFile(noesisBatFile);
            File.Delete(noesisBatFile);

            return exitCode;
        }

        public static int ExecuteBatFile(string filePath)
        {
            var proc = new Process();
            proc.StartInfo.WorkingDirectory = Path.GetDirectoryName(filePath);
            proc.StartInfo.FileName = Path.GetFileName(filePath);
            proc.StartInfo.CreateNoWindow = false;
            proc.Start();
            proc.WaitForExit();
            var exitCode = proc.ExitCode;
            proc.Close();

            return exitCode;
        }
    }
}