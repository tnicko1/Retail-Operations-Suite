import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QFormLayout, QGroupBox, QComboBox, QMessageBox, QDialog,
                             QDialogButtonBox)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, QSize

# Import your existing logic
import data_handler
import price_generator
import a4_layout_generator


class PriceTagDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Price Tag Dashboard by Nikoloz Taturashvili")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(100, 100, 1400, 800)

        # --- Load settings and data ---
        self.settings = data_handler.get_settings()
        self.paper_sizes = data_handler.get_all_paper_sizes()
        self.current_item_data = {}

        # --- Define Themes ---
        self.themes = {
            "Default": {"price_color": "#D32F2F"},
            "New Year's": {"price_color": "#008000", "background_image": "themes/new_year.png"}
        }

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Create Panels ---
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        main_layout.addWidget(left_panel, 1)  # Ratio 1
        main_layout.addWidget(right_panel, 2)  # Ratio 2 (larger)

        # --- Initial State ---
        self.update_paper_size_combo()
        self.update_theme_combo()
        self.clear_all_fields()

    def create_left_panel(self):
        """Creates the left-side control panel widget."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # --- SKU Input ---
        sku_box = QGroupBox("1. Find Item")
        sku_layout = QHBoxLayout()
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Enter SKU and press Enter...")
        self.sku_input.returnPressed.connect(self.find_item)
        find_button = QPushButton("Find")
        find_button.clicked.connect(self.find_item)
        sku_layout.addWidget(self.sku_input)
        sku_layout.addWidget(find_button)
        sku_box.setLayout(sku_layout)

        # --- Item Details ---
        details_box = QGroupBox("Item Details")
        details_layout = QFormLayout()
        self.name_label = QLineEdit(readOnly=True)
        self.price_label = QLineEdit(readOnly=True)
        self.sale_price_label = QLineEdit(readOnly=True)
        details_layout.addRow("Name:", self.name_label)
        details_layout.addRow("Price:", self.price_label)
        details_layout.addRow("Sale Price:", self.sale_price_label)
        details_box.setLayout(details_layout)

        # --- Settings & Theme ---
        settings_box = QGroupBox("2. Select Style")
        settings_layout = QFormLayout()
        self.paper_size_combo = QComboBox()
        self.paper_size_combo.currentTextChanged.connect(self.update_preview)
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self.update_preview)
        settings_layout.addRow("Paper Size:", self.paper_size_combo)
        settings_layout.addRow("Theme:", self.theme_combo)
        settings_box.setLayout(settings_layout)

        # --- Specs Editor ---
        specs_box = QGroupBox("3. Edit Specifications")
        specs_layout = QVBoxLayout()
        self.specs_list = QListWidget()
        self.specs_list.itemChanged.connect(self.update_preview)
        specs_buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_spec)
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_spec)
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_spec)
        specs_buttons_layout.addWidget(add_button)
        specs_buttons_layout.addWidget(edit_button)
        specs_buttons_layout.addWidget(remove_button)
        specs_layout.addWidget(self.specs_list)
        specs_layout.addLayout(specs_buttons_layout)
        specs_box.setLayout(specs_layout)

        # --- Action Buttons ---
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

        # --- Add all widgets to left panel ---
        layout.addWidget(sku_box)
        layout.addWidget(details_box)
        layout.addWidget(settings_box)
        layout.addWidget(specs_box)
        layout.addWidget(actions_box)

        return panel

    def create_right_panel(self):
        """Creates the right-side live preview panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        self.preview_label = QLabel("Enter an SKU to see a preview.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(600, 700)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        layout.addWidget(self.preview_label)
        return panel

    # --- UI Update Functions ---
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
        """Fetches item data and populates the UI."""
        sku = self.sku_input.text().strip()
        if not sku:
            return

        item_data = data_handler.find_item_by_sku(sku)
        if not item_data:
            QMessageBox.warning(self, "Not Found", f"SKU '{sku}' was not found in the data file.")
            self.clear_all_fields()
            return

        self.current_item_data = item_data
        self.name_label.setText(item_data.get("Name", ""))
        self.price_label.setText(item_data.get("Regular price", ""))
        self.sale_price_label.setText(item_data.get("Sale price", ""))

        specs = data_handler.extract_specifications(item_data.get('Description'))
        warranty = item_data.get('Attribute 3 value(s)')
        if warranty and warranty != '-':
            specs.append(f"Warranty: {warranty}")

        self.specs_list.clear()
        self.specs_list.addItems(specs)
        self.update_preview()

    def update_preview(self):
        """Generates a new price tag image and displays it."""
        if not self.current_item_data:
            return

        specs = [self.specs_list.item(i).text() for i in range(self.specs_list.count())]
        self.current_item_data['specs'] = specs

        size_name = self.paper_size_combo.currentText()
        theme_name = self.theme_combo.currentText()
        if not size_name or not theme_name:
            return

        size_config = self.paper_sizes[size_name]
        theme_config = self.themes[theme_name]

        pil_image = price_generator.create_price_tag(self.current_item_data, size_config, theme_config)

        # Convert PIL image to QPixmap
        q_image = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, pil_image.width * 3,
                         QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # Scale pixmap to fit the preview label while maintaining aspect ratio
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation))

    # --- Spec Editor Functions ---
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

    # --- Generation Functions ---
    def generate_single(self):
        if not self.current_item_data:
            QMessageBox.warning(self, "No Item", "Please find an item first.")
            return

        size_name = self.paper_size_combo.currentText()
        theme_name = self.theme_combo.currentText()
        size_config = self.paper_sizes[size_name]
        theme_config = self.themes[theme_name]

        tag_image = price_generator.create_price_tag(self.current_item_data, size_config, theme_config)
        a4_page = a4_layout_generator.create_a4_for_single(tag_image)

        filename = os.path.join("output", f"A4_SINGLE_{self.current_item_data['SKU']}.png")
        a4_page.save(filename, dpi=(price_generator.DPI, price_generator.DPI))
        QMessageBox.information(self, "Success", f"File saved to:\n{os.path.abspath(filename)}")

    def generate_batch(self):
        # This function would be expanded to allow adding multiple SKUs
        QMessageBox.information(self, "Batch Mode",
                                "This would open a new window to input multiple SKUs for a full A4 page.")


if __name__ == "__main__":
    # Ensure necessary folders exist
    if not os.path.exists('output'): os.makedirs('output')
    if not os.path.exists('themes'): os.makedirs('themes')
    if not os.path.exists('fonts'): os.makedirs('fonts')

    app = QApplication(sys.argv)
    dashboard = PriceTagDashboard()
    dashboard.show()
    sys.exit(app.exec())
