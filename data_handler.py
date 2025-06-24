import csv
import os
import json
from bs4 import BeautifulSoup

DATA_FILE = 'Items for Web Mixed.txt'
USER_SETTINGS_FILE = 'user_settings.json'

DEFAULT_PAPER_SIZES = {
    '6x3.5cm': {'dims': (6, 3.5), 'specs': 0},
    '10x8cm': {'dims': (10, 8), 'specs': 8},
    '14.4x8cm': {'dims': (14.4, 8), 'specs': 12},
    '15x10cm': {'dims': (15, 10), 'specs': 13},
    '17x12cm': {'dims': (17, 12), 'specs': 11}
}
CSV_HEADERS = None


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
            "generate_dual_language": False
        }
        save_settings(settings)
        return settings

    with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
        settings = json.load(f)
        if "language" not in settings: settings["language"] = "en"
        if "generate_dual_language" not in settings: settings["generate_dual_language"] = False
        return settings


def save_settings(settings):
    with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)


def get_all_paper_sizes():
    settings = get_settings()
    all_sizes = DEFAULT_PAPER_SIZES.copy()
    all_sizes.update(settings.get("custom_sizes", {}))
    return all_sizes


def find_item_by_sku(sku):
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row.get('SKU') == sku:
                    return row
    except FileNotFoundError:
        return None
    return None


def find_item_by_sku_or_barcode(identifier):
    """
    Finds an item by SKU first, then by barcode if no SKU match is found.
    The barcode is assumed to be in the 'Attribute 4 value(s)' column.
    """
    if not identifier:
        return None
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            # Load data into a list to search multiple times without re-reading file
            data = list(reader)
    except FileNotFoundError:
        return None

    # First, search by SKU (primary identifier)
    for row in data:
        if row.get('SKU') == identifier:
            return row

    # If not found by SKU, search by Barcode
    for row in data:
        if row.get('Attribute 4 value(s)') == identifier:
            return row

    return None  # Not found by either


def extract_specifications(html_description):
    if not html_description: return []
    soup = BeautifulSoup(html_description, 'html.parser')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in soup.find_all('li')]
