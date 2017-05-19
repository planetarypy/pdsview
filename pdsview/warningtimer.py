from qtpy import QtWidgets, QtCore


class WarningTimerModel(object):
    """Model for Warning Boxes that close after a certain amount of time

    Parameters
    ----------
    parent
        The parent of the QMessageBox
    title : :obj:`str`
        The title of the window
    message : :obj:`str`
        The warning message
    time_to_wait : :obj:`int`
        The amount of time in seconds to wait. 3 seconds by default

    Attributes
    ----------
    parent
        The parent of the QMessageBox
    """

    def __init__(self, parent, title, message, time_to_wait=3):
        self._views = set()
        self.parent = parent
        self._title = title
        self._message = message
        self._time_to_wait = time_to_wait

    @property
    def title(self):
        """The warning window title

        Setting the title will notify the views to change the window title
        """
        return self._title

    @title.setter
    def title(self, new_title):
        self._title = new_title
        for view in self._views:
            view.change_title()

    @property
    def message(self):
        """The warning message to be displayed

        Setting the message will notify the views to change the message
        """
        return self._message

    @message.setter
    def message(self, new_message):
        self._message = new_message
        for view in self._views:
            view.chanage_text()

    @property
    def time_to_wait(self):
        """The amount of time in seconds to wait until the window closes

        Setting the time will notify the views to either close if the time is
        less than 0 or adjust the text to show how much time is left to wait
        """
        return self._time_to_wait

    @time_to_wait.setter
    def time_to_wait(self, time_to_wait):
        self._time_to_wait = time_to_wait
        if self.time_to_wait < 0:
            self.close_views()
        else:
            for view in self._views:
                view.change_text()

    @property
    def text(self):
        """The message with the amount of time until the window closes"""
        time_text = "\n\n Closing in %d seconds" % (self.time_to_wait)
        return self.message + time_text

    def register(self, view):
        """Register a view with the model"""
        self._views.add(view)

    def unregister(self, view):
        """Unregister a view with the model"""
        self._view.remove(view)

    def close_views(self):
        """Close all the views (called when the time has run out)"""
        for view in self._views:
            view.close_view()


class WarningTimerController(object):
    """The Warning Timer Controller

    Parameters
    ----------
    model : :class:`WarningTimerModel`
        The Warning Timer Model
    view : :class:`QtWidgets.QMessageBox`
        A message box with a :class:`WarningTimerModel` model
    """

    def __init__(self, model, view):
        self._model = model
        self._view = view

    def minus_one_second(self):
        """Subtract a second from the time to wait"""
        self._model.time_to_wait -= 1


class WarningTimer(QtWidgets.QMessageBox):
    """A Warning Message Box that closes after some time

    Parameters
    ----------
    model : :class:`WarningTimerModel`
        The Warning Timer Model

    Attributes
    ----------
    model : :class:`WarningTimerModel`
        The Warning Timer Model
    control : :class:`WarningTimerController`
        The controller
    timer : :class:`QtCore.QTimer`
        The timer
    """

    def __init__(self, model, start_timer=True):
        super(WarningTimer, self).__init__(model.parent)
        self.model = model
        self.control = WarningTimerController(self.model, self)
        self.model.register(self)
        self.change_text()
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.one_second_passed)
        if start_timer:
            self.start_timer()
        self.setWindowTitle(self.model.title)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.setIcon(QtWidgets.QMessageBox.Warning)

    def start_timer(self):
        self.timer.start()

    def one_second_passed(self):
        """After a second, subtract from the time_to_wait"""
        self.control.minus_one_second()

    def change_text(self):
        """Set the text to the text given by the model"""
        self.setText(self.model.text)

    def change_title(self):
        """Change the title to the model's title"""
        self.setWindowTitle(self.model.title)

    def close_view(self):
        """Close the Warning Box"""
        self.close()

    def closeEvent(self, event):
        self.timer.stop()
        self.accept()
        event.accept()
