import maya.cmds as mc
from os import path


def viewport_screenshot(filePath, name)-> str:
    """
    Takes a screenshot of Maya's current viewport and saves it to a file in a given filePath.
    -> Saves a .jpg
    """
    mc.refresh(currentView=True, fileExtension="jpg", filename=path.join(filePath, name))
    print(f"{name}.jpg saved at {filePath}.")    
    return path.join(filePath, name)


def cam_screenshot(filePath, selObj=False, imageName='.jpg', activeCamera=False, currentBG=False):
    """
    Creates a camera to take a screenshot with specific dimensions.
    Has options to focus on and isolate selected objects, use the current camera, and change the background.
    -> Saves a .jpg
    """
    #Put together the filePath and fileName and make sure the filename has the right suffix.
    pathName = path.join(filePath, imageName)
    if not pathName.endswith('.jpg'):
        pathName += '.jpg'

    if selObj != False:
        # Duplicate and group the selected objects to create a bounding box that can be used to position the camera.
        select_dup = mc.duplicate(selObj)
        temp_grp = mc.group(select_dup, name='screenShot_TEMP_GRP')

        # get the bounding box for the selection
        bbox = mc.exactWorldBoundingBox(temp_grp)
        # set size of each axis (X, Y, Z)
        size_x = bbox[3] - bbox[0]
        size_y = bbox[4] - bbox[1]
        size_z = bbox[5] - bbox[2]
        # set the max size from all three axis
        max_size = max(size_x, size_y, size_z)
        # set how far the camera will be placed from the selection
        cam_distance = max_size*1.15
    else:
        temp_grp = False

    #Create a default/temporary camera
    if not activeCamera:
        # Position it in X, Y, Z with the object's max size * 1.25
        shapeCam = mc.camera(name='shapeCam_TEMP', position=(cam_distance,cam_distance,cam_distance), 
                                                    rotation=(-36.5,45,0), focalLength=55, o=False)[0]
        #Look through the temporary camera.
        mc.lookThru(shapeCam)

    if not currentBG:
        #Saves the current background colours so they can be reset.
        ogBackground = mc.displayRGBColor('background', query=True)
        ogBackgroundTop = mc.displayRGBColor('backgroundTop', query=True)
        ogBackgroundBot = mc.displayRGBColor('backgroundBottom', query=True)
        #Sets the background to light grey.
        # mc.displayRGBColor( 'background', 0.403922, 0.403922, 0.403922 )
        # mc.displayRGBColor( 'backgroundTop', 0.403922, 0.403922, 0.403922 )
        # mc.displayRGBColor( 'backgroundBottom', 0.403922, 0.403922, 0.403922 )
        #Sets the background to a gradient.
        mc.displayRGBColor( 'background', 0.5309999823570251, 0.5309999823570251, 0.6309999823570251 )
        mc.displayRGBColor( 'backgroundTop', 0.5350000262260437, 0.6169999837875366, 0.6520000219345093 )
        mc.displayRGBColor( 'backgroundBottom', 0.2, 0.2, 0.3 )

    #Get the current active viewport panel
    current_panel = mc.paneLayout('viewPanes', query=True, pane1=True) 
    #Get the current frame
    currentFrame = mc.currentTime(query=True)
    #Hide every heads up display widget
    mc.modelEditor(current_panel, edit=True, hud=False)
    #Turn off the grid.
    mc.grid(toggle=False)
    if temp_grp:
        # view only the selected objects
        mc.select(temp_grp)
        mc.isolateSelect(current_panel, state=True)
        mc.isolateSelect(current_panel, addSelected=True)
        # hide all the objects
        # toggle visible only NURBSCurves and CVs
        mc.modelEditor(current_panel, edit=True, allObjects=False)
        mc.modelEditor(current_panel, edit=True, nurbsCurves=True, controlVertices=True)

    #Enable anti-aliasing in the viewport
    mc.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
    #Save a 1 frame playblast as a jpg.
    mc.playblast(startTime=currentFrame, endTime=currentFrame+1, completeFilename=pathName, format="image", compression="jpg", viewer=False, widthHeight=(256,256))

    #Set everything back to default 
    mc.modelEditor(current_panel, edit=True, allObjects=True)
    mc.modelEditor(current_panel, edit=True, hud=True)
    mc.grid(toggle=True)
    if temp_grp:
        mc.isolateSelect(current_panel, state=False)
        mc.delete(temp_grp)

    if not activeCamera:
        #Remove the temporary camera and reset which camera the viewport is in.
        mc.delete(shapeCam)
        mc.lookThru('persp')
    
    if not currentBG:
        #Reset the background colours.
        mc.displayRGBColor('background', ogBackground[0], 
                                        ogBackground[1], 
                                        ogBackground[2]
                                        )
        mc.displayRGBColor('backgroundTop', ogBackgroundTop[0], 
                                        ogBackgroundTop[1], 
                                        ogBackgroundTop[2]
                                        ) 
        mc.displayRGBColor('backgroundBottom', ogBackgroundBot[0], 
                                        ogBackgroundBot[1], 
                                        ogBackgroundBot[2]
                                        )