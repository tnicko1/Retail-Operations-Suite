import json
import pyrebase
import os
import csv
from bs4 import BeautifulSoup
import re

firebase_app = None
auth = None
db = None

# A simple cache for category data to reduce downloads
category_cache = {}


def initialize_firebase():
    """Initializes the Firebase app using credentials from config.json."""
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
    """
    Signs the user in and fetches their profile using their auth token.
    """
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_profile = db.child("users").child(user['localId']).get(user['idToken']).val()

        if user_profile:
            user['role'] = user_profile.get('role', 'User')
        else:
            user['role'] = 'User'
        return user
    except Exception as e:
        print(f"Login error: {e}")
        return None


def is_first_user():
    """
    Checks if any users exist. With the new rules, this will only succeed
    if the /users node does not exist, otherwise it will be denied and return False.
    """
    try:
        users = db.child("users").get().val()
        return not users
    except Exception as e:
        print(f"Info: Checking for first user received expected error: {e}")
        return False


def register_user(email, password, is_first):
    """
    Creates a user, immediately signs them in to get a token,
    and uses the token to create their database profile securely.
    """
    try:
        user_auth = auth.create_user_with_email_and_password(email, password)
        if user_auth:
            user = auth.sign_in_with_email_and_password(email, password)
            role = "Admin" if is_first else "User"
            user_data = {"email": email, "role": role}
            db.child("users").child(user['localId']).set(user_data, user['idToken'])
            user['role'] = role
            return user
    except Exception as e:
        print(f"Registration error: {e}")
    return None


def get_all_users(token):
    if not token: return []
    users_data = db.child("users").get(token).val()
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


def promote_user_to_admin(uid, admin_token):
    if not admin_token: return
    db.child("users").child(uid).update({"role": "Admin"}, admin_token)


def sync_products_from_file(filepath, admin_token):
    if not admin_token:
        return False, "Authentication token is missing. Cannot sync.", 0
    try:
        file_skus = set()
        file_items = {}
        with open(filepath, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                sku = row.get("SKU")
                if sku:
                    file_skus.add(sku)
                    file_items[sku] = row

        firebase_items = db.child("items").get(admin_token).val()
        firebase_skus = set(firebase_items.keys()) if firebase_items else set()

        skus_to_delete = firebase_skus - file_skus

        update_payload = {}
        for sku in skus_to_delete:
            update_payload[f"items/{sku}"] = None

        for sku, item_data in file_items.items():
            update_payload[f"items/{sku}"] = item_data

        if update_payload:
            db.update(update_payload, admin_token)

        num_synced = len(file_items)
        num_deleted = len(skus_to_delete)

        return True, num_synced, num_deleted

    except FileNotFoundError:
        return False, "File not found.", 0
    except Exception as e:
        return False, f"An error occurred: {e}", 0


def add_new_item(item_data, token):
    sku = item_data.get("SKU")
    if not sku or not token:
        return False
    try:
        db.child("items").child(sku).set(item_data, token)
        return True
    except Exception as e:
        print(f"Error adding new item to Firebase: {e}")
        return False


def find_item_by_identifier(identifier, token):
    if not identifier: return None

    item = db.child("items").child(identifier).get(token).val()
    if item:
        return item

    try:
        results = db.child("items").order_by_child("Attribute 4 value(s)").equal_to(identifier).get(token).val()
        if results:
            return list(results.values())[0]
    except Exception as e:
        print(f"Warning: Query on barcode failed. Is it indexed in Firebase Rules? Error: {e}")

    all_items_dict = db.child("items").get(token).val()
    if not all_items_dict: return None
    for sku, item_data in all_items_dict.items():
        part_number = extract_part_number(item_data.get('Description', ''))
        if part_number and part_number.upper() == identifier.upper():
            return item_data

    return None


def get_replacement_suggestions(category, branch_stock_column, token):
    global category_cache
    if not category or not branch_stock_column or not token:
        return []

    try:
        results = db.child("items").order_by_child("Categories").equal_to(category).get(token).val()
        category_items = list(results.values()) if results else []
    except Exception as e:
        print(f"Warning: Query on category failed. Is it indexed in Firebase Rules? Error: {e}")
        category_items = []

    status_dict = get_display_status(token)
    on_display_skus = status_dict.get(branch_stock_column, [])
    suggestions = []

    for item in category_items:
        stock_str = item.get(branch_stock_column, '0')
        is_in_stock = False
        if stock_str:
            stock_value_clean = str(stock_str).replace(',', '')
            is_in_stock = int(stock_value_clean) > 0 if stock_value_clean.isdigit() else False

        if item.get('SKU') not in on_display_skus and is_in_stock:
            suggestions.append(item)

    return suggestions


def get_display_status(token):
    if not token: return {}
    status = db.child("displayStatus").get(token).val()
    return status if status else {}


def save_display_status(status_dict, token):
    if not token: return
    db.child("displayStatus").set(status_dict, token)


def add_item_to_display(sku, branch_db_key, token):
    if not sku or not branch_db_key or not token: return
    status_dict = get_display_status(token)
    if branch_db_key not in status_dict:
        status_dict[branch_db_key] = []

    if sku not in status_dict[branch_db_key]:
        status_dict[branch_db_key].append(sku)
        save_display_status(status_dict, token)


def remove_item_from_display(sku, branch_db_key, token):
    if not sku or not branch_db_key or not token: return
    status_dict = get_display_status(token)
    if branch_db_key in status_dict and sku in status_dict[branch_db_key]:
        status_dict[branch_db_key].remove(sku)
        save_display_status(status_dict, token)


def is_item_on_display(sku, branch_db_key, token):
    if not token: return False
    status_dict = get_display_status(token)
    return sku in status_dict.get(branch_db_key, [])


def extract_part_number(description):
    if not description: return ""
    match = re.search(r'\[p/n\s*([^\]]+)\]', description, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def extract_specifications(html_description):
    if not html_description: return []
    soup = BeautifulSoup(html_description, 'html.parser')
    return [li.get_text(strip=True).replace(':', ': ').replace('  ', ' ') for li in soup.find_all('li')]
