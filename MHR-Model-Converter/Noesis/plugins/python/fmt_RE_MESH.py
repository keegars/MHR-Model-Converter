#RE Engine [PC] - ".mesh" plugin
#v2.6 (August 16 2021)
#By alphaZomega and Gh0stblade 
#Special thanks: Chrrox 

#Options: These are global options that change or enable/disable certain features

#Var												Effect
#Export Extensions
fExportExtension 			= ".1902042334"			#You can set the default MESH export extension here (.1902042334 for RE3, .1808312334 for RE2, .1808282334 for DMC5)
bRE2Export 					= True					#Enable or disable export of mesh.1808312334 and tex.10 from the export list			
bRE3Export 					= True					#Enable or disable export of mesh.1902042334 and tex.190820018 from the export list
bDMCExport 					= True					#Enable or disable export of mesh.1808282334 and tex.11 from the export list
bRE7Export 					= True					#Enable or disable export of mesh.32 and tex.8 from the export list
bREVExport 					= True					#Enable or disable export of mesh.2010231143 from the export list (and tex.30)
bRE8Export 					= True					#Enable or disable export of mesh.2101050001 from the export list (and tex.30)

#Mesh Global
fDefaultMeshScale 			= 100.0 				#Override mesh scale (default is 1.0)
bMaterialsEnabled 			= True					#Materials (1 = on, 0 = off)
bRenderAsPoints 			= False					#Render mesh as points without triangles drawn (1 = on, 0 = off)
bImportAllLODs 				= False					#Imports all LODGroups (as separate models)

#Vertex Components (Import)
bNORMsEnabled 				= True					#Normals (1 = on, 0 = off)
bTANGsEnabled 				= True					#Tangents (1 = on, 0 = off)
bUVsEnabled 				= True					#UVs (1 = on, 0 = off))
bSkinningEnabled 			= True					#Enable skin weights (1 = on, 0 = off)
bDebugNormals 				= False					#Debug normals as RGBA
bDebugTangents 				= False					#Debug tangents as RGBA
            
#Import Options
bPrintMDF 					= True					#Prints debug info for MDF files (1 = on, 0 = off)
bDebugMESH 					= False					#Prints debug info for MESH files (1 = on, 0 = off)
bPopupDebug 				= True					#Pops up debug window on opening MESH with MDF (1 = on, 0 = off)
bPrintFileList 				= True					#Prints a list of files used by the MDF
bColorize 					= False					#Colors the materials of the model and lists which material is which color
bUseOldNamingScheme 		= False					#Names submeshes by their material ID (like in the MaxScript) rather than by their order in the file 
bRenameMeshesToFilenames 	= False					#For use with Noesis Model Merger. Renames submeshes to have their filenames in the mesh names

#Export Options
bNormalizeWeights 			= False					#Makes sure that the weights of every vertex add up to 1.0, giving the remainder to the bone with the least influence
bDoAutoScale 				= False					#

#Import/Export:
bAddBoneNumbers 			= False					#Adds bone numbers like the MaxScript. If rewriting the skeleton, enable this to make only bones with bone numbers be in the riggable bone map

from inc_noesis import *
import math
import os
import re
import copy

def registerNoesisTypes():
	handle = noesis.register("RE Engine MESH [PC]", ".1902042334;.1808312334;.1808282334;.2008058288;.2010231143;.2101050001;.32;.NewMesh")
	noesis.setHandlerTypeCheck(handle, meshCheckType)
	noesis.setHandlerLoadModel(handle, meshLoadModel)
	noesis.addOption(handle, "-noprompt", "Do not prompt for MDF file", 0)
	noesis.setTypeSharedModelFlags(handle, (noesis.NMSHAREDFL_WANTGLOBALARRAY))
	
	handle = noesis.register("RE Engine Texture [PC]", ".10;.190820018;.11;.8;.30")
	noesis.setHandlerTypeCheck(handle, texCheckType)
	noesis.setHandlerLoadRGBA(handle, texLoadDDS)

	if bRE2Export:
		handle = noesis.register("RE2 Remake Texture [PC]", ".10")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
		handle = noesis.register("RE2 MESH", (".1808312334"))
		noesis.setHandlerTypeCheck(handle, meshCheckType)
		noesis.setHandlerWriteModel(handle, meshWriteModel)
		noesis.setTypeExportOptions(handle, "-noanims")
		noesis.addOption(handle, "-bones", "Write new skeleton on export", 0)
		#noesis.addOption(handle, "-rewrite", "Rewrite submeshes and materials structure", 0)
		noesis.addOption(handle, "-flip", "Reverse handedness from DirectX to OpenGL", 0)
		noesis.addOption(handle, "-bonenumbers", "Add bone numbers to imported bones", 0)
		noesis.addOption(handle, "-meshfile", "Reverse handedness from DirectX to OpenGL", noesis.OPTFLAG_WANTARG)
	if bRE3Export:
		handle = noesis.register("RE3 Remake Texture [PC]", ".190820018")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
		handle = noesis.register("RE3 MESH", (".1902042334"))
		noesis.setHandlerTypeCheck(handle, meshCheckType)
		noesis.setHandlerWriteModel(handle, meshWriteModel)
		noesis.setTypeExportOptions(handle, "-noanims")
		noesis.addOption(handle, "-bones", "Write new skeleton on export", 0)
		#noesis.addOption(handle, "-rewrite", "Rewrite submeshes and materials structure", 0)
		noesis.addOption(handle, "-flip", "Reverse handedness from DirectX to OpenGL", 0)
		noesis.addOption(handle, "-bonenumbers", "Add bone numbers to imported bones", 0)
		noesis.addOption(handle, "-meshfile", "Reverse handedness from DirectX to OpenGL", noesis.OPTFLAG_WANTARG)
	if bDMCExport:
		handle = noesis.register("Devil May Cry 5 Texture [PC]", ".11")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
		handle = noesis.register("DMC5 MESH", (".1808282334"))
		noesis.setHandlerTypeCheck(handle, meshCheckType)
		noesis.setHandlerWriteModel(handle, meshWriteModel)
		noesis.setTypeExportOptions(handle, "-noanims")
		noesis.addOption(handle, "-bones", "Write new skeleton on export", 0)
		#noesis.addOption(handle, "-rewrite", "Rewrite submeshes and materials structure", 0)
		noesis.addOption(handle, "-flip", "Reverse handedness from DirectX to OpenGL", 0)
		noesis.addOption(handle, "-bonenumbers", "Add bone numbers to imported bones", 0)
		noesis.addOption(handle, "-meshfile", "Reverse handedness from DirectX to OpenGL", noesis.OPTFLAG_WANTARG)
	if bREVExport or bRE8Export:
		handle = noesis.register("RE8 / ReVerse Texture [PC]", ".30")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA);
	if bREVExport:
		handle = noesis.register("ReVerse MESH", (".2010231143"))
		noesis.setHandlerTypeCheck(handle, meshCheckType)
		noesis.setHandlerWriteModel(handle, meshWriteModel)
		noesis.setTypeExportOptions(handle, "-noanims")
		noesis.addOption(handle, "-bones", "Write new skeleton on export", 0)
		#noesis.addOption(handle, "-rewrite", "Rewrite submeshes and materials structure", 0)
		noesis.addOption(handle, "-flip", "Reverse handedness from DirectX to OpenGL", 0)
		noesis.addOption(handle, "-bonenumbers", "Add bone numbers to imported bones", 0)
		noesis.addOption(handle, "-meshfile", "Reverse handedness from DirectX to OpenGL", noesis.OPTFLAG_WANTARG)
	if bRE8Export:
		handle = noesis.register("RE8 MESH", (".2101050001"))
		noesis.setHandlerTypeCheck(handle, meshCheckType)
		noesis.setHandlerWriteModel(handle, meshWriteModel)
		noesis.setTypeExportOptions(handle, "-noanims")
		noesis.addOption(handle, "-bones", "Write new skeleton on export", 0)
		#noesis.addOption(handle, "-rewrite", "Rewrite submeshes and materials structure", 0)
		noesis.addOption(handle, "-flip", "Reverse handedness from DirectX to OpenGL", 0)
		noesis.addOption(handle, "-bonenumbers", "Add bone numbers to imported bones", 0)
		noesis.addOption(handle, "-meshfile", "Reverse handedness from DirectX to OpenGL", noesis.OPTFLAG_WANTARG)
	if bRE7Export:
		handle = noesis.register("Resident Evil 7 Texture [PC]", ".8")
		noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
		handle = noesis.register("RE7 MESH", (".32"))
		noesis.setHandlerTypeCheck(handle, meshCheckType)
		noesis.setHandlerWriteModel(handle, meshWriteModel)
		noesis.setTypeExportOptions(handle, "-noanims")
		noesis.addOption(handle, "-bones", "Write new skeleton on export", 0)
		#noesis.addOption(handle, "-rewrite", "Rewrite submeshes and materials structure", 0)
		noesis.addOption(handle, "-flip", "Reverse handedness from DirectX to OpenGL", 0)
		noesis.addOption(handle, "-bonenumbers", "Add bone numbers to imported bones", 0)
		noesis.addOption(handle, "-meshfile", "Reverse handedness from DirectX to OpenGL", noesis.OPTFLAG_WANTARG)
		
	noesis.logPopup()
	return 1

def meshCheckType(data):
	bs = NoeBitStream(data)
	magic = bs.readUInt()
	if magic == 0x4853454D:
		return 1
	if magic == 0x4853414d:
		return 1	
	else: 
		print("Fatal Error: Unknown file magic: " + str(hex(magic) + " expected 'MESH'!"))
		return 0

def texCheckType(data):
	bs = NoeBitStream(data)
	magic = bs.readUInt()
	if magic == 0x00584554:
		return 1
	else: 
		print("Fatal Error: Unknown file magic: " + str(hex(magic) + " expected TEX!"))
		return 0
	
def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c
	
def dot(v1, v2):
	return sum(x*y for x,y in zip(v1,v2))
	
def texLoadDDS(data, texList):
	bs = NoeBitStream(data)
	
	magic = bs.readUInt()
	version = bs.readUInt()
	width = bs.readUShort()
	height = bs.readUShort()
	unk00 = bs.readUShort()
	mipCount = bs.readUByte()
	numImages = bs.readUByte()
	
	format = bs.readUInt()
	unk02 = bs.readUInt()
	unk03 = bs.readUInt()
	unk04 = bs.readUInt()
	
	mipData = []
	mipDataAll = []
	if version == 30:
		bs.seek(8,1)
	
	for i in range(numImages):
		for j in range(mipCount):
			mipData.append([bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
		mipDataAll.append(mipData[i])
		
	bs.seek(mipDataAll[0][0])
	texData = bs.readBytes(mipDataAll[0][3])
		
	texFormat = noesis.NOESISTEX_RGBA32
	if format == 29 or  format == 28:
		fmtName = ("r8g8b8a8")
		texData = rapi.imageDecodeRaw(texData, width, height, "r8g8b8a8")
	elif format == 61:
		fmtName = ("r8")
		texData = rapi.imageDecodeRaw(texData, width, height, "r8")
	elif format == 10:
		fmtName = ("r16g16b16a16")
		texData = rapi.imageDecodeRaw(texData, width, height, "r16g16b16a16")
	elif format == 2:
		fmtName = ("r32g32b32a32")
		texData = rapi.imageDecodeRaw(texData, width, height, "r32g32b32a32", 1)
	#elif format == 28:
	#	print ("FOURCC_ATI1")
	#	texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_ATI1)
	elif format == 71 or format == 72: #ATOS
		fmtName = ("FOURCC_DXT1")
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_DXT1)
	elif format == 77: #BC3
		fmtName = ("FOURCC_BC3")
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC3)
	elif format == 80: #BC4 wetmasks
		fmtName = ("FOURCC_BC4")
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC4)
	elif format == 83: #BC5
		fmtName = ("FOURCC_BC5")
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC5)
	elif format == 95:
		fmtName = ("FOURCC_BC6H")
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC6H)
	elif format == 98 or format == 99:
		texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
		fmtName = ("FOURCC_BC7")
	else:
		print("Fatal Error: Unsupported texture type: " + str(format))
		return 0
		
	if bPrintMDF:
		print(fmtName, "(", format, ")")
		
	texList.append(NoeTexture(rapi.getInputName(), int(width), int(height), texData, texFormat))
	return 1
	
