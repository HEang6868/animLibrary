import maya.cmds as mc
import os
from pathlib import Path


# Save where this .py file is located.
SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
MAYAPATH = SCRIPTPATH.split("scripts")[0]
MODNAME = "animLibrary"


def onMayaDroppedPythonFile(*args):
    """
    Installs the script as a button when it's dragged into the Maya viewport
    """
    shelf_name = "Custom"  # Change to existing shelf name if you like.
    button_label = "Anim Pose Library"
    tooltip = "Launches the Anim Pose Library."
    icon_name = "AnimLibraryIcon.png"  # Your custom icon file name.

    # Find icon path (assumes icon is next to this .py file)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, icon_name)

    # Confirm shelf exists.
    if not mc.shelfLayout(shelf_name, exists=True):
        print(f"Shelf '{shelf_name}' not found. Please create it or change to an existing shelf (e.g., 'Polygons').")
        return

    install_module()

    #remove existing button with same label.
    children = mc.shelfLayout(shelf_name, query=True, childArray=True) or []
    for child in children:
        if mc.shelfButton(child, query=True, label=True) == button_label:
            mc.deleteUI(child)

    # Command that will run your tool when the button is clicked.
    cmd = 'import animLibrary.animLibraryUI as al; al.animLibrary()'

    # Add the button to the shelf.
    mc.shelfButton(
        label=button_label,
        parent=shelf_name,
        command=cmd,
        sourceType="Python",
        annotation=tooltip,
        image=icon_path 
        )

    mc.inViewMessage(amg=f"<hl>{button_label}</hl> added to <hl>{shelf_name}</hl> shelf!", pos='topCenter', fade=True)


def mod_file_write(filePath):
    """
    Writes the .mod file.
    """
    #Create a mod file.
    open(f"{filePath}/{MODNAME}.mod", "w")
    #Open the file with python for editting.
    modFile = open(file=f"{filePath}/{MODNAME}.mod", mode="w")
    #Write the information into the mod file.
    modFile.write(f"+ {MODNAME} 1.0 {MAYAPATH}\n{MAYAPATH}")


def install_module():
    """
    Installs the module that tells Maya where to find the script. 
    Creates the necessary files and folders if they do not exist.
    """
    mayaVersion = mc.about(version=True)   

    #Check if the Maya folder has a "module" folder.
    modPath = Path(fr"{MAYAPATH}{mayaVersion}\modules")
    if not os.path.exists(modPath):
        #Create it if it doesn't exist.
        print(f"{modPath} does not exist. Creating modules folder.")
        Path.mkdir(f"{modPath}")
    else:
        print(f"{modPath} exists. Creating .mod file.")
    #Check if a mod file already exists in the "module" folder.
    filePath = Path(f"{modPath}\{MODNAME}.mod")
    print(filePath)
    if filePath.is_file():
        print(f"{modPath}{MODNAME}.mod already exists!")
        #If it exists, create a popup asking if you'd like to overwrite the existing file.
        copyCheck = mc.confirmDialog(title="Module File Exists!",
                                    message=f"{MODNAME}.mod already exists at this location. \nDo you want to overwrite it?",
                                    button=["Replace file", "Cancel"],
                                    defaultButton="Replace file",
                                    cancelButton="Cancel"
                                    )
        if copyCheck ==  "Replace file":
            mod_file_write(modPath)
            print(f"{modPath}\{MODNAME}.mod overwritten.")
        else:
            print("Module installation cancelled.")
    else:
        mod_file_write(modPath)
        print(f"{modPath}\{MODNAME}.mod created!")
                
    #Load all module you have installed in Maya.
    mc.loadModule(allModules=True)
