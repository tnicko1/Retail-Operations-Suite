import csv
import os
import json
from bs4 import BeautifulSoup

DATA_FILE = 'Items for Web Mixed.txt'
USER_SETTINGS_FILE = 'user_settings.json'
DISPLAY_STATUS_FILE = 'display_status.json'

DEFAULT_PAPER_SIZES = {
    '6x3.5cm': {'dims': (6, 3.5), 'specs': 0},
    '10x8cm': {'dims': (10, 8), 'specs': 8},
    '14.4x8cm': {'dims': (14.4, 8), 'specs': 12},
    '15x10cm': {'dims': (15, 10), 'specs': 13},
    '17x12cm': {'dims': (17, 12), 'specs': 11}
}
CSV_HEADERS = None


# --- Display Status Management ---

def get_display_status():
    """Loads the list of SKUs currently on display from a JSON file."""
    if not os.path.exists(DISPLAY_STATUS_FILE):
        return []
    try:
        with open(DISPLAY_STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_display_status(sku_list):
    """Saves the list of on-display SKUs to a JSON file."""
    with open(DISPLAY_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(set(sku_list))), f, indent=4)


def add_item_to_display(sku):
    """Adds a SKU to the on-display list."""
    if not sku: return
    on_display_skus = get_display_status()
    if sku not in on_display_skus:
        on_display_skus.append(sku)
        save_display_status(on_display_skus)


def remove_item_from_display(sku):
    """Removes a SKU from the on-display list."""
    if not sku: return
    on_display_skus = get_display_status()
    if sku in on_display_skus:
        on_display_skus.remove(sku)
        save_display_status(on_display_skus)


def is_item_on_display(sku):
    """Checks if a given SKU is in the on-display list."""
    return sku in get_display_status()


# --- Main Data and Settings ---

def get_all_items():
    """Loads all items from the CSV data file."""
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8-sig') as infile:
            return list(csv.DictReader(infile))
    except FileNotFoundError:
        return []


def get_replacement_suggestions(category, branch_stock_column):
    """
    Finds items of the same category that are in stock AT A SPECIFIC BRANCH
    and not on display.
    """
    if not category or not branch_stock_column:
        return []

    all_items = get_all_items()
    on_display_skus = get_display_status()
    suggestions = []

    for item in all_items:
        # Check stock for the specific branch
        stock_str = item.get(branch_stock_column, '0')
        if stock_str:
            stock_value_clean = stock_str.replace(',', '')
            is_in_stock = int(stock_value_clean) > 0 if stock_value_clean.isdigit() else False
        else:
            is_in_stock = False

        # Check conditions: same category, not on display, and in stock at the branch
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
    """Gets user settings, adding defaults for branch if they don't exist."""
    if not os.path.exists(USER_SETTINGS_FILE):
        settings = {
            "default_size": "14.4x8cm",
            "custom_sizes": {},
            "default_theme": "Default",
            "language": "en",
            "generate_dual_language": False,
            "default_branch": "Vaja Shop"  # Add default branch
        }
        save_settings(settings)
        return settings

    with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
        settings = json.load(f)
        if "language" not in settings: settings["language"] = "en"
        if "generate_dual_language" not in settings: settings["generate_dual_language"] = False
        if "default_branch" not in settings: settings["default_branch"] = "Vaja Shop"
        return settings


def save_settings(settings):
    with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)


def get_all_paper_sizes():
    settings = get_settings()
    all_sizes = DEFAULT_PAPER_SIZES.copy()
    all_sizes.update(settings.get("custom_sizes", {}))
    return all_sizes


def find_item_by_sku_or_barcode(identifier):
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

    return None


def extract_specifications(html_description):
    if not html_description: return []
    soup = BeautifulSoup(html_description, 'html.parser')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in soup.find_all('li')]
