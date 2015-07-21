import sys
from pdsview import pdsview
import pytestqt
from ginga.qtw.QtHelp import QtGui, QtCore


def test_invalid_names():
    """Verifies that invalid file names will be removed from the loading list
    if they are entered as arguments when calling pdsview.
    """
    window = pdsview.PDSViewer()
    window.show()
#   This simulates sys.argv
    arguments = ['/home/zburnham/.virtualenvs/pdsview/bin/pdsview',
                 'tests/mission_data/foo.img',
                 'tests/mission_data/bar.IMG',
                 'tests/mission_data/2m132591087cfd1800p2977m2f1.img']
    window.parse_arguments(arguments)
    assert window.open_label.isEnabled() is True
    assert window.next_channel.isEnabled() is False
    assert window.previous_channel.isEnabled() is False
    assert window.names[0] is "tests/mission_data/2m132591087cfd1800p2977m2f1.img"


def test_duplicates():
    """Verifies that duplicate files are removed from the loading list if they
    are entered as arguments when calling pdsview.
    """
    window = pdsview.PDSViewer()
    window.show()
#   This simulates sys.argv
    arguments = ['/home/zburnham/.virtualenvs/pdsview/bin/pdsview',
                 'tests/mission_data/2m132591087cfd1800p2977m2f1.img',
                 'tests/mission_data/2m132591087cfd1800p2977m2f1.img',
                 'tests/mission_data/2m132591087cfd1800p2977m2f1.img']
    window.parse_arguments(arguments)
    assert window.open_label.isEnabled() is True
    assert window.next_channel.isEnabled() is False
    assert window.previous_channel.isEnabled() is False
    assert window.names[0] is "tests/mission_data/2m132591087cfd1800p2977m2f1.img"


def test_image_next_switch(qtbot):
    """Verifies that pdsview will switch to the next image properly when 
    multiple images are loaded. Also verifies that pdsview will jump
    to the first image in the set when the "Next" button is pressed while
    viewing the last image.
    """
    window = pdsview.PDSViewer()
    window.show()
    qtbot.addWidget(window)
#   This simulates sys.argv
    arguments = ['/home/zburnham/.virtualenvs/pdsview/bin/pdsview',
                 'tests/mission_data/1p190678905erp64kcp2600l8c1.img',
                 'tests/mission_data/2m132591087cfd1800p2977m2f1.img',
                 'tests/mission_data/2p129641989eth0361p2600r8m1.img']
    window.parse_arguments(arguments)
    assert window.open_label.isEnabled() is True
    assert window.next_channel.isEnabled() is True
    assert window.previous_channel.isEnabled() is True
    assert window.names[0] is "tests/mission_data/1p190678905erp64kcp2600l8c1.img"

#   '1p1...' file
    assert window.loaded_file == "1p190678905erp64kcp2600l8c1.img"

#   '2m1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window.loaded_file == "2m132591087cfd1800p2977m2f1.img"

#   '2p1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window.loaded_file == "2p129641989eth0361p2600r8m1.img"

#   back to the '1p1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window.loaded_file == "1p190678905erp64kcp2600l8c1.img"


def test_image_previous_switch(qtbot):
    """Verifies that pdsview will switch to the next image properly when
    multiple images are loaded. Also verifies that pdsview will jump
    to the first image in the set when the "Next" button is pressed while
    viewing the last image.
    """
    window = pdsview.PDSViewer()
    window.show()
    qtbot.addWidget(window)
#   This simulates sys.argv
    arguments = ['/home/zburnham/.virtualenvs/pdsview/bin/pdsview',
                 'tests/mission_data/1p190678905erp64kcp2600l8c1.img',
                 'tests/mission_data/2m132591087cfd1800p2977m2f1.img',
                 'tests/mission_data/2p129641989eth0361p2600r8m1.img']
    window.parse_arguments(arguments)
    assert window.open_label.isEnabled() is True
    assert window.next_channel.isEnabled() is True
    assert window.previous_channel.isEnabled() is True
    assert window.names[0] is "tests/mission_data/1p190678905erp64kcp2600l8c1.img"

#   '1p1...' file
    assert window.loaded_file == "1p190678905erp64kcp2600l8c1.img"

#   jump to the '2p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window.loaded_file == "2p129641989eth0361p2600r8m1.img"

#   '2m1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window.loaded_file == "2m132591087cfd1800p2977m2f1.img"

#   back to the '1p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window.loaded_file == "1p190678905erp64kcp2600l8c1.img"


def test_label_previous_switch(qtbot):
    """Verifies that the label will be properly updated when switching to the
    previous image in the set. Also verifies that the label updates properly
    when pdsview jumps to the last image in the set.
    """
    window = pdsview.PDSViewer()
    window.show()
    qtbot.addWidget(window)
#   This simulates sys.argv
    arguments = ['/home/zburnham/.virtualenvs/pdsview/bin/pdsview',
                 'tests/mission_data/1p190678905erp64kcp2600l8c1.img',
                 'tests/mission_data/2p129641989eth0361p2600r8m1.img',
                 'tests/mission_data/2m132591087cfd1800p2977m2f1.img']
    window.parse_arguments(arguments)

#   '1p1...' file
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"

#   jumps to the '2m1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[182:186] == "1029"

#   '2p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[193:196] == "332"

#   the original '1p1...' file
    qtbot.mouseClick(window.previous_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"



def test_label_next_switch(qtbot):
    """Verifies that the label will be properly updated when switching to the
    previous image in the set. Also verifies that the label updates properly
    when pdsview jumps to the last image in the set.
    """
    window = pdsview.PDSViewer()
    window.show()
    qtbot.addWidget(window)
#   This simulates sys.argv
    arguments = ['/home/zburnham/.virtualenvs/pdsview/bin/pdsview',
                 'tests/mission_data/1p190678905erp64kcp2600l8c1.img',
                 'tests/mission_data/2p129641989eth0361p2600r8m1.img',
                 'tests/mission_data/2m132591087cfd1800p2977m2f1.img']
    window.parse_arguments(arguments)

#   '1p1...' file
    qtbot.mouseClick(window.open_label, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"

#   '2p1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[193:196] == "332"

#   '2m1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[182:186] == "1029"

#   jump to the original '1p1...' file
    qtbot.mouseClick(window.next_channel, QtCore.Qt.LeftButton)
    assert window._label_window.label_contents.toPlainText()[188:192] == "1561"
