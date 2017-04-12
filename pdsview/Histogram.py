from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from ginga.qtw.QtHelp import QtGui, QtCore
import numpy as np


class HistogramWidget(QtGui.QWidget):

    def __init__(self, view=None):

        super(HistogramWidget, self).__init__()
        self.view = view
        self.histogram = Histogram(self, view)
        self.cut_low_label = QtGui.QLabel("Cut Low:")
        self.cut_low = QtGui.QLineEdit()
        self.cut_high_label = QtGui.QLabel("Cut High:")
        self.cut_high = QtGui.QLineEdit()
        layout = self.create_layout()
        self.setLayout(layout)

    def create_layout(self):
        layout = QtGui.QVBoxLayout()
        cut_boxes_layout = QtGui.QGridLayout()
        cut_boxes_layout.addWidget(self.cut_low_label, 0, 0)
        cut_boxes_layout.addWidget(self.cut_low, 0, 1)
        cut_boxes_layout.addWidget(self.cut_high_label, 0, 2)
        cut_boxes_layout.addWidget(self.cut_high, 0, 3)
        cut_boxes = QtGui.QWidget()
        cut_boxes.setLayout(cut_boxes_layout)
        layout.addWidget(self.histogram)
        layout.addWidget(cut_boxes)

        return layout

    def set_cut_boxes(self):
        cut_low, cut_high = self.histogram.cuts
        self.cut_low.setText("%.3f" % (cut_low))
        self.cut_high.setText("%.3f" % (cut_high))

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            try:
                cut_high = float(self.cut_high.text())
                cut_low = float(self.cut_low.text())
                self.histogram.change_cuts(cut_low, cut_high)
                self.set_cut_boxes()
            except ValueError:
                print("The cut low and high values must be numbers.")


class Histogram(FigureCanvasQTAgg):

    def __init__(self, parent=None, view=None):
        fig = Figure(figsize=(2, 2), dpi=100)
        fig.subplots_adjust(
            left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0,
            hspace=0.0)
        super(Histogram, self).__init__(fig)

        self.control = parent
        self.view = view
        self.figure = fig
        policy = self.sizePolicy()
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        self.setMinimumSize(self.size())
        self.ax = fig.add_subplot(111)
        self.ax.set_axis_bgcolor('black')
        self.left_vline = None
        self.right_vline = None
        self.leftx = None
        self.rightx = None

    @property
    def cuts(self):
        if self.leftx is not None and self.rightx is not None:
            cut_low, cut_high = self.leftx, self.rightx
        else:
            cut_low, cut_high = self.view.get_cut_levels()
        return cut_low, cut_high

    def change_cuts(self, cut_low=None, cut_high=None):
        if cut_low is None and cut_high is None:
            return
        if cut_low == self.leftx and cut_high == self.rightx:
            return
        cut_low = self.leftx if cut_low is None else cut_low
        cut_high = self.rightx if cut_high is None else cut_high
        self.leftx = cut_low
        self.rightx = cut_high
        self.left_vline.set_xdata([cut_low, cut_low])
        self.right_vline.set_xdata([cut_high, cut_high])
        self.view.cut_levels(cut_low, cut_high)
        self.control.set_cut_boxes()
        self.draw()

    def set_data(self, data):
        self.ax.cla()
        self.ax.hist(data.flatten(), 100, color='white')
        self.set_vlines()
        self.control.set_cut_boxes()
        self.draw()

    def move_line(self, event):
        if not event.inaxes or event.button != 1:
            return
        X = event.xdata
        cut_low, cut_high = self.cuts
        if np.abs(X - self.leftx) < np.abs(X - self.rightx):
            self.left_vline.set_xdata([X, X])
            cut_low = X
        else:
            self.right_vline.set_xdata([X, X])
            cut_high = X
        self.change_cuts(cut_low, cut_high)

    def set_vlines(self):
        cut_low, cut_high = self.view.get_cut_levels()
        self.left_vline = self.ax.axvline(
            cut_low, color='r', linewidth=2)
        self.right_vline = self.ax.axvline(
            cut_high, color='r', linewidth=2)
        self.figure.canvas.mpl_connect('motion_notify_event', self.move_line)
        self.figure.canvas.mpl_connect('button_press_event', self.move_line)
        self.leftx = cut_low
        self.rightx = cut_high
