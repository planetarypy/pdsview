import sys
from pdsview import pdsview
import pytestqt
from ginga.qtw.QtHelp import QtGui, QtCore


def test_window_cascade(qtbot):
    """Tests the window cascade."""

    window = pdsview.PDSViewer()
    window.show()
    qtbot.addWidget(window)

    # Initial checks
    assert window._label_window is None
    assert window.open_label.isEnabled() is False

    # Load test file and check the label button
    window.load_file("./tests/mission_data/1p190678905erp64kcp2600l8c1.img")
    assert window.open_label.isEnabled() is True

    # Open the label window and run appropriate checks
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window is not None
    assert window._label_window._finder_window is None
    assert window._label_window.is_open is True

    # Open the finder window and run appropriate checks
    qtbot.mouseClick(window._label_window.find_button, QtCore.Qt.LeftButton)
    assert window._label_window._finder_window is not None
    assert window._label_window._finder_window.query_edit is False

    # Hide windows and check to make sure they are hidden
    qtbot.mouseClick(window._label_window._finder_window.ok_button, QtCore.Qt.LeftButton)
    assert window._label_window._finder_window.isHidden() is True
    qtbot.mouseClick(window._label_window.cancel_button, QtCore.Qt.LeftButton)
    assert window._label_window.isHidden() is True

    # Test the ability for the parent (label) to hide the child (finder)
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    qtbot.mouseClick(window._label_window.find_button, QtCore.Qt.LeftButton)
    assert window._label_window.isHidden() is not True
    assert window._label_window._finder_window.isHidden() is not True
    qtbot.mouseClick(window._label_window.cancel_button, QtCore.Qt.LeftButton)
    assert window._label_window.isHidden() is True
    assert window._label_window._finder_window.isHidden() is True


def test_label_refresh(qtbot):
    """Tests the label display and refresh features."""

    window = pdsview.PDSViewer()
    window.show()
    qtbot.addWidget(window)
    window.load_file("./tests/mission_data/1p190678905erp64kcp2600l8c1.img")
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"

    window.load_file("./tests/mission_data/2p129641989eth0361p2600r8m1.img")
    assert window._label_window.label_contents.toPlainText()[193:196] == "332"


def test_label_load(qtbot):
    """Tests the ability to properly load a label."""

    window = pdsview.PDSViewer()
    window.show()
    qtbot.addWidget(window)
    window.load_file("./tests/mission_data/1p190678905erp64kcp2600l8c1.img")
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"

    qtbot.mouseClick(window._label_window.find_button, QtCore.Qt.LeftButton)
    assert window._label_window._finder_window.find_field.toPlainText() == ""
