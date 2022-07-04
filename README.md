# MHR-Model-Converter

This is a program to convert base MH Rise armor mods over to the Sunbreak Demo, and eventually the full game on release.

Supported :
* Chain from .35 to .48
* Meshes base to sunbreak
* Texture renaming
* MDF2 (Player support only at present, weapons and NPC's will come shortly)

It can so far:
* Select a folder where the mod is being held
* Detect the noesis folder provided
* Create a new folder to hold converted files to keep the original and provide converted separately 
* Attempt conversion with latest noesis version (2.999) of base rise meshes to latest re7 format
* Convert failed conversions with a modified version of 2.999, of base rise meshes to latest re7 format
* Convert failed conversions of base rise meshes to fbx with modified version of 2.999 and placed in root folder named with _converted
* Error log detailing which files failed 
* Merge mdf2 files with an existing working mdf2 from the demo, with textures and properties being fully merged (Major help from the MDF2 Manager to even make this possible)
* Convert Chain files from .35 to .48
* Rename remaining file extensions to new file extensions
* Open file location of converted files

Installation:
1. Go to https://github.com/keegars/MHR-Model-Converter/releases and find the latest release, click assets and download the MHR-Model-Converter-8version*.zip
2. Unzip and place in folder on it's own, not within the root folder of Monster Hunter or within a mod folder
3. Run the provided executable
4. Pick the folder to convert
5. If any errors occur, press ok to the dialog box as it is a noesis warning
6. When converted folder opens in file explorer, check there is no errorlog.

Notes:
Meshes - 
** If there is an error log, there is now a PDF provided in the zip file to help facilitate fixing the mesh! Please read all the instructions and follow it through, it is simple and rather quick once you are use to it. Sadly, it cannot be further automated with the current scripts for noesis. **


Chains - 
There may be a few errors with the chains, as there is only so many file formats I can support at once. If there are any errors that occur, please share the errorlog.txt and the chain file that failed and I can check the issue.

Prefabs - 
Dytsers Physics Enabler will be updated shortly to support jiggles!

Contributions:  
  
**Please give credit where it is due, and include my name on any mods that use this converter.**  

MDF Manager for the template to convert MDF files over.  
Noesis tool for importing/exporting mesh files.  
Noesis scripts which none of this would've been possible.  
The Particular Pommels for their support and help with testing.
Mangie for providing help on chain and pfb files.  
Capcom for giving me the motivation to not lose our mods!!!  
