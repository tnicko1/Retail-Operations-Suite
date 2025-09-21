import copy
from datetime import datetime
import sys
import winsound

import pytz
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QSlider, QLabel, QHBoxLayout, QPushButton,
                             QDialogButtonBox, QLineEdit, QDoubleSpinBox, QSpinBox, QCheckBox, QMessageBox,
                             QListWidget, QTableWidget, QHeaderView, QTableWidgetItem, QInputDialog, QComboBox,
                             QGroupBox, QAbstractItemView, QTextEdit, QWidget)

import data_handler
import firebase_handler
from translations import Translator
from utils import format_timedelta


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

    def update_label_and_preview(self):
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

    def reset_to_defaults(self):
        defaults = data_handler.get_default_layout_settings()
        for key, slider in self.sliders.items():
            slider.setValue(int(defaults.get(key, 1.0) * 100))

    def get_layout_settings(self):
        return self.layout_settings


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
        self.setWindowTitle(self.translator.get("size_manager_title"))
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        self.size_list = QListWidget()
        self.populate_list()
        layout.addWidget(self.size_list)

        button_layout = QHBoxLayout()
        add_btn = QPushButton(self.translator.get("add_button"))
        add_btn.clicked.connect(self.add_size)
        edit_btn = QPushButton(self.translator.get("edit_button"))
        edit_btn.clicked.connect(self.edit_size)
        remove_btn = QPushButton(self.translator.get("remove_button"))
        remove_btn.clicked.connect(self.remove_size)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(remove_btn)
        layout.addLayout(button_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def populate_list(self):
        self.size_list.clear()
        for name in sorted(self.settings.get("custom_sizes", {}).keys()):
            self.size_list.addItem(name)

    def add_size(self):
        dialog = AddEditSizeDialog(self.translator, parent=self)
        if dialog.exec():
            new_size = dialog.get_size_data()
            self.settings["custom_sizes"][new_size['name']] = {
                "dims": new_size['dims'],
                "spec_limit": new_size['spec_limit'],
                "is_accessory_style": new_size['is_accessory_style']
            }
            self.populate_list()

    def edit_size(self):
        current_item = self.size_list.currentItem()
        if not current_item:
            return

        name = current_item.text()
        size_data_to_edit = self.settings["custom_sizes"][name]
        size_data_to_edit['name'] = name

        dialog = AddEditSizeDialog(self.translator, size_data=size_data_to_edit, parent=self)
        if dialog.exec():
            edited_size = dialog.get_size_data()
            # Remove old entry if name changed
            if name != edited_size['name']:
                del self.settings["custom_sizes"][name]

            self.settings["custom_sizes"][edited_size['name']] = {
                "dims": edited_size['dims'],
                "spec_limit": edited_size['spec_limit'],
                "is_accessory_style": edited_size['is_accessory_style']
            }
            self.populate_list()

    def remove_size(self):
        current_item = self.size_list.currentItem()
        if not current_item:
            return

        name = current_item.text()
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(self.translator.get("remove_size_message", name))
        msg.setWindowTitle(self.translator.get("remove_size_title"))
        msg.addButton(QMessageBox.StandardButton.Yes)
        msg.addButton(QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            del self.settings["custom_sizes"][name]
            self.populate_list()

    def accept(self):
        data_handler.save_settings(self.settings)
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
    def __init__(self, translator, user, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.user = user
        self.uid = self.user.get('localId')
        self.token = self.user.get('idToken')
        self.parent_window = parent

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
        self.sku_list_widget = QListWidget()
        self.sku_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
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
        saved_layout.addWidget(self.saved_lists_combo)
        saved_layout.addWidget(self.load_button)
        saved_layout.addWidget(self.save_button)
        saved_layout.addWidget(self.delete_list_button)
        saved_group.setLayout(saved_layout)
        main_layout.addWidget(saved_group)

        self.modern_design_checkbox = QCheckBox("Use Modern Design for all applicable brands")
        main_layout.addWidget(self.modern_design_checkbox)

        self.generate_button = QPushButton(self.translator.get("print_queue_generate_button"))
        self.generate_button.setFixedHeight(40)
        self.generate_button.clicked.connect(self.accept)
        main_layout.addWidget(self.generate_button)

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
            if sku_to_add in [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]:
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

        self.sku_list_widget.addItem(sku_to_add)
        self.save_queue()
        self.sku_input.clear()
        if sys.platform == "win32":
            winsound.Beep(880, 150)

    def load_queue(self):
        self.sku_list_widget.clear()
        queue_data = firebase_handler.get_print_queue(self.user)
        if queue_data:
            self.sku_list_widget.addItems(queue_data)

    def save_queue(self):
        queue_items = [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]
        firebase_handler.save_print_queue(self.user, queue_items)

    def load_saved_lists(self):
        self.saved_lists_combo.clear()
        saved_lists = firebase_handler.get_saved_batch_lists(self.user)
        if saved_lists:
            self.saved_lists_combo.addItems(sorted(saved_lists.keys()))

    def remove_selected(self):
        for item in self.sku_list_widget.selectedItems():
            self.sku_list_widget.takeItem(self.sku_list_widget.row(item))
        self.save_queue()

    def clear_queue(self):
        self.sku_list_widget.clear()
        self.save_queue()

    def load_list(self):
        list_name = self.saved_lists_combo.currentText()
        if not list_name: return

        all_lists = firebase_handler.get_saved_batch_lists(self.user)
        skus_to_load = all_lists.get(list_name, [])
        self.sku_list_widget.clear()
        self.sku_list_widget.addItems(skus_to_load)
        self.save_queue()

    def save_list(self):
        current_queue = [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]
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
        return [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]

    def get_modern_design_state(self):
        return self.modern_design_checkbox.isChecked()


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

        layout = QVBoxLayout(self)

        # --- NEW: Find by Category Group ---
        self.find_group = QGroupBox(self.translator.get("find_by_category_group"))
        find_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.find_by_category_button = QPushButton(self.translator.get("find_available_button"))
        self.find_by_category_button.clicked.connect(self.find_available_for_display)
        self.category_label = QLabel(self.translator.get("category_label"))
        find_layout.addWidget(self.category_label)
        find_layout.addWidget(self.category_combo)
        find_layout.addWidget(self.find_by_category_button)
        self.find_group.setLayout(find_layout)
        self.populate_category_combo()

        # --- Return Item Group ---
        self.return_group = QGroupBox(self.translator.get("return_tag_group"))
        return_layout = QHBoxLayout()
        self.return_input = QLineEdit()
        self.return_input.setPlaceholderText(self.translator.get("return_tag_placeholder"))
        self.return_input.returnPressed.connect(self.find_replacements_for_return)
        self.find_replacements_button = QPushButton(self.translator.get("find_replacements_button"))
        self.find_replacements_button.clicked.connect(self.find_replacements_for_return)
        self.return_tag_label = QLabel(self.translator.get("return_tag_label"))
        return_layout.addWidget(self.return_tag_label)
        return_layout.addWidget(self.return_input)
        return_layout.addWidget(self.find_replacements_button)
        self.return_group.setLayout(return_layout)

        # --- Suggestions Group (reused for both actions) ---
        self.suggestions_group = QGroupBox(self.translator.get("suggestions_group_empty"))
        suggestions_layout = QVBoxLayout()
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
        self.suggestions_group.setLayout(suggestions_layout)

        layout.addWidget(self.find_group)
        layout.addWidget(self.return_group)
        layout.addWidget(self.suggestions_group)

        self.retranslate_ui()

    def retranslate_ui(self):
        """Updates all translatable text in the dialog."""
        self.setWindowTitle(self.translator.get("display_manager_title"))
        self.find_group.setTitle(self.translator.get("find_by_category_group"))
        self.category_label.setText(self.translator.get("category_label"))
        self.find_by_category_button.setText(self.translator.get("find_available_button"))

        # Repopulate combo to update the placeholder
        current_data = self.category_combo.currentData()
        self.populate_category_combo()
        index = self.category_combo.findData(current_data)
        if index != -1:
            self.category_combo.setCurrentIndex(index)

        self.return_group.setTitle(self.translator.get("return_tag_group"))
        self.return_tag_label.setText(self.translator.get("return_tag_label"))
        self.return_input.setPlaceholderText(self.translator.get("return_tag_placeholder"))
        self.find_replacements_button.setText(self.translator.get("find_replacements_button"))

        # Update table headers and button text within the table
        self.update_header_indicators()
        for row in range(self.suggestions_table.rowCount()):
            button = self.suggestions_table.cellWidget(row, 4)
            if button:
                button.setText(self.translator.get("quick_print_button"))

    def populate_category_combo(self):
        self.category_combo.clear()
        self.category_combo.addItem(self.translator.get("all_categories_placeholder"), "all")
        if self.parent and self.parent.all_items_cache:
            categories = sorted(list(
                set(item.get("Categories", "N/A") for item in self.parent.all_items_cache.values() if
                    item.get("Categories"))))
            self.category_combo.addItems(categories)

    def find_available_for_display(self):
        category = self.category_combo.currentText()
        if self.category_combo.currentData() == "all":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.translator.get("category_selection_error_message"))
            msg.setWindowTitle(self.translator.get("template_validation_error_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        branch_name = self.parent.branch_combo.currentText()
        self.suggestions_group.setTitle(self.translator.get("available_for_display_group_title", category, branch_name))

        self.original_suggestions = firebase_handler.get_available_items_for_display(
            category, self.branch_db_key, self.branch_stock_col, self.token
        )

        self.current_sort_column = -1
        self.current_sort_order = None
        self.populate_suggestions(self.original_suggestions)
        self.update_header_indicators()

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
        self.populate_suggestions(self.original_suggestions)
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

        if self.current_sort_order is not None:
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

            print_button = QPushButton(self.translator.get("quick_print_button"))
            print_button.clicked.connect(lambda checked, sku=item.get('SKU'): self.quick_print_tag(sku))
            self.suggestions_table.setCellWidget(row, 4, print_button)

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