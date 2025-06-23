import csv
import os
import json
from bs4 import BeautifulSoup

DATA_FILE = 'Items for Web Mixed.txt'
USER_SETTINGS_FILE = 'user_settings.json'

DEFAULT_PAPER_SIZES = {
    '10x8cm': {'dims': (10, 8), 'specs': 8},
    '14.4x8cm': {'dims': (14.4, 8), 'specs': 12},
    '15x10cm': {'dims': (15, 10), 'specs': 13},
    '17x12cm': {'dims': (17, 12), 'specs': 11}
}
CSV_HEADERS = None


def get_csv_headers():
    """Reads and returns the header row from the data file, caching it for efficiency."""
    global CSV_HEADERS
    if CSV_HEADERS:
        return CSV_HEADERS

    try:
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            CSV_HEADERS = next(reader)
            return CSV_HEADERS
    except (FileNotFoundError, StopIteration):
        print(f"ERROR: Could not read headers from {DATA_FILE}")
        return None


def add_new_item(item_data):
    """Appends a new item record to the data file."""
    headers = get_csv_headers()
    if not headers:
        return False

    new_row = [item_data.get(header, "") for header in headers]

    try:
        with open(DATA_FILE, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(new_row)
        return True
    except Exception as e:
        print(f"Error writing to data file: {e}")
        return False


def get_settings():
    """Loads settings from the user file, creating it with defaults if it doesn't exist."""
    if not os.path.exists(USER_SETTINGS_FILE):
        settings = {
            "default_size": "14.4x8cm",
            "custom_sizes": {},
            "default_theme": "Default",
            "language": "en"  # Added language setting
        }
        save_settings(settings)
        return settings

    with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
        settings = json.load(f)
        # Ensure language setting exists for older configs
        if "language" not in settings:
            settings["language"] = "en"
        return settings


def save_settings(settings):
    """Saves the settings dictionary to the user file."""
    with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)


def get_all_paper_sizes():
    """Returns a merged dictionary of default and custom paper sizes."""
    settings = get_settings()
    all_sizes = DEFAULT_PAPER_SIZES.copy()
    all_sizes.update(settings.get("custom_sizes", {}))
    return all_sizes


def find_item_by_sku(sku):
    """Finds an item in the data file by its SKU."""
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row.get('SKU') == sku:
                    return row
    except FileNotFoundError:
        return None
    return None


def extract_specifications(html_description):
    """Parses an HTML string to extract list items as specifications."""
    if not html_description:
        return []

    soup = BeautifulSoup(html_description, 'html.parser')
    list_items = soup.find_all('li')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in list_items]
