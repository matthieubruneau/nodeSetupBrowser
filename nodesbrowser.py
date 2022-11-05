from PySide2 import QtWidgets, QtGui, QtCore
from . import utils
from collections import OrderedDict
from datetime import date
import os
import hou
import json


class Export(QtWidgets.QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(Export, self).__init__()

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()

        # Secondary layout
        self.layout = QtWidgets.QFormLayout()
        self.layout.setVerticalSpacing(10)
        self.nodeSetupName = QtWidgets.QLineEdit()
        self.layout.addRow(QtWidgets.QLabel("Node Setup Name:"), self.nodeSetupName)

        self.label = QtWidgets.QLabel()
        self.layout.addRow(QtWidgets.QLabel("Category:"), self.label)

        self.metadata = QtWidgets.QPlainTextEdit()
        self.layout.addRow(QtWidgets.QLabel("Comments:"), self.metadata)

        mainLayout.addLayout(self.layout)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Export Node")


class NodesBrowser(QtWidgets.QWidget):
    removeSignal = QtCore.Signal(object)

    def __init__(self):
        super(NodesBrowser, self).__init__()
        self.addNode = None
        self.newNodeData = None
        self.username = os.getlogin()

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

        # Main layout
        grid = QtWidgets.QGridLayout()

        # Filter QLine Edit
        self.filter = QtWidgets.QLineEdit('')

        # Create Tree View and Configure it
        self.treeView = QtWidgets.QTreeView()
        self.treeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # self.treeView.setHeaderHidden(True)

        self.model = utils.NodeModel()
        self.proxyModel = utils.ProxyModel(self, recursiveFilteringEnabled=True)
        self.proxyModel.setSourceModel(self.model)

        self.treeView.setModel(self.model)
        self.treeView.header().setDefaultAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.treeView.selectionModel().selectionChanged.connect(self.selectedNode)

        self.metadata = QtWidgets.QPlainTextEdit()
        # self.metadata.setReadOnly(True)
        # self.metadata.setFixedWidth(250)

        refresh = QtWidgets.QPushButton('Refresh Window')
        copy = QtWidgets.QPushButton('Export Node Selection')
        paste = QtWidgets.QPushButton('Import Node Setup')
        delete = QtWidgets.QPushButton('Delete Node Setup')

        # grid.addWidget(self.filter, 1, 1, 1, 3)
        grid.addWidget(self.treeView, 2, 1, 4, 4)
        # grid.addWidget(self.metadata, 2, 4, 2, 1)
        grid.addWidget(refresh, 6, 1, 1, 4)
        grid.addWidget(copy, 7, 1, 1, 1)
        grid.addWidget(paste, 7, 2, 1, 2)
        grid.addWidget(delete, 7, 4, 1, 1)

        mainLayout.addLayout(grid)

        copy.clicked.connect(self.addNodeWindow)
        paste.clicked.connect(self.importNode)
        delete.clicked.connect(self.removeData)
        refresh.clicked.connect(self.refreshWindow)
        self.filter.textChanged.connect(self.onFilterChanged)

        # Connect custom signals
        self.removeSignal.connect(self.model.removeData)

    @QtCore.Slot(str)
    def onFilterChanged(self, text):
        self.proxyModel.setFilterRegExp(text)
        # self.treeView.expandAll()

    @staticmethod
    def getCurrentNetworkTab():
        networkTabs = [t for t in hou.ui.paneTabs() if t.type() == hou.paneTabType.NetworkEditor]
        if networkTabs:
            for tab in networkTabs:
                if tab.isCurrentTab():
                    return tab

    def refreshWindow(self):
        self.model = utils.NodeModel()
        self.treeView.setModel(self.model)
        self.treeView.selectionModel().selectionChanged.connect(self.selectedNode)

    def exportNode(self, nodes, nodeData):
        # self.treeView.model().sourceModel().addNewData(nodeData)
        self.model.addNewData(nodeData)
        parentNode = nodes[0].parent()
        nodeType = list(nodeData.keys())[0]

        path = utils.path + nodeType + '/' + nodeData[nodeType]['name'] + utils.extension
        utils.serialize(nodeData)

        if not os.path.exists(utils.path + nodeType):
            os.makedirs(utils.path + nodeType)

        parentNode.saveItemsToFile(nodes, path)

    def addNodeWindow(self):
        self.addNode = Export()
        selectedNodes = hou.selectedNodes()
        tab = self.getCurrentNetworkTab()
        if selectedNodes:
            node = tab.currentNode()
            context = node.type().category().name() if node.type().category().name() != 'Object' else node.type().name()
            self.addNode.label.setText(context)
            if self.addNode.exec_():
                name = self.addNode.nodeSetupName.text()
                nodeType = self.addNode.label.text()
                self.newNodeData = {nodeType: OrderedDict([('name', name),
                                                           ('user', self.username),
                                                           ('date', date.today().strftime("%m/%d/%y")),
                                                           ('comment', self.addNode.metadata.toPlainText()),
                                                           ('Node Path',
                                                            utils.path + nodeType + '/' + name + utils.extension)])}

                self.exportNode(selectedNodes, self.newNodeData)


    def selectedNode(self, selected, deselected):
        index = selected.indexes()
        try:
            selectionData = index[0].data()
            parent = index[0].parent().data()
            if parent is not None and parent != 'Categories':
                data = utils.deserialize(utils.path)

                node = data['Categories'][parent][selectionData]
            #     text = "\n".join(["date: {}".format(node['date']), "user: {}".format(node['user']),
            #                       "description: {}".format(node['comment'])])
            #     self.metadata.setPlainText(text)
        except IndexError or KeyError:
            pass

    def importNode(self):
        selection = self.treeView.selectionModel().selectedIndexes()[0]
        selectionData = selection.data(0)
        parent = selection.parent().data(0)

        path = None
        if parent is not None:
            data = utils.deserialize(utils.path)
            path = data['Categories'][parent][selectionData][-1]
            tab = utils.getCurrentNetworkTab()
            parent = tab.pwd()
            parent.loadItemsFromFile(path)

    def removeData(self):
        if len(self.treeView.selectionModel().selectedIndexes()) != 0:
            selection = self.treeView.selectionModel().selectedIndexes()[0]
            selectionData = selection.data(0)
            parent = selection.parent().data(0)

            if parent is not None:
                jsonPath = f"{utils.path}{parent}_nodes.json"
                data = utils.deserialize(jsonPath, allType=False)
                nodePath = data['Categories'][parent][selectionData][-1]

                # nodes = self.proxyModel.mapToSource(selection).internalPointer()
                nodes = selection.internalPointer()
                node = utils.Node(nodes, selection.parent())

                # Update json
                del data['Categories'][parent][selectionData]
                utils.updateJson(data, jsonPath)

                self.removeSignal.emit(node)
                os.remove(nodePath)

                # Set metadata to empty
                self.metadata.setPlainText('')


