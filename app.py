import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QFormLayout, QGroupBox, QComboBox, QMessageBox, QDialog,
                             QDialogButtonBox, QAbstractItemView, QTextEdit, QCheckBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QFileDialog,
                             QMenuBar)
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter, QAction
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

import firebase_handler
import data_handler
import price_generator
import a4_layout_generator
from translations import Translator


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
        self.templates = data_handler.get_item_templates()
        for key in self.templates.keys():
            self.template_list.addItem(self.translator.get(key))
        self.template_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.template_list)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        selected_item = self.template_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, self.translator.get("template_validation_error_title"),
                                self.translator.get("template_validation_error_message"))
            return

        self.selected_template_key = self.translator.get_key_from_value(selected_item.text())
        self.selected_template_data = self.templates.get(self.selected_template_key)

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
            QMessageBox.warning(self, self.translator.get("new_item_validation_error"),
                                self.translator.get("new_item_name_empty_error"))
            return

        self.new_item_data["Name"] = name
        self.new_item_data["Regular price"] = self.price_input.text().strip()
        self.new_item_data["Sale price"] = self.sale_price_input.text().strip()

        specs_html = "".join(
            [f"<li>{line}</li>" for line in self.specs_input.toPlainText().strip().split('\n') if line and ':' in line])
        self.new_item_data["Description"] = f"<ul>{specs_html}</ul>"

        self.accept()


