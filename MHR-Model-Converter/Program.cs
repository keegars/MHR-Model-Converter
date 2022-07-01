using System;
using System.IO;
using System.Linq;
using MHR_Model_Converter.Helpers;
using static MHR_Model_Converter.Helper.ChainHelper;
using static MHR_Model_Converter.Helpers.CMDHelper;
using static MHR_Model_Converter.Helpers.FolderHelper;
using static MHR_Model_Converter.Helpers.MDFHelper;
using static MHR_Model_Converter.Helpers.NoesisHelper;
using static MHR_Model_Converter.Helpers.PathHelper;
using static MHR_Model_Converter.MDF.MDFEnums;

namespace MHR_Model_Converter
{
    public static class Program
    {
        [STAThread]
        private static void Main()
        {
            //Create folder to place converted files, essentially create a new folder with the contents in it
            Console.WriteLine("Please select the folder to convert...");

            //Pick a folder to convert files
            var baseFolder = PickStaticFolder(Environment.GetFolderPath(Environment.SpecialFolder.Desktop));

            if (!baseFolder.Exists)
            {
                return; //Quit out
            }

            //Create temp folder, then clone directory to the temp folder
            var baseConversionFolder = CreateFolder(Environment.CurrentDirectory, "Conversions");
            var conversionFolder = baseConversionFolder.CreateSubdirectory($"{DateTime.Now:yyyyMMdd_HHmmss}_{Path.GetFileName(baseFolder.FullName)}");
            CloneDirectory(baseFolder, conversionFolder);

            ErrorHelper.ConversionFolder = conversionFolder.FullName;

            //Pick noesis folder
            var noesisFileInfo = PickExecutableFromFolder("Noesis.exe", Environment.CurrentDirectory, "Noesis");

            if (!noesisFileInfo.Exists)
            {
                return; // Quit out
            }

            NoesisFilePath = noesisFileInfo.FullName;

            //Convert with v2.999
            //any failed conversions with v2.999 export to fbx with v2.999 modified and move to foot of conversion folder
            //any failed conversions with v2.999 export with modified v2.999 to produce "something"
            var fbxFile = ".fbx";
            var mhRiseBaseMesh = ".2008058288";
            var re7Mesh = ".2109108288";
            var sunbreakMesh = ".2109148288";

            //Convert with v2.9993 from base to sunbreak format
            var baseMeshes = GetFiles(conversionFolder.FullName, $"*{mhRiseBaseMesh}");
            var failedConversions = ConvertWithNoesis(baseMeshes, mhRiseBaseMesh, sunbreakMesh, NoesisVersions.v2_99993, false, "-rewrite");

            //Any failed conversions export base to re7 format with v2.999 modified
            ConvertWithNoesis(failedConversions, mhRiseBaseMesh, re7Mesh, NoesisVersions.v2_9999_modified, false, "-rewrite");

            //No longer providing the original fbx, as too many issues occuring with users
            ////Any failed conversions, export to fbx with v2.999 modified (use to be original v2.6, but modified can now export it with 'unknown' as material name), then move fbx to root folder
            ////Convert failed base to fbx and move
            //ConvertWithNoesis(failedConversions, mhRiseBaseMesh, fbxFile, NoesisVersions.v2_6, false, "-rewrite");
            //var fbxFiles = conversionFolder.GetFiles("*.fbx", SearchOption.AllDirectories).ToList();
            //fbxFiles.ForEach(z => File.Move(z.FullName, Path.Combine(conversionFolder.FullName, Path.GetFileName(z.FullName))));

            //Convert failed re7 to fbx and move
            var failedRe7Meshes = conversionFolder.GetFiles($"*{re7Mesh}", SearchOption.AllDirectories).ToList();
            var tmpfailedRe7Meshes = failedRe7Meshes.Where(z => failedConversions.Select(Path.GetFileNameWithoutExtension).Contains(Path.GetFileNameWithoutExtension(z.FullName))).Select(z => z.FullName).ToList();
            ConvertWithNoesis(tmpfailedRe7Meshes, re7Mesh, fbxFile, NoesisVersions.v2_9999_modified, true, "-rewrite");
            var fbxFiles = conversionFolder.GetFiles("*.fbx", SearchOption.AllDirectories).Where(z => Path.GetDirectoryName(z.FullName) != conversionFolder.FullName).ToList();
            fbxFiles.ForEach(z => File.Move(z.FullName, Path.Combine(conversionFolder.FullName, $"{Path.GetFileNameWithoutExtension(z.FullName)}_converted{fbxFile}")));

            //Move failed conversion meshes to conversion folder root
            failedConversions.ForEach(z => File.Move(z, Path.Combine(conversionFolder.FullName, Path.GetFileName(z))));

            //Print out an error log saying which files failed, and that it will most likely be due to the naming conventions and material names.
            //Naming convention must be: The naming scheme of meshes must match the Noesis plugin format: LODGroup_X_MainMesh_Y_SubMesh_Z__materialName
            foreach (var failure in failedConversions)
            {
                ErrorHelper.Log($"Failed to convert file: {failure} {Environment.NewLine} Most likely case will be the naming convention for the meshes and material name not matching, please update the fbx in blender using the following naming scheme: LODGroup_X_MainMesh_Y_SubMesh_Z__materialName . E.g. LODGroup_1_MainMesh_1_SubMesh_1__fskin, LODGroup_1_MainMesh_1_SubMesh_2__fbody etc, incrementing the submesh and adding the material name each time. DO NOTE: there must be two underscores before the material name when naming the mesh. {Environment.NewLine}{Environment.NewLine}");              
            }

            //Remove each base mesh file
            baseMeshes.Select(z => new FileInfo(z)).Where(z => z.Exists).ToList().ForEach(z => File.Delete(z.FullName));

            //-------------------------------------------------
            //MDF2 Conversion
            //Need to add in the detection for hand textures, as some old mods have issues and will need to copy files across...need to check when sunbreak is released that this doesn't happen anymore.
            //-------------------------------------------------
            var mdfFiles = GetFiles(conversionFolder.FullName, "*.mdf2.19");
            ConvertMDFFiles(mdfFiles, MDFConversion.MergeAndAddMissingProperties);

            //Convert chain files from .35 to .48, can be reversed, but no need.
            var chains = GetFiles(conversionFolder.FullName, "*.chain.35");
            ConvertChainFiles(chains);

            //Rename File Extensions for each: tex, mesh, mdf2, chain
            RenameFileExtensions(conversionFolder.FullName);

            //Make sure Noesis is using the latest version
            NoesisHelper.CopyVersionFiles(NoesisVersions.v2_99993);

            //Open Folder Location with file explorer
            OpenExplorerLocation(conversionFolder.FullName);
        }
    }
}