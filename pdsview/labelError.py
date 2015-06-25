from ginga.qtw.QtHelp import QtGui, QtCore
import textFinder


class LabelError(QtGui.QDialog):
    def __init__(self, parent=None):
#   Add exception vaiable if generalizing this error message window.
        super(LabelError, self).__init__(parent)
#        print("Label Error")

#       Setup the two layouts that will house the message and the
#       acknowledgement fields.
        self.windowLayout = QtGui.QVBoxLayout()
        self.windowLayout.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.addStretch()
        self.buttonLayout.setContentsMargins(QtCore.QMargins(4, 2, 4, 2))

        self.setWindowTitle("Label Error")
        self.resize(400, 140)

#        self.explanation = exception.__doc__
#        self.eMessage = exception.message
#
#       Create and populate the message and the acknowledgement fields.
        self.messageField = QtGui.QLabel("<font color=black size=24><center><b>No label found.</b></center></font>")
        self.messageField.resize(350, 100)
#        self.errorExp = QtGui.QTextEdit()
#        self.errorMessage = QtGui.QTextEdit()
        self.confirmButton = QtGui.QPushButton("Ok")
        self.confirmButton.clicked.connect(self.confirm)

#       Add the fields to the their layouts and add the layouts to the Qdialog.
        self.windowLayout.addWidget(self.messageField, stretch=0)
        self.buttonLayout.addWidget(self.confirmButton)
        self.layout = QtGui.QGridLayout()
        self.layout.addLayout(self.windowLayout, 0, 0)
        self.layout.addLayout(self.buttonLayout, 1, 0)
        
        self.setLayout(self.layout)

    def confirm(self):
#        print "Closing label error window...."
        self.hide()
#        self.messageBox.close()
#        print "Label close done"