def texWriteRGBA(data, width, height, bs):
	bTexAsSource = False
	print ("\n			----RE Engine TEX Export----\n")
	def getExportName(fileName):		
		if fileName == None:
			newTexName = rapi.getOutputName().lower()
		else: newTexName = fileName
		
		while newTexName.find("out.") != -1: newTexName = newTexName.replace("out.",".")
		newTexName =  newTexName.replace(".dds","").replace(".tex","").replace(".10","").replace(".190820018","").replace(".11","").replace(".8","").replace(".30","").replace(".jpg","").replace(".png","").replace(".tga","").replace(".gif","").replace(".8","")
		ext = ".tex.10"
		if rapi.checkFileExists(newTexName + ".tex.190820018"):
			ext = ".tex.190820018"
		elif rapi.checkFileExists(newTexName + ".tex.11"):
			ext = ".tex.11"
		elif rapi.checkFileExists(newTexName + ".tex.8"):
			ext = ".tex.8"
		elif rapi.checkFileExists(newTexName + ".tex.30"):
			ext = ".tex.30"
			
		newTexName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Export over tex", "Choose a tex file to export over", newTexName + ext, None)
		if newTexName == None:
			print("Aborting...")
			return
		return newTexName
		
	fileName = None
	newTexName = getExportName(fileName)
	if newTexName == None:
		return 0
	while not (rapi.checkFileExists(newTexName)):
		print ("File not found")
		newTexName = getExportName(fileName)	
		fileName = newTexName
		if newTexName == None:
			return 0	
			
	newTEX = rapi.loadIntoByteArray(newTexName)
	oldDDS = rapi.loadIntoByteArray(rapi.getInputName())
	f = NoeBitStream(newTEX)
	og = NoeBitStream(oldDDS)

	magic = f.readUInt()
	version = f.readUInt()
	reVerseSize = 8 if version == 30 else 0
	f.seek(14)
	maxMips = f.readUByte()
	reVMipCount = int(f.readUByte() / 16)
	if version == 30: maxMips = reVMipCount
	
	ddsMagic = og.readUInt()
	bDoEncode = False
	if magic != 5784916:
		print ("Selected file is not a TEX file!\nAborting...")
		return 0
		
	f.seek(16)
	imgType = f.readUInt()
	print ("TEX type:", imgType)
	
	ddsFmt = 0
	bQuitIfEncode = False
	try:
		if imgType == 71 or imgType == 72: ddsFmt = noesis.NOE_ENCODEDXT_BC1
		elif imgType == 80: ddsFmt = noesis.NOE_ENCODEDXT_BC4
		elif imgType == 83: ddsFmt = noesis.NOE_ENCODEDXT_BC5
		elif imgType == 95: ddsFmt = noesis.NOE_ENCODEDXT_BC6H
		elif imgType == 98 or imgType == 99: ddsFmt = noesis.NOE_ENCODEDXT_BC7
		elif imgType == 28 or imgType == 29: ddsFmt = "r8g8b8a8"
		elif imgType == 77: ddsFmt = noesis.NOE_ENCODEDXT_BC3;
		elif imgType == 10: ddsFmt = "r16g16b16a16"
		elif imgType == 61: ddsFmt = "r8"
		else: 
			print ("Unknown TEX type:", imgType)
			if imgType != 10:
				return 0
	except: 
		bQuitIfEncode = True

	print ("Exporting over \"" + rapi.getLocalFileName(newTexName)+ "\"")
	
	texFmt = ddsFmt
	#headerSize = 0
	if ddsMagic == 542327876: #DDS
		headerSize = og.readUInt() + 4
		og.seek(84)
		if og.readUInt() == 808540228: #DX10
			headerSize += 20
			if ddsFmt == noesis.NOE_ENCODEDXT_BC1:
				print ("Source DDS encoding (BC7) does not match TEX file (BC1).\nEncoding image...")
				bDoEncode = True
		elif ddsFmt == noesis.NOE_ENCODEDXT_BC7:
			print ("Source DDS encoding (BC1) does not match TEX file (BC7).\nEncoding image...")
			bDoEncode = True
	elif ddsMagic == 5784916: #TEX
		bTexAsSource = True
		og.seek(8)
		ogWidth = og.readUShort()
		ogHeight = og.readUShort()
		print (width, height, ogWidth, ogHeight)
		if ogWidth != width or ogHeight != height: 
			print ("Input TEX file uses a different resolution from Source TEX file.\nEncoding image...")
			bDoEncode = True
		og.seek(14)
		headerSize = og.readUByte() * 16 + 32
		if version == 30: 
			headerSize = 40 + og.readUByte()
		og.seek(16)
		srcType = og.readUInt()  
		if srcType == 71 or srcType == 72: texFmt = noesis.NOE_ENCODEDXT_BC1
		elif srcType == 80: texFmt = noesis.NOE_ENCODEDXT_BC4
		elif srcType == 83: ddsFmt = noesis.NOE_ENCODEDXT_BC5
		elif srcType == 95: texFmt = noesis.NOE_ENCODEDXT_BC6H
		elif srcType == 98 or srcType == 99: texFmt = noesis.NOE_ENCODEDXT_BC7
		elif srcType == 28 or srcType == 29: texFmt = "r8g8b8a8"
		elif srcType == 77: texFmt = noesis.NOE_ENCODEDXT_BC3;
		elif srcType == 10: texFmt = "r16g16b16a16"
		elif srcType == 61: texFmt = "r8"
		else: 
			print ("Unknown TEX type:", srcType)
			return 0
		if texFmt != ddsFmt or (os.path.splitext(newTexName)[1] == ".30" and os.path.splitext(rapi.getInputName())[1] != ".30"): 
			print ("Input TEX file uses a different compression or format from Source TEX file.\nEncoding image...")
			bDoEncode = True
	else: 
		print ("Input file is not a DDS or TEX file\nEncoding image...")
		bDoEncode = True
	
	mipSize = width * height
	if texFmt == noesis.NOE_ENCODEDXT_BC1: mipSize = int(mipSize / 2)
	if not bDoEncode and mipSize < int((os.path.getsize(rapi.getInputName())) / 4):
		print ("Unexpected source image size\nEncoding image...")
		bDoEncode = True
	
	if not bDoEncode: 
		print ("Copying image data from \"" + rapi.getLocalFileName(rapi.getInputName()) + "\"")
	elif bQuitIfEncode:
		print ("Fatal Error: BC7 Encoding not supported!\nUpdate to Noesis v4434 (Oct 14, 2020) or later to encode BC7 images\nAborting...\n")
		return 0
		
	#copy header
	f.seek(0)
	bs.writeBytes(f.readBytes(32 + reVerseSize))
	
	numMips = 0
	dataSize = 0
	totalData = 0
	sizeArray = []
	fileData = []
	mipWidth = width
	mipHeight = height
	
	#write mipmap headers & encode image
	while mipWidth > 4 or mipHeight > 4:
		if (numMips == maxMips) or (ddsFmt == "r8" and numMips > 1):
			break
		numMips += 1
		if bDoEncode:
			mipData = rapi.imageResample(data, width, height, mipWidth, mipHeight)
			try:
				dxtData = rapi.imageEncodeDXT(mipData, 4, mipWidth, mipHeight, ddsFmt)
			except:
				dxtData = rapi.imageEncodeRaw(mipData, mipWidth, mipHeight, ddsFmt)
			mipSize = len(dxtData)
			fileData.append(dxtData)
			
		else:
			mipSize = mipWidth * mipHeight
			if texFmt == noesis.NOE_ENCODEDXT_BC1:
				mipSize = int(mipSize / 2)
			
		sizeArray.append(dataSize)
		dataSize += mipSize
		
		pitch = 4 * mipWidth
		if ddsFmt == noesis.NOE_ENCODEDXT_BC1:
			pitch = int(pitch / 2)
			
		bs.writeUInt64(0)
		bs.writeUInt(pitch)
		bs.writeUInt(mipSize)
		
		print ("Mip", numMips, ": ", mipWidth, "x", mipHeight, "\n            ", pitch, "\n            ", mipSize)
		if mipWidth > 4: mipWidth = int(mipWidth / 2)
		if mipHeight > 4: mipHeight = int(mipHeight / 2)
	
	if bDoEncode: 
		for d in range(len(fileData)): #write image data
			bs.writeBytes(fileData[d])
	else:
		og.seek(headerSize) #copy image data
		bs.writeBytes(og.readBytes(os.path.getsize(rapi.getInputName()) - headerSize))

	#adjust header
	bs.seek(28)
	if reVerseSize > 0:
		bs.writeUByte(128) #ReVerse streaming
	else: bs.writeUByte(0) #streaming texture
		
	bs.seek(8)
	bs.writeUShort(width)
	bs.writeUShort(height)
	if version == 30:
		bs.seek(15)
		bs.writeUByte(numMips * 16)
	else:
		bs.seek(14)
		bs.writeUByte(numMips)
	
	bsHeaderSize = maxMips * 16 + 32 + reVerseSize
	bs.seek(32 + reVerseSize)
	
	for mip in range(numMips):
		bs.writeUInt64(sizeArray[mip] + bsHeaderSize)
		bs.seek(8, 1)	

	return 1
	
def ReadUnicodeString(bs):
	numZeroes = 0
	resultString = ""
	while(numZeroes < 2):
		c = bs.readUByte()
		if c == 0:
			numZeroes+=1
			continue
		else:
			numZeroes = 0
		resultString += chr(c)
	return resultString
		
def GetRootGameDir():
	path = rapi.getDirForFilePath(rapi.getInputName())
	while len(path) > 3:
		lastFolderName = os.path.basename(os.path.normpath(path)).lower()
		if lastFolderName == "stm" or lastFolderName == "x64":
			break
		else:
			path = os.path.normpath(os.path.join(path, ".."))
	return path	+ "\\"
	
def LoadExtractedDir():
	nativesPath = ""
	try: 
		with open(noesis.getPluginsPath() + '\python\\' + fGameName + 'NativesPath.txt') as fin:
			nativesPath = fin.read()
			fin.close()
	except IOError:
		pass
	if not os.path.isdir(nativesPath):
		return ""
	return nativesPath
		
def SaveExtractedDir(dirIn):
	try: 
		print (noesis.getPluginsPath() + 'python\\' + fGameName + 'NativesPath.txt')
		with open(noesis.getPluginsPath() + 'python\\' + fGameName + 'NativesPath.txt', 'w') as fout:
			print ("Writing string: " + dirIn + " to " + noesis.getPluginsPath() + 'python\\' + fGameName + 'NativesPath.txt')
			fout.flush()
			fout.write(str(dirIn))
			fout.close()
	except IOError:
		print ("Failed to save natives path: IO Error")
		return 0
	return 1

#murmur3 hash algorithm
#Credit to Darkness for adapting this
def hash(key, seed=0xffffffff):
    key = bytearray(key, 'utf8')

    def fmix(h):
        h ^= h >> 16
        h = (h * 0x85ebca6b) & 0xFFFFFFFF
        h ^= h >> 13
        h = (h * 0xc2b2ae35) & 0xFFFFFFFF
        h ^= h >> 16
        return h

    length = len(key)
    nblocks = int(length / 4)

    h1 = seed

    c1 = 0xcc9e2d51
    c2 = 0x1b873593

    for block_start in range(0, nblocks * 4, 4):
        k1 = key[block_start + 3] << 24 | \
             key[block_start + 2] << 16 | \
             key[block_start + 1] << 8 | \
             key[block_start + 0]

        k1 = (c1 * k1) & 0xFFFFFFFF
        k1 = (k1 << 15 | k1 >> 17) & 0xFFFFFFFF
        k1 = (c2 * k1) & 0xFFFFFFFF

        h1 ^= k1
        h1 = (h1 << 13 | h1 >> 19) & 0xFFFFFFFF
        h1 = (h1 * 5 + 0xe6546b64) & 0xFFFFFFFF

    tail_index = nblocks * 4
    k1 = 0
    tail_size = length & 3

    if tail_size >= 3:
        k1 ^= key[tail_index + 2] << 16
    if tail_size >= 2:
        k1 ^= key[tail_index + 1] << 8
    if tail_size >= 1:
        k1 ^= key[tail_index + 0]

    if tail_size > 0:
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = (k1 << 15 | k1 >> 17) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1

    unsigned_val = fmix(h1 ^ length)
    if unsigned_val & 0x80000000 == 0:
        return unsigned_val
    else:
        return -((unsigned_val ^ 0xFFFFFFFF) + 1)


def hash_wide(key, seed=0xffffffff):
    key_temp = ''

    for char in key:
        key_temp += char + '\x00'

    return hash(key_temp, seed)
	
