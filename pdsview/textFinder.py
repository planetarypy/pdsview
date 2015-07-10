#
# This module implements a search feature for the label window. Since the label
# will not be edited, the only thing this does is highlight query matches in the
# label window. The search is a live search, so it will work as text is being
# entered. When the search window is closed (hidden), the highlighting will be
# undone. Also, the query will remain in the dialog for the lifetime of the
# label window. When the label window is hidden, the query is cleared.
#

from ginga.qtw.QtHelp import QtGui, QtCore

class LabelSearch(QtGui.QDialog):
    def __init__(self, parent):
        super(LabelSearch, self).__init__(parent)
        
#       Setting a way to access the parent so the search can access the text
#       field where the label lives. Also, set a flag to let the program know if
#       there have been changes to the query field.
        self.parent = parent
        self.edit = False

        self.resize(250, 70)
        self.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))

        self.findField = QtGui.QTextEdit(self)
        self.findField.resize(200, 50)
        self.font = QtGui.QFont("Monaco")
        self.font.setPointSize(12)

#       This is a live search, so the only button needed is one to hide the
#       window.
        self.buttonLayout = QtGui.QHBoxLayout()
        self.okButton = QtGui.QPushButton("Ok")
        self.buttonLayout.addWidget(self.okButton)
        self.okButton.clicked.connect(self.close)

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.findField, 0, 0)
        self.layout.addLayout(self.buttonLayout)

        self.setLayout(self.layout)
        
        self.findField.textChanged.connect(self.highlighter)

    def highlighter(self):
        self.cursor = self.parent.labelContents.textCursor()
        self.highlightReset()

        self.edit = True

#       Setting and using the query. X.toPlainText() returns an empty string if
#       there is nothing in the box. The search spazzes out if there is an empty
#       string, so the "if" filter is needed. This method does nothing if the
#       query is an empty string.
        query = self.findField.toPlainText()
        if(query != ""):
#           Setting the highlight color, the query, and the cursor for the label
#           contents window.
            queryColor = QtGui.QTextCharFormat()
            queryColor.setBackground(QtGui.QBrush(QtGui.QColor("red")))
            regex = QtCore.QRegExp(query)
            self.cursor = self.parent.labelContents.textCursor()
            pos = 0
            index = regex.indexIn(self.parent.labelContents.toPlainText(), pos)

#           This finds and highlights all occurences of the query.
            while (index != -1):
                self.cursor.setPosition(index)
                self.cursor.movePosition(QtGui.QTextCursor.Right,
                                         QtGui.QTextCursor.KeepAnchor, 
                                         len(query))
                self.cursor.mergeCharFormat(queryColor)
                pos = index + regex.matchedLength()
                index = regex.indexIn(self.parent.labelContents.toPlainText(),
                                      pos)
 
    def highlightReset(self):
#       This method makes sure the text is unhighlighted.
        normalColor = QtGui.QTextCharFormat()
        normalColor.setBackground(QtGui.QBrush(QtGui.QColor("white")))
        self.cursor.setPosition(0)
        self.cursor.movePosition(QtGui.QTextCursor.End,
                                 QtGui.QTextCursor.KeepAnchor, 1)
        self.cursor.mergeCharFormat(normalColor)

    def close(self):
        if self.edit:
            self.highlightReset()
        self.findField.setText("")
        self.hide()
