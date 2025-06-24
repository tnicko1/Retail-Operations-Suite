import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QFormLayout, QGroupBox, QComboBox, QMessageBox, QDialog,
                             QDialogButtonBox, QAbstractItemView, QTextEdit, QCheckBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog)
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

import data_handler
import price_generator
import a4_layout_generator
from translations import Translator


class NewItemDialog(QDialog):
    def __init__(self, sku, translator, parent=None):
        super().__init__(parent)
        self.tr, self.new_item_data = translator, {"SKU": sku}
        self.setWindowTitle(self.tr.get("new_item_dialog_title"));
        self.setMinimumWidth(500)
        layout, form_layout = QVBoxLayout(self), QFormLayout()
        self.sku_label, self.name_input, self.price_input, self.sale_price_input, self.specs_input = QLineEdit(
            sku), QLineEdit(), QLineEdit(), QLineEdit(), QTextEdit()
        self.sku_label.setReadOnly(True);
        self.specs_input.setPlaceholderText(self.tr.get("new_item_specs_placeholder"))
        form_layout.addRow(self.tr.get("new_item_sku_label"), self.sku_label);
        form_layout.addRow(self.tr.get("new_item_name_label"), self.name_input)
        form_layout.addRow(self.tr.get("new_item_price_label"), self.price_input);
        form_layout.addRow(self.tr.get("new_item_sale_price_label"), self.sale_price_input)
        form_layout.addRow(self.tr.get("new_item_specs_label"), self.specs_input);
        layout.addLayout(form_layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self.tr.get("new_item_save_button"))
        self.button_box.accepted.connect(self.save_item);
        self.button_box.rejected.connect(self.reject);
        layout.addWidget(self.button_box)

    def save_item(self):
        name = self.name_input.text().strip()
        if not name: QMessageBox.warning(self, self.tr.get("new_item_validation_error"),
                                         self.tr.get("new_item_name_empty_error")); return
        self.new_item_data["Name"], self.new_item_data["Regular price"], self.new_item_data[
            "Sale price"] = name, self.price_input.text().strip(), self.sale_price_input.text().strip()
        self.new_item_data["Description"] = "<ul>" + "".join(
            [f"<li>{s}</li>" for s in self.specs_input.toPlainText().strip().split('\n') if s]) + "</ul>";
        self.accept()


class BatchDialog(QDialog):
    def __init__(self, max_items, translator, dual_lang_enabled, parent=None):
        super().__init__(parent)
        self.tr = translator
        self.max_items = max_items // 2 if dual_lang_enabled else max_items
        self.setWindowTitle(self.tr.get("batch_dialog_title"));
        self.setMinimumSize(400, 500)
        layout = QVBoxLayout(self)
        self.list_label = QLabel(self.tr.get("batch_list_label", self.max_items))
        self.sku_list_widget = QListWidget();
        self.sku_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.list_label);
        layout.addWidget(self.sku_list_widget);
        input_layout = QHBoxLayout()
        self.sku_input = QLineEdit()
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self.add_item)
        input_layout.addWidget(self.sku_input);
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout);
        self.remove_button = QPushButton();
        self.remove_button.clicked.connect(self.remove_sku)
        layout.addWidget(self.remove_button);
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept);
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.retranslate_ui();
        self.check_limit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.sku_input.hasFocus():
                self.add_item()
                return
        super().keyPressEvent(event)

    def retranslate_ui(self):
        self.sku_input.setPlaceholderText(self.tr.get("sku_placeholder"));
        self.add_button.setText(self.tr.get("batch_add_sku_button"))
        self.remove_button.setText(self.tr.get("batch_remove_button"));
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self.tr.get("batch_generate_button"))

    def check_limit(self):
        is_full = self.sku_list_widget.count() >= self.max_items
        self.sku_input.setEnabled(not is_full);
        self.add_button.setEnabled(not is_full)
        self.sku_input.setPlaceholderText(self.tr.get("sku_placeholder") if not is_full else "")

    def add_item(self):
        if self.sku_list_widget.count() >= self.max_items: QMessageBox.information(self,
                                                                                   self.tr.get("batch_limit_title"),
                                                                                   self.tr.get("batch_limit_message",
                                                                                               self.max_items)); return
        identifier = self.sku_input.text().strip().upper()
        if not identifier: return

        item_data = data_handler.find_item_by_sku_or_barcode(identifier)
        if not item_data:
            QMessageBox.warning(self, self.tr.get("sku_not_found_title"),
                                self.tr.get("sku_not_found_message", identifier))
            return

        sku_to_add = item_data.get('SKU')
        if sku_to_add in [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]:
            QMessageBox.warning(self, self.tr.get("batch_duplicate_title"),
                                self.tr.get("batch_duplicate_message", sku_to_add))
            return

        self.sku_list_widget.addItem(sku_to_add);
        self.sku_input.clear();
        self.check_limit()

    def remove_sku(self):
        for item in self.sku_list_widget.selectedItems(): self.sku_list_widget.takeItem(self.sku_list_widget.row(item))
        self.check_limit()

    def get_skus(self):
        return [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]


