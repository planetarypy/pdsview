#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pytest
import numpy as np
from qtpy import QtWidgets, QtCore
from matplotlib.lines import Line2D


from pdsview import pdsview, histogram

FILE_1 = os.path.join(
    'tests', 'mission_data', '1p190678905erp64kcp2600l8c1.img')
FILE_2 = os.path.join(
    'tests', 'mission_data', '2p129641989eth0361p2600r8m1.img')
FILE_3 = os.path.join(
    'tests', 'mission_data', '1p134482118erp0902p2600r8m1.img')

test_images = pdsview.ImageSet([FILE_1, FILE_2])
window = pdsview.PDSViewer(test_images)
image_view = window.view_canvas


def test_model_init():
    model = histogram.HistogramModel(image_view)
    assert model._image_view == image_view
    assert model._views == set()
    assert model._cut_low is None
    assert model._cut_high is None
    assert model._bins == 100


def test_model_image_view():
    image_view = window.view_canvas
    model = histogram.HistogramModel(image_view)
    model.image_view == image_view
    model.image_view == model._image_view
    # Test setter method
    image_view2 = pdsview.PDSViewer(pdsview.ImageSet([FILE_3])).view_canvas
    model.image_view = image_view2
    assert model.image_view == image_view2


def test_model_cut_low():
    model = histogram.HistogramModel(image_view)
    assert model.cut_low == model.view_cuts[0]
    assert model.cut_low == model._cut_low
    # Test Setting
    model.cut_low = 42
    assert model.cut_low == 42
    assert model._cut_low == 42
    assert model.view_cuts[0] == 42


def test_model_cut_high():
    model = histogram.HistogramModel(image_view)
    assert model.cut_high is model.view_cuts[1]
    assert model.cut_high == model._cut_high
    # Test Setting
    model.cut_high = 42
    assert model.cut_high == 42
    assert model._cut_high == 42
    assert model.view_cuts[1] == 42


def test_model_cuts():
    def test_new_cuts(new_cuts, model):
        model.cuts = new_cuts
        assert model.cuts == new_cuts
        assert model.cut_low == new_cuts[0]
        assert model.cut_high == new_cuts[1]
        assert model.view_cuts == new_cuts
    model = histogram.HistogramModel(image_view)
    assert model.cuts == model.view_cuts
    # Test Setter
    test_new_cuts((24, 42), model)
    test_new_cuts((20, 42), model)
    test_new_cuts((20, 40), model)
    with pytest.warns(UserWarning):
        model.cuts = 42, 24
    assert model.cuts == (24, 42)


def test_model_view_cuts():
    model = histogram.HistogramModel(image_view)
    assert model.view_cuts == image_view.get_cut_levels()


def test_bins():
    model = histogram.HistogramModel(image_view)
    assert model.bins == model._bins
    # Test Setter
    model.bins = 42
    assert model.bins == 42
    assert model.bins == model._bins


def test_model_data():
    model = histogram.HistogramModel(image_view)
    assert np.array_equal(model.data, image_view.get_image().data)


def test_model_register():
    model = histogram.HistogramModel(image_view)
    mock_view = QtWidgets.QWidget()
    model.register(mock_view)
    assert mock_view in model._views


def test_model_unregister():
    model = histogram.HistogramModel(image_view)
    mock_view = QtWidgets.QWidget()
    model.register(mock_view)
    assert mock_view in model._views
    model.unregister(mock_view)
    assert mock_view not in model._views


def test_model_restore():
    model = histogram.HistogramModel(image_view)
    assert model.cuts == model.view_cuts
    image_view.cut_levels(24, 42)
    model.cuts = 10, 100
    model.restore()
    assert model.cuts == model.view_cuts


def test_model__set_view_cuts():
    model = histogram.HistogramModel(image_view)
    model._cut_low = 24
    model._cut_high = 42
    model._set_view_cuts()
    assert model.view_cuts == (24, 42)


def test_controller_set_cut_low():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    test_controller.set_cut_low(24)
    assert model.cut_low == 24
    assert model.view_cuts[0] == 24


def test_controller_set_cut_high():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    test_controller.set_cut_high(42)
    assert model.cut_high == 42
    assert model.view_cuts[1] == 42


def test_controller_set_cuts():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    test_controller.set_cuts(10, 100)
    assert model.cut_low == 10
    assert model.cut_high == 100
    assert model.cuts == (10, 100)
    assert model.view_cuts == (10, 100)


def test_controller_set_bins():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    test_controller.set_bins(50)
    assert model.bins == 50


def test_controller_restore():
    model = histogram.HistogramModel(image_view)
    def_cuts = model.view_cuts
    test_hist = histogram.Histogram(model)
    test_controller = histogram.HistogramController(model, test_hist)
    model.cuts = 24, 42
    image_view.cut_levels(*def_cuts)
    test_controller.restore()
    assert model.cuts != (24, 42)
    assert model.cuts == def_cuts
    assert model.view_cuts == def_cuts


def test_histogram_init():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    assert test_hist.model == model
    assert test_hist in model._views
    assert test_hist.sizePolicy().hasHeightForWidth()
    assert test_hist._right_vline is None
    assert test_hist._left_vline is None


def test_histogram_set_vlines():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist._set_vlines()
    assert isinstance(test_hist._left_vline, Line2D)
    assert isinstance(test_hist._right_vline, Line2D)
    assert test_hist._left_vline.get_xdata()[0] == model.cut_low
    assert test_hist._right_vline.get_xdata()[0] == model.cut_high


def test_histogram_change_cut_low():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist._set_vlines()
    model._cut_low = 24
    test_hist.change_cut_low(draw=False)
    assert test_hist._left_vline.get_xdata()[0] == 24
    assert test_hist._right_vline.get_xdata()[0] == model.cut_high


