"""This module is a label viewer. At the moment, all it really does is display
the label and give the option to pull up a search window to search the text in
the label. When this window is hidden, the search query in the text finder is
cleared and that window is hidden as well if it is not already. Also, if this
window is left open, pdsview will automatically update the label field so the
label being displayed is always the label for the current product being
displayed.
"""

from qtpy import QtWidgets, QtCore, QtGui
try:
    import textfinder
except:
    from pdsview import textfinder


class LabelView(QtWidgets.QDialog):
    """A PDS image label viewer."""

    def __init__(self, parent):
        super(LabelView, self).__init__(parent)

        # Initialize the subdialogs
        self._finder_window = None

        self.parent = parent
        self.is_open = True

        # Setting up the layout boxes.
        self.text_layout = QtWidgets.QVBoxLayout()
        self.text_layout.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.setContentsMargins(QtCore.QMargins(4, 2, 4, 2))
        self.layout = QtWidgets.QGridLayout()

        # Setting up window details.
        self.setWindowTitle("Label")
        self.resize(640, 620)

        # Setting up the area where the label will be displayed.
        self.label_contents = QtWidgets.QTextEdit()
        self.label_contents.setReadOnly(True)
        self.font = QtGui.QFont("Courier")
        self.font.setPointSize(12)
        self.label_contents.setFont(self.font)

        # Setting up the label and adding it to the label field.
        self.label_contents.setText('\n'.join(self.parent.image_label))

        # Creating and binding the buttons.
        self.find_button = QtWidgets.QPushButton("Find")
        self.find_button.clicked.connect(self.finder_window)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)

        # Adding the text and button widgets to the layout boxes.
        self.text_layout.addWidget(self.label_contents, stretch=0)
        self.button_layout.addWidget(self.find_button)
        self.button_layout.addWidget(self.cancel_button)

        # Adding all of the layout boxes to the overall layout.
        self.layout.addLayout(self.text_layout, 0, 0)
        self.layout.addLayout(self.button_layout, 1, 0)

        # Adding the overall layout to the dialog box.
        self.setLayout(self.layout)

    def finder_window(self):
        """Check for a previously opened finder window and open/show it."""
        if self._finder_window is None:
            self._finder_window = textfinder.LabelSearch(self)
        self._finder_window.show()
        self._finder_window.activateWindow()

    def cancel(self):
        """Hiding the label window and the finder window if open."""
        self.is_open = False
        if self._finder_window is not None:
            self._finder_window.cancel()
        self.hide()
