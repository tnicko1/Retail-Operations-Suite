# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი). All Rights Reserved.
#
# This file is part of the Retail Operations Suite.
# This software is proprietary and confidential.
#
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.


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
    '14.4x8cm': {'dims': (14.4, 8), 'spec_limit': 12},
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
        "default_size": "14.4x8cm",
        "custom_sizes": {},
        "default_theme": "Default",
        "language": "en",
        "generate_dual_language": False,
        "default_branch": "branch_vaja",
        "low_stock_threshold": 3,
        "layout_settings": get_default_layout_settings()
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


def extract_specifications(html_description):
    if not html_description: return []
    soup = BeautifulSoup(html_description, 'html.parser')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in soup.find_all('li')]