class meshFile(object): 

	def __init__(self, data):
		self.inFile = NoeBitStream(data)
		self.boneList = []
		self.matNames = []
		self.matHashes = []
		self.matList = []
		self.texList = []
		self.texNames = []
		self.missingTexNames = []
		self.texColors = []
	
	def createMaterials(self):
		global bColorize, bPrintMDF, fGameName, fExportExtension
		noMDFFound = 0
		skipPrompt = 0
		
		nDir = "x64"
		mdfExt = ".mdf2.10"
		modelExt= ".1808312334" 
		texExt = ".10"
		mmtrExt = ".1808160001"
		
		if fGameName == "DMC5":
			modelExt = ".1808282334"
			texExt = ".11"
			mmtrExt = ".1808168797"
		elif fGameName == "RE3":
			modelExt = ".1902042334"
			texExt = ".190820018"
			mmtrExt = ".1905100741"
			nDir = "stm"
			mdfExt = ".mdf2.13"		
		elif fGameName == "REVerse":
			modelExt = ".2010231143"
			texExt = ".30"
			mmtrExt = ".2011178797"
			nDir = "stm"
			mdfExt = ".mdf2.19"
		elif fGameName == "RE8":
			modelExt = ".2101050001"
			texExt = ".30"
			mmtrExt = ".2102188797"
			nDir = "stm"
			mdfExt = ".mdf2.19"
		elif fGameName == "MHRise":
			modelExt = ".2008058288"
			texExt = ".28"
			mmtrExt = ".2007288797"
			nDir = "NSW"
			mdfExt = ".mdf2.19"
		elif fGameName == "RE7":
			modelExt = ".32"
			texExt = ".8"
			mmtrExt = ".69"
			nDir = "x64"
			mdfExt = ".mdf2.6"
			
		print (fGameName)
		fExportExtension = modelExt
		
		extractedNativesPath = LoadExtractedDir()
		
		#Try to find & save extracted game dir for later if extracted game dir is unknown
		if extractedNativesPath == "":
			dirName = GetRootGameDir()
			if (dirName.endswith("chunk_000\\natives\\" + nDir + "\\")):
				print ("Saving extracted natives path...")
				if SaveExtractedDir(dirName):
					extractedNativesPath = dirName
					
		if extractedNativesPath != "":
			print ("Using this extracted natives path:", extractedNativesPath + "\n")
		pathPrefix = rapi.getInputName().replace(modelExt,"").replace(".NEW", "")
		while pathPrefix.find("out.") != -1: pathPrefix = pathPrefix.replace("out.",".")
		if fGameName == "REVerse" and os.path.isdir(os.path.dirname(rapi.getInputName()) + "\\Material"):
			pathPrefix = (os.path.dirname(rapi.getInputName()) + "\\Material\\" + rapi.getLocalFileName(rapi.getInputName()).replace("SK_", "M_")).replace(".NEW", "")
			while pathPrefix.find("out.") != -1: pathPrefix = pathPrefix.replace("out.",".")
			pathPrefix = pathPrefix.replace(".mesh" + modelExt,"")
			if not rapi.checkFileExists(pathPrefix + mdfExt):
				pathPrefix = pathPrefix.replace("00_", "")
			if not rapi.checkFileExists(pathPrefix + mdfExt):
				for item in os.listdir(os.path.dirname(pathPrefix + mdfExt)):
					if mdfExt == (".mdf2" + os.path.splitext(os.path.join(os.path.dirname(pathPrefix), item))[1]):
						pathPrefix = os.path.join(os.path.dirname(pathPrefix), item).replace(mdfExt, "")
						break
			print (pathPrefix + mdfExt) 
		similarityCounter = 0
		ogFileName = rapi.getLocalFileName(rapi.getInputName())
		if not rapi.checkFileExists(pathPrefix + mdfExt):
			for item in os.listdir(os.path.dirname(pathPrefix + mdfExt)):
				if mdfExt == (".mdf2" + os.path.splitext(os.path.join(os.path.dirname(pathPrefix), item))[1]):
					test = rapi.getLocalFileName(os.path.join(os.path.dirname(pathPrefix), item).replace(mdfExt, ""))
					sameCharCntr = 0
					for c, char in enumerate(test):
						if c < len(ogFileName) and char == ogFileName[c]:
							sameCharCntr += 1
					if sameCharCntr > similarityCounter:
						pathPrefix = os.path.join(os.path.dirname(pathPrefix), item).replace(mdfExt, "")
						similarityCounter = sameCharCntr
					
		materialFileName = (pathPrefix + mdfExt)
		
		if not (rapi.checkFileExists(materialFileName)):
			materialFileName = (pathPrefix + "_mat" + mdfExt)
		if not (rapi.checkFileExists(materialFileName)):
			materialFileName = (pathPrefix + "_00" + mdfExt)
		if not (rapi.checkFileExists(materialFileName)):
			if fGameName == "RE3" or fGameName == "REVerse" or fGameName == "RE8":
				pathPrefix = extractedNativesPath + re.sub(r'.*stm\\', '', rapi.getInputName())
			elif fGameName == "MHRise":
				pathPrefix = extractedNativesPath + re.sub(r'.*NSW\\', '', rapi.getInputName())
			else:
				pathPrefix = extractedNativesPath + re.sub(r'.*x64\\', '', rapi.getInputName()) 
			pathPrefix = pathPrefix.replace(modelExt,"").replace(".mesh","")
			materialFileName = (pathPrefix + mdfExt)
			print (materialFileName)
			if not (rapi.checkFileExists(materialFileName)):
				materialFileName = (pathPrefix + "_mat" + mdfExt)
			if not (rapi.checkFileExists(materialFileName)):
				materialFileName = (pathPrefix + "_00" + mdfExt)
				
		if not (rapi.checkFileExists(materialFileName)):
			materialFileName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "MDF File Not Found", "Manually enter the name of the MDF file or cancel.", os.path.join(os.path.dirname(rapi.getInputName()), rapi.getLocalFileName(materialFileName)) , None)
			if (materialFileName is None):
				print("No material file.")
				return
			elif not (rapi.checkFileExists(materialFileName)):
				noMDFFound = 1
			skipPrompt = 1
			msgName = materialFileName
		
		#Prompt for MDF load
		if not (skipPrompt):
			msgName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "MDF File Detected", "Load materials? This may take some time.", materialFileName, None)
			if msgName is None:
				print("No material file.")
				return False
				
			bColorize = 0
			if msgName.endswith(" -c"):
				print (msgName)
				bColorize = 1
				bPrintMDF = 0												
				msgName = msgName.lower().replace(" -c", "")												
			
			if ((rapi.checkFileExists(msgName)) and (msgName.endswith(mdfExt))):
				materialFileName = msgName
			else:
				noMDFFound = 1
		
		if (bPopupDebug == 1):
			noesis.logPopup()
		
		#Save a manually entered natives directory path name for later
		if ((msgName.endswith("\\natives\\" + nDir + "\\")) and (os.path.isdir(msgName))):
			print ("Attempting to write: ")
			if SaveExtractedDir(msgName):
				extractedNativesPath = msgName
				
		if (noMDFFound == 1) or not (rapi.checkFileExists(materialFileName)):
			print("Failed to open material file.")
			return False
	
		texBaseColour = []
		texRoughColour = []
		texSpecColour = []
		texAmbiColour = []
		texMetallicColour = []
		texFresnelColour = []
			
		bs = rapi.loadIntoByteArray(materialFileName)
		bs = NoeBitStream(bs)
		#Magic, Unknown, MaterialCount, Unknown, Unknown
		matHeader = [bs.readUInt(), bs.readUShort(), bs.readUShort(), bs.readUInt(), bs.readUInt()]
		
		#Parse Materials
		for i in range(matHeader[2]):
			
			if fGameName == "RE7":
				bs.seek(0x10 + (i * 72))
			elif fGameName == "REVerse" or fGameName == "RE8" or fGameName == "MHRise":
				bs.seek(0x10 + (i * 80))
			else:
				bs.seek(0x10 + (i * 64))

			materialNamesOffset = bs.readUInt64()
			materialHash = bs.readInt()
			if fGameName == "RE7":
				bs.seek(8,1)
			sizeOfFloatStr = bs.readUInt()
			floatCount = bs.readUInt()
			texCount = bs.readUInt()
			bs.seek(8,1)
			if fGameName == "REVerse" or fGameName == "RE8" or fGameName == "MHRise":
				bs.seek(8,1)
			floatHdrOffs = bs.readUInt64()
			texHdrOffs = bs.readUInt64()
			if fGameName == "REVerse" or fGameName == "RE8" or fGameName == "MHRise":
				firstMtrlNameOffs = bs.readUInt64()
			floatStartOffs = bs.readUInt64()
			mmtr_PathOffs = bs.readUInt64()
			bs.seek(materialNamesOffset)
			materialName = ReadUnicodeString(bs)
			bs.seek(mmtr_PathOffs)
			mmtrName = ReadUnicodeString(bs)
			if bPrintFileList:
				self.texNames.append(("natives/" + nDir + "/" + mmtrName + mmtrExt).lower())
				if not rapi.checkFileExists(extractedNativesPath + (mmtrName + mmtrExt).lower()) and not rapi.checkFileExists(self.rootDir + (mmtrName + mmtrExt).lower()) and rapi.getInputName().find("natives".lower()) != -1:
					self.missingTexNames.append("DOES NOT EXIST " + ("natives/" + nDir + "/" + mmtrName + mmtrExt).lower())
			
			if bPrintMDF:
				print(materialName + "[" + str(i) + "]\n")
				
			self.matNames.append(materialName)
			self.matHashes.append(materialHash)
			materialFlags = 0
			materialFlags2 = 0
			material = NoeMaterial(materialName, "")
			material.setDefaultBlend(0)
			#material.setBlendMode("GL_ONE", "GL_ONE")
			material.setAlphaTest(0)
		
			#Parse Textures
			textureInfo = []
			paramInfo = []
			
			bFoundBM = False
			bFoundNM = False
			bFoundHM = False
			bFoundBT = False
			bFoundSSSM = False
				
			bFoundBaseColour = False
			bFoundRoughColour = False
			bFoundSpecColour = False
			bFoundAmbiColour = False
			bFoundMetallicColour = False
			bFoundFresnelColour = False
			
			if bPrintMDF:
				print ("Material Properties:")
				
			for j in range(floatCount): # floats
				bs.seek(floatHdrOffs + (j * 0x18))
				paramInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt(), bs.readUInt()]) #dscrptnOffs[0], type[1], strctOffs[2], numFloats[3] 
				bs.seek(paramInfo[j][0])
				paramType = ReadUnicodeString(bs)
				
				colours = []
				if fGameName == "RE3" or fGameName == "REVerse" or fGameName == "RE8" or fGameName == "MHRise" :
					bs.seek(floatStartOffs + paramInfo[j][2])
					if paramInfo[j][3] == 4:
						colours.append(NoeVec4((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())))
					elif paramInfo[j][3] == 1:
						colours.append(bs.readFloat())
				else:
					bs.seek(floatStartOffs + paramInfo[j][3])
					if paramInfo[j][2] == 4:
						colours.append(NoeVec4((bs.readFloat(), bs.readFloat(), bs.readFloat(), bs.readFloat())))
					elif paramInfo[j][2] == 1:
						colours.append(bs.readFloat())
					
				if bPrintMDF:
					print(paramType + ":", colours)
				
				if paramType == "BaseColor" and not bFoundBaseColour:
					bFoundBaseColour = True
					texBaseColour.append(colours)
				if paramType == "Roughness" and not bFoundRoughColour:
					bFoundRoughColour = True
					texRoughColour.append(colours)
				if paramType == "PrimalySpecularColor" and not bFoundSpecColour:
					bFoundSpecColour = True
					texSpecColour.append(colours)
				if paramType == "AmbientColor" and not bFoundAmbiColour:
					bFoundAmbiColour = True
					texAmbiColour.append(colours)
				if paramType == "Metallic" and not bFoundMetallicColour:
					bFoundMetallicColour = True
					texMetallicColour.append(colours)
				if paramType == "Fresnel_DiffuseIntensity" and not bFoundFresnelColour:
					bFoundFresnelColour = True
					texFresnelColour.append(colours)
			
			#Append defaults
			if not bFoundBaseColour:
				texBaseColour.append(NoeVec4((1.0, 1.0, 1.0, 1.0)))
			if not bFoundRoughColour:
				texRoughColour.append(1.0)
			if not bFoundSpecColour:
				texSpecColour.append(NoeVec4((1.0, 1.0, 1.0, 0.8)))
			if not bFoundAmbiColour:
				texAmbiColour.append(NoeVec4((1.0, 1.0, 1.0, 1.0)))
			if not bFoundMetallicColour:
				texMetallicColour.append(1.0)
			if not bFoundFresnelColour:
				texFresnelColour.append(0.8)
			
			if bPrintMDF:
				print ("\nTextures for " + materialName + "[" + str(i) + "]" + ":")
				
			for j in range(texCount): # texture headers
				
				if fGameName == "RE3" or fGameName == "REVerse" or fGameName == "RE8" or fGameName == "MHRise" :
					bs.seek(texHdrOffs + (j * 0x20))
					textureInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt64(), bs.readUInt64()]) #TextureTypeOffset[0], uknBytes[1], TexturePathOffset[2], padding[3]
				else:
					bs.seek(texHdrOffs + (j * 0x18))
					textureInfo.append([bs.readUInt64(), bs.readUInt64(), bs.readUInt64()])
				bs.seek(textureInfo[j][0])
				textureType = ReadUnicodeString(bs)
				bs.seek(textureInfo[j][2])
				textureName = ReadUnicodeString(bs)
				
				textureFilePath = ""
				textureFilePath2 = ""
				if rapi.getInputName().find("natives".lower()) == -1:
					self.texNames.append((textureName + texExt).lower())
					
				elif (rapi.checkFileExists(self.rootDir + "streaming/" + textureName + texExt)):
					textureFilePath = self.rootDir + "streaming/" + textureName + texExt						
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + "streaming/" + textureName).rsplit('.', 1)[0] + ".dds"
							
				elif (rapi.checkFileExists(self.rootDir + textureName + texExt)):
					textureFilePath = self.rootDir + textureName + texExt
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList and not (rapi.checkFileExists(self.rootDir + textureName + texExt)):
						self.missingTexNames.append("DOES NOT EXIST: " + (('natives/' + (re.sub(r'.*natives\\', '', textureFilePath)).lower()).replace("\\","/")).replace(extractedNativesPath,''))
					
				elif (rapi.checkFileExists(extractedNativesPath + "streaming/" + textureName + texExt)):
					textureFilePath = extractedNativesPath + "streaming/" + textureName + texExt
					textureFilePath2 = rapi.getLocalFileName(extractedNativesPath + "streaming/" + textureName).rsplit('.', 1)[0] + ".dds"
							
				elif (rapi.checkFileExists(extractedNativesPath + textureName + texExt)):
					textureFilePath = extractedNativesPath + textureName + texExt
					textureFilePath2 = rapi.getLocalFileName(extractedNativesPath + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList and not (rapi.checkFileExists(extractedNativesPath + textureName + texExt)):
						self.missingTexNames.append("DOES NOT EXIST: " + ('natives/' + (re.sub(r'.*natives\\', '', textureFilePath)).lower()).replace("\\","/").replace(extractedNativesPath,''))
					
				else:
					textureFilePath = self.rootDir + textureName + texExt
					textureFilePath2 = rapi.getLocalFileName(self.rootDir + textureName).rsplit('.', 1)[0] + ".dds"
					if bPrintFileList and not (textureFilePath.endswith("rtex" + texExt)):
						self.missingTexNames.append("DOES NOT EXIST: " + ('natives/' + (re.sub(r'.*natives\\', '', textureFilePath)).lower()).replace("\\","/").replace("streaming/",""))
				
				bAlreadyLoadedTexture = False
				
				for k in range(len(self.texList)):
					if self.texList[k].name == textureFilePath2:
						bAlreadyLoadedTexture = True
				
				if bPrintFileList and rapi.getInputName().find("natives".lower()) != -1:
					if (textureName.endswith("rtex")):
						self.texNames.append((((('natives/' + (re.sub(r'.*natives\\', '', textureFilePath))).replace("\\","/")).replace(texExt,".4")).replace(extractedNativesPath,'')).lower())
					else:
						newTexPath = ((('natives/' + (re.sub(r'.*natives\\', '', textureFilePath))).replace("\\","/")).replace(extractedNativesPath,'')).lower()
						self.texNames.append(newTexPath)
						if newTexPath.find('streaming') != -1:
							testPath = newTexPath.replace('natives/' + nDir + '/streaming/', '')
							if rapi.checkFileExists(self.rootDir + testPath) or rapi.checkFileExists(extractedNativesPath + testPath):
								self.texNames.append(newTexPath.replace('streaming/',''))
								
				if bColorize:
					colors = [(0.0, 0.0, 0.0, 1.0), 	(1.0, 1.0, 1.0, 1.0), 	  (1.0, 0.0, 0.0, 1.0),	  	(0.0, 1.0, 0.0, 1.0), 		(0.0, 0.0, 1.0, 1.0), 	 (1.0, 1.0, 0.0, 1.0), 		(0.0, 1.0, 1.0, 1.0),\
							  (1.0, 0.0, 1.0, 1.0), 	(0.75, 0.75, 0.75, 1.0),  (0.5, 0.5, 0.5, 1.0),	  	(0.5, 0.0, 0.0, 1.0), 		(0.5, 0.5, 0.0, 1.0), 	 (0.0, 0.5, 0.0, 1.0), 		(0.5, 0.0, 0.5, 1.0),\
							  (0.0, 0.5, 0.5, 1.0), 	(0.0, 0.0, 0.5, 1.0), 	  (0.82, 0.7, 0.53, 1.0), 	(0.294, 0.0, 0.51, 1.0), 	(0.53, 0.8, 0.92, 1.0),  (0.25, 0.88, 0.815, 1.0),  (0.18, 0.545, 0.34, 1.0),\
							  (0.68, 1.0, 0.18, 1.0), 	(0.98, 0.5, 0.45, 1.0),   (1.0, 0.41, 0.7, 1.0),  	(0.0, 0.0, 0.0, 1.0), 		(1.0, 1.0, 1.0, 1.0), 	 (1.0, 0.0, 0.0, 1.0), 		(0.0, 1.0, 0.0, 1.0),\
							  (0.0, 0.0, 1.0, 1.0), 	(1.0, 1.0, 0.0, 1.0), 	  (0.0, 1.0, 1.0, 1.0),	  	(1.0, 0.0, 1.0, 1.0), 	 	(0.75, 0.75, 0.75, 1.0), (0.5, 0.5, 0.5, 1.0), 	 	(0.5, 0.0, 0.0, 1.0),\
							  (0.5, 0.5, 0.0, 1.0), 	(0.0, 0.5, 0.0, 1.0),	  (0.5, 0.0, 0.5, 1.0),	  	(0.0, 0.5, 0.5, 1.0), 		(0.0, 0.0, 0.5, 1.0), 	 (0.82, 0.7, 0.53, 1.0), 	(0.294, 0.0, 0.51, 1.0),\
							  (0.53, 0.8, 0.92, 1.0), 	(0.25, 0.88, 0.815, 1.0), (0.18, 0.545, 0.34, 1.0), (0.68, 1.0, 0.18, 1.0), 	(0.98, 0.5, 0.45, 1.0),  (1.0, 0.41, 0.7, 1.0)]
					colorNames = ['Black', 'White', 'Red', 'Lime', 'Blue', 'Yellow', 'Cyan', 'Magenta', 'Silver', 'Gray', 'Maroon', 'Olive', 'Green', 'Purple', 'Teal', 'Navy', 'Tan', 'Indigo', 'Sky Blue', 'Turquoise',\
					'Sea Green', 'Green Yellow', 'Salmon', 'Hot Pink', 'Black', 'White', 'Red', 'Lime', 'Blue', 'Yellow', 'Cyan', 'Magenta', 'Silver', 'Gray', 'Maroon', 'Olive', 'Green', 'Purple', 'Teal', 'Navy', 'Tan',\
					'Indigo', 'Sky Blue', 'Turquoise', 'Sea Green', 'Green Yellow', 'Salmon', 'Hot Pink']					
					
					material.setDiffuseColor(colors[i])
					if i < 10:
						myIndex = "0" + str(i)
					else:
						myIndex = str(i)
					self.texColors.append(myIndex + ": Material[" + str(i) + "] -- " + materialName + " is colored " + colorNames[i])
				else:
					if not bAlreadyLoadedTexture:
						if (textureName.endswith("rtex")):
							pass
							#print(str(textureFilePath).replace(texExt,".4") + " cannot be read!")
							
						elif not (rapi.checkFileExists(textureFilePath)):
							if textureFilePath != "": 
								print("Error: Texture at path: " + str(textureFilePath) + " does not exist!")
							
						else:
							textureData = rapi.loadIntoByteArray(textureFilePath)
							if texLoadDDS(textureData, self.texList) == 1:
								self.texList[len(self.texList)-1].name = textureFilePath2
								
					if textureType == "BaseMetalMap" or textureType == "BaseShiftMap" or "Base" in textureType and not bFoundBM:
						bFoundBM = True
						material.setTexture(textureFilePath2)
						material.setDiffuseColor(texBaseColour[i][0])
						material.setSpecularTexture(textureFilePath2)
						materialFlags |= noesis.NMATFLAG_PBR_SPEC #Not really :(
						material.setSpecularSwizzle( NoeMat44([[1, 1, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]]) )
					elif textureType == "NormalRoughnessMap" and not bFoundNM:
						bFoundNM = True
						material.setNormalTexture(textureFilePath2)
						materialFlags |= noesis.NMATFLAG_PBR_ROUGHNESS_NRMALPHA
					elif textureType == "AlphaTranslucentOcclusionSSSMap" and not bFoundSSSM:
						bFoundSSSM = True
						material.setOpacityTexture(textureFilePath2)
						#material.setNextPass(textureFilePath2)
						material.setOcclTexture(textureFilePath2) 
						#matArray.append(textureFilePath2)
						try:
							materialFlags2 |= noesis.NMATFLAG2_OPACITY_UV1 | noesis.NMATFLAG2_OCCL_UV1 | noesis.NMATFLAG2_OCCL_BLUE
							#material.setAlphaTest(0.5)
						except:
							print ("Please update Noesis to fix MDF occlusion map preview")
							
					elif textureType == "Heat_Mask" and not bFoundHM:
						bFoundHM = True
					elif textureType == "BloodTexture" and not bFoundBT:
						bFoundBT = True
					
					if bFoundSpecColour:
						material.setSpecularColor(texSpecColour[i][0])
					if bFoundAmbiColour:
						material.setAmbientColor(texAmbiColour[i][0])
					if bFoundMetallicColour:
						material.setMetal(texMetallicColour[i][0], 0.25)
					if bFoundRoughColour:
						material.setRoughness(texRoughColour[i][0], 0.25)
					if bFoundFresnelColour:
						material.setEnvColor(NoeVec4((1.0, 1.0, 1.0, texFresnelColour[i][0])))
						
					if bPrintMDF:
						print(textureType + ":\n    " + textureName)
						
			material.setFlags(materialFlags)
			material.setFlags2(materialFlags2)
			self.matList.append(material)
			
			if bPrintMDF:
				print("--------------------------------------------------------------------------------------------\n")
					
		if bPrintFileList:
			if len(self.texNames) > 0:
				print ("Referenced Files:")
				textureList = sorted(list(set(self.texNames)))
				for x in range (len(textureList)):
					print (textureList[x])
				print ("")
			
			if len(self.missingTexNames) > 0:
				print ("Missing Files:")
				missingTextureList = sorted(list(set(self.missingTexNames)))
				for x in range (len(missingTextureList)):
					print (missingTextureList[x])
				print ("")
			
		if bColorize:
			colorList = sorted(list(set(self.texColors)))
			print ("Color-coded Materials:")
			for g in range (len(colorList)):
				print (colorList[g])
			print ("")
		
		return True
			
	def loadMeshFile(self, mdlList):
		global bAddBoneNumbers, fGameName, bSkinningEnabled
		fGameName = "RE2"
		if rapi.getInputName().find(".1808282334") != -1:
			fGameName = "DMC5"
		elif rapi.getInputName().find(".1902042334") != -1:
			fGameName = "RE3"
		elif rapi.getInputName().find(".2010231143") != -1:
			fGameName = "REVerse"
		elif rapi.getInputName().find(".2101050001") != -1:
			fGameName = "RE8"
		elif rapi.getInputName().find(".2008058288") != -1:
			fGameName = "MHRise"
		elif rapi.getInputName().find(".32") != -1:
			fGameName = "RE7"
			
		bs = self.inFile		
		
		magic = bs.readUInt()
		meshVersion = bs.readUInt()
		fileSize = bs.readUInt()
		if fGameName != "RE7":
			unk02 = bs.readUInt()
		unk03 = bs.readUShort()
		numNodes = bs.readUShort()
		if fGameName != "RE7":
			unk04 = bs.readUInt()			
		LOD1Offs = bs.readUInt64()
		LOD2Offs = bs.readUInt64()
		ukn2 = bs.readUInt64()
		bonesOffs = bs.readUInt64()
		if fGameName != "RE7":
			topologyOffs = bs.readUInt64()
		bShapesHdrOffs = bs.readUInt64()
		floatsHdrOffs = bs.readUInt64()
		vBuffHdrOffs = bs.readUInt64()
		ukn3 = bs.readUInt64()
		nodesIndicesOffs = bs.readUInt64()
		boneIndicesOffs = bs.readUInt64()
		bshapesIndicesOffs = bs.readUInt64()
		namesOffs = bs.readUInt64()
		
		
		bs.seek(LOD1Offs)
		countArray = bs.read("16B") #[0] = LODGroupCount, [1] = MaterialCount, [2] = UVChannelCount
		
		self.rootDir = GetRootGameDir()
		bLoadedMats = False
		if not (noesis.optWasInvoked("-noprompt")) and not rapi.noesisIsExporting() and not bRenameMeshesToFilenames:
			bLoadedMats = self.createMaterials();
		
		if noesis.optWasInvoked("-bonenumbers"):
			bAddBoneNumbers = 1
		
		if bDebugMESH:
			print("Count Array")
			print(countArray)
		
		bs.seek(48, 1) #unknown floats 
		if fGameName != "REVerse" and fGameName != "RE8" and fGameName != "MHRise" :
			bs.seek(bs.readUInt64())
			
		if numNodes == 0:
			print("Unsupported model type")
			return
		
		offsetInfo = []
		for i in range(countArray[0]):
			offsetInfo.append(bs.readUInt64())
			
		if bDebugMESH:
			print("Vertex Info Offsets")
			print(offsetInfo)
		
		nameOffsets = []
		names = []
		nameRemapTable = []
		
		bs.seek(nodesIndicesOffs)
		for i in range(numNodes):
			nameRemapTable.append(bs.readUShort())
			
		bs.seek(namesOffs)
		for i in range(numNodes):
			nameOffsets.append(bs.readUInt64())
			
		for i in range(numNodes):
			bs.seek(nameOffsets[i])
			names.append(bs.readString())
			
		if bDebugMESH:
			print("Names:")
			print(names)
			
		bs.seek(LOD1Offs + 1)
		matCount = bs.readUByte()
		bs.seek(nodesIndicesOffs) #material indices
		matIndices =[]
		for i in range(matCount):
			matIndices.append(bs.readUShort())
			
		#Skeleton
		if fGameName == "RE7":
			bs.seek(floatsHdrOffs)
			boneMapCount = bs.readUInt()
			bs.seek(LOD1Offs+72)
			RE7SkinBoneMapOffs = bs.readUInt64()+16
		else:
			bs.seek(bonesOffs+4)
			boneMapCount = bs.readUInt()
			
		bs.seek(bonesOffs)
		if bonesOffs > 0 and boneMapCount:
			boneCount = bs.readUInt()
			bs.seek(12,1)
			hierarchyOffs = bs.readUInt64()
			localOffs = bs.readUInt64()
			globalOffs = bs.readUInt64()
			inverseGlobalOffs = bs.readUInt64()
			
			if fGameName == "RE7":
				bs.seek(RE7SkinBoneMapOffs)
				
			boneRemapTable = []
			for i in range(boneMapCount):
				boneRemapTable.append(bs.readShort())
				
			if bDebugMESH:
				print(boneRemapTable)

			boneParentInfo = []
			bs.seek(hierarchyOffs)
			for i in range(boneCount):
				boneParentInfo.append([bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort(), bs.readShort()])
			
			trans = NoeVec3((100.0, 100.0, 100.0))
			bs.seek(localOffs)
			for i in range(boneCount):
				mat = NoeMat44.fromBytes(bs.readBytes(0x40)).toMat43()
				mat[3] *= trans
				boneName = names[countArray[1] + i]
				if bAddBoneNumbers:
					for j in range(len(boneRemapTable)):
						if boneParentInfo[i][0] == boneRemapTable[j]:
							if j<9:
								boneName = "b00" + str(j+1) + ":" + boneName
							elif j>8 and j<99:
								boneName = "b0" + str(j+1) + ":" + boneName
							elif j>98 and j<999:
								boneName = "b" + str(j+1) + ":" + boneName	
							break
				self.boneList.append(NoeBone(boneParentInfo[i][0], boneName, mat, None, boneParentInfo[i][1]))
			self.boneList = rapi.multiplyBones(self.boneList)
		else:
			bSkinningEnabled = False
		bs.seek(vBuffHdrOffs)
		
		if fGameName == "RE7":
			vertBuffSize = bs.readUInt()
			bs.seek(12,1)
			faceBuffSize = bs.readUInt()
			bs.seek(20,1)
			faceBuffOffs = bs.readUInt()
			bytesPerVert = 24 if bonesOffs == 0 else 40
			addBytes = 0
			if countArray[2] > 1: 
				addBytes = 4
				bytesPerVert += addBytes
			while bs.tell() % 16 != 0:
				bs.seek(1,1)
		else:
			vertElemHdrOffs = bs.readUInt64()
			vertBuffOffs = bs.readUInt64()
			faceBuffOffs = bs.readUInt64()
			vertBuffSize = bs.readUInt()
			faceBuffSize = bs.readUInt()
			vertElemCountA = bs.readUShort()
			vertElemCountB = bs.readUShort()
			faceBufferSize2nd = bs.readUInt64()
			blendshapesOffset = bs.readUInt()
			
			vertElemHeaders = []
			positionIndex = -1
			normalIndex = -1
			uvIndex = -1
			uv2Index = -1
			weightIndex = -1
			for i in range (vertElemCountB):
				vertElemHeaders.append([bs.readUShort(), bs.readUShort(), bs.readUInt()])
				if vertElemHeaders[i][0] == 0 and positionIndex == -1:
					positionIndex = i
				elif vertElemHeaders[i][0] == 1 and normalIndex == -1:
					normalIndex = i
				elif vertElemHeaders[i][0] == 2 and uvIndex == -1:
					uvIndex = i
				elif vertElemHeaders[i][0] == 3 and uv2Index == -1:
					uv2Index = i
				elif vertElemHeaders[i][0] == 4 and weightIndex == -1:
					weightIndex = i
			bs.seek(vertBuffOffs)
		vertexStartIndex = bs.tell()
		vertexBuffer = bs.readBytes(vertBuffSize)
		submeshDataArr = []
		
		for i in range(countArray[0]): #numLODs
			meshVertexInfo = []
			ctx = rapi.rpgCreateContext()
			bs.seek(offsetInfo[i])
			numOffsets = bs.readUByte()
			bs.seek(3,1)
			uknFloat = bs.readUInt()
			offsetSubOffsets = bs.readUInt64()
			bs.seek(offsetSubOffsets)
			
			meshOffsetInfo = []
			
			for j in range(numOffsets):
				meshOffsetInfo.append(bs.readUInt64())
			
			for j in range(numOffsets):
				bs.seek(meshOffsetInfo[j])
				meshVertexInfo.append([bs.readUByte(), bs.readUByte(), bs.readUShort(), bs.readUInt(), bs.readUInt(), bs.readUInt()])
				submeshData = []
				for k in range(meshVertexInfo[j][1]):
					if fGameName == "REVerse" or fGameName == "MHRise" or fGameName == "RE8":
						submeshData.append([bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt64()])
					else:
						submeshData.append([bs.readUInt(), bs.readUInt(), bs.readUInt(), bs.readUInt()]) #0 MaterialID, 1 faceCount, 2 indexBufferStartIndex, 3 vertexStartIndex
				
				submeshDataArr.append(submeshData)
				
				for k in range(meshVertexInfo[j][1]):
				
					if bUseOldNamingScheme:
						meshName = "LODGroup_" + str(i+1) + "_MainMesh_" + str(j+1) + "_SubMesh_" + str(submeshData[k][0]+1)
					else:
						if bRenameMeshesToFilenames:
							meshName = os.path.splitext(rapi.getLocalFileName(rapi.getInputName()))[0].replace(".mesh", "") + "_" + str(j+1) + "_" + str(k+1)
							
						else:
							meshName = "LODGroup_" + str(i+1) + "_MainMesh_" + str(j+1) + "_SubMesh_" + str(k+1)
						
					rapi.rpgSetName(meshName)
					if bRenameMeshesToFilenames: 
						rapi.rpgSetMaterial(meshName)
					rapi.rpgSetName(meshName)
					matName = ""
					
					#Search for material
					if bLoadedMats:
						matHash = hash_wide(names[matIndices[submeshData[k][0]]])
						if i == 0:
							for m in range(len(self.matHashes)):
								if self.matHashes[m] == matHash:
									if self.matNames[m] != names[nameRemapTable[submeshData[k][0]]]:
										print ("WARNING: " + meshName + "\'s material name \"" + self.matNames[m] + "\" in MDF does not match its material hash! \n	True material name: \"" + names[nameRemapTable[submeshData[k][0]]] + "\"")
									matName = self.matNames[m]
									#rapi.rpgSetLightmap(matArray[k].replace(".dds".lower(), ""))
									break
						if matName == "":
							print ("WARNING: " + meshName + "\'s material \"" + names[nameRemapTable[submeshData[k][0]]] + "\" hash " + str(matHash) + " not found in MDF!")
							for m in range(len(self.matNames)):
								if self.matNames[m] == names[nameRemapTable[submeshData[k][0]]]:
									matName = self.matNames[m]
									break
									
					rapi.rpgSetMaterial(matName)
					rapi.rpgSetPosScaleBias((fDefaultMeshScale, fDefaultMeshScale, fDefaultMeshScale), (0, 0, 0))
					
					if fGameName == "RE7":
						rapi.rpgBindPositionBufferOfs(vertexBuffer, noesis.RPGEODATA_FLOAT, bytesPerVert, (submeshData[k][3] * bytesPerVert))
						rapi.rpgBindNormalBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, bytesPerVert, 12 + (submeshData[k][3] * bytesPerVert))
						rapi.rpgBindTangentBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, bytesPerVert, 16 + (submeshData[k][3] * bytesPerVert))
						rapi.rpgBindUV1BufferOfs(vertexBuffer, noesis.RPGEODATA_HALFFLOAT, bytesPerVert, 20 + (submeshData[k][3] * bytesPerVert))
						if (countArray[2] > 1):
							rapi.rpgBindUV2BufferOfs(vertexBuffer, noesis.RPGEODATA_HALFFLOAT, bytesPerVert, 24 + (submeshData[k][3] * bytesPerVert))
						if bonesOffs > 0:
							rapi.rpgSetBoneMap(boneRemapTable)
							rapi.rpgBindBoneIndexBufferOfs(vertexBuffer, noesis.RPGEODATA_UBYTE, bytesPerVert, 24 + addBytes + (submeshData[k][3] * bytesPerVert), 8)
							rapi.rpgBindBoneWeightBufferOfs(vertexBuffer, noesis.RPGEODATA_UBYTE, bytesPerVert, 32 + addBytes + (submeshData[k][3] * bytesPerVert), 8)
					else:
						if positionIndex != -1:
							rapi.rpgBindPositionBufferOfs(vertexBuffer, noesis.RPGEODATA_FLOAT, vertElemHeaders[positionIndex][1], (vertElemHeaders[positionIndex][1] * submeshData[k][3]))
						
						if normalIndex != -1 and bNORMsEnabled:
							if bDebugNormals:
								rapi.rpgBindColorBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, vertElemHeaders[normalIndex][1], vertElemHeaders[normalIndex][2] + (vertElemHeaders[normalIndex][1] * submeshData[k][3]), 4)
							else:
								rapi.rpgBindNormalBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, vertElemHeaders[normalIndex][1], vertElemHeaders[normalIndex][2] + (vertElemHeaders[normalIndex][1] * submeshData[k][3]))
								if bTANGsEnabled:
									rapi.rpgBindTangentBufferOfs(vertexBuffer, noesis.RPGEODATA_BYTE, vertElemHeaders[normalIndex][1], 4 + vertElemHeaders[normalIndex][2] + (vertElemHeaders[normalIndex][1] * submeshData[k][3]))
						
						if uvIndex != -1 and bUVsEnabled:
							rapi.rpgBindUV1BufferOfs(vertexBuffer, noesis.RPGEODATA_HALFFLOAT, vertElemHeaders[uvIndex][1], vertElemHeaders[uvIndex][2] + (vertElemHeaders[uvIndex][1] * submeshData[k][3]))
						if uv2Index != -1 and bUVsEnabled:
							rapi.rpgBindUV2BufferOfs(vertexBuffer, noesis.RPGEODATA_HALFFLOAT, vertElemHeaders[uv2Index][1], vertElemHeaders[uv2Index][2] + (vertElemHeaders[uv2Index][1] * submeshData[k][3]))
						
						if weightIndex != -1 and bSkinningEnabled:
							rapi.rpgSetBoneMap(boneRemapTable)
							rapi.rpgBindBoneIndexBufferOfs(vertexBuffer, noesis.RPGEODATA_UBYTE, vertElemHeaders[weightIndex][1], vertElemHeaders[weightIndex][2] + (vertElemHeaders[weightIndex][1] * submeshData[k][3]), 8)
							rapi.rpgBindBoneWeightBufferOfs(vertexBuffer, noesis.RPGEODATA_UBYTE, vertElemHeaders[weightIndex][1], vertElemHeaders[weightIndex][2] + (vertElemHeaders[weightIndex][1] * submeshData[k][3]) + 8, 8)
						
					if submeshData[k][1] > 0:
						bs.seek(faceBuffOffs + (submeshData[k][2] * 2))
						indexBuffer = bs.readBytes(submeshData[k][1] * 2)
						if bRenderAsPoints:
							rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, (meshVertexInfo[j][4] - (submeshData[k][3])), noesis.RPGEO_POINTS, 0x1)
						else:
							rapi.rpgSetStripEnder(0x10000)
							rapi.rpgCommitTriangles(indexBuffer, noesis.RPGEODATA_USHORT, submeshData[k][1], noesis.RPGEO_TRIANGLE, 0x1)
							rapi.rpgClearBufferBinds()
							
			try:
				mdl = rapi.rpgConstructModelAndSort()
				if mdl.meshes[0].name.find("_") == 4:
					print ("\nWARNING: Noesis split detected! Export this mesh to FBX with the advanced option '-fbxmeshmerge'\n")
					rapi.rpgOptimize()
			except:
				mdl = NoeModel()
			mdl.setBones(self.boneList)
			mdl.setModelMaterials(NoeModelMaterials(self.texList, self.matList))
			mdlList.append(mdl)
				
			#set source names	
			'''for i, mesh in enumerate(mdl.meshes):
				if len(mesh.name.split('_')) > 6: #for when Noesis auto-renames
					mainMeshIdx = int(mesh.name.split('_')[4]) - 1
					submeshIdx = int(mesh.name.split('_')[6]) - 1
				else:
					mainMeshIdx = int(mesh.name.split('_')[3]) - 1
					submeshIdx = int(mesh.name.split('_')[5]) - 1
				#mesh.setSourceName(names[matIndices[submeshDataArr[mainMeshIdx][submeshIdx][0]]])'''
			if not bImportAllLODs:
				break
				
		print ("")
		return mdlList
				
