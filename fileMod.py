import json
from os import path
from pathlib import Path


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


def file_path_check(filePath):
        """
        Checks for a filePath and creates it if it doesn't exist.
        """
        if not path.exists(filePath):
            print(f"Could not locate directory. Creating {filePath}.")
            Path.mkdir(fr"{filePath}")
        else:
            print(f"Confirmed directory: {filePath}.")