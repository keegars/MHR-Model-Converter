--RE Engine MESH Noesis CMD tool
--Version: v0.28
--Last Release: August 16 2021
--Authors: mariokart64n and alphaZomega

global noesis_path = "C:\\Program Files (x86)\\Noesis\\Noesis.exe"
global reimport_path = "D:\\"
global python_plugin = "fmt_RE_MESH.py"
global formNoesisCMD

fn collectSkinBones node = (
	fn findNodesByName list name = (
		for node in list where stricmp node.name name == 0 collect node
	)
	max modify mode
	local bones = #()
	for sk in node.modifiers where iskindof sk Skin do (
		modpanel.setcurrentobject sk
		nodes = for n in (refs.dependson sk) where isvalidnode n collect n
		
		for k=1 to skinops.getnumberbones sk do (
			name = skinops.getbonename sk k 0
			join bones (findNodesByName nodes name)
		)
	)
	bones
)	

fn selectSkeleton node = (
	local originalSelection = selection as array
	local bones = collectSkinBones node
	while bones[1].parent != undefined do
		bones[1] = bones[1].parent
	bones = #(bones[1])
	for p in bones where p.children != undefined do join bones p.children
	join originalSelection bones
	select originalSelection
)

fn findBoneIdx skinMod bnName = ( 
	for i=1 to (skinOps.GetNumberBones skinMod) do ( 
		if bnName == (skinOps.GetBoneName skinMod i 0) then (
			return i 
		)
	)
	return 0
)

