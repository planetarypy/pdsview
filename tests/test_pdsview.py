#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pdsview import pdsview
import pytestqt
from ginga.qtw.QtHelp import QtGui, QtCore
import os

FILE_1 = os.path.join(
    'tests', 'mission_data', '1p190678905erp64kcp2600l8c1.img')
FILE_2 = os.path.join(
    'tests', 'mission_data', '2p129641989eth0361p2600r8m1.img')


def test_window_cascade(qtbot):
    """Tests the window cascade."""

    test_image = pdsview.ImageSet([FILE_1])
    window = pdsview.PDSViewer(test_image)
    window.show()
    qtbot.addWidget(window)

    # Initial checks
    assert window._label_window is None
    assert window.open_label.isEnabled()

    # Open the label window and run appropriate checks
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window is not None
    assert window._label_window._finder_window is None
    assert window._label_window.is_open

    # Open the finder window and run appropriate checks
    qtbot.mouseClick(window._label_window.find_button, QtCore.Qt.LeftButton)
    assert window._label_window._finder_window is not None
    assert not(window._label_window._finder_window.query_edit)

    # Hide windows and check to make sure they are hidpden
    qtbot.mouseClick(
        window._label_window._finder_window.ok_button, QtCore.Qt.LeftButton)
    assert window._label_window._finder_window.isHidden()
    qtbot.mouseClick(window._label_window.cancel_button, QtCore.Qt.LeftButton)
    assert window._label_window.isHidden()

    # Test the ability for the parent (label) to hide the child (finder)
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    qtbot.mouseClick(window._label_window.find_button, QtCore.Qt.LeftButton)
    assert not(window._label_window.isHidden())
    assert not(window._label_window._finder_window.isHidden())
    qtbot.mouseClick(window._label_window.cancel_button, QtCore.Qt.LeftButton)
    assert window._label_window.isHidden()
    assert window._label_window._finder_window.isHidden()


def test_label_refresh(qtbot):
    """Tests the label display and refresh features."""

    test_images = pdsview.ImageSet([FILE_1, FILE_2])
    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[193:196] == "332"


def test_label_load(qtbot):
    """Tests the ability to properly load a label."""

    test_image = pdsview.ImageSet([FILE_1])
    window = pdsview.PDSViewer(test_image)
    window.show()
    qtbot.addWidget(window)
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"

    qtbot.mouseClick(window._label_window.find_button, QtCore.Qt.LeftButton)
    assert window._label_window._finder_window.find_field.toPlainText() == ""
