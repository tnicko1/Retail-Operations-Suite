import csv
import os
from bs4 import BeautifulSoup

CONFIG_FILE = 'configuration.txt'
DATA_FILE = 'Items for Web Mixed.txt'

# UPDATED: Changed the dimensions and name for paper size '2'.
PAPER_SIZES = {
    '1': {'name': '10x8cm', 'dims': (10, 8), 'specs': 8},
    '2': {'name': '14.4x8cm', 'dims': (14.4, 8), 'specs': 12},
    '3': {'name': '15x10cm', 'dims': (15, 10), 'specs': 13},
    '4': {'name': '17x12cm', 'dims': (17, 12), 'specs': 11}
}


def get_config():
    """Reads saved configuration or prompts user for initial setup."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value

    if 'paper_size' not in config:
        config['paper_size'] = choose_paper_size()
        save_config(config)
    else:
        print(f"Using saved paper size: {PAPER_SIZES[config['paper_size']]['name']}")

    if 'manual_edit' not in config:
        config['manual_edit'] = choose_manual_edit_setting()
        save_config(config)
    else:
        edit_status = "Enabled" if config['manual_edit'] == 'true' else "Disabled"
        print(f"Manual spec editing is currently: {edit_status}")

    return config


def save_config(config_dict):
    """Saves the current configuration to the file."""
    with open(CONFIG_FILE, 'w') as f:
        for key, value in config_dict.items():
            f.write(f"{key}={value}\n")


def choose_paper_size():
    """Prompts the user to select a paper size."""
    print("\nPlease choose a paper size for the price tags:")
    for key, value in PAPER_SIZES.items():
        print(f"  {key}: {value['name']}")

    while True:
        choice = input("Enter your choice (1-4): ")
        if choice in PAPER_SIZES:
            print(f"Selected size: {PAPER_SIZES[choice]['name']}")
            return choice
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")


def choose_manual_edit_setting():
    """Asks the user if they want to enable manual editing by default."""
    while True:
        choice = input("Enable manual specification editing by default? (yes/no): ").lower()
        if choice in ['y', 'yes']:
            print("Manual editing enabled.")
            return 'true'
        elif choice in ['n', 'no']:
            print("Manual editing disabled.")
            return 'false'
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


def find_item_by_sku(sku):
    """Finds an item in the data file by its SKU."""
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row.get('SKU') == sku:
                    return row
    except FileNotFoundError:
        print(f"ERROR: Data file '{DATA_FILE}' not found.")
        return None
    return None


def extract_specifications(html_description):
    """Parses an HTML string to extract list items as specifications."""
    if not html_description:
        return []

    soup = BeautifulSoup(html_description, 'html.parser')
    list_items = soup.find_all('li')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in list_items]
