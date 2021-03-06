#cue extraction support

from inc_noesis import *
from inc_imgtools import NoeImgReader, NoeImgTrack
import shlex

MAX_REASONABLE_CUE_SIZE = 1024 * 1024

def registerNoesisTypes():
	handle = noesis.register("Cue Sheet container", ".cue")
	noesis.setHandlerExtractArc(handle, cueExtractArc)
	noesis.addOption(handle, "-cuepreservexa", "write whole sectors for files beginning with cdxa video/audio.", 0)
	#cuepreserveall may be necessary for some special cases where a file is marked data-only but still needs the xa header to be interpreted correctly
	noesis.addOption(handle, "-cuepreserveall", "write whole sectors for all files.", 0)
	return 1

def lbaToMsf(lba):
	second = 75
	minute = second * 60
	
	minutes = lba // minute
	seconds = (lba // second) % 60
	frames = lba % 75
	return "%02i:%02i:%02i"%(minutes, seconds, frames)
	
def msfToLba(msf):
	s = msf.split(":")
	if len(s) != 3:
		print("Warning: Bad MSF formatting -", msf)
		return 0
		
	secondSize = 75
	minuteSize = secondSize * 60
	return int(s[2]) + int(s[1]) * secondSize + int(s[0]) * minuteSize
	
class CueTrack:
	def __init__(self, binPath, fullBinPath, trackIndex, sectorSize, userSize, headerSize):
		self.binPath = binPath
		self.fullBinPath = fullBinPath
		self.trackIndex = trackIndex
		self.sectorSize = sectorSize
		self.userSize = userSize
		self.headerSize = headerSize
		self.preGap = 0
		self.postGap = 0
		self.startLba = 0
		self.sizeInBlocks = 0

	def calculateSizeInBlocks(self):
		with open(self.fullBinPath, "rb") as f:
			f.seek(0, os.SEEK_END)
			size = f.tell()
			if (size % self.sectorSize) != 0:
				print("Warning: Image not evenly divisible by sector size:", self.binPath)
			self.sizeInBlocks = size // self.sectorSize
	
def cueExtractArc(fileName, fileLen, justChecking):
	if fileLen > MAX_REASONABLE_CUE_SIZE: #sanity check
		return 0

	preserveXA = noesis.optWasInvoked("-cuepreservexa")
	preserveAll = noesis.optWasInvoked("-cuepreserveall")

	curTrackBinPath = None
	curTrackFullBinPath = None
	curTrackIndex = -1
	cueTracks = []
	discardHeaderWarning = False
	try:
		with open(fileName, "r") as f:
			for line in f:
				values = shlex.split(line)
				if len(values) > 0:
					cmd = values[0].lower()
					if cmd == "file" and len(values) >= 2:
						curTrackBinPath = None
						curTrackIndex = -1
						path = values[1]
						type = values[2].lower()
						if type == "binary" or type == "motorola":
							fullPath = os.path.join(rapi.getDirForFilePath(fileName), path)
							if os.path.exists(fullPath):
								curTrackBinPath = path
								curTrackFullBinPath = fullPath
							else:
								print("Warning: Can't find track data:", fullPath)
						else:
							print("Not searching for volume in track type:", type)
					elif cmd == "track" and len(values) >= 2:
						if curTrackBinPath:
							trackTypeDict = {
								#haven't tested most of these, let me know if one of them falls over
								"audio" : (2352, 2352, 0),
								"cdg" : (2448, 2448, 0),
								"mode1/2048" : (2048, 2048, 0),
								"mode1/2352" : (2352, 2048, 16), #mode 1
								"mode2/2048" : (2352, 2048, 24), #xa form 1
								"mode2/2324" : (2352, 2324, 24), #xa form 2
								"mode2/2336" : (2352, 2336, 16), #mode 2
								"mode2/2352" : (2352, 2048, 24), #xa "raw" (mmv, but typically want to discard error data as used by psx rips and such)
								"cdi/2336" : (2352, 2048, 24),
								"cdi/2352" : (2352, 2324, 24)
							}
							trackType = values[2].lower()
							if trackType in trackTypeDict:
								if trackType == "mode2/2352" and not preserveXA and not preserveAll:
									discardHeaderWarning = True
								curTrackIndex = len(cueTracks)
								sectorSize, userSize, headerSize = trackTypeDict[trackType]
								cueTracks.append(CueTrack(curTrackBinPath, curTrackFullBinPath, int(values[1]), sectorSize, userSize, headerSize))
							else:
								print("Warning: Unsupported track type:", trackType)
								curTrackIndex = -1
					elif cmd == "pregap" and curTrackIndex >= 0 and len(values) >= 2:
						cueTracks[curTrackIndex].preGap += msfToLba(values[1])
					elif cmd == "postgap" and curTrackIndex >= 0 and len(values) >= 2:
						cueTracks[curTrackIndex].postGap += msfToLba(values[1])
					elif cmd == "index" and curTrackIndex >= 0 and len(values) >= 3:
						i = int(values[1])
						if i == 0:
							cueTracks[curTrackIndex].preGap += msfToLba(values[2])
						elif i == 1:
							#supposedly this can also be absolute instead of relative to the last track, but don't have any samples to test that.
							cueTracks[curTrackIndex].startLba += msfToLba(values[2])
					#otherwise discard the line (this includes rem)
	except:
		return 0

	if len(cueTracks) == 0:
		return 0

	if justChecking:
		return 1

	cueTracks = sorted(cueTracks, key=noeCmpToKey(lambda a,b: a.trackIndex - b.trackIndex))
	currentLba = 0
	tracks = []
	for cueTrack in cueTracks:
		cueTrack.calculateSizeInBlocks()
		currentLba += cueTrack.startLba + cueTrack.preGap
		track = NoeImgTrack(open(cueTrack.fullBinPath, "rb"), cueTrack.trackIndex, currentLba, cueTrack.sectorSize, cueTrack.userSize, cueTrack.headerSize)
		track.binPath = cueTrack.binPath
		track.fullBinPath = cueTrack.fullBinPath
		tracks.append(track)
		currentLba += cueTrack.sizeInBlocks + cueTrack.postGap
	
	img = NoeImgReader(tracks)
	for track in tracks:
		imgVol = img.readFileSystemVolume(track.index)
		if imgVol:
			preserveFullSector = (preserveXA and track.sectorSize == 2352) or preserveAll
			print("Read volume information from", track.fullBinPath)
			for imgFile in imgVol.files:
				writePath = track.binPath + "_track%02i/"%track.index + imgFile.path

				typeSuffix = ""
				originalSectorSize = track.userSize
				originalSectorOffset = track.userOffset
				if preserveFullSector and len(imgFile.lbas) > 0:
					track.userSize = track.sectorSize
					track.userOffset = 0
					if not preserveAll:
						#check for xa video/audio
						img.setSector(imgFile.lbas[0])
						xaData = img.readSectors(1)
						xaSm = xaData[18]
						isAudio = (xaSm & 4) != 0
						#consider realtime without audio/video set to be video as well
						isVideo = (xaSm & 2) != 0 or ((xaSm & 6) == 0 and (xaSm & 64) != 0)
						if isAudio or isVideo:
							typeSuffix = " (video)" if isVideo else " (audio)"
						else:
							#set it back before the read if this isn't audio/video
							track.userSize = originalSectorSize
							track.userOffset = originalSectorOffset

				if track.userSize != originalSectorSize:
					#modify the file size(s) to reflect the full sector size
					for sizeIndex in range(len(imgFile.sizes)):
						originalSize = imgFile.sizes[sizeIndex]
						originalSectorCount = (originalSize + (originalSectorSize - 1)) // originalSectorSize
						imgFile.sizes[sizeIndex] = originalSectorCount * track.userSize

				print("Writing", writePath + typeSuffix)
				rapi.exportArchiveFile(writePath, img.readFileData(imgFile))
				track.userSize = originalSectorSize
				track.userOffset = originalSectorOffset
	img.close()

	if discardHeaderWarning:
		print("Warning: CD-XA header data was discarded, consider using -cuepreservexa when extracting this image.")
	
	return 1
