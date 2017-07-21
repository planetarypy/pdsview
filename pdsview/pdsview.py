#! /usr/bin/env python

import os
import sys
import math
import argparse
import warnings
from glob import glob
from functools import wraps

import numpy as np
from qtpy import QtWidgets, QtCore
from planetaryimage import PDS3Image
from ginga.BaseImage import BaseImage
from ginga.qtw.ImageViewCanvasQt import ImageViewCanvas

from .histogram import HistogramWidget, HistogramModel
from .channels_dialog import ChannelsDialog, ChannelsDialogModel
try:
    from . import label
except ImportError:
    from pdsview import label


app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication(sys.argv)


class ImageStamp(BaseImage):
    """A ginga BaseImage object that will be displayed in PDSViewer.

    Parameters
    ----------
    filepath: string
        A file and its relative path from the current working directory


    Attributes
    ----------
    image_name : string
        The filename of the filepath
    pds_image : planetaryimage object
        A planetaryimage object
    label : array
        The images label in an array
    cuts : tuple (int, int)
        The min and max pixel value scaling
    sarr : np array
        The color map of the array in an array
    zoom : float
        Zoom level of the image
    rotation : float
        The degrees the image is rotated
    transforms : tuple (bool, bool, bool)
        Whether the image is flipped across the x-axis, y-axis, or x/y is
        switched
    not_been_displayed : bool
        Whether the image has been displayed already
    """

    def __init__(self, filepath, name, pds_image, data_np, metadata=None,
                 logger=None):
        BaseImage.__init__(self, data_np=data_np, metadata=metadata,
                           logger=logger)
        self.set_data(data_np)
        with open(filepath, 'rb') as f:
            label_array = []
            for lineno, line in enumerate(f):
                line = line.decode().rstrip()
                label_array.append(line)
                if line.strip() == 'END':
                    break
        self.data = data_np
        self.image_name = name
        self.file_name = os.path.basename(filepath)
        self.pds_image = pds_image
        self.label = label_array
        self.cuts = None
        self.sarr = None
        self.zoom = None
        self.rotation = None
        self.transforms = None
        self.not_been_displayed = True

    def __repr__(self):
        return self.image_name


