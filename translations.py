# -*- coding: utf-8 -*-

TRANSLATIONS = {
    "en": {
        # UI Text
        "window_title": "Price Tag Dashboard by Nikoloz Taturashvili",
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
        "output_group": "4. Generate Output",
        "generate_single_button": "Generate Single Tag (on A4)",
        "generate_batch_button": "Generate Full A4 Batch",
        "preview_default_text": "Enter an SKU or Barcode to see a preview.",
        "sku_not_found_title": "Not Found",
        "sku_not_found_message": "SKU '{}' was not found in the data file.",
        "register_new_item_prompt": "\n\nWould you like to register it as a new item?",
        "remove_spec_title": "Remove",
        "remove_spec_message": "Are you sure you want to remove '{}'?",
        "no_item_title": "No Item",
        "no_item_message": "Please find an item first.",
        "success_title": "Success",
        "file_saved_message": "File saved to:\n{}",
        "batch_dialog_title": "Generate A4 Batch",
        "batch_list_label": "SKUs to add (max {} for this paper size):",
        "batch_add_sku_button": "Add SKU",
        "batch_remove_button": "Remove Selected",
        "batch_generate_button": "Generate",
        "batch_duplicate_title": "Duplicate",
        "batch_duplicate_message": "SKU '{}' is already in the list.",
        "batch_limit_title": "Limit Reached",
        "batch_limit_message": "The maximum of {} items for this paper size has been reached.",
        "batch_empty_title": "Empty List",
        "batch_empty_message": "No SKUs were added to the batch.",
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
        "new_item_save_success": "Item '{}' has been saved.",
        "new_item_save_error": "Could not save the new item to the data file.",
        "cannot_register_barcode_error": "Cannot register a new item using a barcode. Please use a new, unique SKU.",


        # Spec Labels (for translation on the tag itself)
        # UPDATED: Added all new labels from the image.
        "spec_labels": {
            "SKU": "SKU",
            "Screen": "Screen",
            "Processor": "Processor",
            "Memory": "Memory",
            "Storage": "Storage",
            "Graphics": "Graphics",
            "Ports": "Ports",
            "Connectivity": "Connectivity",
            "Operating System": "Operating System",
            "Battery": "Battery",
            "Weight": "Weight",
            "Color": "Color",
            "Warranty": "Warranty",
            "Brand": "Brand",
            "Model": "Model",
            "Display": "Display",
            "Design": "Design",
            "Camera": "Camera",
            "CPU Cooler": "CPU Cooler",
            "Motherboard": "Motherboard",
            "RAM": "RAM",
            "Case": "Case",
            "Power Supply": "Power Supply",
            "Graphics Card": "Graphics Card",
            "Printer Type": "Printer Type",
            "Print Technology": "Print Technology",
            "Print Speed": "Print Speed",
            "Print Speed (ISO)": "Print Speed (ISO)",
            "Print Resolution": "Print Resolution",
            "Scan Type": "Scan Type",
            "Optical Scan Resolution": "Optical Scan Resolution",
            "Mobile Printing": "Mobile Printing",
            "Monthly Duty Cycle": "Monthly Duty Cycle",
            "Supported OS": "Supported OS",
            "Included Accessories": "Included Accessories",
            "Audio": "Audio",
            "Keyboard": "Keyboard",
            "Mouse": "Mouse"
        }
    },
    "ka": {
        # UI Text
        "window_title": "ფასმაჩვენებლის დაფა - ავტორი: ნიკოლოზ ტატურაშვილი",
        "find_item_group": "1. პროდუქტის მოძებნა (კოდით / შტრიხკოდით)",
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
        "output_group": "4. გენერირება",
        "generate_single_button": "1 ფასმაჩვენებელი (A4-ზე)",
        "generate_batch_button": "სრული A4 გვერდი",
        "preview_default_text": "შეიყვანეთ კოდი ან შტრიხკოდი, რომ ნახოთ.",
        "sku_not_found_title": "ვერ მოიძებნა",
        "sku_not_found_message": "კოდი '{}' ვერ მოიძებნა.",
        "register_new_item_prompt": "\n\nგსურთ ახალი პროდუქტის დამატება?",
        "remove_spec_title": "წაშლა",
        "remove_spec_message": "დარწმუნებული ხართ, რომ გსურთ წაშალოთ '{}'?",
        "no_item_title": "არჩეული არ არის",
        "no_item_message": "გთხოვთ, მოძებნოთ პროდუქტი.",
        "success_title": "წარმატება",
        "file_saved_message": "ფაილი შენახულია:\n{}",
        "batch_dialog_title": "A4 გვერდის გენერირება",
        "batch_list_label": "დასამატებელი კოდები (მაქსიმუმ {} ამ ზომაზე):",
        "batch_add_sku_button": "კოდის დამატება",
        "batch_remove_button": "მონიშნულის წაშლა",
        "batch_generate_button": "გენერირება",
        "batch_duplicate_title": "დუბლიკატი",
        "batch_duplicate_message": "კოდი '{}' უკვე სიაშია.",
        "batch_limit_title": "ლიმიტი მიღწეულია",
        "batch_limit_message": "ამ ზომის ქაღალდზე ეტევა მაქსიმუმ {} ცალი.",
        "batch_empty_title": "სია ცარიელია",
        "batch_empty_message": "სიაში პროდუქტები არ არის.",
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
        "new_item_save_success": "პროდუქტი '{}' შენახულია.",
        "new_item_save_error": "პროდუქტის შენახვა ვერ მოხერხდა.",
        "cannot_register_barcode_error": "შტრიხკოდით ახალი ნივთის რეგისტრაცია შეუძლებელია. გთხოვთ გამოიყენოთ ახალი, უნიკალური კოდი.",

        # Spec Labels (for translation on the tag itself)
        # UPDATED: Added Georgian translations for all new labels.
        "spec_labels": {
            "SKU": "კოდი",
            "Screen": "ეკრანი",
            "Processor": "პროცესორი",
            "Memory": "ოპერატიული მეხსიერება",
            "Storage": "შიდა მეხსიერება",
            "Graphics": "გრაფიკა",
            "Ports": "პორტები",
            "Connectivity": "კავშირი",
            "Operating System": "ოპერაციული სისტემა",
            "Battery": "ბატარეა",
            "Weight": "წონა",
            "Color": "ფერი",
            "Warranty": "გარანტია",
            "Brand": "ბრენდი",
            "Model": "მოდელი",
            "Display": "ეკრანი",
            "Design": "დიზაინი",
            "Camera": "კამერა",
            "CPU Cooler": "გაგრილების სისტემა",
            "Motherboard": "დედაპლატა",
            "RAM": "ოპერატიული მეხსიერება",
            "Case": "ქეისი",
            "Power Supply": "დენის წყარო",
            "Graphics Card": "ვიდეობარათი",
            "Printer Type": "პრინტერის ტიპი",
            "Print Technology": "ბეჭდვის ტექნოლოგია",
            "Print Speed": "ბეჭდვის სიჩქარე",
            "Print Speed (ISO)": "ბეჭდვის სიჩქარე (ISO)",
            "Print Resolution": "ბეჭდვის რეზოლუცია",
            "Scan Type": "სკანერის ტიპი",
            "Optical Scan Resolution": "ოპტიკური სკანირების რეზოლუცია",
            "Mobile Printing": "მობილური ბეჭდვა",
            "Monthly Duty Cycle": "ყოველთვიური დატვირთვა",
            "Supported OS": "თავსებადი ოპერაციული სისტემები",
            "Included Accessories": "კომპლექტაცია",
            "Audio": "აუდიო",
            "Keyboard": "კლავიატურა",
            "Mouse": "მაუსი"
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

    def get_spec_label(self, label, target_lang):
        """Translates a specification label into the target language."""
        try:
            # Find which English key matches the label
            for key_en, value_en in TRANSLATIONS["en"]["spec_labels"].items():
                if value_en.lower() == label.lower():
                    # Return the translation for that key in the target language
                    return TRANSLATIONS[target_lang]["spec_labels"][key_en]
            return label  # Return original if no match found
        except KeyError:
            return label  # Fallback to original label
