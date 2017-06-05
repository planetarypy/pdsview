import warnings

import numpy as np
from matplotlib.figure import Figure
from qtpy import QtWidgets, QtCore
from qtpy import QT_VERSION

from .warningtimer import WarningTimer, WarningTimerModel
qt_ver = int(QT_VERSION[0])
if qt_ver == 4:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
elif qt_ver == 5:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class HistogramModel(object):
    """Model for a Histogram which can apply cut levels to an image

    Any View that utilizes this model must define the following methods:
    ``set_data``, ``change_cut_low``, ``change_cut_high``, ``change_cuts``,
    ``warn``, and ``change_bins``. The ``warn`` method must return a boolean
    and if more than one view utilizes this model, you should consider only
    one actually creating a warning box and return ``True`` while the others
    just return ``False``.

    Parameters
    ----------
    image_view : :class:`ImageViewCanvas`
        The image view canvas
    cut_low ::obj:`float`
        The lower cut level
    cut_high : :obj:`float`
        The higher cut level
    bins : :obj:`int`
        The number of bins the histogram uses
    """

    def __init__(self, image_view, cut_low=None, cut_high=None, bins=100):

        self._image_view = image_view
        self._views = set()
        self._cut_low = cut_low
        self._cut_high = cut_high
        self._bins = bins

    @property
    def image_view(self):
        """:class:`ImageViewCanvas` The image view canvas

        Setting the image view will reset the data
        """
        return self._image_view

    @image_view.setter
    def image_view(self, image_view):
        self._image_view = image_view
        self.set_data()

    @property
    def cut_low(self):
        """:obj:`float` The lower cut level

        Setting the low cut value will adjust the cut values in the image view
        and notify the views that the low cut value changed
        """
        if self._cut_low is None:
            self._cut_low = self.view_cuts[0]
        return self._cut_low

    @cut_low.setter
    def cut_low(self, cut_low):
        self._cut_low = cut_low
        self._set_view_cuts()
        self._change_cut_low()

    @property
    def cut_high(self):
        """:obj:`float` The higher cut level

        Setting the high cut value will adjust the cut values in the image view
        and notify the views that the high cut value changed."""
        if self._cut_high is None:
            self._cut_high = self.view_cuts[1]
        return self._cut_high

    @cut_high.setter
    def cut_high(self, cut_high):
        self._cut_high = cut_high
        self._set_view_cuts()
        self._change_cut_high()

    @property
    def bins(self):
        """:obj:`int` The number of bins the histogram uses

        Setting the bins will notify the views that the bins have changed
        """
        return self._bins

    @bins.setter
    def bins(self, bins):
        if bins == self._bins:
            return
        self._bins = bins
        self._change_bins()

    @property
    def cuts(self):
        """:obj:`tuple` The lower and higher cut levels. If the lower and
        higher cut levels are not set, use the image_view cut levels

        Setting the cuts will adjust the cut levels in the image viewer and
        notify the views that the cuts have changed. The low cut must be
        less than the high cut, otherwise they will be switched to satisfy
        that condition.
        """
        if self.cut_low is not None and self.cut_high is not None:
            cut_low, cut_high = self.cut_low, self.cut_high
        else:
            cut_low, cut_high = self.view_cuts
        return cut_low, cut_high

    @cuts.setter
    def cuts(self, cuts):
        cut_low, cut_high = cuts
        if cut_low > cut_high:
            message = (
                "The low cut cannot be bigger than the high cut. " +
                "Switching cuts.")
            self.warn("Cut Warning", message)
            cut_low, cut_high = cut_high, cut_low

        diff_cut_low = cut_low != self.cut_low
        diff_cut_high = cut_high != self.cut_high

        if diff_cut_low and diff_cut_high:
            self._cut_low, self._cut_high = cut_low, cut_high
            self._set_view_cuts()
            self._change_cuts()
        elif diff_cut_low:
            self.cut_low = cut_low
        elif diff_cut_high:
            self.cut_high = cut_high

    @property
    def view_cuts(self):
        """:obj:`tuple` The image_view cut levels"""
        cut_low, cut_high = self.image_view.get_cut_levels()
        return cut_low, cut_high

    @property
    def data(self):
        """:class:`ndarray` The current image data"""
        return self.image_view.get_image().get_data()

    def register(self, view):
        """Register a view with the model

        Parameters
        ----------
        view : :class:`QtWidgets.QWidget`
            A view that utilizes this model
        """
        self._views.add(view)

    def unregister(self, view):
        """Unregister a view with the model

        Parameters
        ----------
        view : :class:`QtWidgets.QWidget`
            A view that utilizes this model
        """
        self._views.remove(view)

    def set_data(self):
        """Set the data the histogram is to display"""
        for view in self._views:
            view.set_data()

    def restore(self):
        """Restore the cut levels"""
        cut_low, cut_high = self.view_cuts
        self.cuts = cut_low, cut_high

    def warn(self, title, message):
        """Display a warning box

        Each view must define a ``warn`` method that returns a boolean value:
        True when a warning box is displayed and False when a warning
        box not displayed. Only one display box will be displayed. This is
        because multiple views should not have different handling for the same
        errors.
        """
        warnings.warn(message)
        for view in self._views:
            warned = view.warn(title, message)
            if warned:
                break

    def _set_view_cuts(self):
        """Set the image view cut levels"""
        self.image_view.cut_levels(self.cut_low, self.cut_high)

    def _change_cut_low(self):
        """Notfiy the views to that the low cut level was changed"""
        for view in self._views:
            view.change_cut_low()

    def _change_cut_high(self):
        """Notify the views the high cut level was changed"""
        for view in self._views:
            view.change_cut_high()

    def _change_cuts(self):
        """Notify the views the cut levels were changed"""
        for view in self._views:
            view.change_cuts()

    def _change_bins(self):
        """Notify the views the number of bins were changed"""
        for view in self._views:
            view.change_bins()


