from ginga.qtw.QtHelp import QtGui, QtCore


class WarningTimerModel(object):

    def __init__(self, parent, title, message, time_to_wait=3):
        self._listeners = set()
        self.parent = parent
        self.title = title
        self.message = message
        self.time_to_wait = time_to_wait
        self.text = None
        self.setText()

    def register(self, listener):
        self._listeners.add(listener)

    def unregister(self, listener):
        self._listener.remove(listener)

    def minusOneSecond(self):
        self.time_to_wait -= 1
        if self.time_to_wait < 0:
            self.closeViews()
        else:
            self.setText()

    def closeViews(self):
        for listener in self._listeners:
            listener.closeView()

    def setText(self):
        time_text = "\n\n Closing in %d seconds" % (self.time_to_wait)
        self.text = self.message + time_text
        for listener in self._listeners:
            listener.changeText()


class WarningTimer(QtGui.QMessageBox):

    def __init__(self, model):
        super(WarningTimer, self).__init__(model.parent)
        self.model = model
        self.model.register(self)
        self.changeText()
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.oneSecondPassed)
        self.timer.start()
        self.setWindowTitle(self.model.title)
        self.setStandardButtons(QtGui.QMessageBox.Ok)
        self.setIcon(QtGui.QMessageBox.Warning)

    def oneSecondPassed(self):
        self.model.minusOneSecond()

    def changeText(self):
        self.setText(self.model.text)

    def closeView(self):
        self.timer.stop()
        self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
