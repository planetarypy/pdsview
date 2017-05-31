import numpy as np
from qtpy import QtWidgets, QtCore


class ChannelsDialog(QtWidgets.QDialog):
    """A Dialog box to adjust the channels and alpha values"""
    def __init__(self, current_image, main_window):
        super(ChannelsDialog, self).__init__()

        self.main_window = main_window
        self.current_image = current_image
        images = main_window.image_set.images
        image_names = [image.image_name for sub in images for image in sub]
        self.image_names = image_names
        rgb_names = [band.image_name for band in main_window.image_set.rgb]

        # Create display of image names and highlight the current image/channel
        self.image_list = QtWidgets.QTreeWidget()
        self.image_list.setColumnCount(1)
        self.image_list.setHeaderLabel('Channels')
        self.items = []
        for image_name in image_names:
            self.items.append(QtWidgets.QTreeWidgetItem(self.image_list))
        for index in range(len(self.items)):
            self.items[index].setText(0, image_names[index])
        self.image_list.insertTopLevelItems(1, self.items)
        # Do not allow selection of images from list
        self.image_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        # highlight the current image
        self.current_index = image_names.index(current_image.image_name)
        current_item = self.items[self.current_index]
        current_item.setSelected(True)
        self.image_list.setIndentation(0)
        self.image_list.setFixedWidth(400)

        # Create rgb check-box to toggle display of color or single band image
        # This rgb check box connects with the rgb check box in the main window
        self.rgb_check_box = QtWidgets.QCheckBox("RGB")
        self.rgb_check_box.stateChanged.connect(self.check_rgb)

        # Create Red Menu
        # Create the red menu drop down box
        self.red_menu = QtWidgets.QComboBox()
        red_label = QtWidgets.QLabel("Red")
        red_box = QtWidgets.QHBoxLayout()
        R_index = image_names.index(rgb_names[0])
        self.add_text_to_menu(self.red_menu, image_names, R_index)
        self.create_color_layout(red_label, self.red_menu, red_box)
        # Create red alpha slider
        self.red_alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        red_alpha_value = QtWidgets.QLabel()
        red_alpha_value_container = QtWidgets.QHBoxLayout()
        red_alpha_label = QtWidgets.QLabel('Red %')
        red_alpha_slider_container = QtWidgets.QHBoxLayout()
        red_alpha_container = QtWidgets.QVBoxLayout()
        self.create_slider_layout(
            self.red_alpha_slider, red_alpha_value, red_alpha_label,
            red_alpha_slider_container, red_alpha_value_container,
            red_alpha_container)

        # Create Green Menu
        # Create the green menu drop down box
        self.green_menu = QtWidgets.QComboBox()
        green_label = QtWidgets.QLabel("Green")
        green_box = QtWidgets.QHBoxLayout()
        G_index = image_names.index(rgb_names[1])
        self.add_text_to_menu(self.green_menu, image_names, G_index)
        self.create_color_layout(green_label, self.green_menu, green_box)
        # Create green alpha slider
        self.green_alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        green_alpha_value = QtWidgets.QLabel()
        green_alpha_value_container = QtWidgets.QHBoxLayout()
        green_alpha_label = QtWidgets.QLabel('Green %')
        green_alpha_slider_container = QtWidgets.QHBoxLayout()
        green_alpha_container = QtWidgets.QVBoxLayout()
        self.create_slider_layout(
            self.green_alpha_slider, green_alpha_value, green_alpha_label,
            green_alpha_slider_container, green_alpha_value_container,
            green_alpha_container)

        # Create Blue Menu
        # Create the blue menu drop down box
        self.blue_menu = QtWidgets.QComboBox()
        blue_label = QtWidgets.QLabel("Blue")
        blue_box = QtWidgets.QHBoxLayout()
        B_index = image_names.index(rgb_names[2])
        self.add_text_to_menu(self.blue_menu, image_names, B_index)
        self.create_color_layout(blue_label, self.blue_menu, blue_box)
        # Create blue alpha slider
        self.blue_alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        blue_alpha_value = QtWidgets.QLabel()
        blue_alpha_value_container = QtWidgets.QHBoxLayout()
        blue_alpha_label = QtWidgets.QLabel('Blue %')
        blue_alpha_slider_container = QtWidgets.QHBoxLayout()
        blue_alpha_container = QtWidgets.QVBoxLayout()
        self.create_slider_layout(
            self.blue_alpha_slider, blue_alpha_value, blue_alpha_label,
            blue_alpha_slider_container, blue_alpha_value_container,
            blue_alpha_container)

        # Create a close button
        self.close_button = QtWidgets.QPushButton('Close')
        self.close_button.clicked.connect(self.close_dialog)

        containers = [self.image_list, self.rgb_check_box, red_box,
                      red_alpha_container, green_box,
                      green_alpha_container, blue_box, blue_alpha_container,
                      self.close_button]

        # Set items created above in a grid layout
        self.layout = QtWidgets.QGridLayout()
        row = 0
        for container in containers:
            try:
                self.layout.addLayout(container, row, 0)
                self.layout.setAlignment(container, QtCore.Qt.AlignLeft)
            except:
                self.layout.addWidget(container, row, 0)
                self.layout.setAlignment(container, QtCore.Qt.AlignHCenter)
            row += 1

        self.setLayout(self.layout)
        self.update_menus_index()
        # Match the rgb check box state from the main window
        state = main_window.rgb_check_box.checkState()
        self.rgb_check_box.setCheckState(state)

    def check_rgb(self, state):
        """Displays the rgb image when checked, single band otherwise"""
        if state == QtCore.Qt.Checked:
            self.main_window.rgb_check_box.setCheckState(QtCore.Qt.Checked)
            self.main_window.switch_rgb(state)
            self.create_composite_image()
        elif state == QtCore.Qt.Unchecked:
            self.main_window.rgb_check_box.setCheckState(QtCore.Qt.Unchecked)

    def create_slider_layout(self, slider, value, label, slider_container,
                             value_container, container):
        """Creates the alpha slider layout"""
        slider.setRange(0, 100)
        slider.setValue(100)
        value_container.addWidget(value)
        slider.valueChanged.connect(
            lambda: self.update_alpha_value(slider, value, label))
        slider.sliderReleased.connect(self.create_composite_image)
        slider.setFixedWidth(100)
        value.setNum(slider.value())
        label.setFixedWidth(label.sizeHint().width())
        value.setIndent((slider.width()/100) * slider.value() + label.width())
        slider_container.addWidget(label)
        slider_container.addWidget(slider)
        container.addLayout(value_container)
        container.addLayout(slider_container)
        slider_container.setAlignment(label, QtCore.Qt.AlignLeft)
        slider_container.setAlignment(slider, QtCore.Qt.AlignLeft)
        value_container.setAlignment(value, QtCore.Qt.AlignHCenter)
        container.setAlignment(slider_container, QtCore.Qt.AlignLeft)
        container.setAlignment(value_container, QtCore.Qt.AlignLeft)

    def update_alpha_value(self, slider, slider_value, label):
        """Displays the slider value over the alpha slider cursor"""
        slider_value.setNum(slider.value())
        slider_value.setIndent((
            slider.width() / 100) * slider.value() + label.width())

    def get_alphas(self):
        """Returns the alpha values from each alpha slider"""
        red_alpha = self.red_alpha_slider.value() / 100.
        green_alpha = self.green_alpha_slider.value() / 100.
        blue_alpha = self.blue_alpha_slider.value() / 100.
        alphas = [red_alpha, green_alpha, blue_alpha]
        return alphas

    def add_text_to_menu(self, menu, names, index):
        """Adds the images to the menu & sets the current item in the menu"""
        for name in names:
            menu.addItem(name)
        menu.setCurrentIndex(index)
        menu.activated[int].connect(self.create_composite_image)

    def update_menus_index(self):
        """Updates indices so menu can return to default item"""
        red = self.red_menu.currentIndex()
        green = self.green_menu.currentIndex()
        blue = self.blue_menu.currentIndex()
        self.indices = [red, green, blue]

    def update_menus_current_item(self):
        """Change each menus current item to match the main windows rgb list"""
        rgb_names = [band.image_name for band in self.main_window.rgb]
        indices = [self.image_names.index(rgb_name) for rgb_name in rgb_names]
        menus = [self.red_menu, self.green_menu, self.blue_menu]
        for index, menu in zip(indices, menus):
            menu.setCurrentIndex(index)

    def menus_current_text(self):
        """Returns the text of each menu"""
        red = self.red_menu.currentText()
        green = self.green_menu.currentText()
        blue = self.blue_menu.currentText()
        bands = [red, green, blue]
        return bands

    def create_composite_image(self, index=None):
        """Creates the rgb composite image and displays it"""
        if self.rgb_check_box.checkState() == QtCore.Qt.Unchecked:
            return
        bands = self.menus_current_text()
        alphas = self.get_alphas()
        file_dict = self.main_window.image_set.file_dict
        composite_layers = []
        try:
            for band, alpha in zip(bands, alphas):
                layer = file_dict[band]
                layer_data = layer.data * alpha
                composite_layers.append(layer_data)
            rgb_data = np.dstack(composite_layers)
            self.current_image.set_data(rgb_data)
            self.update_menus_index()
            self.main_window.next_channel_btn.setEnabled(False)
            self.main_window.previous_channel_btn.setEnabled(False)
        except ValueError:
            menus = [self.red_menu, self.green_menu, self.blue_menu]
            for menu, index in zip(menus, self.indices):
                menu.setCurrentIndex(index)
            print("Images must be the same size")
            self.rgb_check_box.setCheckState(QtCore.Qt.Unchecked)

    def create_color_layout(self, label, menu, box):
        """Set the menu and its label next to each other"""
        box.addWidget(label)
        box.addWidget(menu)

    def change_image(self, previous_channel):
        """Change the menu and image list when the image is changed"""
        last_item = self.items[self.current_index + previous_channel]
        channel = self.main_window.image_set.channel
        current_image = self.main_window.image_set.current_image[channel]
        self.current_image = current_image
        self.current_index = self.image_names.index(current_image.image_name)
        current_item = self.items[self.current_index]
        current_item.setSelected(True)
        last_item.setSelected(False)
        self.update_menus_current_item()
        self.create_composite_image()

    def change_channel(self, previous_channel):
        """Move to the next image when next channel is clicked"""
        channel = self.main_window.image_set.channel
        last_item = self.items[self.current_index + previous_channel]
        current_item = self.items[self.current_index + channel]
        current_item.setSelected(True)
        last_item.setSelected(True)

    def close_dialog(self):
        """Close the dialog and save the position"""
        self.main_window.channels_window_is_open = False
        self.main_window.channels_window_pos = self.pos()
        self.hide()