class HistogramController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def set_cut_low(self, cut_low):
        self.model.cut_low = cut_low

    def set_cut_high(self, cut_high):
        self.model.cut_high = cut_high

    def set_cuts(self, cut_low, cut_high):
        self.model.cuts = cut_low, cut_high

    def set_bins(self, bins):
        self.model.bins = bins

    def restore(self):
        self.model.restore()


class HistogramWidget(QtWidgets.QWidget):
    """View to display the histogram with text boxes for cuts and bins

    Parameters
    ----------
    model : :class:`HistogramModel`

    Attributes
    ----------
    model : :class:`HistogramModel`
        The view's model
    """

    def __init__(self, model):

        super(HistogramWidget, self).__init__()
        self.model = model
        self.model.register(self)
        self.controller = HistogramController(self.model, self)
        self.histogram = Histogram(model)
        self._cut_low_label = QtWidgets.QLabel("Cut Low:")
        self._cut_low_box = QtWidgets.QLineEdit()
        self._cut_high_label = QtWidgets.QLabel("Cut High:")
        self._cut_high_box = QtWidgets.QLineEdit()
        self._bins_label = QtWidgets.QLabel("Bins:")
        self._bins_box = QtWidgets.QLineEdit()
        layout = self._create_layout()
        self.setLayout(layout)
        self.change_bins()
        self.change_cuts()

    def _create_layout(self):
        layout = QtWidgets.QVBoxLayout()
        cut_boxes_layout = QtWidgets.QGridLayout()
        cut_boxes_layout.addWidget(self._cut_low_label, 0, 0)
        cut_boxes_layout.addWidget(self._cut_low_box, 0, 1)
        cut_boxes_layout.addWidget(self._cut_high_label, 0, 2)
        cut_boxes_layout.addWidget(self._cut_high_box, 0, 3)
        cut_boxes_layout.addWidget(self._bins_label, 0, 4)
        cut_boxes_layout.addWidget(self._bins_box, 0, 5)
        cut_boxes = QtWidgets.QWidget()
        cut_boxes.setLayout(cut_boxes_layout)
        layout.addWidget(self.histogram)
        layout.addWidget(cut_boxes)

        return layout

    def change_cut_low(self):
        """Set the low cut box text"""
        self._cut_low_box.setText("%.3f" % (self.model.cut_low))

    def change_cut_high(self):
        """Set the high cut box text"""
        self._cut_high_box.setText("%.3f" % (self.model.cut_high))

    def change_cuts(self):
        """Set the low and high cut boxes' text"""
        cut_low, cut_high = self.model.cuts
        self._cut_low_box.setText("%.3f" % (cut_low))
        self._cut_high_box.setText("%.3f" % (cut_high))

    def change_bins(self):
        """Change the bins box text"""
        self._bins_box.setText("%d" % (self.model.bins))

    def keyPressEvent(self, event):
        """When the enter button is pressed, adjust the cut levels and bins"""
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            try:
                cut_low = float(self._cut_low_box.text())
                cut_high = float(self._cut_high_box.text())
            except ValueError:
                self.warn(
                    "Cuts Warning",
                    "The cut low and high values must be numbers.")
                self.change_cuts()
                return

            try:
                bins_text = self._bins_box.text()
                bins = int(bins_text)
            except ValueError:
                message = (
                    "The number of bins must be a integer." +
                    "Attempting to round down to nearest integer")
                try:
                    bins = int(float(bins_text))
                except ValueError:
                    message = ("The number of bins must be a number. " +
                               "Specifically, an integer.")
                    self.warn("Bins Warning", message)
                    self.change_bins()
                    return

            self.controller.set_cuts(cut_low, cut_high)
            self.controller.set_bins(bins)

    # def restore(self):
    #     self.model.restore()

    def warn(self, title, message):
        """Displayed a timed message box the warning"""
        WarningTimer(WarningTimerModel(self, title, message)).exec_()
        return True

    def set_data(self):
        pass