class DisplayManagerDialog(QDialog):
    def __init__(self, translator, branch_stock_column, parent=None):
        super().__init__(parent)
        self.tr = translator
        self.parent = parent
        self.branch_stock_column = branch_stock_column
        self.setWindowTitle(self.tr.get("display_manager_title"))
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        return_group = QGroupBox(self.tr.get("return_tag_group"))
        return_layout = QHBoxLayout()
        self.return_input = QLineEdit()
        self.return_input.setPlaceholderText(self.tr.get("return_tag_placeholder"))
        self.find_replacements_button = QPushButton(self.tr.get("find_replacements_button"))
        self.find_replacements_button.clicked.connect(self.find_replacements)
        return_layout.addWidget(QLabel(self.tr.get("return_tag_label")))
        return_layout.addWidget(self.return_input)
        return_layout.addWidget(self.find_replacements_button)
        return_group.setLayout(return_layout)

        suggestions_group = QGroupBox(self.tr.get("suggestions_group", self.parent.branch_combo.currentText()))
        suggestions_layout = QVBoxLayout()
        self.suggestions_table = QTableWidget()
        self.suggestions_table.setColumnCount(5)
        self.suggestions_table.setHorizontalHeaderLabels([
            self.tr.get("suggestions_header_sku"),
            self.tr.get("suggestions_header_name"),
            self.tr.get("suggestions_header_stock"),
            self.tr.get("suggestions_header_price"),
            self.tr.get("suggestions_header_action")
        ])
        self.suggestions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.suggestions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        suggestions_layout.addWidget(self.suggestions_table)
        suggestions_group.setLayout(suggestions_layout)

        layout.addWidget(return_group)
        layout.addWidget(suggestions_group)

    def find_replacements(self):
        identifier = self.return_input.text().strip().upper()
        if not identifier:
            return

        item_data = data_handler.find_item_by_sku_or_barcode(identifier)
        if not item_data:
            QMessageBox.warning(self, self.tr.get("sku_not_found_title"),
                                self.tr.get("sku_not_found_message", identifier))
            return

        sku = item_data.get('SKU')
        data_handler.remove_item_from_display(sku)
        QMessageBox.information(self, self.tr.get("success_title"), self.tr.get("item_returned_message", sku))
        self.return_input.clear()

        category = item_data.get('Categories')
        suggestions = data_handler.get_replacement_suggestions(category, self.branch_stock_column)
        self.populate_suggestions(suggestions)

        if self.parent and self.parent.current_item_data.get('SKU') == sku:
            self.parent.update_status_display()

    def populate_suggestions(self, suggestions):
        self.suggestions_table.setRowCount(0)
        if not suggestions:
            return

        self.suggestions_table.setRowCount(len(suggestions))
        for row, item in enumerate(suggestions):
            sale_price = item.get('Sale price', '').strip()
            regular_price = item.get('Regular price', '').strip()
            display_price = f"₾{sale_price}" if sale_price and float(
                sale_price.replace(',', '.')) > 0 else f"₾{regular_price}"

            self.suggestions_table.setItem(row, 0, QTableWidgetItem(item.get('SKU')))
            self.suggestions_table.setItem(row, 1, QTableWidgetItem(item.get('Name')))
            self.suggestions_table.setItem(row, 2, QTableWidgetItem(item.get(self.branch_stock_column, '0')))
            self.suggestions_table.setItem(row, 3, QTableWidgetItem(display_price))

            print_button = QPushButton(self.tr.get("quick_print_button"))
            print_button.clicked.connect(lambda _, r=row: self.quick_print_tag(r))
            self.suggestions_table.setCellWidget(row, 4, print_button)

    def quick_print_tag(self, row):
        sku = self.suggestions_table.item(row, 0).text()
        if self.parent:
            self.parent.generate_single_by_sku(sku, mark_on_display=True)
            self.suggestions_table.removeRow(row)


class PriceTagDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = data_handler.get_settings()
        self.translator = Translator(self.settings.get("language", "en"))
        self.tr = self.translator.get

        self.branch_map = {
            self.tr("branch_vaja"): "Stock Vaja",
            self.tr("branch_marj"): "Stock Marj",
            self.tr("branch_gldani"): "Stock Gldan"
        }

        self.setWindowIcon(QIcon("assets/logo.png"))
        self.setGeometry(100, 100, 1400, 800)
        self.paper_sizes = data_handler.get_all_paper_sizes()
        self.current_item_data = {}
        self.themes = {
            "Default": {"price_color": "#D32F2F", "text_color": "black", "strikethrough_color": "black",
                        "logo_path": "assets/logo.png", "logo_path_ka": "assets/logo-geo.png",
                        "logo_scale_factor": 0.9},
            "Winter": {"price_color": "#0077be", "text_color": "#0a1931", "strikethrough_color": "#0a1931",
                       "logo_path": "assets/logo-santa-hat.png", "logo_path_ka": "assets/logo-geo-santa-hat.png",
                       "logo_scale_factor": 1.1, "bullet_image_path": "assets/snowflake.png", "background_snow": True}
        }
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.create_left_panel(), 1)
        main_layout.addWidget(self.create_right_panel(), 2)
        self.retranslate_ui()
        self.clear_all_fields()

    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.lang_button = QPushButton()
        self.lang_button.setFixedSize(40, 40)
        self.lang_button.setIconSize(QSize(32, 32))
        self.lang_button.clicked.connect(self.switch_language)
        top_layout.addWidget(self.lang_button)
        layout.addLayout(top_layout)

        branch_group = QGroupBox(self.tr("branch_group_title"))
        branch_layout = QFormLayout()
        self.branch_combo = QComboBox()
        self.branch_combo.currentTextChanged.connect(self.handle_branch_change)
        branch_layout.addRow(self.tr("branch_label"), self.branch_combo)
        branch_group.setLayout(branch_layout)

        self.find_item_group = QGroupBox()
        find_layout = QVBoxLayout()
        sku_layout = QHBoxLayout()
        self.sku_input = QLineEdit()
        self.sku_input.returnPressed.connect(self.find_item)
        self.find_button = QPushButton()
        self.find_button.clicked.connect(self.find_item)
        sku_layout.addWidget(self.sku_input)
        sku_layout.addWidget(self.find_button)
        find_layout.addLayout(sku_layout)

        status_layout = QHBoxLayout()
        self.status_label_title = QLabel()
        self.status_label_value = QLabel()
        self.toggle_status_button = QPushButton()
        self.toggle_status_button.clicked.connect(self.toggle_display_status)
        self.toggle_status_button.setVisible(False)
        status_layout.addWidget(self.status_label_title)
        status_layout.addWidget(self.status_label_value)
        status_layout.addStretch()
        status_layout.addWidget(self.toggle_status_button)
        find_layout.addLayout(status_layout)
        self.find_item_group.setLayout(find_layout)

        self.details_group = QGroupBox()
        details_layout = QFormLayout()
        self.name_label_widget, self.price_label_widget, self.sale_price_label_widget = QLabel(), QLabel(), QLabel()
        self.name_input, self.price_input, self.sale_price_input = QLineEdit(), QLineEdit(), QLineEdit()
        self.name_input.textChanged.connect(self.update_preview)
        self.price_input.textChanged.connect(self.update_preview)
        self.sale_price_input.textChanged.connect(self.update_preview)
        details_layout.addRow(self.name_label_widget, self.name_input)
        details_layout.addRow(self.price_label_widget, self.price_input)
        details_layout.addRow(self.sale_price_label_widget, self.sale_price_input)
        self.details_group.setLayout(details_layout)

        self.style_group = QGroupBox()
        settings_layout = QFormLayout()
        self.paper_size_label, self.theme_label = QLabel(), QLabel();
        self.paper_size_combo = QComboBox();
        self.paper_size_combo.currentTextChanged.connect(self.handle_paper_size_change)
        self.theme_combo = QComboBox();
        self.theme_combo.currentTextChanged.connect(self.update_preview);
        self.dual_lang_label = QLabel()
        self.dual_lang_checkbox = QCheckBox();
        self.dual_lang_checkbox.setChecked(self.settings.get("generate_dual_language", False));
        self.dual_lang_checkbox.stateChanged.connect(self.toggle_dual_language)
        settings_layout.addRow(self.paper_size_label, self.paper_size_combo);
        settings_layout.addRow(self.theme_label, self.theme_combo);
        settings_layout.addRow(self.dual_lang_label, self.dual_lang_checkbox)
        self.style_group.setLayout(settings_layout);

        self.specs_group = QGroupBox();
        specs_layout = QVBoxLayout();
        self.specs_list = QListWidget()
        self.specs_list.itemChanged.connect(self.update_preview);
        specs_buttons_layout = QHBoxLayout();
        self.add_button, self.edit_button, self.remove_button = QPushButton(), QPushButton(), QPushButton()
        self.add_button.clicked.connect(self.add_spec);
        self.edit_button.clicked.connect(self.edit_spec);
        self.remove_button.clicked.connect(self.remove_spec)
        specs_buttons_layout.addWidget(self.add_button);
        specs_buttons_layout.addWidget(self.edit_button);
        specs_buttons_layout.addWidget(self.remove_button)
        specs_layout.addWidget(self.specs_list);
        specs_layout.addLayout(specs_buttons_layout);
        self.specs_group.setLayout(specs_layout)

        self.output_group = QGroupBox()
        actions_layout = QVBoxLayout()
        self.display_manager_button = QPushButton()
        self.display_manager_button.setFixedHeight(40)
        self.display_manager_button.clicked.connect(self.open_display_manager)
        self.single_button = QPushButton()
        self.single_button.setFixedHeight(40)
        self.single_button.clicked.connect(self.generate_single)
        self.batch_button = QPushButton()
        self.batch_button.setFixedHeight(40)
        self.batch_button.clicked.connect(self.generate_batch)
        actions_layout.addWidget(self.display_manager_button)
        actions_layout.addWidget(self.single_button)
        actions_layout.addWidget(self.batch_button)
        self.output_group.setLayout(actions_layout)

        layout.addWidget(branch_group)
        layout.addWidget(self.find_item_group)
        layout.addWidget(self.details_group)
        layout.addWidget(self.style_group)
        layout.addWidget(self.specs_group)
        layout.addWidget(self.output_group)

        return panel

    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(600, 700)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        layout.addWidget(self.preview_label)
        return panel

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("window_title"))
        self.branch_map = {
            self.tr("branch_vaja"): "Stock Vaja",
            self.tr("branch_marj"): "Stock Marj",
            self.tr("branch_gldani"): "Stock Gldan"
        }
        self.update_branch_combo()
        self.update_paper_size_combo()
        self.update_theme_combo()

        self.find_item_group.setTitle(self.tr("find_item_group"))
        self.sku_input.setPlaceholderText(self.tr("sku_placeholder"))
        self.find_button.setText(self.tr("find_button"))
        self.details_group.setTitle(self.tr("item_details_group"))
        self.name_label_widget.setText(self.tr("name_label"))
        self.price_label_widget.setText(self.tr("price_label"))
        self.sale_price_label_widget.setText(self.tr("sale_price_label"))
        self.style_group.setTitle(self.tr("style_group"))
        self.paper_size_label.setText(self.tr("paper_size_label"))
        self.theme_label.setText(self.tr("theme_label"))
        self.dual_lang_label.setText(self.tr("dual_language_label"))
        self.specs_group.setTitle(self.tr("specs_group"))
        self.add_button.setText(self.tr("add_button"))
        self.edit_button.setText(self.tr("edit_button"))
        self.remove_button.setText(self.tr("remove_button"))
        self.output_group.setTitle(self.tr("output_group"))
        self.display_manager_button.setText(self.tr("display_manager_button"))
        self.single_button.setText(self.tr("generate_single_button"))
        self.batch_button.setText(self.tr("generate_batch_button"))
        self.status_label_title.setText(f"{self.tr('status_label')}:")
        self.lang_button.setIcon(QIcon("assets/en.png" if self.translator.language == "en" else "assets/ka.png"))
        self.update_status_display()
        if not self.current_item_data:
            self.preview_label.setText(self.tr("preview_default_text"))

    def switch_language(self):
        branch_key = self.settings.get("default_branch", "branch_vaja")

        new_lang = "ka" if self.translator.language == "en" else "en"
        self.translator.set_language(new_lang)
        self.settings["language"] = new_lang
        data_handler.save_settings(self.settings)

        self.retranslate_ui()
        self.branch_combo.setCurrentText(self.tr(branch_key))
        self.update_preview()

    def update_branch_combo(self):
        current_selection = self.branch_combo.currentText()
        self.branch_combo.clear()
        self.branch_combo.addItems(self.branch_map.keys())
        if current_selection and current_selection in self.branch_map.keys():
            self.branch_combo.setCurrentText(current_selection)
        else:
            default_branch_key = self.settings.get("default_branch", "branch_vaja")
            self.branch_combo.setCurrentText(self.tr(default_branch_key))

    def handle_branch_change(self, branch_name):
        if not branch_name: return
        key = self.translator.get_key_from_value(branch_name)
        if key:
            self.settings["default_branch"] = key
            data_handler.save_settings(self.settings)

    def get_current_branch_column(self):
        current_branch_name = self.branch_combo.currentText()
        return self.branch_map.get(current_branch_name, "Stock Vaja")

    def open_display_manager(self):
        branch_column = self.get_current_branch_column()
        dialog = DisplayManagerDialog(self.translator, branch_column, self)
        dialog.exec()

    def update_paper_size_combo(self):
        self.paper_sizes = data_handler.get_all_paper_sizes()
        sorted_sizes = sorted(self.paper_sizes.keys(),
                              key=lambda s: self.paper_sizes[s]['dims'][0] * self.paper_sizes[s]['dims'][1])
        self.paper_size_combo.clear()
        self.paper_size_combo.addItems(sorted_sizes)
        self.paper_size_combo.setCurrentText(self.settings.get("default_size", "14.4x8cm"))

    def update_theme_combo(self):
        self.theme_combo.clear()
        self.theme_combo.addItems(self.themes.keys())
        self.theme_combo.setCurrentText(self.settings.get("default_theme", "Default"))

    def clear_all_fields(self):
        self.current_item_data = {}
        self.name_input.clear()
        self.sku_input.clear()
        self.price_input.clear()
        self.sale_price_input.clear()
        self.specs_list.clear()
        self.preview_label.setText(self.tr("preview_default_text"))
        self.update_status_display()
        self.toggle_status_button.setVisible(False)

    def find_item(self):
        identifier = self.sku_input.text().strip().upper()
        if not identifier:
            return
        item_data = data_handler.find_item_by_sku_or_barcode(identifier)
        if not item_data:
            self.clear_all_fields()
            QMessageBox.warning(self, self.tr.get("sku_not_found_title"),
                                self.tr.get("sku_not_found_message", identifier))
            return
        self.populate_ui_with_item_data(item_data)

    def populate_ui_with_item_data(self, item_data):
        self.current_item_data = item_data.copy()
        self.sku_input.setText(item_data.get('SKU'))
        self.name_input.setText(item_data.get("Name", ""))
        self.price_input.setText(item_data.get("Regular price", "").strip())
        self.sale_price_input.setText(item_data.get("Sale price", "").strip())
        specs = data_handler.extract_specifications(item_data.get('Description'))
        warranty = item_data.get('Attribute 3 value(s)')
        if warranty and warranty != '-':
            specs.append(f"Warranty: {warranty}")
        self.specs_list.clear()
        self.specs_list.addItems(specs)
        self.update_status_display()
        self.update_preview()

    def update_status_display(self):
        if not self.current_item_data:
            self.status_label_value.setText("-")
            self.status_label_value.setStyleSheet("")
            self.toggle_status_button.setVisible(False)
            return

        sku = self.current_item_data.get('SKU')
        if data_handler.is_item_on_display(sku):
            self.status_label_value.setText(self.tr('status_on_display'))
            self.status_label_value.setStyleSheet("color: green; font-weight: bold;")
            self.toggle_status_button.setText(self.tr('set_to_storage_button'))
        else:
            self.status_label_value.setText(self.tr('status_in_storage'))
            self.status_label_value.setStyleSheet("color: red; font-weight: bold;")
            self.toggle_status_button.setText(self.tr('set_to_display_button'))
        self.toggle_status_button.setVisible(True)

    def toggle_display_status(self):
        if not self.current_item_data: return
        sku = self.current_item_data.get('SKU')
        if data_handler.is_item_on_display(sku):
            data_handler.remove_item_from_display(sku)
        else:
            data_handler.add_item_to_display(sku)
        self.update_status_display()

    def generate_single(self):
        if not self.current_item_data:
            QMessageBox.warning(self, self.tr("no_item_title"), self.tr("no_item_message"))
            return
        sku = self.current_item_data.get('SKU')
        self.generate_single_by_sku(sku, mark_on_display=True)

    def generate_single_by_sku(self, sku, mark_on_display=False):
        item_data = data_handler.find_item_by_sku_or_barcode(sku)
        if not item_data:
            QMessageBox.warning(self, self.tr.get("sku_not_found_title"), self.tr.get("sku_not_found_message", sku))
            return
        original_data = self.current_item_data.copy() if self.current_item_data else None
        self.populate_ui_with_item_data(item_data)
        data_to_print = self.get_current_data_from_ui()
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        is_dual = self.dual_lang_checkbox.isChecked() and size_name != '6x3.5cm'
        filename = ""
        if is_dual:
            tag_en = price_generator.create_price_tag(data_to_print, size_config, theme_config, language='en')
            tag_ka = price_generator.create_price_tag(data_to_print, size_config, theme_config, language='ka')
            a4_pages = a4_layout_generator.create_a4_for_dual_single(tag_en, tag_ka)
            for i, page in enumerate(a4_pages):
                filename = os.path.join("output", f"A4_DUAL_{data_to_print['SKU']}_{i + 1}.png")
                page.save(filename, dpi=(300, 300))
                self.handle_printing(QPixmap(filename))
        else:
            lang = 'en' if size_name == '6x3.5cm' else self.translator.language
            tag_image = price_generator.create_price_tag(data_to_print, size_config, theme_config, language=lang)
            a4_page = a4_layout_generator.create_a4_for_single(tag_image)
            filename = os.path.join("output", f"A4_SINGLE_{data_to_print['SKU']}.png")
            a4_page.save(filename, dpi=(300, 300))
            self.handle_printing(QPixmap(filename))
        QMessageBox.information(self, self.tr("success_title"),
                                self.tr("file_saved_message", os.path.abspath(filename)))
        if mark_on_display:
            data_handler.add_item_to_display(sku)
        if original_data and original_data.get('SKU') != sku:
            self.populate_ui_with_item_data(original_data)
        else:
            self.update_status_display()

    def generate_batch(self):
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        if not size_name or not theme_name: return
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        layout_info = a4_layout_generator.calculate_layout(*size_config['dims'])
        dual_lang_enabled = self.dual_lang_checkbox.isChecked() and size_name != '6x3.5cm'
        dialog = BatchDialog(layout_info['total'], self.translator, dual_lang_enabled, self)
        if not dialog.exec(): return
        skus = dialog.get_skus()
        if not skus:
            QMessageBox.warning(self, self.tr("batch_empty_title"), self.tr("batch_empty_message"))
            return

        tag_images, valid_skus = [], []
        for sku in skus:
            item_data = data_handler.find_item_by_sku_or_barcode(sku)
            if not item_data:
                QMessageBox.warning(self, self.tr("sku_not_found_title"), self.tr("sku_not_found_message", sku))
                continue

            # **FIXED**: Add spec processing logic for batch items.
            specs = data_handler.extract_specifications(item_data.get('Description'))
            warranty = item_data.get('Attribute 3 value(s)')
            if warranty and warranty != '-':
                specs.append(f"Warranty: {warranty}")
            item_data['specs'] = specs

            valid_skus.append(item_data.get('SKU'))
            if dual_lang_enabled:
                tag_images.append(price_generator.create_price_tag(item_data, size_config, theme_config, language='en'))
                tag_images.append(price_generator.create_price_tag(item_data, size_config, theme_config, language='ka'))
            else:
                lang = 'en' if size_name == '6x3.5cm' else self.translator.language
                tag_images.append(price_generator.create_price_tag(item_data, size_config, theme_config, language=lang))

        if not tag_images: return
        a4_sheet = a4_layout_generator.create_a4_sheet(tag_images, layout_info)
        filename = os.path.join("output", f"A4_BATCH_{size_name}.png")
        a4_sheet.save(filename, dpi=(300, 300))
        self.handle_printing(QPixmap(filename))
        QMessageBox.information(self, self.tr("success_title"),
                                self.tr("file_saved_message", os.path.abspath(filename)))
        for sku in valid_skus: data_handler.add_item_to_display(sku)
        if self.current_item_data.get('SKU') in valid_skus: self.update_status_display()

    def get_current_data_from_ui(self):
        if not self.current_item_data: return None
        data = self.current_item_data.copy()
        data['Name'] = self.name_input.text()
        data['Regular price'] = self.price_input.text()
        data['Sale price'] = self.sale_price_input.text()
        data['specs'] = [self.specs_list.item(i).text() for i in range(self.specs_list.count())]
        return data

    def update_preview(self):
        data_to_preview = self.get_current_data_from_ui()
        if not data_to_preview: return
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        if not size_name or not theme_name: return
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        current_lang = 'en' if size_name == '6x3.5cm' else self.translator.language
        pil_image = price_generator.create_price_tag(data_to_preview, size_config, theme_config, language=current_lang)
        q_image = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, pil_image.width * 3,
                         QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaledToWidth(self.preview_label.width(), Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)

    def handle_paper_size_change(self, size_name):
        is_special_size = size_name == '6x3.5cm'
        self.dual_lang_checkbox.setEnabled(not is_special_size)
        if is_special_size:
            self.dual_lang_checkbox.setChecked(False)
        else:
            self.dual_lang_checkbox.setChecked(self.settings.get("generate_dual_language", False))
        self.specs_group.setVisible(not is_special_size)
        self.update_preview()

    def add_spec(self):
        self.specs_list.addItem("New Specification: Edit Me");
        self.specs_list.setCurrentRow(self.specs_list.count() - 1);
        self.edit_spec()

    def edit_spec(self):
        item = self.specs_list.currentItem()
        if item: item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable); self.specs_list.editItem(item)

    def remove_spec(self):
        item = self.specs_list.currentItem()
        if item:
            reply = QMessageBox.question(self, self.tr("remove_spec_title"),
                                         self.tr("remove_spec_message", item.text()))
            if reply == QMessageBox.StandardButton.Yes: self.specs_list.takeItem(
                self.specs_list.row(item)); self.update_preview()

    def toggle_dual_language(self, state):
        if self.dual_lang_checkbox.isEnabled():
            self.settings["generate_dual_language"] = bool(state)
            data_handler.save_settings(self.settings)

    def handle_printing(self, pixmap):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter()
            painter.begin(printer)
            rect = painter.viewport()
            size = pixmap.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect())
            painter.drawPixmap(0, 0, pixmap)
            painter.end()


if __name__ == "__main__":
    for folder in ['output', 'assets', 'fonts']:
        if not os.path.exists(folder): os.makedirs(folder)
    app = QApplication(sys.argv)
    dashboard = PriceTagDashboard()
    dashboard.show()
    sys.exit(app.exec())