class BatchDialog(QDialog):
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.get("batch_dialog_title"));
        self.setMinimumSize(400, 500)
        layout = QVBoxLayout(self)

        self.list_label = QLabel(self.translator.get("batch_list_label_unlimited", 0))

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.sku_input.hasFocus():
                self.add_item()
                return
        super().keyPressEvent(event)

    def retranslate_ui(self):
        self.sku_input.setPlaceholderText(self.translator.get("sku_placeholder"));
        self.add_button.setText(self.translator.get("batch_add_sku_button"))
        self.remove_button.setText(self.translator.get("batch_remove_button"));
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self.translator.get("batch_generate_button"))
        self.update_item_count()

    def update_item_count(self):
        count = self.sku_list_widget.count()
        self.list_label.setText(self.translator.get("batch_list_label_unlimited", count))

    def add_item(self):
        identifier = self.sku_input.text().strip().upper()
        if not identifier: return

        item_data = firebase_handler.find_item_by_identifier(identifier, None)
        if not item_data:
            QMessageBox.warning(self, self.translator.get("sku_not_found_title"),
                                self.translator.get("sku_not_found_message", identifier))
            return

        sku_to_add = item_data.get('SKU')
        if sku_to_add in [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]:
            QMessageBox.warning(self, self.translator.get("batch_duplicate_title"),
                                self.translator.get("batch_duplicate_message", sku_to_add))
            return

        self.sku_list_widget.addItem(sku_to_add);
        self.sku_input.clear();
        self.update_item_count()

    def remove_sku(self):
        for item in self.sku_list_widget.selectedItems(): self.sku_list_widget.takeItem(self.sku_list_widget.row(item))
        self.update_item_count()

    def get_skus(self):
        return [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]


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
        self.setMinimumSize(800, 600)

        self.original_suggestions = []
        self.current_sort_column = -1
        self.current_sort_order = None

        layout = QVBoxLayout(self)

        return_group = QGroupBox(self.translator.get("return_tag_group"))
        return_layout = QHBoxLayout()
        self.return_input = QLineEdit()
        self.return_input.setPlaceholderText(self.translator.get("return_tag_placeholder"))
        self.find_replacements_button = QPushButton(self.translator.get("find_replacements_button"))
        self.find_replacements_button.clicked.connect(self.find_replacements)
        return_layout.addWidget(QLabel(self.translator.get("return_tag_label")))
        return_layout.addWidget(self.return_input)
        return_layout.addWidget(self.find_replacements_button)
        return_group.setLayout(return_layout)

        suggestions_group = QGroupBox(self.translator.get("suggestions_group", self.parent.branch_combo.currentText()))
        suggestions_layout = QVBoxLayout()
        self.suggestions_table = QTableWidget()
        self.suggestions_table.setColumnCount(5)
        self.suggestions_table.setHorizontalHeaderLabels([
            self.translator.get("suggestions_header_sku"),
            self.translator.get("suggestions_header_name"),
            self.translator.get("suggestions_header_stock"),
            self.translator.get("suggestions_header_price"),
            self.translator.get("suggestions_header_action")
        ])
        self.suggestions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.suggestions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.suggestions_table.horizontalHeader().sectionClicked.connect(self.handle_header_click)
        suggestions_layout.addWidget(self.suggestions_table)
        suggestions_group.setLayout(suggestions_layout)

        layout.addWidget(return_group)
        layout.addWidget(suggestions_group)

    def find_replacements(self):
        identifier = self.return_input.text().strip().upper()
        if not identifier: return

        item_data = firebase_handler.find_item_by_identifier(identifier, self.token)
        if not item_data:
            QMessageBox.warning(self, self.translator.get("sku_not_found_title"),
                                self.translator.get("sku_not_found_message", identifier))
            return

        sku = item_data.get('SKU')
        firebase_handler.remove_item_from_display(sku, self.branch_db_key, self.token)
        QMessageBox.information(self, self.translator.get("success_title"),
                                self.translator.get("item_returned_message", sku))
        self.return_input.clear()

        category = item_data.get('Categories')
        self.original_suggestions = firebase_handler.get_replacement_suggestions(category, self.branch_stock_col,
                                                                                 self.token)

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
                sale_price = item.get('Sale price', '').strip()
                if sale_price and float(sale_price.replace(',', '.')) > 0:
                    return float(sale_price.replace(',', '.'))
                regular_price = item.get('Regular price', '').strip()
                if regular_price:
                    return float(regular_price.replace(',', '.'))
                return 0
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
        for i in range(header.count()):
            original_text = self.translator.get(f"suggestions_header_{['sku', 'name', 'stock', 'price', 'action'][i]}")
            if i == self.current_sort_column:
                if self.current_sort_order == Qt.SortOrder.AscendingOrder:
                    self.suggestions_table.horizontalHeaderItem(i).setText(f"{original_text} ▲")
                else:
                    self.suggestions_table.horizontalHeaderItem(i).setText(f"{original_text} ▼")
            else:
                self.suggestions_table.horizontalHeaderItem(i).setText(original_text)

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
            print_button.clicked.connect(lambda _, r=row, s=item.get('SKU'): self.quick_print_tag(r, s))
            self.suggestions_table.setCellWidget(row, 4, print_button)

    def _get_price_for_sort(self, item):
        try:
            sale_price = item.get('Sale price', '').strip()
            if sale_price and float(sale_price.replace(',', '.')) > 0:
                return float(sale_price.replace(',', '.'))
            regular_price = item.get('Regular price', '').strip()
            if regular_price: return float(regular_price.replace(',', '.'))
        except (ValueError, TypeError):
            pass
        return 0

    def quick_print_tag(self, row, sku):
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
            self.table.setItem(row_num, 0, QTableWidgetItem(user_data.get("email")))
            self.table.setItem(row_num, 1, QTableWidgetItem(user_data.get("role")))

            if user_data.get("role") != "Admin":
                promote_button = QPushButton(self.translator.get("user_mgmt_promote_button"))
                promote_button.clicked.connect(lambda _, u=user_data: self.promote_user(u))
                self.table.setCellWidget(row_num, 2, promote_button)

    def promote_user(self, user_data):
        uid = user_data.get("uid")
        email = user_data.get("email")
        reply = QMessageBox.question(self, self.translator.get("user_mgmt_confirm_promote_title"),
                                     self.translator.get("user_mgmt_confirm_promote_message", email))
        if reply == QMessageBox.StandardButton.Yes:
            firebase_handler.promote_user_to_admin(uid, self.token)
            self.load_users()


