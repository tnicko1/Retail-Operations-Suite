# -*- coding: utf-8 -*-

TRANSLATIONS = {
    "en": {
        # UI Text
        "window_title": "Price Tag Dashboard by Nikoloz Taturashvili",
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
        "style_group": "Style",
        "paper_size_label": "Paper Size:",
        "theme_label": "Theme:",
        "dual_language_label": "Generate Georgian Tag:",
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

        # Menus
        "file_menu": "&File",
        "select_printer_menu": "&Select Printer...",
        "open_master_list_title": "Open Master Product List",
        "admin_tools_menu": "Admin Tools",
        "admin_upload_master_list": "Update Product List from File...",
        "admin_manage_users": "Manage Users...",
        "admin_dashboard": "Dashboard",
        "admin_activity_log": "User Activity Log",
        "admin_template_manager": "Category & Template Manager",

        # Admin Dashboard
        "dashboard_title": "Admin Dashboard",
        "dashboard_refresh_button": "Refresh Data",
        "dashboard_stats_group": "Branch Statistics",
        "dashboard_on_display_label": "Items on Display:",
        "dashboard_stock_levels_group": "Stock Levels",
        "dashboard_low_stock_label": "Items with Low Stock (<= {}):",

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

        # New Item & Template Dialogs
        "new_item_dialog_title": "Register New Item",
        "new_item_sku_label": "SKU:",
        "new_item_name_label": "Item Name:",
        "new_item_price_label": "Regular Price:",
        "new_item_sale_price_label": "Sale Price (optional):",
        "new_item_specs_label": "Specifications:",
        "new_item_specs_placeholder": "Enter one specification per line.\nExample:\nScreen: 15.6 inch\nCPU: Intel Core i5",
        "new_item_save_button": "Save Item",
        "new_item_validation_error": "Validation Error",
        "new_item_name_empty_error": "Item Name cannot be empty.",
        "template_selection_title": "Select a Template",
        "template_selection_label": "Choose a template for the new item:",
        "template_validation_error_title": "No Template Selected",
        "template_validation_error_message": "Please select a template from the list.",
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

        # Spec Labels
        "spec_labels": {
            "SKU": "SKU", "Screen": "Screen", "Processor": "Processor", "Memory": "Memory", "Storage": "Storage",
            "Graphics": "Graphics", "Ports": "Ports", "Connectivity": "Connectivity",
            "Operating System": "Operating System",
            "Battery": "Battery", "Weight": "Weight", "Color": "Color", "Warranty": "Warranty", "Brand": "Brand",
            "Model": "Model", "Display": "Display", "Design": "Design", "Camera": "Camera", "CPU Cooler": "CPU Cooler",
            "Motherboard": "Motherboard", "RAM": "RAM", "Case": "Case", "Power Supply": "Power Supply",
            "Graphics Card": "Graphics Card", "Printer Type": "Printer Type", "Print Technology": "Print Technology",
            "Print Speed": "Print Speed", "Print Speed (ISO)": "Print Speed (ISO)",
            "Print Resolution": "Print Resolution",
            "Scan Type": "Scan Type", "Optical Scan Resolution": "Optical Scan Resolution",
            "Mobile Printing": "Mobile Printing",
            "Monthly Duty Cycle": "Monthly Duty Cycle", "Supported OS": "Supported OS",
            "Included Accessories": "Included Accessories",
            "Audio": "Audio", "Keyboard": "Keyboard", "Mouse": "Mouse"
        }
    },
    "ka": {
        # UI Text
        "window_title": "ფასმაჩვენებლის დაფა - ნიკოლოზ ტატურაშვილი",
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
        "style_group": "სტილი",
        "paper_size_label": "ქაღალდის ზომა:",
        "theme_label": "თემა:",
        "dual_language_label": "ინგლისური ვერსიის დამატება:",
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

        # Menus
        "file_menu": "&ფაილი",
        "select_printer_menu": "&პრინტერის არჩევა...",
        "open_master_list_title": "პროდუქტების სიის გახსნა",
        "admin_tools_menu": "ადმინის ხელსაწყოები",
        "admin_upload_master_list": "პროდუქტების სიის განახლება...",
        "admin_manage_users": "მომხმარებლების მართვა...",
        "admin_dashboard": "დაფა",
        "admin_activity_log": "მომხმარებელთა აქტივობა",
        "admin_template_manager": "კატეგორიების მართვა",

        # Admin Dashboard
        "dashboard_title": "ადმინისტრატორის დაფა",
        "dashboard_refresh_button": "განახლება",
        "dashboard_stats_group": "ფილიალების სტატისტიკა",
        "dashboard_on_display_label": "ვიტრინაშია:",
        "dashboard_stock_levels_group": "მარაგების მდგომარეობა",
        "dashboard_low_stock_label": "პროდუქცია მცირე მარაგით (<= {}):",

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
        "new_item_price_label": "სტანდარტული ფასი:",
        "new_item_sale_price_label": "ფასდაკლებული ფასი:",
        "new_item_specs_label": "მონაცემები:",
        "new_item_specs_placeholder": "შეიყვანეთ თითო მონაცემი ახალ ხაზზე.\nმაგალითად:\nეკრანი: 15.6 ინჩი\nპროცესორი: Intel Core i5",
        "new_item_save_button": "პროდუქტის შენახვა",
        "new_item_validation_error": "შეცდომა",
        "new_item_name_empty_error": "პროდუქტის სახელი ცარიელია.",
        "template_selection_title": "აირჩიეთ შაბლონი",
        "template_selection_label": "აირჩიეთ შაბლონი ახალი პროდუქტისთვის:",
        "template_validation_error_title": "შაბლონი არ არის არჩეული",
        "template_validation_error_message": "გთხოვთ, აირჩიოთ შაბლონი სიიდან.",
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

        # Spec Labels
        "spec_labels": {
            "SKU": "კოდი", "Screen": "ეკრანი", "Processor": "პროცესორი", "Memory": "ოპერატიული",
            "Storage": "შიდა მეხსიერება", "Graphics": "გრაფიკა", "Ports": "პორტები", "Connectivity": "კავშირი",
            "Operating System": "ოპერაციული სისტემა", "Battery": "ბატარეა", "Weight": "წონა", "Color": "ფერი",
            "Warranty": "გარანტია", "Brand": "ბრენდი", "Model": "მოდელი", "Display": "ეკრანი", "Design": "დიზაინი",
            "Camera": "კამერა", "CPU Cooler": "გაგრილება", "Motherboard": "დედაპლატა", "RAM": "ოპერატიული",
            "Case": "ქეისი", "Power Supply": "კვების ბლოკი", "Graphics Card": "ვიდეობარათი",
            "Printer Type": "პრინტერის ტიპი", "Print Technology": "ბეჭდვის ტექნოლოგია",
            "Print Speed": "ბეჭდვის სიჩქარე",
            "Print Speed (ISO)": "ბეჭდვის სიჩქარე (ISO)", "Print Resolution": "ბეჭდვის რეზოლუცია",
            "Scan Type": "სკანერის ტიპი",
            "Optical Scan Resolution": "ოპტიკური რეზოლუცია", "Mobile Printing": "მობილური ბეჭდვა",
            "Monthly Duty Cycle": "თვიური დატვირთვა", "Supported OS": "თავსებადი OS",
            "Included Accessories": "კომპლექტაცია",
            "Audio": "აუდიო", "Keyboard": "კლავიატურა", "Mouse": "მაუსი"
        }
    }
}


class Translator:
    def __init__(self, language="en"):
        self.language = language

    def set_language(self, language):
        self.language = language

    def get(self, key, *args):
        try:
            translation = TRANSLATIONS[self.language][key]
            return translation.format(*args)
        except (KeyError, IndexError):
            try:
                translation = TRANSLATIONS["en"][key]
                return translation.format(*args)
            except (KeyError, IndexError):
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
            for key_en, value_en in TRANSLATIONS["en"]["spec_labels"].items():
                if value_en.lower() == label.lower():
                    return TRANSLATIONS[target_lang]["spec_labels"][key_en]
            return label
        except KeyError:
            return label
