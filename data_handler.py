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


def get_settings():
    """Loads settings from the user file, creating it with defaults if it doesn't exist."""
    if not os.path.exists(USER_SETTINGS_FILE):
        settings = {
            "default_size": "14.4x8cm",
            "custom_sizes": {},
            "default_theme": "Default"
        }
        save_settings(settings)
        return settings

    with open(USER_SETTINGS_FILE, 'r') as f:
        return json.load(f)


def save_settings(settings):
    """Saves the settings dictionary to the user file."""
    with open(USER_SETTINGS_FILE, 'w') as f:
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