class Histogram(FigureCanvasQTAgg):
    """The Histogram View

    Parameters
    ----------
    model : :class:`HistogramModel`
        The view's model

    Attributes
    ----------
    model : :class:`HistogramModel`
        The view's model
    """

    def __init__(self, model):
        fig = Figure(figsize=(2, 2), dpi=100)
        fig.subplots_adjust(
            left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0,
            hspace=0.0)
        super(Histogram, self).__init__(fig)

        self.model = model
        self.model.register(self)
        self.controller = HistogramController(self.model, self)
        self._figure = fig
        policy = self.sizePolicy()
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        self.setMinimumSize(self.size())
        self._ax = fig.add_subplot(111)
        self._ax.set_facecolor('black')
        self._left_vline = None
        self._right_vline = None

    def change_cut_low(self, draw=True):
        """Change the position of the left line to the low cut level"""
        if self._left_vline is None:
            return
        self._left_vline.set_xdata([self.model.cut_low, self.model.cut_low])
        if draw:
            self.draw()

    def change_cut_high(self, draw=True):
        """Change the position of the right line to the high cut level"""
        if self._right_vline is None:
            return
        self._right_vline.set_xdata([self.model.cut_high, self.model.cut_high])
        if draw:
            self.draw()

    def change_cuts(self):
        """Change the position of the left & right lines to respective cuts"""
        self.change_cut_low(draw=False)
        self.change_cut_high(draw=False)
        self.draw()

    def change_bins(self):
        """Adjust the number of bins without adjusting the lines"""
        self.set_data(False)

    def set_data(self, reset_vlines=True):
        """Set the histogram's data

        Parameters
        ----------
        reset_vlines : :obj:`bool`
            Reset the vertical lines to the default cut levels if True,
            otherwise False. True by default
        """
        self._ax.cla()
        self._left_vline = None
        self._right_vline = None
        self._ax.hist(
            self.model.data.flatten(), self.model.bins, color='white')
        self._set_vlines(reset_vlines)
        self.draw()

    def _move_line(self, event):
        # The left mouse button must be down to adjust the cut levels
        if not event.inaxes or event.button != 1:
            return
        x = event.xdata
        cut_low, cut_high = self.model.cuts
        # Adjust the line that is closer to the point
        if np.abs(x - self.model.cut_low) < np.abs(x - self.model.cut_high):
            self.controller.set_cut_low(x)
        else:
            self.controller.set_cut_high(x)

    def _set_vlines(self, reset=True):
        if reset:
            self.model.restore()
        cut_low, cut_high = self.model.cuts
        self._left_vline = self._ax.axvline(
            cut_low, color='r', linewidth=2)
        self._right_vline = self._ax.axvline(
            cut_high, color='r', linewidth=2)
        self._figure.canvas.mpl_connect('motion_notify_event', self._move_line)
        self._figure.canvas.mpl_connect('button_press_event', self._move_line)

    def warn(self, title, message):
        return False