def test_histogram_change_cut_high():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist._set_vlines()
    model._cut_high = 42
    test_hist.change_cut_high(draw=False)
    assert test_hist._right_vline.get_xdata()[0] == 42
    assert test_hist._left_vline.get_xdata()[0] == model.cut_low


def test_histogram_change_cuts():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist._set_vlines()
    model._cut_low = 24
    model._cut_high = 42
    test_hist.change_cuts()
    assert test_hist._left_vline.get_xdata()[0] == 24
    assert test_hist._right_vline.get_xdata()[0] == 42


def test_histogram_change_bins():
    model = histogram.HistogramModel(image_view)
    test_hist = histogram.Histogram(model)
    test_hist.set_data()
    assert model.bins == 100
    assert len(test_hist._ax.patches) == 100
    model._bins = 50
    test_hist.change_bins()
    assert len(test_hist._ax.patches) == 50


def get_xdata(ax, x):
    xdata, _ = ax.transform((x, 10))
    return xdata


# def test_histogram_move_line(qtbot):
    """Testing the move line is much more difficult than I thought
    Passing in the correct data points is very tough and I can't
    figure out exactly how to do so."""


def test_histogram_widget_change_cut_low():
    model = histogram.HistogramModel(image_view)
    test_hist_widget = histogram.HistogramWidget(model)
    new_cut_low = model.cut_low - 3
    model._cut_low = new_cut_low
    test_hist_widget.change_cut_low()
    assert float(test_hist_widget._cut_low_box.text()) == new_cut_low
    new_cut_low += 1.2
    model._cut_low = new_cut_low
    test_hist_widget.change_cut_low()
    assert float(test_hist_widget._cut_low_box.text()) == new_cut_low


def test_histogram_widget_change_cut_high():
    model = histogram.HistogramModel(image_view)
    test_hist_widget = histogram.HistogramWidget(model)
    new_cut_high = model.cut_high + 3
    model._cut_high = new_cut_high
    test_hist_widget.change_cut_high()
    assert float(test_hist_widget._cut_high_box.text()) == new_cut_high
    new_cut_high -= 1.2
    model._cut_high = new_cut_high
    test_hist_widget.change_cut_high()
    assert float(test_hist_widget._cut_high_box.text()) == new_cut_high


def test_histogram_widget_change_cuts():
    model = histogram.HistogramModel(image_view)
    test_hist_widget = histogram.HistogramWidget(model)
    new_cut_high = model.cut_high + 3
    model._cut_high = new_cut_high
    new_cut_low = model.cut_low - 3
    model._cut_low = new_cut_low
    test_hist_widget.change_cuts()
    assert float(test_hist_widget._cut_low_box.text()) == new_cut_low
    assert float(test_hist_widget._cut_high_box.text()) == new_cut_high
    new_cut_high -= 1.2
    model._cut_high = new_cut_high
    new_cut_low += 1.2
    model._cut_low = new_cut_low
    test_hist_widget.change_cuts()
    assert float(test_hist_widget._cut_low_box.text()) == new_cut_low
    assert float(test_hist_widget._cut_high_box.text()) == new_cut_high


def test_histogram_widget_change_bins():
    model = histogram.HistogramModel(image_view)
    test_hist_widget = histogram.HistogramWidget(model)
    new_bins = model.bins + 20
    model._bins = new_bins
    test_hist_widget.change_bins()
    assert int(test_hist_widget._bins_box.text()) == new_bins


def test_histogram_widget_keyPressEvent(qtbot):
    window.show()
    qtbot.addWidget(window.histogram_widget)
    qtbot.addWidget(window)
    # Change only cut low
    new_cut_low = window.histogram.cut_low - 3
    window.histogram_widget._cut_low_box.setText("%.3f" % (new_cut_low))
    qtbot.keyPress(window.histogram_widget, QtCore.Qt.Key_Return)
    assert window.histogram.cut_low == new_cut_low
    # Change only cut high
    new_cut_high = window.histogram.cut_high + 3
    window.histogram_widget._cut_high_box.setText("%.3f" % (new_cut_high))
    qtbot.keyPress(window.histogram_widget, QtCore.Qt.Key_Return)
    assert window.histogram.cut_high == new_cut_high
    # Change both cuts
    new_cut_low += 1.5
    new_cut_high -= 1.5
    window.histogram_widget._cut_low_box.setText("%.3f" % (new_cut_low))
    window.histogram_widget._cut_high_box.setText("%.3f" % (new_cut_high))
    qtbot.keyPress(window.histogram_widget, QtCore.Qt.Key_Return)
    assert window.histogram.cut_low == new_cut_low
    assert window.histogram.cut_high == new_cut_high
    # Change the bins
    new_bins = window.histogram.bins + 50
    window.histogram_widget._bins_box.setText("%d" % (new_bins))
    qtbot.keyPress(window.histogram_widget, QtCore.Qt.Key_Return)
    assert window.histogram.bins == new_bins
    assert window.histogram.cut_low == new_cut_low
    assert window.histogram.cut_high == new_cut_high
    # Change all
    new_cut_low += 1.5
    new_cut_high -= 1.5
    window.histogram_widget._cut_low_box.setText("%.3f" % (new_cut_low))
    window.histogram_widget._cut_high_box.setText("%.3f" % (new_cut_high))
    new_bins -= 25
    window.histogram_widget._bins_box.setText("%d" % (new_bins))
    qtbot.keyPress(window.histogram_widget, QtCore.Qt.Key_Return)
    assert window.histogram.bins == new_bins
    assert window.histogram.cut_low == new_cut_low
    assert window.histogram.cut_high == new_cut_high
