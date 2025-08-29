This is an animation pose library for Maya 2025.

    It's built for animators to save all keyable attributes on either just the selected controls, or for all controls on a selected rig. 
This tool is built to work with referenced rigs and requires that they have namespaces in order to work.
The poses you save can be saved to individual tabs which will also sort their files into folders.

Known issues: 
- Deleting a tab after you've deleted the folder will freeze Maya and require a restart.
- Closing tabs is currently broken.


INSTALLATION:
- Save the folder this file is in to your maya/scripts directory and load this folder as a module.
- Open animLibraryUI.py in Maya's script editor.
- Press 'ctrl + a' to select all of the contents in the script editor, then middle-click and drag from the script editor to your desired Maya shelf to create a button.


SETTINGS:
Tab Options:
> Add Tab: Opens a dialog that lets you name and create a new tab. This will also create a folder wheree any poses and thumbnails ypu save to it will go.
> Load Tab: Opens a file dialog that lets you open a new tab from an existing folder.
> Rename Tab: Lets you rename a tab which also renames its matching folder.
> Delete Current Pose Folder: Deletes the folder containing all of the pose data and thumbnails in the currently selected tab. !!!WARNING: Deleting the tab after 
                                you've deleted the folder will freeze Maya and require a restart!!!

'Select All' Settings:
> Select with Suffix: When selecting all of a rig's controls, the tool will search using the suffix of the selected control.
> Select All Curves: When selecting all of a rig's controls, the tool will select all curves with the same namespace.

If you right click on a pose, you will also have access to these options:
> Rename Pose: Opens a dialog that lets you rename the selected pose.
> Replace Thumbnail: Trades the selected pose's thumbnail image for the window's last screenshot.
> Delete Pose: Deletes the selected pose button from the tool and its matching file and thumbnail from the folders.


HOW TO USE:
    Upon running it for the first time the animLibrary will create a folder in your Maya project to hold the folders, data, and thumbnails that you save with it.
The basics of using this tool are to pose a rig however you want it saved and then to use the tool to save its pose in a library for use later. Using the buttons 
and settings on the tool allow you to affect either specific controls or every part of the selected rig.

The options and buttons on the right side of the tool work as follows:
Rig Geo Only: This checkbox sets what the toold will see when it takes a screenshot. While it is checked, thumbnails will only display the selected rig's geometry. 
                This means you must have at least one control selected on a rig for the tool to take a screenshot. If the box is unchecked, it will display everything 
                currently visible in the viewport.

Create Thumbnail: Takes a screenshot with the current active viewport and displays what it saved above.

Save from Selection Only: This checkbox sets whether the "Save Pose" button only saves data from  the controls you have selected or for the entire rig.

Save Pose: Opens a dialogue box that will ask you for a file name. Upon entering and confirming one, the thumbnail and file are saved and a button is created in the 
            left panel.

Select Controls from Pose: This button will look at whichever pose you currently have selected in the tool, and will attempt to select the matching controls on the rig 
                            you currently have selected.

Select ALL Rig Controls: This button expands your selection to every control on the selected rig. The method it uses to find the rig's controls depends on which 
                            option is selected in the 'Select All' Settings menu.

Load to Selection Only: This checkbox sets how the tool will load the selected pose. If it is checked, it only load pose data on to the contorls that you currenlty 
                        have selected. If it isn't checked, the tool will load as much of the pose as it can on to the selected rig.

Load Pose: This button gets the pose data from the selected pose in the tool and applies it to the rig based on the above checkbox and the file that's selected.