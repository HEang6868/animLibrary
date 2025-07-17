import maya.cmds as mc
import json
from os import path


class CtrlAttrSaver():
    """
    Creates a window with buttons that can export a selected object's keyable attributes to a json file.
    """
    def __init__(self):
        self.winName  = "CtrlSaver"
        self.winSize = (400, 300)
        self.suffix = "_CTL"

        self.filePath = "C:/Users/phyre/Documents/maya/projects/TECA6500_AdvancedScripting/animPoses"

        if mc.window(self.winName, exists=True):
            mc.deleteUI(self.winName)
        
        mainWindow = mc.window(self.winName, widthHeight=self.winSize, title="Control Saver")

        mainLayout = mc.columnLayout(adjustableColumn=True)
        mc.button(label="Save Control Data", parent=mainLayout, command=lambda x: dataBtnFunc(self.filePath, "Test"))


        mc.showWindow()



def dataGet(obj)-> dict:
    """
    Collects an object's keyable attributes and their values into a dictionary {object:{attribute:value, attribute:value, etc}}
    """
    attrDict = {}
    attrs = mc.listAnimatable(obj)
    for a in attrs:
        #Breakdown each object into its namespace, object, attribute, and value.
        ns, a = a.split(":")[0][1:], a.split(":")[-1]
        object, attribute = a.split(".")
        value = mc.getAttr(f"{ns}:{a}")
        #Add the attribute as a keyword and its value as a value to a dictionary.
        attrDict[attribute] = value
    #Create a dictionary with the object(removed from its namespace) as a keyword and the attrDict as its value.
    objDict = {object:attrDict}
    #print(f"{objDict=}")
    return objDict



def writeFile(filePath, fileName, data):
    """
    Writes and saves a json file.
    """
    fullPath = path.join(filePath, f"{fileName}.json")

    with open(fullPath, "w") as file:
        json.dump(data, file, indent=4)


def dataBtnFunc(filePath, fileName):
        """
        Runs dataGet() for each selected object.
        """
        objList = mc.ls(sl=True)
        print(f"Saving data for: {objList}")
        dataList = []
        for obj in objList:
            dataList.append(dataGet(obj))
        finalDict = {fileName: dataList} #{fileName:{object:{attribute:value, attribute:value, etc} } }
        
        writeFile(filePath, fileName, finalDict)



CtrlAttrSaver()