try(destroydialog formNoesisCMD; clearlistener())catch()
rollout formNoesisCMD "REEM Noesis 0.28" (
	
	group "Import" (
		button btn_import "Import To Scene" align:#center
		checkbox chk_resetScene "Reset On Import" checked:false align:#left
		checkbox chk_legacyFBX "Use Legacy FBX" checked:false align:#left 
		checkbox chk_fbxMerge "fbxmeshmerge" checked:true align:#left tooltip:"Merges together meshes that have been split apart and have \"0001_\" before their names"
		checkbox chk_folder "Import Folder" checked:false align:#left
	)
	group "Export" (
		button btn_export "Export to Game" align:#center
		checkbox chk_writeBones "Write skeleton" checked:false align:#left
		checkbox chk_flipHandedness "DirectX handedness" checked:true align:#left
	)
	group "Utilities" (		
		button BtnRemoveBoneNumbers "Add/Remove Bone Numbers" align:#center 
		--button BtnSkinOnTop "Move Skin to Top of Stack" align:#center 
		button BtnSetScale "xScale" offset:[-30,0]
		edittext FldScale "" text:"1.0" fieldWidth:60 labelOnTop:false offset:[70,-25]
		button btn_reimport "Reimport Noesis FBX" align:#center
		--checkbox chk_uv2 "UV2 Version" checked:false align:#right
		button BtnAnimToBlender "Export FBX Animation" align:#center

	)
	group "Config" (
		checkbox chk_showPlugOpt  "Show FBX Options" checked:true align:#left
		checkbox chk_delFBX  "Delete FBX Files" checked:true align:#left
		checkbox chk_bnNumbers  "Use Bone Numbers" checked:true align:#left
		checkbox chk_showCMD  "Show Console" checked:false align:#left enabled:true
		
		label lbl_noesis "Noesis Path:" align:#left
		edittext edt_noesis "" align:#left
		button btn_noesis "Browse" align:#center
	)
	
	local ScaleValue = 1.0
	local cmd = ""
	local fbx_path = ""
	
	fn checkDialog = (
		local hwnd = dialogMonitorOps.getWindowHandle()
		if (uiAccessor.getWindowText hwnd == "Import Name Conflict") then (
			uiAccessor.PressButtonByName hwnd "OK"
		)
		true
	)
	fn waitForFileUnlock file file_open_limit:30 = (
		local i = 0
		while i < file_open_limit do (
			if (try(renameFile file (file + ".tmp"))catch(false)) do (
				renameFile (file + ".tmp") file
				exit
			)
			sleep 1
			i += 1
		)
	)
	fn noesisComponentsFound = (
		local state = false
		--if doesFileExist noesis_path and doesFileExist ((getFilenamePath noesis_path) + "plugins\\python\\" + python_plugin) do (
		if doesFileExist noesis_path do (
			state = true
		)
		state
	)
	on formNoesisCMD open do (
		if doesFileExist (try(noesis_path)catch("")) do (
			edt_noesis.text = noesis_path
			)
		)
	on btn_noesis pressed do (
		cmd = getOpenFileName types:"Noesis.exe|noesis.exe|All|*.*|"
		if cmd != undefined and cmd != "" do (
			edt_noesis.text = noesis_path = cmd
		)
	)
	on edt_noesis changed cmd do (
		edt_noesis.text = noesis_path = cmd
	)
	
	on btn_import pressed do (
		
		if noesisComponentsFound() then (
			cmd = getOpenFileName types:"RE Engine Model|*.32;*.1808282334;*.1902042334;*.1808312334;*.2101050001;*.32;*.2010231143;|All|*.*|"
			if cmd != undefined and doesFileExist cmd do (
				local showFbxOptions = chk_showPlugOpt.checked
				
				local files = #(cmd)
				if chk_folder.checked then 
					files = getFiles (getFilenamePath cmd + "\\*.mesh.*")
				
				for f = 1 to files.count do (
					cmd = files[f]
					if chk_resetScene.checked do 
						resetMaxFile #noPrompt
					fbx_path = (getFilenamePath cmd) + (getFilenameFile (getFilenameFile cmd)) + ".fbx"
					cmd = (
						"\"" + noesis_path + "\" ?cmode \"" + cmd + "\" \"" + fbx_path + "\"" \
						 + (if chk_legacyFBX.checked then " -fbxoldexport -fbxexportver FBX201400" else "") \
						 + (if chk_bnNumbers.checked then " -bonenumbers" else "") \
						 + (if chk_fbxMerge.checked then " -fbxmeshmerge" else "") \
						 + (" -noprompt") \
					)
					if chk_showCMD.checked then (
						DOSCommand ("\"" + cmd + "\"") 
					)
					else (
						HiddenDOSCommand ("\"" + cmd + "\"") startpath:(getFilenamePath noesis_path) donotwait:false
					)
					
					waitForFileUnlock(fbx_path)
					if showFbxOptions then (--chk_impPrompt
						success = importFile fbx_path using:FBXIMP
					)
					else (
						success = importFile fbx_path #noPrompt using:FBXIMP
					)
					if chk_delFBX.checked do (deleteFile fbx_path)
					
					format "%\n" cmd
					
					if success and chk_bnNumbers.checked then (
						with redraw off (
							local objSelected = selection as array
							local meshes = for obj in objSelected where (classof obj == Editable_mesh) collect obj 
							local bones = for obj in objSelected where (superclassof obj == Helper or classof obj == BoneGeometry) collect obj 
							for bone in bones do hide bone
							container = Point size:1.0
							local uniqueNames = #(); local mainmeshes = #()
							container.name = getFilenameFile (getFilenameFile cmd)
							
							for mesh in meshes do ( -- create MainMesh containers
								fs = filterstring mesh.name "_"
								if appendIfUnique uniqueNames (fs[1] + "_" + fs[2] + "_" + fs[3] + "_" + fs[4]) then (
									mainmesh = Point size:1.0
									mainmesh.name = (fs[1] + "_" + fs[2] + "_" + fs[3] + "_" + fs[4])
									mainmesh.parent = container
									append mainmeshes mainmesh
								)
								mesh.parent = mainmeshes[mainmeshes.count]
							)
							
							for mesh in meshes do (
								mesh.material = undefined
								mesh.wirecolor = color (random 0 255) (random 0 255) (random 0 255)
								if getNumVerts mesh == 3 or mesh.modifiers[#Skin] == undefined then continue
								select mesh
								max modify mode
								mesh.modifiers[#Skin].bone_Limit = 8 
								for b = 1 to bones.count do (
									bones[b].showLinks = true
									bones[b].showLinksOnly = true
									bones[b].wirecolor = yellow
									fs = filterstring bones[b].name ":"
									if fs.count > 1 then (
										if (getuserprop bones[b] "Bone_Number") == undefined do setuserprop bones[b] "Bone_Number" fs[1]
										if (getuserprop bones[b] "Bone_Name") == undefined do setuserprop bones[b] "Bone_Name" fs[2]
									)
									bnIdx = findBoneIdx mesh.modifiers[#Skin] bones[b].name
									if bnIdx == 0 then ( -- add bones to Skin that have numbers but are not currently in
										if fs.count > 1 then 
											skinOps.addBone mesh.modifiers[#Skin] bones[b] 0
									) else if fs.count == 1 then ( -- remove bones from Skin that have no numbers
										skinOps.selectbone mesh.modifiers[#Skin] bnIdx
										skinOps.removebone mesh.modifiers[#Skin]
									)
								)
							)
						)
					)
					if chk_folder.checked then
						showFbxOptions = false
				)
			)
		) else (messagebox "Failed to Locate Noesis!")
	)
	
	on btn_export pressed do (
		if noesisComponentsFound() then (
			cmd = getOpenFileName types:"RE Engine Model|*.1808282334;*.1902042334;*.2010231143;*.2101050001;*.32;*.1808312334|All|*.*|"			--"Resident Evil 2R|*.1808312334|Resident Evil 3R|*.1902042334|Devil May Cry 5|*.1808282334"
			if cmd != undefined and cmd != "" do (
			
				fbx_path = (getFilenamePath cmd) + (getFilenameFile (getFilenameFile cmd)) + ".fbx"
				out_path = (getFilenamePath cmd) + (getFilenameFile (getFilenameFile cmd)) + ".NEW.mesh" + (getFilenameType  cmd)
				
				if findString (toLower fbx_path) ".ORIG.fbx" != undefined then (
					newExtension = getFilenameType out_path
					meshPath = (replace fbx_path (findString (toLower fbx_path) "ORIG.fbx") 8 ("mesh" + newExtension))
					format "Changing file output from % to %\n" (getFilenameFile out_path) (getFilenameFile meshPath)
					out_path = meshPath
				)
				originalSelection = selection as array
				copyNodes = #()
				for obj in originalSelection where superclassof obj == GeometryClass and obj.modifiers[#Skin] != undefined do ( 
					try (
						selectSkeleton obj
						if chk_writeBones.checked then ( --Create dummy mesh with all bones in skin modifier so that FBX will save all bones
							maxOps.cloneNodes obj cloneType:#copy newNodes:&copyNodes #nodialog
							lastSelection = (selection as array); select copyNodes[1]; copyNodes[1].name = "FBXBoneStorage"
							for bn in lastSelection do 
								if superclassof bn == Helper or classof bn == BoneGeometry then 
									skinops.addBone copyNodes[1].modifiers[#Skin] bn 0
							selectmore lastSelection
						)
						exit 
					) catch ( print "Could not select skeleton! Select bones manually before export" )
				)
				if chk_showPlugOpt.checked then (--chk_expPrompt
					exportFile fbx_path selectedOnly:true using:FBXEXP
				) else (
					exportFile fbx_path #noPrompt selectedOnly:true using:FBXEXP
				)
				if copyNodes[1] != undefined then delete copyNodes[1]
				if doesFileExist fbx_path do (
					
					waitForFileUnlock(fbx_path)
					cmd = (
						"\"" + noesis_path + "\" ?cmode \"" + fbx_path + "\" \"" + out_path + "\"" \
						+ (if chk_writeBones.checked then " -bones" else "") \
						+ (if not chk_flipHandedness.checked then " -flip" else "") \
						+ (if chk_bnNumbers.checked then " -bonenumbers" else "") \
						+ (" -meshfile \"" + cmd + "\"")
					)
					if chk_showCMD.checked then (
						DOSCommand ("\"" + cmd + "\"")
					)
					else (
						HiddenDOSCommand ("\"" + cmd + "\"") startpath:(getFilenamePath noesis_path) donotwait:false
					)
					waitForFileUnlock(fbx_path)
					if chk_delFBX.checked do (deleteFile fbx_path)
				)
				format "%\n" cmd				 
				
				select originalSelection
			)
		) else (messagebox "Failed to Locate Noesis!")
	)
	
	on btn_reimport pressed do (
		if true then ( --with redraw off (
			if noesisComponentsFound() then (
				if superclassof $ != GeometryClass then return false
				cmd = reimport_path + "ReImportedMeshout.fbx"
				newFile = cmd; 
				origNode = $
				fbx_path = reimport_path + "ReImportedMesh.fbx"
				copyNodes = #(); maxOps.cloneNodes selection cloneType:#copy newNodes:&copyNodes #nodialog
				select copyNodes[1]; collapsestack $; $.name = origNode.name
				if chk_showPlugOpt.checked then (--chk_expPrompt
					if not (exportFile fbx_path selectedOnly:true using:FBXEXP) then format ("Failed to export %\n" fbx_path)
				)
				else (
					if not (exportFile fbx_path #noPrompt selectedOnly:true using:FBXEXP) then format ("Failed to export %\n" fbx_path)
				)
				if doesFileExist fbx_path do (
					waitForFileUnlock(fbx_path)
					cmd = (
						"\"" + noesis_path + "\" ?cmode \"" + fbx_path + "\" \"" + cmd + "\"" + " -noanims -notex -fbxmeshmerge"  -- + (if chk_noesisOpt.checked then " -RPGOptimize" else "")
					)
					if chk_showCMD.checked then (
						DOSCommand ("\"" + cmd + "\"")
					)
					else (
						HiddenDOSCommand ("\"" + cmd + "\"") startpath:(getFilenamePath noesis_path) donotwait:false
					)
					
					format "%\n" cmd
					waitForFileUnlock(fbx_path)
					waitForFileUnlock(newFile)
					oldObj = objects as array
					
					if chk_showPlugOpt.checked then (
						if not (importFile newFile using:FBXIMP) then ( format "Failed to import %\n" newFile)
					) else ( if not (importFile newFile #noPrompt using:FBXIMP) then ( format "Failed to import %\n" newFile) )
					
					if chk_delFBX.checked do (
						deleteFile fbx_path
						deleteFile newFile
					)
					
					newObj = for o in objects where findItem oldObj o == 0 collect o
					for obj in newObj do (
						if superclassof obj == GeometryClass then 
							selectmore obj
						else delete obj
					)
					
					/*if origNode.modifiers[#Skin] != undefined then (
						collapsestack $
						addModifier $ (Skin_Wrap())
						skinWrap = $.modifiers["Skin_Wrap"]
						skinWrap.weightAllVerts = true
						skinWrap.falloff = 1.0
						skinWrap.Distance = 0.05
						skinWrap.meshList = #(origNode)
						skinWrap.convertToSkin false
						$.modifiers[#Skin].bone_Limit = 8
						deleteModifier $ $.modifiers["Skin_Wrap"]
					)*/
				)	
				delete copyNodes[1]
			) else (messagebox "Failed to Locate Noesis!")
		)
	)
	
	on BtnRemoveBoneNumbers pressed do (
		select selection[1]
		if not (classof $ == Editable_mesh and $.modifiers["Skin"] != undefined) then (
			messageBox "Select one (1) submesh with a Skin modifier"
			return false
		)
		with redraw off (
			local sourceMesh = $
			local skinBoneMapS = #()
			local sourceBones = collectSkinBones sourceMesh
			local bHasNumbers = false
			max modify mode
			theSkinS = sourceMesh.modifiers[#skin]
			if ( filterString (skinOps.GetBoneName theSkinS 1 0) ":")[2] != undefined then 
				bHasNumbers = true
			if bHasNumbers == true then ( --remove numbers
				for i = 1 to (skinOps.getnumberbones theSkinS) do (
					local boneName = skinOps.GetBoneName theSkinS i 0
					local bs = filterString boneName ":"
					if bs[2] == undefined then (bs[2] = getuserprop sourceBones[i] "Bone_Number")
					if bs[2] != undefined then (
						sourceBones[i].name = bs[2]
						append skinBoneMapS i
						if (getuserprop sourceBones[i] "Bone_Number") == undefined do setuserprop sourceBones[i] "Bone_Number" bs[1]
						if (getuserprop sourceBones[i] "Bone_Name") == undefined do setuserprop sourceBones[i] "Bone_Name" bs[2]
					)
				)
			) 
			else ( --restore numbers
				for b = 1 to (sourceBones.count) do (
					local BN = getuserprop sourceBones[b] "Bone_Number"
					local prop = getuserprop sourceBones[b] "Bone_Name"
					if prop != undefined then ( sourceBones[b].name = prop )
					if BN != undefined then ( sourceBones[b].name = BN + ":" + sourceBones[b].name)
				)
			)		
		)
	)
	
	on BtnSkinOnTop pressed do (
		local meshes = for obj in (selection as array) where (classof obj == Editable_mesh) collect obj 
		with redraw off (
			for msh in meshes do (
				if classof msh.modifiers[1] == Skin then continue
				local theSkinArray = for i = msh.modifiers.count to 1 by -1 where classof msh.modifiers[i] == Skin collect #(i, msh.modifiers[i])
				skinUtils.ExtractSkinData msh
				local skinData = (maxOps.getNodeByHandle objects[objects.count].inode.handle)
				select msh
				selectmore skinData
				for modifier in theSkinArray do deleteModifier msh (modifier[1]) --delete all collected modifiers by index
				for modifier in theSkinArray do addModifier msh modifier[2] --add back all collected instances on top of the stack
				skinUtils.ImportSkinDataNoDialog true false false false false 0.01 0
				delete skinData
			)
		)
	)
	
	on FldScale entered num do (
		ScaleValue = try(num as float)catch(1.0)
		FldScale.text = ScaleValue as string
	)
	
	on BtnSetScale pressed do (
		local object = $
		if superclassof object == GeometryClass and object.modifiers[#skin] != undefined then (
			local bones = collectSkinBones object
			while bones[1].parent != undefined do
				bones[1] = bones[1].parent
			object = bones[1]
		)
		if (superclassof object == Helper or classof object == BoneGeometry) then (
			with undo on (
				local bone = object
				while bone.parent != undefined do bone = bone.parent
				local delta = (matrix3 [1,0,0][0,0,-1][0,1,0][0,0,0])--inverse bone.transform
				if ScaleValue == 1 then
					bone.transform = (matrix3 [1,0,0] [0,0,1] [0,-1,0] bone.pos)
				else bone.transform *= delta * (matrix3 [ScaleValue,0,0] [0,0,ScaleValue] [0,-ScaleValue,0] [0,0,0]) -- 
			)
		) else 
			messagebox "Select the root bone"
	)
	
	on BtnSetScale rightclick do (
		if ScaleValue == 1.0 then ScaleValue = 0.393701
		else if ScaleValue == 0.393701 then ScaleValue = 2.54
		else if ScaleValue == 2.54 then ScaleValue = 1.0
		FldScale.text = ScaleValue as string
	)
	
	on BtnAnimToBlender pressed do (
		objSelected = selection as array
		cmd = getSaveFileName types:"FBX animation|*.fbx|All|*.*|"
		if cmd != undefined then (
			dummy = mesh vertices:#([0,0,0],[0,0,0],[0,0,0]) faces:#([1,2,3])
			selectmore dummy
			selectmore objselected
			dummy.name = "dummy"
			dummySkin = Skin()
			addModifier dummy dummySkin
			max modify mode
			modPanel.setCurrentObject dummySkin
			for obj in objSelected do (
				if superclassof obj == Helper or superclassof obj == BoneGeometry then 
					skinops.addBone dummySkin obj 0
			)
			if cmd != undefined and cmd != "" do (
				fbx_path = (getFilenamePath cmd) + (getFilenameFile (getFilenameFile cmd)) + "_(Max).fbx"
				if chk_showPlugOpt.checked then (--chk_expPrompt
					exportFile fbx_path selectedOnly:true
				) else (
					exportFile fbx_path #noPrompt selectedOnly:true
				)
				if doesFileExist fbx_path do (
					waitForFileUnlock(fbx_path)
					cmd = (
						"\"" + noesis_path + "\" ?cmode \"" + fbx_path + "\" \"" + cmd + "\"" + " -notex"  -- + (if chk_noesisOpt.checked then " -RPGOptimize" else "")
					)
					if chk_showCMD.checked then (
						DOSCommand ("\"" + cmd + "\"")
					)
					else (
						HiddenDOSCommand ("\"" + cmd + "\"") startpath:(getFilenamePath noesis_path) donotwait:false
					)
					
					format "%\n" cmd
					waitForFileUnlock(fbx_path)
					if chk_delFBX.checked do
						deleteFile fbx_path
				)	
			)
			if chk_delFBX.checked do
				delete dummy
		)
		select objSelected
	)
)
createdialog formNoesisCMD