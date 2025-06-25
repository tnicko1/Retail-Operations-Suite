import json
import pyrebase
import os
import csv
from bs4 import BeautifulSoup
import re

firebase_app = None
auth = None
db = None


def initialize_firebase():
    global firebase_app, auth, db
    try:
        with open('config.json', 'r') as f:
            firebase_config = json.load(f)

        firebase_app = pyrebase.initialize_app(firebase_config)
        auth = firebase_app.auth()
        db = firebase_app.database()
        return True
    except FileNotFoundError:
        print("ERROR: config.json not found.")
        return False
    except Exception as e:
        print(f"ERROR: Failed to initialize Firebase: {e}")
        return False


def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_profile = db.child("users").child(user['localId']).get().val()
        if user_profile:
            user['role'] = user_profile.get('role', 'User')
        else:
            user['role'] = 'User'
        return user
    except Exception as e:
        print(f"Login error: {e}")
        return None


def is_first_user():
    users = db.child("users").get().val()
    return not users


def register_user(email, password, is_first):
    user = auth.create_user_with_email_and_password(email, password)
    if user:
        role = "Admin" if is_first else "User"
        user_data = {
            "email": email,
            "role": role
        }
        db.child("users").child(user['localId']).set(user_data)
        return user
    return None


def get_all_users():
    users_data = db.child("users").get().val()
    if not users_data:
        return []

    user_list = []
    for uid, data in users_data.items():
        user_list.append({
            "uid": uid,
            "email": data.get("email"),
            "role": data.get("role")
        })
    return user_list


def promote_user_to_admin(uid):
    db.child("users").child(uid).update({"role": "Admin"})


def sync_products_from_file(filepath):
    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            updates = {}
            for row in reader:
                sku = row.get("SKU")
                if sku:
                    updates[f"items/{sku}"] = row

            db.update(updates)
            return True, f"Successfully synced {len(updates)} items."
    except FileNotFoundError:
        return False, "File not found."
    except Exception as e:
        return False, f"An error occurred: {e}"


def add_new_item(item_data):
    """Adds a single new item to the database."""
    sku = item_data.get("SKU")
    if not sku:
        return False
    try:
        db.child("items").child(sku).set(item_data)
        return True
    except Exception as e:
        print(f"Error adding new item to Firebase: {e}")
        return False


def get_all_items():
    all_items = db.child("items").get().val()
    return list(all_items.values()) if all_items else []


def find_item_by_identifier(identifier):
    if not identifier: return None

    all_items_dict = db.child("items").get().val()
    if not all_items_dict: return None

    # 1. Search by SKU
    if identifier in all_items_dict:
        return all_items_dict[identifier]

    # 2. Search by Barcode and Part Number
    for sku, item_data in all_items_dict.items():
        if item_data.get('Attribute 4 value(s)') == identifier:
            return item_data
        part_number = extract_part_number(item_data.get('Description', ''))
        if part_number and part_number.upper() == identifier.upper():
            return item_data

    return None


def get_replacement_suggestions(category, branch_stock_column):
    all_items = get_all_items()
    if not all_items: return []

    status_dict = get_display_status()
    on_display_skus = status_dict.get(branch_stock_column, [])
    suggestions = []

    for item in all_items:
        stock_str = item.get(branch_stock_column, '0')
        is_in_stock = False
        if stock_str:
            stock_value_clean = str(stock_str).replace(',', '')
            is_in_stock = int(stock_value_clean) > 0 if stock_value_clean.isdigit() else False

        if item.get('Categories') == category and item.get('SKU') not in on_display_skus and is_in_stock:
            suggestions.append(item)

    return suggestions


# --- Display Status ---
def get_display_status():
    status = db.child("displayStatus").get().val()
    return status if status else {}


def save_display_status(status_dict):
    db.child("displayStatus").set(status_dict)


def add_item_to_display(sku, branch_column):
    if not sku or not branch_column: return
    status_dict = get_display_status()
    if branch_column not in status_dict:
        status_dict[branch_column] = []

    if sku not in status_dict[branch_column]:
        status_dict[branch_column].append(sku)
        save_display_status(status_dict)


def remove_item_from_display(sku, branch_column):
    if not sku or not branch_column: return
    status_dict = get_display_status()
    if branch_column in status_dict and sku in status_dict[branch_column]:
        status_dict[branch_column].remove(sku)
        save_display_status(status_dict)


def is_item_on_display(sku, branch_column):
    status_dict = get_display_status()
    return sku in status_dict.get(branch_column, [])


# --- Other Helpers ---
def extract_part_number(description):
    if not description: return ""
    match = re.search(r'\[p/n\s*([^\]]+)\]', description, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def extract_specifications(html_description):
    if not html_description: return []
    soup = BeautifulSoup(html_description, 'html.parser')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in soup.find_all('li')]
