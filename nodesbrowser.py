import sys
import time
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from . import utils
import hou


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
    def __init__(self):
        super(NodesBrowser, self).__init__()
        self.addNode = None
        self.newNodeData = None

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

        # Main layout
        grid = QtWidgets.QGridLayout()
        self.treeView = QtWidgets.QTreeView()
        self.metadata = QtWidgets.QPlainTextEdit()
        self.metadata.setReadOnly(True)
        self.metadata.setPlainText('This is a test')
        self.metadata.setFixedWidth(250)

        copy = QtWidgets.QPushButton('Export Node Selection')
        paste = QtWidgets.QPushButton('Import Node Setup')
        delete = QtWidgets.QPushButton('Delete Node Setup')

        grid.addWidget(self.treeView, 1, 1, 4, 3)
        grid.addWidget(self.metadata, 1, 4, 2, 1)
        grid.addWidget(copy, 5, 1, 1, 1)
        grid.addWidget(paste, 5, 2, 1, 2)
        grid.addWidget(delete, 5, 4, 1, 1)

        mainLayout.addLayout(grid)

        copy.clicked.connect(self.addNodeWindow)

    @staticmethod
    def getCurrentNetworkTab():
        networkTabs = [t for t in hou.ui.paneTabs() if t.type() == hou.paneTabType.NetworkEditor]
        if networkTabs:
            for tab in networkTabs:
                if tab.isCurrentTab():
                    return tab

    def addNodeWindow(self):
        self.addNode = Export()
        selectedNodes = hou.selectedNodes()
        tab = self.getCurrentNetworkTab()
        if selectedNodes:
            node = tab.currentNode()
            context = node.type().category().name() if node.type().category().name() != 'Object' else node.type().name()
            self.addNode.label.setText(context)
            if self.addNode.exec_():
                self.newNodeData = {'name': self.addNode.nodeSetupName.text(), 'type': self.addNode.label.text(),
                                    'comment': self.addNode.metadata.toPlainText()}
                self.exportNode(selectedNodes, self.newNodeData)

    @staticmethod
    def exportNode(nodes, nodeData):
        parentNode = nodes[0].parent()
        path = utils.path + nodeData['name'] + utils.extension
        print(parentNode)