class ImageSet(object):
    """A set of ginga images to be displayed and methods to control the images.

    Parameters
    ----------
    filepaths: list
        A list of filepaths to pass through ImageStamp

    Attribute
    ---------
    images : list
        A list of ginga images with attributes set in ImageStamp that can be
        displayed in PDSViewer
    current_image : ImageStamp object
        The currently displayed image
    current_image_index : int
        Index value of the current image
    file_dict : dictionary
        dictionary of images list, makes accessing images by name easier
    channel : int
        Which channel in the image the view should be in
    next_prev_enabled : bool
        Whether the next and previous buttons should be enabled
    """

    def __init__(self, filepaths):
        # Remove any duplicate filepaths and sort the list alpha-numerically.
        filepaths = sorted(list(set(filepaths)))

        self._views = set()

        # Create image objects with attributes set in ImageStamp
        # These objects contain the data ginga will use to display the image
        self.images = []
        self.create_image_set(filepaths)
        self._current_image_index = 0
        self._channel = 0
        # self._last_channel = None
        self._x_value = 0
        self._y_value = 0
        self._pixel_value = (0, )
        self.use_default_text = True
        self.rgb = []
        if self.images:
            self.current_image = self.images[self.current_image_index]
        else:
            self.current_image = None

    def register(self, view):
        """Register a view with the model"""
        self._views.add(view)

    def unregister(self, view):
        """Unregister a view with the model"""
        self._views.remove(view)

    def create_image_set(self, filepaths):
        rgb = ['R', 'G', 'B']
        for filepath in filepaths:
            try:
                channels = []
                pds_image = PDS3Image.open(filepath)
                bands = pds_image.label['IMAGE']['BANDS']
                if bands == 3:
                    for n in range(bands):
                        name = os.path.basename(filepath) + '(%s)' % (rgb[n])
                        data = pds_image.image[:, :, n]
                        image = ImageStamp(
                            filepath=filepath, name=name, data_np=data,
                            pds_image=pds_image)
                        # self.file_dict[image.image_name] = image
                        channels.append(image)
                    self.images.append(channels)
                else:
                    name = os.path.basename(filepath)
                    data = pds_image.image
                    image = ImageStamp(
                        filepath=filepath, name=name, data_np=data,
                        pds_image=pds_image)
                    self.images.append([image])
                    # self.file_dict[image.image_name] = image
            except:
                warnings.warn(filepath + " cannnot be opened")

    @property
    def next_prev_enabled(self):
        """Set whether the next and previous buttons are enabled."""
        return len(self.images) > 1

    @property
    def current_image_index(self):
        return self._current_image_index

    @current_image_index.setter
    def current_image_index(self, index):
        while index >= len(self.images):
            index -= len(self.images)
        while index < 0:
            index += len(self.images)
        self._current_image_index = index
        self.current_image = self.images[index]
        self._channel = 0
        for view in self._views:
            view.display_image()

    @property
    def channel(self):
        return self._channel

    # @property
    # def last_channel(self):
    #     return self._last_channel

    @channel.setter
    def channel(self, new_channel):
        number_channels = len(self.current_image)
        if number_channels == 1:
            return
        self._previous_channel = self._channel
        self._channel = new_channel
        if self._channel == number_channels:
            self._channel = 0
        for view in self._views:
            view.display_image()

    @property
    def x_value(self):
        return self._x_value

    @x_value.setter
    def x_value(self, new_x_value):
        self._x_value = int(round(new_x_value, 0))
        for view in self._views:
            view.set_x_value_text()

    @property
    def x_value_text(self):
        return 'X: %d' % (self.x_value)

    @property
    def y_value(self):
        return self._y_value

    @y_value.setter
    def y_value(self, new_y_value):
        self._y_value = int(round(new_y_value, 0))
        for view in self._views:
            view.set_y_value_text()

    @property
    def y_value_text(self):
        return 'Y: %d' % (self.y_value)

    @property
    def pixel_value(self):
        return tuple([float(round(value, 3)) for value in self._pixel_value])

    @pixel_value.setter
    def pixel_value(self, new_pixel_value):
        if isinstance(new_pixel_value, (tuple, list, np.ndarray)):
            _new_pixel_value = [float(pixel) for pixel in new_pixel_value]
        else:
            _new_pixel_value = [float(new_pixel_value)]
        self._pixel_value = tuple(_new_pixel_value)
        for view in self._views:
            view.set_pixel_value_text()

    @property
    def pixel_value_text(self):
        current_image = self.current_image[self.channel]
        if current_image.ndim == 3:
            return 'R: %.3f G: %.3f B: %.3f' % (self.pixel_value)
        else:
            return 'Value: %.3f' % (self.pixel_value)

    def append(self, new_files, dipslay_first_new_image):
        """Append a new image to the images list if it is pds compatible"""
        self.create_image_set(new_files)
        if dipslay_first_new_image == len(self.images):
            return
        self.current_image_index = dipslay_first_new_image
        self.current_image = self.images[self.current_image_index]

    @property
    def bands_are_composite(self):
        r_band = self.rgb[0]
        # Use logic that if a=b and a=c then b=c
        return all([r_band.data.shape == band.data.shape for band in self.rgb])

    def _create_rgb_image_wrapper(func):
        @wraps(func)
        def wrapper(self):
            if not self.bands_are_composite:
                raise ValueError(
                    (
                        'The bands must all be the same shape in order to' +
                        'make a composite image'
                    )
                )
            else:
                return func(self)
        return wrapper

    @_create_rgb_image_wrapper
    def create_rgb_image(self):
        rgb_image = np.stack(
            [band.data for band in self.rgb],
            axis=-1
        )
        return rgb_image

    def ROI_data(self, left, bottom, right, top):
        """Calculate the data in the Region of Interest

        Parameters
        ----------

        left : float
            The x coordinate value of the left side of the Region of Interest
        bottom : float
            The y coordinate value of the bottom side of the Region of Interest
        right : float
            The x coordinate value of the right side of the Region of Interest
        bottom : float
            The y coordinate value of the top side of the Region of Interest

        Returns
        -------
        data : array
            The data within the Region of Interest

        """

        left = int(math.ceil(left))
        bottom = int(math.ceil(bottom))
        right = int(math.ceil(right))
        top = int(math.ceil(top))
        data = self.current_image[self.channel].cutout_data(
            left, bottom, right, top)
        return data

    def ROI_pixels(self, left, bottom, right, top):
        """Calculate the number of pixels in the Region of Interest

        Parameters
        ----------
        See ROI_data

        Returns
        -------
        pixels : int
            The number of pixels in the Region of Interest

        """

        pixels = (right - left) * (top - bottom)
        return pixels

    def ROI_std_dev(
            self, left=None, bottom=None, right=None, top=None, data=None):
        """Calculate the standard deviation in the Region of Interest

        Note
        ----
        If data is not provided, the left, bottom, right, and top parameters
        must be provided. Otherwise it will result in a TypeError.

        Parameters
        ----------
        left : Optional[float]
            The x coordinate value of the left side of the Region of Interest
        bottom : Optional[float]
            The y coordinate value of the bottom side of the Region of Interest
        right : Optional[float]
            The x coordinate value of the right side of the Region of Interest
        bottom : Optional[float]
            The y coordinate value of the top side of the Region of Interest
        data : Optional[array]
            The data within the Region of Interest

        Returns
        -------
        std_dev : float
            The standard deviation of the pixels in the Region of Interest

        """

        if data is None:
            data = self.ROI_data(left, bottom, right, top)
        std_dev = round(np.std(data), 6)
        return std_dev

    def ROI_mean(
            self, left=None, bottom=None, right=None, top=None, data=None):
        """Calculate the mean of the Region of Interest

        Parameters
        ----------
        See ROI_std_dev

        Note
        ----
        See ROI_std_dev

        Returns
        -------
        mean : float
            The mean pixel value of the Region of Interest

        """

        if data is None:
            data = self.ROI_data(left, bottom, right, top)
        mean = round(np.mean(data), 4)
        return mean

    def ROI_median(
            self, left=None, bottom=None, right=None, top=None, data=None):
        """Find the median of the Region of Interest

        Parameters
        ----------
        See ROI_std_dev

        Note
        ----
        See ROI_std_dev

        Returns
        -------
        median : float
            The median pixel value of the Region of Interest

        """

        if data is None:
            data = self.ROI_data(left, bottom, right, top)
        median = np.median(data)
        return median

    def ROI_min(
            self, left=None, bottom=None, right=None, top=None, data=None):
        """Find the minimum pixel value of the Region of Interest

        Parameters
        ----------
        See ROI_std_dev

        Note
        ----
        See ROI_std_dev

        Returns
        -------
        minimum : float
            The minimum pixel value of the Region of Interest

        """

        if data is None:
            data = self.ROI_data(left, bottom, right, top)
        minimum = np.nanmin(data)
        return minimum

    def ROI_max(
            self, left=None, bottom=None, right=None, top=None, data=None):
        """Find the maximum pixel value of the Region of Interest

        Parameters
        ----------
        See ROI_std_dev

        Note
        ----
        See ROI_std_dev

        Returns
        -------
        maximum : float
            The maximum pixel value of the Region of Interest

        """

        if data is None:
            data = self.ROI_data(left, bottom, right, top)
        maximum = np.nanmax(data)
        return maximum


