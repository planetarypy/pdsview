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
# import logging
import PDSImage
import label

from ginga.qtw.QtHelp import QtGui, QtCore
from ginga.qtw.ImageViewCanvasQt import ImageViewCanvas

STD_FORMAT = '%(asctime)s | %(levelname)1.1s | %(filename)s:%(lineno)d (%(funcName)s) | %(message)s'


class PDSViewer(QtGui.QMainWindow):

    def __init__(self):
        super(PDSViewer, self).__init__()

        self.image = ""

        # Set the subwindow names here. This implementation will help prevent
        # the main window from spawning duplicate children. Even if the
        # duplication prevention is not set up for a window, this will be a
        # handy reference list of windows(or dialogues in most cases) that can
        # be spawned out of this window.
        self._label_window = None

        self.pds_view = ImageViewCanvas(render='widget')
        self.pds_view.enable_autocuts('on')
        self.pds_view.set_autocut_params('zscale')
        self.pds_view.enable_autozoom('on')
        self.pds_view.set_callback('drag-drop', self.drop_file)
        self.pds_view.set_bg(0.5, 0.5, 0.5)
        self.pds_view.ui_setActive(True)

        self.pds_view.get_bindings().enable_all(True)

        pdsview_widget = self.pds_view.get_widget()
        pdsview_widget.resize(768, 768)

        vertical_align = QtGui.QVBoxLayout()
        vertical_align.setContentsMargins(QtCore.QMargins(2, 2, 2, 2))
        vertical_align.setSpacing(1)
        vertical_align.addWidget(pdsview_widget, stretch=1)

        horizontal_align = QtGui.QHBoxLayout()
        horizontal_align.setContentsMargins(QtCore.QMargins(4, 2, 4, 2))

        # self.open_label is need as an attribute to determine whether the user
        # should be able to open the label window. The other side of this
        # toggle is found in load_file().
        open_file = QtGui.QPushButton("Open File")
        open_file.clicked.connect(self.open_file)
        self.open_label = QtGui.QPushButton("Label")
        self.open_label.clicked.connect(self.label)
        self.open_label.setEnabled(False)
        quit_button = QtGui.QPushButton("Quit")
        quit_button.clicked.connect(self.quit)

        horizontal_align.addStretch(1)
        for button in (open_file, self.open_label, quit_button):
            horizontal_align.addWidget(button, stretch=0)

        hw = QtGui.QWidget()
        hw.setLayout(horizontal_align)
        vertical_align.addWidget(hw, stretch=0)
        self.vertical_align = vertical_align
        self.horizontal_align = horizontal_align
        self.pdsview_widget = pdsview_widget

        vw = QtGui.QWidget()
        self.setCentralWidget(vw)
        vw.setLayout(vertical_align)

    def label(self):
        # Utilizing the subwindow variables to check if the label window has
        # been opened before. If not, the window is initialized.
        self.image_label = self.image.pds_image.labelview
        if self._label_window is None:
            self._label_window = label.LabelView(self)
        self._label_window.is_open = True
        self._label_window.show()
        self._label_window.activateWindow()

    def open_file(self):
        res = QtGui.QFileDialog.getOpenFileName(self, "Open IMG file",
                                                ".", "IMG files (*.IMG)")
        if isinstance(res, tuple):
            file_name = res[0]
        else:
            file_name = str(res)
        if(file_name != ""):
            self.load_file(file_name)
        else:
            print "No file selected!"
            return

    def load_file(self, filepath):
        self.image = PDSImage.PDSImage()
        self.image.load_file(filepath)
        self.pds_view.set_image(self.image)

        # This checks to see if the label window exists and is open. If so,
        # this resets the label field so that the label being displayed is the
        # label for the current product.
        if self._label_window is not None:
            if self._label_window.is_open is True:
                self.image_label = self.image.pds_image.labelview
                self._label_window.label_contents.setText('\n'.join(self.image_label))
                self._label_window.cancel()
                self._label_window.show()
                self._label_window.activateWindow()

        print('File_Loaded')
        self.setWindowTitle(filepath)
        self.open_label.setEnabled(True)

    def drop_file(self, pdsimage, paths):
        file_name = paths[0]
        self.load_file(file_name)

    def quit(self, *args):
        if self._label_window is not None:
            self._label_window.cancel()
        self.close()


def main():

    app = QtGui.QApplication(sys.argv)

    w = PDSViewer()
    w.resize(780, 770)
    w.show()
    app.setActiveWindow(w)
    w.raise_()
    w.activateWindow()
    app.exec_()

if __name__ == '__main__':
    main()
