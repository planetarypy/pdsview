from ginga.qtw.QtHelp import QtGui, QtCore
import text_finderUI


class LabelView(QtGui.QWidget):
    def __init__(self, image_label):
        QtGui.QWidget.__init__(self, None)
        print("Label Show")
        self.textwindow = QtGui.QVBoxLayout()
        self.textwindow.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))
        self.buttonwindow = QtGui.QHBoxLayout()
        self.labelwindowlayout = QtGui.QHBoxLayout()
        self.buttonwindow.setContentsMargins(QtCore.QMargins(4, 2, 4, 2))

        self.textwidget = QtGui.QWidget()
        self.textwidget.setWindowTitle("Label")
        self.textwidget.resize(640, 620)
        self.labelPT = QtGui.QTextEdit()
        self.labelPT.setReadOnly(True)
        self.font = QtGui.QFont("Monaco")
        self.font.setPointSize(12)

        self.image_label = image_label
        self.labelPT.setFont(self.font)
        self.textwindow.addWidget(self.labelPT, stretch=0)

        findButton = QtGui.QPushButton("Find")
        findButton.clicked.connect(self.find)
        cancelbutton = QtGui.QPushButton("Cancel")
        cancelbutton.clicked.connect(self.cancel)

        for button in (findButton, cancelbutton):
            self.buttonwindow.addWidget(button, stretch=0)

        self.buttonwidget = QtGui.QWidget()
        self.buttonwidget.setLayout(self.buttonwindow)
        self.textwindow.addWidget(self.buttonwidget, stretch=0)
        self.textwidget.setLayout(self.textwindow)

        self.label_show()

    def label_show(self):
        if self.image_label == None:
            self.labelPT.setText("Please Open an Image First !")
        else:
            self.labelPT.setText('\n'.join(self.image_label))
            # labelPT.setText(json.dumps(image_label, indent=4))
        self.textwidget.setLayout(self.textwindow)
        self.textwidget.setMinimumWidth(50)
        self.textwidget.show()
        self.textwidget.raise_()
        self.textwidget.activateWindow()
        labelview_window = self.textwidget
        return labelview_window

    def find(self):
        self.lastMatch = None
        self.finderUI()

    def finderUI(self):
        mw = text_finderUI.LabelSearch()
        self.labelwindowlayout.addWidget(mw, stretch=0)
        print mw.search()

    def cancel(self):
        self.deleteLater()
