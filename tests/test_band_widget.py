import os

from qtpy import QtWidgets

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


class TestBandWidgetModel(object):

    test_images = pdsview.ImageSet(test_files)
    window = pdsview.PDSViewer(test_images)
    channels_model = channels_dialog.ChannelsDialogModel(window)
    model = band_widget.BandWidgetModel(channels_model, 0, 'Test')

    def test_init1(self):
        test_name = 'Test1'
        test_rgb_index = 0
        model = band_widget.BandWidgetModel(
            self.channels_model, test_rgb_index, test_name)
        assert isinstance(model.max_alpha, float)
        assert model.max_alpha == 100.
        assert isinstance(model.min_alpha, float)
        assert model.min_alpha == 0.
        assert model._views == set()
        assert model.name == test_name
        assert model.rgb_index == test_rgb_index
        assert model.channels_model == self.channels_model
        assert model._index == 0
        assert model._alpha_value == model.max_alpha

    def test_init2(self):
        test_name = 'Test2'
        test_rgb_index = 2
        model = band_widget.BandWidgetModel(
            self.channels_model, test_rgb_index, test_name)
        assert isinstance(model.max_alpha, float)
        assert model.max_alpha == 100.
        assert isinstance(model.min_alpha, float)
        assert model.min_alpha == 0.
        assert model._views == set()
        assert model.name == test_name
        assert model.rgb_index == test_rgb_index
        assert model.channels_model == self.channels_model
        assert model._index == 2
        assert model._alpha_value == model.max_alpha

    def test_index(self):
        assert self.model.index == self.model._index

    def test_selected_image(self):
        expected_selected_image = self.channels_model.images[self.model.index]
        assert self.model.selected_image == expected_selected_image

    def test_update_index(self):
        assert self.model.index == 0
        new_index = 1
        new_selected_image = self.channels_model.images[new_index]
        self.model.update_index(new_index)
        assert self.model.index == new_index
        assert self.model.selected_image == new_selected_image
        new_index = 0
        new_selected_image = self.channels_model.images[new_index]
        self.model.index = new_index
        assert self.model.index == new_index
        assert self.model.selected_image == new_selected_image

    def test_alpha_value(self):
        assert self.model.alpha_value == self.model._alpha_value
        self.model.alpha_value = 50.
        assert self.model.alpha_value == 50.
        self.model.alpha_value = 100.
        assert self.model.alpha_value == 100.


class TestBandWidgetController(object):
    test_images = pdsview.ImageSet(test_files)
    window = pdsview.PDSViewer(test_images)
    channels_model = channels_dialog.ChannelsDialogModel(window)
    model = band_widget.BandWidgetModel(
        channels_model, 0, 'Test')
    controller = band_widget.BandWidgetController(model, None)

    def test_init(self):
        assert self.controller.model == self.model
        assert self.controller.view is None

    def test_update_index(self):
        assert self.model.index == 0
        new_index = 1
        self.controller.update_index(new_index, True)
        assert self.model.index == new_index
        new_index = 0
        self.controller.update_index(new_index, True)
        assert self.model.index == new_index

    def test_reset_index(self):
        assert self.model.index == 0
        new_index = 1
        self.model._index = new_index
        self.controller.reset_index()
        assert self.model.index == 0

    def test_update_alpha_value(self):
        assert self.model.alpha_value == 100.
        self.controller.update_alpha(50.)
        assert self.model.alpha_value == 50.
        self.controller.update_alpha(75.)
        assert self.model.alpha_value == 75.
        self.controller.update_alpha(-1)
        assert self.model.alpha_value == 0.
        self.controller.update_alpha(-100000)
        assert self.model.alpha_value == 0.
        self.controller.update_alpha(101)
        assert self.model.alpha_value == 100.
        self.controller.update_alpha(10000)
        assert self.model.alpha_value == 100.
        self.controller.update_alpha(0)
        assert self.model.alpha_value == 0.
        self.controller.update_alpha(100)
        assert self.model.alpha_value == 100.


class TestBandWidget(object):
    test_images = pdsview.ImageSet(test_files)
    window = pdsview.PDSViewer(test_images)
    channels_model = channels_dialog.ChannelsDialogModel(window)
    model = band_widget.BandWidgetModel(
        channels_model, 0, 'Test')
    band = band_widget.BandWidget(model)

    def check_menu_text(self):
        for index, name in enumerate(self.channels_model.image_names):
            assert self.band.menu.itemText(index) == name

    def test_init(self):
        assert self.band.model == self.model
        assert isinstance(
            self.band.controller, band_widget.BandWidgetController
        )
        assert isinstance(self.band.menu, QtWidgets.QComboBox)
        assert isinstance(self.band.alpha_slider, QtWidgets.QSlider)
        assert isinstance(self.band.alpha_value, QtWidgets.QLabel)
        assert isinstance(self.band.alpha_label, QtWidgets.QLabel)
        assert isinstance(self.band.layout, QtWidgets.QGridLayout)
        self.check_menu_text()
        assert self.band.alpha_value.text() == str(int(self.model.max_alpha))
        assert self.band.alpha_label.text() == 'Test %'
        assert self.band.alpha_slider.value() == self.model.max_alpha

    def test_add_text_to_menu(self):
        self.check_menu_text()
        test_names = ['foo', 'bar']
        self.band.add_text_to_menu(test_names)
        num_names = len(self.channels_model.image_names)
        assert self.band.menu.itemText(num_names + 0) == test_names[0]
        assert self.band.menu.itemText(num_names + 1) == test_names[1]
        self.band.menu.removeItem(num_names + 0)
        self.band.menu.removeItem(num_names + 1)
        self.check_menu_text()

    def test_set_current_index(self):
        assert self.band.menu.currentIndex() == 0
        self.model.index = 1
        self.band.set_current_index()
        assert self.band.menu.currentIndex() == 1
        self.model.index = 0
        self.band.set_current_index()
        assert self.band.menu.currentIndex() == 0

    def test_image_selected(self):
        assert self.model.index == 0
        new_index = 1
        new_selected_image = self.channels_model.images[new_index]
        self.band.image_selected(new_index)
        assert self.model.index == new_index
        assert self.model.selected_image == new_selected_image
        new_index = 0
        new_selected_image = self.channels_model.images[new_index]
        self.band.image_selected(new_index)
        assert self.model.index == new_index
        assert self.model.selected_image == new_selected_image

    def test_value_changed(self):
        assert self.model.alpha_value == 100.
        assert self.band.alpha_value.text() == '100'
        self.band.alpha_slider.setValue(50.)
        assert self.model.alpha_value == 50.
        assert self.band.alpha_value.text() == '50'
        self.band.alpha_slider.setValue(75.)
        assert self.model.alpha_value == 75.
        assert self.band.alpha_value.text() == '75'
        self.band.alpha_slider.setValue(-1)
        assert self.model.alpha_value == 0.
        assert self.band.alpha_value.text() == '0'
        self.band.alpha_slider.setValue(-100000)
        assert self.model.alpha_value == 0.
        assert self.band.alpha_value.text() == '0'
        self.band.alpha_slider.setValue(101)
        assert self.model.alpha_value == 100.
        assert self.band.alpha_value.text() == '100'
        self.band.alpha_slider.setValue(10000)
        assert self.model.alpha_value == 100.
        self.band.alpha_slider.setValue(0)
        assert self.band.alpha_value.text() == '0'
        assert self.model.alpha_value == 0.
        self.band.alpha_slider.setValue(100)
        assert self.model.alpha_value == 100.
        assert self.band.alpha_value.text() == '100'
