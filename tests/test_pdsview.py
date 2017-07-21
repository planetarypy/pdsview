#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pytest
import numpy as np
from qtpy import QtWidgets, QtCore
from planetaryimage import PDS3Image
from ginga.qtw.ImageViewCanvasQt import ImageViewCanvas

from pdsview import pdsview
from pdsview.channels_dialog import ChannelsDialog
from pdsview.histogram import HistogramWidget, HistogramModel

FILE_1 = os.path.join(
    'tests', 'mission_data', '2m132591087cfd1800p2977m2f1.img')
FILE_2 = os.path.join(
    'tests', 'mission_data', '2p129641989eth0361p2600r8m1.img')
FILE_3 = os.path.join(
    'tests', 'mission_data', '1p190678905erp64kcp2600l8c1.img')
FILE_4 = os.path.join(
    'tests', 'mission_data', 'h58n3118.img')
FILE_5 = os.path.join(
    'tests', 'mission_data', '1p134482118erp0902p2600r8m1.img')
FILE_6 = os.path.join(
    'tests', 'mission_data', '0047MH0000110010100214C00_DRCL.IMG')
FILE_1_NAME = '2m132591087cfd1800p2977m2f1.img'
FILE_2_NAME = '2p129641989eth0361p2600r8m1.img'
FILE_3_NAME = '1p190678905erp64kcp2600l8c1.img'
FILE_4_NAME = 'h58n3118.img'
FILE_5_NAME = '1p134482118erp0902p2600r8m1.img'
FILE_6_NAME = '0047MH0000110010100214C00_DRCL.IMG'


def test_image_stamp():
    """Test that ImageStamp sets correct attributes to pds compatible image"""
    pds_image = PDS3Image.open(FILE_1)
    test_image = pdsview.ImageStamp(FILE_1, FILE_1, pds_image, pds_image.data)
    assert test_image.file_name == FILE_1_NAME
    assert test_image.image_name == FILE_1
    assert 'PDS' in test_image.label[0]
    assert isinstance(test_image.label, list)
    assert not test_image.cuts
    assert not test_image.sarr
    assert not test_image.zoom
    assert not test_image.rotation
    assert not test_image.transforms
    assert test_image.not_been_displayed


