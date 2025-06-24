import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QFormLayout, QGroupBox, QComboBox, QMessageBox, QDialog,
                             QDialogButtonBox, QAbstractItemView, QTextEdit, QCheckBox)
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
        self.add_button.clicked.connect(self.add_sku)
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
                self.add_sku()
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

    def add_sku(self):
        if self.sku_list_widget.count() >= self.max_items: QMessageBox.information(self,
                                                                                   self.tr.get("batch_limit_title"),
                                                                                   self.tr.get("batch_limit_message",
                                                                                               self.max_items)); return
        sku = self.sku_input.text().strip().upper()
        if not sku: return
        if sku in [self.sku_list_widget.item(i).text() for i in
                   range(self.sku_list_widget.count())]: QMessageBox.warning(self, self.tr.get("batch_duplicate_title"),
                                                                             self.tr.get("batch_duplicate_message",
                                                                                         sku)); return
        if data_handler.find_item_by_sku(sku):
            self.sku_list_widget.addItem(sku); self.sku_input.clear(); self.check_limit()
        else:
            QMessageBox.warning(self, self.tr.get("sku_not_found_title"), self.tr.get("sku_not_found_message", sku))

    def remove_sku(self):
        for item in self.sku_list_widget.selectedItems(): self.sku_list_widget.takeItem(self.sku_list_widget.row(item))
        self.check_limit()

    def get_skus(self):
        return [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]


class PriceTagDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = data_handler.get_settings();
        self.translator = Translator(self.settings.get("language", "en"));
        self.tr = self.translator.get
        self.setWindowIcon(QIcon("assets/logo.png"));
        self.setGeometry(100, 100, 1400, 800)
        self.paper_sizes = data_handler.get_all_paper_sizes();
        self.current_item_data = {}
        self.themes = {
            "Default": {"price_color": "#D32F2F", "text_color": "black", "strikethrough_color": "black",
                        "logo_path": "assets/logo.png", "logo_path_ka": "assets/logo-geo.png",
                        "logo_scale_factor": 0.9},
            "Winter": {"price_color": "#0077be", "text_color": "#0a1931", "strikethrough_color": "#0a1931",
                       "logo_path": "assets/logo-santa-hat.png", "logo_path_ka": "assets/logo-geo-santa-hat.png",
                       "logo_scale_factor": 1.1, "bullet_image_path": "assets/snowflake.png", "background_snow": True}
        }
        central_widget = QWidget();
        self.setCentralWidget(central_widget);
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.create_left_panel(), 1);
        main_layout.addWidget(self.create_right_panel(), 2)
        self.retranslate_ui();
        self.update_paper_size_combo();
        self.update_theme_combo();
        self.clear_all_fields()

    def create_left_panel(self):
        panel = QWidget();
        layout = QVBoxLayout(panel);
        self.find_item_group = QGroupBox();
        sku_layout = QHBoxLayout()
        self.sku_input = QLineEdit();
        self.sku_input.returnPressed.connect(self.find_item);
        self.find_button = QPushButton()
        self.find_button.clicked.connect(self.find_item);
        sku_layout.addWidget(self.sku_input);
        sku_layout.addWidget(self.find_button)
        self.find_item_group.setLayout(sku_layout);
        self.details_group = QGroupBox();
        details_layout = QFormLayout()
        self.name_label_widget, self.price_label_widget, self.sale_price_label_widget = QLabel(), QLabel(), QLabel()
        self.name_input, self.price_input, self.sale_price_input = QLineEdit(), QLineEdit(), QLineEdit()
        self.name_input.textChanged.connect(self.update_preview);
        self.price_input.textChanged.connect(self.update_preview);
        self.sale_price_input.textChanged.connect(self.update_preview)
        details_layout.addRow(self.name_label_widget, self.name_input);
        details_layout.addRow(self.price_label_widget, self.price_input);
        details_layout.addRow(self.sale_price_label_widget, self.sale_price_input)
        self.details_group.setLayout(details_layout);
        self.style_group = QGroupBox();
        settings_layout = QFormLayout()
        self.paper_size_label, self.theme_label = QLabel(), QLabel();
        self.paper_size_combo = QComboBox();
        self.paper_size_combo.currentTextChanged.connect(self.update_preview)
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
        self.output_group = QGroupBox();
        actions_layout = QVBoxLayout();
        self.single_button = QPushButton();
        self.single_button.setFixedHeight(40)
        self.single_button.clicked.connect(self.generate_single);
        self.batch_button = QPushButton();
        self.batch_button.setFixedHeight(40)
        self.batch_button.clicked.connect(self.generate_batch);
        actions_layout.addWidget(self.single_button);
        actions_layout.addWidget(self.batch_button)
        self.output_group.setLayout(actions_layout);
        self.lang_button = QPushButton();
        self.lang_button.setFixedSize(40, 40)
        self.lang_button.setIconSize(QSize(32, 32));
        self.lang_button.clicked.connect(self.switch_language);
        top_layout = QHBoxLayout()
        top_layout.addStretch();
        top_layout.addWidget(self.lang_button);
        layout.addLayout(top_layout);
        layout.addWidget(self.find_item_group)
        layout.addWidget(self.details_group);
        layout.addWidget(self.style_group);
        layout.addWidget(self.specs_group);
        layout.addWidget(self.output_group)
        return panel

    def create_right_panel(self):
        panel = QWidget();
        layout = QVBoxLayout(panel);
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter);
        self.preview_label.setMinimumSize(600, 700)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;");
        layout.addWidget(self.preview_label)
        return panel

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("window_title"));
        self.find_item_group.setTitle(self.tr("find_item_group"));
        self.sku_input.setPlaceholderText(self.tr("sku_placeholder"))
        self.find_button.setText(self.tr("find_button"));
        self.details_group.setTitle(self.tr("item_details_group"));
        self.name_label_widget.setText(self.tr("name_label"))
        self.price_label_widget.setText(self.tr("price_label"));
        self.sale_price_label_widget.setText(self.tr("sale_price_label"));
        self.style_group.setTitle(self.tr("style_group"))
        self.paper_size_label.setText(self.tr("paper_size_label"));
        self.theme_label.setText(self.tr("theme_label"));
        self.dual_lang_label.setText(self.tr("dual_language_label"))
        self.specs_group.setTitle(self.tr("specs_group"));
        self.add_button.setText(self.tr("add_button"));
        self.edit_button.setText(self.tr("edit_button"))
        self.remove_button.setText(self.tr("remove_button"));
        self.output_group.setTitle(self.tr("output_group"));
        self.single_button.setText(self.tr("generate_single_button"))
        self.batch_button.setText(self.tr("generate_batch_button"));
        if not self.current_item_data: self.preview_label.setText(self.tr("preview_default_text"))
        self.lang_button.setIcon(QIcon("assets/en.png" if self.translator.language == "en" else "assets/ka.png"))

    def switch_language(self):
        new_lang = "ka" if self.translator.language == "en" else "en"
        self.translator.set_language(new_lang);
        self.settings["language"] = new_lang
        data_handler.save_settings(self.settings);
        self.retranslate_ui()
        self.update_preview()

    def toggle_dual_language(self, state):
        self.settings["generate_dual_language"] = bool(state); data_handler.save_settings(self.settings)

    def update_paper_size_combo(self):
        self.paper_sizes = data_handler.get_all_paper_sizes();
        self.paper_size_combo.clear();
        self.paper_size_combo.addItems(self.paper_sizes.keys())
        self.paper_size_combo.setCurrentText(self.settings.get("default_size", "14.4x8cm"))

    def update_theme_combo(self):
        self.theme_combo.clear(); self.theme_combo.addItems(self.themes.keys()); self.theme_combo.setCurrentText(
            self.settings.get("default_theme", "Default"))

    def clear_all_fields(self):
        self.name_input.clear(); self.price_input.clear(); self.sale_price_input.clear(); self.specs_list.clear(); self.preview_label.setText(
            self.tr("preview_default_text")); self.current_item_data = {}

    def extract_part_number(self, description):
        """Finds and returns the part number from the description string."""
        if not description: return ""
        match = re.search(r'\[p/n\s*([^\]]+)\]', description)
        return match.group(1).strip() if match else ""

    def process_specifications(self, specs):
        first_warranty_found = False
        filtered_specs = []
        for spec in specs:
            if spec.lower().startswith('warranty:'):
                if not first_warranty_found:
                    filtered_specs.append(spec)
                    first_warranty_found = True
            else:
                filtered_specs.append(spec)
        return filtered_specs

    def find_item(self):
        sku = self.sku_input.text().strip().upper()
        if not sku: return
        item_data = data_handler.find_item_by_sku(sku)
        if not item_data:
            reply = QMessageBox.question(self, self.tr("sku_not_found_title"),
                                         self.tr("sku_not_found_message", sku) + self.tr("register_new_item_prompt"),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.register_new_item(sku)
            else:
                self.clear_all_fields()
            return
        self.current_item_data = item_data.copy()
        self.name_input.setText(item_data.get("Name", ""));
        self.price_input.setText(item_data.get("Regular price", "").strip());
        self.sale_price_input.setText(item_data.get("Sale price", "").strip())

        specs = data_handler.extract_specifications(item_data.get('Description'))
        warranty = item_data.get('Attribute 3 value(s)')
        if warranty and warranty != '-': specs.append(f"Warranty: {warranty}")

        self.current_item_data['part_number'] = self.extract_part_number(item_data.get('Description', ''))
        specs = self.process_specifications(specs)

        self.specs_list.clear();
        self.specs_list.addItems(specs);
        self.update_preview()

    def register_new_item(self, sku):
        dialog = NewItemDialog(sku, self.translator, self)
        if dialog.exec():
            new_data = dialog.new_item_data
            if data_handler.add_new_item(new_data):
                QMessageBox.information(self, self.tr("success_title"),
                                        self.tr("new_item_save_success", sku)); self.sku_input.setText(
                    sku); self.find_item()
            else:
                QMessageBox.critical(self, self.tr("new_item_validation_error"), self.tr.get("new_item_save_error"))

    def update_preview(self):
        data_to_preview = self.get_current_data_from_ui()
        if not data_to_preview: return
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        if not size_name or not theme_name: return
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        pil_image = price_generator.create_price_tag(data_to_preview, size_config, theme_config,
                                                     language=self.translator.language)
        q_image = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, pil_image.width * 3,
                         QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaledToWidth(self.preview_label.width(), Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)

    def add_spec(self):
        self.specs_list.addItem("New Specification: Edit Me"); self.specs_list.setCurrentRow(
            self.specs_list.count() - 1); self.edit_spec()

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

    def get_current_data_from_ui(self):
        if not self.current_item_data: return None
        data = self.current_item_data.copy();
        data['Name'] = self.name_input.text();
        data['Regular price'] = self.price_input.text()
        data['Sale price'] = self.sale_price_input.text();
        data['specs'] = [self.specs_list.item(i).text() for i in range(self.specs_list.count())]
        return data

    def handle_printing(self, pixmap):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution);
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            painter = QPainter();
            painter.begin(printer);
            rect = painter.viewport();
            size = pixmap.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio);
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect());
            painter.drawPixmap(0, 0, pixmap);
            painter.end()

    def generate_single(self):
        data_to_print = self.get_current_data_from_ui()
        if not data_to_print: QMessageBox.warning(self, self.tr("no_item_title"), self.tr("no_item_message")); return
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]

        if self.dual_lang_checkbox.isChecked():
            tag_en = price_generator.create_price_tag(data_to_print, size_config, theme_config, language='en')
            tag_ka = price_generator.create_price_tag(data_to_print, size_config, theme_config, language='ka')
            a4_pages = a4_layout_generator.create_a4_for_dual_single(tag_en, tag_ka)
            for i, page in enumerate(a4_pages):
                filename = os.path.join("output", f"A4_DUAL_{data_to_print['SKU']}_{i + 1}.png");
                page.save(filename, dpi=(price_generator.DPI, price_generator.DPI))
                self.handle_printing(QPixmap(filename))
        else:
            tag_image = price_generator.create_price_tag(data_to_print, size_config, theme_config,
                                                         language=self.translator.language)
            a4_page = a4_layout_generator.create_a4_for_single(tag_image)
            filename = os.path.join("output", f"A4_SINGLE_{data_to_print['SKU']}.png");
            a4_page.save(filename, dpi=(price_generator.DPI, price_generator.DPI))
            self.handle_printing(QPixmap(filename))
        QMessageBox.information(self, self.tr("success_title"),
                                self.tr("file_saved_message", os.path.abspath("output")))

    def generate_batch(self):
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        layout_info = a4_layout_generator.calculate_layout(*size_config['dims'])

        dialog = BatchDialog(max_items=layout_info['total'], translator=self.translator,
                             dual_lang_enabled=self.dual_lang_checkbox.isChecked(), parent=self)

        if dialog.exec():
            skus = dialog.get_skus()
            if not skus: QMessageBox.warning(self, self.tr("batch_empty_title"), self.tr("batch_empty_message")); return

            tag_images = []
            for sku in skus:
                item_data = data_handler.find_item_by_sku(sku)
                specs = data_handler.extract_specifications(item_data.get('Description'));
                warranty = item_data.get('Attribute 3 value(s)')
                if warranty and warranty != '-': specs.append(f"Warranty: {warranty}")

                specs = self.process_specifications(specs)

                item_data['specs'] = specs[:size_config['specs']]
                item_data['part_number'] = self.extract_part_number(item_data.get('Description', ''))

                if self.dual_lang_checkbox.isChecked():
                    tag_images.append(
                        price_generator.create_price_tag(item_data, size_config, theme_config, language='en'))
                    tag_images.append(
                        price_generator.create_price_tag(item_data, size_config, theme_config, language='ka'))
                else:
                    tag_images.append(price_generator.create_price_tag(item_data, size_config, theme_config,
                                                                       language=self.translator.language))

            a4_sheet = a4_layout_generator.create_a4_sheet(tag_images, layout_info)
            filename = os.path.join("output", f"A4_BATCH_{size_name}.png")
            a4_sheet.save(filename, dpi=(price_generator.DPI, price_generator.DPI))
            self.handle_printing(QPixmap(filename))
            QMessageBox.information(self, self.tr("success_title"),
                                    self.tr("file_saved_message", os.path.abspath(filename)))


if __name__ == "__main__":
    for folder in ['output', 'assets', 'fonts']:
        if not os.path.exists(folder): os.makedirs(folder)

    app = QApplication(sys.argv)
    dashboard = PriceTagDashboard()
    dashboard.show()
    sys.exit(app.exec())
