import csv
import os
import json
import re
from bs4 import BeautifulSoup

DATA_FILE = 'Items for Web Mixed.txt'
USER_SETTINGS_FILE = 'user_settings.json'
DISPLAY_STATUS_FILE = 'display_status.json'
TEMPLATES_FILE = 'templates.json'

DEFAULT_PAPER_SIZES = {
    '6x3.5cm': {'dims': (6, 3.5), 'spec_limit': 0},
    '10x8cm': {'dims': (10, 8), 'spec_limit': 8},
    '14.4x8cm': {'dims': (14.4, 8), 'spec_limit': 12},
    '15x10cm': {'dims': (15, 10), 'spec_limit': 13},
    '17x12cm': {'dims': (17, 12), 'spec_limit': 11}
}
CSV_HEADERS = None


# --- Helper Functions ---
def extract_part_number(description):
    if not description: return ""
    match = re.search(r'\[p/n\s*([^\]]+)\]', description, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def get_all_items():
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8-sig') as infile:
            return list(csv.DictReader(infile))
    except FileNotFoundError:
        return []


# --- Template Management ---

def get_item_templates():
    if not os.path.exists(TEMPLATES_FILE):
        default_templates = {
            "template_blank": {"category_name": "Uncategorized", "specs": []},
            "template_laptop": {"category_name": "Laptops",
                                "specs": ["Brand", "Model", "Screen", "Processor", "Memory", "Storage", "Graphics",
                                          "Operating System", "Color", "Warranty"]},
            "template_monitor": {"category_name": "Monitors",
                                 "specs": ["Brand", "Model", "Screen Size", "Resolution", "Panel Type", "Refresh Rate",
                                           "Ports", "Warranty"]},
            "template_tv": {"category_name": "TVs",
                            "specs": ["Brand", "Model", "Screen Size", "Resolution", "Smart TV", "Ports", "Warranty"]},
            "template_phone": {"category_name": "Mobile Phones",
                               "specs": ["Brand", "Model", "Screen", "Processor", "RAM", "Storage", "Main Camera",
                                         "Front Camera", "Battery", "Color", "Warranty"]},
            "template_printer": {"category_name": "Printers",
                                 "specs": ["Brand", "Model", "Printer Type", "Print Technology", "Print Speed",
                                           "Connectivity", "Warranty"]},
            "template_ups": {"category_name": "UPS",
                             "specs": ["Brand", "Model", "Capacity (VA)", "Capacity (Watts)", "Outlets", "Warranty"]}
        }
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_templates, f, indent=4)
        return default_templates

    try:
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


# --- Display Status Management (Branch-Specific) ---

def get_display_status():
    """Loads the display status dictionary from a JSON file. Keys are branches."""
    if not os.path.exists(DISPLAY_STATUS_FILE):
        return {}
    try:
        with open(DISPLAY_STATUS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Backward compatibility: convert old list format to new dict format
            if isinstance(data, list):
                print("Old display_status format detected, converting to new format.")
                new_data = {"Stock Vaja": data, "Stock Marj": [], "Stock Gldan": []}
                save_display_status(new_data)
                return new_data
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_display_status(status_dict):
    """Saves the display status dictionary to a JSON file."""
    with open(DISPLAY_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status_dict, f, indent=4)


def add_item_to_display(sku, branch_column):
    """Adds a SKU to the on-display list for a specific branch."""
    if not sku or not branch_column: return
    status_dict = get_display_status()
    if branch_column not in status_dict:
        status_dict[branch_column] = []

    if sku not in status_dict[branch_column]:
        status_dict[branch_column].append(sku)
        save_display_status(status_dict)


def remove_item_from_display(sku, branch_column):
    """Removes a SKU from the on-display list for a specific branch."""
    if not sku or not branch_column: return
    status_dict = get_display_status()
    if branch_column in status_dict and sku in status_dict[branch_column]:
        status_dict[branch_column].remove(sku)
        save_display_status(status_dict)


def is_item_on_display(sku, branch_column):
    """Checks if a given SKU is in the on-display list for a specific branch."""
    status_dict = get_display_status()
    return sku in status_dict.get(branch_column, [])


# --- Main Data and Settings ---

def get_replacement_suggestions(category, branch_stock_column):
    if not category or not branch_stock_column:
        return []

    all_items = get_all_items()
    on_display_skus = get_display_status().get(branch_stock_column, [])
    suggestions = []

    for item in all_items:
        stock_str = item.get(branch_stock_column, '0')
        if stock_str:
            stock_value_clean = stock_str.replace(',', '')
            is_in_stock = int(stock_value_clean) > 0 if stock_value_clean.isdigit() else False
        else:
            is_in_stock = False

        if item.get('Categories') == category and item.get('SKU') not in on_display_skus and is_in_stock:
            suggestions.append(item)

    return suggestions


def get_csv_headers():
    global CSV_HEADERS
    if CSV_HEADERS: return CSV_HEADERS

    try:
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            CSV_HEADERS = next(reader)
            return CSV_HEADERS
    except (FileNotFoundError, StopIteration):
        return None


def add_new_item(item_data):
    headers = get_csv_headers()
    if not headers: return False
    new_row = [item_data.get(header, "") for header in headers]
    try:
        with open(DATA_FILE, 'a', newline='', encoding='utf-8-sig') as f:
            csv.writer(f).writerow(new_row)
        return True
    except Exception as e:
        print(f"Error writing to data file: {e}")
        return False


def get_settings():
    if not os.path.exists(USER_SETTINGS_FILE):
        settings = {
            "default_size": "14.4x8cm",
            "custom_sizes": {},
            "default_theme": "Default",
            "language": "en",
            "generate_dual_language": False,
            "default_branch": "branch_vaja"
        }
        save_settings(settings)
        return settings

    with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
        settings = json.load(f)
        if "language" not in settings: settings["language"] = "en"
        if "generate_dual_language" not in settings: settings["generate_dual_language"] = False
        if "default_branch" not in settings: settings["default_branch"] = "branch_vaja"
        return settings


def save_settings(settings):
    with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)


def get_all_paper_sizes():
    settings = get_settings()
    all_sizes = DEFAULT_PAPER_SIZES.copy()
    all_sizes.update(settings.get("custom_sizes", {}))
    return all_sizes


def find_item_by_identifier(identifier):
    if not identifier:
        return None

    all_items = get_all_items()
    if not all_items:
        return None

    for row in all_items:
        if row.get('SKU') == identifier:
            return row

    for row in all_items:
        if row.get('Attribute 4 value(s)') == identifier:
            return row

    for row in all_items:
        part_number = extract_part_number(row.get('Description', ''))
        if part_number and part_number.upper() == identifier.upper():
            return row

    return None


def extract_specifications(html_description):
    if not html_description: return []
    soup = BeautifulSoup(html_description, 'html.parser')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in soup.find_all('li')]