class TestImageSet(object):
    filepaths = [FILE_1, FILE_2, FILE_3, FILE_4, FILE_5]
    test_set = pdsview.ImageSet(filepaths)

    def test_init(self):
        assert self.test_set._views == set()
        assert len(self.test_set.images) == len(self.filepaths)
        filepaths = sorted(self.filepaths)
        for image, filepath in zip(self.test_set.images, filepaths):
            assert image[0].file_name == os.path.basename(filepath)

        assert self.test_set._current_image_index == 0
        assert self.test_set._channel == 0
        # assert self.test_set._last_channel is None
        assert self.test_set._x_value == 0
        assert self.test_set._y_value == 0
        assert self.test_set._pixel_value == (0, )
        assert self.test_set.use_default_text
        assert self.test_set.rgb == []
        assert self.test_set.current_image is not None

    def test_next_prev_enabled(self):
        assert self.test_set.next_prev_enabled

        test_set2 = pdsview.ImageSet([])
        assert not test_set2.next_prev_enabled

    @pytest.mark.parametrize(
        "index, expected, channel",
        [
            (1, 1, 1),
            (5, 0, 4),
            (11, 1, -1),
            (-1, 4, 7),
            (-13, 2, 42),
            (0, 0, 0)
        ])
    def test_current_image_index(self, index, expected, channel):
        self.test_set.channel = channel
        self.test_set.current_image_index = index
        assert self.test_set.current_image_index == expected
        assert self.test_set.current_image == self.test_set.images[expected]
        assert self.test_set.channel == 0

    def test_channel(self):
        assert self.test_set._channel == self.test_set.channel
        assert len(self.test_set.current_image) == 1
        self.test_set.channel = 42
        # When the current image only has one band, don't change the channel
        assert self.test_set.channel == 0
        assert self.test_set._channel == self.test_set.channel
        # TODO: When an rgb image is in the default test_mission_data, test
        # actually chaning the channel

    def test_x_value(self):
        assert self.test_set.x_value == self.test_set._x_value
        self.test_set.x_value = 42.123456789
        assert isinstance(self.test_set.x_value, int)
        assert self.test_set.x_value == 42
        assert self.test_set.x_value == self.test_set._x_value
        self.test_set.x_value = 0
        assert self.test_set.x_value == 0
        assert self.test_set.x_value == self.test_set._x_value

    def test_y_value(self):
        assert self.test_set.y_value == self.test_set._y_value
        self.test_set.y_value = 42.123456789
        assert isinstance(self.test_set.y_value, int)
        assert self.test_set.y_value == 42
        assert self.test_set.y_value == self.test_set._y_value
        self.test_set.y_value = 0
        assert self.test_set.y_value == 0
        assert self.test_set.y_value == self.test_set._y_value

    def test_pixel_value(self):

        def check_pixel_value(new_pixel, expected):
            self.test_set.pixel_value = new_pixel
            assert self.test_set.pixel_value == expected
            assert isinstance(self.test_set.pixel_value, tuple)
            for val in self.test_set.pixel_value:
                assert isinstance(val, float)
        assert self.test_set.pixel_value == (0.0,)
        check_pixel_value(
            (2.3456, 3.4567, 4.5678), (2.346, 3.457, 4.568))
        check_pixel_value([2.3456, 3.4567, 4.5678], (2.346, 3.457, 4.568))
        check_pixel_value(
            np.array([2.3456, 3.4567, 4.5678]), (2.346, 3.457, 4.568))
        check_pixel_value(
            42.1234, (42.123,))
        check_pixel_value(
            int(42), (42.0,))
        check_pixel_value(
            0, (0,))

    def test_pixel_value_text(self):
        assert self.test_set.pixel_value_text == 'Value: 0.000'
        # TODO: TEST WITH RGB IMAGE

    def test_image_set_append_method(self):
        """Test append method with multiple images"""
        filepaths = [FILE_1]
        new_files = [FILE_2, FILE_3]
        test_set = pdsview.ImageSet(filepaths)
        assert test_set.current_image_index == 0
        assert test_set.current_image[0].file_name == FILE_1_NAME
        assert len(test_set.images) == 1
        assert not(test_set.next_prev_enabled)
        # Mimic how append method is used in pdsview
        first_new_image = len(test_set.images)
        test_set.append(new_files, first_new_image)
        assert test_set.current_image_index == 1
        assert test_set.current_image[0].file_name == FILE_2_NAME
        assert FILE_3_NAME in str(test_set.images)
        assert test_set.next_prev_enabled

    def test_bands_are_composite(self):
        self.test_set.rgb = [image[0] for image in self.test_set.images[:3]]
        assert not self.test_set.bands_are_composite
        # TODO: TEST WITH RGB IMAGE

    # TODO: TEST create_rgb_image WHEN RGB IMAGE IN TEST DATA

    def test_ROI_data(self):
        """Test the ROI_data to cut out the correct region of data"""
        test_set = pdsview.ImageSet([FILE_3])
        width = test_set.current_image[0].width
        height = test_set.current_image[0].height
        test_data_1 = test_set.ROI_data(0, 0, width, height)
        assert test_data_1[0][0] == 23
        assert test_data_1[512][16] == 25
        assert test_data_1[1023][31] == 115
        test_data_2 = test_set.ROI_data(9.5, 18.5, 11.5, 20.5)
        assert test_data_2[0][0] == 22
        assert test_data_2[0][1] == 23
        assert test_data_2[1][0] == 24
        assert test_data_2[1][1] == 24

    def test_ROI_pixels(self):
        """Test ROI_pixels to return the correct number of pixels for a ROI"""
        test_set = pdsview.ImageSet([FILE_3])
        test_pixels = test_set.ROI_pixels(9.5, 18.5, 11.5, 20.5)
        assert test_pixels == 4

    def test_ROI_std_dev(self):
        """Test ROI_std_dev to return the correct standard deviation for ROI"""
        test_set = pdsview.ImageSet([FILE_3])
        test_std_dev = test_set.ROI_std_dev(9.5, 18.5, 11.5, 20.5)
        assert test_std_dev == 0.829156

    def test_ROI_mean(self):
        """Test ROI_mean to return the correct mean value of pixels for ROI"""
        test_set = pdsview.ImageSet([FILE_3])
        test_mean = test_set.ROI_mean(9.5, 18.5, 11.5, 20.5)
        assert test_mean == 23.25

    def test_ROI_median(self):
        """Test ROI_median to return the correct median value for a ROI"""
        test_set = pdsview.ImageSet([FILE_3])
        test_median = test_set.ROI_median(9.5, 18.5, 11.5, 20.5)
        assert test_median == 23.5

    def test_ROI_min(self):
        """Test ROI_min to return the correct minimum pixel value for a ROI"""
        test_set = pdsview.ImageSet([FILE_3])
        test_min = test_set.ROI_min(9.5, 18.5, 11.5, 20.5)
        assert test_min == 22

    def test_ROI_max(self):
        """Test ROI_mx to return the correct maximum pixel value for a ROI"""
        test_set = pdsview.ImageSet([FILE_3])
        test_max = test_set.ROI_max(9.5, 18.5, 11.5, 20.5)
        assert test_max == 24

