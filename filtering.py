from PySide2 import QtCore, QtWidgets
from . import utils


# TODO Ajouter les checkboxed pour le combo list
class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)


# TODO Ajouter le model de la filter list contenant la liste des utilisateurs
class ListModel(QtCore.QAbstractListModel):
    def __init__(self):
        super(ListModel, self).__init__()
        self._data = ['test']

    def rowCount(self, parent=QtCore.QModelIndex):
        return len(self._data)

    def data(self, index=QtCore.QModelIndex, role=int):
        return self._data
