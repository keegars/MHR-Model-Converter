using System;
using System.IO;
using System.Windows.Forms;
using Microsoft.WindowsAPICodePack.Dialogs;

namespace MHR_Model_Converter.Helpers
{
    public static class FolderHelper
    {
        public static DirectoryInfo PickStaticFolder(params string[] path)
        {
            var folderPath = string.Empty;

            var folderDialog = new CommonOpenFileDialog();
            folderDialog.IsFolderPicker = true;
            folderDialog.InitialDirectory =   path.Length != 0 ? Path.Combine(path) : Environment.GetFolderPath(Environment.SpecialFolder.Desktop);

            var dialogResult = folderDialog.ShowDialog();

            if (dialogResult == CommonFileDialogResult.Ok)
            {
                folderPath = folderDialog.FileName;
            }

            return new DirectoryInfo(folderPath);
        }

        public static FileInfo PickExecutableFromFolder(string executableName, params string[] path)
        {
            var folderPath = string.Empty;

            var folderDialog = new CommonOpenFileDialog();
            folderDialog.IsFolderPicker = true;
            folderDialog.InitialDirectory = path.Length != 0 ? Path.Combine(path) : Environment.GetFolderPath(Environment.SpecialFolder.Desktop);

            var fileInfo = new FileInfo(Path.Combine(folderDialog.InitialDirectory, executableName));

            if (!fileInfo.Exists)
            {
                Console.WriteLine($"Please select the folder which {executableName} is located...");
            }

            while (!fileInfo.Exists)
            {
                if (folderDialog.ShowDialog() != CommonFileDialogResult.Ok)
                {
                    folderDialog.InitialDirectory = string.Empty;
                    break; //Quit out
                }

                fileInfo = new FileInfo(Path.Combine(folderDialog.InitialDirectory, executableName));

                if (!fileInfo.Exists)
                {
                    Console.WriteLine($"{executableName} not detected, please pick a folder where it does exist");
                }
            };

            return fileInfo;
        }
    }
}