#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import pytest
from qtpy import QtWidgets

from pdsview import warningtimer


def test_model_init():
    test_timer = warningtimer.WarningTimerModel(None, "Title", "Message")
    assert test_timer._title == "Title"
    assert test_timer._message == "Message"
    assert test_timer._time_to_wait == 3
    assert test_timer.parent is None
    assert len(test_timer._views) == 0

    test_timer2 = warningtimer.WarningTimerModel(
        None, "Title2", "Message2", 10)
    assert test_timer2._title == "Title2"
    assert test_timer2._message == "Message2"
    assert test_timer2._time_to_wait == 10
    assert test_timer2.parent is None


def test_model_title():
    test_timer = warningtimer.WarningTimerModel(None, "Title", "Message")
    assert test_timer.title == "Title"
    test_timer.title = "New Title"
    assert test_timer.title == "New Title"


def test_model_message():
    test_timer = warningtimer.WarningTimerModel(None, "Title", "Message")
    assert test_timer.message == "Message"
    test_timer.message = "New Message"
    assert test_timer.message == "New Message"


def test_model_time_to_wait():
    test_timer = warningtimer.WarningTimerModel(None, "Title", "Message")
    assert test_timer.time_to_wait == 3
    test_timer.time_to_wait = 10
    assert test_timer.time_to_wait == 10


def test_model_test():
    test_timer = warningtimer.WarningTimerModel(None, "Title", "Message")
    assert test_timer.text == "Message\n\n Closing in 3 seconds"
    test_timer.time_to_wait -= 1
    assert test_timer.text == "Message\n\n Closing in 2 seconds"
    test_timer.time_to_wait -= 2
    test_timer.message = "New Message"
    assert test_timer.text == "New Message\n\n Closing in 0 seconds"


def test_controller_minus_one_seond():
    test_model = warningtimer.WarningTimerModel(None, "Title", "Message")
    test_controller = warningtimer.WarningTimerController(test_model, None)
    assert test_model.time_to_wait == 3
    assert test_controller._model.time_to_wait == 3
    test_controller.minus_one_second()
    assert test_controller._model.time_to_wait == 2
    assert test_model.time_to_wait == 2


def test_warningtimer_one_second_passed(qtbot):
    test_model = warningtimer.WarningTimerModel(None, "Title", "Message")
    test_view = warningtimer.WarningTimer(test_model, start_timer=False)
    test_view.show()
    qtbot.addWidget(test_view)
    assert test_model.time_to_wait == 3
    test_view.one_second_passed()
    assert test_model.time_to_wait == 2


def test_warningtimer_one_second_passed2(qtbot):
    test_model = warningtimer.WarningTimerModel(None, "Title", "Message")
    test_view = warningtimer.WarningTimer(test_model, start_timer=False)
    test_view.show()
    qtbot.addWidget(test_view)
    assert test_model.time_to_wait == 3
    assert test_view.text() == test_model.text
    # Test that one second passed will eventully call change text
    test_view.one_second_passed()
    assert test_model.time_to_wait == 2
    assert test_view.text() == test_model.text
    test_model._message = "New Message"
    test_view.change_text()
    assert test_view.text() == "New Message\n\n Closing in 2 seconds"


@pytest.mark.skipif(sys.platform == 'darwin', reason="No titles on macOS")
def test_warningtimer_change_title(qtbot):
    test_model = warningtimer.WarningTimerModel(None, "Title", "Message")
    test_view = warningtimer.WarningTimer(test_model, start_timer=False)
    test_view.show()
    qtbot.addWidget(test_view)
    assert test_view.windowTitle() == "Title"
    test_model._title = "New Title"
    test_view.change_title()
    test_view.windowTitle() == "New Title"


def test_warningtimer_close_by_timer(qtbot):
    test_model = warningtimer.WarningTimerModel(None, "Title", "Message", 1)
    test_view = warningtimer.WarningTimer(test_model, start_timer=False)
    test_view.show()
    qtbot.addWidget(test_view)
    assert test_view.isVisible()
    test_view.start_timer()
    qtbot.waitUntil(lambda: test_model.time_to_wait < 0, 3000)
    assert not test_view.isVisible()
    assert test_view.result() == QtWidgets.QDialog.Accepted
