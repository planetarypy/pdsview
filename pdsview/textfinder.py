"""This module implements a search feature for the label window. Since the
label will not be edited, the only thing this does is highlight query matches
in the label window. The search is a live search, so it will work as text is
being entered. When the search window is closed (hidden), the highlighting
will be undone and the query will be cleared.
"""

from qtpy import QtWidgets, QtCore, QtGui


class LabelSearch(QtWidgets.QDialog):
    """A simple search tool for text widgets."""

    def __init__(self, parent):
        super(LabelSearch, self).__init__(parent)

        # Setting a way to access the parent so the search can access the text
        # field where the label lives. Also, set a flag to let the program know
        # if there have been changes to the query field.
        self.parent = parent

        # This is used to determine when to reset the search highlighter.
        self.query_edit = False

        self.resize(250, 70)
        self.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))

        self.find_field = QtWidgets.QTextEdit(self)
        self.find_field.resize(200, 50)
        self.font = QtGui.QFont("Monaco")
        self.font.setPointSize(12)

        # This is a live search, so the only button needed is one to hide the
        # window.
        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.clicked.connect(self.cancel)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.find_field)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

        self.find_field.textChanged.connect(self.highlighter)

    def highlighter(self):
        self.cursor = self.parent.label_contents.textCursor()
        self.highlight_reset()

        self.query_edit = True

        # Setting and using the query. X.toPlainText() returns an empty string
        # if there is nothing in the box. The search spazzes out if there is an
        # empty string, so the "if" filter is needed. This method does nothing
        # if the query is an empty string.
        query = self.find_field.toPlainText()
        if(query != ""):
            # Setting the highlight color, the query, and the cursor for the
            # label contents window.
            query_color = QtGui.QTextCharFormat()
            query_color.setBackground(QtGui.QBrush(QtGui.QColor("red")))
            regex = QtCore.QRegExp(query)
            self.cursor = self.parent.label_contents.textCursor()
            pos = 0
            index = regex.indexIn(
                self.parent.label_contents.toPlainText(), pos)

            # This finds and highlights all occurences of the query.
            while (index != -1):
                self.cursor.setPosition(index)
                self.cursor.movePosition(QtGui.QTextCursor.Right,
                                         QtGui.QTextCursor.KeepAnchor,
                                         len(query))
                self.cursor.mergeCharFormat(query_color)
                pos = index + regex.matchedLength()
                index = regex.indexIn(self.parent.label_contents.toPlainText(),
                                      pos)

    def highlight_reset(self):
        # This method makes sure the text is unhighlighted.
        normal_color = QtGui.QTextCharFormat()
        normal_color.setBackground(QtGui.QBrush(QtGui.QColor("white")))
        self.cursor.setPosition(0)
        self.cursor.movePosition(QtGui.QTextCursor.End,
                                 QtGui.QTextCursor.KeepAnchor, 1)
        self.cursor.mergeCharFormat(normal_color)

    def cancel(self):
        if self.query_edit:
            self.highlight_reset()
        self.find_field.setText("")
        self.hide()
