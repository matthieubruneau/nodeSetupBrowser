from PySide2 import QtCore, QtWidgets, QtGui
from . import utils
import os


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
        data = utils.deserialize(utils.path)
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
                if list(data[category].values())[0] in [child.data(0) for child in parentNode.childItems]:
                    return
                rows = parentNode.childCount()
                dataNode = NodeItem(list(data[category].values()), parentNode)
                self.beginInsertRows(parentIndex, rows, rows)
                parentNode.appendChild(dataNode)
                self.endInsertRows()


    @QtCore.Slot(object)
    def removeData(self, node):
        nodedata = node.node
        row = nodedata.row()
        parent = nodedata.parent()
        self.beginRemoveRows(node.parent, row, row)
        parent.removeChild(nodedata)
        self.endRemoveRows()

        if parent.childCount() == 0:
            row = parent.row()
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            self.rootItem.removeChild(parent)
            self.endRemoveRows()
            os.remove(f"{utils.path}{parent.data(0)}_nodes.json")

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
        pattern = self.filterRegExp().pattern()
        model = self.sourceModel()
        sourceData = model.index(source_row, 1, source_parent).data()
        if pattern == '' or pattern == 'All':
            return True
        elif sourceData in pattern:
            return True
        else:
            return False