class PDSController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def next_image(self):
        self.model.current_image_index += 1

    def previous_image(self):
        self.model.current_image_index -= 1

    def next_channel(self):
        self.model.channel += 1

    def previous_channel(self):
        self.model.channel -= 1

    def new_x_value(self, new_x):
        self.model.x_value = new_x

    def new_y_value(self, new_y):
        self.model.y_value = new_y

    def new_pixel_value(self, new_pixel_value):
        self.model.pixel_value = new_pixel_value

    def _populate_rgb(self, image_index):
        rgb = []
        number_of_images = len(self.model.images)
        while len(rgb) < 3:
            for band in self.model.images[image_index]:
                rgb.append(band)
                if len(rgb) == 3:
                    break
            at_end_of_image_list = image_index == (number_of_images - 1)
            image_index = 0 if at_end_of_image_list else image_index + 1
        return rgb

    def update_rgb(self):
        """Update the rgb list to have the 3 channels or the next 3 images"""
        self.model.rgb = []
        current_image = self.model.current_image
        image_is_not_rgb = len(current_image) < 3
        if image_is_not_rgb:
            self.model.rgb = self._populate_rgb(self.model.current_image_index)
        else:
            for band in current_image:
                self.model.rgb.append(band)


class PDSViewer(QtWidgets.QMainWindow):
    """A display of a single image with the option to view other images

    Parameters
    ----------
    image_set: list
        A list of ginga objects with attributes set in ImageStamp"""

    def __init__(self, image_set):
        super(PDSViewer, self).__init__()

        self.image_set = image_set
        self.image_set.register(self)
        self.controller = PDSController(self.image_set, self)

        # Set the sub window names here. This implementation will help prevent
        # the main window from spawning duplicate children. Even if the
        # duplication prevention is not set up for a window, this will be a
        # handy reference list of windows(or dialogs in most cases) that can
        # be spawned out of this window.
        self._label_window = None
        self._label_window_pos = None
        self.channels_window = None
        self.channels_window_is_open = False
        self.channels_window_pos = None

        self.view_canvas = ImageViewCanvas(render='widget')
        self.view_canvas.set_autocut_params('zscale')
        self.view_canvas.enable_autozoom('override')
        self.view_canvas.enable_autocuts('override')
        self.view_canvas.set_callback('drag-drop', self.drop_file)
        self.view_canvas.set_bg(0.5, 0.5, 0.5)
        self.view_canvas.ui_setActive(True)
        self.view_canvas.get_bindings().enable_all(True)
        # Activate left mouse click to display values
        self.view_canvas.set_callback('cursor-down', self.display_values)
        # Activate click and drag to update values
        self.view_canvas.set_callback('cursor-move', self.display_values)
        self.view_canvas.set_callback('draw-down', self.start_ROI)
        self.view_canvas.set_callback('draw-up', self.stop_ROI)
        self.view_canvas.enable_draw(True)
        self.view_canvas.set_drawtype('rectangle')

        main_layout = QtWidgets.QGridLayout()

        # self.open_label is need as an attribute to determine whether the user
        # should be able to open the label window. The other side of this
        # toggle is found in load_file().
        open_file = QtWidgets.QPushButton("Open File")
        open_file.clicked.connect(self.open_file)
        self.next_image_btn = QtWidgets.QPushButton("Next")
        self.next_image_btn.clicked.connect(self.next_image)
        self.next_image_btn.setEnabled(image_set.next_prev_enabled)
        self.previous_image_btn = QtWidgets.QPushButton("Previous")
        self.previous_image_btn.clicked.connect(self.previous_image)
        self.previous_image_btn.setEnabled(image_set.next_prev_enabled)
        self.open_label = QtWidgets.QPushButton("Label")
        self.open_label.clicked.connect(self.display_label)
        quit_button = QtWidgets.QPushButton("Quit")
        quit_button.clicked.connect(self.quit)
        self.rgb_check_box = QtWidgets.QCheckBox("RGB")
        self.rgb_check_box.stateChanged.connect(self.switch_rgb)
        self.next_channel_btn = QtWidgets.QPushButton('CH +')
        self.next_channel_btn.clicked.connect(self.next_channel)
        self.previous_channel_btn = QtWidgets.QPushButton('CH -')
        self.previous_channel_btn.clicked.connect(self.previous_channel)
        self.restore_defaults = QtWidgets.QPushButton("Restore Defaults")
        self.restore_defaults.clicked.connect(self.restore)
        self.channels_button = QtWidgets.QPushButton("Channels")
        self.channels_button.clicked.connect(self.channels_dialog)
        # Set Text so the size of the boxes are at an appropriate size
        self.x_value_lbl = QtWidgets.QLabel('X: #####')
        self.y_value_lbl = QtWidgets.QLabel('Y: #####')
        self.pixel_value_lbl = QtWidgets.QLabel(
            'R: ######, G: ###### B: ######')

        self.pixels = QtWidgets.QLabel('#Pixels: #######')
        self.std_dev = QtWidgets.QLabel(
            'Std Dev: R: ######### G: ######### B: #########')
        self.mean = QtWidgets.QLabel(
            'Mean: R: ######## G: ######## B: ########')
        self.median = QtWidgets.QLabel(
            'Median: R: ######## G: ######## B: ########')
        self.min = QtWidgets.QLabel('Min: R: ### G: ### B: ###')
        self.max = QtWidgets.QLabel('Max: R: ### G: ### B: ###')

        main_layout.setHorizontalSpacing(10)
        # Set format for each information box to be the same
        for info_box in (self.x_value_lbl, self.y_value_lbl,
                         self.pixel_value_lbl, self.pixels, self.std_dev,
                         self.mean, self.median, self.min, self.max):
            info_box.setFrameShape(QtWidgets.QFrame.Panel)
            info_box.setFrameShadow(QtWidgets.QFrame.Sunken)
            info_box.setLineWidth(3)
            info_box.setMidLineWidth(1)
            info_box.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)

        for main_box, second_box in ((self.std_dev, self.pixels),
                                     (self.mean, self.median),
                                     (self.min, self.max)):
            main_box.setMinimumSize(main_box.sizeHint())
            main_box.setMaximumSize(main_box.sizeHint())
            second_box.setMinimumSize(main_box.sizeHint())
            second_box.setMaximumSize(main_box.sizeHint())

        self.histogram = HistogramModel(self.view_canvas, bins=100)
        self.histogram_widget = HistogramWidget(self.histogram)
        min_width = self.histogram_widget.histogram.width()
        for widget in (open_file, self.next_image_btn, self.previous_image_btn,
                       self.channels_button, self.open_label,
                       self.restore_defaults, self.rgb_check_box,
                       self.x_value_lbl, self.y_value_lbl, quit_button,
                       self.next_channel_btn, self.previous_channel_btn,
                       self.pixel_value_lbl):
            widget.setMinimumWidth(min_width)
            widget.setMaximumWidth(min_width)
        fixed_size = self.pixel_value_lbl.sizeHint().width()
        self.x_value_lbl.setMinimumWidth(fixed_size / 2)
        self.x_value_lbl.setMaximumWidth(fixed_size / 2)
        self.y_value_lbl.setMinimumWidth(fixed_size / 2)
        self.y_value_lbl.setMaximumWidth(fixed_size / 2)
        column_spacing_x_y = 5
        self.pixel_value_lbl.setMinimumWidth(fixed_size + column_spacing_x_y)
        self.pixel_value_lbl.setMaximumWidth(fixed_size + column_spacing_x_y)

        main_layout.addWidget(open_file, 0, 0)
        main_layout.addWidget(quit_button, 0, 1)
        main_layout.addWidget(self.pixels, 0, 2)
        main_layout.addWidget(self.mean, 0, 3)
        main_layout.addWidget(self.min, 0, 4)
        main_layout.addWidget(self.previous_image_btn, 1, 0)
        main_layout.addWidget(self.next_image_btn, 1, 1)
        main_layout.addWidget(self.std_dev, 1, 2)
        main_layout.addWidget(self.median, 1, 3)
        main_layout.addWidget(self.max, 1, 4)
        main_layout.addWidget(self.previous_channel_btn, 2, 0)
        main_layout.addWidget(self.next_channel_btn, 2, 1)
        main_layout.addWidget(self.channels_button, 3, 0)
        main_layout.addWidget(self.open_label, 3, 1)
        main_layout.addWidget(self.restore_defaults, 4, 0)
        main_layout.addWidget(self.rgb_check_box, 4, 1)
        main_layout.addWidget(self.histogram_widget, 5, 0, 2, 2)
        x_y_layout = QtWidgets.QGridLayout()
        x_y_layout.setHorizontalSpacing(column_spacing_x_y)
        x_y_layout.addWidget(self.x_value_lbl, 0, 0)
        x_y_layout.addWidget(self.y_value_lbl, 0, 1)
        main_layout.addLayout(x_y_layout, 7, 0)
        main_layout.addWidget(self.pixel_value_lbl, 8, 0, 1, 2)
        main_layout.addWidget(self.view_canvas.get_widget(), 2, 2, 9, 4)

        main_layout.setRowStretch(9, 1)
        main_layout.setColumnStretch(5, 1)

        vw = QtWidgets.QWidget()
        self.setCentralWidget(vw)
        vw.setLayout(main_layout)

        self.view_canvas.set_desired_size(100, 100)

        if self.image_set.current_image:
            self.display_image()
            self._reset_display_values()

    @property
    def current_image(self):
        return self.image_set.current_image[self.image_set.channel]

    def display_image(self):
        self.controller.update_rgb()
        self._set_rgb_state()
        self._update_channels_image()
        self.view_canvas.set_image(self.current_image)
        if self.current_image.not_been_displayed:
            self.restore()
        else:
            self.apply_parameters(self.current_image, self.view_canvas)
        self.view_canvas.delayed_redraw()

        self.current_image.not_been_displayed = False

        self.histogram.set_data()

        self._disable_next_previous()

        self._reset_ROI()

        self._update_label()

        self.setWindowTitle(self.current_image.image_name)

    def _refresh_ROI_text(self):
        self.stop_ROI(self.view_canvas, None, None, None)

    def _reset_ROI(self):
        if len(self.view_canvas.objects) > 1:
            self._refresh_ROI_text()
            self.view_canvas.update_canvas()
        else:
            self.set_ROI_text(
                0, 0, self.current_image.width, self.current_image.height)

    def _update_channels_image(self):
        if self.channels_window:
            self.channels_window.change_image()

    def _set_rgb_state(self):
        state = self.rgb_check_box.checkState()
        self.switch_rgb(state)

    def _disable_next_previous(self):
        if len(self.image_set.current_image) < 3:
            self.next_channel_btn.setEnabled(False)
            self.previous_channel_btn.setEnabled(False)

    def _renew_display_values(self):
        try:
            data_x = self.image_set.x_value
            data_y = self.image_set.y_value
            self.display_values(self.view_canvas, None, data_x, data_y)
        except ValueError:
            pass

    def _reset_display_values(self):
        self.x_value_lbl.setText('X: ????')
        self.y_value_lbl.setText('Y: ????')
        if self.current_image.ndim == 3:
            self.pixel_value_lbl.setText('R: ???? G: ???? B: ????')
        elif self.current_image.ndim == 2:
            self.pixel_value_lbl.setText('Value: ????')

    def _change_wrapper(image_was_changed):
        # To be more explicit later
        channel_was_changed = not image_was_changed

        def decorator(func):
            @wraps(func)
            def wrapper(self):
                self.save_parameters()
                result = func(self)
                if image_was_changed:
                    self._reset_display_values()
                elif channel_was_changed:
                    self._renew_display_values()
                return result
            return wrapper
        return decorator

    @_change_wrapper(True)
    def next_image(self):
        self.controller.next_image()

    @_change_wrapper(True)
    def previous_image(self):
        self.controller.previous_image()

    @_change_wrapper(False)
    def next_channel(self):
        self.controller.next_channel()

    @_change_wrapper(False)
    def previous_channel(self):
        self.controller.previous_channel()

    def display_rgb_image(self):
        rgb_image = self.image_set.create_rgb_image()
        self.current_image.set_data(rgb_image)
        self.next_channel_btn.setEnabled(False)
        self.previous_channel_btn.setEnabled(False)

    def _undo_display_rgb_image(self):
        self.current_image.set_data(self.current_image.data)
        if len(self.image_set.current_image) == 3:
            self.next_channel_btn.setEnabled(True)
            self.previous_channel_btn.setEnabled(True)
        if self.channels_window:
            self.channels_window.rgb_check_box.setCheckState(
                QtCore.Qt.Unchecked)

    def switch_rgb(self, state):
        """Display rgb image when rgb box is checked, single band otherwise"""
        if state == QtCore.Qt.Checked:
            if self.channels_window:
                self.channels_window.rgb_check_box.setCheckState(
                    QtCore.Qt.Checked)
            else:
                if self.image_set.bands_are_composite:
                    self.display_rgb_image()
                else:
                    print("Images must be the same size")
                    print("Use the channels button to select the bands")
                    self.rgb_check_box.setCheckState(QtCore.Qt.Unchecked)
        elif state == QtCore.Qt.Unchecked:
            self._undo_display_rgb_image()
        if len(self.view_canvas.objects) >= 1:
            self._refresh_ROI_text()

        if self.view_canvas.get_image() is not None:
            self.histogram.set_data()

    def _point_is_in_image(self, point):
        data_x, data_y = point
        height, width = self.current_image.shape[:2]
        in_width = data_x >= -0.5 and data_x <= (width + 0.5)
        in_height = data_y >= -0.5 and data_y <= (height + 0.5)
        return in_width and in_height

    def _set_point_in_image(self, point):
        data_x, data_y = point
        image = self.view_canvas.get_image()
        self.controller.new_x_value(data_x)
        self.controller.new_y_value(data_y)
        x, y = self.image_set.x_value, self.image_set.y_value
        self.controller.new_pixel_value(image.get_data_xy(x, y))

    def _set_point_out_of_image(self):
        x, y = self.view_canvas.get_last_data_xy()
        self.controller.new_x_value(x)
        self.controller.new_y_value(y)
        if self.current_image.ndim == 3:
            self.controller.new_pixel_value((0, 0, 0))
        elif self.current_image.ndim == 2:
            self.controller.new_pixel_value(0)

    def set_x_value_text(self):
        self.x_value_lbl.setText(self.image_set.x_value_text)

    def set_y_value_text(self):
        self.y_value_lbl.setText(self.image_set.y_value_text)

    def set_pixel_value_text(self):
        self.pixel_value_lbl.setText(self.image_set.pixel_value_text)

    def display_values(self, view_canvas, button, data_x, data_y):
        "Display the x, y, and pixel value when the mouse is pressed and moved"
        point = (data_x, data_y)
        if self._point_is_in_image(point):
            self._set_point_in_image(point)
        else:
            self._set_point_out_of_image()

    def display_label(self):
        """Display the label over the image"""
        # Utilizing the sub window variables to check if the label window has
        # been opened before. If not, the window is initialized.
        if self._label_window is None:
            self._label_window = label.LabelView(self)
        self._label_window.is_open = True
        self._label_window.show()
        self._label_window.activateWindow()

    def _update_label(self):
        # Update label
        self.image_label = self.current_image.label

        # This checks to see if the label window exists and is open. If so,
        # this resets the label field so that the label being displayed is the
        # label for the current product. The label does not reset its position.
        if self._label_window is not None:
            pos = self._label_window.pos()
            label_text = '\n'.join(self.image_label)
            self._label_window.label_contents.setText(label_text)
            if self._label_window.is_open:
                self._label_window.cancel()
                self._label_window.move(pos)
                self._label_window.show()
                self._label_window.is_open = True
                self._label_window.activateWindow()

    def open_file(self):
        """Open a new image file from a file explorer"""
        file_name = QtWidgets.QFileDialog()
        file_name.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        new_files = file_name.getOpenFileNames(self)[0]
        if new_files:
            if self.image_set.current_image:
                self.save_parameters()
            first_new_image = len(self.image_set.images)
            self.image_set.append(new_files, first_new_image)
            # If there are no new images, don't continue
            if first_new_image == len(self.image_set.images):
                warnings.warn("The image(s) chosen are not PDS compatible")
                return
            self.next_image_btn.setEnabled(
                self.image_set.next_prev_enabled)
            self.previous_image_btn.setEnabled(
                self.image_set.next_prev_enabled)
            self._display_image()
        else:
            # integrate with logger
            print("No file selected!")
            return

    def channels_dialog(self):
        """Display the channels dialog box"""
        if not self.channels_window:
            self.channels_window = ChannelsDialog(ChannelsDialogModel(self))
        self.channels_window_is_open = True
        if self.channels_window_pos:
            self.channels_window.move(self.channels_window_pos)
        self.channels_window.show()

    def save_parameters(self):
        """Save the view parameters on the image"""
        last_image = self.image_set.current_image[self.image_set.channel]
        last_image.sarr = self.view_canvas.get_rgbmap().get_sarr()
        last_image.zoom = self.view_canvas.get_zoom()
        last_image.rotation = self.view_canvas.get_rotation()
        last_image.transforms = self.view_canvas.get_transforms()
        last_image.cuts = self.view_canvas.get_cut_levels()

    def apply_parameters(self, image, view):
        """Display image with the images parameters"""
        if image.sarr is None:
            pass
        else:
            view.get_rgbmap().set_sarr(image.sarr)
        if image.zoom is None:
            pass
        else:
            view.zoom_to(image.zoom)
        if image.rotation is None:
            pass
        else:
            view.rotate(image.rotation)
        if image.transforms is None:
            pass
        else:
            flip_x = image.transforms[0]
            flip_y = image.transforms[1]
            switch_xy = image.transforms[2]
            view.transform(flip_x, flip_y, switch_xy)
        if image.cuts is None:
            pass
        else:
            loval, hival = image.cuts
            view.cut_levels(loval, hival, True)

    def restore(self):
        """Restore image to the default settings"""
        self.view_canvas.get_rgbmap().reset_sarr()
        self.view_canvas.enable_autocuts('on')
        self.view_canvas.auto_levels()
        self.view_canvas.enable_autocuts('override')
        self.view_canvas.rotate(0.0)
        # The default transform/rotation of the image will be image specific so
        # transform bools will change in the future
        self.view_canvas.transform(False, False, False)
        self.view_canvas.zoom_fit()
        self.histogram.restore()

    def start_ROI(self, view_canvas, button, data_x, data_y):
        """Ensure only one Region of Interest (ROI) exists at a time

        Note
        ----
        This method is called when the right mouse button is pressed. Even
        though the arguments are not used, they are necessary to catch the
        right mouse button press event.

        Parameters
        ----------
        view_canvas : ImageViewCanvas object
            The view that displays the image
        button : Qt.RightButton
            The right mouse button
        data_x : float
            The x-value of the location of the right button
        data_y : float
            The y-value of the location of the right button

        """

        if len(view_canvas.objects) > 1:
            self.delete_ROI()

    def stop_ROI(self, view_canvas, button, data_x, data_y):
        """Create a Region of Interest (ROI)

        When drawing stops (release of the right mouse button), the ROI border
        snaps to inclusive pixel (see top_right_pixel_snap and
        bottom_left_pixel_snap). The ROI's information is set as an attributes
        of the current image (see calculate_ROI_info).

        Note
        ----
        This method is called when the right mouse button is released. Even
        though only the view_canvas argument is used, they are all necessary to
        catch the right mouse button release event.

        Parameters
        ----------
        See start_ROI parameters

        """

        # If there are no draw objects, stop
        current_image = self.image_set.current_image[self.image_set.channel]
        if len(view_canvas.objects) == 1:
            self.set_ROI_text(0, 0, current_image.width, current_image.height)
            return

        draw_obj = view_canvas.objects[1]

        # Retrieve the left, right, top, & bottom x and y values
        roi = self.left_right_bottom_top(
            draw_obj.x1, draw_obj.x2, draw_obj.y1, draw_obj.y2)
        left_x, right_x, bot_y, top_y, x2_is_right, y2_is_top = roi

        # Single right click deletes any ROI & sets the whole image as the ROI
        if left_x == right_x and bot_y == top_y:
            self.set_ROI_text(0, 0, current_image.width, current_image.height)
            self.delete_ROI()
            return

        # Determine if the ROI is outside the image.
        max_height = current_image.height
        max_width = current_image.width
        top_y, top_in_image = self.top_right_pixel_snap(top_y, max_height)
        bot_y, bot_in_image = self.bottom_left_pixel_snap(bot_y, max_height)
        right_x, right_in_image = self.top_right_pixel_snap(right_x, max_width)
        left_x, left_in_image = self.bottom_left_pixel_snap(left_x, max_width)

        # If the entire ROI is outside the ROI, delete the ROI and set the ROI
        # to the whole image
        if not any(left_in_image, right_in_image, top_in_image, bot_in_image):
            self.set_ROI_text(0, 0, current_image.width, current_image.height)
            self.delete_ROI()
            return

        # Snap the ROI to the edge of the image if it is outside the image
        if y2_is_top:
            draw_obj.y2 = top_y
            draw_obj.y1 = bot_y
        else:
            draw_obj.y1 = top_y
            draw_obj.y2 = bot_y
        if x2_is_right:
            draw_obj.x2 = right_x
            draw_obj.x1 = left_x
        else:
            draw_obj.x1 = right_x
            draw_obj.x2 = left_x

        # Calculate the ROI information

        self.set_ROI_text(left_x, bot_y, right_x, top_y)

    def top_right_pixel_snap(self, ROI_side, image_edge):
        """Snaps the top or right side of the ROI to the inclusive pixel

        Parameters
        ----------
        ROI_side : float
            Either the ROI's top-y or right-x value
        image_edge : float
            The top or right edge of the image

        Returns
        -------
        ROI_side : float
            The x or y value of the right or top ROI side respectively
        side_in_image : bool
            True if the side is in the image, False otherwise

        """

        # If the top/right ROI edge is outside the image, reset the top/right
        # ROI side value to the edge
        if ROI_side > image_edge:
            ROI_side = image_edge + .5
            side_in_image = True

        # If the right side is to the left of the image or the top side is
        # below the image, then the entire ROI is outside the image
        elif ROI_side < 0.0:
            side_in_image = False

        # If the top/right ROI values is inside the image, snap it the edge
        # of the inclusive pixel. If the value is already on the edge, pass
        else:
            if ROI_side - int(ROI_side) == .5:
                pass
            else:
                ROI_side = round(ROI_side) + .5
            side_in_image = True
        return (ROI_side, side_in_image)

    def bottom_left_pixel_snap(self, ROI_side, image_edge):
        """Snaps the bottom or left side of the ROI to the inclusive pixel

        Parameters
        ----------

        ROI_side : float
            Either the ROI's bottom-y or left-x value
        image_edge : float
            The top or right edge of the image

        Returns
        -------
        ROI_side : float
            The x or y value of the left or bottom ROI side respectively
        side_in_image : bool
            True if the side is in the image, False otherwise

        """

        # If the bottom/left ROI edge is outside the image, reset the
        # bottom/left ROI side value to the bottom/left edge (-0.5)
        if ROI_side < 0.0:
            ROI_side = -0.5
            side_in_image = True

        # If the left side is to the right of the image or the bottom side is
        # above the image, then the entire ROI is outside the image
        elif ROI_side > image_edge:
            side_in_image = False

        # If the bottom/left ROI values is inside the image, snap it the edge
        # of the inclusive pixel. If the value is already on the edge, pass
        else:
            if ROI_side - int(ROI_side) == .5:
                pass
            else:
                ROI_side = round(ROI_side) - 0.5
            side_in_image = True
        return (ROI_side, side_in_image)

    def left_right_bottom_top(self, x1, x2, y1, y2):
        """Determines the values for the left, right, bottom, and top vertices

        Parameters
        ----------
        x1 : float
            The x-value of where the right cursor was clicked
        x2 : float
            The x-value of where the right cursor was released
        y1 : float
            The y-value of where the right cursor was clicked
        y2 : float
            The y-value of where the right cursor was released

        Returns
        -------
        left_x : float
            The x-value of the left side of the ROI
        right_x : float
            The x-value of the right side of the ROI
        bot_y : float
            The y-value of the bottom side of the ROI
        top_y : float
            The y-value of the top side of the ROI
        x2_is_right : bool
            True if the x2 input is the right side of the ROI, False otherwise
        y2_is_top : bool
            True if the y2 input is the top side of the ROI, False otherwise

        """

        if x2 > x1:
            right_x = x2
            left_x = x1
            x2_is_right = True
        else:
            right_x = x1
            left_x = x2
            x2_is_right = False
        if y2 > y1:
            top_y = y2
            bot_y = y1
            y2_is_top = True
        else:
            top_y = y1
            bot_y = y2
            y2_is_top = False
        return (left_x, right_x, bot_y, top_y, x2_is_right, y2_is_top)

    def delete_ROI(self):
        """Deletes the Region of Interest"""
        try:
            self.view_canvas.deleteObject(self.view_canvas.objects[1])
        except:
            return

    def set_ROI_text(self, left, bottom, right, top):
        """Set the text of the ROI information boxes

        When the image has three bands (colored), the ROI value boxes will
        display the values for each band.

        Parameters
        ----------
        left : float
            The x coordinate value of the left side of the ROI
        bottom : float
            The y coordinate value of the bottom side of the ROI
        right : float
            The x coordinate value of the right side of the ROI
        bottom : float
            The y coordinate value of the top side of the ROI

        """

        data = self.image_set.ROI_data(
            left, bottom, right, top)
        # Calculate the number of pixels in the ROI
        ROI_pixels = self.image_set.ROI_pixels(left, bottom, right, top)
        self.pixels.setText('#Pixels: %d' % (ROI_pixels))
        if data.ndim == 2:
            # 2 band image is a gray scale image
            self.set_ROI_gray_text(data)
        elif data.ndim == 3:
            # Three band image is a RGB colored image
            try:
                self.set_ROI_RGB_text(data)
            except:
                # If the ROI does not contain values for each band, treat the
                # ROI like a gray scale image
                self.set_ROI_gray_text(data)

    def set_ROI_gray_text(self, data):
        """Set the values for the ROI in the text boxes for a gray image

        Parameters
        ----------
        data : array
            The data from the Region of Interest

        """

        ROI_std_dev = self.image_set.ROI_std_dev(data=data)
        ROI_mean = self.image_set.ROI_mean(data=data)
        ROI_median = self.image_set.ROI_median(data=data)
        ROI_min = self.image_set.ROI_min(data=data)
        ROI_max = self.image_set.ROI_max(data=data)
        self.std_dev.setText('Std Dev: %.6f' % (ROI_std_dev))
        self.mean.setText('Mean: %.4f' % (ROI_mean))
        self.median.setText('Median: %.1f' % (ROI_median))
        self.min.setText('Min: %d' % (ROI_min))
        self.max.setText('Max: %d' % (ROI_max))

    def set_ROI_RGB_text(self, data):
        """Set the values for the ROI in the text boxes for a RGB image

        Parameters
        ----------
        data : array
            The data from the Region of Interest

        """

        calc = self.image_set
        ROI_stdev = [calc.ROI_std_dev(data=data[:, :, n]) for n in range(3)]
        ROI_mean = [calc.ROI_mean(data=data[:, :, n]) for n in range(3)]
        ROI_median = [calc.ROI_median(data=data[:, :, n]) for n in range(3)]
        ROI_max = [int(calc.ROI_max(data=data[:, :, n])) for n in range(3)]
        ROI_min = [int(calc.ROI_min(data=data[:, :, n])) for n in range(3)]
        self.std_dev.setText(
            'Std Dev: R: %.6f G: %.6f B: %.6f' % (tuple(ROI_stdev)))
        self.mean.setText(
            'Mean: R: %s G: %s B: %s' % (tuple(ROI_mean)))
        self.median.setText(
            'Median: R: %s G: %s B: %s' % (tuple(ROI_median)))
        self.max.setText(
            'Max: R: %s G: %s B: %s' % (tuple(ROI_max)))
        self.min.setText(
            'Min: R: %s G: %s B: %s' % (tuple(ROI_min)))

    def drop_file(self, pdsimage, paths):
        """This function is not yet supported"""
        # file_name = paths[0]
        # self.load_file(file_name)
        pass

    def quit(self, *args):
        """Close pdsview"""
        if self._label_window is not None:
            self._label_window.cancel()
        if self.channels_window:
            self.channels_window.hide()
        self.close()


