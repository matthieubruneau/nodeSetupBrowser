import json
import os
import hou

path = "D:/Projets_Houdini/CopiedSetup/"
extension = '.uti'


def writeJson(newData, filePath):
    if os.path.exists(filePath):
        with open(filePath, 'r+') as file:
            data = json.load(file)
            tmpDict = list(newData.values())[0]
            nodeType = list(newData.keys())[0]
            name = tmpDict.pop('name')
            data['Categories'][nodeType][name] = tmpDict
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        with open(filePath, 'w') as file:
            tmpDict = list(newData.values())[0]
            nodeType = list(newData.keys())[0]
            name = tmpDict.pop('name')
            data = {'Categories': {nodeType: {name: tmpDict}}}
            file.seek(0)
            json.dump(data, file, indent=4)


def updateJson(newData, filePath):
    tmpData = newData['Categories']
    for key, value in tmpData.items():
        for subkey, subvalue in value.items():
            newData['Categories'][key][subkey] = dict(zip(['user', 'date', 'comment', 'Node Path'], subvalue))
    if os.path.exists(filePath):
        with open(filePath, 'w') as file:
            json.dump(newData, file, indent=4)


def serialize(data):
    nodeName = list(data.keys())[0]
    jsonFilePath = "{}{}_nodes.json".format(path, nodeName)
    writeJson(data, jsonFilePath)


def createData(file, data):
    with open(file, 'r') as f:
        nodeData = json.load(f)
    tmpData = nodeData['Categories']
    nodeType = list(tmpData.keys())[0]
    nodes = {k: list(v.values()) for k, v in tmpData[nodeType].items()}
    data['Categories'][nodeType] = nodes


def deserialize(filepath, allType=True):
    data = {'Categories': {}}
    if allType:
        files = ['{}{}'.format(filepath, file) for file in os.listdir(filepath) if '.json' in file]
        for file in files:
            createData(file, data)
    else:
        createData(filepath, data)
    return data


def getCurrentNetworkTab():
    network_tabs = [t for t in hou.ui.paneTabs() if t.type() == hou.paneTabType.NetworkEditor]
    if network_tabs:
        for tab in network_tabs:
            if tab.isCurrentTab():
                return tab
    return None

