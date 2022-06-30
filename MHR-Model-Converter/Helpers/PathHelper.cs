using System.Collections.Generic;
using System.IO;
using System.Text;

namespace MHR_Model_Converter.Helpers
{
    public static class PathHelper
    {
        public static Dictionary<string, string> _fileTransform = new Dictionary<string, string>
        {
            {".chain.35", ".chain.48" },
            {".mesh.2109108288", ".mesh.2109148288" },
            {".mdf2.19", ".mdf2.23" }
        };

        public static DirectoryInfo CreateFolder(params string[] path)
        {
            var folder = new DirectoryInfo(Path.Combine(path));

            if (!folder.Exists)
            {
                folder.Create();
            }

            return folder;
        }

        public static void CloneDirectory(string root, string dest)
        {
            CloneDirectory(new DirectoryInfo(root), new DirectoryInfo(dest));
        }

        public static void CloneDirectory(DirectoryInfo root, DirectoryInfo dest)
        {
            foreach (var directory in root.GetDirectories())
            {
                string dirName = Path.GetFileName(directory.FullName);
                if (!Directory.Exists(Path.Combine(dest.FullName, dirName)))
                {
                    Directory.CreateDirectory(Path.Combine(dest.FullName, dirName));
                }
                CloneDirectory(directory, new DirectoryInfo(Path.Combine(dest.FullName, dirName)));
            }

            foreach (var file in root.GetFiles())
            {
                File.Copy(file.FullName, Path.Combine(dest.FullName, Path.GetFileName(file.FullName)), true);
            }
        }

        public static string[] GetFiles(string path, string search)
        {
            return Directory.GetFiles(path, search, SearchOption.AllDirectories);
        }

        public static void RenameFileExtensions(string selectedPath)
        {
            foreach (var transform in _fileTransform)
            {
                var files = GetFiles(selectedPath, $"*{transform.Key}");
                if (files.Length > 0)
                {
                    foreach (var file in files)
                    {
                        var newFile = file.Replace(transform.Key, transform.Value);

                        if (File.Exists(newFile))
                        {
                            File.Delete(newFile);
                        }
                        File.Move(file, newFile);
                    }
                }
            }
        }

        public static void RemoveFiles(string[] files, params string[] folders)
        {
            foreach (var folder in folders)
            {
                var folderInfo = new DirectoryInfo(folder);

                if (folderInfo.Exists)
                {
                    foreach (var file in files)
                    {
                        var fileInfo = new FileInfo(Path.Combine(folderInfo.FullName, Path.GetFileName(file)));

                        if (fileInfo.Exists)
                        {
                            fileInfo.Delete();
                        }
                    }
                }
            }
        }

        public static BinaryReader OpenFile(string filePath)
        {
            return new BinaryReader(new FileStream(filePath, FileMode.Open), Encoding.Unicode);
        }

        public static void SaveFile(string filePath, byte[] bytes)
        {
            using (var bw = new BinaryWriter(new FileStream(filePath, FileMode.Create)))
            {
                foreach (var value in bytes)
                {
                    bw.Write(value);
                }
            }
        }
    }
}