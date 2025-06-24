# -*- coding: utf-8 -*-

TRANSLATIONS = {
    "en": {
        # UI Text
        "window_title": "Price Tag Dashboard by Nikoloz Taturashvili",
        "branch_group_title": "Store Branch",
        "branch_label": "Current Branch:",
        "branch_vaja": "Vaja Shop",
        "branch_marj": "Marjanishvili Shop",
        "branch_gldani": "Gldani Shop",
        "find_item_group": "1. Find Item by SKU / Barcode",
        "sku_placeholder": "Enter SKU or Barcode and press Enter...",
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
        "preview_default_text": "Enter an SKU or Barcode to see a preview.",
        "sku_not_found_title": "Not Found",
        "sku_not_found_message": "Item with ID '{}' was not found in the data file.",
        "register_new_item_prompt": "\n\nWould you like to register it as a new item?",
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

        # Batch Dialog
        "batch_dialog_title": "Generate A4 Batch",
        "batch_list_label": "Items to add (max {} for this paper size):",
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
        "branch_vaja": "ვაჟას ფილიალი",
        "branch_marj": "მარჯანიშვილის ფილიალი",
        "branch_gldani": "გლდანის ფილიალი",
        "find_item_group": "1. ძებნა (კოდით / შტრიხკოდით)",
        "sku_placeholder": "შეიყვანეთ კოდი ან შტრიხკოდი...",
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
        "preview_default_text": "შეიყვანეთ კოდი ან შტრიხკოდი, რომ ნახოთ.",
        "sku_not_found_title": "ვერ მოიძებნა",
        "sku_not_found_message": "პროდუქტი ID-ით '{}' ვერ მოიძებნა.",
        "register_new_item_prompt": "\n\nგსურთ ახალი პროდუქტის დამატება?",
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

        # Batch Dialog
        "batch_dialog_title": "A4 გვერდის გენერირება",
        "batch_list_label": "დასამატებელი კოდები (მაქსიმუმ {} ამ ზომაზე):",
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
        except KeyError:
            try:
                translation = TRANSLATIONS["en"][key]
                return translation.format(*args)
            except KeyError:
                return f"<{key}>"

    def get_key_from_value(self, value_to_find):
        """Finds the base key for a given translated value."""
        if not value_to_find:
            return None

        # Search in all languages for the value to find its canonical key
        for lang_dict in TRANSLATIONS.values():
            for key, value in lang_dict.items():
                # We only care about top-level keys, not spec_labels etc.
                if isinstance(value, str) and value == value_to_find:
                    return key
        return None

    def get_spec_label(self, label, target_lang):
        """Translates a specification label into the target language."""
        try:
            for key_en, value_en in TRANSLATIONS["en"]["spec_labels"].items():
                if value_en.lower() == label.lower():
                    return TRANSLATIONS[target_lang]["spec_labels"][key_en]
            return label
        except KeyError:
            return label
