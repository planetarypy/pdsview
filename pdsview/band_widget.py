from qtpy import QtWidgets, QtCore


class BandWidgetModel(object):

    max_alpha = 100.
    min_alpha = 0.

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

    @property
    def selected_image(self):
        return self.channels_model.images[self._index]

    def update_index(self, new_index):
        self._index = new_index

        self.channels_model.rgb[self.rgb_index] = self.selected_image

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

        self.model.alpha_value = float(new_alpha_value)


class BandWidget(QtWidgets.QWidget):

    def __init__(self, model):
        self.model = model
        self.model.register(self)
        self.controller = BandWidgetController(model, self)
        super(BandWidget, self).__init__()
        self.menu = QtWidgets.QComboBox()
        label = QtWidgets.QLabel(model.name)
        box = QtWidgets.QHBoxLayout()
        self.add_text_to_menu(model.channels_model.image_names)
        box.addWidget(label)
        box.addWidget(self.menu)
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

    def add_text_to_menu(self, names):
        """Adds the images to the menu & sets the current item in the menu"""
        for name in names:
            self.menu.addItem(name)
        self.set_current_index()

    def set_current_index(self):
        self.menu.setCurrentIndex(self.model.index)

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
