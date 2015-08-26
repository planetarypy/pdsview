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

    # Hide windows and check to make sure they are hidden
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


def test_display_values(qtbot):
    """Test the display values text boxes"""
    test_images = pdsview.ImageSet([FILE_1, FILE_2])
    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
    # Test default values
    assert window.x_value.text() == 'X: ????'
    assert window.y_value.text() == 'Y: ????'
    assert window.pixel_value.text() == 'Value: ????'
    assert window.pds_view.has_callback('cursor-down')
    assert window.pds_view.has_callback('cursor-down')
    # Test the text changes to the rounded value
    window.display_values(window.pds_view, QtCore.Qt.LeftButton, 10.4, 50.6)
    assert window.x_value.text() == 'X: 10'
    assert window.y_value.text() == 'Y: 51'
    # Python 2 and 3 have different round methods
    try:
        assert window.pixel_value.text() == 'Value: 24.0'
    except:
        assert window.pixel_value.text() == 'Value: 24'
    assert window.pds_view.has_callback('motion')
    # Test Values go back to default after switching images
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window.x_value.text() == 'X: ????'
    assert window.y_value.text() == 'Y: ????'
    assert window.pixel_value.text() == 'Value: ????'
    # Test second display
    window.display_values(window.pds_view, QtCore.Qt.LeftButton, 14, 38)
    assert window.x_value.text() == 'X: 14'
    assert window.y_value.text() == 'Y: 38'
    # Python 2 and 3 have different round methods
    try:
        assert window.pixel_value.text() == 'Value: 15.0'
    except:
        assert window.pixel_value.text() == 'Value: 15'
    # Test when clicking outside the image
    window.display_values(window.pds_view, QtCore.Qt.LeftButton, 100, 200)
    assert window.pixel_value.text() == 'Value: 0'
    # TODO test that the X/Y values changed as well, right now qtbot and ginga
    # are having trouble communicating where/which widget is clicked so the
    # values do not update correctly
    # TODO test with a 3 band color image


def test_apply_parameters(qtbot):
    """Test that images maintain their parameters"""
    test_images = pdsview.ImageSet([FILE_1, FILE_2])
    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
    image1 = window.image_set.current_image
    assert image1.sarr[0] == 0
    assert image1.sarr[255] == 255
    assert image1.zoom == 1.0
    assert image1.rotation == 0.0
    assert image1.transforms == (False, False, False)
    assert image1.cuts == (0.0, 0.0)
    # Change parameters
    image1.sarr[0] = 42
    image1.sarr[255] = 13
    window.pds_view.get_rgbmap().set_sarr(image1.sarr)
    window.pds_view.zoom_to(3)
    window.pds_view.rotate(45)
    window.pds_view.transform(False, True, False)
    window.pds_view.cut_levels(24, 95)
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    # Test the second image parameters are None by defualt
    image2 = window.image_set.current_image
    assert image2.sarr is None
    assert image2.zoom is None
    assert image2.rotation is None
    assert image2.transforms is None
    assert image2.cuts is None
    # Test the view was reset to defualt paramters for the image
    assert window.pds_view.get_rgbmap().get_sarr()[0] == 0
    assert window.pds_view.get_rgbmap().get_sarr()[255] == 255
    assert window.pds_view.get_zoom() == 4.746031746031746
    assert window.pds_view.get_rotation() == 0.0
    assert window.pds_view.get_transforms() == (False, False, False)
    assert window.pds_view.get_cut_levels() == (15, 17)
    # Test changing back to the first image maintains image1's parameters
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    image1 = window.image_set.current_image
    assert image1.sarr[0] == 42
    assert image1.sarr[255] == 13
    assert image1.zoom == 3.0
    assert image1.rotation == 45.0
    assert image1.transforms == (False, True, False)
    assert image1.cuts == (24, 95)
    # Test that image2 stored its parameters
    image2 = window.image_set.images[1]
    assert image2.sarr[0] == 0
    assert image2.sarr[255] == 255
    assert image2.zoom == 4.746031746031746
    assert image2.rotation == 0.0
    assert image2.transforms == (False, False, False)
    assert image2.cuts == (15, 17)
