# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import csv
import os
import json
import re
from bs4 import BeautifulSoup
import firebase_handler


def _get_user_data_dir():
    """
    Gets the path to a user-writable directory for application data.
    Creates the directory if it doesn't exist.
    """
    # APPDATA is the standard environment variable for this on Windows.
    # os.path.expanduser('~') is a fallback for other systems.
    base_path = os.getenv('APPDATA') or os.path.expanduser('~')

    # We create a dedicated folder for our application to keep things tidy.
    app_dir = os.path.join(base_path, "RetailOperationsSuite")

    # The exist_ok=True argument prevents an error if the directory already exists.
    os.makedirs(app_dir, exist_ok=True)

    return app_dir


# Define the path for the user settings file in the user-writable directory.
USER_SETTINGS_FILE = os.path.join(_get_user_data_dir(), 'user_settings.json')

# This file is a fallback and is read-only, so it can stay relative.
# cx_Freeze will bundle it alongside the executable.
TEMPLATES_FILE = 'templates.json'

DEFAULT_PAPER_SIZES = {
    '6x3.5cm': {'dims': (6, 3.5), 'spec_limit': 0, 'is_accessory_style': True},
    '10x8cm': {'dims': (10, 8), 'spec_limit': 8},
    '14.8x8cm': {'dims': (14.8, 8), 'spec_limit': 12},
    '15x10cm': {'dims': (15, 10), 'spec_limit': 13},
    '17x5.7cm Keyboard': {'dims': (17, 5.7), 'spec_limit': 4, 'design': 'keyboard'},
    '17.5x12.5cm': {'dims': (17.5, 12.5), 'spec_limit': 11}
}

def get_default_layout_settings():
    return {
        "logo_scale": 1.0,
        "title_scale": 1.0,
        "spec_scale": 1.0,
        "price_scale": 1.0,
        "sku_scale": 1.0,
        "pn_scale": 1.0,
    }

def get_default_settings():
    return {
        "default_size": "14.8x8cm",
        "custom_sizes": {},
        "default_theme": "Default",
        "language": "en",
        "generate_dual_language": False,
        "default_branch": "branch_vaja",
        "low_stock_threshold": 3,
        "layout_settings": get_default_layout_settings(),
        "recent_items": [],
        "recent_items_max_size": 10
    }





def extract_part_number(description):
    if not description: return ""
    match = re.search(r'\[p/n\s*([^\]]+)\]', description, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def sanitize_for_indexing(text):
    """
    Sanitizes a string to be safely used for Firebase indexing by removing
    problematic characters.
    """
    if not text:
        return ""
    text = text.strip()
    # Replace common separators and problematic characters with an underscore
    s = re.sub(r'[ >/\\.]', '_', text)
    # Remove any characters that are not alphanumeric or underscore
    s = re.sub(r'[^a-zA-Z0-9_]', '', s)
    # Replace multiple underscores with a single one
    s = re.sub(r'__+', '_', s)
    return s


# --- Template Management ---
def get_item_templates(token=None):
    """
    Fetches templates from Firebase first. If unavailable or empty,
    falls back to the local JSON file.
    """
    # 1. Try to get from Firebase
    if token:
        firebase_templates = firebase_handler.get_templates_from_firebase(token)
        if firebase_templates:
            return firebase_templates

    # 2. Fallback to local file
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
        # Note: We don't write the fallback templates to the AppData folder,
        # as it's just a read-only default. It should be bundled with the app.
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_templates, f, indent=4)
        return default_templates

    try:
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


# --- Main Data and Settings ---
def get_settings():
    # This function now reads from the user's AppData directory.
    if not os.path.exists(USER_SETTINGS_FILE):
        settings = get_default_settings()
        save_settings(settings)
        return settings

    try:
        with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            # Ensure all keys exist to prevent errors on older settings files
            defaults = get_default_settings()
            for key, value in defaults.items():
                if key not in settings:
                    settings[key] = value
            return settings
    except (json.JSONDecodeError, FileNotFoundError):
        # If the file is corrupted or missing, create a default one.
        settings = get_default_settings()
        save_settings(settings)
        return settings


def save_settings(settings):
    # This function now saves to the user's AppData directory.
    with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)


def get_all_paper_sizes():
    settings = get_settings()
    all_sizes = DEFAULT_PAPER_SIZES.copy()
    all_sizes.update(settings.get("custom_sizes", {}))
    return all_sizes


