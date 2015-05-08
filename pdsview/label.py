import json
from ginga.qtw.QtHelp import QtGui


def label_show(image_label):
    print("Label Show")
    labelwindow = QtGui.QWidget()
    labelwindow.setWindowTitle("Label")
    labelwindow.resize(524, 540)
    labelPT = QtGui.QTextEdit()
    labelPT.setReadOnly(True)
    if image_label == None:
        labelPT.setText("Please Open an Image First !")
    else:
        labelPT.setText(json.dumps(image_label, indent=4))
    vbox1 = QtGui.QVBoxLayout()
    vbox1.addWidget(labelPT)
    labelwindow.setLayout(vbox1)
    labelwindow.setMinimumWidth(50)
    labelwindow.show()
    labelwindow.raise_()
    labelwindow.activateWindow()
    return labelwindow
