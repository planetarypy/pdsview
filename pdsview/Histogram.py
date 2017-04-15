import warnings

import numpy as np
from matplotlib.figure import Figure
from ginga.qtw.QtHelp import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg

from WarningTimer import WarningTimer, WarningTimerModel


class HistogramModel(object):

    def __init__(self, image_view, cut_low=None, cut_high=None, bins=100):

        self._image_view = image_view
        self._listeners = set()
        self._cut_low = cut_low
        self._cut_high = cut_high
        self._bins = bins

    @property
    def image_view(self):
        return self._image_view

    @property
    def cut_low(self):
        return self._cut_low

    @property
    def cut_high(self):
        return self._cut_high

    @property
    def bins(self):
        return self._bins

    @property
    def cuts(self):
        if self.cut_low is not None and self.cut_high is not None:
            cut_low, cut_high = self.cut_low, self.cut_high
        else:
            cut_low, cut_high = self.view_cuts
        return cut_low, cut_high

    @property
    def view_cuts(self):
        return self.image_view.get_cut_levels()

    @property
    def data(self):
        return self.image_view.get_image().data

    def register(self, listener):
        self._listeners.add(listener)

    def unregister(self, listener):
        self._listeners.remove(listener)

    def set_image_view(self, image_view):
        self._image_view = image_view

    def set_cut_low(self, cut_low):
        self._cut_low = cut_low
        self._set_view_cuts()
        self._change_cut_low()

    def set_cut_high(self, cut_high):
        self._cut_high = cut_high
        self._set_view_cuts()
        self._change_cut_high()

    def set_cuts(self, cut_low, cut_high):
        if cut_low > cut_high:
            message = (
                "The low cut cannot be bigger than the high cut. " +
                "Switching cuts.")
            self.warn("Cut Warning", message)
            cut_low, cut_high = cut_high, cut_low

        diff_cut_low = cut_low != self.cut_low
        diff_cut_high = cut_high != self.cut_high
        if diff_cut_low and diff_cut_high:
            self._cut_low = cut_low
            self._cut_high = cut_high
            self._set_view_cuts()
            self._change_cuts()
        elif diff_cut_low:
            self.set_cut_low(cut_low)
        elif diff_cut_high:
            self.set_cut_high(cut_high)

    def reset_cuts(self):
        self._cut_low, self._cut_high = self.view_cuts
        self._change_cuts()

    def set_bins(self, bins):
        if bins == self._bins:
            return
        self._bins = bins
        self._change_bins()

    def set_data(self):
        for listener in self._listeners:
            listener.set_data()

    def restore(self):
        cut_low, cut_high = self.view_cuts
        self.set_cuts(cut_low, cut_high)

    def warn(self, title, message):
        warnings.warn(message)
        for listener in self._listeners:
            warned = listener.warn(title, message)
            if warned:
                break

    def _set_view_cuts(self):
        self.image_view.cut_levels(self.cut_low, self.cut_high)

    def _change_cut_low(self):
        for listener in self._listeners:
            listener.change_cut_low()

    def _change_cut_high(self):
        for listener in self._listeners:
            listener.change_cut_high()

    def _change_cuts(self):
        for listener in self._listeners:
            listener.change_cuts()

    def _change_bins(self):
        for listener in self._listeners:
            listener.change_bins()