def extract_specs_from_description(html_description):
    """
    Parses an HTML string (specifically <li> elements) and returns a dictionary
    of key-value pairs.
    """
    if not html_description: return {}
    soup = BeautifulSoup(html_description, 'html.parser')
    specs = {}
    for li in soup.find_all('li'):
        text = li.get_text(strip=True)
        if ':' in text:
            key, value = text.split(':', 1)
            specs[key.strip()] = value.strip()
    return specs


def extract_specifications(html_description):
    if not html_description: return []
    soup = BeautifulSoup(html_description, 'html.parser')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in soup.find_all('li')]


def extract_specs_from_html(html_content):
    """Extracts specifications from an HTML string, returning a list of strings."""
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    specs = []
    # These prefixes will be ignored, case-insensitively with leading space removal.
    ignore_prefixes = ("brand:", "model:")
    for li in soup.find_all('li'):
        spec_text = li.get_text(strip=True)
        if not spec_text.lower().lstrip().startswith(ignore_prefixes):
            specs.append(spec_text)
    return specs


def _natural_sort_key(s):
    """A key for natural sorting of strings like 'c1', 'c10', 'c2'."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]


def extract_specs_from_attributes(attributes, column_mappings):
    """
    Extracts specifications from the 'attributes' dictionary, applying display names,
    ignoring rules from mappings, and pairing 'c' columns correctly.
    """
    if not attributes or not isinstance(attributes, dict):
        return []
    
    specs = []
    
    # Sort keys naturally to ensure c1, c2, c10 order
    sorted_keys = sorted(attributes.keys(), key=_natural_sort_key)
    
    ignore_spec_keys = {"Brand", "Model"}

    # --- Process paired 'c' columns first ---
    processed_c_keys = set()
    # Iterate through the sorted keys to find 'c' columns that are attribute names
    for i in range(len(sorted_keys)):
        key_col = sorted_keys[i]
        
        # Skip if already processed or not a 'c' column for a label
        if key_col in processed_c_keys or not key_col.startswith('c'):
            continue
            
        # Find the corresponding value column, which should be the next 'c' column
        try:
            num = int(key_col[1:])
            if num % 2 != 1: # We only start with odd numbers (c1, c3, etc.)
                continue
                
            value_col_name = f'c{num + 1}'
            if value_col_name in attributes:
                spec_key = attributes.get(key_col)
                spec_value = attributes.get(value_col_name)

                if spec_key and spec_value and spec_key not in ignore_spec_keys:  # Both key and value must exist
                    specs.append(f"{spec_key}: {spec_value}")
                
                processed_c_keys.add(key_col)
                processed_c_keys.add(value_col_name)
        except (ValueError, IndexError):
            # Not a 'c' column or something is wrong, skip
            continue

    # --- Process other attributes that are not part of the 'c' pairs ---
    for key in sorted_keys:
        if key in processed_c_keys:
            continue # Skip 'c' columns that we've already paired

        value = attributes[key]
        if not value:  # Skip empty values
            continue
            
        mapping = column_mappings.get(key, {})
        if mapping.get('ignore', False):
            continue
            
        display_name = mapping.get('displayName', '').strip() or key
        if display_name not in ignore_spec_keys:
            specs.append(f"{display_name}: {value}")
        
    return specs


def extract_specs_from_toplevel(item_data, column_mappings):
    """
    Extracts specifications from top-level fields in the item data,
    skipping known non-spec fields and all 'c' columns (which are handled elsewhere).
    """
    specs = []
    known_non_spec_keys = {
        'SKU', 'Name', 'Regular price', 'Sale price', 'Description',
        'Categories', 'attributes', 'all_specs', 'part_number',
        'Tags', 'Type', 'On sale?', 'In stock?', 'Short description', 'category_sanitized',
        'Brand', 'Model'
    }

    # Process all other top-level fields that are not known non-spec fields,
    # not stock fields, and not 'c' columns.
    other_keys = [
        k for k in item_data 
        if k not in known_non_spec_keys 
        and not k.startswith("Stock") 
        and not (k.startswith('c') and k[1:].isdigit())
    ]

    for key in other_keys:
        value = item_data[key]
        if not value or isinstance(value, (dict, list)):
            continue

        mapping = column_mappings.get(key, {})
        if mapping.get('ignore', False):
            continue
        display_name = mapping.get('displayName', '').strip() or key
        specs.append(f"{display_name}: {value}")

    return specs