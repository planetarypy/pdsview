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
FILE_3 = os.path.join(
    'tests', 'mission_data', '1p134482118erp0902p2600r8m1.img')


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
    qtbot.mouseClick(window.next_image, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[233:236] == "170"


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
    qtbot.mouseClick(window.next_image, QtCore.Qt.LeftButton)
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
    window.save_parameters()
    image1 = window.image_set.current_image[0]
    assert image1.sarr[0] == 0
    assert image1.sarr[255] == 255
    # assert image1.zoom == 1.0
    assert image1.rotation == 0.0
    assert image1.transforms == (False, False, False)
    assert image1.cuts == (22, 26)
    # Change parameters
    image1.sarr[0] = 42
    image1.sarr[255] = 13
    window.pds_view.get_rgbmap().set_sarr(image1.sarr)
    # window.pds_view.zoom_to(3)
    window.pds_view.rotate(45)
    window.pds_view.transform(False, True, False)
    window.pds_view.cut_levels(24, 95)
    qtbot.mouseClick(window.next_image, QtCore.Qt.LeftButton)
    # Test the second image parameters are None by defualt
    image2 = window.image_set.current_image[0]
    assert image2.sarr is None
    assert image2.zoom is None
    assert image2.rotation is None
    assert image2.transforms is None
    assert image2.cuts is None
    # Test the view was reset to defualt paramters for the image
    assert window.pds_view.get_rgbmap().get_sarr()[0] == 0
    assert window.pds_view.get_rgbmap().get_sarr()[255] == 255
    # assert window.pds_view.get_zoom() == 1.0
    assert window.pds_view.get_rotation() == 0.0
    assert window.pds_view.get_transforms() == (False, False, False)
    assert window.pds_view.get_cut_levels() == (15, 17)
    # Test changing back to the first image maintains image1's parameters
    qtbot.mouseClick(window.previous_image, QtCore.Qt.LeftButton)
    image1 = window.image_set.current_image[0]
    assert image1.sarr[0] == 42
    assert image1.sarr[255] == 13
    # assert image1.zoom == 3.0
    assert image1.rotation == 45.0
    assert image1.transforms == (False, True, False)
    assert image1.cuts == (24, 95)
    # Test that image2 stored its parameters
    image2 = window.image_set.images[1][0]
    assert image2.sarr[0] == 0
    assert image2.sarr[255] == 255
    # assert image2.zoom == 4.746031746031746
    assert image2.rotation == 0.0
    assert image2.transforms == (False, False, False)
    assert image2.cuts == (15, 17)


def test_set_ROI_text(qtbot):
    """Test the ROI text to contain the correct values"""
    test_images = pdsview.ImageSet([FILE_1, FILE_2])
    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
    # Test Whole image ROI
    # window.set_ROI_text(0, 0, current_image.width, current_image.height)
    assert window.pixels.text() == '#Pixels: 32768'
    assert window.std_dev.text() == 'Std Dev: 15.769365'
    assert window.mean.text() == 'Mean: 27.2659'
    assert window.median.text() == 'Median: 24.0'
    assert window.min.text() == 'Min: 22'
    assert window.max.text() == 'Max: 115'
    # Test 2x2 random ROI
    # .5 values because these are the edge of the ROI pixels
    window.set_ROI_text(9.5, 18.5, 11.5, 20.5)
    assert window.pixels.text() == '#Pixels: 4.0'
    assert window.std_dev.text() == 'Std Dev: 0.829156'
    assert window.mean.text() == 'Mean: 23.25'
    assert window.median.text() == 'Median: 23.5'
    assert window.min.text() == 'Min: 22'
    assert window.max.text() == 'Max: 24'


def test_top_right_pixel_snap(qtbot):
    """Test the top and right values snap to the inclusive edge"""
    test_images = pdsview.ImageSet([FILE_1, FILE_2])
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    test_snap_1 = window.top_right_pixel_snap(10, 5)
    assert test_snap_1[0] == 5.5
    assert test_snap_1[1]
    test_snap_2 = window.top_right_pixel_snap(-5, 5)
    assert not test_snap_2[1]
    test_snap_3 = window.top_right_pixel_snap(5.4, 10)
    assert test_snap_3[0] == 5.5
    assert test_snap_3[1]
    test_snap_4 = window.top_right_pixel_snap(5.5, 10)
    assert test_snap_4[0] == 5.5
    assert test_snap_4[1]
    test_snap_5 = window.top_right_pixel_snap(5.6, 10)
    assert test_snap_5[0] == 6.5
    assert test_snap_5[1]


def test_bottom_left_pixel_snap(qtbot):
    """Test the bottom and left values snap to the inclusive edge"""
    test_images = pdsview.ImageSet([FILE_1, FILE_2])
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    test_snap_1 = window.bottom_left_pixel_snap(-5, 5)
    assert test_snap_1[0] == -0.5
    assert test_snap_1[1]
    test_snap_2 = window.bottom_left_pixel_snap(10, 5)
    assert not test_snap_2[1]
    test_snap_3 = window.bottom_left_pixel_snap(5.4, 10)
    assert test_snap_3[0] == 4.5
    assert test_snap_3[1]
    test_snap_4 = window.bottom_left_pixel_snap(5.5, 10)
    assert test_snap_4[0] == 5.5
    assert test_snap_4[1]


def test_left_right_bottom_top(qtbot):
    """Test that the x1, x2, y1, y2 values are assigned to the correct edge"""
    test_images = pdsview.ImageSet([FILE_1, FILE_2])
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    test_coords_1 = window.left_right_bottom_top(1, 2, 1, 2)
    assert test_coords_1[0:4] == (1, 2, 1, 2)
    assert test_coords_1[4]
    assert test_coords_1[5]
    test_coords_2 = window.left_right_bottom_top(2, 1, 1, 2)
    assert test_coords_2[0:4] == (1, 2, 1, 2)
    assert not test_coords_2[4]
    assert test_coords_2[5]
    test_coords_3 = window.left_right_bottom_top(1, 2, 2, 1)
    assert test_coords_3[0:4] == (1, 2, 1, 2)
    assert test_coords_3[4]
    assert not test_coords_3[5]
    test_coords_4 = window.left_right_bottom_top(2, 1, 2, 1)
    assert test_coords_4[0:4] == (1, 2, 1, 2)
    assert not test_coords_4[4]
    assert not test_coords_4[5]


def test_switch_rgb(qtbot):
    """Test switch_rgb makes a 3 band image when checked, single band else"""
    test_images = pdsview.ImageSet([FILE_1, FILE_3])
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    # Check that intially the current image is a single band
    assert window.image_set.current_image[0].ndim == 2
    window.next_channel.setEnabled(False)
    window.rgb_check_box.setCheckState(QtCore.Qt.Checked)
    # Test the current image is now a 3 band image
    assert window.image_set.current_image[0].ndim == 3
    assert not window.next_channel.isEnabled()
    window.rgb_check_box.setCheckState(QtCore.Qt.Unchecked)
    # Test the current image is now a single band image again
    assert window.image_set.current_image[0].ndim == 2


def test_update_rgb(qtbot):
    """Test update_rgb chooses the correc images to add to rgb list"""
    test_images = pdsview.ImageSet([FILE_1, FILE_3])
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    window.update_rgb()
    image_1 = window.image_set.images[0][0]
    image_2 = window.image_set.images[1][0]
    image_3 = window.image_set.images[0][0]
    assert window.rgb == [image_1, image_2, image_3]
    # TODO: Test with a 3 band image


def test_restore(qtbot):
    """Test restore resets any changes to defaults"""
    test_images = pdsview.ImageSet([FILE_1, FILE_2])
    window = pdsview.PDSViewer(test_images)
    window.show()
    qtbot.addWidget(window)
    window.save_parameters()
    image1 = window.pds_view.get_image()
    # Initial checks
    assert image1.sarr[0] == 0
    assert image1.sarr[255] == 255
    assert image1.zoom == 1.0
    assert image1.rotation == 0.0
    assert image1.transforms == (False, False, False)
    assert image1.cuts == (22, 26)
    # Change parameters
    window.pds_view.zoom_to(3)
    window.pds_view.rotate(45)
    window.pds_view.transform(False, True, False)
    window.pds_view.cut_levels(24, 95)
    # Restore back to defaults
    qtbot.mouseClick(window.restore_defaults, QtCore.Qt.LeftButton)
    assert image1.sarr[0] == 0
    assert image1.sarr[255] == 255
    assert image1.zoom == 1.0
    assert image1.rotation == 0.0
    assert image1.transforms == (False, False, False)
    assert image1.cuts == (22, 26)
