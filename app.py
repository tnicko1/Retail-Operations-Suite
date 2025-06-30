import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QFormLayout, QGroupBox, QComboBox, QMessageBox, QDialog,
                             QDialogButtonBox, QAbstractItemView, QTextEdit, QCheckBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QFileDialog,
                             QMenuBar, QTabWidget, QMenu)
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
            QMessageBox.warning(self, self.translator.get("template_validation_error_title"),
                                self.translator.get("template_validation_error_message"))
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
        identifier = self.sku_input.text().strip().upper()
        if not identifier: return

        item_data = firebase_handler.find_item_by_identifier(identifier, self.token)
        if not item_data:
            QMessageBox.warning(self, self.translator.get("sku_not_found_title"),
                                self.translator.get("sku_not_found_message", identifier))
            return

        sku_to_add = item_data.get('SKU')
        if sku_to_add in [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]:
            QMessageBox.warning(self, self.translator.get("batch_duplicate_title"),
                                self.translator.get("batch_duplicate_message", sku_to_add))
            return

        self.sku_list_widget.addItem(sku_to_add)
        self.save_queue()
        self.sku_input.clear()

    def load_queue(self):
        self.sku_list_widget.clear()
        queue_data = firebase_handler.get_print_queue(self.uid, self.token)
        self.sku_list_widget.addItems(queue_data)

    def save_queue(self):
        queue_items = [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]
        firebase_handler.save_print_queue(self.uid, self.token, queue_items)

    def load_saved_lists(self):
        self.saved_lists_combo.clear()
        saved_lists = firebase_handler.get_saved_batch_lists(self.uid, self.token)
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

        all_lists = firebase_handler.get_saved_batch_lists(self.uid, self.token)
        skus_to_load = all_lists.get(list_name, [])
        self.sku_list_widget.clear()
        self.sku_list_widget.addItems(skus_to_load)
        self.save_queue()

    def save_list(self):
        current_queue = [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]
        if not current_queue:
            QMessageBox.warning(self, "Empty Queue", "Cannot save an empty queue.")
            return

        list_name, ok = QInputDialog.getText(self, self.translator.get("print_queue_save_prompt"), "List Name:")
        if ok and list_name:
            firebase_handler.save_batch_list(self.uid, self.token, list_name, current_queue)
            self.load_saved_lists()
            self.saved_lists_combo.setCurrentText(list_name)

    def delete_list(self):
        list_name = self.saved_lists_combo.currentText()
        if not list_name: return

        reply = QMessageBox.question(self, "Delete List", self.translator.get("print_queue_delete_confirm", list_name))
        if reply == QMessageBox.StandardButton.Yes:
            firebase_handler.delete_batch_list(self.uid, self.token, list_name)
            self.load_saved_lists()

    def get_skus(self):
        return [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]


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
        reply = QMessageBox.question(self, self.translator.get("template_manager_delete_cat_confirm_title"),
                                     self.translator.get("template_manager_delete_cat_confirm_msg", name))
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
            QMessageBox.information(self, self.translator.get("success_title"),
                                    self.translator.get("templates_saved_success"))
        else:
            QMessageBox.critical(self, "Error", self.translator.get("templates_saved_fail"))


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

        for row, entry in enumerate(log_data):
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
        self.original_suggestions = firebase_handler.get_replacement_suggestions(category, self.branch_db_key,
                                                                                 self.branch_stock_col, self.token)

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
            self.table.setItem(row_num, 0, QTableWidgetItem(user_data.get("email", "")))
            self.table.setItem(row_num, 1, QTableWidgetItem(user_data.get("role", "")))

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
        self.uid = self.user.get('localId')
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

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.generator_tab = QWidget()
        self.dashboard_tab = QWidget()

        self.tab_widget.addTab(self.generator_tab, "Price Tag Generator")

        self.setup_generator_ui()

        if self.user.get('role') == 'Admin':
            self.tab_widget.addTab(self.dashboard_tab, self.tr("admin_dashboard"))
            self.setup_dashboard_ui()

        self.create_menu()
        self.retranslate_ui()
        self.clear_all_fields()

    def setup_generator_ui(self):
        main_layout = QHBoxLayout(self.generator_tab)
        main_layout.addWidget(self.create_left_panel(), 1)
        main_layout.addWidget(self.create_right_panel(), 2)

    def setup_dashboard_ui(self):
        layout = QVBoxLayout(self.dashboard_tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton(self.tr("dashboard_refresh_button"))
        self.refresh_button.clicked.connect(self.update_dashboard_data)
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_button)
        layout.addLayout(refresh_layout)

        stats_group = QGroupBox(self.tr("dashboard_stats_group"))
        stats_layout = QFormLayout()
        self.stats_labels = {}
        for key, data in self.branch_data_map.items():
            display_name = self.tr(key)
            self.stats_labels[key] = QLabel("...")
            stats_layout.addRow(f"{display_name} ({self.tr('dashboard_on_display_label')})", self.stats_labels[key])
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        low_stock_group = QGroupBox()
        low_stock_layout = QVBoxLayout()
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(3)
        self.low_stock_table.setHorizontalHeaderLabels(["SKU", "Name", "Stock"])
        self.low_stock_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        low_stock_layout.addWidget(self.low_stock_table)
        low_stock_group.setLayout(low_stock_layout)
        layout.addWidget(low_stock_group)

        self.low_stock_group = low_stock_group
        self.update_dashboard_data()

    def update_dashboard_data(self):
        threshold = self.settings.get('low_stock_threshold', 3)
        self.low_stock_group.setTitle(self.tr("dashboard_low_stock_label", threshold))

        all_items = firebase_handler.db.child("items").get(self.token).val() or {}
        display_statuses = firebase_handler.get_display_status(self.token)

        for key, data in self.branch_data_map.items():
            db_key = data['db_key']
            count = len(display_statuses.get(db_key, []))
            self.stats_labels[key].setText(str(count))

        self.low_stock_table.setRowCount(0)
        low_stock_items = []
        for sku, item_data in all_items.items():
            for branch_key, branch_info in self.branch_data_map.items():
                stock_col = branch_info['stock_col']
                stock_str = str(item_data.get(stock_col, '0')).replace(',', '')
                if stock_str.isdigit() and 0 < int(stock_str) <= threshold:
                    low_stock_items.append({
                        "sku": sku,
                        "name": item_data.get("Name", "N/A"),
                        "stock": f"{branch_info['db_key']}: {int(stock_str)}"
                    })

        self.low_stock_table.setRowCount(len(low_stock_items))
        for row, item in enumerate(low_stock_items):
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(item['sku']))
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.low_stock_table.setItem(row, 2, QTableWidgetItem(item['stock']))

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

            template_manager_action = QAction(self.tr("admin_template_manager"), self)
            template_manager_action.triggered.connect(self.open_template_manager)
            admin_menu.addAction(template_manager_action)

            activity_log_action = QAction(self.tr("admin_activity_log"), self)
            activity_log_action.triggered.connect(self.open_activity_log)
            admin_menu.addAction(activity_log_action)

            user_mgmt_action = QAction(self.tr('admin_manage_users'), self)
            user_mgmt_action.triggered.connect(self.open_user_management)
            admin_menu.addAction(user_mgmt_action)

    def open_user_management(self):
        dialog = UserManagementDialog(self.translator, self.user, self)
        dialog.exec()

    def open_template_manager(self):
        dialog = TemplateManagerDialog(self.translator, self.token, self)
        dialog.exec()

    def open_activity_log(self):
        dialog = ActivityLogDialog(self.translator, self.token, self)
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
        self.add_to_queue_button = QPushButton()
        self.add_to_queue_button.setFixedSize(40, self.find_button.sizeHint().height())
        self.add_to_queue_button.clicked.connect(self.add_current_to_queue)

        sku_layout.addWidget(self.sku_input)
        sku_layout.addWidget(self.find_button)
        sku_layout.addWidget(self.add_to_queue_button)
        find_layout.addLayout(sku_layout)

        status_layout = QHBoxLayout()
        self.status_label_title = QLabel()
        self.status_label_value = QLabel()
        self.stock_label_title = QLabel(self.tr("stock_label"))
        self.stock_label_value = QLabel("-")
        self.low_stock_warning_label = QLabel()

        self.toggle_status_button = QPushButton()
        self.toggle_status_button.clicked.connect(self.toggle_display_status)
        self.toggle_status_button.setVisible(False)

        status_layout.addWidget(self.status_label_title)
        status_layout.addWidget(self.status_label_value)
        status_layout.addStretch()
        status_layout.addWidget(self.stock_label_title)
        status_layout.addWidget(self.stock_label_value)
        status_layout.addWidget(self.low_stock_warning_label)
        status_layout.addStretch()
        status_layout.addWidget(self.toggle_status_button)
        find_layout.addLayout(status_layout)
        self.find_item_group.setLayout(find_layout)

        self.details_group = QGroupBox()
        details_layout = QFormLayout()
        self.name_label_widget, self.price_label_widget, self.sale_price_label_widget = QLabel(), QLabel(), QLabel()
        self.name_input, self.price_input, self.sale_price_input = QLineEdit(), QLineEdit(), QLineEdit()
        self.price_history_button = QPushButton(self.tr("price_history_button"))
        self.price_history_button.clicked.connect(self.show_price_history)
        self.price_history_button.setVisible(False)

        self.name_input.textChanged.connect(self.update_preview)
        self.price_input.textChanged.connect(self.update_preview)
        self.sale_price_input.textChanged.connect(self.update_preview)
        details_layout.addRow(self.name_label_widget, self.name_input)
        price_layout = QHBoxLayout()
        price_layout.addWidget(self.price_input)
        price_layout.addWidget(self.price_history_button)
        details_layout.addRow(self.price_label_widget, price_layout)
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
        self.add_spec_button = QPushButton()
        self.add_spec_button.clicked.connect(self.add_spec)
        self.edit_button, self.remove_button = QPushButton(), QPushButton()
        self.edit_button.clicked.connect(self.edit_spec);
        self.remove_button.clicked.connect(self.remove_spec)
        specs_buttons_layout.addWidget(self.add_spec_button);
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
        self.batch_button.clicked.connect(self.open_print_queue)
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
        self.tab_widget.setTabText(0, self.tr("window_title"))
        if self.user.get('role') == 'Admin':
            self.tab_widget.setTabText(1, self.tr("admin_dashboard"))

        self.update_branch_combo()
        self.update_paper_size_combo()
        self.update_theme_combo()
        self.create_menu()

        self.find_item_group.setTitle(self.tr("find_item_group"))
        self.sku_input.setPlaceholderText(self.tr("sku_placeholder"))
        self.find_button.setText(self.tr("find_button"))
        self.add_to_queue_button.setText("+")
        self.add_to_queue_button.setToolTip(self.tr("add_to_queue_button"))
        self.details_group.setTitle(self.tr("item_details_group"))
        self.name_label_widget.setText(self.tr("name_label"))
        self.price_label_widget.setText(self.tr("price_label"))
        self.sale_price_label_widget.setText(self.tr("sale_price_label"))
        self.style_group.setTitle(self.tr("style_group"))
        self.paper_size_label.setText(self.tr("paper_size_label"))
        self.theme_label.setText(self.tr("theme_label"))
        self.dual_lang_label.setText(self.tr("dual_language_label"))
        self.specs_group.setTitle(self.tr("specs_group"))
        self.add_spec_button.setText(self.tr("add_button"))
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
        self.update_stock_display()
        self.update_preview()

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

    def open_print_queue(self):
        dialog = PrintQueueDialog(self.translator, self.user, self)
        if dialog.exec():
            skus_to_print = dialog.get_skus()
            if skus_to_print:
                self.generate_batch(skus_to_print)

    def add_current_to_queue(self):
        if not self.current_item_data:
            QMessageBox.warning(self, "No Item", "Please find an item to add to the queue.")
            return

        sku = self.current_item_data.get("SKU")
        queue = firebase_handler.get_print_queue(self.uid, self.token)
        if sku not in queue:
            queue.append(sku)
            firebase_handler.save_print_queue(self.uid, self.token, queue)
            QMessageBox.information(self, "Success", f"Item {sku} added to the print queue.")
        else:
            QMessageBox.information(self, "Duplicate", f"Item {sku} is already in the print queue.")

    def show_price_history(self):
        if not self.current_item_data: return
        sku = self.current_item_data.get("SKU")
        dialog = PriceHistoryDialog(sku, self.translator, self.token, self)
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
        self.update_stock_display()
        self.price_history_button.setVisible(False)
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
        self.update_stock_display()
        self.price_history_button.setVisible(True)
        self.update_preview()

    def update_stock_display(self):
        if not self.current_item_data:
            self.stock_label_value.setText("-")
            self.low_stock_warning_label.setText("")
            return

        stock_col = self.get_current_branch_stock_column()
        if not stock_col:
            self.stock_label_value.setText("N/A")
            self.low_stock_warning_label.setText("")
            return

        stock_str = str(self.current_item_data.get(stock_col, '0')).replace(',', '')
        if stock_str.isdigit():
            stock_val = int(stock_str)
            self.stock_label_value.setText(str(stock_val))
            threshold = self.settings.get('low_stock_threshold', 3)
            if 0 < stock_val <= threshold:
                self.low_stock_warning_label.setText(self.tr("low_stock_warning"))
                self.low_stock_warning_label.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.low_stock_warning_label.setText("")
        else:
            self.stock_label_value.setText(stock_str)
            self.low_stock_warning_label.setText("")

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
            firebase_handler.log_activity(self.token, f"User printed and marked {sku} as on display.")

        if self.current_item_data.get('SKU') == sku:
            self.update_status_display()

    def generate_batch(self, skus_to_print):
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        if not size_name or not theme_name: return

        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        layout_info = a4_layout_generator.calculate_layout(*size_config['dims'])
        tags_per_sheet = layout_info.get('total', 0)

        if tags_per_sheet <= 0:
            QMessageBox.warning(self, "Layout Error", "The selected paper size cannot fit any tags.")
            return

        dual_lang_enabled = self.dual_lang_checkbox.isChecked() and size_name != '6x3.5cm'
        items_per_sheet = tags_per_sheet
        if dual_lang_enabled:
            items_per_sheet //= 2

        dialog = QPrintDialog(self.printer, self)
        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            QMessageBox.warning(self, "Printing Cancelled",
                                "The batch print job was cancelled because no printer was selected.")
            return

        sku_pages = list(a4_layout_generator.chunks(skus_to_print, items_per_sheet))
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
            firebase_handler.log_activity(self.token, f"User printed a batch of {len(skus_to_print)} items.")

        for sku in skus_to_print:
            firebase_handler.add_item_to_display(sku, branch_db_key, self.token)
        if self.current_item_data.get('SKU') in skus_to_print:
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
        if not self.current_item_data: return

        menu = QMenu()
        templates = data_handler.get_item_templates(self.token)
        category = self.current_item_data.get("Categories", "Uncategorized")

        template_key = None
        for key, value in templates.items():
            if value.get("category_name") == category:
                template_key = key
                break

        if template_key and templates[template_key].get("specs"):
            for spec in templates[template_key]["specs"]:
                menu.addAction(spec)
            menu.addSeparator()

        custom_action = menu.addAction("Custom...")

        action = menu.exec(self.add_spec_button.mapToGlobal(self.add_spec_button.rect().bottomLeft()))

        if action:
            spec_text = action.text()
            if action == custom_action:
                text, ok = QInputDialog.getText(self, "Add Custom Specification", "Specification:")
                if ok and text:
                    self.specs_list.addItem(text)
            else:
                self.specs_list.addItem(spec_text + ":")
            self.update_preview()

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
