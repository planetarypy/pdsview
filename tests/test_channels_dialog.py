from pdsview import pdsview
import pytestqt
from ginga.qtw.QtHelp import QtGui, QtCore
import os

FILE_1 = os.path.join(
    'tests', 'mission_data', '2m132591087cfd1800p2977m2f1.img')
FILE_2 = os.path.join(
    'tests', 'mission_data', '2p129641989eth0361p2600r8m1.img')
FILE_3 = os.path.join(
    'tests', 'mission_data', '1p190678905erp64kcp2600l8c1.img')
FILE_4 = os.path.join(
    'tests', 'mission_data', 'h58n3118.img')
FILE_5 = os.path.join(
    'tests', 'mission_data', '1p134482118erp0902p2600r8m1.img')
FILE_6 = os.path.join(
    'tests', 'mission_data', '0047MH0000110010100214C00_DRCL.IMG')
test_files = [FILE_1, FILE_2, FILE_3, FILE_4, FILE_5, FILE_6]
FILE_1_NAME = '2m132591087cfd1800p2977m2f1.img'
FILE_2_NAME = '2p129641989eth0361p2600r8m1.img'
FILE_3_NAME = '1p190678905erp64kcp2600l8c1.img'
FILE_4_NAME = 'h58n3118.img'
FILE_5_NAME = '1p134482118erp0902p2600r8m1.img'
FILE_6_NAME = '0047MH0000110010100214C00_DRCL.IMG'

test_images = pdsview.ImageSet(test_files)


def test_channels_dialog(qtbot):
    """Test the channels dialog has the correct initial featuresvalues"""
    window = pdsview.PDSViewer(test_images)
    dialog = pdsview.ChannelsDialog(window.image_set.current_image[0], window)
    dialog.show()
    qtbot.addWidget(dialog)
    assert dialog.main_window == window
    assert dialog.current_image == window.image_set.current_image[0]
    print(dialog.image_names)
    assert dialog.image_names == [FILE_5_NAME, FILE_3_NAME, FILE_1_NAME,
                                  FILE_2_NAME, FILE_4_NAME]
    assert isinstance(dialog.image_list, QtGui.QTreeWidget)
    assert dialog.image_list.columnCount() == 1
    assert isinstance(dialog.items[0], QtGui.QTreeWidgetItem)
    assert dialog.items[0].text(0) == FILE_5_NAME
    assert dialog.current_index == 0
    assert isinstance(dialog.rgb_check_box, QtGui.QCheckBox)
    assert dialog.rgb_check_box.checkState() == QtCore.Qt.Unchecked
    assert isinstance(dialog.red_menu, QtGui.QComboBox)
    assert dialog.red_menu.count() == 5
    assert isinstance(dialog.red_alpha_slider, QtGui.QSlider)
    assert dialog.red_alpha_slider.value() == 100
    assert dialog.red_alpha_slider.maximum() == 100
    assert dialog.red_alpha_slider.minimum() == 0
    assert dialog.red_alpha_slider.width() == 100
    assert isinstance(dialog.layout, QtGui.QGridLayout)


def test_menus_current_text(qtbot):
    """Test menus_current_text returns the correct text from the menu"""
    window = pdsview.PDSViewer(test_images)
    dialog = pdsview.ChannelsDialog(window.image_set.current_image[0], window)
    dialog.show()
    qtbot.addWidget(dialog)
    bands = dialog.menus_current_text()
    assert bands[0] == window.rgb[0].file_name
    assert bands[1] == window.rgb[1].file_name
    assert bands[2] == window.rgb[2].file_name


def test_get_alphas(qtbot):
    """Test get_alphas return the correct alpha value from the slider"""
    window = pdsview.PDSViewer(test_images)
    dialog = pdsview.ChannelsDialog(window.image_set.current_image[0], window)
    dialog.show()
    qtbot.addWidget(dialog)
    alphas = dialog.get_alphas()
    assert alphas[0] == 1.0
    assert alphas[1] == 1.0
    assert alphas[2] == 1.0
    dialog.red_alpha_slider.setValue(50)
    dialog.green_alpha_slider.setValue(25)
    dialog.blue_alpha_slider.setValue(75)
    alphas = dialog.get_alphas()
    assert alphas[0] == 0.5
    assert alphas[1] == 0.25
    assert alphas[2] == 0.75


