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
        "find_item_group": "1. Find Item by SKU / Barcode / P/N",
        "sku_placeholder": "Enter SKU, Barcode, or P/N and press Enter...",
        "find_button": "Find",
        "item_details_group": "Item Details",
        "name_label": "Name:",
        "price_label": "Price:",
        "sale_price_label": "Sale Price:",
        "style_group": "2. Select Style",
        "paper_size_label": "Paper Size:",
        "theme_label": "Theme:",
        "dual_language_label": "Generate Georgian Tag:",
        "specs_group": "3. Edit Specifications",
        "add_button": "Add",
        "edit_button": "Edit",
        "remove_button": "Remove",
        "output_group": "4. Output & Display Management",
        "display_manager_button": "Display Manager...",
        "generate_single_button": "Generate Single Tag (on A4)",
        "generate_batch_button": "Generate Full A4 Batch",
        "preview_default_text": "Enter an SKU, Barcode, or P/N to see a preview.",
        "sku_not_found_title": "Not Found",
        "sku_not_found_message": "Item with ID '{}' was not found in the database.",
        "register_new_item_prompt": "Would you like to register it as a new item?",
        "cannot_register_barcode_error": "Cannot register a new item using a barcode. Please use a new, unique SKU.",
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

        # Menus
        "file_menu": "&File",
        "select_printer_menu": "&Select Printer...",
        "open_master_list_title": "Open Master Product List",
        "admin_tools_menu": "Admin Tools",
        "admin_upload_master_list": "Update Product List from File...",
        "admin_manage_users": "Manage Users...",

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

        # Batch Dialog
        "batch_dialog_title": "Generate A4 Batch",
        "batch_list_label_unlimited": "Items to add (Count: {})",
        "batch_add_sku_button": "Add Item",
        "batch_remove_button": "Remove Selected",
        "batch_generate_button": "Generate",
        "batch_duplicate_title": "Duplicate",
        "batch_duplicate_message": "Item with SKU '{}' is already in the list.",
        "batch_limit_title": "Limit Reached",
        "batch_limit_message": "The maximum of {} items for this paper size has been reached.",
        "batch_empty_title": "Empty List",
        "batch_empty_message": "No items were added to the batch.",

        # Display Manager Dialog
        "display_manager_title": "Display Manager",
        "return_tag_group": "Return Tag to Find Replacement",
        "return_tag_label": "Returned Item SKU/Barcode:",
        "return_tag_placeholder": "Scan barcode or enter SKU of returned tag",
        "find_replacements_button": "Find Replacements",
        "suggestions_group": "Replacements for {} (In Stock, Not on Display)",
        "suggestions_header_sku": "SKU",
        "suggestions_header_name": "Name",
        "suggestions_header_stock": "Stock",
        "suggestions_header_price": "Price",
        "suggestions_header_action": "Action",
        "quick_print_button": "Quick Print",

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
        "find_item_group": "1. ძებნა (კოდით / შტრიხკოდით / P/N)",
        "sku_placeholder": "შეიყვანეთ კოდი, შტრიხკოდი, ან P/N...",
        "find_button": "ძებნა",
        "item_details_group": "პროდუქტის მონაცემები",
        "name_label": "დასახელება:",
        "price_label": "ფასი:",
        "sale_price_label": "ფასდაკლება:",
        "style_group": "2. სტილის არჩევა",
        "paper_size_label": "ქაღალდის ზომა:",
        "theme_label": "თემა:",
        "dual_language_label": "ინგლისური ვერსიის დამატება:",
        "specs_group": "3. მონაცემების რედაქტირება",
        "add_button": "დამატება",
        "edit_button": "შეცვლა",
        "remove_button": "წაშლა",
        "output_group": "4. გენერირება და ვიტრინის მართვა",
        "display_manager_button": "ვიტრინის მენეჯერი...",
        "generate_single_button": "1 ფასმაჩვენებელი (A4-ზე)",
        "generate_batch_button": "სრული A4 გვერდი",
        "preview_default_text": "შეიყვანეთ კოდი, შტრიხკოდი, ან P/N, რომ ნახოთ.",
        "sku_not_found_title": "ვერ მოიძებნა",
        "sku_not_found_message": "პროდუქტი ID-ით '{}' ვერ მოიძებნა.",
        "register_new_item_prompt": "გსურთ ახალი პროდუქტის დამატება?",
        "cannot_register_barcode_error": "შტრიხკოდით ახალი ნივთის რეგისტრაცია შეუძლებელია.",
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

        # Menus
        "file_menu": "&ფაილი",
        "select_printer_menu": "&პრინტერის არჩევა...",
        "open_master_list_title": "პროდუქტების სიის გახსნა",
        "admin_tools_menu": "ადმინის ხელსაწყოები",
        "admin_upload_master_list": "პროდუქტების სიის განახლება...",
        "admin_manage_users": "მომხმარებლების მართვა...",

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

        # Batch Dialog
        "batch_dialog_title": "A4 გვერდის გენერირება",
        "batch_list_label_unlimited": "დამატებული კოდები (რაოდენობა: {})",
        "batch_add_sku_button": "დამატება",
        "batch_remove_button": "მონიშნულის წაშლა",
        "batch_generate_button": "გენერირება",
        "batch_duplicate_title": "დუბლიკატი",
        "batch_duplicate_message": "პროდუქტი კოდით '{}' უკვე სიაშია.",
        "batch_limit_title": "ლიმიტი მიღწეულია",
        "batch_limit_message": "ამ ზომის ქაღალდზე ეტევა მაქსიმუმ {} ცალი.",
        "batch_empty_title": "სია ცარიელია",
        "batch_empty_message": "სიაში პროდუქტები არ არის.",

        # Display Manager Dialog
        "display_manager_title": "ვიტრინის მენეჯერი",
        "return_tag_group": "ფასმაჩვენებლის დაბრუნება და შემცვლელის მოძებნა",
        "return_tag_label": "დაბრუნებული ნივთის კოდი/შტრიხკოდი:",
        "return_tag_placeholder": "შეიყვანეთ დაბრუნებული ნივთის კოდი",
        "find_replacements_button": "შემცვლელის მოძებნა",
        "suggestions_group": "შემცვლელები {}სთვის (მარაგშია, არაა ვიტრინაში)",
        "suggestions_header_sku": "კოდი",
        "suggestions_header_name": "დასახელება",
        "suggestions_header_stock": "მარაგი",
        "suggestions_header_price": "ფასი",
        "suggestions_header_action": "მოქმედება",
        "quick_print_button": "სწრაფი ბეჭდვა",

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