# TODO test channels when there is a 3 band test image


class TestPDSController(object):
    filepaths = [FILE_1, FILE_2, FILE_3, FILE_4, FILE_5]
    test_set = pdsview.ImageSet(filepaths)
    controller = pdsview.PDSController(test_set, None)

    def test_init(self):
        assert self.controller.model == self.test_set
        assert self.controller.view is None

    def test_next_image(self):
        assert self.test_set.current_image_index == 0
        self.controller.next_image()
        assert self.test_set.current_image_index == 1
        self.test_set.current_image_index = len(self.test_set.images) - 1
        self.controller.next_image()
        assert self.test_set.current_image_index == 0

    def test_previous_image(self):
        assert self.test_set.current_image_index == 0
        self.controller.previous_image()
        last = len(self.test_set.images) - 1
        assert self.test_set.current_image_index == last
        self.test_set.current_image_index = 1
        self.controller.previous_image()
        assert self.test_set.current_image_index == 0

    def test_next_channel(self):
        assert self.test_set.channel == 0
        self.controller.next_channel()
        assert self.test_set.channel == 0
        # TODO: TEST MORE WHEN THERE IS AN RGB IMAGE

    def test_previous_channel(self):
        assert self.test_set.channel == 0
        self.controller.previous_channel()
        assert self.test_set.channel == 0
        # TODO: TEST MORE WHEN THERE IS AN RGB IMAGE

    def test_new_x_value(self):
        self.controller.new_x_value(42.123456789)
        assert isinstance(self.test_set.x_value, int)
        assert self.test_set.x_value == 42
        assert self.test_set.x_value == self.test_set._x_value
        self.controller.new_x_value(0)
        assert self.test_set.x_value == 0
        assert self.test_set.x_value == self.test_set._x_value

    def test_new_y_value(self):
        assert self.test_set.y_value == self.test_set._y_value
        self.controller.new_y_value(42.123456789)
        assert isinstance(self.test_set.y_value, int)
        assert self.test_set.y_value == 42
        assert self.test_set.y_value == self.test_set._y_value
        self.controller.new_y_value(0)
        assert self.test_set.y_value == 0
        assert self.test_set.y_value == self.test_set._y_value

    def test_new_pixel_value(self):

        def check_pixel_value(new_pixel, expected):
            self.controller.new_pixel_value(new_pixel)
            assert self.test_set.pixel_value == expected
            assert isinstance(self.test_set.pixel_value, tuple)
            for val in self.test_set.pixel_value:
                assert isinstance(val, float)
        assert self.test_set.pixel_value == (0.0,)
        check_pixel_value(
            (2.3456, 3.4567, 4.5678), (2.346, 3.457, 4.568))
        check_pixel_value([2.3456, 3.4567, 4.5678], (2.346, 3.457, 4.568))
        check_pixel_value(
            np.array([2.3456, 3.4567, 4.5678]), (2.346, 3.457, 4.568))
        check_pixel_value(
            42.1234, (42.123,))
        check_pixel_value(
            int(42), (42.0,))
        check_pixel_value(
            0, (0,))

    images = test_set.images

    @pytest.mark.parametrize(
        'image_index, expected',
        [
            (0, [images[0][0], images[1][0], images[2][0]]),
            (1, [images[1][0], images[2][0], images[3][0]]),
            (len(images) - 1, [images[-1][0], images[0][0], images[1][0]])
        ])
    def test_populate_rgb(self, image_index, expected):
        test_rgb = self.controller._populate_rgb(image_index)
        assert test_rgb == expected

    def test_update_rgb(self):
        expected = [self.images[0][0], self.images[1][0], self.images[2][0]]
        self.test_set.rgb = [1, 2, 3]
        self.controller.update_rgb()
        assert self.test_set.rgb != [1, 2, 3]
        assert self.test_set.rgb == expected


