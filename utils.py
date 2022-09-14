import json
import os

path = "D:/Projets_Houdini/CopiedSetup/"
extension = '.uti'


def writeJson(data, nodeType, filePath):
    if not os.path.exists(filePath):
        with open(filePath, 'w') as file:
            newData = {nodeType: []}
            newData[nodeType].append(data)
            file.seek(0)
            json.dump(newData, file, indent=4)
    else:
        with open(filePath, 'r+') as file:
            newData = json.load(file)
            newData[nodeType].append(data)
            file.seek(0)
            json.dump(newData, file, indent=4)


def serialize(data):
    nodeType = data['type']
    jsonFilePath = f'{path}{nodeType}_nodes.json'

    writeJson(data, nodeType, jsonFilePath)




