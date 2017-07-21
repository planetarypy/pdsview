import os
from functools import wraps

from qtpy import QtWidgets, QtCore

from pdsview import pdsview, channels_dialog, band_widget

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


class TestChannelsDialogModel(object):
    test_images = pdsview.ImageSet(test_files)
    window = pdsview.PDSViewer(test_images)
    model = channels_dialog.ChannelsDialogModel(window)

    def test_init(self):
        assert self.model._views == set()
        assert self.model.current_index == 0
        assert isinstance(self.model.rgb_models, tuple)
        assert len(self.model.rgb_models) == 3
        for model in self.model.rgb_models:
            assert isinstance(model, band_widget.BandWidgetModel)
        assert self.model.red_model.name == 'Red'
        assert self.model.red_model.rgb_index == 0
        assert self.model.green_model.name == 'Green'
        assert self.model.green_model.rgb_index == 1
        assert self.model.blue_model.name == 'Blue'
        assert self.model.blue_model.rgb_index == 2
        assert isinstance(self.model.menu_indices, list)
        assert self.model.menu_indices == [0, 1, 2]

    def test_images(self):
        images = self.window.image_set.images
        expected_images = [image[0] for image in images]
        assert self.model.images == expected_images

    def test_rgb(self):
        assert self.model.rgb == self.window.image_set.rgb

    def test_image_names(self):
        names = [
            FILE_5_NAME, FILE_3_NAME, FILE_1_NAME, FILE_2_NAME, FILE_4_NAME
        ]
        assert self.model.image_names == names

    def test_rgb_names(self):
        rgb_names = [FILE_5_NAME, FILE_3_NAME, FILE_1_NAME]
        assert self.model.rgb_names == rgb_names

    def test_alphas(self):
        assert self.model.alphas == [1., 1., 1.]
        self.model.red_model.alpha_value = 75
        self.model.green_model.alpha_value = 50
        self.model.blue_model.alpha_value = 25
        assert self.model.alphas == [.75, .5, .25]


class TestChannelDialogController(object):
    test_images = pdsview.ImageSet(test_files)
    window = pdsview.PDSViewer(test_images)
    model = channels_dialog.ChannelsDialogModel(window)
    controller = channels_dialog.ChannelsDialogController(model, None)

    def test_init(self):
        assert self.controller.model == self.model
        assert self.controller.view is None

    def test_update_menus_indices(self):
        assert self.model.menu_indices == [0, 1, 2]
        self.model.red_model.update_index(1)
        self.model.green_model.update_index(3)
        self.model.blue_model.update_index(0)
        assert self.model.menu_indices == [0, 1, 2]
        self.controller.update_menu_indices()
        assert self.model.menu_indices == [1, 3, 0]

    def test_update_current_index(self):
        assert self.model.current_index == 0
        self.model.main_window.controller.next_image()
        assert self.model.current_index == 0
        self.controller.update_current_index()
        assert self.model.current_index == 1
        self.model.main_window.controller.previous_image()
        assert self.model.current_index == 1
        self.controller.update_current_index()
        assert self.model.current_index == 0


