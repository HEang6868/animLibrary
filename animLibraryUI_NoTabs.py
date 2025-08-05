import maya.cmds as mc
from pathlib import Path
import os
import shutil
import animLibrary.screenshotMod as ssm
import animLibrary.fileMod as fm
from animLibrary.screenshotMod import cam_screenshot
from animLibrary.fileMod import write_json_file, read_json_file

import imp
imp.reload(ssm)
imp.reload(fm)



class AnimLibrary():
    """
    Creates the window that contains the anim pose library.
    """
    def __init__(self):
        self.winName = "animLibrary"
        self.winSize = (560, 480)
        #Save the current project folder as a variable and use it to define some folders for the tool's files.
        self.projectFolder = mc.workspace(q=True, rootDirectory=True)
        self.posePath = f"{self.projectFolder}animPoses"
        self.thumbPath = f"{self.projectFolder}animPoses/thumbnails"
        self.suffixPick = True

        #Close the tool if it's already open.
        if mc.window(self.winName, exists=True):
            mc.deleteUI(self.winName)
        
        #Confirm or create the filePaths defined above.
        self.file_path_check(self.posePath)
        self.file_path_check(self.thumbPath)
        #Create the self.currentPose variable.
        self.currentPose = ""

        #Create the tool window!
        self.mainWindow = mc.window(self.winName, widthHeight=self.winSize, title="Anim Pose Library", menuBar=True)
        #######################################################################################################
        # fileMenu = mc.menu(label="File", parent=self.mainWindow)
        # mc.menuItem(label="Set Library Path", parent=fileMenu)

        #Create the layouts and controls.
        mainLayout = mc.formLayout(numberOfDivisions=100)
        poseScrollLayout = mc.scrollLayout(parent=mainLayout, childResizable=True, verticalScrollBarAlwaysVisible=True)
        poseLayout = mc.flowLayout(parent=poseScrollLayout, generalSpacing=5, columnSpacing=5, wrap=True, height=420, bgc=(.4, .4, .4))
        btnCol = mc.iconTextRadioCollection("PoseBtnCollection")

        ctrlLayout = mc.columnLayout(parent=mainLayout, adj=True, columnAlign="center", rowSpacing=10, margins=10)
        #Take a screenshot immediately to put in the thumbnail UI.
        cam_screenshot(self.thumbPath, imageName="TempImg.jpg", activeCamera=True)
        uiThumb = mc.image(parent=ctrlLayout, image=os.path.join(self.thumbPath, "TempImg.jpg"), height=120, width=100)
        self.GeoOnlyChkBox = mc.checkBox(label="Rig Geo Only", parent=ctrlLayout, value=True)

        thumbnailBtn = mc.button(label="Create Thumbnail", parent=ctrlLayout, command=lambda x:self.set_ui_thumbnail(uiThumb, self.thumbPath))
        self.selectionSaveChkBox = mc.checkBox(label="Save from Selection Only", parent=ctrlLayout, value=True)
        saveBtn = mc.button(label="Save Pose", parent=ctrlLayout, command=lambda x: self.lib_save_pose(poseLayout, self.posePath, btnCol))
        selCtrlsBtn = mc.button(label="Select Controls from Pose", parent=ctrlLayout, command=lambda x: self.select_pose_ctrls())
        self.selectionLoadChkBox = mc.checkBox(label="Load to Selection Only", parent=ctrlLayout, value=True)
        loadBtn = mc.button(label="Load Pose", parent=ctrlLayout, command=lambda x:self.lib_load_pose())
        selAllBtn = mc.button(label="Select ALL Rig Controls", parent=ctrlLayout, command=lambda x:self.select_rig_ctrls())
        #Create a popup menu for selAllBtn to switch how the tool finds a rig's controls.
        currentMenu = mc.popupMenu(parent=selAllBtn)
        mc.menuItem(parent=currentMenu, label="Select with Suffix", command=lambda x: self.suffixPickTrue())
        mc.menuItem(parent=currentMenu, label="Select All Curves", command=lambda x: self.suffixPickFalse())

        #testBtn = mc.button(label="TEST", parent=ctrlLayout, command=lambda x: self.geo_check(mc.ls(sl=True))) #print("test"))

        #Attach the pose and control layouts to the main formLayout
        mc.formLayout(mainLayout, e=True, attachForm=([poseScrollLayout, "left", 10], 
                                                      [poseScrollLayout, "top", 10],
                                                      [poseScrollLayout, "bottom", 10],
                                                      [ctrlLayout, "right", 10], 
                                                      [ctrlLayout, "top", 10],
                                                      [ctrlLayout, "bottom", 10]
                                                      ),
                                        attachPosition=([poseScrollLayout, "right", 0, 70]),
                                        attachControl=([ctrlLayout, "left", 0, poseScrollLayout])
                                                      )
        
        mc.showWindow()
        mc.window(self.winName, edit=True, widthHeight=self.winSize)
        #Populates the tool with any existing poses.
        self.load_all_btns(self.posePath, poseLayout, btnCol)
        #self.btn_process(poseLayout)
        

    ########################
    ###   UI FUNCTIONS   ###
    ########################

    def load_all_btns(self, filePath, layout, collection):
        """
        Lists the files in a directory and creates a button for each file it finds.
        """
        #Make of list of all of the files in the filePath, excluding any directories.
        ExistingPoseFiles = []
        for (dirPath, dirnames, fileNames) in os.walk(filePath):
            ExistingPoseFiles.extend(fileNames)
            #Break the for loop so it only looks in the first folder.
            break
        print(f"Loading poses from {filePath=}\n   Poses found: {ExistingPoseFiles}")
        for pf in ExistingPoseFiles:
            #Seperate the json filename from its extension.
            poseName = pf.split(".")[0]
            #print(f"{poseName=}")
            #Use the filename to find the matching thumbnail jpg.
            thumbName = poseName+".jpg"
            thumbPath = os.path.join(filePath, "thumbnails", thumbName)
            #Add a button to the layout using the info above. Set its command to print "Files Missing" in case btn_process can't find its matching file.
            newBtn = self.add_pic_btn(layout, poseName, thumbPath, print, collection)
            #print(f"{newBtn=}")
            mc.iconTextRadioButton(newBtn, e=True, onCommand=lambda x:print("Files Missing") )
            #Assign the button's command.
            self.set_btn_path(newBtn)
        

    # def btn_process(self, layout):
    #     """
    #     Goes through each button in the given layout and runs sets their onCommand to set the currentPose.
    #     """
    #     btnList = mc.flowLayout(layout, q=True, childArray=True)
    #     for btn in btnList:
    #         self.set_btn_path(btn)
    

    def set_btn_path(self, button):
        """
        Sets the command for the given button to call the correct pose file.
        ***Needs to be a seperate function or else the same pose is applied to every button.
        """
        btnName = mc.iconTextRadioButton(button, q=True, label=True)
        mc.iconTextRadioButton(button, e=True, onCommand=(lambda x: self.set_current_pose(self.posePath, btnName) ) )


    def file_name_dialog(self):
        """
        Opens a dialog that asks for a filename. 
        """
        #Opens a dialong that asks for a name.
        nameInput = mc.promptDialog(title="Name File", 
                                    message="What do you want to call this file?", 
                                    button=["Confirm", "Cancel"], 
                                    defaultButton="Confirm", 
                                    cancelButton="Cancel"
                                    )
        if nameInput == "Confirm":
            name = mc.promptDialog(q=True, text=True)
            if name == "":
                print("Operation cancelled. No name entered.")
                return False
            else:
                #Returns the name.
                return name
        else:
            print("Operation cancelled.")
            return False


    def overwrite_check(self, filePath)-> str:
        """
        Checks if a file already exists and creates a dialog to ask how to proceed.
        ->True = Proceed, False = Cancel
        """
        if os.path.exists(filePath):
            #Seperates a file from the rest of its filePath.
            fileName = filePath.split(r"\\")[-1]
            #Open a dialog asking if you want to overwrite the existing file or not.
            overwriteCheck = mc.confirmDialog(title="File Exists.", 
                                              message=f"{fileName} already exists in this location. How do you want to proceed?", 
                                              button=["Overwrite Existing File", "Cancel"], 
                                              defaultButton="Cancel", 
                                              cancelButton="Cancel"
                                              )
            if overwriteCheck == "Overwrite Existing File":
                return "Overwrite"
            else:
                print("Operation cancelled.")
                return "Cancel"
        else:
            return "Clear"


    def set_ui_thumbnail(self, control, filePath, name="TempImg.jpg"):
        """
        Takes a screenshot of Maya's current viewport and saves it to a file.
        Changes the image in an image control to the new file.
        """
        #Check if the "Geo Only" checkbox is checked.
        getGeoChkBox = mc.checkBox(self.GeoOnlyChkBox, q=True, value=True)
        #Save selected objects.
        selObjs = mc.ls(sl=True)
        if getGeoChkBox:
            #Select the selected rig's geometry.
            geo = self.select_rig_geo()
            print(f"{geo=}")
            #Take a screenshot with only the rig's geometry visible.
            cam_screenshot(filePath, selObj=False, geoOnly=geo ,imageName=name, activeCamera=True, currentBG=False)
        else:
            #Clear the selection.
            mc.select(clear=True)
            #Take a screenshot without altering the viewport.
            cam_screenshot(filePath, selObj=False, imageName=name, activeCamera=True, currentBG=False)
        #Re-select the selected objects.
        mc.select(selObjs)
        #Find the new screenshot.
        newThumbnail = os.path.join(filePath, name)
        #print(f"{newThumbnail=}")
        #Sets the screenshot as the image in the image control.
        mc.image(control, e=True, image=newThumbnail)


    def select_rig_geo(self)-> list:
        """
        Selects the geometry of the selected rig.
        """
        #Gets the last selected object.
        selObj = mc.ls(sl=True)[0]
        #print(selObj)
        #Gets its namespace
        nameSpace = selObj.split(":")[0]
        #Gets all visible dagObjects in the same namespace.
        rigAll = mc.ls(f"{nameSpace}:*", dagObjects=True, visible=True, objectsOnly=True, type="transform")
        #print(rigAll)
        rigMesh = []
        #Checks the shape node of each listed dagObject and adds it to a list.
        for obj in rigAll:
            shape = mc.listRelatives(obj, shapes=True, fullPath=True)
            if shape:
                for s in shape:
                    #print(mc.objectType(s))
                    if mc.objectType(s, isType="mesh"):
                        rigMesh.append(s)
                    else:
                        pass
            else:
                pass
        #print(rigMesh)
        #mc.select(rigMesh)
        return rigMesh
        

    def set_current_pose(self, dirPath, fileName):
        """
        Sets which pose json file is to be loaded.
        """
        self.currentPose = os.path.join(dirPath, f"{fileName}.json")
        print(self.currentPose)
        return self.currentPose


    def add_pic_btn(self, layout, label, imgFilePath, command, *args):
        """
        Adds a button to a layout with a picture in it.
        """
        #Creates an iconTextRadioButton
        newIconBtn = mc.iconTextRadioButton(label=label, parent=layout, collection=args[0], image=imgFilePath, onCommand=command,
                                            style="iconAndTextVertical",
                                            height=120, width=100
                                            )
        #Saves the flowLayout's height.
        layoutHeight = mc.flowLayout(layout, q=True, height=True)
        #Increases the layout's height.
        mc.flowLayout(layout, e=True, height=int(layoutHeight)+126)
        #Adds a popupMenu to the button that appears when the button is right clicked.
        self.poseBtn_popup_menu(newIconBtn, layout)
        return newIconBtn
        

    def poseBtn_popup_menu(self, button, layout):
        """
        Creates a popup menu for a given pose button.
        """
        currentMenu = mc.popupMenu(parent=button)
        mc.menuItem(parent=currentMenu, label="Rename pose", command=lambda x: self.rename_pose_btn(button, layout))
        mc.menuItem(parent=currentMenu, label="Replace Thumbnail", command=lambda x:self.replace_thumbnail(button))
        mc.menuItem(parent=currentMenu, label="Delete pose", command=lambda x: self.delete_pose_btn(button, layout))
    
    
    def rename_pose_btn(self, button, layout):
        """
        Opens a prompt dialog that allows the user to rename a pose button along with its thumbnail and json files.
        """
        #Get the button's label and connected thumbail and json file.
        poseName = mc.iconTextRadioButton(button, q=True, label=True)
        thumbFile = os.path.join(self.thumbPath, f"{poseName}.jpg")
        poseFile = os.path.join(self.posePath, f"{poseName}.json")
        #Open a dialog that asks for a new name.
        nameInput = mc.promptDialog(title="Rename Pose", 
                                    message=f"What would you like to change this pose's name to?", 
                                    button=["Confirm", "Cancel"], 
                                    defaultButton="Confirm", 
                                    cancelButton="Cancel"
                                    )
        if nameInput == "Confirm":
            #Get the new name from the dialog.
            newName = mc.promptDialog(q=True, text=True)
            if newName == "":
                return print("Rename cancelled.")
            else:
                newThumb = os.path.join(self.thumbPath, f"{newName}.jpg")
                newFile = os.path.join(self.posePath, f"{newName}.json")
                #Check if the json file with this name already exists.
                overwriteCheck = self.overwrite_check(newFile)
                if overwriteCheck == "Overwrite":
                    #Delete the existing json file.
                    os.remove(newFile)
                    #Search for and delete the matching thumbnail.
                    if os.path.isfile(newThumb):
                        os.remove(newThumb)
                    #Find the existing button that shares a name with the input name and delete it.
                    oldBtn = self.find_button_by_label(layout, newName)
                    self.delete_pose_btn(oldBtn, layout, confirmCheck=False)
                elif overwriteCheck == "Cancel":
                    return
            #Change the button's label to the new name and change its command to match.
            mc.iconTextRadioButton(button, e=True, label=newName, onCommand=lambda x:self.set_current_pose(self.posePath, newName))
            #Check for the matching thumbnail and rename it.
            if os.path.isfile(thumbFile):                        
                os.rename(thumbFile, newThumb)
            #Check for the matching json and rename it.
            if os.path.isfile(poseFile):                        
                os.rename(poseFile, newFile)


    def replace_thumbnail(self, button):
        """
        Switches the thumbnail on an iconTextRadioButton and deletes the previous file.
        """
        buttonName = mc.iconTextRadioButton(button, q=True, label=True)
        confirm = mc.confirmDialog(title="Are You Sure?", 
                                    message=f"Are you sure you want to replace \n{buttonName}'s thumbnail image?", 
                                    button=["Confirm", "Cancel"], 
                                    defaultButton="Confirm", 
                                    cancelButton="Cancel"
                                    )
        if confirm == "Confirm":
            imgPath = os.path.join(self.thumbPath, "TempImg.jpg")
            newPath = os.path.join(self.thumbPath, f"{buttonName}.jpg")
            shutil.copy(imgPath, newPath)
            mc.iconTextRadioButton(button, e=True, image=newPath)
        else:
            print("Thumbnail replacement cancelled.")


    def delete_pose_btn(self, button, layout, confirmCheck=True):
        """
        Deletes a pose button from the UI along with its thumbnail and json file. 
        """
        #Get the button's label and connected thumbail and json file.
        poseName = mc.iconTextRadioButton(button, q=True, label=True)
        thumbFile = os.path.join(self.thumbPath, f"{poseName}.jpg")
        poseFile = os.path.join(self.posePath, f"{poseName}.json")
        if confirmCheck:
            #Open a dialog menu that asks for confirmation.
            confirm = mc.confirmDialog(title="Are You Sure?", 
                                        message=f"Are you sure you want to delete {poseName}?", 
                                        button=["Confirm", "Cancel"], 
                                        defaultButton="Confirm", 
                                        cancelButton="Cancel"
                                        )
        else:
            confirm="Confirm"
        if confirm == "Confirm":
            #Check for the thumbnail and delete it.
            if os.path.isfile(thumbFile):
                os.remove(thumbFile)
            #Check for the json file and delete it.
            if os.path.isfile(poseFile):
                os.remove(poseFile)
            #Delete the button.
            mc.deleteUI(button, control=True)
             #Saves the flowLayout's height.
            layoutHeight = mc.flowLayout(layout, q=True, height=True)
            #Increases the layout's height.
            mc.flowLayout(layout, e=True, height=int(layoutHeight)-126)
        else:
            print("Pose deletion cancelled.")


    def find_button_by_label(self, layout, label) -> str:
        """
        Searches a UI for a button with a given label and return it.
        """
        allBtns = mc.flowLayout(layout, q=True, childArray=True)
        #print(f"{allBtns=}")
        if allBtns:
            for btn in allBtns:
                labelCheck = mc.iconTextRadioButton(btn, q=True, label=True)
                if labelCheck == label:
                    return btn
                else:
                    pass
            

    ##########################
    ###   POSE FUNCTIONS   ###
    ##########################
    def ctrl_check(self, obj) -> bool:
        """
        Checks if the given object is a nurbsCurve.
        """
        #Get the object's shape node and check if it's a nurbsCurve.
        shape = mc.listRelatives(obj, shapes=True, fullPath=True)
        #print(f"{shape=}")
        #Return the result.
        if shape:
            for s in shape:
                if mc.objectType(s, isType="nurbsCurve"):
                    #print("yah")
                    return True
                else:
                    #print("no")
                    return False
        else:
            #print("NO")
            return False


    def lib_save_pose(self, layout, dirPath, *args): 
        """
        Function that runs when "Save Pose" button is pressed.
        """
        #Check that at least one control is selected.
        selObjs = mc.ls(sl=True)
        if len(selObjs) < 1:
            return print("Select at least one control to save.")
        #Opens a dialog to ask for a name.
        nameInput = self.file_name_dialog()
        if nameInput:
            #Create the filepaths and file names for the json file and thumbnail jpg.
            tempImgFile = os.path.join(dirPath, "thumbnails", "TempImg.jpg")
            ImgFile = os.path.join(dirPath, "thumbnails", f"{nameInput}.jpg")
            #Check if the files exist already.
            if self.overwrite_check(ImgFile) == "Overwrite":
                #Check if the button already exists.
                btnCheck = self.find_button_by_label(layout, nameInput)
                if btnCheck:
                    self.delete_pose_btn(btnCheck, layout, confirmCheck=False)
            #Copy the TempImg and rename it to the given name.
            shutil.copy(tempImgFile, ImgFile)
            #Add a button to the UI.
            self.add_pic_btn(layout, nameInput, ImgFile, lambda x:self.set_current_pose(dirPath, nameInput), args[0])
            #Save the selected controls' attribute data in a json file.
            self.write_pose_file(dirPath, nameInput)      


    def lib_load_pose(self): 
        """
        Loads the current pose and applies it to selected objects.
        """
        #Get the currentPose.
        filePath = self.currentPose
        selObj = mc.ls(sl=True)
        if filePath == "":
            print("No pose was selected!")
        if len(selObj) < 1:
            return print("No controls were selected!")
        else:
            #Check the UI if "Load to Selection Only" checkbox is checked.
            getSelOnlyCheck = mc.checkBox(self.selectionLoadChkBox, q=True, value=True)
            if getSelOnlyCheck:
                pass
            else:
                #Select all contorls in the rig.
                self.select_pose_ctrls()
            selList = mc.ls(sl=True)
            #List selected controls.
            selList = mc.ls(sl=True)
            for obj in selList:
                #Seperate the object's name from its namespace.
                object = obj.split(":")[-1]
                #Read the json file and apply its values to any selected controls that are in it.
                poseData = self.read_pose_file(filePath)
                #print(f"2 {poseData=}\n {object=}")
                attributes = poseData.get(object)
                print(f"{attributes=}")
                if attributes:
                    for attr in attributes:
                        value = poseData[object].get(attr)
                        #print(f"{obj}.{attr} = {value}")
                        try:
                            mc.setAttr(f"{obj}.{attr}", value)
                        except RuntimeError:
                            print(f"{obj}.{attr} could not be altered and was skipped.")


    def select_pose_ctrls(self):
        """
        Select all involved controls in the self.currentPose file.
        """
        #Make sure a pose is selected.
        if self.currentPose == "":
            print("No pose was selected.")
        #Make sure a control is selected.
        selObj = mc.ls(sl=True)
        if len(selObj) > 0:
            #Get the control's namespace.
            nameSpace = selObj[0].split(":")[0]
        else:
            return print("Nothing selected. Select one control on the rig you wish to affect.")
        #Read the pose's json file to get its controls.
        poseData = read_json_file(self.currentPose)
        objectList = poseData.keys()
        objList = []
        for obj in objectList:
            #Put the controls in the json file into a list.
            objList.append(nameSpace+":"+obj)
        #print(f"{objList=}")
        #Clear the current selection.
        mc.select(clear=True)
        #Seperate objList into objects that can be found and objects that can't.
        skippedList = [obj for obj in objList if not mc.objExists(obj)]
        objList = [obj for obj in objList if mc.objExists(obj)]
        #Select all existing objects from objList and print the results.
        mc.select(objList)
        print(f"Pose controls selected: {objList}")
        if len(skippedList) > 0:
            print(f"{skippedList} not found. Selection skipped.")

    
    def suffixPickFalse(self):
        """
        Sets the self.suffixPick to False.
        """
        self.suffixPick = False
        print("'Select ALL Rig Controls' will select all curves in the rig.")
    
    def suffixPickTrue(self):
        """
        Sets the self.suffixPick to True.
        """
        self.suffixPick = True
        print("'Select ALL Rig Controls' will select controls based on suffix.")


    def select_rig_ctrls(self):
        """
        Select all controls in a rig, from one selected control.
        Uses different methods based on self.suffixPick variable.
        """
        selObj = mc.ls(sl=True)[0]
        ns, obj = selObj.split(":")[0], selObj.split(":")[-1]
        if self.suffixPick:
            ctrlSuffixes = ["ctrl", "ctl"]
            suffix = obj.split("_")[-1]
            if suffix.lower() not in ctrlSuffixes:
                mc.inViewMessage(assistMessage="WARNING: Control suffix may not work with tool. Consider switching tool's selection method. ", fade=True, position="midCenter") 
            rigCtrls = mc.ls(f"{ns}:*{suffix}")
        else:
            wholeRig = mc.ls(f"{ns}:*")
            rigCtrls = [x for x in wholeRig if self.ctrl_check(x)]
        mc.select(rigCtrls)
        print(f"Selected controls: {rigCtrls}")

    
    # def sort_btns(self, layout):
    #     """
    #     WiP function that reorders buttons in the layout.
    #     """
    #     children = mc.layout(layout, q=True, childArray=True)
    #     print(children)


    ##########################
    ###   FILE FUNCTIONS   ###
    ##########################

    def file_path_check(self, filePath):
        """
        Checks for a filePath and creates it if it doesn't exist.
        """
        if not os.path.exists(filePath):
            print(f"Could not locate directory. Creating {filePath}.")
            Path.mkdir(fr"{filePath}")
        else:
            print(f"Confirmed directory: {filePath}.")


    def get_ctrl_attrs_data(self, obj)-> dict:
        """
        Collects an object's keyable attributes and their values into a dictionary {object:{attribute:value, attribute:value, etc}}
        """
        attrDict = {}
        attrs = mc.listAnimatable(obj)
        #print(f"{obj=} {attrs=}")
        if attrs is not None:
            #print("attrs is not None")
            for a in attrs:
                #Replaces "|" with ":" in case namespaces are seperated by "|" instead of ":"
                a = a.replace("|", ":")
                #Breakdown each object into its namespace, object, attribute, and value.
                namespace, attr = a.split(":")[0], a.split(":")[-1]
                if namespace == "":
                    namespace = a.split(":")[1]
                #print(a.split(":"))
                object, attribute = attr.split(".")
                #print(f"{namespace=} {attr=} {object=} {attribute=}")
                value = mc.getAttr(f"{namespace}:{attr}")
                #Add the attribute as a keyword and its value as a value to a dictionary.
                attrDict[attribute] = value
            #Create a dictionary with the object(removed from its namespace) as a keyword and the attrDict as its value.
            objDict = {object:attrDict}
            #print(f"{objDict=}")
            return objDict
        elif attrs is None:
            #print("attrs is NONE")
            pass



    def write_pose_file(self, dirPath, fileName):
        """
        Runs get_ctrl_attrs_data() for each selected object and compiles the data into a json file.
        -> Saves a .json file.
        """
        #Check the UI if "Save from Selection Only" checkbox is checked.
        getSelOnlyCheck = mc.checkBox(self.selectionSaveChkBox, q=True, value=True)
        if getSelOnlyCheck:
            pass
        else:
            #Select all contorls in the rig.
            selList = self.select_rig_ctrls()
        selList = mc.ls(sl=True)
        objList = []
        for obj in selList:
            #Isolate only selected nurbsCurves into a list.
            if self.ctrl_check(obj):
                objList.append(obj)
        print(f"Saving data for: {objList}")
        #Build a dictionary of attribute data for all selected controls.
        data = {}
        #print(f"{objList=}")
        for obj in objList:
            #print(f"{obj=}")
            objData = self.get_ctrl_attrs_data(obj)
            if objData:
                data.update(objData)
        #{object:{attribute:value, attribute:value, etc}, object:{attribute:value, attribute:value, etc}, etc}
        write_json_file(dirPath, fileName, data)
    

    def read_pose_file(self, filePath): 
        """
        Reads and prints the contents of a pose json file.
        """
        #Read the json file.
        poseData = read_json_file(filePath)
        return poseData



AnimLibrary()