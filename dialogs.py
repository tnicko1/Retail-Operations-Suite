import copy
from datetime import datetime
import sys
import winsound

import price_generator

import pytz
import base64
import price_generator
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt6.QtCore import Qt, QSize, QEvent, QBuffer, QByteArray
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QFormLayout, QSlider, QLabel, QHBoxLayout, QPushButton,
                             QDialogButtonBox, QLineEdit, QDoubleSpinBox, QSpinBox, QCheckBox, QMessageBox,
                             QListWidget, QListWidgetItem, QTableWidget, QHeaderView, QTableWidgetItem, QInputDialog, QComboBox,
                             QGroupBox, QAbstractItemView, QTextEdit, QWidget, QRadioButton, QButtonGroup, QProgressBar,
                             QFileDialog, QCompleter)
from utils import resource_path
import data_handler
import firebase_handler
from translations import Translator
from utils import format_timedelta
from theme_utils import get_theme_colors


class LayoutSettingsDialog(QDialog):
    def __init__(self, translator, settings, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.parent_window = parent
        # Work on a deep copy so changes can be cancelled
        self.temp_settings = copy.deepcopy(settings)
        self.setWindowTitle(self.translator.get("layout_settings_title"))
        self.setMinimumWidth(500)

        self.layout_settings = self.temp_settings.get("layout_settings", data_handler.get_default_layout_settings())

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.sliders = {}
        self.labels = {}

        # Define slider properties: key, label_key, min_val, max_val
        slider_defs = [
            ("logo_scale", "layout_logo_size", 50, 200),
            ("title_scale", "layout_title_size", 70, 200),
            ("spec_scale", "layout_spec_size", 70, 200),
            ("price_scale", "layout_price_size", 70, 200),
            ("sku_scale", "layout_sku_size", 70, 200),
            ("pn_scale", "layout_pn_size", 70, 200),
        ]

        for key, label_key, min_val, max_val in slider_defs:
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(int(self.layout_settings.get(key, 1.0) * 100))
            slider.valueChanged.connect(self.update_label_and_preview)

            label = QLabel(f"{slider.value()}%")

            self.sliders[key] = slider
            self.labels[key] = label

            row_layout = QHBoxLayout()
            row_layout.addWidget(slider)
            row_layout.addWidget(label)

            form_layout.addRow(self.translator.get(label_key), row_layout)

        self.recent_items_spinbox = QSpinBox()
        self.recent_items_spinbox.setRange(1, 100)
        self.recent_items_spinbox.setValue(self.temp_settings.get("recent_items_max_size", 10))
        self.recent_items_spinbox.valueChanged.connect(self.update_recent_items_max_size)
        form_layout.addRow(self.translator.get("recent_items_max_size_label", "Recent Items History Size:"), self.recent_items_spinbox)

        main_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        reset_button = QPushButton(self.translator.get("layout_reset_button"))
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        button_layout.addStretch()

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout.addLayout(button_layout)

    def update_label_and_preview(self, value):
        # Find which slider was moved
        sender = self.sender()
        for key, slider in self.sliders.items():
            if slider == sender:
                # Update the percentage label
                self.labels[key].setText(f"{slider.value()}%")
                # Update the temporary settings dictionary
                self.layout_settings[key] = slider.value() / 100.0
                # Trigger a real-time preview update in the main window
                if self.parent_window:
                    self.parent_window.settings['layout_settings'] = self.layout_settings
                    self.parent_window.update_preview()
                break

    def update_recent_items_max_size(self, value):
        self.temp_settings["recent_items_max_size"] = value
        if self.parent_window:
            self.parent_window.settings["recent_items_max_size"] = value
            self.parent_window.update_recent_items_list()


    def reset_to_defaults(self):
        defaults = data_handler.get_default_layout_settings()
        for key, slider in self.sliders.items():
            slider.setValue(int(defaults.get(key, 1.0) * 100))

        default_settings = data_handler.get_default_settings()
        self.recent_items_spinbox.setValue(default_settings.get("recent_items_max_size", 10))


    def get_settings(self):
        return self.temp_settings


class AddEditSizeDialog(QDialog):
    def __init__(self, translator, size_data=None, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.get("size_dialog_edit_title") if size_data else self.translator.get(
            "size_dialog_add_title"))

        self.size_data = {}
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.width_input = QDoubleSpinBox()
        self.width_input.setRange(1, 50)
        self.width_input.setDecimals(2)
        self.width_input.setSuffix(" cm")
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(1, 50)
        self.height_input.setDecimals(2)
        self.height_input.setSuffix(" cm")
        self.speclimit_input = QSpinBox()
        self.speclimit_input.setRange(0, 50)
        self.accessory_checkbox = QCheckBox()

        if size_data:
            self.name_input.setText(size_data.get('name'))
            self.width_input.setValue(size_data.get('dims', [0, 0])[0])
            self.height_input.setValue(size_data.get('dims', [0, 0])[1])
            self.speclimit_input.setValue(size_data.get('spec_limit', 0))
            self.accessory_checkbox.setChecked(size_data.get('is_accessory_style', False))

        layout.addRow(self.translator.get("size_dialog_name"), self.name_input)
        layout.addRow(self.translator.get("size_dialog_width"), self.width_input)
        layout.addRow(self.translator.get("size_dialog_height"), self.height_input)
        layout.addRow(self.translator.get("size_dialog_spec_limit"), self.speclimit_input)
        layout.addRow(self.translator.get("size_dialog_accessory_style"), self.accessory_checkbox)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

    def accept(self):
        name = self.name_input.text().strip()
        if not name:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Size name cannot be empty.")
            msg.setWindowTitle("Input Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        self.size_data = {
            "name": name,
            "dims": [self.width_input.value(), self.height_input.value()],
            "spec_limit": self.speclimit_input.value(),
            "is_accessory_style": self.accessory_checkbox.isChecked()
        }
        super().accept()

    def get_size_data(self):
        return self.size_data


class CustomSizeManagerDialog(QDialog):
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.settings = data_handler.get_settings()
        # Work on a copy of the custom sizes
        self.custom_sizes = self.settings.get("custom_sizes", {}).copy()

        self.setWindowTitle(self.translator.get("size_manager_title"))
        self.setMinimumSize(700, 450)

        main_layout = QVBoxLayout(self)

        # Table for sizes
        self.size_table = QTableWidget()
        self.size_table.setColumnCount(5)
        self.size_table.setHorizontalHeaderLabels([
            self.translator.get("size_dialog_name"),
            self.translator.get("size_dialog_width"),
            self.translator.get("size_dialog_height"),
            self.translator.get("size_dialog_spec_limit"),
            self.translator.get("size_dialog_accessory_style")
        ])
        self.size_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.size_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.size_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.size_table.doubleClicked.connect(self.edit_size)
        main_layout.addWidget(self.size_table)

        # Buttons with icons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(self.translator.get("add_button"))
        self.add_btn.setIcon(QIcon(price_generator.resource_path("assets/spec_icons/plus.svg")))
        self.add_btn.clicked.connect(self.add_size)

        self.edit_btn = QPushButton(self.translator.get("edit_button"))
        self.edit_btn.setIcon(QIcon(price_generator.resource_path("assets/spec_icons/cog.svg")))
        self.edit_btn.clicked.connect(self.edit_size)

        self.remove_btn = QPushButton(self.translator.get("remove_button"))
        self.remove_btn.setIcon(QIcon(price_generator.resource_path("assets/spec_icons/shredder.svg")))
        self.remove_btn.clicked.connect(self.remove_size)

        button_layout.addStretch()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.remove_btn)
        main_layout.addLayout(button_layout)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.populate_table()

    def populate_table(self):
        self.size_table.setRowCount(0)
        for name, data in sorted(self.custom_sizes.items()):
            row_position = self.size_table.rowCount()
            self.size_table.insertRow(row_position)
            self.size_table.setItem(row_position, 0, QTableWidgetItem(name))
            self.size_table.setItem(row_position, 1, QTableWidgetItem(f"{data['dims'][0]:.2f} cm"))
            self.size_table.setItem(row_position, 2, QTableWidgetItem(f"{data['dims'][1]:.2f} cm"))
            self.size_table.setItem(row_position, 3, QTableWidgetItem(str(data['spec_limit'])))

            accessory_item = QTableWidgetItem("Yes" if data.get('is_accessory_style', False) else "No")
            accessory_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.size_table.setItem(row_position, 4, accessory_item)

    def add_size(self):
        dialog = AddEditSizeDialog(self.translator, parent=self)
        if dialog.exec():
            new_size = dialog.get_size_data()
            self.custom_sizes[new_size['name']] = {
                "dims": new_size['dims'],
                "spec_limit": new_size['spec_limit'],
                "is_accessory_style": new_size['is_accessory_style']
            }
            self.populate_table()

    def edit_size(self):
        selected_row = self.size_table.currentRow()
        if selected_row < 0:
            return

        name = self.size_table.item(selected_row, 0).text()
        size_data_to_edit = self.custom_sizes[name]
        size_data_to_edit['name'] = name

        dialog = AddEditSizeDialog(self.translator, size_data=size_data_to_edit, parent=self)
        if dialog.exec():
            edited_size = dialog.get_size_data()
            if name != edited_size['name']:
                del self.custom_sizes[name]

            self.custom_sizes[edited_size['name']] = {
                "dims": edited_size['dims'],
                "spec_limit": edited_size['spec_limit'],
                "is_accessory_style": edited_size['is_accessory_style']
            }
            self.populate_table()

    def remove_size(self):
        selected_row = self.size_table.currentRow()
        if selected_row < 0:
            return

        name = self.size_table.item(selected_row, 0).text()
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(self.translator.get("remove_size_message", name))
        msg.setWindowTitle(self.translator.get("remove_size_title"))
        msg.addButton(QMessageBox.StandardButton.Yes)
        msg.addButton(QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            del self.custom_sizes[name]
            self.populate_table()

    def get_updated_sizes(self):
        return self.custom_sizes

    def accept(self):
        # The saving will be handled by the main window
        super().accept()



class QuickStockDialog(QDialog):
    def __init__(self, translator, token, branch_map, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.token = token
        self.branch_map = branch_map
        self.setWindowTitle(self.translator.get("stock_checker_title"))
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        # Input section
        input_layout = QHBoxLayout()
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText(self.translator.get("sku_placeholder"))
        self.sku_input.returnPressed.connect(self.check_stock)
        self.check_button = QPushButton(self.translator.get("stock_checker_button"))
        self.check_button.clicked.connect(self.check_stock)
        input_layout.addWidget(self.sku_input)
        input_layout.addWidget(self.check_button)
        layout.addLayout(input_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels([
            self.translator.get("stock_checker_branch_header"),
            self.translator.get("stock_checker_stock_header")
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.results_table)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.translator.get("stock_checker_title"))
        self.sku_input.setPlaceholderText(self.translator.get("sku_placeholder"))
        self.check_button.setText(self.translator.get("stock_checker_button"))
        self.results_table.setHorizontalHeaderLabels([
            self.translator.get("stock_checker_branch_header"),
            self.translator.get("stock_checker_stock_header")
        ])

    def check_stock(self):
        self.results_table.setRowCount(0)
        identifier = self.sku_input.text().strip()
        if not identifier:
            return

        # Automatically prefix with 'I' if it's a 5-digit number
        if len(identifier) == 5 and identifier.isdigit():
            identifier = f"I{identifier}"
            self.sku_input.setText(identifier)

        item_data = firebase_handler.find_item_by_identifier(identifier.upper(), self.token)
        if not item_data:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.translator.get("sku_not_found_message", identifier))
            msg.setWindowTitle(self.translator.get("sku_not_found_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        self.setWindowTitle(f"{self.translator.get('stock_checker_title')} - {item_data.get('Name')}")
        self.results_table.setRowCount(len(self.branch_map))

        for i, (branch_key, branch_info) in enumerate(self.branch_map.items()):
            branch_name = self.translator.get(branch_key)
            stock_col = branch_info['stock_col']
            stock_level = item_data.get(stock_col, "0")

            self.results_table.setItem(i, 0, QTableWidgetItem(branch_name))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(stock_level)))


class TemplateSelectionDialog(QDialog):
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.get("template_selection_title"))
        self.selected_template_key = None
        self.selected_template_data = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(self.translator.get("template_selection_label")))

        self.template_list = QListWidget()
        self.templates = data_handler.get_item_templates(parent.token if parent else None)
        for key in self.templates.keys():
            self.template_list.addItem(self.templates[key]['category_name'])
        self.template_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.template_list)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        selected_item = self.template_list.currentItem()
        if not selected_item:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.translator.get("template_validation_error_message"))
            msg.setWindowTitle(self.translator.get("template_validation_error_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        selected_name = selected_item.text()
        for key, value in self.templates.items():
            if value['category_name'] == selected_name:
                self.selected_template_key = key
                self.selected_template_data = value
                break

        super().accept()


class NewItemDialog(QDialog):
    def __init__(self, sku, translator, template=None, category_name=None, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.new_item_data = {"SKU": sku}
        if category_name:
            self.new_item_data["Categories"] = category_name

        self.setWindowTitle(self.translator.get("new_item_dialog_title"))
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.sku_label = QLineEdit(sku)
        self.sku_label.setReadOnly(True)
        self.name_input = QLineEdit()
        self.part_number_input = QLineEdit()
        self.price_input = QLineEdit()
        self.sale_price_input = QLineEdit()
        self.specs_input = QTextEdit()

        if template:
            specs_text = "\n".join([f"{spec}:" for spec in template])
            self.specs_input.setPlainText(specs_text)
        else:
            self.specs_input.setPlaceholderText(self.translator.get("new_item_specs_placeholder"))

        form_layout.addRow(self.translator.get("new_item_sku_label"), self.sku_label)
        form_layout.addRow(self.translator.get("new_item_name_label"), self.name_input)
        form_layout.addRow(self.translator.get("part_number_label"), self.part_number_input)
        form_layout.addRow(self.translator.get("new_item_price_label"), self.price_input)
        form_layout.addRow(self.translator.get("new_item_sale_price_label"), self.sale_price_input)
        form_layout.addRow(self.translator.get("new_item_specs_label"), self.specs_input)
        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self.translator.get("new_item_save_button"))
        self.button_box.accepted.connect(self.save_item)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def save_item(self):
        name = self.name_input.text().strip()
        if not name:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.translator.get("new_item_name_empty_error"))
            msg.setWindowTitle(self.translator.get("new_item_validation_error"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        self.new_item_data["Name"] = name
        self.new_item_data["Regular price"] = self.price_input.text().strip()
        self.new_item_data["Sale price"] = self.sale_price_input.text().strip()
        self.new_item_data["isManual"] = True

        part_number = self.part_number_input.text().strip()
        if part_number:
            # Store it in both places for consistency with how existing data is handled
            self.new_item_data['part_number'] = part_number
            if 'attributes' not in self.new_item_data:
                self.new_item_data['attributes'] = {}
            self.new_item_data['attributes']['Part Number'] = part_number

        specs_html = "".join(
            [f"<li>{line}</li>" for line in self.specs_input.toPlainText().strip().split('\n') if line and ':' in line])
        self.new_item_data["Description"] = f"<ul>{specs_html}</ul>"

        self.accept()



class PrintQueueDialog(QDialog):
    def __init__(self, translator, user, all_items_cache, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.user = user
        self.uid = self.user.get('localId')
        self.token = self.user.get('idToken')
        self.parent_window = parent
        self.all_items_cache = all_items_cache or {}

        self.setWindowTitle(self.translator.get("print_queue_title"))
        self.setMinimumSize(600, 700)

        main_layout = QVBoxLayout(self)

        add_group = QGroupBox(self.translator.get("print_queue_add_item_group"))
        add_layout = QHBoxLayout()
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText(self.translator.get("sku_placeholder"))
        self.add_button = QPushButton(self.translator.get("print_queue_add_button"))
        self.add_button.clicked.connect(self.add_item_from_input)
        add_layout.addWidget(self.sku_input)
        add_layout.addWidget(self.add_button)
        add_group.setLayout(add_layout)
        main_layout.addWidget(add_group)

        queue_group = QGroupBox(self.translator.get("print_queue_skus_group"))
        queue_layout = QVBoxLayout()
        self.sku_list_widget = QTableWidget()
        self.sku_list_widget.setColumnCount(2)
        self.sku_list_widget.setHorizontalHeaderLabels([self.translator.get("sku_label"), self.translator.get("name_label")])
        self.sku_list_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.sku_list_widget.setColumnWidth(0, 80)
        self.sku_list_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.sku_list_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sku_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.sku_list_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        queue_layout.addWidget(self.sku_list_widget)

        buttons_layout = QHBoxLayout()
        self.remove_button = QPushButton(self.translator.get("print_queue_remove_button"))
        self.remove_button.clicked.connect(self.remove_selected)
        self.clear_button = QPushButton(self.translator.get("print_queue_clear_button"))
        self.clear_button.clicked.connect(self.clear_queue)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        queue_layout.addLayout(buttons_layout)
        queue_group.setLayout(queue_layout)
        main_layout.addWidget(queue_group)

        saved_group = QGroupBox(self.translator.get("print_queue_load_save_group"))
        saved_layout = QHBoxLayout()
        self.saved_lists_combo = QComboBox()
        self.load_button = QPushButton(self.translator.get("print_queue_load_button"))
        self.load_button.clicked.connect(self.load_list)
        self.save_button = QPushButton(self.translator.get("print_queue_save_button"))
        self.save_button.clicked.connect(self.save_list)
        self.delete_list_button = QPushButton(self.translator.get("print_queue_delete_button"))
        self.delete_list_button.clicked.connect(self.delete_list)
        self.upload_excel_button = QPushButton(self.translator.get("upload_excel_button"))
        self.upload_excel_button.clicked.connect(self.load_from_excel)
        saved_layout.addWidget(self.saved_lists_combo)
        saved_layout.addWidget(self.load_button)
        saved_layout.addWidget(self.save_button)
        saved_layout.addWidget(self.delete_list_button)
        saved_layout.addWidget(self.upload_excel_button)
        saved_group.setLayout(saved_layout)
        main_layout.addWidget(saved_group)

        self.modern_design_checkbox = QCheckBox("Use Modern Design for all applicable brands")
        main_layout.addWidget(self.modern_design_checkbox)

        self.use_default_settings_checkbox = QCheckBox("Use Default Settings for selected paper size")
        main_layout.addWidget(self.use_default_settings_checkbox)

        action_buttons_layout = QHBoxLayout()
        self.print_list_button = QPushButton(self.translator.get("print_queue_print_list_button", "Print Item List"))
        self.print_list_button.setFixedHeight(40)
        self.print_list_button.clicked.connect(self.print_item_list)
        action_buttons_layout.addWidget(self.print_list_button)

        self.generate_button = QPushButton(self.translator.get("print_queue_generate_button"))
        self.generate_button.setFixedHeight(40)
        self.generate_button.clicked.connect(self.accept)
        action_buttons_layout.addWidget(self.generate_button)
        main_layout.addLayout(action_buttons_layout)

        self.load_saved_lists()
        self.load_queue()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.sku_input.hasFocus():
                self.add_item_from_input()
                return
        super().keyPressEvent(event)

    def add_item_from_input(self):
        identifier = self.sku_input.text().strip()
        if not identifier: return

        # Automatically prefix with 'I' if it's a 5-digit number
        if len(identifier) == 5 and identifier.isdigit():
            identifier = f"I{identifier}"
            self.sku_input.setText(identifier)

        item_data = firebase_handler.find_item_by_identifier(identifier.upper(), self.token)
        if not item_data:
            if sys.platform == "win32":
                winsound.Beep(440, 100)
                winsound.Beep(440, 100)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.translator.get("sku_not_found_message", identifier))
            msg.setWindowTitle(self.translator.get("sku_not_found_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        sku_to_add = item_data.get('SKU')

        # Check for duplicates only if the selected size is NOT the accessory size
        if self.parent_window and self.parent_window.paper_size_combo.currentText() != "6x3.5cm":
            # Extract SKU from the list items for comparison
            current_skus = [self.sku_list_widget.item(i).text().split(' - ')[0] for i in range(self.sku_list_widget.count())]
            if sku_to_add in current_skus:
                if sys.platform == "win32":
                    winsound.Beep(440, 100)
                    winsound.Beep(440, 100)
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText(self.translator.get("batch_duplicate_message", sku_to_add))
                msg.setWindowTitle(self.translator.get("batch_duplicate_title"))
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()
                return

        name = item_data.get('Name', 'Unknown Name')
        row_position = self.sku_list_widget.rowCount()
        self.sku_list_widget.insertRow(row_position)
        self.sku_list_widget.setItem(row_position, 0, QTableWidgetItem(sku_to_add))
        self.sku_list_widget.setItem(row_position, 1, QTableWidgetItem(name))
        self.save_queue()
        self.sku_input.clear()
        if sys.platform == "win32":
            winsound.Beep(880, 150)

    def load_from_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.translator.get("select_excel_file"), "", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path, header=None) # Read without header
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(f"Failed to read Excel file: {e}")
            msg.setWindowTitle("Error")
            msg.exec()
            return

        # Find the cell containing 'No.'
        start_row, start_col = -1, -1
        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                if str(df.iat[r, c]).strip() == 'No.':
                    start_row, start_col = r, c
                    break
            if start_row != -1:
                break

        skus_from_excel = []
        if start_row != -1:
            # If 'No.' was found, get SKUs from the column below it
            skus_from_excel = df.iloc[start_row + 1:, start_col].dropna().astype(str).tolist()
        else:
            # If 'No.' was not found, assume the first column contains the SKUs
            if not df.empty:
                skus_from_excel = df.iloc[:, 0].dropna().astype(str).tolist()

        if not skus_from_excel:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("No SKUs found in the Excel file.")
            msg.setWindowTitle("No Data")
            msg.exec()
            return

        # Automatically prefix with 'I' if it's a 5-digit number
        skus_from_excel = [f"I{sku}" if len(sku) == 5 and sku.isdigit() else sku for sku in skus_from_excel]

        branch_db_key = self.parent_window.branch_combo.currentData()
        on_display_data = firebase_handler.get_display_status(self.token).get(branch_db_key, {})
        on_display_skus = {str(key) for key in on_display_data.keys()}

        current_skus_in_queue = {self.sku_list_widget.item(i, 0).text() for i in range(self.sku_list_widget.rowCount()) if self.sku_list_widget.item(i, 0)}
        added_count = 0
        for sku in skus_from_excel:
            if sku in on_display_skus and sku not in current_skus_in_queue:
                item_data = self.all_items_cache.get(sku, {})
                name = item_data.get('Name', 'Unknown Name')
                row_position = self.sku_list_widget.rowCount()
                self.sku_list_widget.insertRow(row_position)
                self.sku_list_widget.setItem(row_position, 0, QTableWidgetItem(sku))
                self.sku_list_widget.setItem(row_position, 1, QTableWidgetItem(name))
                added_count += 1

        if added_count > 0:
            self.save_queue()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"Added {added_count} items to the print queue.")
        msg.setWindowTitle("Success")
        msg.exec()

    def load_queue(self):
        self.sku_list_widget.setRowCount(0) # Clear table
        queue_data = firebase_handler.get_print_queue(self.user)
        if queue_data:
            for sku in queue_data:
                item_data = self.all_items_cache.get(sku, {})
                name = item_data.get('Name', 'Unknown Name')
                row_position = self.sku_list_widget.rowCount()
                self.sku_list_widget.insertRow(row_position)
                self.sku_list_widget.setItem(row_position, 0, QTableWidgetItem(sku))
                self.sku_list_widget.setItem(row_position, 1, QTableWidgetItem(name))

    def save_queue(self):
        queue_items = [self.sku_list_widget.item(i).text().split(' - ')[0] for i in range(self.sku_list_widget.count())]
        firebase_handler.save_print_queue(self.user, queue_items)

    def load_saved_lists(self):
        self.saved_lists_combo.clear()
        saved_lists = firebase_handler.get_saved_batch_lists(self.user)
        if saved_lists:
            self.saved_lists_combo.addItems(sorted(saved_lists.keys()))

    def remove_selected(self):
        selected_rows = sorted(set(index.row() for index in self.sku_list_widget.selectedIndexes()), reverse=True)
        for row in selected_rows:
            self.sku_list_widget.removeRow(row)
        self.save_queue()

    def clear_queue(self):
        self.sku_list_widget.clear()
        self.save_queue()

    def load_list(self):
        list_name = self.saved_lists_combo.currentText()
        if not list_name: return

        all_lists = firebase_handler.get_saved_batch_lists(self.user)
        skus_to_load = all_lists.get(list_name, [])
        self.sku_list_widget.setRowCount(0) # Clear table
        for sku in skus_to_load:
            item_data = self.all_items_cache.get(sku, {})
            name = item_data.get('Name', 'Unknown Name')
            row_position = self.sku_list_widget.rowCount()
            self.sku_list_widget.insertRow(row_position)
            self.sku_list_widget.setItem(row_position, 0, QTableWidgetItem(sku))
            self.sku_list_widget.setItem(row_position, 1, QTableWidgetItem(name))
        self.save_queue()

    def save_list(self):
        current_queue = [self.sku_list_widget.item(i).text().split(' - ')[0] for i in range(self.sku_list_widget.count())]
        if not current_queue:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Cannot save an empty queue.")
            msg.setWindowTitle("Empty Queue")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        list_name, ok = QInputDialog.getText(self, self.translator.get("print_queue_save_prompt"), "List Name:")
        if ok and list_name:
            firebase_handler.save_batch_list(self.user, list_name, current_queue)
            self.load_saved_lists()
            self.saved_lists_combo.setCurrentText(list_name)

    def delete_list(self):
        list_name = self.saved_lists_combo.currentText()
        if not list_name: return

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(self.translator.get("print_queue_delete_confirm", list_name))
        msg.setWindowTitle("Delete List")
        msg.addButton(QMessageBox.StandardButton.Yes)
        msg.addButton(QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        reply = msg.exec()
        if reply == QMessageBox.StandardButton.Yes:
            firebase_handler.delete_batch_list(self.user, list_name)
            self.load_saved_lists()

    def get_skus(self):
        skus = []
        for row in range(self.sku_list_widget.rowCount()):
            item = self.sku_list_widget.item(row, 0) # Get item from SKU column
            if item:
                skus.append(item.text())
        return skus

    def get_modern_design_state(self):
        return self.modern_design_checkbox.isChecked()

    def get_use_default_settings_state(self):
        return self.use_default_settings_checkbox.isChecked()

    def print_item_list(self):
        if self.sku_list_widget.count() == 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("The print queue is empty.")
            msg.setWindowTitle("Empty Queue")
            msg.exec()
            return

        html_content = self._generate_item_list_html()
        if not html_content:
            return

        document = QTextEdit()
        document.setHtml(html_content)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.paintRequested.connect(document.print)
        preview_dialog.exec()

    def _generate_item_list_html(self):
        try:
            with open(resource_path("assets/logo.png"), "rb") as f:
                logo_data = f.read()

            pixmap = QPixmap()
            pixmap.loadFromData(logo_data)

            # Resize the pixmap to a height of 25px, keeping aspect ratio
            scaled_pixmap = pixmap.scaledToHeight(25, Qt.TransformationMode.SmoothTransformation)

            buffer = QBuffer()
            buffer.open(QBuffer.OpenModeFlag.ReadWrite)
            scaled_pixmap.save(buffer, "PNG")

            # Base64 encode the image data
            logo_src = f"data:image/png;base64,{buffer.data().toBase64().data().decode()}"

        except FileNotFoundError:
            logo_src = ""

        items_html = ""
        for i in range(self.sku_list_widget.count()):
            item_text = self.sku_list_widget.item(i).text()
            sku = item_text.split(" - ")[0]
            item_data = self.all_items_cache.get(sku, {})

            name = item_data.get("Name", "N/A")

            # Find Part Number from attributes
            attributes = item_data.get('attributes', {})
            part_number = ''
            if attributes:
                for attr_i in range(1, 10): # Check up to 10 attributes
                    if attributes.get(f'Attribute {attr_i} name') == 'Part Number':
                        part_number = attributes.get(f'Attribute {attr_i} value(s)', '')
                        break
            if not part_number:
                 part_number = item_data.get('part_number', '')

            price = item_data.get("Sale price") or item_data.get("Regular price") or "N/A"


            items_html += f"""
                <tr>
                    <td>{i + 1}</td>
                    <td>{sku}</td>
                    <td>{name}</td>
                    <td>{part_number}</td>
                    <td>{price}</td>
                </tr>
            """

        return f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
                body {{
                    font-family: 'Roboto', sans-serif;
                    margin: 40px;
                    color: #333;
                }}
                .header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header img {{
                    width: auto;
                }}
                .header h1 {{
                    font-size: 18px; /* Slightly lower font size */
                    font-weight: 700;
                    color: #222;
                    margin: 0;
                }}
                .date {{
                    font-size: 14px;
                    color: #777;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 48px; /* Much larger font size */
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 18px 20px;
                    text-align: left;
                }}
                th {{
                    background-color: #f8f8f8;
                    font-weight: 700;
                    color: #555;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #eee;
                    font-size: 36px;
                    color: #777;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <img src="{logo_src}" alt="Company Logo">
                <h1>Item Collection List</h1>
                <div class="date">{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
            </div>
            <p>Here are the items to be collected from storage for display. Please handle with care.</p>
            <table>
                <thead>
                    <tr>
                        <th>Order</th>
                        <th>SKU</th>
                        <th>Item Name</th>
                        <th>Part Number</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            <div class="footer">
                <p>Happy hunting! May your carts be full and your steps be few.</p>
            </div>
        </body>
        </html>
        """


class BrandSelectionDialog(QDialog):
    def __init__(self, translator, brand_name, brand_options, item_data, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.brand_name = brand_name
        self.brand_options = brand_options  # This is a dict {key: config}
        self.item_data = item_data
        self.parent_window = parent
        self.selected_key = None

        self.setWindowTitle(translator.get("brand_selection_title", brand_name=brand_name))
        self.setMinimumWidth(800)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel(translator.get("brand_selection_prompt", brand_name=brand_name)))

        previews_layout = QHBoxLayout()
        self.button_group = QButtonGroup(self)

        # Get common data for preview generation from parent
        size_name = self.parent_window.paper_size_combo.currentText()
        size_config = self.parent_window.paper_sizes[size_name]
        layout_settings = self.parent_window.settings.get("layout_settings", data_handler.get_default_layout_settings())
        data_to_print = self.parent_window._prepare_data_for_printing(self.item_data)
        is_special = self.parent_window.special_tag_checkbox.isChecked()

        # A separate background cache for this dialog's previews
        background_cache = {}

        first_button = None
        for key, config in self.brand_options.items():
            preview_group = QGroupBox(key)
            preview_group_layout = QVBoxLayout()

            # Radio button for selection
            radio_button = QRadioButton(key)
            self.button_group.addButton(radio_button)

            # Store the key in the button itself
            radio_button.key = key

            # Generate preview
            preview_label = QLabel()
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.setMinimumSize(300, 400)  # Adjust size as needed
            colors = get_theme_colors()
            preview_label.setStyleSheet(f"border: 1px solid {colors["preview_border"]}; background-color: {colors["preview_bg"]};")

            theme_config = copy.deepcopy(self.parent_window.themes["Default"])
            theme_config.update(config)

            # Simplified preview generation
            lang = 'en' if size_config.get("is_accessory_style", False) else self.translator.language
            img = price_generator.create_price_tag(data_to_print, size_config, theme_config, layout_settings,
                                                   language=lang, is_special=is_special,
                                                   background_cache=background_cache)
            q_image = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            preview_label.setPixmap(
                pixmap.scaled(preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation))

            preview_group_layout.addWidget(radio_button)
            preview_group_layout.addWidget(preview_label)
            preview_group.setLayout(preview_group_layout)
            previews_layout.addWidget(preview_group)

            if not first_button:
                first_button = radio_button

        main_layout.addLayout(previews_layout)

        self.choose_for_all_checkbox = QCheckBox(translator.get("brand_selection_choose_all", brand_name=self.brand_name))
        main_layout.addWidget(self.choose_for_all_checkbox)

        if first_button:
            first_button.setChecked(True)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def accept(self):
        checked_button = self.button_group.checkedButton()
        if checked_button:
            self.selected_key = checked_button.key
        super().accept()

    def get_selected_brand_key(self):
        return self.selected_key

    def is_choice_for_all(self):
        return self.choose_for_all_checkbox.isChecked()


class PriceHistoryDialog(QDialog):
    def __init__(self, sku, translator, token, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translator.get("price_history_title", sku))
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            translator.get("price_history_header_date"),
            translator.get("price_history_header_old"),
            translator.get("price_history_header_new")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        history_data = firebase_handler.get_item_price_history(sku, token)
        self.table.setRowCount(len(history_data))

        for row, entry in enumerate(sorted(history_data, key=lambda x: x['timestamp'], reverse=True)):
            self.table.setItem(row, 0, QTableWidgetItem(entry.get("timestamp")))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("old_price")))
            self.table.setItem(row, 2, QTableWidgetItem(entry.get("new_price")))


class TemplateManagerDialog(QDialog):
    def __init__(self, translator, token, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.token = token
        self.setWindowTitle(self.translator.get("template_manager_title"))
        self.setMinimumSize(800, 600)

        self.templates = data_handler.get_item_templates(self.token)

        main_layout = QHBoxLayout(self)

        cat_group = QGroupBox(self.translator.get("template_manager_categories_group"))
        cat_layout = QVBoxLayout()
        self.cat_list = QListWidget()
        self.cat_list.currentTextChanged.connect(self.populate_specs)
        cat_layout.addWidget(self.cat_list)

        cat_buttons = QHBoxLayout()
        add_cat_btn = QPushButton(self.translator.get("template_manager_add_cat_button"))
        add_cat_btn.clicked.connect(self.add_category)
        rename_cat_btn = QPushButton(self.translator.get("template_manager_rename_cat_button"))
        rename_cat_btn.clicked.connect(self.rename_category)
        del_cat_btn = QPushButton(self.translator.get("template_manager_delete_cat_button"))
        del_cat_btn.clicked.connect(self.delete_category)
        cat_buttons.addWidget(add_cat_btn)
        cat_buttons.addWidget(rename_cat_btn)
        cat_buttons.addWidget(del_cat_btn)
        cat_layout.addLayout(cat_buttons)
        cat_group.setLayout(cat_layout)

        self.spec_group = QGroupBox()
        spec_layout = QVBoxLayout()
        self.spec_list = QListWidget()
        spec_layout.addWidget(self.spec_list)

        spec_buttons = QHBoxLayout()
        add_spec_btn = QPushButton(self.translator.get("template_manager_add_spec_button"))
        add_spec_btn.clicked.connect(self.add_spec)
        del_spec_btn = QPushButton(self.translator.get("template_manager_remove_spec_button"))
        del_spec_btn.clicked.connect(self.remove_spec)
        spec_buttons.addWidget(add_spec_btn)
        spec_buttons.addWidget(del_spec_btn)
        spec_layout.addLayout(spec_buttons)
        self.spec_group.setLayout(spec_layout)

        main_layout.addWidget(cat_group, 1)
        main_layout.addWidget(self.spec_group, 1)

        bottom_layout = QVBoxLayout()
        main_layout.addLayout(bottom_layout)

        save_button = QPushButton(self.translator.get("template_manager_save_button"))
        save_button.setFixedHeight(40)
        save_button.clicked.connect(self.save_templates)

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        dialog_buttons.rejected.connect(self.reject)

        bottom_container = QWidget()
        bottom_container_layout = QVBoxLayout(bottom_container)
        bottom_container_layout.addStretch()
        bottom_container_layout.addWidget(save_button)
        bottom_container_layout.addWidget(dialog_buttons)

        main_layout.addWidget(bottom_container)

        self.populate_categories()

    def populate_categories(self):
        self.cat_list.clear()
        for key in sorted(self.templates.keys()):
            self.cat_list.addItem(self.templates[key]['category_name'])

    def get_current_cat_key(self):
        current_item = self.cat_list.currentItem()
        if not current_item: return None
        current_name = current_item.text()
        for key, value in self.templates.items():
            if value['category_name'] == current_name:
                return key
        return None

    def populate_specs(self, cat_name):
        self.spec_list.clear()
        self.spec_group.setTitle(self.translator.get("template_manager_specs_group", cat_name))
        key = self.get_current_cat_key()
        if key and 'specs' in self.templates[key]:
            self.spec_list.addItems(self.templates[key]['specs'])

    def add_category(self):
        text, ok = QInputDialog.getText(self, "Add Category", self.translator.get("template_manager_new_cat_prompt"))
        if ok and text:
            new_key = f"template_{text.lower().replace(' ', '_')}"
            self.templates[new_key] = {"category_name": text, "specs": []}
            self.populate_categories()
            for i in range(self.cat_list.count()):
                if self.cat_list.item(i).text() == text:
                    self.cat_list.setCurrentRow(i)
                    break

    def rename_category(self):
        key = self.get_current_cat_key()
        if not key: return

        old_name = self.templates[key]['category_name']
        text, ok = QInputDialog.getText(self, "Rename Category",
                                        self.translator.get("template_manager_rename_prompt", old_name), text=old_name)
        if ok and text and text != old_name:
            self.templates[key]['category_name'] = text
            self.populate_categories()
            for i in range(self.cat_list.count()):
                if self.cat_list.item(i).text() == text:
                    self.cat_list.setCurrentRow(i)
                    break

    def delete_category(self):
        key = self.get_current_cat_key()
        if not key: return

        name = self.templates[key]['category_name']
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(self.translator.get("template_manager_delete_cat_confirm_msg", name))
        msg.setWindowTitle(self.translator.get("template_manager_delete_cat_confirm_title"))
        msg.addButton(QMessageBox.StandardButton.Yes)
        msg.addButton(QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        reply = msg.exec()
        if reply == QMessageBox.StandardButton.Yes:
            del self.templates[key]
            self.populate_categories()

    def add_spec(self):
        key = self.get_current_cat_key()
        if not key: return

        text, ok = QInputDialog.getText(self, "Add Specification",
                                        self.translator.get("template_manager_new_spec_prompt"))
        if ok and text:
            if 'specs' not in self.templates[key]:
                self.templates[key]['specs'] = []
            self.templates[key]['specs'].append(text)
            self.populate_specs(self.templates[key]['category_name'])

    def remove_spec(self):
        key = self.get_current_cat_key()
        spec_item = self.spec_list.currentItem()
        if not key or not spec_item: return

        self.templates[key]['specs'].remove(spec_item.text())
        self.populate_specs(self.templates[key]['category_name'])

    def save_templates(self):
        if firebase_handler.save_templates_to_firebase(self.templates, self.token):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(self.translator.get("templates_saved_success"))
            msg.setWindowTitle(self.translator.get("success_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(self.translator.get("templates_saved_fail"))
            msg.setWindowTitle("Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()


class ActivityLogDialog(QDialog):
    def __init__(self, translator, token, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translator.get("activity_log_title"))
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            translator.get("activity_log_header_time"),
            translator.get("activity_log_header_email"),
            translator.get("activity_log_header_action")
        ])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 200)
        layout.addWidget(self.table)

        log_data = firebase_handler.get_activity_log(token)
        self.table.setRowCount(len(log_data))

        for row, entry in enumerate(log_data):  # Already sorted in firebase_handler
            self.table.setItem(row, 0, QTableWidgetItem(entry.get("timestamp")))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("email")))
            self.table.setItem(row, 2, QTableWidgetItem(entry.get("message")))

class MultiSelectCategoryDialog(QDialog):
    def __init__(self, translator, categories, selected_categories, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.get("category_selection_title"))
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout(self)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Categories...")
        self.search_input.textChanged.connect(self.filter_categories)
        layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        for category in categories:
            item = QListWidgetItem(category)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            check_state = Qt.CheckState.Checked if category in selected_categories else Qt.CheckState.Unchecked
            item.setCheckState(check_state)
            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def filter_categories(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def get_selected_categories(self):
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected



class DisplayManagerDialog(QDialog):
    def __init__(self, translator, branch_db_key, branch_stock_col, user, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.parent = parent
        self.branch_db_key = branch_db_key
        self.branch_stock_col = branch_stock_col
        self.user = user
        self.token = self.user.get('idToken') if self.user else None
        self.setWindowTitle(self.translator.get("display_manager_title"))
        self.setMinimumSize(900, 700)

        self.original_suggestions = []
        self.current_sort_column = -1
        self.current_sort_order = None
        self.selected_categories = []

        # --- Main Layout ---
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        self.setStyleSheet("""
            QGroupBox {
                font-size: 11pt;
                font-weight: bold;
            }
            QLabel {
                font-size: 10pt;
            }
            QPushButton {
                font-size: 10pt;
                padding: 8px;
            }
            QTableWidget {
                font-size: 10pt;
            }
        """)

        # --- Find by Category Group ---
        self.find_group = QGroupBox(self.translator.get("find_by_category_group"))
        find_layout = QFormLayout(self.find_group)
        find_layout.setSpacing(10)
        self.category_button = QPushButton(self.translator.get("all_categories_placeholder"))
        self.category_button.clicked.connect(self.open_category_selection)
        self.find_by_category_button = QPushButton(self.translator.get("find_available_button"))
        self.find_by_category_button.clicked.connect(self.find_available_for_display)
        find_layout.addRow(self.translator.get("category_label"), self.category_button)
        find_layout.addRow(self.find_by_category_button)


        # --- Return Item Group ---
        self.return_group = QGroupBox(self.translator.get("return_tag_group"))
        return_layout = QFormLayout(self.return_group)
        return_layout.setSpacing(10)
        self.return_input = QLineEdit()
        self.return_input.setPlaceholderText(self.translator.get("return_tag_placeholder"))
        self.return_input.returnPressed.connect(self.find_replacements_for_return)
        self.find_replacements_button = QPushButton(self.translator.get("find_replacements_button"))
        self.find_replacements_button.clicked.connect(self.find_replacements_for_return)
        return_layout.addRow(self.translator.get("return_tag_label"), self.return_input)
        return_layout.addRow(self.find_replacements_button)


        # --- Available for Display Group ---
        self.suggestions_group = QGroupBox(self.translator.get("suggestions_group_empty"))
        suggestions_layout = QVBoxLayout(self.suggestions_group)
        self.suggestions_table = QTableWidget()
        self.suggestions_table.setColumnCount(5)
        self.suggestions_table.setHorizontalHeaderLabels([
            self.translator.get("suggestions_header_sku"),
            self.translator.get("suggestions_header_name"),
            self.translator.get("suggestions_stock_header"),
            self.translator.get("suggestions_header_price"),
            self.translator.get("suggestions_header_action")
        ])
        self.suggestions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.suggestions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.suggestions_table.horizontalHeader().sectionClicked.connect(self.handle_header_click)
        suggestions_layout.addWidget(self.suggestions_table)

        # --- Actions Group ---
        self.actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(self.actions_group)
        self.export_button = QPushButton(self.translator.get("export_to_excel_button", "Export to Excel"))
        self.export_button.setIcon(QIcon(price_generator.resource_path("assets/spec_icons/archive-restore.svg")))
        self.export_button.clicked.connect(self.export_to_excel)
        actions_layout.addStretch()
        actions_layout.addWidget(self.export_button)


        top_layout = QHBoxLayout()
        top_layout.addWidget(self.find_group, 1)
        top_layout.addWidget(self.return_group, 1)

        layout.addLayout(top_layout)
        layout.addWidget(self.suggestions_group, 5)
        layout.addWidget(self.actions_group)


        self.retranslate_ui()

    def retranslate_ui(self):
        """Updates all translatable text in the dialog."""
        self.setWindowTitle(self.translator.get("display_manager_title"))
        self.find_group.setTitle(self.translator.get("find_by_category_group"))
        self.category_button.setText(self.translator.get("all_categories_placeholder"))
        self.find_by_category_button.setText(self.translator.get("find_available_button"))
        self.update_category_button_text()
        self.return_group.setTitle(self.translator.get("return_tag_group"))
        self.find_replacements_button.setText(self.translator.get("find_replacements_button"))
        self.export_button.setText(self.translator.get("export_to_excel_button", "Export to Excel"))
        self.suggestions_table.setHorizontalHeaderLabels([
            self.translator.get("suggestions_header_sku"),
            self.translator.get("suggestions_header_name"),
            self.translator.get("suggestions_stock_header"),
            self.translator.get("suggestions_header_price"),
            self.translator.get("suggestions_header_action")
        ])


    def get_all_categories(self):
        if self.parent and self.parent.all_items_cache:
            return sorted(list(
                set(item.get("Categories", "N/A") for item in self.parent.all_items_cache.values() if
                    item.get("Categories"))))
        return []

    def open_category_selection(self):
        all_categories = self.get_all_categories()
        dialog = MultiSelectCategoryDialog(self.translator, all_categories, self.selected_categories, self)
        if dialog.exec():
            self.selected_categories = dialog.get_selected_categories()
            self.update_category_button_text()

    def update_category_button_text(self):
        if not self.selected_categories:
            self.category_button.setText(self.translator.get("all_categories_placeholder"))
        elif len(self.selected_categories) == 1:
            self.category_button.setText(self.selected_categories[0])
        else:
            self.category_button.setText(f"{len(self.selected_categories)} categories selected")

    def find_available_for_display(self):
        if not self.selected_categories:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.translator.get("category_selection_error_message"))
            msg.setWindowTitle(self.translator.get("template_validation_error_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        branch_name = self.parent.branch_combo.currentText()
        self.suggestions_group.setTitle(self.translator.get("available_for_display_group_title", ", ".join(self.selected_categories), branch_name))

        self.original_suggestions = []
        for category in self.selected_categories:
            self.original_suggestions.extend(firebase_handler.get_available_items_for_display(
                category, self.branch_db_key, self.branch_stock_col, self.token
            ))
        self.current_sort_column = -1
        self.current_sort_order = None
        self.sort_and_repopulate()

    def find_replacements_for_return(self):
        identifier = self.return_input.text().strip()
        if not identifier: return

        # Automatically prefix with 'I' if it's a 5-digit number
        if len(identifier) == 5 and identifier.isdigit():
            identifier = f"I{identifier}"
            self.return_input.setText(identifier)

        item_data = firebase_handler.find_item_by_identifier(identifier.upper(), self.token)
        if not item_data:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.translator.get("sku_not_found_message", identifier))
            msg.setWindowTitle(self.translator.get("sku_not_found_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        sku = item_data.get('SKU')
        firebase_handler.remove_item_from_display(sku, self.branch_db_key, self.token)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(self.translator.get("item_returned_message", sku))
        msg.setWindowTitle(self.translator.get("success_title"))
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        msg.exec()
        self.return_input.clear()

        category = item_data.get('Categories', 'N/A')
        branch_name = self.parent.branch_combo.currentText()
        self.suggestions_group.setTitle(self.translator.get("suggestions_group_filled", category, branch_name))

        self.original_suggestions = firebase_handler.get_replacement_suggestions(category, self.branch_db_key,
                                                                                 self.branch_stock_col, self.token)

        self.original_suggestions = [item for item in self.original_suggestions if item.get('SKU') != sku]

        self.current_sort_column = -1
        self.current_sort_order = None
        self.sort_and_repopulate()
        self.update_header_indicators()

        if self.parent and self.parent.current_item_data.get('SKU') == sku:
            self.parent.update_status_display()

    def handle_header_click(self, logicalIndex):
        if logicalIndex == 4: return

        if self.current_sort_column == logicalIndex:
            if self.current_sort_order == Qt.SortOrder.AscendingOrder:
                self.current_sort_order = Qt.SortOrder.DescendingOrder
            else:
                self.current_sort_column = -1
                self.current_sort_order = None
        else:
            self.current_sort_column = logicalIndex
            self.current_sort_order = Qt.SortOrder.AscendingOrder

        self.sort_and_repopulate()

    def _get_sort_key(self, item):
        column = self.current_sort_column
        try:
            if column == 0:
                return item.get('SKU', '')
            elif column == 1:
                return item.get('Name', '').lower()
            elif column == 2:
                stock_str = str(item.get(self.branch_stock_col, '0'))
                return int(stock_str.replace(',', ''))
            elif column == 3:
                return self._get_price_for_sort(item)
        except (ValueError, TypeError):
            return 0
        return item

    def sort_and_repopulate(self):
        display_list = self.original_suggestions.copy()

        if self.current_sort_column != -1 and self.current_sort_order is not None:
            reverse = self.current_sort_order == Qt.SortOrder.DescendingOrder
            display_list.sort(key=self._get_sort_key, reverse=reverse)

        self.populate_suggestions(display_list)
        self.update_header_indicators()

    def update_header_indicators(self):
        header = self.suggestions_table.horizontalHeader()
        header_keys = ['sku', 'name', 'stock', 'price', 'action']
        for i in range(header.count()):
            original_text = self.translator.get(f"suggestions_header_{header_keys[i]}")
            if i == self.current_sort_column:
                arrow = '▲' if self.current_sort_order == Qt.SortOrder.AscendingOrder else '▼'
                header.model().setHeaderData(i, Qt.Orientation.Horizontal, f"{original_text} {arrow}")
            else:
                header.model().setHeaderData(i, Qt.Orientation.Horizontal, original_text)

    def populate_suggestions(self, suggestions):
        self.suggestions_table.setRowCount(0)
        if not suggestions: return

        self.suggestions_table.setRowCount(len(suggestions))
        for row, item in enumerate(suggestions):
            price_value = self._get_price_for_sort(item)
            display_price = f"₾{price_value:.2f}" if price_value > 0 else "N/A"

            self.suggestions_table.setItem(row, 0, QTableWidgetItem(item.get('SKU')))
            self.suggestions_table.setItem(row, 1, QTableWidgetItem(item.get('Name')))
            self.suggestions_table.setItem(row, 2, QTableWidgetItem(str(item.get(self.branch_stock_col, '0'))))
            self.suggestions_table.setItem(row, 3, QTableWidgetItem(display_price))

            add_to_queue_button = QPushButton(self.translator.get("add_to_print_queue_button", "Add to Print Queue"))
            add_to_queue_button.clicked.connect(lambda checked, sku=item.get('SKU'): self.add_to_print_queue(sku))
            self.suggestions_table.setCellWidget(row, 4, add_to_queue_button)

    def add_to_print_queue(self, sku):
        if self.parent:
            self.parent.add_sku_to_print_queue(sku)
            # Maybe provide some feedback to the user, e.g., a status bar message
            self.parent.statusBar().showMessage(f"SKU {sku} added to print queue.", 3000)


    def _get_price_for_sort(self, item):
        try:
            sale_price_str = str(item.get('Sale price', '')).strip().replace(',', '.')
            if sale_price_str and float(sale_price_str) > 0:
                return float(sale_price_str)

            regular_price_str = str(item.get('Regular price', '')).strip().replace(',', '.')
            if regular_price_str:
                return float(regular_price_str)
        except (ValueError, TypeError):
            pass
        return 0

    def quick_print_tag(self, sku):
        if self.parent:
            self.parent.generate_single_by_sku(sku, mark_on_display=True)
            self.original_suggestions = [item for item in self.original_suggestions if item.get('SKU') != sku]
            self.sort_and_repopulate()

    def export_to_excel(self):
        if self.suggestions_table.rowCount() == 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("There is no data to export.")
            msg.setWindowTitle("Export Empty")
            msg.exec()
            return

        settings = data_handler.get_settings()
        default_path = settings.get("default_export_path", "")

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", default_path, "Excel Files (*.xlsx)")

        if not file_path:
            return

        # Save the selected directory for next time
        settings["default_export_path"] = file_path
        data_handler.save_settings(settings)

        column_headers = []
        for j in range(self.suggestions_table.columnCount() -1): # Exclude the action column
            column_headers.append(self.suggestions_table.horizontalHeaderItem(j).text())

        data = []
        for i in range(self.suggestions_table.rowCount()):
            row_data = []
            for j in range(self.suggestions_table.columnCount() - 1): # Exclude the action column
                item = self.suggestions_table.item(i, j)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        df = pd.DataFrame(data, columns=column_headers)

        try:
            df.to_excel(file_path, index=False)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(f"Data exported successfully to {file_path}")
            msg.setWindowTitle("Export Successful")
            msg.exec()
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(f"Failed to export data: {e}")
            msg.setWindowTitle("Export Error")
            msg.exec()


class ExportStockDialog(QDialog):
    def __init__(self, translator, token, branch_map, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.token = token
        self.branch_map = branch_map
        self.parent = parent
        self.selected_categories = []

        self.setWindowTitle("Export Stock Information")
        self.setMinimumSize(500, 200)

        layout = QVBoxLayout(self)

        self.category_button = QPushButton("Select Categories")
        self.category_button.clicked.connect(self.open_category_selection)
        layout.addWidget(self.category_button)

        self.export_button = QPushButton("Export to Excel")
        self.export_button.clicked.connect(self.export_to_excel)
        layout.addWidget(self.export_button)

    def get_all_categories(self):
        if self.parent and self.parent.all_items_cache:
            return sorted(list(
                set(item.get("Categories", "N/A") for item in self.parent.all_items_cache.values() if
                    item.get("Categories"))))
        return []

    def open_category_selection(self):
        all_categories = self.get_all_categories()
        dialog = MultiSelectCategoryDialog(self.translator, all_categories, self.selected_categories, self)
        if dialog.exec():
            self.selected_categories = dialog.get_selected_categories()
            self.update_category_button_text()

    def update_category_button_text(self):
        if not self.selected_categories:
            self.category_button.setText("Select Categories")
        elif len(self.selected_categories) == 1:
            self.category_button.setText(self.selected_categories[0])
        else:
            self.category_button.setText(f"{len(self.selected_categories)} categories selected")

    def export_to_excel(self):
        if not self.selected_categories:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Please select at least one category.")
            msg.setWindowTitle("No Categories Selected")
            msg.exec()
            return

        branch_key = self.parent.logistics_branch_combo.currentData()
        if not branch_key or branch_key == "all":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Please select a single branch in the Logistics tab.")
            msg.setWindowTitle("No Branch Selected")
            msg.exec()
            return

        branch_info = self.branch_map[branch_key]
        stock_col = branch_info['stock_col']

        items_to_export = []
        for sku, item_data in self.parent.all_items_cache.items():
            if item_data.get("Categories") in self.selected_categories:
                stock_str = str(item_data.get(stock_col, '0')).replace(',', '')
                if stock_str.isdigit() and int(stock_str) > 0:
                    items_to_export.append({
                        "SKU": sku,
                        "Name": item_data.get("Name", "N/A"),
                        "Category": item_data.get("Categories", "N/A"),
                        "Stock": int(stock_str)
                    })

        if not items_to_export:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("No items with stock found in the selected categories for this branch.")
            msg.setWindowTitle("No Data to Export")
            msg.exec()
            return

        df = pd.DataFrame(items_to_export)

        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
            if file_path:
                df.to_excel(file_path, index=False)
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText(f"Data exported successfully to {file_path}")
                msg.setWindowTitle("Export Successful")
                msg.exec()
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(f"Failed to export data: {e}")
            msg.setWindowTitle("Export Error")
            msg.exec()


class UserManagementDialog(QDialog):
    def __init__(self, translator, user, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.user = user
        self.token = self.user.get('idToken') if self.user else None
        self.setWindowTitle(self.translator.get("admin_manage_users"))
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            self.translator.get("user_mgmt_header_email"),
            self.translator.get("user_mgmt_header_role"),
            self.translator.get("user_mgmt_header_action")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)
        self.load_users()

    def load_users(self):
        self.table.setRowCount(0)
        users = firebase_handler.get_all_users(self.token)
        if not users: return

        self.table.setRowCount(len(users))
        for row_num, user_data in enumerate(users):
            self.table.setItem(row_num, 0, QTableWidgetItem(user_data.get("email", "")))
            self.table.setItem(row_num, 1, QTableWidgetItem(user_data.get("role", "")))

            if user_data.get("role") != "Admin":
                promote_button = QPushButton(self.translator.get("user_mgmt_promote_button"))
                promote_button.clicked.connect(lambda _, u=user_data: self.promote_user(u))
                self.table.setCellWidget(row_num, 2, promote_button)

    def promote_user(self, user_data):
        uid = user_data.get("uid")
        email = user_data.get("email")
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(self.translator.get("user_mgmt_confirm_promote_message", email))
        msg.setWindowTitle(self.translator.get("user_mgmt_confirm_promote_title"))
        msg.addButton(QMessageBox.StandardButton.Yes)
        msg.addButton(QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        reply = msg.exec()
        if reply == QMessageBox.StandardButton.Yes:
            if firebase_handler.promote_user_to_admin(uid, self.token):
                self.load_users()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Failed to promote user.")
                msg.setWindowTitle("Error")
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()


class ColumnMappingManagerDialog(QDialog):
    def __init__(self, translator, token, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.token = token
        self.parent_window = parent
        self.setWindowTitle(self.translator.get("column_mapping_title"))
        self.setMinimumSize(950, 600)

        self.mappings = firebase_handler.get_column_mappings(self.token)
        self.example_values = {}
        self.barcode_checkboxes = []  # To manage radio-button behavior

        layout = QVBoxLayout(self)

        # --- Controls ---
        controls_layout = QHBoxLayout()
        info_label = QLabel(self.translator.get("column_mapping_info"))
        refresh_button = QPushButton(self.translator.get("column_mapping_refresh_button"))
        refresh_button.clicked.connect(self.refresh_keys)
        controls_layout.addWidget(info_label)
        controls_layout.addStretch()
        controls_layout.addWidget(refresh_button)
        layout.addLayout(controls_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            self.translator.get("column_mapping_header_original"),
            self.translator.get("column_mapping_header_example"),
            self.translator.get("column_mapping_header_display"),
            self.translator.get("column_mapping_header_ignore"),
            self.translator.get("column_mapping_header_is_barcode")
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        layout.addWidget(self.table)

        # --- Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_mappings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.refresh_keys()

    def refresh_keys(self):
        """Fetch all unique attribute keys and examples from Firebase and populate the table."""
        all_keys, self.example_values = firebase_handler.get_attributes_with_examples(self.token)
        self.table.setRowCount(0)  # Clear table before populating
        self.barcode_checkboxes.clear() # Clear the list of checkboxes

        current_keys_in_table = set()

        # Use a combined and sorted list of keys from mappings and fetched keys
        # Exclude the special 'barcodeField' from this list
        mapping_keys = [k for k in self.mappings.keys() if k != 'barcodeField']
        combined_keys = sorted(list(all_keys.union(set(mapping_keys))))

        for key in combined_keys:
            if key not in current_keys_in_table:
                self.add_key_to_table(key)
                current_keys_in_table.add(key)

    def add_key_to_table(self, key):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Column 0: Original Name (read-only)
        original_item = QTableWidgetItem(key)
        original_item.setFlags(original_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, original_item)

        # Column 1: Example Value (read-only)
        example_value = self.example_values.get(key, "")
        example_item = QTableWidgetItem(str(example_value))
        example_item.setFlags(example_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        example_item.setToolTip(str(example_value)) # Show full value on hover
        self.table.setItem(row, 1, example_item)

        # Column 2: Display Name (QLineEdit)
        display_name_input = QLineEdit()
        mapping_data = self.mappings.get(key, {})
        # Ensure mapping_data is a dictionary before calling .get()
        if isinstance(mapping_data, dict):
            display_name_input.setText(mapping_data.get('displayName', ''))
        self.table.setCellWidget(row, 2, display_name_input)

        # Column 3: Ignore (QCheckBox)
        ignore_checkbox = QCheckBox()
        if isinstance(mapping_data, dict):
            ignore_checkbox.setChecked(mapping_data.get('ignore', False))
        ignore_cell_widget = QWidget()
        ignore_cell_layout = QHBoxLayout(ignore_cell_widget)
        ignore_cell_layout.addWidget(ignore_checkbox)
        ignore_cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ignore_cell_layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 3, ignore_cell_widget)

        # Column 4: Is Barcode (QCheckBox)
        barcode_checkbox = QCheckBox()
        barcode_checkbox.setChecked(key == self.mappings.get("barcodeField"))
        barcode_checkbox.stateChanged.connect(self.handle_barcode_checkbox_state_changed)
        self.barcode_checkboxes.append(barcode_checkbox)
        barcode_cell_widget = QWidget()
        barcode_cell_layout = QHBoxLayout(barcode_cell_widget)
        barcode_cell_layout.addWidget(barcode_checkbox)
        barcode_cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        barcode_cell_layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 4, barcode_cell_widget)

    def handle_barcode_checkbox_state_changed(self, state):
        """Ensures only one barcode checkbox can be checked at a time."""
        if state == Qt.CheckState.Checked.value:
            sender = self.sender()
            for checkbox in self.barcode_checkboxes:
                if checkbox != sender:
                    checkbox.setChecked(False)

    def save_mappings(self):
        """Read the table and save the mappings to Firebase."""
        new_mappings = {}
        barcode_field = None

        for row in range(self.table.rowCount()):
            original_name = self.table.item(row, 0).text()

            display_name_widget = self.table.cellWidget(row, 2)
            display_name = display_name_widget.text().strip() if display_name_widget else ""

            ignore_widget_container = self.table.cellWidget(row, 3)
            is_ignored = False
            if ignore_widget_container:
                ignore_checkbox = ignore_widget_container.layout().itemAt(0).widget()
                is_ignored = ignore_checkbox.isChecked()

            barcode_widget_container = self.table.cellWidget(row, 4)
            is_barcode = False
            if barcode_widget_container:
                barcode_checkbox = barcode_widget_container.layout().itemAt(0).widget()
                if barcode_checkbox.isChecked():
                    barcode_field = original_name

            # Only create an entry if there's something to save
            if display_name or is_ignored:
                new_mappings[original_name] = {
                    'displayName': display_name,
                    'ignore': is_ignored
                }

        # Add the special barcodeField key to the top level of the mappings
        if barcode_field:
            new_mappings['barcodeField'] = barcode_field

        if firebase_handler.save_column_mappings(new_mappings, self.token):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Column mappings saved successfully.")
            msg.setWindowTitle("Success")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            if self.parent_window:
                self.parent_window.column_mappings = new_mappings
                self.parent_window.update_preview()
            self.accept()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("Failed to save column mappings.")
            msg.setWindowTitle("Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()

class QRCodeURLDialog(QDialog):
    def __init__(self, translator, item_name, sku, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.sku = sku
        # Using hardcoded strings as I cannot modify the translations dictionary.
        self.setWindowTitle("QR Code URL")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        message = QLabel(f"Could not automatically find a URL for the item: <b>{item_name}</b> (SKU: {sku}).<br><br>Please provide a URL for the QR code, or press Skip to not include a QR code for this item.")
        message.setWordWrap(True)
        layout.addWidget(message)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/product/...")
        layout.addWidget(self.url_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("OK")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Skip")

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        button_layout = QHBoxLayout()
        copy_sku_button = QPushButton("Copy SKU")
        copy_sku_button.clicked.connect(self.copy_sku)
        button_layout.addWidget(copy_sku_button)
        button_layout.addStretch()
        button_layout.addWidget(self.button_box)

        layout.addLayout(button_layout)

        self.url = None

    def copy_sku(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.sku)

    def accept(self):
        self.url = self.url_input.text().strip()
        if not self.url:
            # Maybe show a warning, but for now, just treat as accept with no URL
             super().accept()
             return
        super().accept()

    def get_url(self):
        return self.url

class QRGenerationProgressDialog(QDialog):
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle("Generating QR Codes...")
        self.setMinimumWidth(500)
        self.setModal(True) # Block interaction with the main window

        layout = QVBoxLayout(self)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.log_widget = QListWidget()
        layout.addWidget(self.log_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.item_count = 0
        self.processed_count = 0
        self.user_cancelled = False

    def set_total_items(self, count):
        self.item_count = count
        self.progress_bar.setRange(0, count)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"%v / %m Items ({0:.0f}%)")

    def update_progress(self, item_name, status, url=None):
        if self.user_cancelled:
            return

        if status == 'searching':
            self.log_widget.addItem(f"Searching for '{item_name}'...")
        elif status == 'success':
            self.log_widget.addItem(f"  ✓ Found: {url}")
            self.processed_count += 1
        elif status == 'fail':
            self.log_widget.addItem(f"  ✗ Failed to find URL for '{item_name}'.")
            self.processed_count += 1 # Still counts as processed
        elif status == 'cached':
             self.log_widget.addItem(f"  ✓ Using cached URL for '{item_name}'.")
             self.processed_count += 1

        self.progress_bar.setValue(self.processed_count)
        percentage = (self.processed_count / self.item_count * 100) if self.item_count > 0 else 0
        self.progress_bar.setFormat(f"%v / %m Items ({percentage:.0f}%)")
        QApplication.processEvents() # Keep UI responsive

    def prompt_for_url(self, item_name, sku):
        if self.user_cancelled:
            return None
        self.log_widget.addItem(f"  Action Required: Please provide a URL for '{item_name}'.")
        dialog = QRCodeURLDialog(self.translator, item_name, sku, self)
        if dialog.exec():
            url = dialog.get_url()
            if url:
                self.log_widget.addItem(f"  ✓ User provided URL: {url}")
            else:
                self.log_widget.addItem("  ✗ User skipped providing a URL.")
            return url
        else: # User clicked Skip in the URL dialog
            self.log_widget.addItem("  ✗ User skipped providing a URL.")
            return None

    def reject(self):
        self.user_cancelled = True
        self.log_widget.addItem("Operation cancelled by user.")
        super().reject()

    def was_cancelled(self):
        return self.user_cancelled