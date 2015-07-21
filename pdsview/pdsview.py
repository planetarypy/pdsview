#! /usr/bin/env python

import sys
import os
# import logging
import PDSImage
import label

from ginga.qtw.QtHelp import QtGui, QtCore
from ginga.qtw.ImageViewCanvasQt import ImageViewCanvas

STD_FORMAT = '%(asctime)s | %(levelname)1.1s | %(filename)s:%(lineno)d (%(funcName)s) | %(message)s'
#
#
# class PDSModel():
#


class PDSViewer(QtGui.QMainWindow):

    def __init__(self):
        super(PDSViewer, self).__init__()

        self.image = ""
        self.index_count = 0
        self.pos = 1
        self.names = []

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
        self.next_channel = QtGui.QPushButton("Next")
        self.next_channel.clicked.connect(lambda: self.switch_channel(1))
        self.next_channel.setEnabled(False)
        self.previous_channel = QtGui.QPushButton("Previous")
        self.previous_channel.clicked.connect(lambda: self.switch_channel(-1))
        self.previous_channel.setEnabled(False)
        self.open_label = QtGui.QPushButton("Label")
        self.open_label.clicked.connect(self.label)
        self.open_label.setEnabled(False)
        quit_button = QtGui.QPushButton("Quit")
        quit_button.clicked.connect(self.quit)

        horizontal_align.addStretch(1)
        for button in (self.previous_channel, self.next_channel, open_file, self.open_label, quit_button):
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

        self.parse_arguments(sys.argv)

    def parse_arguments(self, arguments):
        total = len(arguments)
        if total is not 1:
            for arg in arguments[1:total]:
                self.names.append(arg)
            self.name_check()
            self.index_count = len(self.names)
            if len(self.names) is not 1 and len(self.names) is not 0:
                self.next_channel.setEnabled(True)
                self.previous_channel.setEnabled(True)
                self.switch_channel(0)
            elif len(self.names) is 1:
                self.load_file(self.names[0])
                self.next_channel.setEnabled(False)
                self.previous_channel.setEnabled(False)

    def name_check(self):
        self.verify_names()
        if(len(self.names) > 1):
            self.names = self.remove_duplicate_names(self.names)

    def verify_names(self):
        """This method removes non-existant files and files with improper file
        extensions.
        """
        removal_flag = 0
        removal_list = []
        for name in self.names:
            if os.path.isfile(name) is not True:
                # integrate with logger
                print name, "cannot be located. Removing from list..."
                removal_list.append(name)
                removal_flag = 1
            elif name.endswith('.img') is not True and name.endswith('.IMG') is not True:
                # integrate with logger
                print name, "does not have a valid file extension. Removing from list..."
                removal_list.append(name)
                removal_flag = 1
        if removal_flag is 1:
            removal_list = self.remove_duplicate_names(removal_list)
            for name in removal_list:
                self.names.remove(name)
            removal_flag = 0

    def remove_duplicate_names(self, name_list):
        """This function exists to remove duplicate items in lists. It also
        preserves the order of the list.
        """
        seen = {}
        result = []
        for item in name_list:
            marker = item
            if marker in seen: 
                print item, "is a duplicate. Removing from list..."
                continue
            seen[marker] = 1
            result.append(item)
        return result

    def switch_channel(self, direction):
        self.pos = self.pos + direction
        if(self.pos > self.index_count):
            self.pos = 1
        elif(self.pos < 1):
            self.pos = self.index_count
        self.load_file(self.names[self.pos-1])

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
        filter = "IMG files (*.IMG)"
        file_name = QtGui.QFileDialog()
        file_name.setFileMode(QtGui.QFileDialog.ExistingFiles)
        opens = file_name.getOpenFileNames(self, "Open IMG files", ".", filter)
        if(opens[1] != ""):
            self.names = opens[0]
            self.index_count = len(self.names)
            if len(self.names) is not 1:
                self.next_channel.setEnabled(True)
                self.previous_channel.setEnabled(True)
                self.switch_channel(0)
            else:
                self.load_file(self.names[0])
                self.next_channel.setEnabled(False)
                self.previous_channel.setEnabled(False)
        else:
            # integrate with logger
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
                self._label_window.is_open = True
                self._label_window.activateWindow()

        print('File_Loaded')
        self.setWindowTitle(filepath)
        # save this line for testing purposes
        self.loaded_file = os.path.basename(filepath)
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
