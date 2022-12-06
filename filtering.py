from PySide2 import QtCore, QtWidgets, QtGui
from . import utils


# TODO Ajouter les checkboxed pour le combo list
class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)


class ListModel(QtCore.QAbstractListModel):
    def __init__(self):
        super(ListModel, self).__init__()
        data = utils.deserialize(utils.path)
        self._data = self.initData(data['Categories'])

    def rowCount(self, parent=QtCore.QModelIndex):
        return len(self._data)

    def data(self, index=QtCore.QModelIndex, role=int):
        if not index.isValid():
            return None

        item = self._data[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return item

    def initData(self, data):
        users = []
        for key, value in data.items():
            for k, v in value.items():
                users.append(v[0])
        return ['All'] + list(set(users))

    @QtCore.Slot()
    def updateData(self):
        # print('received')
        data = utils.deserialize(utils.path)
        self._data = self.initData(data['Categories'])
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex(), QtGui.QVector3D())



