#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pdsview import pdsview
import pytestqt
from ginga.qtw.QtHelp import QtGui, QtCore
import os
FILE_1 = os.path.join(
    'tests', 'mission_data', '2m132591087cfd1800p2977m2f1.img')
FILE_2 = os.path.join(
    'tests', 'mission_data', '2p129641989eth0361p2600r8m1.img')
FILE_3 = os.path.join(
    'tests', 'mission_data', '1p190678905erp64kcp2600l8c1.img')
FILE_1_NAME = "2m132591087cfd1800p2977m2f1.img"
FILE_2_NAME = "2p129641989eth0361p2600r8m1.img"
FILE_3_NAME = "1p190678905erp64kcp2600l8c1.img"
test_images = pdsview.ImageSet([FILE_1, FILE_2, FILE_3])


def test_image_next_switch(qtbot):
    """Verifies that pdsview will switch to the next image properly when
    multiple images are loaded. Also verifies that pdsview will jump
    to the first image in the set when the "Next" button is pressed while
    viewing the last image.
    """

    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
#   This simulates sys.argv
    assert window.open_label.isEnabled()
    assert window.next_channel.isEnabled()

#   '2m1...' file
    assert test_images.current_image.file_name == FILE_1_NAME
    assert test_images.current_image_index == 0

#   '2p1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert test_images.current_image.file_name == FILE_2_NAME
    assert test_images.current_image_index == 1

#   '1p1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert test_images.current_image.file_name == FILE_3_NAME
    assert test_images.current_image_index == 2

#   back to the '2m1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert test_images.current_image.file_name == FILE_1_NAME
    assert test_images.current_image_index == 0


def test_image_previous_switch(qtbot):
    """Verifies that pdsview will switch to the previous image properly when
    multiple images are loaded. Also verifies that pdsview will jump
    to the last image in the set when the "Previous" button is pressed while
    viewing the first image.
    """
    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
#   This simulates sys.argv

    assert window.open_label.isEnabled()
    assert window.previous_channel.isEnabled()

#   '2m1...' file
    assert test_images.current_image.file_name == FILE_1_NAME
    assert test_images.current_image_index == 0

#   '1p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert test_images.current_image.file_name == FILE_3_NAME
    assert test_images.current_image_index == 2

#   '2p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert test_images.current_image.file_name == FILE_2_NAME
    assert test_images.current_image_index == 1

#   back to the '2m1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert test_images.current_image.file_name == FILE_1_NAME
    assert test_images.current_image_index == 0


def test_label_next_switch(qtbot):
    """Verifies that the label will be properly updated when switching to the
    next image in the set. Also verifies that the label updates properly
    when pdsview jumps to the first image in the set.
    """
    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
#   This simulates sys.argv

#   '2m1...' file
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[182:186] == "1029"

#   '2p1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[193:196] == "332"

#   jumps to the '1p1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"

#   jump to the original '2m1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[182:186] == "1029"


def test_label_previous_switch(qtbot):
    """Verifies that the label will be properly updated when switching to the
    previous image in the set. Also verifies that the label updates properly
    when pdsview jumps to the last image in the set.
    """
    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
#   This simulates sys.argv

#   '2m1...' file
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[182:186] == "1029"

#   jumps to the '1p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"

#   '2p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[193:196] == "332"

#   the original '1p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[182:186] == "1029"
