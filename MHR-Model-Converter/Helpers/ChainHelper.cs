using System;
using System.IO;
using MHR_Model_Converter.Chain;
using MHR_Model_Converter.Helpers;

namespace MHR_Model_Converter.Helper
{
    public static class ChainHelper
    {
        public static void ConvertChainFiles(string[] files, bool deleteOriginal = true)
        {
            foreach (var file in files)
            {
                var fileInfo = new FileInfo(file);

                if (fileInfo.Exists)
                {
                    try
                    {
                        var chain35 = new Chain.Chain(file, ChainEnums.ChainVersion.v35);
                        chain35.Populate();

                        var newFileBytes = chain35.Export(ChainEnums.ChainVersion.v48);
                        PathHelper.SaveFile(file.Replace(".35", ".48"), newFileBytes);
                    }
                    catch (Exception ex)
                    {                        
                        ErrorHelper.Log($"Failed to convert chain file: {file}");
                        ErrorHelper.Log($"Stack trace: {ex.Message} {ex.StackTrace} {ex.InnerException}");
                        ErrorHelper.Log($"Please share this with the developer.");
                    }

                    if (deleteOriginal)
                    {
                        fileInfo.Delete();
                    }
                }
            }
        }
    }
}