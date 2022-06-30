using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using static MHR_Model_Converter.Helpers.PathHelper;

namespace MHR_Model_Converter.Helpers
{
    public static class NoesisHelper
    {
        public static string NoesisFilePath = string.Empty;

        private static string _NoesisFolder
        {
            get
            {
                if (!string.IsNullOrWhiteSpace(NoesisFilePath))
                {
                    return Path.GetDirectoryName(NoesisFilePath);
                }

                return string.Empty;
            }
        }

        public static List<string> ConvertWithNoesis(string file, string oldFileExtension, string newFileExtension, NoesisVersions version, bool deleteFile = true, params string[] options)

        {
            return ConvertWithNoesis(new string[1] { file }, oldFileExtension, newFileExtension, version, deleteFile, options);
        }

        public static List<string> ConvertWithNoesis(List<string> files, string oldFileExtension, string newFileExtension, NoesisVersions version, bool deleteFile = true, params string[] options)

        {
            return ConvertWithNoesis(files.ToArray(), oldFileExtension, newFileExtension, version, deleteFile, options);
        }

        public static List<string> ConvertWithNoesis(string[] files, string oldFileExtension, string newFileExtension, NoesisVersions version, bool deleteFile = true, params string[] options)
        {
            CopyVersionFiles(version);

            var failedConversions = new List<string>();

            foreach (var file in files)
            {
                //New file name to detect the file type
                var newFileName = file.Replace(oldFileExtension, newFileExtension);
                var newFileNameInfo = new FileInfo(newFileName);

                if (newFileNameInfo.Exists)
                {
                    newFileNameInfo.Delete();
                }

                File.Copy(file, newFileNameInfo.FullName);
                newFileNameInfo.Refresh();

                //Create command to run noesis.exe, and run it
                var noesisOptions = string.Join(" ", options.Select(z => z.StartsWith("-") ? z : $"-{z}"));

                try
                {
                    var timeNow = DateTime.Now.AddSeconds(-5);

                    var command = $@"noesis.exe ?cmode ""{file}"" ""{newFileName}"" {noesisOptions}";
                    var exitCode = _NoesisFolder.RunCMDCommand(command);

                    //check if file was created...
                    newFileNameInfo.Refresh();
                    if (!newFileNameInfo.Exists || newFileNameInfo.LastWriteTime < timeNow)
                    {
                        //File failed to be created, add to failed conversions
                        failedConversions.Add(file);
                        if (newFileNameInfo.Exists)
                        {
                            newFileNameInfo.Delete();
                        }
                    }

                    if (deleteFile)
                    {
                        //Remove original
                        File.Delete(file);
                    }
                }
                catch (Exception ex)
                {
                    failedConversions.Add(file);
                }
            }

            return failedConversions;
        }

        private static void CopyVersionFiles(NoesisVersions version)
        {
            var currentDirectory = Environment.CurrentDirectory;
            var scriptsDirectory = Path.Combine(currentDirectory, "Scripts");

            var v2_9999_modified = Path.Combine(scriptsDirectory, "Modified");
            var v2_9999 = Path.Combine(scriptsDirectory, "Originals", "2.999");
            var v2_99993 = Path.Combine(scriptsDirectory, "Originals", "2.9993");
            var v2_6 = Path.Combine(scriptsDirectory, "Originals", "2.6");

            var v2_9999_modified_Files = Directory.GetFiles(v2_9999_modified, "*", SearchOption.AllDirectories);
            var v2_9999_Files = Directory.GetFiles(v2_9999, "*", SearchOption.AllDirectories);
            var v2_99993_Files = Directory.GetFiles(v2_99993, "*", SearchOption.AllDirectories);
            var v2_6_Files = Directory.GetFiles(v2_6, "*", SearchOption.AllDirectories);

            var pythonFolder = Path.Combine(_NoesisFolder, "plugins", "python");
            var maxscriptFolder = Path.Combine(pythonFolder, "Noesis Maxscript");
            switch (version)
            {
                case NoesisVersions.v2_9999_modified:
                    RemoveFiles(v2_9999_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    RemoveFiles(v2_99993_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    RemoveFiles(v2_6_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    CloneDirectory(v2_9999_modified, pythonFolder);
                    break;
                case NoesisVersions.v2_9999:
                    RemoveFiles(v2_9999_modified_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    RemoveFiles(v2_99993_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    RemoveFiles(v2_6_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    CloneDirectory(v2_9999, pythonFolder);
                    break;
                case NoesisVersions.v2_99993:
                    RemoveFiles(v2_9999_modified_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    RemoveFiles(v2_9999_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    RemoveFiles(v2_6_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    CloneDirectory(v2_99993, pythonFolder);
                    break;
                case NoesisVersions.v2_6:
                    RemoveFiles(v2_9999_modified_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    RemoveFiles(v2_9999_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    RemoveFiles(v2_99993_Files.Select(z => Path.GetFileName(z)).ToArray(), pythonFolder, maxscriptFolder);
                    CloneDirectory(v2_6, pythonFolder);
                    break;
            }
        }

        public enum NoesisVersions
        {
            v2_99993,
            v2_9999,
            v2_9999_modified,
            v2_6,
            None
        }
    }
}