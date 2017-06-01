import numpy as np
from qtpy import QtWidgets, QtCore


class BandWidgetModel(object):

    max_alpha = 100
    min_alpha = 0

    def __init__(self, channels_model, rgb_index, name):
        self._views = set()
        self.name = name
        self.rgb_index = rgb_index
        self.channels_model = channels_model
        self._index = channels_model.image_names.index(
            channels_model.rgb_names[rgb_index])
        self._alpha_value = self.max_alpha

    def register(self, view):
        """Register a view with the model"""
        self._views.add(view)

    def unregister(self, view):
        """Unregister a view with the model"""
        self._views.remove(view)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, new_index):
        self.update_index(new_index)

        self.channels_model.update_image()

    def update_index(self, new_index):
        self._index = new_index

        self.channels_model.rgb[self.rgb_index] = self.selected_image

    @property
    def selected_image(self):
        return self.channels_model.images[self._index]

    @property
    def alpha_value(self):
        return self._alpha_value

    @alpha_value.setter
    def alpha_value(self, new_alpha_value):
        self._alpha_value = new_alpha_value
        for view in self._views:
            view.update_alpha_value()


class BandWidgetController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def update_index(self, new_index, active):
        if active:
            self.model.index = new_index
        else:
            self.model.update_index(new_index)

    def reset_index(self):
        self.model._index = self.model.channels_model.image_names.index(
            self.model.channels_model.rgb_names[self.model.rgb_index])

    def update_alpha(self, new_alpha_value):
        if new_alpha_value > self.model.max_alpha:
            new_alpha_value = self.model.max_alpha
        elif new_alpha_value < self.model.min_alpha:
            new_alpha_value = self.model.min_alpha

        self.model.alpha_value = new_alpha_value


class BandWidget(QtWidgets.QWidget):

    def __init__(self, model):
        self.model = model
        self.model.register(self)
        self.controller = BandWidgetController(model, self)
        super(BandWidget, self).__init__()
        self.menu = QtWidgets.QComboBox()
        label = QtWidgets.QLabel(model.name)
        box = QtWidgets.QHBoxLayout()
        self.add_text_to_menu(
            self.menu, model.channels_model.image_names)
        self.create_color_layout(label, self.menu, box)
        self.menu.currentIndexChanged.connect(self.image_selected)
        self.alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.alpha_value = QtWidgets.QLabel()
        alpha_value_container = QtWidgets.QHBoxLayout()
        self.alpha_label = QtWidgets.QLabel('%s %%' % (model.name))
        alpha_slider_container = QtWidgets.QHBoxLayout()
        alpha_container = QtWidgets.QVBoxLayout()
        self.create_slider_layout(
            self.alpha_slider, self.alpha_value, self.alpha_label,
            alpha_slider_container, alpha_value_container,
            alpha_container)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addLayout(box, 0, 0)
        self.layout.addLayout(alpha_container, 1, 0)

        self.setLayout(self.layout)

    def add_text_to_menu(self, menu, names):
        """Adds the images to the menu & sets the current item in the menu"""
        for name in names:
            menu.addItem(name)
        self.set_current_index()
        # menu.activated[int].connect(self.create_composite_image)

    def set_current_index(self):
        self.menu.setCurrentIndex(self.model.index)

    def create_color_layout(self, label, menu, box):
        """Set the menu and its label next to each other"""
        box.addWidget(label)
        box.addWidget(menu)

    def create_slider_layout(self, slider, value, label, slider_container,
                             value_container, container):
        """Creates the alpha slider layout"""
        slider.setRange(self.model.min_alpha, self.model.max_alpha)
        slider.setValue(self.model.max_alpha)
        value_container.addWidget(value)
        slider.valueChanged.connect(self.value_changed)
        slider.sliderReleased.connect(self.slider_released)
        slider.setFixedWidth(self.model.max_alpha)
        value.setNum(slider.value())
        label.setFixedWidth(label.sizeHint().width())
        value.setIndent(
            (slider.width() / self.model.max_alpha) * slider.value() +
            label.width())
        slider_container.addWidget(label)
        slider_container.addWidget(slider)
        container.addLayout(value_container)
        container.addLayout(slider_container)
        slider_container.setAlignment(label, QtCore.Qt.AlignLeft)
        slider_container.setAlignment(slider, QtCore.Qt.AlignLeft)
        value_container.setAlignment(value, QtCore.Qt.AlignHCenter)
        container.setAlignment(slider_container, QtCore.Qt.AlignLeft)
        container.setAlignment(value_container, QtCore.Qt.AlignLeft)

    def image_selected(self, index):
        self.controller.update_index(index, True)

    def value_changed(self, value):
        self.controller.update_alpha(value)

    def update_alpha_value(self):
        """Displays the slider value over the alpha slider cursor"""
        self.alpha_value.setNum(self.alpha_slider.value())
        self.alpha_value.setIndent((
            self.alpha_slider.width() / self.model.max_alpha) *
            self.alpha_slider.value() + self.alpha_label.width()
        )

    def slider_released(self):
        self.model.channels_model.update_image()