class PriceTagDashboard(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.token = self.user.get('idToken')
        self.settings = data_handler.get_settings()
        self.translator = Translator(self.settings.get("language", "en"))
        self.tr = self.translator.get
        self.printer = QPrinter(QPrinter.PrinterMode.HighResolution)

        self.branch_data_map = {
            "branch_vaja": {"db_key": "Vazha-Pshavela Shop", "stock_col": "Stock Vaja"},
            "branch_marj": {"db_key": "Marjanishvili", "stock_col": "Stock Marj"},
            "branch_gldani": {"db_key": "Gldani Shop", "stock_col": "Stock Gldan"},
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
        self.create_menu()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.create_left_panel(), 1)
        main_layout.addWidget(self.create_right_panel(), 2)
        self.retranslate_ui()
        self.clear_all_fields()

    def create_menu(self):
        menu_bar = self.menuBar()
        menu_bar.clear()

        file_menu = menu_bar.addMenu(self.tr("file_menu"))
        select_printer_action = QAction(self.tr("select_printer_menu"), self)
        select_printer_action.triggered.connect(self.select_printer)
        file_menu.addAction(select_printer_action)

        if self.user.get('role') == 'Admin':
            admin_menu = menu_bar.addMenu(self.tr('admin_tools_menu'))

            upload_action = QAction(self.tr('admin_upload_master_list'), self)
            upload_action.triggered.connect(self.upload_master_list)
            admin_menu.addAction(upload_action)

            user_mgmt_action = QAction(self.tr('admin_manage_users'), self)
            user_mgmt_action.triggered.connect(self.open_user_management)
            admin_menu.addAction(user_mgmt_action)

    def open_user_management(self):
        dialog = UserManagementDialog(self.translator, self.user, self)
        dialog.exec()

    def upload_master_list(self):
        filepath, _ = QFileDialog.getOpenFileName(self, self.tr("open_master_list_title"), "",
                                                  "Text Files (*.txt);;All Files (*)")
        if filepath:
            success, val1, val2 = firebase_handler.sync_products_from_file(filepath, self.token)
            if success:
                message = self.tr("sync_results_message", val1, val2)
                QMessageBox.information(self, self.tr("success_title"), message)
            else:
                QMessageBox.critical(self, "Error", val1)

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
        self.branch_combo.currentIndexChanged.connect(self.handle_branch_change)
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
        self.update_branch_combo()
        self.update_paper_size_combo()
        self.update_theme_combo()
        self.create_menu()

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
        index = self.branch_combo.findData(branch_key)
        if index != -1:
            self.branch_combo.setCurrentIndex(index)
        self.update_preview()

    def update_branch_combo(self):
        self.branch_combo.blockSignals(True)
        current_key = self.branch_combo.currentData() or self.settings.get("default_branch", "branch_vaja")
        self.branch_combo.clear()
        for key in self.branch_data_map.keys():
            self.branch_combo.addItem(self.tr(key), key)

        index = self.branch_combo.findData(current_key)
        if index != -1:
            self.branch_combo.setCurrentIndex(index)

        self.branch_combo.blockSignals(False)

    def handle_branch_change(self, index):
        key = self.branch_combo.currentData()
        if key:
            self.settings["default_branch"] = key
            data_handler.save_settings(self.settings)
        self.update_status_display()

    def get_current_branch_stock_column(self):
        current_key = self.branch_combo.currentData()
        return self.branch_data_map.get(current_key, {}).get("stock_col")

    def get_current_branch_db_key(self):
        current_key = self.branch_combo.currentData()
        return self.branch_data_map.get(current_key, {}).get("db_key")

    def open_display_manager(self):
        branch_db_key = self.get_current_branch_db_key()
        branch_stock_col = self.get_current_branch_stock_column()
        dialog = DisplayManagerDialog(self.translator, branch_db_key, branch_stock_col, self.user, self)
        dialog.exec()

    def update_paper_size_combo(self):
        self.paper_size_combo.clear()
        self.paper_sizes = data_handler.get_all_paper_sizes()
        sorted_sizes = sorted(self.paper_sizes.keys(),
                              key=lambda s: self.paper_sizes[s]['dims'][0] * self.paper_sizes[s]['dims'][1])
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
        if not identifier: return

        item_data = firebase_handler.find_item_by_identifier(identifier, self.token)
        if not item_data:
            self.clear_all_fields()
            reply = QMessageBox.question(self, self.tr("sku_not_found_title"),
                                         self.tr("sku_not_found_message", identifier) + "\n\n" + self.tr(
                                             "register_new_item_prompt"),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.register_new_item(identifier)
            return

        self.populate_ui_with_item_data(item_data)

    def register_new_item(self, sku):
        template_dialog = TemplateSelectionDialog(self.translator, self)
        if not template_dialog.exec():
            return

        template_data = template_dialog.selected_template_data
        template_specs = template_data.get("specs", [])
        category_name = template_data.get("category_name", "")

        dialog = NewItemDialog(sku, self.translator, template=template_specs, category_name=category_name, parent=self)
        if dialog.exec():
            new_data = dialog.new_item_data
            if firebase_handler.add_new_item(new_data, self.token):
                QMessageBox.information(self, self.tr("success_title"), self.tr("new_item_save_success", sku))
                self.sku_input.setText(sku)
                self.find_item()
            else:
                QMessageBox.critical(self, self.tr("new_item_validation_error"), self.tr("new_item_save_error"))

    def populate_ui_with_item_data(self, item_data):
        self.current_item_data = item_data.copy()

        specs = firebase_handler.extract_specifications(item_data.get('Description'))
        warranty = item_data.get('Attribute 3 value(s)')
        if warranty and warranty != '-':
            specs.append(f"Warranty: {warranty}")
        self.current_item_data['all_specs'] = self.process_specifications(specs)
        self.current_item_data['part_number'] = firebase_handler.extract_part_number(item_data.get('Description', ''))

        self.sku_input.setText(self.current_item_data.get('SKU'))
        self.name_input.setText(self.current_item_data.get("Name", ""))
        self.price_input.setText(self.current_item_data.get("Regular price", "").strip())
        self.sale_price_input.setText(self.current_item_data.get("Sale price", "").strip())

        self.update_specs_list()
        self.update_status_display()
        self.update_preview()

    def update_status_display(self):
        if not self.current_item_data:
            self.status_label_value.setText("-")
            self.status_label_value.setStyleSheet("")
            self.toggle_status_button.setVisible(False)
            return

        sku = self.current_item_data.get('SKU')
        branch_db_key = self.get_current_branch_db_key()
        if firebase_handler.is_item_on_display(sku, branch_db_key, self.token):
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
        branch_db_key = self.get_current_branch_db_key()
        if firebase_handler.is_item_on_display(sku, branch_db_key, self.token):
            firebase_handler.remove_item_from_display(sku, branch_db_key, self.token)
        else:
            firebase_handler.add_item_to_display(sku, branch_db_key, self.token)
        self.update_status_display()

    def generate_single(self):
        if not self.current_item_data:
            QMessageBox.warning(self, self.tr("no_item_title"), self.tr("no_item_message"))
            return
        sku = self.current_item_data.get('SKU')
        self.generate_single_by_sku(sku, mark_on_display=True)

    def generate_single_by_sku(self, sku, mark_on_display=False):
        item_data = firebase_handler.find_item_by_identifier(sku, self.token)
        if not item_data:
            QMessageBox.warning(self, self.tr("sku_not_found_title"), self.tr("sku_not_found_message", sku))
            return

        data_to_print = self._prepare_data_for_printing(item_data)

        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        is_dual = self.dual_lang_checkbox.isChecked() and size_name != '6x3.5cm'

        pixmaps_to_print = []
        filenames = []

        if is_dual:
            tag_en = price_generator.create_price_tag(data_to_print, size_config, theme_config, language='en')
            tag_ka = price_generator.create_price_tag(data_to_print, size_config, theme_config, language='ka')
            a4_pages = a4_layout_generator.create_a4_for_dual_single(tag_en, tag_ka)
            for i, page in enumerate(a4_pages):
                filename = os.path.join("output", f"A4_DUAL_{data_to_print['SKU']}_{i + 1}.png")
                page.save(filename, dpi=(300, 300))
                pixmaps_to_print.append(QPixmap(filename))
                filenames.append(filename)
        else:
            lang = 'en' if size_name == '6x3.5cm' else self.translator.language
            tag_image = price_generator.create_price_tag(data_to_print, size_config, theme_config, language=lang)
            a4_page = a4_layout_generator.create_a4_for_single(tag_image)
            filename = os.path.join("output", f"A4_SINGLE_{data_to_print['SKU']}.png")
            a4_page.save(filename, dpi=(300, 300))
            pixmaps_to_print.append(QPixmap(filename))
            filenames.append(filename)

        self.handle_single_print_with_dialog(pixmaps_to_print)

        QMessageBox.information(self, self.tr("success_title"),
                                self.tr("file_saved_message", "\n".join(map(os.path.abspath, filenames))))

        if mark_on_display:
            branch_db_key = self.get_current_branch_db_key()
            firebase_handler.add_item_to_display(sku, branch_db_key, self.token)

        if self.current_item_data.get('SKU') == sku:
            self.update_status_display()

    def generate_batch(self):
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        if not size_name or not theme_name: return

        size_config = self.paper_sizes[size_name]
        theme_config = self.themes[theme_name]
        layout_info = a4_layout_generator.calculate_layout(*size_config['dims'])
        tags_per_sheet = layout_info.get('total', 0)

        if tags_per_sheet <= 0:
            QMessageBox.warning(self, "Layout Error",
                                "The selected paper size cannot fit any tags. Please choose a larger paper size or smaller tag size.")
            return

        dual_lang_enabled = self.dual_lang_checkbox.isChecked() and size_name != '6x3.5cm'
        items_per_sheet = tags_per_sheet
        if dual_lang_enabled:
            items_per_sheet //= 2

        dialog = BatchDialog(self.translator, self)
        if not dialog.exec(): return

        skus = dialog.get_skus()
        if not skus:
            QMessageBox.warning(self, self.tr("batch_empty_title"), self.tr("batch_empty_message"))
            return

        all_valid_skus = [sku for sku in skus if firebase_handler.find_item_by_identifier(sku, self.token)]
        if not all_valid_skus:
            QMessageBox.warning(self, self.tr("sku_not_found_title"),
                                "None of the provided SKUs were found in the database.")
            return

        dialog = QPrintDialog(self.printer, self)
        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            QMessageBox.warning(self, "Printing Cancelled",
                                "The batch print job was cancelled because no printer was selected.")
            return

        sku_pages = list(a4_layout_generator.chunks(all_valid_skus, items_per_sheet))
        total_pages = len(sku_pages)
        branch_db_key = self.get_current_branch_db_key()

        for page_num, page_skus in enumerate(sku_pages, 1):
            tag_images_for_page = []
            for sku in page_skus:
                item_data = firebase_handler.find_item_by_identifier(sku, self.token)
                if not item_data: continue

                data_to_print = self._prepare_data_for_printing(item_data)

                if dual_lang_enabled:
                    tag_images_for_page.append(
                        price_generator.create_price_tag(data_to_print, size_config, theme_config, language='en'))
                    tag_images_for_page.append(
                        price_generator.create_price_tag(data_to_print, size_config, theme_config, language='ka'))
                else:
                    lang = 'en' if size_name == '6x3.5cm' else self.translator.language
                    tag_images_for_page.append(
                        price_generator.create_price_tag(data_to_print, size_config, theme_config, language=lang))

            if not tag_images_for_page: continue

            a4_sheet = a4_layout_generator.create_a4_sheet(tag_images_for_page, layout_info)
            filename = os.path.join("output", f"A4_BATCH_{size_name}_Page_{page_num}_of_{total_pages}.png")
            a4_sheet.save(filename, dpi=(300, 300))

            if not self._execute_print_job(QPixmap(filename), self.printer):
                QMessageBox.critical(self, "Printing Error",
                                     f"Failed to print page {page_num}. The batch job has been aborted.")
                break
        else:
            QMessageBox.information(self, "Batch Complete",
                                    self.tr("print_job_sent", total_pages, self.printer.printerName()))

        for sku in all_valid_skus:
            firebase_handler.add_item_to_display(sku, branch_db_key, self.token)
        if self.current_item_data.get('SKU') in all_valid_skus:
            self.update_status_display()

    def get_current_data_from_ui(self):
        if not self.current_item_data: return None
        data = self.current_item_data.copy()
        data['Name'] = self.name_input.text()
        data['Regular price'] = self.price_input.text()
        data['Sale price'] = self.sale_price_input.text()
        data['specs'] = [self.specs_list.item(i).text() for i in range(self.specs_list.count())]
        data['part_number'] = self.current_item_data.get('part_number', '')
        return data

    def _prepare_data_for_printing(self, item_data):
        data_to_print = item_data.copy()
        data_to_print['part_number'] = data_handler.extract_part_number(item_data.get('Description', ''))

        specs = data_handler.extract_specifications(item_data.get('Description'))
        warranty = item_data.get('Attribute 3 value(s)')
        if warranty and warranty != '-':
            specs.append(f"Warranty: {warranty}")

        processed_specs = self.process_specifications(specs)
        data_to_print['specs'] = self._prepare_specs_for_display(processed_specs)
        return data_to_print

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
        self.update_specs_list()
        self.update_preview()

    def update_specs_list(self):
        if not self.current_item_data:
            self.specs_list.clear()
            return

        all_specs = self.current_item_data.get('all_specs', [])
        display_specs = self._prepare_specs_for_display(all_specs)

        self.specs_list.clear()
        self.specs_list.addItems(display_specs)

    def _prepare_specs_for_display(self, all_specs):
        size_name = self.paper_size_combo.currentText()
        if not size_name: return all_specs

        size_config = self.paper_sizes.get(size_name, {})
        spec_limit = size_config.get('spec_limit', 99)

        if not spec_limit or len(all_specs) <= spec_limit:
            return all_specs

        warranty_spec = None
        other_specs = []

        for spec in all_specs:
            if 'warranty' in spec.lower() and not warranty_spec:
                warranty_spec = spec
            else:
                other_specs.append(spec)

        if warranty_spec:
            truncated_specs = other_specs[:spec_limit - 1]
            truncated_specs.append(warranty_spec)
            return truncated_specs
        else:
            return all_specs[:spec_limit]

    def process_specifications(self, specs):
        first_warranty_found = False
        filtered_specs = []
        for spec in specs:
            if 'warranty' in spec.lower():
                if not first_warranty_found:
                    filtered_specs.append(spec)
                    first_warranty_found = True
            else:
                filtered_specs.append(spec)
        return filtered_specs

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

    def select_printer(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Printer Selected",
                                    f"Printer '{self.printer.printerName()}' has been selected for subsequent print jobs.")

    def _execute_print_job(self, pixmap, printer):
        painter = QPainter()
        if painter.begin(printer):
            printer.setResolution(300)
            page_rect_pixels = printer.pageRect(QPrinter.Unit.DevicePixel)
            x_offset = (page_rect_pixels.width() - pixmap.width()) / 2
            y_offset = (page_rect_pixels.height() - pixmap.height()) / 2
            painter.drawPixmap(int(x_offset), int(y_offset), pixmap)
            painter.end()
            return True
        return False

    def handle_single_print_with_dialog(self, pixmaps):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            for pixmap in pixmaps:
                if not self._execute_print_job(pixmap, self.printer):
                    QMessageBox.critical(self, "Printing Error", f"Could not print on '{self.printer.printerName()}'.")
                    break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Error", "This file is not the main entry point. Please run main.py")
