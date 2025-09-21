import copy
import sys
from datetime import datetime

import pytz
from PyQt6.QtCore import Qt, QSize, QTimer, QRectF
from PyQt6.QtGui import QIcon, QAction, QPixmap, QImage, QPainter, QPageLayout
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
                             QFormLayout, QGroupBox, QComboBox, QMessageBox, QDialog,
                             QDialogButtonBox, QAbstractItemView, QTextEdit, QCheckBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QFileDialog,
                             QMenuBar, QTabWidget, QMenu, QDoubleSpinBox, QSpinBox, QSlider, QApplication)

import a4_layout_generator
import data_handler
import firebase_handler
import price_generator
from dialogs import (LayoutSettingsDialog, AddEditSizeDialog, CustomSizeManagerDialog, QuickStockDialog,
                     TemplateSelectionDialog, NewItemDialog, PrintQueueDialog, PriceHistoryDialog,
                     TemplateManagerDialog, ActivityLogDialog, DisplayManagerDialog, UserManagementDialog,
                     ColumnMappingManagerDialog, BrandSelectionDialog)
from translations import Translator
from utils import format_timedelta, resource_path


class RetailOperationsSuite(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.uid = self.user.get('localId')
        # self.token is now managed by self.ensure_token_valid()
        self.token = self.user.get('idToken') 
        self.settings = data_handler.get_settings()
        self.translator = Translator(self.settings.get("language", "en"))
        self.tr = self.translator.get
        self.printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        self.column_mappings = firebase_handler.get_column_mappings(self.token)

        # Barcode scanner detection setup
        self.scan_timer = QTimer(self)
        self.scan_timer.setSingleShot(True)
        self.scan_timer.timeout.connect(self.process_scan)

        self.branch_data_map = {
            "branch_vaja": {"db_key": "Vazha-Pshavela Shop", "stock_col": "Stock Vaja"},
            "branch_marj": {"db_key": "Marjanishvili", "stock_col": "Stock Marj"},
            "branch_gldani": {"db_key": "Gldani Shop", "stock_col": "Stock Gldan"},
        }

        self.setWindowIcon(QIcon(resource_path("assets/program/logo-no-flair.ico")))
        self.setGeometry(100, 100, 1400, 800)
        self.paper_sizes = data_handler.get_all_paper_sizes()
        self.current_item_data = {}
        self.all_items_cache = firebase_handler.get_all_items(self.token) or {}
        self.themes = {
            "Default": {
                "name_color": "black",
                "price_color": "#D32F2F",
                "sku_color": "black",
                "accent_color": "black",
                "strikethrough_color": "black",
                "logo_path": resource_path("assets/logo.png"),
                "logo_path_ka": resource_path("assets/logo-geo.png")
            },
            "Winter": {
                "name_color": "#0a1931",
                "price_color": "#0077be",
                "sku_color": "#0a1931",
                "accent_color": "#0a1931",
                "strikethrough_color": "#0a1931",
                "logo_path": resource_path("assets/logo-santa-hat.png"),
                "logo_path_ka": resource_path("assets/logo-geo-santa-hat.png"),
                "bullet_image_path": resource_path("assets/snowflake.png"),
                "background_snow": True
            },
            "Back To School": {
                "name_color": "white",
                "price_color": "#FFC107",
                "sku_color": "white",
                "accent_color": "white",
                "strikethrough_color": "white",
                "logo_path": resource_path("assets/logo.png"),
                "logo_path_ka": resource_path("assets/logo-geo.png"),
                "background_grid": True,
                "background_color": "#2E7D32",
                "draw_school_icons": True
            }
        }
        self.brands = {
            "None": {},
            "Baseus": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Baseus.png"),
                "brand_name": "Baseus",
                "bg_color": "#FFF100",
                "text_color": "black"
            },
            "Acefast": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Acefast.png"),
                "brand_name": "Acefast",
                "bg_color": "#536C4C",
                "text_color": "black"
            },
            "Anker": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Anker.png"),
                "brand_name": "Anker",
                "bg_color": "#00A7E1",
                "text_color": "black"
            },
            "Kingston": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Kingston.png"),
                "brand_name": "Kingston",
                "bg_color": "#ED1C2E",
                "text_color": "black"
            },
            "BOYA": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/BOYA.png"),
                "brand_name": "BOYA",
                "bg_color": "#1F86C0",
                "text_color": "black"
            },
            "Gembird": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Gembird.png"),
                "brand_name": "Gembird",
                "bg_color": "#DF0024",
                "text_color": "black"
            },
            "Gembird Gray": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Gembird_Gray.png"),
                "brand_name": "Gembird",
                "bg_color": "#023D5B",
                "text_color": "black"
            },
            "Vention": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Vention.png"),
                "brand_name": "Vention",
                "bg_color": "#00ADEF",
                "text_color": "black"
            },
            "APC": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/APC.png"),
                "brand_name": "APC",
                "bg_color": "#CC1E4C",
                "text_color": "black"
            },
            "Defender": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Defender.png"),
                "brand_name": "Defender",
                "bg_color": "#0066B3",
                "text_color": "black"
            },
            "Yamatik": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Yamatik.png"),
                "brand_name": "Yamatik",
                "bg_color": "#E15517",
                "text_color": "black"
            },
            "SVEN": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/SVEN.png"),
                "brand_name": "SVEN",
                "bg_color": "#25478A",
                "text_color": "black"
            },
            "TP-LINK": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/tp-link.png"),
                "brand_name": "TP-Link",
                "bg_color": "#4ACBD6",
                "text_color": "black"
            },
            "Logitech": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Logitech.png"),
                "brand_name": "Logitech",
                "bg_color": "#28e9cf",
                "text_color": "black"
            },
            "Logitech G": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Logitech-G.png"),
                "brand_name": "Logitech",
                "bg_color": "#00A7E0",
                "text_color": "black"
            },
            "Bloody": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Bloody.png"),
                "brand_name": "Bloody",
                "bg_color": "#E50012",
                "text_color": "black"
            },
            "HP": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/HP.png"),
                "brand_name": "HP",
                "bg_color": "#0096D6",
                "text_color": "black"
            },
            "Legion": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Legion.png"),
                "brand_name": "Lenovo Legion",
                "bg_color": "#3e8ddc",
                "text_color": "black"
            },
            "Genius": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Genius.png"),
                "brand_name": "Genius",
                "bg_color": "#CC2229",
                "text_color": "black"
            },
            "A4Tech": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/A4tech.png"),
                "brand_name": "A4Tech",
                "bg_color": "#F39801",
                "text_color": "black"
            },
            "Razer": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Razer.png"),
                "brand_name": "Razer",
                "bg_color": "#00FF00",
                "text_color": "black"
            },
            "Trust": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Trust.png"),
                "brand_name": "Trust",
                "bg_color": "#E3252F",
                "text_color": "black"
            },
            "Acer Predator": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Predator.png"),
                "brand_name": "Acer Predator",
                "bg_color": "#00FFFF",
                "text_color": "black"
            },
            "Dell": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Dell.png"),
                "brand_name": "Dell",
                "bg_color": "#007DB8",
                "text_color": "black"
            },
            "HyperX": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/HyperX.png"),
                "brand_name": "HyperX",
                "bg_color": "#E31836",
                "text_color": "black"
            },
            "Rivacase": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Rivacase.png"),
                "brand_name": "RIVACASE",
                "bg_color": "#0F2C3E",
                "text_color": "black"
            },
            "SteelSeries": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/SteelSeries.png"),
                "brand_name": "SteelSeries",
                "bg_color": "#EC3E09",
                "text_color": "black"
            },
            "Panasonic": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Panasonic.png"),
                "brand_name": "Panasonic",
                "bg_color": "#0056A8",
                "text_color": "black"
            },
            "Sony": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/Sony.png"),
                "brand_name": "Sony",
                "bg_color": "#003366",
                "text_color": "black"
            },
            "SoundCore": {
                "design": "modern_brand",
                "accessory_logo_path": resource_path("assets/brands/SoundCore.png"),
                "brand_name": "SoundCore",
                "bg_color": "#00A9E2",
                "text_color": "black"
            }
        }

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.brands_by_name = {}
        for key, config in self.brands.items():
            brand_name = config.get("brand_name")
            if brand_name:
                if brand_name not in self.brands_by_name:
                    self.brands_by_name[brand_name] = []
                self.brands_by_name[brand_name].append(key)

        self.generator_tab = QWidget()
        self.dashboard_tab = QWidget()

        self.tab_widget.addTab(self.generator_tab, "Price Tag Generator")

        self.active_dialog = None  # To hold a reference to any active dialog

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

        # --- Controls ---
        controls_layout = QHBoxLayout()
        self.refresh_button = QPushButton(self.tr("dashboard_refresh_button"))
        self.refresh_button.clicked.connect(self.update_dashboard_data)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # --- Stats ---
        self.stats_group = QGroupBox(self.tr("dashboard_stats_group"))
        stats_layout = QFormLayout()
        self.stats_labels = {}
        for key, data in self.branch_data_map.items():
            display_name = self.tr(key)
            self.stats_labels[key] = QLabel("...")
            stats_layout.addRow(f"{display_name} ({self.tr('dashboard_on_display_label')})", self.stats_labels[key])
        self.stats_group.setLayout(stats_layout)
        layout.addWidget(self.stats_group)

        # --- Low Stock ---
        self.low_stock_group = QGroupBox()
        low_stock_layout = QVBoxLayout()

        # Filters
        filters_layout = QHBoxLayout()
        self.branch_filter_combo = QComboBox()
        self.branch_filter_combo.addItem(self.tr("dashboard_all_branches"), "all")
        for key, data in self.branch_data_map.items():
            self.branch_filter_combo.addItem(self.tr(key), key)
        self.branch_filter_combo.currentIndexChanged.connect(self.filter_low_stock_list)

        self.category_filter_combo = QComboBox()
        self.category_filter_combo.currentIndexChanged.connect(self.filter_low_stock_list)

        filters_layout.addWidget(QLabel(self.tr("dashboard_filter_branch")))
        filters_layout.addWidget(self.branch_filter_combo)
        filters_layout.addWidget(QLabel(self.tr("dashboard_filter_category")))
        filters_layout.addWidget(self.category_filter_combo)
        filters_layout.addStretch()
        low_stock_layout.addLayout(filters_layout)

        # Table
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(4)
        self.low_stock_table.setHorizontalHeaderLabels(
            [self.tr("dashboard_header_sku"), self.tr("dashboard_header_name"), self.tr("dashboard_header_category"),
             self.tr("dashboard_header_stock")])
        header = self.low_stock_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(1, 350)  # Give name column a good starting width
        self.low_stock_table.setSortingEnabled(False)
        header.sectionClicked.connect(self.sort_low_stock_table)
        self.current_sort_col = -1
        self.current_sort_order = Qt.SortOrder.AscendingOrder

        low_stock_layout.addWidget(self.low_stock_table)
        self.low_stock_group.setLayout(low_stock_layout)
        layout.addWidget(self.low_stock_group)

        self.update_dashboard_data()

    def update_dashboard_data(self):
        token = self.ensure_token_valid()
        if not token: return
        self.all_items_cache = firebase_handler.get_all_items(token) or {}
        display_statuses = firebase_handler.get_display_status(token)

        for key, data in self.branch_data_map.items():
            db_key = data['db_key']
            count = len(display_statuses.get(db_key, []))
            self.stats_labels[key].setText(str(count))

        self.category_filter_combo.blockSignals(True)
        self.category_filter_combo.clear()
        self.category_filter_combo.addItem(self.tr("dashboard_all_categories"), "all")
        categories = sorted(list(set(item.get("Categories", "N/A") for item in self.all_items_cache.values())))
        for cat in categories:
            self.category_filter_combo.addItem(cat)
        self.category_filter_combo.blockSignals(False)

        self.filter_low_stock_list()

    def filter_low_stock_list(self):
        threshold = self.settings.get('low_stock_threshold', 3)
        self.low_stock_group.setTitle(self.tr("dashboard_low_stock_label", threshold))

        selected_branch_key = self.branch_filter_combo.currentData()
        selected_category = self.category_filter_combo.currentText()
        if self.category_filter_combo.currentData() == "all":
            selected_category = "all"

        low_stock_items = []
        for sku, item_data in self.all_items_cache.items():
            if selected_category != "all" and item_data.get("Categories") != selected_category:
                continue

            branches_to_check = [selected_branch_key] if selected_branch_key != "all" else self.branch_data_map.keys()

            for branch_key in branches_to_check:
                branch_info = self.branch_data_map[branch_key]
                stock_col = branch_info['stock_col']
                stock_str = str(item_data.get(stock_col, '0')).replace(',', '')
                if stock_str.isdigit() and 0 < int(stock_str) <= threshold:
                    low_stock_items.append({
                        "sku": sku,
                        "name": item_data.get("Name", "N/A"),
                        "category": item_data.get("Categories", "N/A"),
                        "stock_val": int(stock_str),
                        "stock_display": f"{self.tr(branch_key)}: {int(stock_str)}"
                    })

        self.populate_low_stock_table(low_stock_items)

    def sort_low_stock_table(self, column_index):
        if self.current_sort_col == column_index:
            self.current_sort_order = Qt.SortOrder.DescendingOrder if self.current_sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.current_sort_col = column_index
            self.current_sort_order = Qt.SortOrder.AscendingOrder

        self.low_stock_table.sortItems(column_index, self.current_sort_order)

    def populate_low_stock_table(self, items):
        self.low_stock_table.setRowCount(0)
        self.low_stock_table.setRowCount(len(items))

        for row, item in enumerate(items):
            sku_item = QTableWidgetItem(item['sku'])
            name_item = QTableWidgetItem(item['name'])
            category_item = QTableWidgetItem(item['category'])
            stock_item = QTableWidgetItem()
            stock_item.setData(Qt.ItemDataRole.DisplayRole, item['stock_display'])
            stock_item.setData(Qt.ItemDataRole.UserRole, item['stock_val'])

            self.low_stock_table.setItem(row, 0, sku_item)
            self.low_stock_table.setItem(row, 1, name_item)
            self.low_stock_table.setItem(row, 2, category_item)
            self.low_stock_table.setItem(row, 3, stock_item)

    def create_menu(self):
        menu_bar = self.menuBar()
        menu_bar.clear()

        file_menu = menu_bar.addMenu(self.tr("file_menu"))

        stock_checker_action = QAction(self.tr("stock_checker_menu"), self)
        stock_checker_action.triggered.connect(self.open_quick_stock_checker)
        file_menu.addAction(stock_checker_action)

        select_printer_action = QAction(self.tr("select_printer_menu"), self)
        select_printer_action.triggered.connect(self.select_printer)
        file_menu.addAction(select_printer_action)

        file_menu.addSeparator()

        logout_action = QAction(self.tr("logout_menu"), self)
        logout_action.triggered.connect(self.handle_logout)
        file_menu.addAction(logout_action)

        if self.user.get('role') == 'Admin':
            admin_menu = menu_bar.addMenu(self.tr('admin_tools_menu'))

            upload_action = QAction(self.tr('admin_upload_master_list'), self)
            upload_action.triggered.connect(self.upload_master_list)
            admin_menu.addAction(upload_action)

            template_manager_action = QAction(self.tr("admin_template_manager"), self)
            template_manager_action.triggered.connect(self.open_template_manager)
            admin_menu.addAction(template_manager_action)

            size_manager_action = QAction(self.tr("size_manager_menu"), self)
            size_manager_action.triggered.connect(self.open_size_manager)
            admin_menu.addAction(size_manager_action)

            mapping_manager_action = QAction(self.tr("column_mapping_menu"), self)
            mapping_manager_action.triggered.connect(self.open_column_mapping_manager)
            admin_menu.addAction(mapping_manager_action)

            activity_log_action = QAction(self.tr("admin_activity_log"), self)
            activity_log_action.triggered.connect(self.open_activity_log)
            admin_menu.addAction(activity_log_action)

            user_mgmt_action = QAction(self.tr('admin_manage_users'), self)
            user_mgmt_action.triggered.connect(self.open_user_management)
            admin_menu.addAction(user_mgmt_action)

    def open_quick_stock_checker(self):
        token = self.ensure_token_valid()
        if not token: return
        self.active_dialog = QuickStockDialog(self.translator, token, self.branch_data_map, self)
        self.active_dialog.exec()
        self.active_dialog = None

    def open_size_manager(self):
        dialog = CustomSizeManagerDialog(self.translator, self)
        if dialog.exec():
            self.update_paper_size_combo()

    def open_column_mapping_manager(self):
        token = self.ensure_token_valid()
        if not token: return
        dialog = ColumnMappingManagerDialog(self.translator, token, self)
        dialog.exec()

    def open_user_management(self):
        dialog = UserManagementDialog(self.translator, self.user, self)
        dialog.exec()

    def open_template_manager(self):
        token = self.ensure_token_valid()
        if not token: return
        dialog = TemplateManagerDialog(self.translator, token, self)
        dialog.exec()

    def open_activity_log(self):
        token = self.ensure_token_valid()
        if not token: return
        dialog = ActivityLogDialog(self.translator, token, self)
        dialog.exec()

    def upload_master_list(self):
        filepath, _ = QFileDialog.getOpenFileName(self, self.tr("open_master_list_title"), "",
                                                  "Text Files (*.txt);;All Files (*)")
        if filepath:
            token = self.ensure_token_valid()
            if not token: return
            success, val1, val2 = firebase_handler.sync_products_from_file(filepath, token)
            if success:
                message = self.tr("sync_results_message", val1, val2)
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText(message)
                msg.setWindowTitle(self.tr("success_title"))
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()
                self.update_dashboard_data()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(val1)
                msg.setWindowTitle("Error")
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()

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

        self.branch_group = QGroupBox()
        branch_layout = QFormLayout()
        self.branch_combo = QComboBox()
        self.branch_combo.currentIndexChanged.connect(self.handle_branch_change)
        self.branch_label_widget = QLabel()
        branch_layout.addRow(self.branch_label_widget, self.branch_combo)
        self.branch_group.setLayout(branch_layout)

        self.find_item_group = QGroupBox(self.tr("find_item_group"))
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
        self.status_duration_label = QLabel()  # New label for duration
        self.stock_label_title = QLabel(self.tr("stock_label"))
        self.stock_label_value = QLabel("-")
        self.low_stock_warning_label = QLabel()

        self.toggle_status_button = QPushButton()
        self.toggle_status_button.clicked.connect(self.toggle_display_status)
        self.toggle_status_button.setVisible(False)

        status_layout.addWidget(self.status_label_title)
        status_layout.addWidget(self.status_label_value)
        status_layout.addWidget(self.status_duration_label)  # Add to layout
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
        style_layout = QVBoxLayout()
        settings_layout = QFormLayout()
        self.paper_size_label, self.theme_label, self.brand_label = QLabel(), QLabel(), QLabel()
        self.paper_size_combo = QComboBox()
        self.paper_size_combo.currentTextChanged.connect(self.handle_paper_size_change)
        self.theme_combo = QComboBox()
        self.brand_combo = QComboBox()
        
        # Connect signals for exclusivity
        self.theme_combo.currentTextChanged.connect(self.handle_theme_selection)
        self.brand_combo.currentTextChanged.connect(self.handle_brand_selection)

        self.dual_lang_label = QLabel()
        self.dual_lang_checkbox = QCheckBox()
        self.dual_lang_checkbox.setChecked(self.settings.get("generate_dual_language", False))
        self.dual_lang_checkbox.stateChanged.connect(self.toggle_dual_language)
        self.special_tag_label = QLabel()
        self.special_tag_checkbox = QCheckBox()
        self.special_tag_checkbox.stateChanged.connect(self.update_preview)
        settings_layout.addRow(self.paper_size_label, self.paper_size_combo)
        settings_layout.addRow(self.theme_label, self.theme_combo)
        settings_layout.addRow(self.brand_label, self.brand_combo)
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.dual_lang_label)
        checkbox_layout.addWidget(self.dual_lang_checkbox)
        checkbox_layout.addStretch()
        checkbox_layout.addWidget(self.special_tag_label)
        checkbox_layout.addWidget(self.special_tag_checkbox)
        checkbox_layout.addStretch()
        style_layout.addLayout(settings_layout)
        style_layout.addLayout(checkbox_layout)

        self.layout_settings_button = QPushButton()
        self.layout_settings_button.clicked.connect(self.open_layout_settings)
        style_layout.addWidget(self.layout_settings_button)

        self.style_group.setLayout(style_layout);

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

        layout.addWidget(self.branch_group)
        layout.addWidget(self.find_item_group)
        layout.addWidget(self.details_group)
        layout.addWidget(self.style_group)
        layout.addWidget(self.specs_group)
        layout.addWidget(self.output_group)
        layout.addStretch()

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
        self.tab_widget.setTabText(0, self.tr("generator_tab_title"))
        if self.user.get('role') == 'Admin':
            self.tab_widget.setTabText(1, self.tr("admin_dashboard"))
            self.refresh_button.setText(self.tr("dashboard_refresh_button"))
            self.stats_group.setTitle(self.tr("dashboard_stats_group"))
            threshold = self.settings.get('low_stock_threshold', 3)
            self.low_stock_group.setTitle(self.tr("dashboard_low_stock_label", threshold))
            self.low_stock_table.setHorizontalHeaderLabels(
                [self.tr("dashboard_header_sku"), self.tr("dashboard_header_name"),
                 self.tr("dashboard_header_category"), self.tr("dashboard_header_stock")])

        self.update_branch_combo()
        self.update_paper_size_combo()
        self.update_theme_combo()
        self.update_brand_combo()
        self.create_menu()

        self.branch_group.setTitle(self.tr("branch_group_title"))
        self.branch_label_widget.setText(self.tr("branch_label"))
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
        self.brand_label.setText(self.tr("brand_label"))
        self.dual_lang_label.setText(self.tr("dual_language_label"))
        self.special_tag_label.setText(self.tr("special_tag_label"))
        self.layout_settings_button.setText(self.tr("layout_settings_button"))
        self.specs_group.setTitle(self.tr("specs_group"))
        self.add_spec_button.setText(self.tr("add_button"))
        self.edit_button.setText(self.tr("edit_button"))
        self.remove_button.setText(self.tr("remove_button"))
        self.output_group.setTitle(self.tr("output_group"))
        self.display_manager_button.setText(self.tr("display_manager_button"))
        self.single_button.setText(self.tr("generate_single_button"))
        self.batch_button.setText(self.tr("generate_batch_button"))
        self.status_label_title.setText(f"{self.tr('status_label')}:")
        self.stock_label_title.setText(self.tr("stock_label"))
        self.lang_button.setIcon(QIcon(resource_path("assets/en.png" if self.translator.language == "en" else "assets/ka.png")))
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

        # If a dialog with retranslate_ui is active, call it
        if self.active_dialog and hasattr(self.active_dialog, 'retranslate_ui'):
            self.active_dialog.retranslate_ui()

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
        token = self.ensure_token_valid()
        if not token: return
        self.active_dialog = DisplayManagerDialog(self.translator, branch_db_key, branch_stock_col, self.user, self)
        self.active_dialog.exec()
        self.active_dialog = None  # Clear reference after dialog closes

    def open_print_queue(self):
        dialog = PrintQueueDialog(self.translator, self.user, self)
        if dialog.exec():
            skus_to_print = dialog.get_skus()
            use_modern_design = dialog.get_modern_design_state()
            if skus_to_print:
                self.generate_batch(skus_to_print, use_modern_design)

    def add_current_to_queue(self):
        if not self.current_item_data:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Please find an item to add to the queue.")
            msg.setWindowTitle("No Item")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        sku = self.current_item_data.get("SKU")
        token = self.ensure_token_valid()
        if not token: return
        queue = firebase_handler.get_print_queue(self.user)
        if sku not in queue:
            queue.append(sku)
            firebase_handler.save_print_queue(self.user, queue)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(f"Item {sku} added to the print queue.")
            msg.setWindowTitle("Success")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(f"Item {sku} is already in the print queue.")
            msg.setWindowTitle("Duplicate")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()

    def show_price_history(self):
        if not self.current_item_data: return
        sku = self.current_item_data.get("SKU")
        token = self.ensure_token_valid()
        if not token: return
        dialog = PriceHistoryDialog(sku, self.translator, token, self)
        dialog.exec()

    def update_paper_size_combo(self):
        self.paper_size_combo.blockSignals(True)
        current_text = self.paper_size_combo.currentText()
        self.paper_size_combo.clear()
        self.paper_sizes = data_handler.get_all_paper_sizes()
        sorted_sizes = sorted(self.paper_sizes.keys(),
                              key=lambda s: self.paper_sizes[s]['dims'][0] * self.paper_sizes[s]['dims'][1])
        self.paper_size_combo.addItems(sorted_sizes)

        index = self.paper_size_combo.findText(current_text)
        if index != -1:
            self.paper_size_combo.setCurrentIndex(index)
        else:
            self.paper_size_combo.setCurrentText(self.settings.get("default_size", "14.8x8cm"))
        self.paper_size_combo.blockSignals(False)

    def update_theme_combo(self):
        self.theme_combo.clear()
        
        current_size = self.paper_size_combo.currentText()
        available_themes = list(self.themes.keys())

        # Special condition for "Back To School" theme
        if "Back To School" in available_themes and current_size != "6x3.5cm":
            available_themes.remove("Back To School")

        self.theme_combo.addItems(available_themes)
        
        # If the currently selected theme is not available for the new size, switch to Default
        current_theme = self.settings.get("default_theme", "Default")
        if self.theme_combo.findText(current_theme) == -1:
            self.theme_combo.setCurrentText("Default")
        else:
            self.theme_combo.setCurrentText(current_theme)

    def update_brand_combo(self):
        self.brand_combo.clear()
        self.brand_combo.addItems(list(self.brands.keys()))
        self.brand_combo.setCurrentText(self.settings.get("default_brand_theme", "None"))

    def handle_theme_selection(self, theme_name):
        if not theme_name or self.theme_combo.signalsBlocked():
            return

        # If a real theme is selected, unselect the brand
        if theme_name != "Default":
            self.brand_combo.blockSignals(True)
            self.brand_combo.setCurrentText("None")
            self.brand_combo.blockSignals(False)
        
        self.update_preview()

    def handle_brand_selection(self, brand_name):
        if not brand_name or self.brand_combo.signalsBlocked():
            return

        # If a real brand is selected, force the theme to Default
        if brand_name != "None":
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentText("Default")
            self.theme_combo.blockSignals(False)
            
        self.update_preview()

    def open_layout_settings(self):
        # Store a deep copy of the settings before opening the dialog
        original_settings = copy.deepcopy(self.settings)

        dialog = LayoutSettingsDialog(self.translator, self.settings, self)

        if dialog.exec():
            # OK was clicked, save the potentially modified settings
            self.settings["layout_settings"] = dialog.get_layout_settings()
            data_handler.save_settings(self.settings)
        else:
            # Cancel was clicked, restore the original settings
            self.settings = original_settings

        # Update the preview regardless of OK/Cancel to reflect final state
        self.update_preview()

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

    def ensure_token_valid(self):
        """
        Checks if the token needs refreshing and refreshes it if necessary.
        Returns the valid token.
        """
        # In a real app, you'd check the token's expiry time.
        # For this fix, we'll attempt a refresh before critical operations.
        refreshed_user = firebase_handler.refresh_token(self.user)
        if refreshed_user:
            self.user = refreshed_user
            self.token = self.user['idToken']
        else:
            # Handle refresh failure: force logout
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("Your session has expired. Please log in again.")
            msg.setWindowTitle("Authentication Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            self.close() # Or emit a signal to the login window to handle this
        return self.token

    def find_item(self):
        identifier = self.sku_input.text().strip()
        if not identifier: return

        # Automatically prefix with 'I' if it's a 5-digit number
        if len(identifier) == 5 and identifier.isdigit():
            identifier = f"I{identifier}"
            self.sku_input.setText(identifier) # Update the UI to reflect the change

        token = self.ensure_token_valid()
        if not token: return

        item_data = firebase_handler.find_item_by_identifier(identifier.upper(), token)
        if not item_data:
            self.clear_all_fields()
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setText(self.tr("sku_not_found_message", identifier) + "\n\n" + self.tr("register_new_item_prompt"))
            msg.setWindowTitle(self.tr("sku_not_found_title"))
            msg.addButton(QMessageBox.StandardButton.Yes)
            msg.addButton(QMessageBox.StandardButton.No)
            msg.setDefaultButton(QMessageBox.StandardButton.No)
            reply = msg.exec()
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
            token = self.ensure_token_valid()
            if not token: return
            if firebase_handler.add_new_item(new_data, token):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText(self.tr("new_item_save_success", sku))
                msg.setWindowTitle(self.tr("success_title"))
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()
                self.sku_input.setText(sku)
                self.find_item()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(self.tr("new_item_save_error"))
                msg.setWindowTitle(self.tr("new_item_validation_error"))
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()

    def populate_ui_with_item_data(self, item_data):
        self.current_item_data = item_data.copy()

        # Use the unified spec processing function
        self.current_item_data['all_specs'] = self.process_specifications(self.current_item_data)
        self.current_item_data['part_number'] = self.current_item_data.get('attributes', {}).get('Part Number', '') \
                                                or data_handler.extract_part_number(
            item_data.get('Description', ''))

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
        self.status_duration_label.setVisible(False)
        self.status_duration_label.setText("")

        if not self.current_item_data:
            self.status_label_value.setText("-")
            self.status_label_value.setStyleSheet("")
            self.toggle_status_button.setVisible(False)
            return

        sku = self.current_item_data.get('SKU')
        branch_db_key = self.get_current_branch_db_key()
        token = self.ensure_token_valid()
        if not token: return
        timestamp_str = firebase_handler.get_item_display_timestamp(sku, branch_db_key, token)

        if timestamp_str:
            self.status_label_value.setText(self.tr('status_on_display'))
            self.status_label_value.setStyleSheet("color: green; font-weight: bold;")
            self.toggle_status_button.setText(self.tr('set_to_storage_button'))

            if isinstance(timestamp_str, str):
                try:
                    tbilisi_tz = pytz.timezone('Asia/Tbilisi')
                    display_time = tbilisi_tz.localize(datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'))
                    now = datetime.now(tbilisi_tz)
                    duration = now - display_time

                    if duration.total_seconds() < 0:
                        self.status_duration_label.setVisible(False)
                    else:
                        duration_str = format_timedelta(duration, self.translator)
                        self.status_duration_label.setText(
                            f"({self.tr('status_on_display_for', duration=duration_str)})")
                        self.status_duration_label.setVisible(True)

                except (ValueError, TypeError) as e:
                    print(f"Error parsing timestamp string '{timestamp_str}': {e}")
                    self.status_duration_label.setVisible(False)
            else:
                self.status_duration_label.setVisible(False)

        else:
            self.status_label_value.setText(self.tr('status_in_storage'))
            self.status_label_value.setStyleSheet("color: red; font-weight: bold;")
            self.toggle_status_button.setText(self.tr('set_to_display_button'))
            self.status_duration_label.setVisible(False)

        self.toggle_status_button.setVisible(True)

    def toggle_display_status(self):
        if not self.current_item_data: return
        sku = self.current_item_data.get('SKU')
        branch_db_key = self.get_current_branch_db_key()
        token = self.ensure_token_valid()
        if not token: return
        is_on_display = firebase_handler.get_item_display_timestamp(sku, branch_db_key, token) is not None

        if is_on_display:
            firebase_handler.remove_item_from_display(sku, branch_db_key, token)
        else:
            firebase_handler.add_item_to_display(sku, branch_db_key, token)

        self.update_status_display()

    def generate_single(self):
        if not self.current_item_data:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.tr("no_item_message"))
            msg.setWindowTitle(self.tr("no_item_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return
        sku = self.current_item_data.get('SKU')
        self.generate_single_by_sku(sku, mark_on_display=True)

    def generate_single_by_sku(self, sku, mark_on_display=False):
        token = self.ensure_token_valid()
        if not token: return
        item_data = firebase_handler.find_item_by_identifier(sku, token)
        if not item_data:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(self.tr("sku_not_found_message", sku))
            msg.setWindowTitle(self.tr("sku_not_found_title"))
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        if self.current_item_data and self.current_item_data.get('SKU') == sku:
            data_to_print = self.get_current_data_from_ui()
        else:
            data_to_print = self._prepare_data_for_printing(item_data)

        size_name = self.paper_size_combo.currentText()
        theme_name = self.theme_combo.currentText()
        brand_name = self.brand_combo.currentText()

        if not size_name or not theme_name or not brand_name:
            return

        size_config = self.paper_sizes[size_name]
        theme_config = self.themes[theme_name]
        brand_config = self.brands[brand_name]
        
        final_theme_config = copy.deepcopy(theme_config)
        final_theme_config.update(brand_config)

        layout_settings = self.settings.get("layout_settings", data_handler.get_default_layout_settings())
        is_dual = self.dual_lang_checkbox.isChecked() and not size_config.get("is_accessory_style", False)
        is_special = self.special_tag_checkbox.isChecked()
        
        background_cache = {}

        a4_pixmaps = []
        if is_dual:
            img_en = price_generator.create_price_tag(data_to_print, size_config, final_theme_config, layout_settings, language='en', is_special=is_special, background_cache=background_cache)
            img_ka = price_generator.create_price_tag(data_to_print, size_config, final_theme_config, layout_settings, language='ka', is_special=is_special, background_cache=background_cache)
            
            a4_images = a4_layout_generator.create_a4_for_dual_single(img_en, img_ka)
            for a4_img in a4_images:
                q_image = QImage(a4_img.tobytes(), a4_img.width, a4_img.height, a4_img.width * 3, QImage.Format.Format_RGB888)
                a4_pixmaps.append(QPixmap.fromImage(q_image))
        else:
            lang = 'en' if size_config.get("is_accessory_style", False) else self.translator.language
            img = price_generator.create_price_tag(data_to_print, size_config, final_theme_config, layout_settings, language=lang, is_special=is_special, background_cache=background_cache)
            
            a4_img = a4_layout_generator.create_a4_for_single(img)
            q_image = QImage(a4_img.tobytes(), a4_img.width, a4_img.height, a4_img.width * 3, QImage.Format.Format_RGB888)
            a4_pixmaps.append(QPixmap.fromImage(q_image))

        self.handle_a4_print_with_dialog(a4_pixmaps)

        if mark_on_display:
            branch_db_key = self.get_current_branch_db_key()
            # Only update the status if it's not already set to "On Display"
            if not firebase_handler.get_item_display_timestamp(sku, branch_db_key, token):
                firebase_handler.add_item_to_display(sku, branch_db_key, token)
                firebase_handler.log_activity(token, f"User printed and marked {sku} as on display.")

        if self.current_item_data.get('SKU') == sku:
            self.update_status_display()

    def generate_batch(self, skus_to_print, use_modern_design=False):
        size_name, theme_name, brand_name = self.paper_size_combo.currentText(), self.theme_combo.currentText(), self.brand_combo.currentText()
        if not size_name or not theme_name: return

        size_config = self.paper_sizes[size_name]

        base_theme_config = self.themes[theme_name]
        if not use_modern_design:
            brand_config = self.brands.get(brand_name, {})
            base_theme_config.update(brand_config)

        layout_settings = self.settings.get("layout_settings", data_handler.get_default_layout_settings())

        layout_info = a4_layout_generator.calculate_layout(*size_config['dims'])

        tags_per_sheet = layout_info.get('total', 0)
        if tags_per_sheet <= 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("The selected paper size cannot fit any tags.")
            msg.setWindowTitle("Layout Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        token = self.ensure_token_valid()
        if not token: return
        all_items_data = firebase_handler.get_items_by_sku(skus_to_print, token)
        all_tags_images = []

        background_cache = {}
        brand_design_choices = {}

        for sku in skus_to_print:
            item_data = all_items_data.get(sku)
            if not item_data:
                print(f"Warning: SKU {sku} not found for batch print.")
                continue

            final_theme_config = copy.deepcopy(base_theme_config)

            if use_modern_design:
                item_name = item_data.get("Name", "").lower()
                detected_brand_name = None

                for b_name in self.brands_by_name.keys():
                    if b_name.lower() in item_name:
                        detected_brand_name = b_name
                        break

                if detected_brand_name:
                    chosen_brand_config = None
                    if detected_brand_name in brand_design_choices:
                        chosen_brand_key = brand_design_choices[detected_brand_name]
                        chosen_brand_config = self.brands[chosen_brand_key]
                    else:
                        brand_keys = self.brands_by_name[detected_brand_name]
                        if len(brand_keys) > 1:
                            brand_options = {key: self.brands[key] for key in brand_keys}
                            dialog = BrandSelectionDialog(self.translator, detected_brand_name, brand_options, item_data, self)
                            if dialog.exec():
                                chosen_brand_key = dialog.get_selected_brand_key()
                                if chosen_brand_key:
                                    chosen_brand_config = self.brands[chosen_brand_key]
                                    if dialog.is_choice_for_all():
                                        brand_design_choices[detected_brand_name] = chosen_brand_key
                        elif len(brand_keys) == 1:
                            chosen_brand_config = self.brands[brand_keys[0]]

                    if chosen_brand_config:
                        final_theme_config.update(chosen_brand_config)

            data_to_print = self._prepare_data_for_printing(item_data)

            if brand_name == "Epson" and not use_modern_design:
                data_to_print['all_specs'] = []

            is_dual = self.dual_lang_checkbox.isChecked() and not size_config.get("is_accessory_style", False)
            is_special = self.special_tag_checkbox.isChecked()

            if is_dual:
                img_en = price_generator.create_price_tag(data_to_print, size_config, final_theme_config, layout_settings,
                                                          language='en', is_special=is_special, background_cache=background_cache)
                img_ka = price_generator.create_price_tag(data_to_print, size_config, final_theme_config, layout_settings,
                                                          language='ka', is_special=is_special, background_cache=background_cache)
                all_tags_images.extend([img_en, img_ka])
            else:
                lang = 'en' if size_config.get("is_accessory_style", False) else self.translator.language
                img = price_generator.create_price_tag(data_to_print, size_config, final_theme_config, layout_settings,
                                                       language=lang, is_special=is_special, background_cache=background_cache)
                all_tags_images.append(img)

        if not all_tags_images:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("None of the SKUs in the queue could be found.")
            msg.setWindowTitle("No Items Found")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        a4_pages = a4_layout_generator.create_a4_layouts(all_tags_images, layout_info)

        a4_pixmaps = []
        for page in a4_pages:
            q_image = QImage(page.tobytes(), page.width, page.height, page.width * 3,
                             QImage.Format.Format_RGB888)
            a4_pixmaps.append(QPixmap.fromImage(q_image))

        if not a4_pixmaps:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Could not generate any pages to print.")
            msg.setWindowTitle("No Pages")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        if self.handle_a4_print_with_dialog(a4_pixmaps):
            branch_db_key = self.get_current_branch_db_key()
            for sku in skus_to_print:
                if not firebase_handler.get_item_display_timestamp(sku, branch_db_key, token):
                    firebase_handler.add_item_to_display(sku, branch_db_key, token)

            if self.current_item_data and self.current_item_data.get('SKU') in skus_to_print:
                self.update_status_display()

            firebase_handler.log_activity(token, f"User printed a batch of {len(skus_to_print)} items and set them to 'on display'.")

    def handle_a4_print_with_dialog(self, pixmaps):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec():
            self.printer.setResolution(price_generator.DPI)
            painter = QPainter(self.printer)
            for i, pixmap in enumerate(pixmaps):
                # Get the printable area rectangle in device pixels. This rectangle's top-left
                # (x, y) coordinate gives us the physical hardware margins of the printer.
                printable_rect_px = self.printer.pageRect(QPrinter.Unit.DevicePixel)

                # The painter's coordinate system starts at the top-left of the printable area.
                # To draw our full-page pixmap as if we're drawing on the physical paper (origin 0,0),
                # we must offset our drawing by the negative of the printable area's origin.
                # This effectively cancels out the printer's hardware margins, ensuring a true 1:1 print.
                x_offset = -printable_rect_px.x()
                y_offset = -printable_rect_px.y()

                # Draw the pixmap at the calculated offset.
                painter.drawPixmap(int(x_offset), int(y_offset), pixmap)

                if i < len(pixmaps) - 1:
                    self.printer.newPage()
            painter.end()
            return True
        return False

    def handle_batch_print_with_dialog(self, pixmap):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec():
            painter = QPainter(self.printer)
            page_rect = self.printer.pageRect(QPrinter.Unit.Point)
            target_rect = QRectF(0, 0, pixmap.width(), pixmap.height())
            target_rect.moveCenter(page_rect.center())
            painter.drawPixmap(page_rect, pixmap, QRectF(pixmap.rect()))
            painter.end()

    def get_current_data_from_ui(self):
        data = self.current_item_data.copy()
        data["Name"] = self.name_input.text()
        data["Regular price"] = self.price_input.text()
        data["Sale price"] = self.sale_price_input.text()
        data['all_specs'] = [self.specs_list.item(i).text() for i in range(self.specs_list.count()) if
                             self.specs_list.item(i).checkState() == Qt.CheckState.Checked]
        return data

    def _prepare_data_for_printing(self, item_data):
        """Prepares a clean dictionary for the price generator, including processed specs."""
        data = item_data.copy()
        data['all_specs'] = self.process_specifications(item_data)
        data['part_number'] = data.get('attributes', {}).get('Part Number', '') or data_handler.extract_part_number(
            data.get('Description', ''))
        return data

    def update_preview(self):
        if not self.current_item_data:
            self.preview_label.setText(self.tr("preview_default_text"))
            return

        data = self.get_current_data_from_ui()
        size_name = self.paper_size_combo.currentText()
        theme_name = self.theme_combo.currentText()
        brand_name = self.brand_combo.currentText()

        if not size_name or not theme_name or not brand_name:
            return

        size_config = self.paper_sizes[size_name]
        theme_config = self.themes[theme_name]
        brand_config = self.brands[brand_name]
        
        # Deep copy to avoid modifying the original theme/brand objects
        final_theme_config = copy.deepcopy(theme_config)
        # Merge brand config into theme config. Brand properties will overwrite theme properties.
        final_theme_config.update(brand_config)

        layout_settings = self.settings.get("layout_settings", data_handler.get_default_layout_settings())

        # For accessory styles, always use 'en' and don't allow dual language
        is_accessory = size_config.get("is_accessory_style", False)
        lang = 'en' if is_accessory else self.translator.language
        is_dual = self.dual_lang_checkbox.isChecked() and not is_accessory
        is_special = self.special_tag_checkbox.isChecked()
        
        background_cache = {}

        if is_dual:
            # Generate two previews side-by-side
            img_en = price_generator.create_price_tag(data, size_config, final_theme_config, layout_settings, language='en', is_special=is_special, background_cache=background_cache)
            img_ka = price_generator.create_price_tag(data, size_config, final_theme_config, layout_settings, language='ka', is_special=is_special, background_cache=background_cache)
            q_image_en = QImage(img_en.tobytes(), img_en.width, img_en.height, img_en.width * 3,
                                QImage.Format.Format_RGB888)
            q_image_ka = QImage(img_ka.tobytes(), img_ka.width, img_ka.height, img_ka.width * 3,
                                QImage.Format.Format_RGB888)
            pixmap_en = QPixmap.fromImage(q_image_en)
            pixmap_ka = QPixmap.fromImage(q_image_ka)

            # Combine pixmaps
            combined_width = pixmap_en.width() + pixmap_ka.width() + 10  # 10px spacing
            combined_height = max(pixmap_en.height(), pixmap_ka.height())
            combined_pixmap = QPixmap(combined_width, combined_height)
            combined_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(combined_pixmap)
            painter.drawPixmap(0, 0, pixmap_en)
            painter.drawPixmap(pixmap_en.width() + 10, 0, pixmap_ka)
            painter.end()
            final_pixmap = combined_pixmap
        else:
            # Generate a single preview
            img = price_generator.create_price_tag(data, size_config, final_theme_config, layout_settings, language=lang, is_special=is_special, background_cache=background_cache)
            q_image = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
            final_pixmap = QPixmap.fromImage(q_image)

        self.preview_label.setPixmap(
            final_pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation))

    def process_specifications(self, item_data):
        """
        Extracts, cleans, normalizes, and de-duplicates specifications from various sources within item_data.
        """
        all_specs = []
        # 1. From "Description" (HTML list)
        all_specs.extend(data_handler.extract_specs_from_html(item_data.get("Description", "")))
        # 2. From "attributes" dictionary
        all_specs.extend(
            data_handler.extract_specs_from_attributes(item_data.get("attributes", {}), self.column_mappings))
        # 3. From other top-level fields
        all_specs.extend(data_handler.extract_specs_from_toplevel(item_data, self.column_mappings))

        # --- De-duplication Logic ---
        
        def normalize_label(label):
            """Normalizes a spec label for accurate comparison."""
            norm = label.lower().strip()
            # Handle special cases like "Warranty" and "Warranty Details"
            if 'warranty' in norm:
                return 'warranty'
            
            # Existing logic for plurals like "Material(s)"
            norm = norm.replace('(s)', '')
            if norm.endswith('s'):
                norm = norm[:-1]
            return norm

        best_specs = {}
        for spec in all_specs:
            if ':' in spec:
                label, value = spec.split(':', 1)
                label = label.strip()
                value = value.strip()
                
                normalized_label = normalize_label(label)

                # If we haven't seen this normalized label, or the new value is longer, store it.
                if normalized_label not in best_specs or len(value) > len(best_specs[normalized_label].split(':', 1)[1].strip()):
                    best_specs[normalized_label] = f"{label}: {value}" # Store the original, un-normalized spec
            else:
                # For specs without a key-value pair, use the spec itself as the key to avoid duplicates
                if spec not in best_specs:
                    best_specs[spec] = spec

        return list(best_specs.values())

    def update_specs_list(self):
        self.specs_list.clear()
        if 'all_specs' in self.current_item_data:
            size_name = self.paper_size_combo.currentText()
            size_config = self.paper_sizes.get(size_name, {})
            is_keyboard_layout = size_config.get('design') == 'keyboard'
            spec_limit = self.paper_sizes.get(size_name, {}).get('spec_limit', 99)
            
            count = 0
            for spec in self.current_item_data['all_specs']:
                item = QListWidgetItem(spec)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

                # Special handling for Warranty: always check it if present
                if 'warranty' in spec.lower():
                    item.setCheckState(Qt.CheckState.Checked)
                # For keyboards, check all specs. Otherwise, respect the limit.
                elif is_keyboard_layout:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    if count < spec_limit:
                        item.setCheckState(Qt.CheckState.Checked)
                        count += 1
                    else:
                        item.setCheckState(Qt.CheckState.Unchecked)
                self.specs_list.addItem(item)

    def handle_paper_size_change(self):
        self.update_specs_list()
        self.update_theme_combo() # Update themes when size changes
        self.update_preview()
        size_name = self.paper_size_combo.currentText()
        if size_name:
            self.settings["default_size"] = size_name
            data_handler.save_settings(self.settings)

    def toggle_dual_language(self, state):
        self.settings["generate_dual_language"] = (state == Qt.CheckState.Checked.value)
        data_handler.save_settings(self.settings)
        self.update_preview()

    def add_spec(self):
        text, ok = QInputDialog.getText(self, self.tr("add_spec_title"), self.tr("add_spec_prompt"))
        if ok and text:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.specs_list.addItem(item)
            self.update_preview()

    def edit_spec(self):
        current_item = self.specs_list.currentItem()
        if not current_item: return
        text, ok = QInputDialog.getText(self, self.tr("edit_spec_title"), self.tr("edit_spec_prompt"),
                                        text=current_item.text())
        if ok and text:
            current_item.setText(text)
            self.update_preview()

    def remove_spec(self):
        current_item = self.specs_list.currentItem()
        if current_item:
            self.specs_list.takeItem(self.specs_list.row(current_item))
            self.update_preview()

    def select_printer(self):
        dialog = QPrintDialog(self.printer, self)
        dialog.exec()

    def handle_sku_input(self, text):
        # Any text change restarts the timer and appends to the buffer.
        self.scan_buffer += text
        self.scan_timer.start()

    def process_scan(self):
        # When the timer times out, process the buffer.
        # We check if the buffer is long enough to be a scan and not just fast typing.
        if len(self.scan_buffer) > 3:
            self.sku_input.setText(self.scan_buffer)
            self.find_item()
        self.scan_buffer = '' # Clear buffer after processing

    def handle_logout(self):
        data_handler.clear_refresh_token()
        self.close()
        QApplication.instance().exit(1)  # Signal to re-open login window