def meshLoadModel(data, mdlList):
	mesh = meshFile(data)
	mdlList = mesh.loadMeshFile(mdlList)
	return 1
	
def meshWriteModel(mdl, bs):
	global fExportExtension, w1, w2, bWriteBones, bReWrite, bRigToCoreBones, bAddBoneNumbers, fGameName #, doLOD
	bRigToCoreBones = False
	w1 = 127; w2 = -128; bWriteBones = noesis.optWasInvoked("-bones");
	bReWrite = noesis.optWasInvoked("-rewrite");
	if noesis.optWasInvoked("-flip"): w1 = -128; w2 = 127
	
	def padToNextLine(bitstream):
		while bitstream.tell() % 16 != 0:
			bitstream.writeByte(0)
			
	def getExportName(fileName):
		global fExportExtension, w1, w2, bWriteBones, bReWrite, bRigToCoreBones #, doLOD
		bRigToCoreBones = False; bWriteBones = 0; w1 = 127; w2 = -128
		if fileName == None:
			newMeshName = rapi.getOutputName().lower()
			while newMeshName.find("out.") != -1: newMeshName = newMeshName.replace("out.",".")
			newMeshName = newMeshName.replace(".mesh","").replace(".fbx","").replace(".1808312334","").replace(".1902042334","").replace(".1808282334","").replace(".2010231143","").replace(".2101050001","").replace(".32","")
			ext = ".mesh" + fExportExtension
			if rapi.checkFileExists(newMeshName + ".mesh.1808312334"):
				ext = ".mesh.1808312334"
			elif rapi.checkFileExists(newMeshName + ".mesh.1902042334"):
				ext = ".mesh.1902042334"
			elif rapi.checkFileExists(newMeshName + ".mesh.1808282334"):
				ext = ".mesh.1808282334"
			elif rapi.checkFileExists(newMeshName + ".mesh.2010231143"):
				ext = ".mesh.2010231143"
			elif rapi.checkFileExists(newMeshName + ".mesh.2101050001"):
				ext = ".mesh.2101050001"
			elif rapi.checkFileExists(newMeshName + ".mesh.32"):
				ext = ".mesh.32"
				
			newMeshName += ext
		else:
			newMeshName = fileName
		newMeshName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Export over MESH", "Choose a MESH file to export over", newMeshName, None)

		if newMeshName == None:
			print("Aborting...")
			return
			
		if noesis.optWasInvoked("-flip") or newMeshName.find(" -flip".lower()) != -1:
			newMeshName = newMeshName.replace(" -flip".lower(), "")
			print ("Exporting with OpenGL handedness")
			w1 = -128
			w2 = 127
		
		if noesis.optWasInvoked("-bones") or newMeshName.find(" -bones".lower()) != -1:
			newMeshName = newMeshName.replace(" -bones".lower(), "")
			print ("Exporting with new skeleton...")
			bWriteBones = 1
			
		if noesis.optWasInvoked("-rewrite") or newMeshName.find(" -rewrite".lower()) != -1:
			newMeshName = newMeshName.replace(" -rewrite".lower(), "")
			print ("Exporting with new Mainmesh and Submesh order...")
			bReWrite = 1
			
		if newMeshName.find(" -match".lower()) != -1:
			newMeshName = newMeshName.replace(" -match".lower(), "")
			print ("Unmatched bones will be rigged to the hips and spine")
			bRigToCoreBones = True
			
		return newMeshName
		
	if noesis.optWasInvoked("-bonenumbers"):
		bAddBoneNumbers = 1
		
	print ("		----RE Engine MESH Export v2.6 by alphaZomega----\nOpen fmt_RE_MESH.py in your Noesis plugins folder to change global exporter options.\nExport Parameters:\n -flip  =  OpenGL / flipped handedness (fixes seams and inverted lighting on some models)\n -bones = save new skeleton from Noesis to the MESH file\n -match = assign non-matching bones to the hips and spine\n") #\n -lod = export with additional LODGroups") # -rewrite = save new MainMesh and SubMesh order 
	
	fileName = None
	if noesis.optWasInvoked("-meshfile"):
		newMeshName = noesis.optGetArg("-meshfile")
	else:
		newMeshName = getExportName(fileName)
	if newMeshName == None:
		return 0
	while not (rapi.checkFileExists(newMeshName)):
		print ("File not found!")
		newMeshName = getExportName(fileName)	
		fileName = newMeshName
		if newMeshName == None:
			return 0
	
	fGameName = "RE2"
	if newMeshName.find(".1808282334") != -1:
		fGameName = "DMC5"
	elif newMeshName.find(".1902042334") != -1:
		fGameName = "RE3"
	elif newMeshName.find(".2010231143") != -1:
		fGameName = "REVerse"
	elif newMeshName.find(".2101050001") != -1:
		fGameName = "RE8"
	elif newMeshName.find(".2008058288") != -1:
		fGameName = "MHRise"
	elif newMeshName.find(".32") != -1:
		fGameName = "RE7"
	print (fGameName)
		
	newMesh = rapi.loadIntoByteArray(newMeshName)
	f = NoeBitStream(newMesh)
	magic = f.readUInt()
	
	if magic != 1213416781:
		noesis.messagePrompt("Not a MESH file.\nAborting...")
		return 0		
	
	f.seek(18)
	if fGameName == "RE7":
		f.seek(14)
	numNodes = f.readUShort()
	
	if fGameName != "RE7":
		f.seek(24)
	
	LOD1Offs = f.readUInt64()
	LOD2Offs = f.readUInt64()
	ukn2 = f.readUInt64()
	bonesOffs = f.readUInt64()
	if fGameName != "RE7":
		topologyOffs = f.readUInt64()
	bShapesHdrOffs = f.readUInt64()
	floatsHdrOffs = f.readUInt64()
	vBuffHdrOffs = f.readUInt64()
	ukn3 = f.readUInt64()
	nodesIndicesOffs = f.readUInt64()
	boneIndicesOffs = f.readUInt64()
	bshapesIndicesOffs = f.readUInt64()
	namesOffs = f.readUInt64()
	f.seek(LOD1Offs)
	countArray = f.read("16B")
	
	numLODs = 1
	#if doLOD:
	#	numLODs = countArray[0]
	
	f.seek(vBuffHdrOffs)
	
	doUV1 = False
	bDoSkin = False
	
	if fGameName == "RE7":
		vertBuffSize = f.readUInt()
		f.seek(12,1)
		faceBuffSize = f.readUInt()
		f.seek(20,1)
		faceBuffOffs = f.readUInt()
		addBytes = 0
		bytesPerVert = 24 
		if bonesOffs > 0:
			bDoSkin = True
			bytesPerVert = 40 
		if countArray[2] > 1: 
			doUV1 = True
			addBytes = 4
			bytesPerVert += addBytes
		while f.tell() % 16 != 0: 
			f.seek(1,1)
		vertBuffOffs = f.tell()
	else:
		vertElemHdrOffs = f.readUInt64()
		vertBuffOffs = f.readUInt64()
		faceBuffOffs = f.readUInt64()
		vertBuffSize = f.readUInt()
		faceBuffSize = f.readUInt()
		vertElemCountA = f.readUShort()
		vertElemCountB = f.readUShort()
		faceBufferSize2nd = f.readUInt64()
		blendshapesOffset = f.readUInt()
			
		vertElemHeaders = []
		for i in range(vertElemCountB):
			vertElemHeaders.append([f.readUShort(), f.readUShort(), f.readUInt()])
		
		for i in range(len(vertElemHeaders)):
			if vertElemHeaders[i][0] == 3:
				doUV1 = 1
			if vertElemHeaders[i][0] == 4:
				bDoSkin = 1
				
	#Automatic scaling fix
	scale = 1.0
	if bDoAutoScale and len(mdl.bones) > 0:
		if mdl.bones[0].getMatrix()[0][0] != 1:
			scale = mdl.bones[0].getMatrix()[0][0]
			print ("Auto-scaling to", scale)
	
	nameOffsets = []	
	f.seek(namesOffs)
	for i in range(numNodes):
		nameOffsets.append(f.readUInt64())
	
	names = []
	for i in range(numNodes):
		f.seek(nameOffsets[i])
		names.append(f.readString())
	bonesList = []
	boneNameAddressList = []
	matNameAddressList = []
	
	#Remove Blender numbers from all names
	for bone in mdl.bones:
		if bone.name.find('.') != -1:
			print ("Renaming Bone " + str(bone.name) + " to " + str(bone.name.split('.')[0]))
			bone.name = bone.name.split('.')[0] 
	for mesh in mdl.meshes:
		if mesh.name.find('.') != -1:
			print ("Renaming Mesh " + str(mesh.name) + " to " + str(mesh.name.split('.')[0]))
			mesh.name = mesh.name.split('.')[0]
		if len(mesh.lmUVs) <= 0: #make sure UV2 exists
			mesh.lmUVs = mesh.uvs
				
	if bDoSkin:		
		boneRemapTable = []
		boneInds = []
		reverseSkinBoneMap = []
		
		#Skeleton
		if fGameName == "RE7":
			f.seek(floatsHdrOffs)
			boneMapCount = f.readUInt()
			f.seek(LOD1Offs+72)
			RE7SkinBoneMapOffs = f.readUInt64()+16
		else:
			f.seek(bonesOffs+4)
			boneMapCount = f.readUInt()
		
		f.seek(bonesOffs)			
		boneCount = f.readUInt()
		f.seek(12,1)
		hierarchyOffs = f.readUInt64()
		localOffs = f.readUInt64()
		globalOffs = f.readUInt64()
		inverseGlobalOffs = f.readUInt64()
		
		if len(mdl.bones) != boneCount:
			if not bWriteBones:
				print ("WARNING: Model Bones do not match the bones in the MESH file!")
			print ("Model Bones: " + str(len(mdl.bones)) + "\nMESH Bones: " + str(boneCount))
		
		if fGameName == "RE7":
			f.seek(RE7SkinBoneMapOffs)
			
		for b in range(boneMapCount):
			boneRemapTable.append(f.readUShort())
		
		f.seek(boneIndicesOffs)
		for i in range(boneCount):
			boneInds.append(f.readUShort())
			boneMapIndex = -1
			for b in range(len(boneRemapTable)):
				if boneRemapTable[b] == i:
					boneMapIndex = b
			reverseSkinBoneMap.append(boneMapIndex)
		
		f.seek(namesOffs)
		for i in range(countArray[1]): 
			matNameAddressList.append(f.readUInt64())
			
		for i in range(boneCount):
			boneNameAddressList.append(f.readUInt64())
		for bone in mdl.bones:
			if str(bone.name).startswith("bone") and bone.name.find("_") == 8:
				bone.name = bone.name[9:len(bone.name)]
		newSkinBoneMap = []
		for i, bone in enumerate(mdl.bones):
			if bone.name.find('.') != -1:
				print ("Renaming Bone " + str(bone.name) + " to " + str(bone.name.split('.')[0]))
				bone.name = bone.name.split('.')[0] #remove blender numbers
			bName = bone.name.split(':') #remove bone numbers
			if len(bName) == 2:
				bonesList.append(bName[1])
				if len(newSkinBoneMap) < 256:
					newSkinBoneMap.append(i)
			else:
				bonesList.append(bone.name)
				if not bAddBoneNumbers and len(newSkinBoneMap) < 256:
					newSkinBoneMap.append(i)			
	
	if fGameName == "REVerse" or fGameName == "MHRise" or fGameName == "RE8" or fGameName == "RE7":
		f.seek(192)
	else:
		f.seek(200)
		f.seek(f.readUInt64())
		
	offsetInfo = []
	meshVertexInfo = []
	for i in range(numLODs): #LODGroup Offsets
		offsetInfo.append(f.readUInt64())
	 
	#merge Noesis-split meshes back together:	
	meshesToExport = mdl.meshes
	if mdl.meshes[0].name.find("_") == 4:
		print ("WARNING: Noesis-split meshes detected. Merging meshes back together...")
		combinedMeshes = []
		lastMesh = None
		offset = 0
		
		for i, mesh in enumerate(mdl.meshes):
			mesh.name = mesh.name[5:len(mesh.name)]
			
			if lastMesh == None:
				lastMesh = copy.copy(mesh)
				offset += len(mesh.positions)
			elif mesh.name == lastMesh.name:
				if len(lastMesh.positions) == len(mesh.positions) and len(lastMesh.indices) == len(mesh.indices): #ignore real duplicates
					continue
				newIndices = []
				for j in range(len(mesh.indices)):
					newIndices.append(mesh.indices[j]  + offset)
				lastMesh.setPositions((lastMesh.positions + mesh.positions))
				lastMesh.setUVs((lastMesh.uvs + mesh.uvs))
				lastMesh.setUVs((lastMesh.lmUVs + mesh.lmUVs), 1)
				lastMesh.setTangents((lastMesh.tangents + mesh.tangents))
				lastMesh.setWeights((lastMesh.weights + mesh.weights))
				lastMesh.setIndices((lastMesh.indices + tuple(newIndices)))
				offset += len(mesh.positions)
				
			if i == len(mdl.meshes)-1:
				combinedMeshes.append(mesh)
			elif mdl.meshes[i+1].sourceName != mesh.sourceName:
				combinedMeshes.append(lastMesh)
				offset = 0
				lastMesh = None
				
		meshesToExport = combinedMeshes
	
	#Validate meshes are named correctly
	objToExport = []
	for i, mesh in enumerate(meshesToExport):
		ss = mesh.name.split('_')
		if len(ss) == 6:
			if ss[0] == 'LODGroup' and ss[1].isnumeric() and ss[2] == 'MainMesh' and ss[3].isnumeric() and ss[4] == 'SubMesh' and ss[5].isnumeric():
				objToExport.append(i)
		
	submeshes = []
	mainmeshcount = 0
	for ldc in range(numLODs):
		f.seek(offsetInfo[ldc])
		mainmeshCount = f.readUByte()
		f.seek(3,1)
		uknFloat = f.readFloat()
		offsetSubOffsets = f.readUInt64()
		f.seek(offsetSubOffsets)
		meshOffsets = []
		for i in range(mainmeshCount):
			meshOffsets.append(f.readUInt64())
		for mmc in range(mainmeshCount):
			f.seek(meshOffsets[mmc])
			meshVertexInfo.append([f.readUByte(), f.readUByte(), f.readUShort(), f.readUInt(), f.readUInt(), f.readUInt()])
			for smc in range(meshVertexInfo[mmc][1]):
				matID = f.readUInt() + 1
				bFind = 0
				for s in range(len(objToExport)):
					sName = meshesToExport[objToExport[s]].name.split('_')
					if int(sName[1]) == (ldc+1) and int(sName[3]) == (mmc+1) and ((not bUseOldNamingScheme and int(sName[5]) == (smc+1)) or (bUseOldNamingScheme and int(sName[5]) == (matID))):
						submeshes.append(copy.copy(meshesToExport[objToExport[s]]))
						bFind = 1
						break
				if bFind == False:  #invisible placeholder submesh
					blankMeshName = "LODGroup_" + str(ldc+1) + "_MainMesh_" + str(mmc+1) + "_SubMesh_" + str(smc+1)
					blankTangent = NoeMat43((NoeVec3((0,0,0)), NoeVec3((0,0,0)), NoeVec3((0,0,0)), NoeVec3((0,0,0)))) 
					blankWeight = NoeVertWeight([0,0,0,0,0,0,0,0], [1,0,0,0,0,0,0,0])
					blankMesh = NoeMesh([0, 1, 2], [NoeVec3((0.00000000001,0,0)), NoeVec3((0,0.00000000001,0)), NoeVec3((0,0,0.00000000001))], blankMeshName, blankMeshName, -1, -1) #positions and faces
					blankMesh.setUVs([NoeVec3((0,0,0)), NoeVec3((0,0,0)), NoeVec3((0,0,0))]) #UV1
					blankMesh.setUVs([NoeVec3((0,0,0)), NoeVec3((0,0,0)), NoeVec3((0,0,0))], 1) #UV2
					blankMesh.setTangents([blankTangent, blankTangent, blankTangent]) #Normals + Tangents
					if bonesOffs > 0:
						blankMesh.setWeights([blankWeight,blankWeight,blankWeight]) #Weights + Indices
					submeshes.append(blankMesh)
					print (blankMeshName, "was not found in FBX and an invisible placeholder was created in its place")
				f.seek(12, 1)
				
	numMats = countArray[1]
	diff = 0
	f.seek(0) 
	bs.seek(0)
	
	#clone beginning of file and save new skeleton
	if bDoSkin and bWriteBones:
		boneRemapTable = []
		
		if bAddBoneNumbers and len(newSkinBoneMap) > 0:
			boneMapLength = 256 if len(newSkinBoneMap) > 256 else len(newSkinBoneMap)
		else:
			boneMapLength = 256 if len(mdl.bones) > 256 else len(mdl.bones)
			
		if fGameName == "RE7":
			f.seek(floatsHdrOffs)
			boneMapCount = f.readUInt()
			f.seek(LOD1Offs+72)
			RE7SkinBoneMapOffs = f.readUInt64()+16
			f.seek(0)
			bs.writeBytes(f.readBytes(RE7SkinBoneMapOffs)) #to skin bone map
			#write skin bone map (RE7):
			if bAddBoneNumbers and len(newSkinBoneMap) > 0:
				for i in range(len(newSkinBoneMap)):
					bs.writeUShort(newSkinBoneMap[i])
				boneRemapTable = newSkinBoneMap
			else:
				for i in range(boneMapLength): 
					bs.writeUShort(i)
					boneRemapTable.append(i)
			padToNextLine(bs)
			newMainMeshHdrOffs = bs.tell()
			
			f.seek(RE7SkinBoneMapOffs-8)
			RE7MainMeshHdrOffs = f.readUInt()
			f.seek(-12,1)
			RE7MainMeshCount = f.readUByte()
			f.seek(RE7MainMeshHdrOffs)
			diff = newMainMeshHdrOffs - RE7MainMeshHdrOffs
			bs.seek(RE7SkinBoneMapOffs-8)
			bs.writeUInt(newMainMeshHdrOffs)
			bs.seek(newMainMeshHdrOffs)
			bs.writeBytes(f.readBytes(bonesOffs - RE7MainMeshHdrOffs)) #to start of bones header
			bonesOffs = bs.tell()
			bs.seek(newMainMeshHdrOffs)
			f.seek(RE7MainMeshHdrOffs)
			for i in range(RE7MainMeshCount):
				bs.writeUInt64(f.readUInt64() + diff)
				meshOffsets[i] += diff
				
			bs.seek(bonesOffs)
		else:
			bs.writeBytes(f.readBytes(bonesOffs)) #to bone name start
		
		#write new skeleton header
		bs.writeUInt(len(mdl.bones)) #bone count
		bs.writeUInt(boneMapLength) #bone map count
		
		for b in range(5): 
			bs.writeUInt64(0)
		
		#write skin bone map:
		if fGameName != "RE7":
			if bAddBoneNumbers and len(newSkinBoneMap) > 0:
				for i in range(len(newSkinBoneMap)):
					bs.writeUShort(newSkinBoneMap[i])
				boneRemapTable = newSkinBoneMap
			else:
				for i in range(boneMapLength): 
					bs.writeUShort(i)
					boneRemapTable.append(i)
			padToNextLine(bs)
		
		if (len(boneRemapTable) > 256):
			print ("WARNING! Bone map is greater than 256 bones!")
		
		#write hierarchy
		newHierarchyOffs = bs.tell()
		for i, bone in enumerate(mdl.bones):
			bs.writeUShort(i) # bone index
			bs.writeUShort(bone.parentIndex)
			nextSiblingIdx = -1
			for j, bn in enumerate(mdl.bones):
				if i < j and bone != bn and bone.parentIndex == bn.parentIndex:
					nextSiblingIdx = j
					break
			bs.writeUShort(nextSiblingIdx)
			nextChildIdx = -1
			for j, bn in enumerate(mdl.bones):
				if bn.parentIndex == i:
					nextChildIdx = j
					break
			bs.writeUShort(nextChildIdx)
			cousinIdx = -1
			cousinBoneName = ""
			bnName = bonesList[i].lower()
			if bnName.startswith('r_'): 
				cousinBoneName = bnName.replace('r_','l_')
			elif bnName.startswith('l_'):
				cousinBoneName = bnName.replace('l_','r_')
			elif bnName.startswith("root") or bnName.startswith("cog") or bnName.startswith("hip") \
			or bnName.startswith("waist") or bnName.startswith("spine") or bnName.startswith("chest") \
			or bnName.startswith("stomach") or bnName.startswith("neck") or bnName.startswith("head") \
			or bnName.startswith("null_"):
				cousinIdx = i
			if cousinBoneName != "":
				for j in range(len(mdl.bones)):
					if bonesList[j].lower() == cousinBoneName:
						cousinIdx = j
						break
			bs.writeUShort(cousinIdx)
			padToNextLine(bs)
		
		#collect old material names:
		oldMaterialNames = []
		for i in range(numMats): 
			f.seek(matNameAddressList[i])
			oldMaterialNames.append(f.readString())
		
		#prepare transform data:
		localTransforms = []
		globalTransforms = []
		for bone in mdl.bones:
			boneGlobalMat = bone.getMatrix().toMat44()
			boneGlobalMat[3] = boneGlobalMat[3] * 0.01 * scale
			boneGlobalMat[3][3] = 1.0
			globalTransforms.append(boneGlobalMat)
			if bone.parentIndex != -1:
				pMat = mdl.bones[bone.parentIndex].getMatrix().toMat44()
				boneLocalMat = (bone.getMatrix().toMat44() * pMat.inverse())
				boneLocalMat[3] = boneLocalMat[3] * 0.01 * scale
				boneLocalMat[3][3] = 1.0
				localTransforms.append(boneLocalMat)
			else:
				localTransforms.append(boneGlobalMat)
		
		#write local bone transforms:
		newLocalOffs = bs.tell()
		for i in range(len(localTransforms)):
			bs.writeBytes(localTransforms[i].toBytes())
		
		#write global bone transforms:
		newGlobalOffs = bs.tell()
		for i in range(len(globalTransforms)):
			bs.writeBytes(globalTransforms[i].toBytes())
		
		#write inverse global bone transforms:
		newInvGlobOffs = bs.tell()
		for i in range(len(globalTransforms)):
			bs.writeBytes(globalTransforms[i].inverse().toBytes())
		
		#write material indices:
		newMatIndicesOffs = bs.tell()
		for i in range(numMats): 
			f.seek(nodesIndicesOffs + i * 2)
			bs.writeUShort(f.readUShort())
		padToNextLine(bs)
		
		boneInds = []
		#write bone map indices:
		newBoneMapIndicesOffs = bs.tell()
		for i in range(len(mdl.bones)): 
			bs.writeUShort(numMats + i)
			boneInds.append(numMats + i)
		padToNextLine(bs)
		
		#write names offsets:
		newNamesOffs = bs.tell()
		nameStringsOffs = newNamesOffs + (numMats + len(mdl.bones)) * 8
		while nameStringsOffs % 16 != 0:
			nameStringsOffs += 1
		
		for i in range(numMats): 
			bs.writeUInt64(nameStringsOffs)
			nameStringsOffs += len(oldMaterialNames[i]) + 1
		for i in range(len(mdl.bones)): 
			bs.writeUInt64(nameStringsOffs)
			nameStringsOffs += len(bonesList[i]) + 1
		padToNextLine(bs)
		
		names = []
		#write name strings
		for i in range(len(oldMaterialNames)):
			bs.writeString(oldMaterialNames[i])
			names.append(oldMaterialNames[i])
		for i in range(len(bonesList)): 
			bs.writeString(bonesList[i])
			names.append(bonesList[i])
		padToNextLine(bs)
		
		#write bounding boxes
		newBBOffs = bs.tell()
		bs.writeUInt64(len(newSkinBoneMap))
		bs.writeUInt64(bs.tell() + 8)
		for i in range(len(newSkinBoneMap)):
			for j in range(3): bs.writeFloat(-0.01)
			bs.writeFloat(1)
			for j in range(3): bs.writeFloat(0.01)
			bs.writeFloat(1)
				 
		diff = bs.tell() - vBuffHdrOffs #to start of VertexBufferInfo
		
		#fix bones header
		bs.seek(bonesOffs + 16)
		bs.writeUInt64(newHierarchyOffs)
		bs.writeUInt64(newLocalOffs)
		bs.writeUInt64(newGlobalOffs)
		bs.writeUInt64(newInvGlobOffs)
		
		#fix main header
		bs.seek(18)
		if fGameName == "RE7": bs.seek(-4,1)
		bs.writeUShort(numMats + len(mdl.bones)) #numNodes
		if fGameName == "RE7": 
			bs.seek(24,1)
			bs.writeUInt64(bonesOffs)
		bs.seek(72)
		if fGameName == "RE7": bs.seek(-16,1)
		bs.writeUInt64(newBBOffs)
		bs.writeUInt64(vBuffHdrOffs + diff)
		bs.seek(8, 1)
		bs.writeUInt64(newMatIndicesOffs)
		bs.writeUInt64(newBoneMapIndicesOffs)
		bs.seek(8, 1)
		bs.writeUInt64(newNamesOffs)
		
		#copy + fix vertexBufferHeader
		bs.seek(vBuffHdrOffs + diff)
		f.seek(vBuffHdrOffs)
		if fGameName == "RE7":
			bs.writeBytes(f.readBytes(48))
		else:
			bs.writeUInt64(f.readUInt64() + diff)
			newVertBuffOffs = f.readUInt64() + diff
			bs.writeUInt64(newVertBuffOffs)
			for i in range(int((vertBuffOffs - f.tell()) / 8)):
				bs.writeUInt64(f.readUInt64())
			pos = bs.tell()
			bs.seek(vBuffHdrOffs + diff + 44)
			bs.writeInt(-newVertBuffOffs) #vertexBufferOffs (negative)
			bs.seek(pos)
	else:
		bs.writeBytes(f.readBytes(vertBuffOffs))
		
	if bReWrite:
		pass
		
	vertexStrideStart = 0
	submeshVertexCount = []
	submeshVertexStride = []
	submeshFaceCount = []
	submeshFaceStride = []
	submeshFaceSize = []
	
	#Write vertex data
	vertexPosStart = bs.tell()
	if fGameName == "RE7":
		for mesh in submeshes:
			submeshVertexStride.append(vertexStrideStart)
			submeshVertexCount.append(len(mesh.positions))
			for v in range(len(mesh.positions)):
				bs.writeBytes((mesh.positions[v] * 0.01).toBytes())
				bs.writeByte(int(mesh.tangents[v][0][0] * 127 + 0.5)) #normal
				bs.writeByte(int(mesh.tangents[v][0][1] * 127 + 0.5))
				bs.writeByte(int(mesh.tangents[v][0][2] * 127 + 0.5))
				bs.writeByte(0)
				bs.writeByte(int(mesh.tangents[v][2][0] * 127 + 0.5)) #bitangent
				bs.writeByte(int(mesh.tangents[v][2][1] * 127 + 0.5))
				bs.writeByte(int(mesh.tangents[v][2][2] * 127 + 0.5))
				TNW = dot(cross(mesh.tangents[v][0], mesh.tangents[v][1]), mesh.tangents[v][2])
				if (TNW < 0.0):
					bs.writeByte(w1)
				else:
					bs.writeByte(w2)
				bs.writeHalfFloat(mesh.uvs[v][0])
				bs.writeHalfFloat(mesh.uvs[v][1])
				if doUV1:
					bs.writeHalfFloat(mesh.lmUVs[v][0])
					bs.writeHalfFloat(mesh.lmUVs[v][1])
				if bDoSkin:
					pos = bs.tell()
					for i in range(4):
						bs.writeFloat(0)
					bs.seek(pos)
					
					total = 0
					tupleList = []
					weightList = []
					for idx in range(len(mesh.weights[v].weights)):
						weightList.append(round(mesh.weights[v].weights[idx] * 255.0))
						total += weightList[idx]
					if bNormalizeWeights and total != 255:
						weightList[0] += 255 - total
						print ("Normalizing vertex weight", mesh.name, "vertex", v,",", total)
							
					for idx in range(len(mesh.weights[v].weights)):
						if idx > 8:
							print ("Warning: ", mesh.name, "vertex", v,"exceeds the vertex weight limit of 8!", )
							break
						elif mesh.weights[v].weights[idx] != 0:				
							byteWeight = weightList[idx]
							tupleList.append((byteWeight, mesh.weights[v].indices[idx]))
							
					tupleList = sorted(tupleList, reverse=True) #sort in ascending order
					
					pos = bs.tell()
					lastBone = 0
					for idx in range(len(tupleList)):	
						#if True:
						bFind = False
						for b in range(len(boneRemapTable)):
							if names[boneInds[boneRemapTable[b]]] == bonesList[tupleList[idx][1]]:
								bs.writeUByte(b)
								lastBone = b
								bFind = True
								break	
						if bFind == False: #assign unmatched bones
							if not bRigToCoreBones:
								bs.writeUByte(lastBone)
							else:
								for b in range(lastBone, 0, -1):
									if names[boneInds[boneRemapTable[b]]].find("spine") != -1 or names[boneInds[boneRemapTable[b]]].find("hips") != -1:
										bs.writeUByte(b)
										break
					for x in range(8 - len(tupleList)):
						bs.writeUByte(lastBone)
					
					bs.seek(pos+8)
					for wval in range(len(tupleList)):
						bs.writeUByte(tupleList[wval][0])
					bs.seek(pos+16)
			vertexStrideStart += len(mesh.positions)
	else:
		for mesh in submeshes:
			submeshVertexStride.append(vertexStrideStart)
			for vcmp in mesh.positions:
				bs.writeBytes((vcmp * 0.01).toBytes())
			submeshVertexCount.append(len(mesh.positions))
			vertexStrideStart += len(mesh.positions)
				
		normalTangentStart = bs.tell()	
		for mesh in submeshes:
			for vcmp in mesh.tangents:
				bs.writeByte(int(vcmp[0][0] * 127 + 0.5)) #normal
				bs.writeByte(int(vcmp[0][1] * 127 + 0.5))
				bs.writeByte(int(vcmp[0][2] * 127 + 0.5))
				bs.writeByte(0)
				bs.writeByte(int(vcmp[2][0] * 127 + 0.5)) #bitangent
				bs.writeByte(int(vcmp[2][1] * 127 + 0.5))
				bs.writeByte(int(vcmp[2][2] * 127 + 0.5))
				TNW = dot(cross(vcmp[0], vcmp[1]), vcmp[2])
				if (TNW < 0.0):
					bs.writeByte(w1)
				else:
					bs.writeByte(w2)
						
		UV0start = bs.tell()
		for mesh in submeshes:
			for vcmp in mesh.uvs:
				bs.writeHalfFloat(vcmp[0])
				bs.writeHalfFloat(vcmp[1])
					
		UV1start = bs.tell()
		if doUV1:
			for mesh in submeshes:
				for vcmp in mesh.lmUVs:
					bs.writeHalfFloat(vcmp[0])
					bs.writeHalfFloat(vcmp[1])
		
		bnWeightStart = bs.tell()
		if bDoSkin:
			for m, mesh in enumerate(submeshes):
				pos = bs.tell()
				for vcmp in mesh.weights: #write 0's
					for i in range(4):
						bs.writeFloat(0)
				bs.seek(pos)
				
				for i, vcmp in enumerate(mesh.weights): #write bone indices & weights over 0's
					total = 0
					tupleList = []
					weightList = []
					for idx in range(len(vcmp.weights)):
						weightList.append(round(vcmp.weights[idx] * 255.0))
						total += weightList[idx]
					if bNormalizeWeights and total != 255:
						weightList[0] += 255 - total
						print ("Normalizing vertex weight", mesh.name, "vertex", i,",", total)
							
					for idx in range(len(vcmp.weights)):
						if idx > 8:
							print ("Warning: ", mesh.name, "vertex", i,"exceeds the vertex weight limit of 8!", )
							break
						elif vcmp.weights[idx] != 0:				
							byteWeight = weightList[idx]
							tupleList.append((byteWeight, vcmp.indices[idx]))
							
					tupleList = sorted(tupleList, reverse=True) #sort in ascending order
					
					pos = bs.tell()
					lastBone = 0
					for idx in range(len(tupleList)):	
						#if True:
						bFind = False
						for b in range(len(boneRemapTable)):
							if names[boneInds[boneRemapTable[b]]] == bonesList[tupleList[idx][1]]:
								bs.writeUByte(b)
								lastBone = b
								bFind = True
								break	
						if bFind == False: #assign unmatched bones
							if not bRigToCoreBones:
								bs.writeUByte(lastBone)
							else:
								for b in range(lastBone, 0, -1):
									if names[boneInds[boneRemapTable[b]]].find("spine") != -1 or names[boneInds[boneRemapTable[b]]].find("hips") != -1:
										bs.writeUByte(b)
										break
					for x in range(8 - len(tupleList)):
						bs.writeUByte(lastBone)
					
					bs.seek(pos+8)
					for wval in range(len(tupleList)):
						bs.writeUByte(tupleList[wval][0])
					bs.seek(pos+16)
	vertexDataEnd = bs.tell()
	
	for mesh in submeshes:
		faceStart = bs.tell()
		submeshFaceStride.append(faceStart - vertexDataEnd)
		submeshFaceCount.append(len(mesh.indices))
		submeshFaceSize.append(len(mesh.indices))
		for idx in mesh.indices:
			bs.writeUShort(idx)
		if ((bs.tell() - faceStart) / 6) % 2 != 0: #padding
			bs.writeUShort(0)
	faceDataEnd = bs.tell()
	
	#update mainmesh and submesh headers
	loopSubmeshCount = 0
	for ldc in range(numLODs):
		for mmc in range(mainmeshCount):
			mainmeshVertexCount = 0
			mainmeshFaceCount = 0
			bs.seek(meshOffsets[mmc] + 16)
			for smc in range(meshVertexInfo[mmc][1]):
				bs.seek(4, 1)
				bs.writeUInt(submeshFaceCount[loopSubmeshCount])
				bs.writeUInt(int(submeshFaceStride[loopSubmeshCount] / 2))
				bs.writeUInt(submeshVertexStride[loopSubmeshCount])
				if fGameName == "REVerse" or fGameName == "MHRise" or fGameName == "RE8":
					bs.seek(8, 1)
				mainmeshVertexCount += submeshVertexCount[loopSubmeshCount]
				mainmeshFaceCount += submeshFaceSize[loopSubmeshCount]
				loopSubmeshCount += 1
			bs.seek(meshOffsets[mmc]+8)
			bs.writeUInt(mainmeshVertexCount)
			bs.writeUInt(mainmeshFaceCount)
	
	if fGameName == "RE7":
		bs.seek(vBuffHdrOffs + diff)
		bs.writeUInt(vertexDataEnd - vertexPosStart) #Vertex Buffer Size
		bs.seek(12,1)
		bs.writeUInt(faceDataEnd - vertexDataEnd) #Face Buffer Size
		bs.seek(20,1)
		bs.writeUInt64(vertexDataEnd) #Face Buffer Offset
	else:
		bs.seek(vBuffHdrOffs + 16 + diff)
		bs.writeInt64(vertexDataEnd) #Face Buffer Offset
		fcBuffSize = faceDataEnd - vertexDataEnd
		bs.writeUInt(vertexDataEnd - vertexPosStart) #Vertex Buffer Size
		bs.writeUInt(fcBuffSize)	#Face Buffer Size
		bs.seek(vertElemHdrOffs + diff)
		for i in range (vertElemCountB):
			elementType = bs.readUShort()
			elementSize = bs.readUShort()
			if elementType == 0:
				bs.writeUInt(vertexPosStart - vertexPosStart)
			elif elementType == 1:
				bs.writeUInt(normalTangentStart - vertexPosStart)
			elif elementType == 2:
				bs.writeUInt(UV0start - vertexPosStart)
			elif elementType == 3:
				bs.writeUInt(UV1start - vertexPosStart)
			elif elementType == 4:
				bs.writeUInt(bnWeightStart - vertexPosStart)
	
	#disable LOD
	bs.seek(LOD1Offs)
	bs.writeByte(1)
	
	#disable 2nd LOD set
	bs.seek(32)
	if fGameName == "RE7": bs.seek(-8,1)
	bs.writeUShort(0)
	
	#shadow fix
	#if bDoSkin:
		#bs.seek(16)
		#if fGameName == "RE7": bs.seek(-4,1)
		#bs.writeByte(3)
	
	#remove topology data
	bs.seek(56)
	if fGameName != "RE7":
		bs.writeUInt(0)
	
	#remove blendshapes offsets
	bs.seek(64)
	if fGameName == "RE7": bs.seek(-16,1)
	bs.writeUInt(0)
	bs.seek(112)
	if fGameName == "RE7": bs.seek(-16,1)
	bs.writeUInt(0)
	bs.seek(vBuffHdrOffs + 36)
	if fGameName != "RE7" and faceBufferSize2nd > 0:
		bs.writeUInt64(fcBuffSize) #face buffer size (2nd)
		bs.writeInt(-(vertBuffOffs)) #set blendshapes offset to -VertexBufferOffset
	else:
		bs.seek(8,1)
	
	#fileSize
	bs.seek(8)
	bs.writeUInt(faceDataEnd) 
	return 1