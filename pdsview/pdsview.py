#! /usr/bin/env python
#
# example1_qt.py -- Simple, configurable FITS viewer.
#
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c)  Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import sys
import logging
import PDSImage
import label
import labelError

from ginga.qtw.QtHelp import QtGui, QtCore
from ginga.qtw.ImageViewCanvasQt import ImageViewCanvas

STD_FORMAT = '%(asctime)s | %(levelname)1.1s | %(filename)s:%(lineno)d (%(funcName)s) | %(message)s'


class PDSViewer(QtGui.QMainWindow):

    def __init__(self, logger):
        super(PDSViewer, self).__init__()
        self.logger = logger

        self.image = ""

#       Set the subwindow names here. This implementation will help prevent the
#       main window from spawning duplicate children. Even if the duplication
#       prevention is not set up for a window, this will be a handy reference
#       list of windows(or dialogues in most cases) that can be spawned out of
#       this window.
        self._labelErrorWindow = None
        self._labelWindow = None
        self.imageFlag = 0

        self.pdsView = ImageViewCanvas(self.logger, render='widget')
        self.pdsView.enable_autocuts('on')
        self.pdsView.set_autocut_params('zscale')
        self.pdsView.enable_autozoom('on')
        self.pdsView.set_callback('drag-drop', self.drop_file)
        self.pdsView.set_bg(0.5, 0.5, 0.5)
        self.pdsView.ui_setActive(True)

        self.pdsView.get_bindings().enable_all(True)

        w = self.pdsView.get_widget()
        w.resize(768, 768)

        vbox = QtGui.QVBoxLayout()
        vbox.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))
        vbox.setSpacing(1)
        vbox.addWidget(w, stretch=1)

        hbox = QtGui.QHBoxLayout()
        self.hboxlayout = QtGui.QHBoxLayout()
        hbox.setContentsMargins(QtCore.QMargins(4, 2, 4, 2))

        openFile = QtGui.QPushButton("Open File")
        openFile.clicked.connect(self.open_file)
        self.openLabel = QtGui.QPushButton("Label")
        self.openLabel.clicked.connect(self.label)
        self.openLabel.setEnabled(False)
        quitButton = QtGui.QPushButton("Quit")
        quitButton.clicked.connect(self.quit)

        hbox.addStretch(1)
        for button in (openFile, self.openLabel, quitButton):
            hbox.addWidget(button, stretch=0)

        hw = QtGui.QWidget()
        hw.setLayout(hbox)
        vbox.addWidget(hw, stretch=0)
        self.vbox = vbox
        self.hbox = hbox
        self.w = w

        vw = QtGui.QWidget()
        self.setCentralWidget(vw)
        vw.setLayout(vbox)

    def label(self):
#       Utilizing the subwindow variables to check if the label window has
#       been opened before. If not, the window is initialized.
        self.imageLabel = self.image.pds_image.labelview
        if self._labelWindow == None:
            self._labelWindow = label.LabelView(self)
            pos  = self.frameGeometry().topLeft()
        self._labelWindow.isOpen = True
        self._labelWindow.show()
        self._labelWindow.activateWindow()

#   I did not like how the implementation of the try/except pair, as I am going
#   to focus on implementing preventative validation to avoid situations like
#   this as opposed to post-mortem validation.
#
#    def label(self):
#        try:
#            print self.image
#            self.imageLabel = self.image.pds_image.labelview
#            if(self.imageFlag == 0):
#                print type(self.image)
#                print self.image
#
#           Utilizing the subwindow variables to check if the label window has
#           been opened before. If not, the window is initialized.
#            if self._labelWindow == None:
#                self._labelWindow = label.LabelView(self)
#                pos  = self.frameGeometry().topLeft()
#            self._labelWindow.isOpen = True
#            self._labelWindow.show()
#            self._labelWindow.activateWindow()
#
#        except NameError:
#            if(self.imageFlag == 0):
#                print self.image
#                print type(self.image)
#            self._labelErrorWindow = labelError.LabelError().exec_()
#        except Exception as e:
#            self._labelErrorWindow = labelError.LabelError(e).exec_()
#

    def open_file(self):
        res = QtGui.QFileDialog.getOpenFileName(self, "Open IMG file",
                                                ".", "IMG files (*.IMG)")
        if isinstance(res, tuple):
            fileName = res[0]
        else:
            fileName = str(res)
        if(fileName != ""):
            self.load_file(fileName)
        else:
            print "No file selected!"
            return

    def load_file(self, filepath):
#       Not sure how to get rid of this global yet. I do know that it is needed
#       for loading the label properly, but beyond that, I do not know what the
#       full purpose of having this global it. might be used as a shortcut for
#       error detection when starting up the label window..
#        global image
        self.image = PDSImage.PDSImage(logger=self.logger)
        self.image.load_file(filepath)
        self.imageFlag = 1
        self.pdsView.set_image(self.image)

#       This checks to see if the label window exists and is open. If so, this
#       resets the label field so that the label being displayed is the label
#       for the current product.
        if(self._labelWindow != None):
            if(self._labelWindow.isOpen == True):
                self.imageLabel = self.image.pds_image.labelview
                self._labelWindow.labelContents.setText('\n'.join(self.imageLabel))
                self._labelWindow.cancel()
                self._labelWindow.show()
                self._labelWindow.activateWindow()

        print('File_Loaded')
        self.setWindowTitle(filepath)
        self.openLabel.setEnabled(True)

    def drop_file(self, pdsimage, paths):
        fileName = paths[0]
        self.load_file(fileName)

#    def 
#
    def quit(self, *args):
        self.logger.info("Attempting to shut down the application...")
        if(self._labelWindow != None):
            self._labelWindow.cancel()
        self.close()


def main():

    app = QtGui.QApplication(sys.argv)

    logger = logging.getLogger("example1")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(STD_FORMAT)
    stderrHdlr = logging.StreamHandler()
    stderrHdlr.setFormatter(fmt)
    logger.addHandler(stderrHdlr)

    w = PDSViewer(logger)
    w.resize(780, 770)
    w.show()
    app.setActiveWindow(w)
    w.raise_()
    w.activateWindow()
    app.exec_()

if __name__ == '__main__':
    main()
