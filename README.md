# MHR-Model-Converter

This is a program to convert base MH Rise armor mods over to the Sunbreak Demo, and eventually the full game on release.

It can so far:
* Select a folder where the mod is being held
* Detect the noesis folder provided
* Create a new folder to hold converted files to keep the original and provide converted separately 
* Attempt conversion with latest noesis version (2.999) of base rise meshes to latest re7 format
* Convert failed conversions with a modified version of 2.999, of base rise meshes to latest re7 format
* Convert failed conversions of base rise meshes to fbx with version 2.6 and place in root folder for easy access
* Convert failed conversions of base rise meshes to fbx with modified version of 2.999 and placed in root folder named with _converted
* Error log detailing which files failed 
* Convert .24 texture files to .34
* Rename remaining file extensions to new file extensions
* Open file location of converted files

TODO:
* Chain files currently cause .pak files to crash, need to find how to convert over
* Pfb files not currently supported
* MDF2 merging/replace/addition to new format needing added (working version is made, but need options added)

Installation:
1. Place in folder on it's own, not within the root folder of Monster Hunter or within a mod folder
2. Run the provided executable
3. Pick the folder to convert
4. If any errors occur, press ok to the dialog box as it is a noesis warning
5. When converted folder opens in file explorer, check there is no errorlog.

Notes:
If there is an error log when converting a file, you will need to fix the mesh with blender. Assuming you created the mod, this should be rather straight forward and you can use the original fbx provided or the converted, the only difference is that the converted has the new mesh naming and you only need to fix the material and add the material name to the mesh naming convention. By default, the material has been renamed to 'unknown' to allow noesis to export it.

Once the mesh has been fixed, you can open noesis.exe, navigate to the fixed .fbx and attempt to export to RE7 mesh (.2109108288) and if it succeeds, rename extension to .2109148288 and move to the correct armor folder.
