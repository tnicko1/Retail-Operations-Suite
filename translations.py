# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

TRANSLATIONS = {
    "en": {
        # UI Text
        "window_title": "Retail Operations Suite by Nikoloz Taturashvili",
        "generator_tab_title": "Price Tag Generator",
        "branch_group_title": "Store Branch",
        "branch_label": "Current Branch:",
        "branch_vaja": "Vazha-Pshavela Shop",
        "branch_marj": "Marjanishvili",
        "branch_gldani": "Gldani Shop",
        "find_item_group": "Find Item by SKU / Barcode / P/N",
        "sku_placeholder": "Enter SKU, Barcode, or P/N and press Enter...",
        "find_button": "Find",
        "item_details_group": "Item Details",
        "name_label": "Name:",
        "price_label": "Price:",
        "sale_price_label": "Sale Price:",
        "style_group": "Style & Layout",
        "paper_size_label": "Paper Size:",
        "theme_label": "Theme:",
        "brand_label": "Brand:",
        "dual_language_label": "Generate Georgian Tag:",
        "special_tag_label": "Generate Special Tag:",
        "layout_settings_button": "Layout Settings...",
        "specs_group": "Specifications",
        "add_button": "Add",
        "edit_button": "Edit",
        "remove_button": "Remove",
        "output_group": "Output & Display Management",
        "display_manager_button": "Display Manager...",
        "generate_single_button": "Generate Single Tag (on A4)",
        "generate_batch_button": "Print Queue...",
        "preview_default_text": "Enter an SKU, Barcode, or P/N to see a preview.",
        "sku_not_found_title": "Not Found",
        "sku_not_found_message": "Item with ID '{}' was not found in the database.",
        "register_new_item_prompt": "Would you like to register it as a new item?",
        "remove_spec_title": "Remove",
        "remove_spec_message": "Are you sure you want to remove '{}'?",
        "no_item_title": "No Item",
        "no_item_message": "Please find an item first.",
        "success_title": "Success",
        "file_saved_message": "File saved to:\n{}",
        "status_label": "Status",
        "status_on_display": "On Display",
        "status_in_storage": "In Storage",
        "status_on_display_for": "On display for {duration}",
        "duration_days": "{d} days",
        "duration_hours": "{h} hours",
        "duration_minutes": "{m} minutes",
        "duration_less_than_minute": "less than a minute",
        "set_to_display_button": "Set to Display",
        "set_to_storage_button": "Set to Storage",
        "item_returned_message": "Item {} marked as 'In Storage'.",
        "new_item_save_success": "Item '{}' has been saved.",
        "new_item_save_error": "Could not save the new item to the database.",
        "print_job_sent": "Sent {0} page(s) to printer: {1}",
        "sync_results_message": "Sync complete.\nUpdated/Added: {0} items.\nRemoved: {1} obsolete items.",
        "add_to_queue_button": "Add to Queue",
        "price_history_button": "Price History...",
        "price_history_title": "Price History for SKU: {}",
        "price_history_header_date": "Date",
        "price_history_header_old": "Old Price",
        "price_history_header_new": "New Price",
        "low_stock_warning": "Low Stock!",
        "stock_label": "Stock:",

        # Layout Settings Dialog
        "layout_settings_title": "Layout Settings",
        "layout_logo_size": "Logo Size:",
        "layout_title_size": "Title Font Size:",
        "layout_spec_size": "Spec Font Size:",
        "layout_price_size": "Price Font Size:",
        "layout_sku_size": "SKU Font Size:",
        "layout_pn_size": "P/N Font Size:",
        "layout_reset_button": "Reset to Defaults",

        # Auth
        "login_window_title": "Login - Retail Operations Suite",
        "login_identifier_label": "Email or Username:",
        "login_password_label": "Password:",
        "login_button": "Login",
        "register_button": "Register New Account",
        
        "register_window_title": "Register New Account",
        "register_username_label": "Username:",
        "register_email_label": "Email:",
        "register_password_label": "Password:",
        "register_confirm_password_label": "Confirm Password:",

        # Quick Stock Checker
        "stock_checker_title": "Quick Stock Checker",
        "stock_checker_button": "Check Stock",
        "stock_checker_branch_header": "Branch",
        "stock_checker_stock_header": "Stock",
        "stock_checker_menu": "Quick Stock Checker...",
        "suggestions_stock_branch_header": "Stock Branch",
        "suggestions_current_branch_header": "Current Branch",
        "suggestions_stock_header": "Stock",

        # Display Manager
        "display_manager_title": "Display Manager",
        "find_by_category_group": "Find Available Items by Category",
        "find_available_button": "Find Available",
        "category_label": "Category:",
        "all_categories_placeholder": "Select a category...",
        "available_for_display_group_title": "Available for Display in '{}' ({})",
        "return_tag_group": "Return Item & Find Replacements",
        "return_tag_label": "Item to Return:",
        "return_tag_placeholder": "Enter SKU/Barcode of item being returned...",
        "find_replacements_button": "Find Replacements",
        "suggestions_group_empty": "Replacement Suggestions",
        "suggestions_group_filled": "Suggestions for '{}' in {} branch",
        "suggestions_header_sku": "SKU",
        "suggestions_header_name": "Name",
        "suggestions_header_stock": "Stock",
        "suggestions_header_price": "Price",
        "suggestions_header_action": "Action",
        "quick_print_button": "Print & Display",

        # Menus
        "file_menu": "&File",
        "select_printer_menu": "&Select Printer...",
        "logout_menu": "Sign Out",
        "open_master_list_title": "Open Master Product List",
        "admin_tools_menu": "Admin Tools",
        "admin_upload_master_list": "Update Product List from File...",
        "admin_manage_users": "Manage Users...",
        "admin_dashboard": "Dashboard",
        "admin_activity_log": "User Activity Log",
        "admin_template_manager": "Category & Template Manager",
        "size_manager_menu": "Manage Custom Sizes...",

        # Custom Size Manager
        "size_manager_title": "Custom Print Size Manager",
        "size_dialog_add_title": "Add Custom Size",
        "size_dialog_edit_title": "Edit Custom Size",
        "size_dialog_name": "Size Name:",
        "size_dialog_width": "Width:",
        "size_dialog_height": "Height:",
        "size_dialog_spec_limit": "Spec Limit:",
        "size_dialog_accessory_style": "Accessory price design:",
        "remove_size_title": "Remove Custom Size",
        "remove_size_message": "Are you sure you want to remove the custom size '{}'?",


        # Admin Dashboard
        "dashboard_title": "Admin Dashboard",
        "dashboard_refresh_button": "Refresh Data",
        "dashboard_stats_group": "Branch Statistics",
        "dashboard_on_display_label": "Items on Display:",
        "dashboard_stock_levels_group": "Stock Levels",
        "dashboard_low_stock_label": "Items with Low Stock (<= {}):",
        "dashboard_filter_branch": "Filter by Branch:",
        "dashboard_filter_category": "Filter by Category:",
        "dashboard_all_categories": "All Categories",
        "dashboard_header_sku": "SKU",
        "dashboard_header_name": "Name",
        "dashboard_header_category": "Category",
        "dashboard_header_stock": "Stock",


        # Activity Log
        "activity_log_title": "User Activity Log",
        "activity_log_header_time": "Timestamp",
        "activity_log_header_email": "User",
        "activity_log_header_action": "Action",

        # Template Manager
        "template_manager_title": "Category & Template Manager",
        "template_manager_categories_group": "Product Categories",
        "template_manager_specs_group": "Specifications for {}",
        "template_manager_add_cat_button": "Add Category",
        "template_manager_rename_cat_button": "Rename",
        "template_manager_delete_cat_button": "Delete",
        "template_manager_add_spec_button": "Add Spec",
        "template_manager_remove_spec_button": "Remove Spec",
        "template_manager_save_button": "Save to Cloud",
        "template_manager_new_cat_prompt": "Enter new category name:",
        "template_manager_new_spec_prompt": "Enter new specification name:",
        "template_manager_rename_prompt": "Enter new name for '{}':",
        "template_manager_delete_cat_confirm_title": "Delete Category",
        "template_manager_delete_cat_confirm_msg": "Are you sure you want to delete the category '{}' and all its spec templates?",
        "templates_saved_success": "Templates have been successfully saved to the cloud.",
        "templates_saved_fail": "Failed to save templates to the cloud.",

        # User Management
        "user_mgmt_header_email": "Email",
        "user_mgmt_header_role": "Role",
        "user_mgmt_header_action": "Action",
        "user_mgmt_promote_button": "Promote to Admin",
        "user_mgmt_confirm_promote_title": "Confirm Promotion",
        "user_mgmt_confirm_promote_message": "Are you sure you want to promote {} to an Admin?",

        # Column Mapping Manager
        "column_mapping_menu": "Column Mapping Manager",
        "column_mapping_title": "Column Mapping Manager",
        "column_mapping_info": "Define how to display columns from your master file on the price tag.",
        "column_mapping_refresh_button": "Refresh Columns from Database",
        "column_mapping_header_original": "Original Column Name",
        "column_mapping_header_display": "Display Name (on Tag)",
        "column_mapping_header_ignore": "Ignore Column",
        "column_mapping_save_success": "Column mappings saved successfully.",
        "column_mapping_save_error": "Failed to save column mappings.",

        # New Item & Template Dialogs
        "new_item_dialog_title": "Register New Item",
        "new_item_sku_label": "SKU:",
        "new_item_name_label": "Item Name:",
        "part_number_label": "Part Number:",
        "new_item_price_label": "Regular Price:",
        "new_item_sale_price_label": "Sale Price (optional):",
        "new_item_specs_label": "Specifications:",
        "new_item_specs_placeholder": "Enter one specification per line.\nExample:\nScreen Size: 15.6 inch\nCPU: Intel Core i5",
        "new_item_save_button": "Save Item",
        "new_item_validation_error": "Validation Error",
        "new_item_name_empty_error": "Item Name cannot be empty.",
        "template_selection_title": "Select a Template",
        "template_selection_label": "Choose a template for the new item:",
        "template_validation_error_title": "No Template Selected",
        "template_validation_error_message": "Please select a template from the list.",
        "category_selection_error_message": "Please select a specific category to search.",
        "template_blank": "Blank Template",
        "template_laptop": "Laptop",
        "template_monitor": "Monitor",
        "template_tv": "TV",
        "template_phone": "Mobile Phone",
        "template_printer": "Printer",
        "template_ups": "UPS",

        # Batch Dialog / Print Queue
        "print_queue_title": "Print Queue",
        "print_queue_add_item_group": "Add Item to Queue by ID",
        "print_queue_add_button": "Add",
        "print_queue_skus_group": "Items to Print",
        "print_queue_load_save_group": "Saved Lists",
        "print_queue_load_button": "Load...",
        "print_queue_save_button": "Save As...",
        "print_queue_delete_button": "Delete",
        "print_queue_clear_button": "Clear Queue",
        "print_queue_remove_button": "Remove Selected",
        "print_queue_generate_button": "Generate & Print All",
        "print_queue_load_prompt_title": "Load Batch List",
        "print_queue_load_prompt_label": "Select a list to load:",
        "print_queue_save_prompt": "Enter a name for this batch list:",
        "print_queue_delete_confirm": "Are you sure you want to delete the saved list '{}'?",

        # Brand Selection Dialog
        "brand_selection_title": "Choose Design for {brand_name}",
        "brand_selection_prompt": "Multiple designs are available for {brand_name}. Please select one.",
        "brand_selection_choose_all": "Use this design for all subsequent '{brand_name}' items in this batch",

        # Spec Labels
        "spec_labels": {
            # --- General Identifiers ---
            "SKU": "SKU",
            "Barcode": "Barcode",
            "PartNumber": "Part Number",
            "Brand": "Brand",
            "Model": "Model",

            # --- Core Components (CPU, Motherboard) ---
            "Processor": "Processor",
            "CPU": "CPU",
            "Chipset": "Chipset",
            "Socket": "Socket",
            "NumberOfCores": "Number of Cores",
            "CPUFrequency": "CPU Frequency",
            "TurboFrequency": "Turbo Frequency",
            "Threads": "Threads",
            "Motherboard": "Motherboard",
            "CPUCooler": "CPU Cooler",

            # --- Memory (RAM & Storage) ---
            "Memory": "Memory",
            "RAM": "RAM",
            "MemoryType": "Memory Type",
            "MemorySpeed": "Memory Speed",
            "MaxMemory": "Max Memory",
            "Storage": "Storage",
            "SSD_Capacity": "SSD Capacity",
            "HDD_Capacity": "HDD Capacity",
            "MemoryCardSupport": "Memory Card Support",
            "OpticalDrive": "Optical Drive",

            # --- Graphics & Display ---
            "Graphics": "Graphics",
            "GraphicsCard": "Graphics Card",
            "GPU_Model": "GPU Model",
            "VRAM": "VRAM",
            "Screen": "Screen",
            "Display": "Display",
            "ScreenSize": "Screen Size",
            "Resolution": "Resolution",
            "RefreshRate": "Refresh Rate",
            "PanelType": "Panel Type",
            "Matrix": "Matrix",
            "AspectRatio": "Aspect Ratio",
            "ResponseTime": "Response Time",
            "Brightness": "Brightness",
            "ContrastRatio": "Contrast Ratio",
            "ViewingAngle": "Viewing Angle",
            "ColorGamut": "Color Gamut",
            "TearingPreventionTechnology": "Tearing Prevention Technology",

            # --- Connectivity & Ports ---
            "Connectivity": "Connectivity",
            "Network": "Network",
            "Interface": "Interface",
            "Ports": "Ports",
            "USB_Ports": "USB Ports",
            "HDMI_Ports": "HDMI Ports",
            "DisplayPort": "DisplayPort",
            "AudioJack": "Audio Jack",
            "WiFi": "Wi-Fi",
            "Bluetooth": "Bluetooth",
            "Ethernet": "Ethernet",
            "NFC": "NFC",

            # --- Physical Attributes ---
            "Design": "Design",
            "Color": "Color",
            "Weight": "Weight",
            "NetWeight": "Net Weight",
            "GrossWeight": "Gross Weight",
            "Dimensions": "Dimensions",
            "Length": "Length",
            "Width": "Width",
            "Height": "Height",
            "FormFactor": "Form Factor",
            "Case": "Case",
            "BuildMaterial": "Build Material",
            "IP_Rating": "IP Rating",

            # --- Laptop Misc ---
            "Keyboard Backlight": "Keyboard Backlight",
            "Keyboard Layout": "Keyboard Layout",
            "Material(s)": "Material(s)",
            "Material": "Material",

            # --- Power ---
            "PowerSupply": "Power Supply",
            "Wattage": "Wattage",
            "Efficiency": "Efficiency",
            "Modular": "Modular",
            "Battery": "Battery",
            "Capacity": "Capacity",
            "InputVoltage": "Input Voltage",
            "OutputVoltage": "Output Voltage",

            # --- UPS Specific ---
            "Topology": "Topology",
            "WaveformType": "Waveform Type",
            "OutputFrequency": "Output Frequency",
            "OutputConnectionCount": "Output Connection Count",
            "OutputConnectionType": "Output Connection Type",
            "InputConnectionType": "Input Connection Type",
            "InputVoltageRange": "Input Voltage Range",
            "InputFrequency": "Input Frequency",

            # --- UPS Specific 2 ---
            "BatteryType": "Battery Type",
            "NumberOfBatteries": "Number of Batteries",
            "TypicalRechargeTime": "Typical Recharge Time",
            "NoiseLevel": "Noise Level",
            "Noise": "Noise",
            "Rackmount": "Rackmount",
            "OutputWaveform": "Output Waveform",
            "UPSCapacity": "UPS Capacity",

            # --- Input, Output & Multimedia ---
            "Audio": "Audio",
            "Speakers": "Speakers",
            "Microphone": "Microphone",
            "Keyboard": "Keyboard",
            "Mouse": "Mouse",
            "Camera": "Camera",
            "MainCamera": "Main Camera",
            "FrontCamera": "Front Camera",
            "Webcam": "Webcam",
            "FingerprintSensor": "Fingerprint Sensor",
            "FaceRecognition": "Face Recognition",

            # --- Device & OS Specific ---
            "OperatingSystem": "Operating System",
            "SupportedOS": "Supported OS",
            "SIM_Support": "SIM Support",
            "SmartFeatures": "Smart Features",
            "Tuner": "Tuner",

            # --- Printer/Scanner Specific ---
            "PrinterType": "Printer Type",
            "Functions": "Functions",
            "PrintTechnology": "Print Technology",
            "PrintSpeed": "Print Speed",
            "PrintSpeed_ISO": "Print Speed (ISO)",
            "PrintResolution": "Print Resolution",
            "ScanType": "Scan Type",
            "OpticalScanResolution": "Optical Scan Resolution",
            "MobilePrinting": "Mobile Printing",
            "MonthlyDutyCycle": "Monthly Duty Cycle",
            "PaperSize": "Paper Size",
            "Connector": "Connector",
            "Copy Speed": "Copy Speed",
            "Duplex Printing": "Duplex Printing",
            "Duplex Printing Speed": "Duplex Printing Speed",
            "Duplex Scanning": "Duplex Scanning",
            "Duplex Scanning Speed": "Duplex Scanning Speed",
            "Duplex": "Duplex",
            "Duplex Print Speed": "Duplex Print Speed",
            "Duplex Print": "Duplex Print",
            "Duplex Scan": "Duplex Scan",
            "Duplex Scan Speed": "Duplex Scan Speed",

            # --- Monitor Specific ---
            "Ports & Connectors": "Ports & Connectors",
            "Backlight Type": "Backlight Type",
            "VESA Mount Compatibility": "VESA Mount Compatibility",
            "VESA Mount Type": "VESA Mount Type",
            "VESA Mount Support": "VESA Mount Support",
            "Flicker-Free Technology": "Flicker-Free Technique",
            "Flicker-Free": "Flicker-Free",
            "Ultra-Narrow Bezels": "Ultra-Narrow Bezels",
            "Tearing Prevention": "Tearing Prevention",
            "Screen Resolution": "Screen Resolution",

            # --- TV Specific ---
            "HDR Compatibility": "HDR Compatibility",
            "HDR": "HDR",
            "Smart TV": "Smart TV",
            "Wireless": "Wireless",
            "Game Mode": "Game Mode",
            "APP Support": "APP Support",

            # --- Projectors ---
            "Optical Zoom": "Optical Zoom",
            "Lamp Life": "Lamp Life",
            "Built-in Speaker": "Built-in Speaker",
            "Technology": "Technology",
            "Power Consumption": "Power Consumption",
            "Mounting": "Mounting",
            "Aspect Ratio": "Aspect Ratio",
            "Form Factor": "Form Factor",

            # --- Chairs & Desks ---
            "MaximumWeight": "Maximum Weight",
            "Max Weight": "Max Weight",
            "Materials": "Materials",
            "Number of Wheels": "Number of Wheels",
            "Armrests": "Armrests",

            # --- Mobiles & Ipads ---
            "Battery Capacity": "Battery Capacity",
            "Selfie Camear": "Selfie Camera",
            "Screen Type": "Screen Type",
            "Network Technology": "Network Technology",

            # --- Miscellaneous ---
            "Warranty": "Warranty",
            "WarrantyDetails": "Warranty Details",
            "IncludedAccessories": "Included Accessories",
            "Portable Design": "Portable Design",
            "Portability": "Portability",
            "SALE": "SALE",
            "SPECIAL": "SPECIAL",
            "Year": "Year",
            "Years": "Years",
            "Material Details": "Material Details",
            "MaterialDetails": "Material Details",
        }
    },
    "ka": {
        # UI Text
        "window_title": "საცალო ოპერაციების კომპლექსი - ნიკოლოზ ტატურაშვილი",
        "generator_tab_title": "ფასმაჩვენებლის გენერატორი",
        "branch_group_title": "ფილიალი",
        "branch_label": "მიმდინარე ფილიალი:",
        "branch_vaja": "ვაჟა-ფშაველას ფილიალი",
        "branch_marj": "მარჯანიშვილი",
        "branch_gldani": "გლდანის ფილიალი",
        "find_item_group": "ძებნა (კოდით / შტრიხკოდით / P/N)",
        "sku_placeholder": "შეიყვანეთ კოდი, შტრიხკოდი, ან P/N...",
        "find_button": "ძებნა",
        "item_details_group": "პროდუქტის მონაცემები",
        "name_label": "დასახელება:",
        "price_label": "ფასი:",
        "sale_price_label": "ფასდაკლება:",
        "style_group": "სტილი და დიზაინი",
        "paper_size_label": "ქაღალდის ზომა:",
        "theme_label": "თემა:",
        "brand_label": "ბრენდი:",
        "dual_language_label": "ინგლისური ვერსიის დამატება:",
        "special_tag_label": "სპეც. ფასმაჩვენებლის გენერირება:",
        "layout_settings_button": "დიზაინის პარამეტრები...",
        "specs_group": "მონაცემები",
        "add_button": "დამატება",
        "edit_button": "შეცვლა",
        "remove_button": "წაშლა",
        "output_group": "გენერირება და ვიტრინის მართვა",
        "display_manager_button": "ვიტრინის მენეჯერი...",
        "generate_single_button": "1 ფასმაჩვენებელი (A4-ზე)",
        "generate_batch_button": "ბეჭდვის რიგი...",
        "preview_default_text": "შეიყვანეთ კოდი, შტრიხკოდი, ან P/N, რომ ნახოთ.",
        "sku_not_found_title": "ვერ მოიძებნა",
        "sku_not_found_message": "პროდუქტი ID-ით '{}' ვერ მოიძებნა.",
        "register_new_item_prompt": "გსურთ ახალი პროდუქტის დამატება?",
        "remove_spec_title": "წაშლა",
        "remove_spec_message": "დარწმუნებული ხართ, რომ გსურთ წაშალოთ '{}'?",
        "no_item_title": "არჩეული არ არის",
        "no_item_message": "გთხოვთ, მოძებნოთ პროდუქტი.",
        "success_title": "წარმატება",
        "file_saved_message": "ფაილი შენახულია:\n{}",
        "status_label": "სტატუსი",
        "status_on_display": "ვიტრინაშია",
        "status_in_storage": "საწყობშია",
        "status_on_display_for": "ვიტრინაშია {duration}",
        "duration_days": "{d} დღე",
        "duration_hours": "{h} საათი",
        "duration_minutes": "{m} წუთი",
        "duration_less_than_minute": "წუთზე ნაკლები",
        "set_to_display_button": "ვიტრინაში გადატანა",
        "set_to_storage_button": "საწყობში დაბრუნება",
        "item_returned_message": "პროდუქტი {} აღინიშნა როგორც 'საწყობშია'.",
        "new_item_save_success": "პროდუქტი '{}' შენახულია.",
        "new_item_save_error": "პროდუქტის შენახვა ვერ მოხერხდა.",
        "print_job_sent": "დაიბეჭდა {0} გვერდი პრინტერზე: {1}",
        "sync_results_message": "სინქრონიზაცია დასრულდა.\nგანახლდა/დაემატა: {0} პროდუქტი.\nწაიშალა: {1} ძველი პროდუქტი.",
        "add_to_queue_button": "რიგში დამატება",
        "price_history_button": "ფასის ისტორია...",
        "price_history_title": "ფასის ისტორია კოდისთვის: {}",
        "price_history_header_date": "თარიღი",
        "price_history_header_old": "ძველი ფასი",
        "price_history_header_new": "ახალი ფასი",
        "low_stock_warning": "მცირე მარაგი!",
        "stock_label": "მარაგი:",

        # Layout Settings Dialog
        "layout_settings_title": "დიზაინის პარამეტრები",
        "layout_logo_size": "ლოგოს ზომა:",
        "layout_title_size": "სათაურის შრიფტი:",
        "layout_spec_size": "მონაცემების შრიფტი:",
        "layout_price_size": "ფასის შრიფტი:",
        "layout_sku_size": "კოდის შრიფტი:",
        "layout_pn_size": "P/N-ის შრიფტი:",
        "layout_reset_button": "საწყისზე დაბრუნება",

        # Auth
        "login_window_title": "ავტორიზაცია - საცალო ოპერაციების კომპლექსი",
        "login_identifier_label": "მეილი ან მომხმარებლის სახელი:",
        "login_password_label": "პაროლი:",
        "login_button": "შესვლა",
        "register_button": "ახალი ანგარიშის რეგისტრაცია",
        
        "register_window_title": "ახალი ანგარიშის რეგისტრაცია",
        "register_username_label": "მომხმარებლის სახელი:",
        "register_email_label": "მეილი:",
        "register_password_label": "პაროლი:",
        "register_confirm_password_label": "გაიმეორეთ პაროლი:",

        # Quick Stock Checker
        "stock_checker_title": "მარაგის სწრაფი შემოწმება",
        "stock_checker_button": "შემოწმება",
        "stock_checker_branch_header": "ფილიალი",
        "stock_checker_stock_header": "მარაგი",
        "stock_checker_menu": "მარაგის სწრაფი შემოწმება...",
        "suggestions_stock_branch_header": "ფილიალის მარაგი",
        "suggestions_current_branch_header": "მიმდინარე ფილიალი",
        "suggestions_stock_header": "მარაგი",

        # Display Manager
        "display_manager_title": "ვიტრინის მენეჯერი",
        "find_by_category_group": "ხელმისაწვდომი პროდუქტების ძებნა კატეგორიით",
        "find_available_button": "ძებნა",
        "category_label": "კატეგორია:",
        "all_categories_placeholder": "აირჩიეთ კატეგორია...",
        "available_for_display_group_title": "ხელმისაწვდომია ვიტრინისთვის '{}'-ში ({})",
        "return_tag_group": "ნივთის დაბრუნება და ჩანაცვლება",
        "return_tag_label": "დასაბრუნებელი ნივთი:",
        "return_tag_placeholder": "შეიყვანეთ დასაბრუნებელი ნივთის კოდი/შტრიხკოდი...",
        "find_replacements_button": "ჩანაცვლების ძებნა",
        "suggestions_group_empty": "შესაძლო ჩანაცვლებები",
        "suggestions_group_filled": "ჩანაცვლება '{}'-სთვის ფილიალში: {}",
        "suggestions_header_sku": "კოდი",
        "suggestions_header_name": "დასახელება",
        "suggestions_header_stock": "მარაგი",
        "suggestions_header_price": "ფასი",
        "suggestions_header_action": "მოქმედება",
        "quick_print_button": "ბეჭდვა და ვიტრინაზე დაყენება",

        # Menus
        "file_menu": "&ფაილი",
        "select_printer_menu": "&პრინტერის არჩევა...",
        "logout_menu": "გასვლა",
        "open_master_list_title": "პროდუქტების სიის გახსნა",
        "admin_tools_menu": "ადმინის ხელსაწყოები",
        "admin_upload_master_list": "პროდუქტების სიის განახლება...",
        "admin_manage_users": "მომხმარებლების მართვა...",
        "admin_dashboard": "დაფა",
        "admin_activity_log": "მომხმარებელთა აქტივობა",
        "admin_template_manager": "კატეგორიების მართვა",
        "size_manager_menu": "ზომების მართვა...",

        # Custom Size Manager
        "size_manager_title": "საბეჭდი ზომების მართვა",
        "size_dialog_add_title": "ახალი ზომის დამატება",
        "size_dialog_edit_title": "ზომის რედაქტირება",
        "size_dialog_name": "ზომის სახელი:",
        "size_dialog_width": "სიგანე:",
        "size_dialog_height": "სიმაღლე:",
        "size_dialog_spec_limit": "მონაცემების ლიმიტი:",
        "size_dialog_accessory_style": "აქსესუარის დიზაინი:",
        "remove_size_title": "ზომის წაშლა",
        "remove_size_message": "დარწმუნებული ხართ, რომ გსურთ წაშალოთ ზომა '{}'?",

        # Admin Dashboard
        "dashboard_title": "ადმინისტრატორის დაფა",
        "dashboard_refresh_button": "განახლება",
        "dashboard_stats_group": "ფილიალების სტატისტიკა",
        "dashboard_on_display_label": "ვიტრინაშია:",
        "dashboard_stock_levels_group": "მარაგების მდგომარეობა",
        "dashboard_low_stock_label": "პროდუქცია მცირე მარაგით (<= {}):",
        "dashboard_filter_branch": "ფილიალის ფილტრი:",
        "dashboard_filter_category": "კატეგორიის ფილტრი:",
        "dashboard_all_branches": "ყველა ფილიალი",
        "dashboard_all_categories": "ყველა კატეგორია",
        "dashboard_header_sku": "კოდი",
        "dashboard_header_name": "დასახელება",
        "dashboard_header_category": "კატეგორია",
        "dashboard_header_stock": "მარაგი",

        # Activity Log
        "activity_log_title": "მომხმარებელთა აქტივობის ისტორია",
        "activity_log_header_time": "თარიღი",
        "activity_log_header_email": "მომხმარებელი",
        "activity_log_header_action": "მოქმედება",

        # Template Manager
        "template_manager_title": "კატეგორიების და შაბლონების მართვა",
        "template_manager_categories_group": "პროდუქტის კატეგორიები",
        "template_manager_specs_group": "მონაცემები კატეგორიისთვის: {}",
        "template_manager_add_cat_button": "კატეგორიის დამატება",
        "template_manager_rename_cat_button": "გადარქმევა",
        "template_manager_delete_cat_button": "წაშლა",
        "template_manager_add_spec_button": "მონაცემის დამატება",
        "template_manager_remove_spec_button": "მონაცემის წაშლა",
        "template_manager_save_button": "შენახვა ღრუბელში",
        "template_manager_new_cat_prompt": "შეიყვანეთ ახალი კატეგორიის სახელი:",
        "template_manager_new_spec_prompt": "შეიყვანეთ ახალი მონაცემის სახელი:",
        "template_manager_rename_prompt": "შეიყვანეთ ახალი სახელი '{}'-თვის:",
        "template_manager_delete_cat_confirm_title": "კატეგორიის წაშლა",
        "template_manager_delete_cat_confirm_msg": "დარწმუნებული ხართ, რომ გსურთ წაშალოთ კატეგორია '{}` და მისი ყველა მონაცემის შაბლონი?",
        "templates_saved_success": "შაბლონები წარმატებით შეინახა ღრუბლოვან საცავში.",
        "templates_saved_fail": "შაბლონების შენახვა ვერ მოხერხდა.",

        # User Management
        "user_mgmt_header_email": "მეილი",
        "user_mgmt_header_role": "როლი",
        "user_mgmt_header_action": "მოქმედება",
        "user_mgmt_promote_button": "ადმინად დაყენება",
        "user_mgmt_confirm_promote_title": "დადასტურება",
        "user_mgmt_confirm_promote_message": "დარწმუნებული ხართ, რომ გსურთ {} გახადოთ ადმინისტრატორი?",

        # New Item & Template Dialogs
        "new_item_dialog_title": "ახალი პროდუქტის რეგისტრაცია",
        "new_item_sku_label": "კოდი:",
        "new_item_name_label": "პროდუქტის სახელი:",
        "part_number_label": "მწარმოებლის ნომერი:",
        "new_item_price_label": "სტანდარტული ფასი:",
        "new_item_sale_price_label": "ფასდაკლებული ფასი:",
        "new_item_specs_label": "მონაცემები:",
        "new_item_specs_placeholder": "შეიყვანეთ თითო მონაცემი ახალ ხაზზე.\nმაგალითად:\nეკრანის ზომა: 15.6 ინჩი\nპროცესორი: Intel Core i5",
        "new_item_save_button": "პროდუქტის შენახვა",
        "new_item_validation_error": "შეცდომა",
        "new_item_name_empty_error": "პროდუქტის სახელი ცარიელია.",
        "template_selection_title": "აირჩიეთ შაბლონი",
        "template_selection_label": "აირჩიეთ შაბლონი ახალი პროდუქტისთვის:",
        "template_validation_error_title": "შაბლონი არ არის არჩეული",
        "template_validation_error_message": "გთხოვთ, აირჩიოთ შაბლონი სიიდან.",
        "category_selection_error_message": "გთხოვთ, აირჩიოთ კონკრეტული კატეგორია.",
        "template_blank": "ცარიელი შაბლონი",
        "template_laptop": "ლეპტოპი",
        "template_monitor": "მონიტორი",
        "template_tv": "ტელევიზორი",
        "template_phone": "მობილური ტელეფონი",
        "template_printer": "პრინტერი",
        "template_ups": "UPS",

        # Batch Dialog / Print Queue
        "print_queue_title": "ბეჭდვის რიგი",
        "print_queue_add_item_group": "რიგში დამატება ID-ით",
        "print_queue_add_button": "დამატება",
        "print_queue_skus_group": "დასაბეჭდი პროდუქტები",
        "print_queue_load_save_group": "შენახული სიები",
        "print_queue_load_button": "ჩატვირთვა...",
        "print_queue_save_button": "შენახვა როგორც...",
        "print_queue_delete_button": "წაშლა",
        "print_queue_clear_button": "რიგის გასუფთავება",
        "print_queue_remove_button": "მონიშნულის წაშლა",
        "print_queue_generate_button": "ყველას გენერირება და ბეჭდვა",
        "print_queue_load_prompt_title": "სიის ჩატვირთვა",
        "print_queue_load_prompt_label": "აირჩიეთ სია:",
        "print_queue_save_prompt": "შეიყვანეთ სახელი ამ სიისთვის:",
        "print_queue_delete_confirm": "დარწმუნებული ხართ რომ გსურთ წაშალოთ შენახული სია '{}'?",

        # Brand Selection Dialog
        "brand_selection_title": "აირჩიეთ დიზაინი ბრენდისთვის: {brand_name}",
        "brand_selection_prompt": "ბრენდისთვის '{brand_name}' ხელმისაწვდომია რამდენიმე დიზაინი. გთხოვთ, აირჩიოთ ერთი.",
        "brand_selection_choose_all": "ამ დიზაინის გამოყენება ამ ბრენდის ყველა შემდგომი პროდუქტისთვის",

        # Spec Labels
        "spec_labels": {
            # --- General Identifiers ---
            "SKU": "კოდი",
            "Barcode": "შტრიხკოდი",
            "PartNumber": "მწ. ნომერი",
            "Brand": "ბრენდი",
            "Model": "მოდელი",

            # --- Core Components (CPU, Motherboard) ---
            "Processor": "პროცესორი",
            "CPU": "პროცესორი",
            "Chipset": "ჩიპსეტი",
            "Socket": "სოკეტი",
            "NumberOfCores": "ბირთვების რაოდენობა",
            "CPUFrequency": "პროცესორის სიხშირე",
            "TurboFrequency": "ტურბო სიხშირე",
            "Threads": "ნაკადები",
            "Motherboard": "დედაპლატა",
            "CPUCooler": "პროცესორის გაგრილება",

            # --- Memory (RAM & Storage) ---
            "Memory": "მეხსიერება",
            "RAM": "ოპერატიული მეხსიერება",
            "MemoryType": "მეხსიერების ტიპი",
            "MemorySpeed": "მეხსიერების სიჩქარე",
            "MaxMemory": "მაქს. მეხსიერება",
            "Storage": "შიდა მეხსიერება",
            "SSD_Capacity": "SSD მოცულობა",
            "HDD_Capacity": "HDD მოცულობა",
            "MemoryCardSupport": "მეხსიერების ბარათის მხარდაჭერა",
            "OpticalDrive": "ოპტიკური დისკი",

            # --- Graphics & Display ---
            "Graphics": "გრაფიკა",
            "GraphicsCard": "ვიდეობარათი",
            "GPU_Model": "GPU-ს მოდელი",
            "VRAM": "ვიდეო მეხსიერება",
            "Screen": "ეკრანი",
            "Display": "ეკრანი",
            "ScreenSize": "ეკრანის ზომა",
            "Resolution": "რეზოლუცია",
            "RefreshRate": "განახლების სიხშირე",
            "PanelType": "პანელის ტიპი",
            "Matrix": "მატრიცა",
            "AspectRatio": "მხარეთა თანაფარდობა",
            "ResponseTime": "რეაგირების დრო",
            "Brightness": "სიკაშკაშე",
            "ContrastRatio": "კონტრასტულობა",
            "ViewingAngle": "ხედვის კუთხე",
            "ColorGamut": "ფერთა გამა",
            "TearingPreventionTechnology": "დახევის საწინააღმდეგო ტექნოლოგია",

            # --- Connectivity & Ports ---
            "Connectivity": "კავშირი",
            "Network": "ქსელი",
            "Interface": "ინტერფეისი",
            "Ports": "პორტები",
            "USB_Ports": "USB პორტები",
            "HDMI_Ports": "HDMI პორტები",
            "DisplayPort": "დისპლეიპორტი",
            "AudioJack": "აუდიო ჯეკი",
            "WiFi": "WiFi",
            "Bluetooth": "ბლუთუზი",
            "Ethernet": "ინტერნეტი",
            "NFC": "NFC",

            # --- Physical Attributes ---
            "Design": "დიზაინი",
            "Color": "ფერი",
            "Weight": "წონა",
            "NetWeight": "სუფთა წონა",
            "GrossWeight": "საერთო წონა",
            "Dimensions": "ზომები",
            "Length": "სიგრძე",
            "Width": "სიგანე",
            "Height": "სიმაღლე",
            "FormFactor": "ფორმ-ფაქტორი",
            "Case": "ქეისი",
            "BuildMaterial": "კორპუსის მასალა",
            "IP_Rating": "IP რეიტინგი",

            # --- Power ---
            "PowerSupply": "კვების ბლოკი",
            "Wattage": "სიმძლავრე (ვტ)",
            "Efficiency": "ეფექტურობა",
            "Modular": "მოდულური",
            "Battery": "ბატარეა",
            "Capacity": "ტევადობა",
            "InputVoltage": "შემავალი ძაბვა",
            "OutputVoltage": "გამომავალი ძაბვა",

            # --- Laptop Misc ---
            "Keyboard Backlight": "კლავიატურის განათება",
            "Keyboard Layout": "კლავიატურის განლაგება",
            "Material(s)": "მატერიალ(ებ)ი",
            "Material": "მატერიალი",

            # --- UPS Specific ---
            "Topology": "ტოპოლოგია",
            "WaveformType": "ტალღის ტიპი",
            "OutputFrequency": "გამომავალი სიხშირე",
            "OutputConnectionCount": "გამომავალი პორტების რაოდენობა",
            "OutputConnectionType": "გამომავალი პორტების ტიპი",
            "InputConnectionType": "შემავალი პორტის ტიპი",
            "InputVoltageRange": "შემავალი ძაბვის დიაპაზონი",
            "InputFrequency": "შემავალი სიხშირე",

            # --- UPS Specific 2 ---
            "BatteryType": "ბატარეის ტიპი",
            "NumberOfBatteries": "ბატარეების რაოდენობა",
            "TypicalRechargeTime": "დატენვის დრო",
            "NoiseLevel": "ხმაურის დონე",
            "Noise": "ხმაური",
            "Rackmount": "სერვერულ კარადაში მონტაჟი",
            "OutputWaveform": "გამომავალი ტალღის ფორმა",
            "UPSCapacity": "UPS-ის სიმძლავრე",

            # --- Input, Output & Multimedia ---
            "Audio": "აუდიო",
            "Speakers": "დინამიკები",
            "Microphone": "მიკროფონი",
            "Keyboard": "კლავიატურა",
            "Mouse": "მაუსი",
            "Camera": "კამერა",
            "MainCamera": "მთავარი კამერა",
            "FrontCamera": "წინა კამერა",
            "Webcam": "ვებკამერა",
            "FingerprintSensor": "თითის ანაბეჭდის სენსორი",
            "FaceRecognition": "სახის ამომცნობი",

            # --- Device & OS Specific ---
            "OperatingSystem": "ოპერაციული სისტემა",
            "SupportedOS": "თავსებადი OS",
            "SIM_Support": "SIM-ის მხარდაჭერა",
            "SmartFeatures": "სმარტ ფუნქციები",
            "Tuner": "ტიუნერი",

            # --- Printer/Scanner Specific ---
            "PrinterType": "პრინტერის ტიპი",
            "Functions": "ფუნქციები",
            "PrintTechnology": "ბეჭდვის ტექნოლოგია",
            "PrintSpeed": "ბეჭდვის სიჩქარე",
            "PrintSpeed_ISO": "ბეჭდვის სიჩქარე (ISO)",
            "PrintResolution": "ბეჭდვის რეზოლუცია",
            "ScanType": "სკანერის ტიპი",
            "OpticalScanResolution": "ოპტიკური რეზოლუცია",
            "MobilePrinting": "მობილური ბეჭდვა",
            "MonthlyDutyCycle": "თვიური დატვირთვა",
            "PaperSize": "ქაღალდის ზომა",
            "Connector": "კონექტორი",
            "Copy Speed": "კოპირების სიჩქარე",
            "Duplex Printing": "ორმხრივი ბეჭდვა",
            "Duplex Printing Speed": "ორმხრივი ბეჭდვის სიჩქარე",
            "Duplex Scanning": "ორმხრივი სკანირება",
            "Duplex Scanning Speed": "ორმხრივი სკანირების სიჩქარე",
            "Duplex": "ორმხრივი",
            "Duplex Print Speed": "ორმხრივი ბეჭდვის სიჩქარე",
            "Duplex Print": "ორმხრივი ბეჭდვა",
            "Duplex Scan": "ორმხრივი სკანირება",
            "Duplex Scan Speed": "ორმხრივი სკანირების სიჩქარე",

            # --- Monitor Specific ---
            "Ports & Connectors": "პორტები და კონექტორები",
            "Backlight Type": "განათების ტიპი",
            "VESA Mount Compatibility": "VESA სამაგრის თავსებადობა",
            "VESA Mount Type": "VESA სამაგრის ტიპი",
            "VESA Mount Support": "VESA სამაგრის მხარდაჭერა",
            "Flicker-Free Technology": "ციმციმის საწინააღმდეგო ტექნოლოგია",
            "Flicker-Free": "ციმციმის გარეშე",
            "Ultra-Narrow Bezels": "ულტრაწვრილი ჩარჩოები",
            "Tearing Prevention": "დახევის საწინააღმდეგო",
            "Screen Resolution": "ეკრანის რეზოლუცია",

            # --- TV Specific ---
            "HDR Compatibility": "HDR-ის თავსებადობა",
            "HDR": "HDR",
            "Smart TV": "სმარტ ტელევიზორი",
            "Wireless": "უკაბელო",
            "Game Mode": "თამაშის რეჟიმი",
            "APP Support": "აპლიკაციების მხარდაჭერა",

            # --- Projectors ---
            "Optical Zoom": "ოპტიკური ზუმი",
            "Lamp Life": "ლამპის ხანგრძლივობა",
            "Built-in Speaker": "ჩაშენებული სპიკერი",
            "Technology": "ტექნოლოგია",
            "Power Consumption": "ენერგიის მოხმარება",
            "Mounting": "მონტაჟი",
            "Aspect Ratio": "მხარეთა თანაფარდობა",
            "Form Factor": "ფორმ-ფაქტორი",

            # --- Chairs & Desks ---
            "MaximumWeight": "მაქსიმუმი წონა",
            "Max Weight": "მაქსიმუმი წონა",
            "Materials": "მატერიალები",
            "Number of Wheels": "ბორბლების რაოდენობა",
            "Armrests": "სახელური",

            # --- Mobiles & Ipads ---
            "Battery Capacity": "ბატარიის მოცულობა",
            "Selfie Camear": "სელფის კამერა",
            "Screen Type": "ეკრანის ტიპი",
            "Network Technology": "ქსელური ტექნოლოგია",

            # --- Miscellaneous ---
            "Warranty": "გარანტია",
            "WarrantyDetails": "გარანტიის დეტალები",
            "IncludedAccessories": "კომპლექტაცია",
            "Portable Design": "პორტატული დიზაინი",
            "Portability": "პორტატულობა",
            "SALE": "აქცია",
            "SPECIAL": "სპეც",
            "Year": "წელი",
            "Years": "წლები",
            "Material Details": "მასალის დეტალები",
            "MaterialDetails": "მასალის დეტალები",
        }
    }
}


class Translator:
    def __init__(self, language="en"):
        self.language = language

    def set_language(self, language):
        self.language = language

    def get(self, key, *args, **kwargs):
        try:
            translation = TRANSLATIONS[self.language][key]
            return translation.format(*args, **kwargs)
        except (KeyError, IndexError):
            try:
                # Fallback to English if key not in current language
                translation = TRANSLATIONS["en"][key]
                return translation.format(*args, **kwargs)
            except (KeyError, IndexError):
                # Return the key itself if not found anywhere
                return f"<{key}>"

    def get_key_from_value(self, value_to_find):
        if not value_to_find:
            return None

        for lang_dict in TRANSLATIONS.values():
            for key, value in lang_dict.items():
                if isinstance(value, str) and value == value_to_find:
                    return key
        return None

    def get_spec_label(self, label, target_lang):
        try:
            # Find the English key for the given label
            for key_en, value_en in TRANSLATIONS["en"]["spec_labels"].items():
                if value_en.lower() == label.lower():
                    # Use the found key to get the label in the target language
                    return TRANSLATIONS[target_lang]["spec_labels"][key_en]
            # If no match found, return the original label
            return label
        except KeyError:
            # If a language or key doesn't exist, return the original label
            return label
            return label
