from qtpy import QtWidgets, QtCore


class LabelError(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LabelError, self).__init__(parent)

        # Setup the two layouts that will house the message and the
        # acknowledgement fields.
        self.window_layout = QtWidgets.QVBoxLayout()
        self.window_layout.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.setContentsMargins(QtCore.QMargins(4, 2, 4, 2))

        self.setWindowTitle("Label Error")
        self.resize(400, 140)

        # Create and populate the message and the acknowledgement fields.
        self.message_field = QtWidgets.QLabel(
            "<font color=black size=24><center><b>No label found.</b>" +
            "</center></font>"
        )
        self.message_field.resize(350, 100)
        self.confirm_button = QtWidgets.QPushButton("Ok")
        self.confirm_button.clicked.connect(self.confirm)

        # Add the fields to the their layouts and the layouts to the Qdialog
        self.window_layout.addWidget(self.message_field, stretch=0)
        self.button_layout.addWidget(self.confirm_button)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addLayout(self.window_layout, 0, 0)
        self.layout.addLayout(self.button_layout, 1, 0)

        self.setLayout(self.layout)

    def confirm(self):
        self.hide()