class TestPDSViewer(object):
    filepaths = [FILE_1, FILE_2, FILE_3, FILE_4, FILE_5]
    test_set = pdsview.ImageSet(filepaths)
    viewer = pdsview.PDSViewer(test_set)
    viewer.show()

    def test_init(self):
        assert self.viewer.image_set == self.test_set
        assert self.viewer in self.test_set._views
        assert self.viewer._label_window is None
        assert self.viewer._label_window_pos is None
        assert self.viewer.channels_window is None
        assert not self.viewer.channels_window_is_open
        assert self.viewer.channels_window_pos is None
        assert isinstance(
            self.viewer.view_canvas, ImageViewCanvas)
        assert isinstance(
            self.viewer.next_image_btn, QtWidgets.QPushButton)
        assert isinstance(
            self.viewer.previous_image_btn, QtWidgets.QPushButton)
        assert isinstance(
            self.viewer.open_label, QtWidgets.QPushButton)
        assert isinstance(
            self.viewer.next_channel_btn, QtWidgets.QPushButton)
        assert isinstance(
            self.viewer.previous_channel_btn, QtWidgets.QPushButton)
        assert isinstance(
            self.viewer.restore_defaults, QtWidgets.QPushButton)
        assert isinstance(
            self.viewer.channels_button, QtWidgets.QPushButton)
        assert isinstance(
            self.viewer.x_value_lbl, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.y_value_lbl, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.pixel_value_lbl, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.pixels, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.std_dev, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.mean, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.median, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.min, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.max, QtWidgets.QLabel)
        assert isinstance(
            self.viewer.histogram, HistogramModel)
        assert isinstance(
            self.viewer.histogram_widget, HistogramWidget)
        assert isinstance(
            self.viewer.rgb_check_box, QtWidgets.QCheckBox)
        assert self.viewer.windowTitle() == FILE_5_NAME

        assert self.viewer.pixels.text() == '#Pixels: 32768'
        assert self.viewer.std_dev.text() == 'Std Dev: 16.100793'
        assert self.viewer.mean.text() == 'Mean: 24.6321'
        assert self.viewer.median.text() == 'Median: 22.0'
        assert self.viewer.min.text() == 'Min: 17'
        assert self.viewer.max.text() == 'Max: 114'
        assert self.viewer.x_value_lbl.text() == 'X: ????'
        assert self.viewer.y_value_lbl.text() == 'Y: ????'
        assert self.viewer.pixel_value_lbl.text() == 'Value: ????'
        assert not self.viewer.rgb_check_box.isChecked()

    def test_current_image(self):
        expected = self.test_set.current_image[self.test_set.channel]
        assert self.viewer.current_image == expected

    def test_refresh_ROI_text(self):
        self.viewer.min.setText("Min: 0")
        self.viewer.max.setText("Max: 100")
        self.viewer._refresh_ROI_text()
        assert self.viewer.min.text() == 'Min: 17'
        assert self.viewer.max.text() == 'Max: 114'

    def test_reset_ROI(self):
        self.viewer.min.setText("Min: 0")
        self.viewer.max.setText("Max: 100")
        self.viewer._reset_ROI()
        assert self.viewer.min.text() == 'Min: 17'
        assert self.viewer.max.text() == 'Max: 114'

    # TODO: When have RGB Image Test _disable_next_previous

    def test_reset_display_values(self):
        self.viewer.x_value_lbl.setText("X: 42")
        self.viewer.y_value_lbl.setText("Y: 42")
        self.viewer.pixel_value_lbl.setText("Value: 42")
        self.viewer._reset_display_values()
        assert self.viewer.x_value_lbl.text() == 'X: ????'
        assert self.viewer.y_value_lbl.text() == 'Y: ????'
        assert self.viewer.pixel_value_lbl.text() == 'Value: ????'

    def test_window_cascade(self, qtbot):
        """Tests the window cascade."""

        # Initial checks
        assert self.viewer._label_window is None
        assert self.viewer.open_label.isEnabled()

        # Open the label window and run appropriate checks
        qtbot.mouseClick(self.viewer.open_label, QtCore.Qt.LeftButton)
        qtbot.add_widget(self.viewer._label_window)
        assert self.viewer._label_window is not None
        assert self.viewer._label_window._finder_window is None
        assert self.viewer._label_window.is_open

        # Open the finder window and run appropriate checks
        qtbot.mouseClick(
            self.viewer._label_window.find_button, QtCore.Qt.LeftButton)
        assert self.viewer._label_window._finder_window is not None
        qtbot.add_widget(self.viewer._label_window._finder_window)
        assert not(self.viewer._label_window._finder_window.query_edit)

        # Hide windows and check to make sure they are hidden
        qtbot.mouseClick(
            self.viewer._label_window._finder_window.ok_button,
            QtCore.Qt.LeftButton)
        assert self.viewer._label_window._finder_window.isHidden()
        qtbot.mouseClick(
            self.viewer._label_window.cancel_button, QtCore.Qt.LeftButton)
        assert self.viewer._label_window.isHidden()

        # Test the ability for the parent (label) to hide the child (finder)
        qtbot.mouseClick(
            self.viewer.open_label, QtCore.Qt.LeftButton)
        qtbot.mouseClick(
            self.viewer._label_window.find_button, QtCore.Qt.LeftButton)
        assert not(self.viewer._label_window.isHidden())
        assert not(self.viewer._label_window._finder_window.isHidden())
        qtbot.mouseClick(
            self.viewer._label_window.cancel_button, QtCore.Qt.LeftButton)
        assert self.viewer._label_window.isHidden()
        assert self.viewer._label_window._finder_window.isHidden()

    def test_label_refresh(self, qtbot):
        """Tests the label display and refresh features."""
        qtbot.mouseClick(self.viewer.open_label, QtCore.Qt.LeftButton)
        qtbot.add_widget(self.viewer._label_window)
        label_contents = self.viewer._label_window.label_contents
        assert label_contents.toPlainText()[233:236] == "341"
        qtbot.mouseClick(self.viewer.next_image_btn, QtCore.Qt.LeftButton)
        label_contents = self.viewer._label_window.label_contents
        assert label_contents.toPlainText()[228:231] == "338"
        qtbot.mouseClick(self.viewer.previous_image_btn, QtCore.Qt.LeftButton)
        label_contents = self.viewer._label_window.label_contents
        assert label_contents.toPlainText()[233:236] == "341"

    def test_channels_dialog(self, qtbot):
        assert self.viewer.channels_window is None
        assert not self.viewer.channels_window_is_open
        assert self.viewer.channels_window_pos is None
        qtbot.add_widget(self.viewer)
        qtbot.mouseClick(self.viewer.channels_button, QtCore.Qt.LeftButton)
        assert self.viewer.channels_window is not None
        assert self.viewer.channels_window_is_open
        assert isinstance(self.viewer.channels_window, ChannelsDialog)
        assert self.viewer.channels_window_pos is None
        qtbot.add_widget(self.viewer.channels_window)
        new_pos = QtCore.QPoint(42, 24)
        self.viewer.channels_window.move(new_pos)
        qtbot.mouseClick(
            self.viewer.channels_window.close_button, QtCore.Qt.LeftButton)
        assert self.viewer.channels_window_pos is not None
        assert self.viewer.channels_window_pos == new_pos
        qtbot.mouseClick(self.viewer.channels_button, QtCore.Qt.LeftButton)
        self.viewer.channels_window.pos() == new_pos

    def test_apply_parameters(self, qtbot):
        """Test that images maintain their parameters"""
        self.viewer.save_parameters()
        image1 = self.viewer.current_image
        assert image1.sarr[0] == 0
        assert image1.sarr[255] == 255
        # assert image1.zoom == 1.0
        assert image1.rotation == 0.0
        assert image1.transforms == (False, False, False)
        assert image1.cuts == (17, 25)
        # Change parameters
        image1.sarr[0] = 42
        image1.sarr[255] = 13
        self.viewer.view_canvas.get_rgbmap().set_sarr(image1.sarr)
        # self.viewer.view_canvas.zoom_to(3)
        self.viewer.view_canvas.rotate(45)
        self.viewer.view_canvas.transform(False, True, False)
        self.viewer.view_canvas.cut_levels(24, 95)
        qtbot.mouseClick(self.viewer.next_image_btn, QtCore.Qt.LeftButton)
        # Test the second image parameters are None by defualt
        image2 = self.viewer.current_image
        # Test the view was reset to defualt paramters for the image
        assert self.viewer.view_canvas.get_rgbmap().get_sarr()[0] == 0
        assert self.viewer.view_canvas.get_rgbmap().get_sarr()[255] == 255
        # assert self.viewer.view_canvas.get_zoom() == 1.0
        assert self.viewer.view_canvas.get_rotation() == 0.0
        assert self.viewer.view_canvas.get_transforms() == (
            False, False, False
        )
        assert self.viewer.view_canvas.get_cut_levels() == (22, 26)
        # Test changing back to the first image maintains image1's parameters
        qtbot.mouseClick(self.viewer.previous_image_btn, QtCore.Qt.LeftButton)
        image1 = self.viewer.image_set.current_image[0]
        assert image1.sarr[0] == 42
        assert image1.sarr[255] == 13
        # assert image1.zoom == 3.0
        assert image1.rotation == 45.0
        assert image1.transforms == (False, True, False)
        assert image1.cuts == (24, 95)
        # Test that image2 stored its parameters
        image2 = self.viewer.image_set.images[1][0]
        assert image2.sarr[0] == 0
        assert image2.sarr[255] == 255
        # assert image2.zoom == 4.746031746031746
        assert image2.rotation == 0.0
        assert image2.transforms == (False, False, False)
        assert image2.cuts == (22, 26)

    def test_restore(self, qtbot):
        image1 = self.viewer.image_set.current_image[0]
        image1.sarr[0] = 42
        image1.sarr[255] = 13
        self.viewer.view_canvas.get_rgbmap().set_sarr(image1.sarr)
        # self.viewer.view_canvas.zoom_to(3)
        self.viewer.view_canvas.rotate(45)
        self.viewer.view_canvas.transform(False, True, False)
        self.viewer.view_canvas.cut_levels(24, 95)
        assert image1.sarr[0] == 42
        assert image1.sarr[255] == 13
        # assert image1.zoom == 3.0
        assert image1.rotation == 45.0
        assert image1.transforms == (False, True, False)
        assert image1.cuts == (24, 95)
        qtbot.mouseClick(self.viewer.restore_defaults, QtCore.Qt.LeftButton)
        self.viewer.save_parameters()
        assert image1.sarr[0] == 0
        assert image1.sarr[255] == 255
        # assert image1.zoom == 1.0
        assert image1.rotation == 0.0
        assert image1.transforms == (False, False, False)
        assert image1.cuts == (17, 25)

    def test_set_ROI_text(self, qtbot):
        """Test the ROI text to contain the correct values"""
        # Test Whole image ROI
        assert self.viewer.pixels.text() == '#Pixels: 32768'
        assert self.viewer.std_dev.text() == 'Std Dev: 16.100793'
        assert self.viewer.mean.text() == 'Mean: 24.6321'
        assert self.viewer.median.text() == 'Median: 22.0'
        assert self.viewer.min.text() == 'Min: 17'
        assert self.viewer.max.text() == 'Max: 114'
        # Test 2x2 random ROI
        # .5 values because these are the edge of the ROI pixels
        self.viewer.set_ROI_text(14.5, 512.5, 16.5, 514.5)
        assert self.viewer.pixels.text() == '#Pixels: 4'
        assert self.viewer.std_dev.text() == 'Std Dev: 1.000000'
        assert self.viewer.mean.text() == 'Mean: 23.0000'
        assert self.viewer.median.text() == 'Median: 23.0'
        assert self.viewer.min.text() == 'Min: 22'
        assert self.viewer.max.text() == 'Max: 24'

    def test_top_right_pixel_snap(self):
        test_snap_1 = self.viewer.top_right_pixel_snap(10, 5)
        assert test_snap_1[0] == 5.5
        assert test_snap_1[1]
        test_snap_2 = self.viewer.top_right_pixel_snap(-5, 5)
        assert not test_snap_2[1]
        test_snap_3 = self.viewer.top_right_pixel_snap(5.4, 10)
        assert test_snap_3[0] == 5.5
        assert test_snap_3[1]
        test_snap_4 = self.viewer.top_right_pixel_snap(5.5, 10)
        assert test_snap_4[0] == 5.5
        assert test_snap_4[1]
        test_snap_5 = self.viewer.top_right_pixel_snap(5.6, 10)
        assert test_snap_5[0] == 6.5
        assert test_snap_5[1]

    def test_bottom_left_pixel_snap(self):
        test_snap_1 = self.viewer.bottom_left_pixel_snap(-5, 5)
        assert test_snap_1[0] == -0.5
        assert test_snap_1[1]
        test_snap_2 = self.viewer.bottom_left_pixel_snap(10, 5)
        assert not test_snap_2[1]
        test_snap_3 = self.viewer.bottom_left_pixel_snap(5.4, 10)
        assert test_snap_3[0] == 4.5
        assert test_snap_3[1]
        test_snap_4 = self.viewer.bottom_left_pixel_snap(5.5, 10)
        assert test_snap_4[0] == 5.5
        assert test_snap_4[1]

    def test_left_right_bottom_top(self):
        test_coords_1 = self.viewer.left_right_bottom_top(1, 2, 1, 2)
        assert test_coords_1[0:4] == (1, 2, 1, 2)
        assert test_coords_1[4]
        assert test_coords_1[5]
        test_coords_2 = self.viewer.left_right_bottom_top(2, 1, 1, 2)
        assert test_coords_2[0:4] == (1, 2, 1, 2)
        assert not test_coords_2[4]
        assert test_coords_2[5]
        test_coords_3 = self.viewer.left_right_bottom_top(1, 2, 2, 1)
        assert test_coords_3[0:4] == (1, 2, 1, 2)
        assert test_coords_3[4]
        assert not test_coords_3[5]
        test_coords_4 = self.viewer.left_right_bottom_top(2, 1, 2, 1)
        assert test_coords_4[0:4] == (1, 2, 1, 2)
        assert not test_coords_4[4]
        assert not test_coords_4[5]
