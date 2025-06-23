import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QFormLayout, QGroupBox, QComboBox, QMessageBox, QDialog,
                             QDialogButtonBox, QAbstractItemView, QTextEdit)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, QSize

# Import your existing logic
import data_handler
import price_generator
import a4_layout_generator


class NewItemDialog(QDialog):
    """A dialog to manually register a new item."""

    def __init__(self, sku, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Item")
        self.setMinimumWidth(500)
        self.new_item_data = {"SKU": sku}

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.sku_label = QLineEdit(sku)
        self.sku_label.setReadOnly(True)
        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.sale_price_input = QLineEdit()
        self.specs_input = QTextEdit()
        self.specs_input.setPlaceholderText(
            "Enter one specification per line.\nExample:\nScreen: 15.6 inch\nCPU: Intel Core i5")

        form_layout.addRow("SKU:", self.sku_label)
        form_layout.addRow("Item Name:", self.name_input)
        form_layout.addRow("Regular Price:", self.price_input)
        form_layout.addRow("Sale Price (optional):", self.sale_price_input)
        form_layout.addRow("Specifications:", self.specs_input)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Save Item")
        self.button_box.accepted.connect(self.save_item)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def save_item(self):
        """Validates input, formats data, and accepts the dialog."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Item Name cannot be empty.")
            return

        self.new_item_data["Name"] = name
        self.new_item_data["Regular price"] = self.price_input.text().strip()
        self.new_item_data["Sale price"] = self.sale_price_input.text().strip()

        # Format specs as HTML list for the description field
        specs = self.specs_input.toPlainText().strip().split('\n')
        specs_html = "<ul>" + "".join([f"<li>{s}</li>" for s in specs if s]) + "</ul>"
        self.new_item_data["Description"] = specs_html

        self.accept()


class BatchDialog(QDialog):
    """A dialog window for inputting multiple SKUs for batch processing."""

    def __init__(self, max_items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate A4 Batch")
        self.setMinimumSize(400, 500)
        self.max_items = max_items

        layout = QVBoxLayout(self)

        list_label = QLabel(f"SKUs to add (max {self.max_items} for this paper size):")
        self.sku_list_widget = QListWidget()
        self.sku_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(list_label)
        layout.addWidget(self.sku_list_widget)

        input_layout = QHBoxLayout()
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Enter SKU...")
        self.sku_input.returnPressed.connect(self.add_sku)
        self.add_button = QPushButton("Add SKU")
        self.add_button.clicked.connect(self.add_sku)
        input_layout.addWidget(self.sku_input)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_sku)
        layout.addWidget(remove_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Generate")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.check_limit()

    def check_limit(self):
        is_full = self.sku_list_widget.count() >= self.max_items
        self.sku_input.setEnabled(not is_full)
        self.add_button.setEnabled(not is_full)
        self.sku_input.setPlaceholderText("Page is full" if is_full else "Enter SKU...")

    def add_sku(self):
        if self.sku_list_widget.count() >= self.max_items:
            QMessageBox.information(self, "Limit Reached", f"The maximum of {self.max_items} items has been reached.")
            return

        sku = self.sku_input.text().strip().upper()
        if not sku: return

        if sku in [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]:
            QMessageBox.warning(self, "Duplicate", f"SKU '{sku}' is already in the list.")
            return

        if data_handler.find_item_by_sku(sku):
            self.sku_list_widget.addItem(sku)
            self.sku_input.clear()
            self.check_limit()
        else:
            QMessageBox.warning(self, "Not Found", f"SKU '{sku}' was not found.")

    def remove_sku(self):
        for item in self.sku_list_widget.selectedItems():
            self.sku_list_widget.takeItem(self.sku_list_widget.row(item))
        self.check_limit()

    def get_skus(self):
        return [self.sku_list_widget.item(i).text() for i in range(self.sku_list_widget.count())]


class PriceTagDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Price Tag Dashboard by Nikoloz Taturashvili")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(100, 100, 1400, 800)

        self.settings = data_handler.get_settings()
        self.paper_sizes = data_handler.get_all_paper_sizes()
        self.current_item_data = {}

        self.themes = {
            "Default": {"price_color": "#D32F2F", "text_color": "black", "strikethrough_color": "black",
                        "logo_path": "logo.png", "logo_scale_factor": 0.9},
            "Winter": {"price_color": "#0077be", "text_color": "#0a1931", "strikethrough_color": "#0a1931",
                       "logo_path": "logo-santa-hat.png", "logo_scale_factor": 1.1,
                       "bullet_image_path": "themes/snowflake.png", "background_snow": True}
        }

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.create_left_panel(), 1)
        main_layout.addWidget(self.create_right_panel(), 2)
        self.update_paper_size_combo()
        self.update_theme_combo()
        self.clear_all_fields()

    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        sku_box = QGroupBox("1. Find Item (for Single Preview)")
        sku_layout = QHBoxLayout()
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Enter SKU and press Enter...")
        self.sku_input.returnPressed.connect(self.find_item)
        find_button = QPushButton("Find")
        find_button.clicked.connect(self.find_item)
        sku_layout.addWidget(self.sku_input)
        sku_layout.addWidget(find_button)
        sku_box.setLayout(sku_layout)

        details_box = QGroupBox("Item Details")
        details_layout = QFormLayout()
        self.name_label = QLineEdit()
        self.price_label = QLineEdit()
        self.sale_price_label = QLineEdit()
        self.name_label.textChanged.connect(self.update_preview)
        self.price_label.textChanged.connect(self.update_preview)
        self.sale_price_label.textChanged.connect(self.update_preview)
        details_layout.addRow("Name:", self.name_label)
        details_layout.addRow("Price:", self.price_label)
        details_layout.addRow("Sale Price:", self.sale_price_label)
        details_box.setLayout(details_layout)

        settings_box = QGroupBox("2. Select Style")
        settings_layout = QFormLayout()
        self.paper_size_combo = QComboBox()
        self.paper_size_combo.currentTextChanged.connect(self.update_preview)
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self.update_preview)
        settings_layout.addRow("Paper Size:", self.paper_size_combo)
        settings_layout.addRow("Theme:", self.theme_combo)
        settings_box.setLayout(settings_layout)

        specs_box = QGroupBox("3. Edit Specifications")
        specs_layout = QVBoxLayout()
        self.specs_list = QListWidget()
        self.specs_list.itemChanged.connect(self.update_preview)
        specs_buttons_layout = QHBoxLayout()
        add_button, edit_button, remove_button = QPushButton("Add"), QPushButton("Edit"), QPushButton("Remove")
        add_button.clicked.connect(self.add_spec)
        edit_button.clicked.connect(self.edit_spec)
        remove_button.clicked.connect(self.remove_spec)
        specs_buttons_layout.addWidget(add_button)
        specs_buttons_layout.addWidget(edit_button)
        specs_buttons_layout.addWidget(remove_button)
        specs_layout.addWidget(self.specs_list)
        specs_layout.addLayout(specs_buttons_layout)
        specs_box.setLayout(specs_layout)

        actions_box = QGroupBox("4. Generate Output")
        actions_layout = QVBoxLayout()
        single_button = QPushButton("Generate Single Tag (on A4)")
        single_button.setFixedHeight(40)
        single_button.clicked.connect(self.generate_single)
        batch_button = QPushButton("Generate Full A4 Batch")
        batch_button.setFixedHeight(40)
        batch_button.clicked.connect(self.generate_batch)
        actions_layout.addWidget(single_button)
        actions_layout.addWidget(batch_button)
        actions_box.setLayout(actions_layout)

        layout.addWidget(sku_box)
        layout.addWidget(details_box)
        layout.addWidget(settings_box)
        layout.addWidget(specs_box)
        layout.addWidget(actions_box)
        return panel

    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        self.preview_label = QLabel("Enter an SKU to see a preview.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(600, 700)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        layout.addWidget(self.preview_label)
        return panel

    def update_paper_size_combo(self):
        self.paper_sizes = data_handler.get_all_paper_sizes()
        self.paper_size_combo.clear()
        self.paper_size_combo.addItems(self.paper_sizes.keys())
        self.paper_size_combo.setCurrentText(self.settings.get("default_size", "14.4x8cm"))

    def update_theme_combo(self):
        self.theme_combo.clear()
        self.theme_combo.addItems(self.themes.keys())
        self.theme_combo.setCurrentText(self.settings.get("default_theme", "Default"))

    def clear_all_fields(self):
        self.name_label.clear()
        self.price_label.clear()
        self.sale_price_label.clear()
        self.specs_list.clear()
        self.preview_label.setText("Enter an SKU to see a preview.")
        self.current_item_data = {}

    def find_item(self):
        sku = self.sku_input.text().strip().upper()
        if not sku: return

        item_data = data_handler.find_item_by_sku(sku)

        # UPDATED: Handle case where SKU is not found
        if not item_data:
            reply = QMessageBox.question(self, "Not Found",
                                         f"SKU '{sku}' was not found.\n\nWould you like to register it as a new item?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.register_new_item(sku)
            else:
                self.clear_all_fields()
            return

        self.current_item_data = item_data.copy()
        self.name_label.setText(item_data.get("Name", ""))
        self.price_label.setText(item_data.get("Regular price", "").strip())
        self.sale_price_label.setText(item_data.get("Sale price", "").strip())
        specs = data_handler.extract_specifications(item_data.get('Description'))
        warranty = item_data.get('Attribute 3 value(s)')
        if warranty and warranty != '-': specs.append(f"Warranty: {warranty}")
        self.specs_list.clear()
        self.specs_list.addItems(specs)
        self.update_preview()

    def register_new_item(self, sku):
        dialog = NewItemDialog(sku, self)
        if dialog.exec():
            new_data = dialog.new_item_data
            if data_handler.add_new_item(new_data):
                QMessageBox.information(self, "Success", f"Item '{sku}' has been saved.")
                # Automatically find the item we just added
                self.sku_input.setText(sku)
                self.find_item()
            else:
                QMessageBox.critical(self, "Error", "Could not save the new item to the data file.")

    def update_preview(self):
        if not self.current_item_data: return

        preview_data = self.get_current_data_from_ui()
        if not preview_data: return

        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        if not size_name or not theme_name: return

        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        pil_image = price_generator.create_price_tag(preview_data, size_config, theme_config)
        q_image = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, pil_image.width * 3,
                         QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaledToWidth(self.preview_label.width(), Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)

    def add_spec(self):
        self.specs_list.addItem("New Specification: Edit Me")
        self.specs_list.setCurrentRow(self.specs_list.count() - 1)
        self.edit_spec()

    def edit_spec(self):
        item = self.specs_list.currentItem()
        if item:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.specs_list.editItem(item)

    def remove_spec(self):
        item = self.specs_list.currentItem()
        if item:
            reply = QMessageBox.question(self, "Remove", f"Are you sure you want to remove '{item.text()}'?")
            if reply == QMessageBox.StandardButton.Yes:
                self.specs_list.takeItem(self.specs_list.row(item))
                self.update_preview()

    def get_current_data_from_ui(self):
        if not self.current_item_data: return None
        data = self.current_item_data.copy()
        data['Name'] = self.name_label.text()
        data['Regular price'] = self.price_label.text()
        data['Sale price'] = self.sale_price_label.text()
        data['specs'] = [self.specs_list.item(i).text() for i in range(self.specs_list.count())]
        return data

    def generate_single(self):
        data_to_print = self.get_current_data_from_ui()
        if not data_to_print:
            QMessageBox.warning(self, "No Item", "Please find an item first.")
            return

        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]

        tag_image = price_generator.create_price_tag(data_to_print, size_config, theme_config)
        a4_page = a4_layout_generator.create_a4_for_single(tag_image)

        filename = os.path.join("output", f"A4_SINGLE_{data_to_print['SKU']}.png")
        a4_page.save(filename, dpi=(price_generator.DPI, price_generator.DPI))
        QMessageBox.information(self, "Success", f"File saved to:\n{os.path.abspath(filename)}")

    def generate_batch(self):
        size_name, theme_name = self.paper_size_combo.currentText(), self.theme_combo.currentText()
        size_config, theme_config = self.paper_sizes[size_name], self.themes[theme_name]
        layout_info = a4_layout_generator.calculate_layout(*size_config['dims'])

        dialog = BatchDialog(max_items=layout_info['total'], parent=self)

        if dialog.exec():
            skus = dialog.get_skus()
            if not skus:
                QMessageBox.warning(self, "Empty List", "No SKUs were added to the batch.")
                return

            tag_images = []
            for sku in skus:
                item_data = data_handler.find_item_by_sku(sku)
                specs = data_handler.extract_specifications(item_data.get('Description'))
                warranty = item_data.get('Attribute 3 value(s)')
                if warranty and warranty != '-': specs.append(f"Warranty: {warranty}")
                item_data['specs'] = specs[:size_config['specs']]

                tag_image = price_generator.create_price_tag(item_data, size_config, theme_config)
                tag_images.append(tag_image)

            a4_sheet = a4_layout_generator.create_a4_sheet(tag_images, layout_info)
            filename = os.path.join("output", f"A4_BATCH_{size_name}.png")
            a4_sheet.save(filename, dpi=(price_generator.DPI, price_generator.DPI))
            QMessageBox.information(self, "Success", f"Batch file saved to:\n{os.path.abspath(filename)}")


if __name__ == "__main__":
    if not os.path.exists('output'): os.makedirs('output')
    if not os.path.exists('themes'): os.makedirs('themes')
    if not os.path.exists('fonts'): os.makedirs('fonts')

    app = QApplication(sys.argv)
    dashboard = PriceTagDashboard()
    dashboard.show()
    sys.exit(app.exec())
