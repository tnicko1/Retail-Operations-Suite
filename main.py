import os
import data_handler
import price_generator
import a4_layout_generator

OUTPUT_DIR = 'output'


def ensure_dirs():
    """Ensure the required directories exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists('fonts'):
        os.makedirs('fonts')
        print("Created 'fonts' directory. Please add your .ttf font file there.")


def manual_spec_editor(specs):
    """Allows the user to add or remove specifications from a list."""
    while True:
        print("\n--- Current Specifications ---")
        if not specs:
            print("  (No specifications yet)")
        for i, spec in enumerate(specs):
            print(f"  {i + 1}: {spec}")

        action = input("\nType 'add', 'remove', or 'done' to continue: ").lower()

        if action == 'add':
            new_spec = input("Enter a new specification (or type 'done'): ")
            if new_spec.lower() != 'done':
                specs.append(new_spec)
        elif action == 'remove':
            try:
                idx_to_remove = input("Enter the number of the spec to remove (or type 'done'): ")
                if idx_to_remove.lower() != 'done':
                    specs.pop(int(idx_to_remove) - 1)
            except (ValueError, IndexError):
                print("Invalid number.")
        elif action == 'done':
            break
    return specs


def get_item_details_with_specs(size_config, manual_edit_enabled):
    """Prompts for SKU and returns the full item data with processed specs."""
    while True:
        sku = input("Enter item SKU: ").strip()
        item_data = data_handler.find_item_by_sku(sku)
        if item_data:
            specs = data_handler.extract_specifications(item_data.get('Description'))
            warranty_info = item_data.get('Attribute 3 value(s)')
            if warranty_info and warranty_info != '-':
                specs.append(f"Warranty: {warranty_info}")

            if manual_edit_enabled:
                if input("Manually edit specs for this item? (yes/no): ").lower() in ['y', 'yes']:
                    specs = manual_spec_editor(specs)

            max_specs = size_config['specs']
            if len(specs) > max_specs:
                print(f"Warning: Item has {len(specs)} specs, truncating to {max_specs}.")
                specs = specs[:max_specs]
            elif len(specs) < max_specs:
                if input("Keep empty bullet points? (yes/no): ").lower() not in ['n', 'no']:
                    specs.extend([''] * (max_specs - len(specs)))

            item_data['specs'] = specs
            return item_data
        else:
            print("SKU not found. Please try again.")


def settings_menu(current_config):
    """Displays the settings menu and handles changes."""
    while True:
        print("\n--- Settings ---")
        edit_status = "Enabled" if current_config.get('manual_edit') == 'true' else "Disabled"
        print(f"1. Change Paper Size (Current: {data_handler.PAPER_SIZES[current_config['paper_size']]['name']})")
        print(f"2. Toggle Manual Spec Editor (Current: {edit_status})")
        print("3. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            current_config['paper_size'] = data_handler.choose_paper_size()
            data_handler.save_config(current_config)
        elif choice == '2':
            current_config['manual_edit'] = 'false' if current_config.get('manual_edit') == 'true' else 'true'
            new_status = "Enabled" if current_config.get('manual_edit') == 'true' else "Disabled"
            print(f"Manual spec editing is now {new_status}.")
            data_handler.save_config(current_config)
        elif choice == '3':
            break
        else:
            print("Invalid choice.")
    return current_config


def main():
    """Main function to run the price tag generator application."""
    print("\n--- Made by Nikoloz Taturashvili ---")
    ensure_dirs()
    config = data_handler.get_config()

    while True:
        size_config = data_handler.PAPER_SIZES[config['paper_size']]
        manual_edit_on = config.get('manual_edit') == 'true'

        print("\n--- Main Menu ---")
        print("1. Generate a single price tag")
        print("2. Generate a full A4 sheet of price tags")
        print("3. Settings")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            item_data = get_item_details_with_specs(size_config, manual_edit_on)
            tag_image = price_generator.create_price_tag(item_data, size_config)
            filename = os.path.join(OUTPUT_DIR, f"{item_data['SKU']}_{size_config['name']}.png")
            tag_image.save(filename, dpi=(price_generator.DPI, price_generator.DPI))
            print(f"\nSuccessfully saved single tag to: {filename}")
            tag_image.show()

        elif choice == '2':
            layout = a4_layout_generator.calculate_layout(*size_config['dims'])
            print(f"\nAn A4 sheet can fit {layout['total']} tags of size {size_config['name']}.")

            tag_images = []
            for i in range(layout['total']):
                print(f"\n--- Entering details for Tag #{i + 1} ---")
                item_data = get_item_details_with_specs(size_config, manual_edit_on)
                tag_image = price_generator.create_price_tag(item_data, size_config)
                tag_images.append(tag_image)

            a4_sheet = a4_layout_generator.create_a4_sheet(tag_images, layout)
            filename = os.path.join(OUTPUT_DIR, f"A4_Sheet_{size_config['name']}.png")
            a4_sheet.save(filename, dpi=(a4_layout_generator.DPI, a4_layout_generator.DPI))
            print(f"\nSuccessfully saved A4 sheet to: {filename}")
            a4_sheet.show()

        elif choice == '3':
            config = settings_menu(config)

        elif choice == '4':
            break

        else:
            print("Invalid choice, please try again.")


if __name__ == '__main__':
    main()
