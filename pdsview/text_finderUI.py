from ginga.qtw.QtHelp import QtGui, QtCore


class LabelSearch(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self, None)
        print("Text Search")
        self.textwindow = QtGui.QVBoxLayout()
        self.textwindow.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))
        self.buttonwindow = QtGui.QHBoxLayout()
        self.labelwindowlayout = QtGui.QHBoxLayout()
        self.buttonwindow.setContentsMargins(QtCore.QMargins(4, 2, 4, 2))

        self.textwidget = QtGui.QWidget()
        self.textwidget.setWindowTitle("Search Window")
        self.textwidget.resize(250, 70)
        self.findField = QtGui.QTextEdit(self)
        self.findField.resize(200, 50)
        self.font = QtGui.QFont("Monaco")
        self.font.setPointSize(12)
        self.searchButton = QtGui.QPushButton("Search")
        self.searchButton.clicked.connect(self.search)
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel)

        self.findField.setFont(self.font)
        self.textwindow.addWidget(self.findField, stretch=0)
        self.buttonwindow.addWidget(self.searchButton, stretch=0)
        self.buttonwindow.addWidget(self.cancelButton, stretch=0)

        self.buttonwidget = QtGui.QWidget()
        self.buttonwidget.setLayout(self.buttonwindow)
        self.textwindow.addWidget(self.buttonwidget, stretch=0)
        self.textwidget.setLayout(self.textwindow)
        self.textwidget.setMinimumWidth(50)
        self.textwidget.show()
        self.textwidget.raise_()
        self.textwidget.activateWindow()

    def search(self):
        # Here, we get the value printed in the findField of the "Search Window"
        # TODO:
        # Set Callback method or Find a way to reflect this value back to the "label.py"
        # Once we populate "label.py" with the updated search-string, one can take a reference from:
        # https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-3/147
        print self.findField.toPlainText()
        return self.findField.toPlainText()

    def cancel(self):
        self.deleteLater()
