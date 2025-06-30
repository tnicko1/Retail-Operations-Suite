import csv
import os
import json
import re
from bs4 import BeautifulSoup
import firebase_handler

USER_SETTINGS_FILE = 'user_settings.json'
TEMPLATES_FILE = 'templates.json' # Local fallback

DEFAULT_PAPER_SIZES = {
    '6x3.5cm': {'dims': (6, 3.5), 'spec_limit': 0, 'is_accessory_style': True},
    '10x8cm': {'dims': (10, 8), 'spec_limit': 8},
    '14.4x8cm': {'dims': (14.4, 8), 'spec_limit': 12},
    '15x10cm': {'dims': (15, 10), 'spec_limit': 13},
    '17.5x12.5cm': {'dims': (17.5, 12.5), 'spec_limit': 11}
}

def extract_part_number(description):
    if not description: return ""
    match = re.search(r'\[p/n\s*([^\]]+)\]', description, re.IGNORECASE)
    return match.group(1).strip() if match else ""

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
    if not os.path.exists(USER_SETTINGS_FILE):
        settings = {
            "default_size": "14.4x8cm",
            "custom_sizes": {},
            "default_theme": "Default",
            "language": "en",
            "generate_dual_language": False,
            "default_branch": "branch_vaja",
            "low_stock_threshold": 3
        }
        save_settings(settings)
        return settings

    with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
        settings = json.load(f)
        if "language" not in settings: settings["language"] = "en"
        if "generate_dual_language" not in settings: settings["generate_dual_language"] = False
        if "default_branch" not in settings: settings["default_branch"] = "branch_vaja"
        if "low_stock_threshold" not in settings: settings["low_stock_threshold"] = 3
        if "custom_sizes" not in settings: settings["custom_sizes"] = {}
        return settings


def save_settings(settings):
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