class TestChannelsDialog(object):
    test_images = pdsview.ImageSet(test_files)
    window = pdsview.PDSViewer(test_images)
    window.channels_dialog()
    dialog = window.channels_window
    model = dialog.model
    window.show()

    def add_widget_wrapper(func):
        @wraps(func)
        def wrapper(self, qtbot):
            self.dialog.show()
            qtbot.addWidget(self.dialog)
            return func(self, qtbot)
        return wrapper

    @add_widget_wrapper
    def test_init(self, qtbot):
        assert self.dialog.model == self.model
        assert self.dialog in self.model._views
        assert isinstance(
            self.dialog.controller, channels_dialog.ChannelsDialogController
        )
        assert isinstance(self.dialog, QtWidgets.QDialog)
        assert isinstance(self.dialog.image_tree, QtWidgets.QTreeWidget)
        for item in self.dialog.items:
            assert isinstance(item, QtWidgets.QTreeWidgetItem)
        selection_mode = QtWidgets.QAbstractItemView.NoSelection
        assert self.dialog.image_tree.selectionMode() == selection_mode
        assert self.model.image_names == [
            item.text(0) for item in self.dialog.items]
        assert self.dialog.current_item.isSelected()
        assert isinstance(self.dialog.rgb_check_box, QtWidgets.QCheckBox)
        assert isinstance(self.dialog.red_widget, band_widget.BandWidget)
        assert isinstance(self.dialog.green_widget, band_widget.BandWidget)
        assert isinstance(self.dialog.blue_widget, band_widget.BandWidget)

    @add_widget_wrapper
    def test_current_item(self, qtbot):
        assert self.dialog.current_item.text(0) == self.dialog.items[0].text(0)
        qtbot.mouseClick(self.window.next_image_btn, QtCore.Qt.LeftButton)
        assert self.model.current_index == 1
        assert self.dialog.current_item.text(0) == self.dialog.items[1].text(0)
        qtbot.mouseClick(self.window.previous_image_btn, QtCore.Qt.LeftButton)
        assert self.model.current_index == 0
        assert self.dialog.current_item.text(0) == self.dialog.items[0].text(0)

    # TODO: CANNOT TEST RGB UNTIL AN RGB IMAGE IS ADDED TO THE TEST DATA
    # @add_widget_wrapper
    # def test_check_rgb(self, qtbot)

    @add_widget_wrapper
    def test_change_image(self, qtbot):
        def check_selected(index1, index2):
            assert self.dialog.items[index1].isSelected()
            assert not self.dialog.items[index2].isSelected()
        check_selected(0, 1)
        qtbot.mouseClick(self.window.next_image_btn, QtCore.Qt.LeftButton)
        check_selected(1, 0)
        qtbot.mouseClick(self.window.previous_image_btn, QtCore.Qt.LeftButton)
        check_selected(0, 1)
        qtbot.mouseClick(self.window.previous_image_btn, QtCore.Qt.LeftButton)
        check_selected(-1, 0)
        qtbot.mouseClick(self.window.next_image_btn, QtCore.Qt.LeftButton)
        check_selected(0, 1)

    @add_widget_wrapper
    def test_set_menus_index(self, qtbot):
        widgets = [
            self.dialog.red_widget,
            self.dialog.green_widget,
            self.dialog.blue_widget
        ]

        def check_currentIndex():
            for widget, index in zip(widgets, self.model.menu_indices):
                assert widget.menu.currentIndex() == index
        self.model.menu_indices = [0, 1, 2]
        self.dialog.set_menus_index()
        check_currentIndex()
        r, g, b = 4, 0, 2
        self.model.menu_indices = [r, g, b]
        self.dialog.set_menus_index()
        check_currentIndex()
        self.model.menu_indices = [0, 1, 2]
        self.dialog.set_menus_index()
        check_currentIndex()
        assert self.model.menu_indices == [0, 1, 2]

    @add_widget_wrapper
    def test_update_menus_current_item(self, qtbot):
        assert self.test_images.rgb == self.model.images[:3]
        r, g, b = 4, 0, 2
        new_rgb = [
            self.model.images[r], self.model.images[g], self.model.images[b]
        ]
        self.test_images.rgb = new_rgb
        self.dialog.update_menus_current_item()
        assert self.model.red_model.index == r
        assert self.model.green_model.index == g
        assert self.model.blue_model.index == b
        red_text = self.dialog.red_widget.menu.currentText()
        assert red_text == self.model.image_names[r]
        green_text = self.dialog.green_widget.menu.currentText()
        assert green_text == self.model.image_names[g]
        blue_text = self.dialog.blue_widget.menu.currentText()
        assert blue_text == self.model.image_names[b]
        self.test_images.rgb = self.model.images[:3]
        assert self.test_images.rgb == self.model.images[:3]

    @add_widget_wrapper
    def test_close_dialog(self, qtbot):
        assert not self.window.channels_window_is_open
        qtbot.mouseClick(self.window.channels_button, QtCore.Qt.LeftButton)
        assert self.window.channels_window_is_open
        pos = self.dialog.pos()
        x, y = pos.x(), pos.y()
        new_pos = QtCore.QPoint(x + 5, y - 10)
        self.dialog.move(new_pos)
        qtbot.mouseClick(self.dialog.close_button, QtCore.Qt.LeftButton)
        assert not self.window.channels_window_is_open
        assert self.window.channels_window_pos == new_pos
        qtbot.mouseClick(self.window.channels_button, QtCore.Qt.LeftButton)
        assert self.window.channels_window_is_open
        assert self.dialog.pos() == new_pos