class ChannelsDialogModel(object):

    def __init__(self, main_window):
        self._views = set()
        self.main_window = main_window
        self.current_index = self.image_names.index(
            main_window.current_image.image_name
        )
        self.red_model = BandWidgetModel(self, 0, 'Red')
        self.green_model = BandWidgetModel(self, 1, 'Green')
        self.blue_model = BandWidgetModel(self, 2, 'Blue')
        self.rgb_models = self.red_model, self.green_model, self.blue_model
        self.menu_indices = [model.index for model in self.rgb_models]

    @property
    def images(self):
        images = self.main_window.image_set.images
        flatten_images = [band for image in images for band in image]
        return flatten_images

    @property
    def rgb(self):
        return self.main_window.image_set.rgb

    @property
    def image_names(self):
        return [band.image_name for band in self.images]

    @property
    def rgb_names(self):
        return [band.image_name for band in self.rgb]

    @property
    def alphas(self):
        return [model.alpha_value / 100. for model in self.rgb_models]

    def update_current_index(self):
        self.current_index = self.image_names.index(
            self.main_window.current_image.image_name
        )

    def update_image(self):
        for view in self._views:
            view.display_composite_image()

    def register(self, view):
        """Register a view with the model"""
        self._views.add(view)

    def unregister(self, view):
        """Unregister a view with the model"""
        self._views.remove(view)


class ChannelsDialogController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def update_menu_indices(self):
        self.model.menu_indices = [
            model.index for model in self.model.rgb_models
        ]


class ChannelsDialog(QtWidgets.QDialog):

    def __init__(self, model):
        self.model = model
        self.model.register(self)
        self.controller = ChannelsDialogController(model, self)
        super(ChannelsDialog, self).__init__()

        # Create display of image names and highlight the current image/channel
        self.image_tree = QtWidgets.QTreeWidget()
        self.image_tree.setColumnCount(1)
        self.image_tree.setHeaderLabel('Channels')
        self.items = []
        for image_name in self.model.image_names:
            item = QtWidgets.QTreeWidgetItem(self.image_tree)
            item.setText(0, image_name)
            self.items.append(item)
        self.image_tree.insertTopLevelItems(1, self.items)
        self.image_tree.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection)
        # highlight the current image
        self.current_item.setSelected(True)
        self.image_tree.setIndentation(0)
        self.image_tree.setFixedWidth(400)

        self.rgb_check_box = QtWidgets.QCheckBox("RGB")
        self.rgb_check_box.stateChanged.connect(self.check_rgb)

        self.red_widget = BandWidget(self.model.red_model)
        self.green_widget = BandWidget(self.model.green_model)
        self.blue_widget = BandWidget(self.model.blue_model)

        self.close_button = QtWidgets.QPushButton('Close')
        self.close_button.clicked.connect(self.close_dialog)

        self.layout = QtWidgets.QGridLayout()
        widgets = [
            self.image_tree, self.rgb_check_box, self.red_widget,
            self.green_widget, self.blue_widget, self.close_button
        ]
        for row, widget in enumerate(widgets):
            self.layout.addWidget(widget, row, 0)
            self.layout.setAlignment(widget, QtCore.Qt.AlignHCenter)

        self.controller.update_menu_indices()

        self.setLayout(self.layout)

        # Match the rgb check box state from the main window
        state = self.model.main_window.rgb_check_box.checkState()
        self.rgb_check_box.setCheckState(state)

    @property
    def current_item(self):
        return self.items[self.model.current_index]

    def check_rgb(self, state):
        """Displays the rgb image when checked, single band otherwise"""
        if state == QtCore.Qt.Checked:
            self.model.main_window.rgb_check_box.setCheckState(
                QtCore.Qt.Checked
            )
            self.model.main_window.switch_rgb(state)
            self.display_composite_image()
        elif state == QtCore.Qt.Unchecked:
            self.model.main_window.rgb_check_box.setCheckState(
                QtCore.Qt.Unchecked)

    def create_composite_image(self):
        composite_layers = []
        for band, alpha in zip(self.model.rgb, self.model.alphas):
            layer_data = band.data * alpha
            composite_layers.append(layer_data)
        composite_image = np.dstack(composite_layers)
        return composite_image

    def set_rgb_image(self):
        composite_image = self.create_composite_image()
        self.model.main_window.current_image.set_data(composite_image)
        self.controller.update_menu_indices()
        self.model.main_window.next_channel_btn.setEnabled(False)
        self.model.main_window.previous_channel_btn.setEnabled(False)

    def set_menus_index(self):
        widgets = self.red_widget, self.green_widget, self.blue_widget
        for widget, index in zip(widgets, self.model.menu_indices):
            widget.menu.setCurrentIndex(index)
            widget.controller.update_index(index, False)

    def reset_gray_image(self):
        self.rgb_check_box.setCheckState(QtCore.Qt.Unchecked)
        self.set_menus_index()

    def display_composite_image(self):
        """Display the rgb composite image"""
        if self.rgb_check_box.checkState() == QtCore.Qt.Unchecked:
            return
        try:
            self.set_rgb_image()
        except ValueError:
            print("Images must be the same size")
            self.reset_gray_image()

    def update_menus_current_item(self):
        for widget in self.red_widget, self.green_widget, self.blue_widget:
            widget.controller.reset_index()
        self.controller.update_menu_indices()
        self.set_menus_index()

    def change_image(self):
        """Change the menu and image list when the image is changed"""
        self.current_item.setSelected(False)
        self.model.update_current_index()
        self.current_item.setSelected(True)
        self.update_menus_current_item()
        self.display_composite_image()

    def closeEvent(self, event):
        self.close_dialog()

    def close_dialog(self):
        """Close the dialog and save the position"""
        self.model.main_window.channels_window_is_open = False
        self.model.main_window.channels_window_pos = self.pos()
        self.hide()