class HistogramWidget(QtGui.QWidget):

    def __init__(self, model):

        super(HistogramWidget, self).__init__()
        self.model = model
        self.model.register(self)
        self._histogram = Histogram(model)
        self._cut_low_label = QtGui.QLabel("Cut Low:")
        self._cut_low_box = QtGui.QLineEdit()
        self._cut_high_label = QtGui.QLabel("Cut High:")
        self._cut_high_box = QtGui.QLineEdit()
        self._bins_label = QtGui.QLabel("Bins:")
        self._bins_box = QtGui.QLineEdit()
        layout = self._create_layout()
        self.setLayout(layout)
        self.change_bins()
        self.change_cuts()

    def _create_layout(self):
        layout = QtGui.QVBoxLayout()
        cut_boxes_layout = QtGui.QGridLayout()
        cut_boxes_layout.addWidget(self._cut_low_label, 0, 0)
        cut_boxes_layout.addWidget(self._cut_low_box, 0, 1)
        cut_boxes_layout.addWidget(self._cut_high_label, 0, 2)
        cut_boxes_layout.addWidget(self._cut_high_box, 0, 3)
        cut_boxes_layout.addWidget(self._bins_label, 0, 4)
        cut_boxes_layout.addWidget(self._bins_box, 0, 5)
        cut_boxes = QtGui.QWidget()
        cut_boxes.setLayout(cut_boxes_layout)
        layout.addWidget(self._histogram)
        layout.addWidget(cut_boxes)

        return layout

    def change_cut_low(self):
        self._cut_low_box.setText("%.3f" % (self.model.cut_low))

    def change_cut_high(self):
        self._cut_high_box.setText("%.3f" % (self.model.cut_high))

    def change_cuts(self):
        cut_low, cut_high = self.model.cuts
        self._cut_low_box.setText("%.3f" % (cut_low))
        self._cut_high_box.setText("%.3f" % (cut_high))

    def change_bins(self):
        self._bins_box.setText("%d" % (self.model.bins))

    def keyPressEvent(self, event):
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

            self.model.set_cuts(cut_low, cut_high)
            self.model.set_bins(bins)

    # def restore(self):
    #     self.model.restore()

    def warn(self, title, message):
        WarningTimer(WarningTimerModel(self, title, message)).exec_()
        return True

    def set_data(self):
        pass


class Histogram(FigureCanvasQTAgg):

    def __init__(self, model):
        fig = Figure(figsize=(2, 2), dpi=100)
        fig.subplots_adjust(
            left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0,
            hspace=0.0)
        super(Histogram, self).__init__(fig)

        self.model = model
        self.model.register(self)
        self._figure = fig
        policy = self.sizePolicy()
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        self.setMinimumSize(self.size())
        self._ax = fig.add_subplot(111)
        self._ax.set_axis_bgcolor('black')
        self._left_vline = None
        self._right_vline = None

    def change_cut_low(self, draw=True):
        if self._left_vline is None:
            return
        self._left_vline.set_xdata([self.model.cut_low, self.model.cut_low])
        if draw:
            self.draw()

    def change_cut_high(self, draw=True):
        if self._right_vline is None:
            return
        self._right_vline.set_xdata([self.model.cut_high, self.model.cut_high])
        if draw:
            self.draw()

    def change_cuts(self):
        self.change_cut_low(draw=False)
        self.change_cut_high(draw=False)
        self.draw()

    def change_bins(self):
        self.set_data(False)

    def set_data(self, reset_vlines=True):
        self._ax.cla()
        self._left_vline = None
        self._right_vline = None
        self._ax.hist(
            self.model.data.flatten(), self.model.bins, color='white')
        self._set_vlines(reset_vlines)
        self.draw()

    def _move_line(self, event):
        if not event.inaxes or event.button != 1:
            return
        x = event.xdata
        cut_low, cut_high = self.model.cuts
        if np.abs(x - self.model.cut_low) < np.abs(x - self.model.cut_high):
            self.model.set_cut_low(x)
        else:
            self.model.set_cut_high(x)

    def _set_vlines(self, reset=True):
        if reset:
            self.model.reset_cuts()
        cut_low, cut_high = self.model.cuts
        self._left_vline = self._ax.axvline(
            cut_low, color='r', linewidth=2)
        self._right_vline = self._ax.axvline(
            cut_high, color='r', linewidth=2)
        self._figure.canvas.mpl_connect('motion_notify_event', self._move_line)
        self._figure.canvas.mpl_connect('button_press_event', self._move_line)

    def warn(self, title, message):
        return False