def test_change_image(qtbot):
    """Test click next/prev image changes the highlighted item in the list"""
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    qtbot.mouseClick(window.channels_button, QtCore.Qt.LeftButton)
    dialog = window.channels_window
    # Initial check that the first image is highlighted, second is not
    assert dialog.image_list.isItemSelected(dialog.items[0])
    assert not dialog.image_list.isItemSelected(dialog.items[1])
    qtbot.mouseClick(window.next_image, QtCore.Qt.LeftButton)
    # Test that the second image is highlighted and the first is not
    assert not dialog.image_list.isItemSelected(dialog.items[0])
    assert dialog.image_list.isItemSelected(dialog.items[1])


def test_close_dialog(qtbot):
    """Test the dialog position is saved when the dialog is closed"""
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    qtbot.mouseClick(window.channels_button, QtCore.Qt.LeftButton)
    dialog = window.channels_window
    # Test this bool is set when the dialog window is opened
    assert dialog.main_window.channels_window_is_open
    default_pos = dialog.pos()
    dialog.move(50, 100)
    # Test that the dialog did in fact move
    assert default_pos != dialog.pos()
    new_pos = dialog.pos()
    dialog.close_dialog()
    # Test that False bool is set when dialog window is closed
    assert not dialog.main_window.channels_window_is_open
    # Test that the new position is saved as an attribute in the main window
    assert dialog.main_window.channels_window_pos == new_pos
    qtbot.mouseClick(window.next_image, QtCore.Qt.LeftButton)
    # Delete channels window by clicking next image
    assert not window.channels_window
    qtbot.mouseClick(window.channels_button, QtCore.Qt.LeftButton)
    dialog = window.channels_window
    assert dialog.main_window.channels_window_is_open
    # Test the dialog opens in the new position and not the default position
    assert dialog.pos() != default_pos
    assert dialog.pos() == new_pos


def test_create_composite_image(qtbot):
    """Test create_composite_image makes a 3 band image"""
    test_images_2 = pdsview.ImageSet([FILE_3, FILE_5])
    window = pdsview.PDSViewer(test_images_2)
    qtbot.addWidget(window)
    qtbot.mouseClick(window.channels_button, QtCore.Qt.LeftButton)
    window.next_channel.setEnabled(True)
    window.previous_channel.setEnabled(True)
    dialog = window.channels_window
    # Initial check the current image is a single band image
    assert dialog.current_image.ndim == 2
    qtbot.mouseClick(dialog.rgb_check_box, QtCore.Qt.LeftButton)
    # Test the image is now a 3 band image
    assert dialog.current_image.ndim == 3
    # Test the channels buttons are diabled
    assert not window.next_channel.isEnabled()
    assert not window.previous_channel.isEnabled()


def test_update_menus_index(qtbot):
    """Test update_menus_index to update indices list when called"""
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    qtbot.mouseClick(window.channels_button, QtCore.Qt.LeftButton)
    dialog = window.channels_window
    default_indices = dialog.indices
    dialog.red_menu.setCurrentIndex(3)
    dialog.green_menu.setCurrentIndex(0)
    dialog.blue_menu.setCurrentIndex(4)
    dialog.update_menus_index()
    assert dialog.indices != default_indices
    assert dialog.indices == [3, 0, 4]


def test_update_menus_current_item(qtbot):
    """Test update_menus_current_item updates from rgb list correctly"""
    window = pdsview.PDSViewer(test_images)
    qtbot.addWidget(window)
    qtbot.mouseClick(window.channels_button, QtCore.Qt.LeftButton)
    dialog = window.channels_window
    default_bands = dialog.menus_current_text()
    window.rgb = [window.image_set.images[0][0]] * 3
    dialog.update_menus_current_item()
    assert dialog.menus_current_text() != default_bands
    image = window.image_set.images[0][0].image_name
    assert dialog.menus_current_text() == [image] * 3