def pdsview(inlist=None):
    """Run pdsview from python shell or command line with arguments

    Parameters
    ----------
    inlist : list
        A list of file names/paths to display in the pdsview

    Examples
    --------

    From the command line:

    To view all images from current directory

    pdsview

    To view all images in a different directory

    pdsview path/to/different/directory/

    This is the same as:

    pdsview path/to/different/directory/*

    To view a specific image or types of images

    pdsview 1p*img

    To view images from multiple directories:

    pdsview * path/to/other/directory/

    From the (i)python command line:

    >>> from pdsview.pdsview import pdsview
    >>> pdsview()
    Displays all of the images from current directory
    >>> pdsview('path/to/different/directory')
    Displays all of the images in the different directory
    >>> pdsview ('1p*img')
    Displays all of the images that follow the glob pattern
    >>> pdsview ('a1.img, b*.img, example/path/x*img')
    You can display multiple images, globs, and paths in one window by
    separating each item by a command
    >>> pdsview (['a1.img, b3.img, c1.img, d*img'])
    You can also pass in a list of files/globs
    """
    files = []
    if isinstance(inlist, list):
        if inlist:
            for item in inlist:
                files += arg_parser(item)
        else:
            files = glob('*')
    elif isinstance(inlist, str):
        names = inlist.split(',')
        for name in names:
            files = files + arg_parser(name.strip())
    elif inlist is None:
        files = glob('*')

    image_set = ImageSet(files)
    w = PDSViewer(image_set)
    w.resize(780, 770)
    w.show()
    w.view_canvas.zoom_fit()
    app.setActiveWindow(w)
    sys.exit(app.exec_())


def arg_parser(args):
    if os.path.isdir(args):
        files = glob(os.path.join('%s' % (args), '*'))
    elif args:
        files = glob(args)
    else:
        files = glob('*')
    return files


def cli():
    """Give pdsview ability to run from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file', nargs='*',
        help="Input filename or glob for files with certain extensions"
        )
    args = parser.parse_args()
    pdsview(args.file)
