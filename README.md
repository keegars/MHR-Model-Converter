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
* Merge mdf2 files with an existing working mdf2 from the demo, with textures and properties being fully merged (Major help from the MDF2 Manager to even make this possible)
* Convert Chain files from .35 to .48
* Rename remaining file extensions to new file extensions
* Open file location of converted files

Installation:
1. Place in folder on it's own, not within the root folder of Monster Hunter or within a mod folder
2. Run the provided executable
3. Pick the folder to convert
4. If any errors occur, press ok to the dialog box as it is a noesis warning
5. When converted folder opens in file explorer, check there is no errorlog.

Notes:
Meshes - 
If there is an error log when converting a file, you will need to fix the mesh with blender. Assuming you created the mod, this should be rather straight forward and you can use the original fbx provided or the converted, the only difference is that the converted has the new mesh naming and you only need to fix the material and add the material name to the mesh naming convention. By default, the material has been renamed to 'unknown' to allow noesis to export it.

Once the mesh has been fixed, you can open noesis.exe, navigate to the fixed .fbx and attempt to export to RE7 mesh (.2109108288) and if it succeeds, rename extension to .2109148288 and move to the correct armor folder.

Chains - 
There may be a few errors with the chains, as there is only so many file formats I can support at once. If there are any errors that occur, please share the errorlog.txt and the chain file that failed and I can check the issue.

Contributions:  
  
**Please give credit where it is due, and include my name on any mods that use this converter.**  

MDF Manager for the template to convert MDF files over.  
Noesis tool for importing/exporting mesh files.  
Noesis scripts which none of this would've been possible.  
Mangie for providing help on chain and pfb files.  
Capcom for giving me the motivation to not lose our mods!!!  
