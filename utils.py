import json
import uuid
from PySide2 import QtCore, QtWidgets, QtGui
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


class Headers(QtWidgets.QHeaderView):
    def __init__(self, orientation):
        super(Headers, self).__init__(orientation)
        self.setStretchLastSection(True)

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            print('Left clicked')


class Node(object):
    def __init__(self, nodes, parent):
        self.node = nodes
        self.parent = parent


class NodeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def removeChild(self, item):
        self.childItems.remove(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 4

    def data(self, column):
        if isinstance(self.itemData, list):
            return self.itemData[column]
        elif column == 0:
            return self.itemData
        return ''

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

    def column(self):
        return 0


class Node(object):
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent


class NodeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(NodeModel, self).__init__(parent)
        tmpNode = NodeItem("")
        self.rootItem = NodeItem("Root", tmpNode)
        data = deserialize(path)
        self.setupModelData(self.rootItem, data['Categories'])
        self.columnsHeader = ['', 'User', 'Date', 'Description']

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter

        if role != QtCore.Qt.DisplayRole:
            return None

        if role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(100, 2000)

        item = index.internalPointer()

        return item.data(index.column())


    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def headerData(self, section, orientation, role=QtCore.Qt.Horizontal):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.columnsHeader[section]

        # Set default header data
        # return super(NodeModel, self).headerData(section, orientation, role)

    def addNewData(self, data):
        children = [child.data(0) for child in self.rootItem.childItems]
        category = list(data.keys())[0]
        node = None
        rows = self.rootItem.childCount()

        if category not in children:
            node = NodeItem(category, self.rootItem)
            nodeExport = NodeItem(list(data[category].values()), node)
            self.beginInsertRows(QtCore.QModelIndex(), rows, rows)
            self.rootItem.appendChild(node)
            node.appendChild(nodeExport)
            self.endInsertRows()
        else:
            nodeType = list(data.keys())[0]
            parent = self.match(self.index(0, 0, QtCore.QModelIndex()), 0, nodeType, 1)
            if len(parent) != 0:
                parentIndex = parent[0]
                parentNode = parentIndex.internalPointer()
                rows = parentNode.childCount()
                dataNode = NodeItem(list(data[category].values()), parentNode)
                self.beginInsertRows(parentIndex, rows, rows)
                parentNode.appendChild(dataNode)
                self.endInsertRows()

    @QtCore.Slot(object)
    def removeData(self, node):
        nodedata = node.node
        # nodeIndex = self.index(nodedata.row(), 0, QtCore.QModelIndex())
        row = nodedata.row()
        parent = nodedata.parent()
        self.beginRemoveRows(node.parent, row, row)
        parent.removeChild(nodedata)
        self.endRemoveRows()
        if parent.childCount() == 0:
            self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
            self.rootItem.removeChild(parent)
            self.endRemoveRows()
            os.remove(f"{path}{parent.data(0)}_nodes.json")

    def setupModelData(self, parent, d):
        for key, value in d.items():
            node = NodeItem(key, parent)
            if isinstance(value, dict):
                parent.appendChild(node)
                self.setupModelData(node, value)
            elif isinstance(value, list):
                value.insert(0, key)
                node = NodeItem(value, parent)
                parent.appendChild(node)
            else:
                pass


class ProxyModel(QtCore.QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        # user = ''
        # widget = self.parent()
        # model = self.sourceModel()
        # sourceData = model.index(source_row, 0, source_parent).data()
        # sourceParent = source_parent.data()
        #
        # if sourceParent is not None:
        #     data = deserialize(path)

        return True

