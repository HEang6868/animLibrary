import json
from os import path



def write_json_file(dirPath, fileName, data):
    """
    Writes and saves a json file.
    """
    fullPath = path.join(dirPath, f"{fileName}.json")
    with open(fullPath, "w") as file:
        json.dump(data, file, indent=4)
    print(f"{fileName}.json written to {dirPath}.")


def read_json_file(filePath)-> dict:
    """
    Reads a json file and returns its data.
    """
    with open(filePath) as dataFile:
        loadedData = json.load(dataFile)
        print(f"Read {filePath}. Returned: {loadedData}")
        return loadedData


