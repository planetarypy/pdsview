#
# This module is a label viewer. At the moment, all it really does is display
# the label and give the option to pull up a search window to search the text in
# the label. When this window is hidden, the search query in the text finder is
# cleared and that window is hidden as well if it is not already. Also, if this
# window is left open, pdsview will automatically update the label field so the
# label being displayed is always the label for the current product being
# displayed.
#

from ginga.qtw.QtHelp import QtGui, QtCore
import textFinder


class LabelView(QtGui.QDialog):
    def __init__(self, parent):
        super(LabelView, self).__init__(parent)

#       Initialize the subdialogs
        self._finderWindow = None

        self.parent = parent
        self.isOpen = True

#       Setting up the layout boxes.
        self.textLayout = QtGui.QVBoxLayout()
        self.textLayout.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.addStretch()
        self.buttonLayout.setContentsMargins(QtCore.QMargins(4, 2, 4, 2))
        self.layout = QtGui.QGridLayout()

#       Setting up window details.
        self.setWindowTitle("Label")
        self.resize(640, 620)

#       Setting up the area where the label will be displayed.
        self.labelContents = QtGui.QTextEdit()
        self.labelContents.setReadOnly(True)
        self.font = QtGui.QFont("Monaco")
        self.font.setPointSize(12)
        self.labelContents.setFont(self.font)

#       Setting up the label and adding it to the label field set up above.
        self.labelContents.setText('\n'.join(self.parent.imageLabel))

#       Creating and binding the buttons.
        self.findButton = QtGui.QPushButton("Find")
        self.findButton.clicked.connect(self.finderWindow)
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel)

#       Adding the text and button widgets to the layout boxes.
        self.textLayout.addWidget(self.labelContents, stretch=0)
        self.buttonLayout.addWidget(self.findButton, 0, 0)
        self.buttonLayout.addWidget(self.cancelButton, 0, 1)

#       Adding all of the layout boxes to the overall layout.
        self.layout.addLayout(self.textLayout, 0, 0)
        self.layout.addLayout(self.buttonLayout, 1, 0)
        
#       Adding the overall layout to the dialog box.
        self.setLayout(self.layout)

    def finderWindow(self):
#       Make sure that there is only one instance of the dialog window.
        if self._finderWindow == None:
            self._finderWindow = textFinder.LabelSearch(self)
            pos  = self.frameGeometry().center()
        self._finderWindow.show()
        self._finderWindow.activateWindow()
    
    def cancel(self):
#       Clear the query field and hide the search dialog if it isn't already
#       hidden.
        self.isOpen = False
        if(self._finderWindow != None):
            self._finderWindow.close()
        self.hide()
