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
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox

from utils import resource_path
import json
import pyrebase
import os
import csv
import re
from datetime import datetime
import pytz
from data_handler import extract_part_number, extract_specifications, sanitize_for_indexing
from requests.exceptions import HTTPError

firebase_app = None
auth = None
db = None

# A simple cache for category data to reduce downloads
category_cache = {}


def _db_request(user, operation):
    """
    Wrapper for database operations to handle token expiration and retries.
    - user: The user object from Pyrebase, which will be mutated with new tokens.
    - operation: A lambda function that takes a token and performs the db action.
    """
    if not user or 'idToken' not in user:
        print("Error: No user or token provided for DB request.")
        return None
    try:
        return operation(user['idToken'])
    except HTTPError as e:
        if e.response.status_code == 401:
            print("Token expired. Attempting to refresh...")
            try:
                refreshed_user = auth.refresh(user['refreshToken'])
                user.update(refreshed_user)  # Update user dict with new tokens
                print("Token refreshed successfully. Retrying request...")
                return operation(user['idToken'])
            except Exception as refresh_error:
                print(f"Failed to refresh token: {refresh_error}")
                # Here we could signal for re-authentication
                return None
        else:
            raise  # Re-raise other HTTP errors
    except Exception as e:
        print(f"An unexpected error occurred during DB request: {e}")
        return None


def initialize_firebase():
    """Initializes the Firebase app using credentials from config.json."""
    global firebase_app, auth, db
    try:
        with open(resource_path('config.json'), 'r') as f:
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


def get_email_for_username(username):
    """Looks up the email associated with a given username."""
    if not username: return None
    try:
        return db.child("usernames").child(username).get().val()
    except Exception as e:
        print(f"Error looking up username {username}: {e}")
        return None


def login_user(identifier, password):
    """
    Signs the user in using either an email or a username.
    Returns a tuple: (user, error_message).
    On success, error_message is None.
    On failure, user is None.
    """
    email = None
    identifier = identifier.strip()
    if '@' in identifier:
        email = identifier
    else:
        email = get_email_for_username(identifier.lower())
        if not email:
            return None, f"Username '{identifier}' not found."

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_profile = db.child("users").child(user['localId']).get(user['idToken']).val()

        if user_profile:
            user['role'] = user_profile.get('role', 'User')
            user['username'] = user_profile.get('username', 'N/A')
        else:
            user['role'] = 'User'
            user['username'] = 'N/A'

        log_activity(user.get('idToken'), f"User {user['username']} ({email}) logged in.")
        return user, None
    except Exception as e:
        try:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            if error_message == "INVALID_PASSWORD" or error_message == "EMAIL_NOT_FOUND":
                return None, "Invalid identifier or password."
            else:
                return None, f"Firebase error: {error_message}"
        except (IndexError, KeyError, json.JSONDecodeError):
            return None, f"An unexpected error occurred: {e}"


def refresh_token(user_obj):
    """Refreshes the user's ID token using the refresh token."""
    if not user_obj or 'refreshToken' not in user_obj:
        return None
    try:
        refreshed_user = auth.refresh(user_obj['refreshToken'])
        # The refreshed response contains a new id_token and refresh_token
        # It's important to update the stored user object with these new tokens
        user_obj['idToken'] = refreshed_user['idToken']
        user_obj['refreshToken'] = refreshed_user['refreshToken']
        return user_obj
    except Exception as e:
        print(f"Failed to refresh token: {e}")
        # This might indicate the refresh token has expired, requiring re-login
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


def register_user(email, password, username, is_first):
    """
    Creates a user, immediately signs them in to get a token,
    and uses the token to create their database profile securely, including a username mapping.
    """
    # Step 1: Check if username is already taken
    if get_email_for_username(username):
        return None, "Username is already taken."

    try:
        # Step 2: Create the user in Firebase Auth
        user_auth = auth.create_user_with_email_and_password(email, password)

        # Step 3: Sign in to get the token needed for database writes
        user = auth.sign_in_with_email_and_password(email, password)

        # Step 4: Prepare and write data to the database
        role = "Admin" if is_first else "User"
        user_data = {"email": email, "role": role, "username": username}

        # Atomically write user profile and username mapping
        update_payload = {
            f"users/{user['localId']}": user_data,
            f"usernames/{username}": email
        }
        db.update(update_payload, user['idToken'])

        user['role'] = role
        user['username'] = username
        log_activity(user.get('idToken'), f"New user registered: {username} ({email})")
        return user, None
    except Exception as e:
        try:
            # Attempt to parse a Firebase-specific error
            error_json = json.loads(e.args[1])
            error_message = error_json.get('error', {}).get('message', 'An unknown error occurred.')
            return None, error_message
        except (IndexError, KeyError, json.JSONDecodeError, AttributeError):
            # Fallback for non-Firebase errors or unexpected structures
            return None, f"An unexpected error occurred: {e}"


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
        file_items = {}
        all_fieldnames = []
        with open(filepath, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            all_fieldnames = reader.fieldnames or []
            for row in reader:
                sku = row.get("SKU")
                if not sku:
                    continue
                file_items[sku] = row

        file_skus = set(file_items.keys())
        branch_stock_columns = [field for field in all_fieldnames if field.startswith("Stock ")]
        known_top_level_keys = [
            "SKU", "Name", "Short description", "Description", "Stock",
            "Regular price", "Sale price", "Categories", "Image", "category_sanitized"
        ] + branch_stock_columns

        firebase_items = db.child("items").get(admin_token).val() or {}
        firebase_skus = set(firebase_items.keys())

        update_payload = {}
        price_history_payload = {}
        display_update_payload = {}
        
        tbilisi_tz = pytz.timezone('Asia/Tbilisi')
        timestamp = datetime.now(tbilisi_tz).strftime('%Y-%m-%d %H:%M:%S')

        skus_to_potentially_delete = firebase_skus - file_skus
        skus_to_delete = {sku for sku in skus_to_potentially_delete if not firebase_items.get(sku, {}).get("isManual")}
        
        all_display_statuses = get_display_status(admin_token)

        if skus_to_delete:
            for branch, on_display_items in all_display_statuses.items():
                for sku in skus_to_delete:
                    if sku in on_display_items:
                        display_update_payload[f"displayStatus/{branch}/{sku}"] = None
            for sku in skus_to_delete:
                update_payload[f"items/{sku}"] = None

        # --- Use the user-provided hardcoded mapping ---
        branch_mapping = {
            "Gldani Shop": "Stock Gldan",
            "Marjanishvili": "Stock Marj",
            "Vazha-Pshavela Shop": "Stock Vaja"
        }

        for branch_db_key, stock_col_name in branch_mapping.items():
            on_display_items_for_branch = all_display_statuses.get(branch_db_key, {})
            if not on_display_items_for_branch:
                continue

            for sku in on_display_items_for_branch:
                item_data_from_file = file_items.get(sku)
                if item_data_from_file:
                    stock_value_str = item_data_from_file.get(stock_col_name, '0').replace(',', '')
                    try:
                        stock_value = int(stock_value_str)
                    except (ValueError, TypeError):
                        stock_value = 0
                    
                    if stock_value <= 0:
                        display_update_payload[f"displayStatus/{branch_db_key}/{sku}"] = None

        for sku, row_data in file_items.items():
            new_item = {'attributes': {}}
            for key, value in row_data.items():
                if not key or value is None or value.strip() in ['', '-']:
                    continue
                # Use all_fieldnames to determine what is a top-level key vs an attribute
                if key in known_top_level_keys:
                    new_item[key] = value
                else:
                    new_item['attributes'][key.strip()] = value.strip()
            
            new_item["category_sanitized"] = sanitize_for_indexing(new_item.get("Categories"))
            update_payload[f"items/{sku}"] = new_item

            old_item_data = firebase_items.get(sku)
            if old_item_data:
                old_price = old_item_data.get("Regular price", "N/A")
                new_price = new_item.get("Regular price", "N/A")
                if old_price != new_price:
                    history_entry = {"timestamp": timestamp, "old_price": old_price, "new_price": new_price}
                    price_history_payload[f"price_history/{sku}/{timestamp.replace('.', ':')}"] = history_entry

        if display_update_payload:
            db.update(display_update_payload, admin_token)
        
        update_payload.update(price_history_payload)
        if update_payload:
            db.update(update_payload, admin_token)

        num_synced = len(file_items)
        num_deleted = len(skus_to_delete)
        log_activity(admin_token, f"Admin performed database sync. Updated/Added: {num_synced}, Removed: {num_deleted}.")
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
        # Add the sanitized category for indexing
        category = item_data.get("Categories")
        item_data["category_sanitized"] = sanitize_for_indexing(category)

        db.child("items").child(sku).set(item_data, token)
        log_activity(token, f"User added new item: {sku}")
        return True
    except Exception as e:
        print(f"Error adding new item to Firebase: {e}")
        return False


def get_all_items(token):
    """Fetches all items from the database. Used for caching in the dashboard."""
    if not token: return None
    try:
        return db.child("items").get(token).val()
    except Exception as e:
        print(f"Error fetching all items: {e}")
        return None


def get_items_by_sku(skus, token):
    """Fetches a batch of items from Firebase by their SKUs and returns them as a dictionary."""
    if not skus or not token:
        return {}

    items_data = {}
    for sku in skus:
        try:
            item = db.child("items").child(sku).get(token).val()
            if item:
                items_data[sku] = item
        except Exception as e:
            print(f"Error fetching item with SKU {sku}: {e}")

    return items_data


def find_item_by_identifier(identifier, token):
    if not identifier: return None

    # Priority 1: Check if the identifier is a direct SKU
    item = db.child("items").child(identifier).get(token).val()
    if item:
        return item

    # Priority 2: Check if the identifier is a user-defined Barcode
    column_mappings = get_column_mappings(token)
    barcode_field = column_mappings.get("barcodeField")

    if barcode_field:
        # The barcode field is nested inside the 'attributes' dictionary.
        query_path = f"attributes/{barcode_field}"
        try:
            results = db.child("items").order_by_child(query_path).equal_to(identifier).get(token).val()
            if results:
                return list(results.values())[0]
        except Exception as e:
            print(f"Warning: Query on user-defined barcode field '{query_path}' failed. Is it indexed correctly in Firebase Rules? Error: {e}")

    # Priority 3: Hardcoded check for "Attribute 4 value(s)"
    try:
        query_path = "attributes/Attribute 4 value(s)"
        results = db.child("items").order_by_child(query_path).equal_to(identifier).get(token).val()
        if results:
            return list(results.values())[0]
    except Exception as e:
        # This might fail if the index doesn't exist, which is fine. We can ignore the error.
        print(f"Info: Query on hardcoded barcode field '{query_path}' failed. This is expected if the field is not indexed. Error: {e}")

    # Priority 4: Fallback to searching by Part Number (slow, scans all items)
    all_items_dict = db.child("items").get(token).val()
    if not all_items_dict: return None
    for sku, item_data in all_items_dict.items():
        part_number = extract_part_number(item_data.get('Description', ''))
        if part_number and part_number.upper() == identifier.upper():
            return item_data

    return None


def get_item_price_history(sku, token):
    if not sku or not token: return []
    try:
        history = db.child("price_history").child(sku).get(token).val()
        return list(history.values()) if history else []
    except Exception as e:
        print(f"Error fetching price history for {sku}: {e}")
        return []


def _get_items_by_category_server_side(category, token):
    """
    Helper function to fetch items by category using a server-side query
    on a sanitized index field.
    """
    if not token or not category:
        return []

    sanitized_category = sanitize_for_indexing(category)

    try:
        results = db.child("items").order_by_child("category_sanitized").equal_to(sanitized_category).get(token).val()
        return list(results.values()) if results else []
    except Exception as e:
        print(f"Error querying by category '{category}' (sanitized: '{sanitized_category}'): {e}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(f"Could not search for category: {category}\n\n" 
                    "Please ensure your database rules include an index for 'category_sanitized' on the 'items' node. " 
                    "You may also need to re-sync your product list to create the index field.")
        msg.setWindowTitle("Database Query Error")
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        msg.exec()
        return []


def get_replacement_suggestions(category, branch_db_key, branch_stock_col, token):
    if not category or not branch_stock_col or not token:
        return []

    category_items = _get_items_by_category_server_side(category, token)

    status_dict = get_display_status(token)
    on_display_skus = set(status_dict.get(branch_db_key, {}).keys())
    suggestions = []

    for item in category_items:
        stock_str = str(item.get(branch_stock_col, '0')).replace(',', '')
        is_in_stock = int(stock_str) > 0 if stock_str.isdigit() else False

        if is_in_stock and item.get('SKU') not in on_display_skus:
            suggestions.append(item)

    return suggestions


def get_available_items_for_display(category, branch_db_key, branch_stock_col, token):
    """
    Finds items in a category that are in stock but not on display.
    """
    if not category or not branch_stock_col or not token:
        return []

    category_items = _get_items_by_category_server_side(category, token)

    status_dict = get_display_status(token)
    on_display_skus = set(status_dict.get(branch_db_key, {}).keys())

    available_items = []
    for item in category_items:
        stock_str = str(item.get(branch_stock_col, '0')).replace(',', '')
        is_in_stock = int(stock_str) > 0 if stock_str.isdigit() else False

        if is_in_stock and item.get('SKU') not in on_display_skus:
            available_items.append(item)

    return available_items


# --- Display Status ---
def get_display_status(token):
    if not token: return {}
    status = db.child("displayStatus").get(token).val()
    return status if status else {}


def add_item_to_display(sku, branch_db_key, token):
    """Adds an item to the display list for a branch with a timestamp."""
    if not sku or not branch_db_key or not token: return
    try:
        tbilisi_tz = pytz.timezone('Asia/Tbilisi')
        timestamp = datetime.now(tbilisi_tz).strftime('%Y-%m-%d %H:%M:%S')
        db.child("displayStatus").child(branch_db_key).child(sku).set(timestamp, token)
    except Exception as e:
        print(f"Error adding item to display: {e}")


def remove_item_from_display(sku, branch_db_key, token):
    """Removes an item from the display list for a branch."""
    if not sku or not branch_db_key or not token: return
    try:
        db.child("displayStatus").child(branch_db_key).child(sku).remove(token)
    except Exception as e:
        print(f"Error removing item from display: {e}")


def get_item_display_timestamp(sku, branch_db_key, token):
    """
    Checks if an item is on display for a given branch.
    Returns the timestamp string if it is, otherwise None.
    """
    if not sku or not branch_db_key or not token:
        return None
    try:
        timestamp = db.child("displayStatus").child(branch_db_key).child(sku).get(token).val()
        return timestamp
    except Exception as e:
        print(f"Error checking display status for {sku}: {e}")
        return None


# --- Column Mapping ---
def get_column_mappings(token):
    """Fetches the column mapping rules from Firebase."""
    if not token: return {}
    mappings = db.child("column_mappings").get(token).val()
    return mappings if mappings else {}


def save_column_mappings(mappings, token):
    """Saves the entire column mapping object to Firebase."""
    if not token: return False
    try:
        db.child("column_mappings").set(mappings, token)
        log_activity(token, "Admin updated the column mappings.")
        return True
    except Exception as e:
        print(f"Error saving column mappings: {e}")
        return False


def get_all_attribute_keys(token):
    """Scans all items to find every unique key used in 'attributes'."""
    if not token: return set()
    all_items = get_all_items(token)
    if not all_items: return set()

    all_keys = set()
    for item_data in all_items.values():
        if 'attributes' in item_data and isinstance(item_data['attributes'], dict):
            for key in item_data['attributes'].keys():
                all_keys.add(key)
    return all_keys


def get_attributes_with_examples(token):
    """
    Fetches all unique attribute keys from all products in Firebase,
    along with a single example value for each key.
    """
    if not token:
        return set(), {}

    all_items = get_all_items(token)
    if not all_items:
        return set(), {}

    all_keys = set()
    example_values = {}

    items_iterator = all_items.values() if isinstance(all_items, dict) else all_items

    for item in items_iterator:
        if not item or not isinstance(item, dict):
            continue

        # Process 'attributes' dictionary
        if 'attributes' in item and isinstance(item['attributes'], dict):
            for key, value in item['attributes'].items():
                if value is not None and str(value).strip() != "":
                    all_keys.add(key)
                    if key not in example_values:
                        example_values[key] = str(value)
    return all_keys, example_values




# --- Template Management ---
def get_templates_from_firebase(token):
    if not token: return None
    return db.child("product_templates").get(token).val()


def save_templates_to_firebase(templates, token):
    if not token: return False
    try:
        db.child("product_templates").set(templates, token)
        log_activity(token, "Admin updated product templates.")
        return True
    except Exception as e:
        print(f"Error saving templates to firebase: {e}")
        return False


# --- Activity Log ---
def log_activity(token, message):
    if not token: return
    try:
        user_info = auth.get_account_info(token)
        email = user_info['users'][0].get('email', 'unknown_user')
        tbilisi_tz = pytz.timezone('Asia/Tbilisi')
        timestamp = datetime.now(tbilisi_tz).strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {"timestamp": timestamp, "email": email, "message": message}
        db.child("activity_log").push(log_entry, token)
    except Exception as e:
        print(f"Error logging activity: {e}")


def get_activity_log(token, limit=100):
    if not token: return []
    try:
        logs = db.child("activity_log").order_by_key().limit_to_last(limit).get(token).val()
        if logs:
            return sorted(list(logs.values()), key=lambda x: x['timestamp'], reverse=True)
        return []
    except Exception as e:
        print(f"Error fetching activity log: {e}")
        return []


# --- Print Queue & Recents ---
def get_print_queue(user):
    if not user: return []
    uid = user['localId']

    def operation(token):
        queue = db.child("user_data").child(uid).child("print_queue").get(token).val()
        return queue if isinstance(queue, list) else []

    return _db_request(user, operation) or []


def save_print_queue(user, queue_data):
    if not user: return
    uid = user['localId']

    def operation(token):
        db.child("user_data").child(uid).child("print_queue").set(queue_data, token)

    return _db_request(user, operation) or []


def get_saved_batch_lists(user):
    if not user: return {}
    uid = user['localId']

    def operation(token):
        lists = db.child("user_data").child(uid).child("saved_lists").get(token).val()
        return lists if lists else {}

    return _db_request(user, operation)


def save_batch_list(user, list_name, skus):
    if not user or not list_name: return
    uid = user['localId']

    def operation(token):
        db.child("user_data").child(uid).child("saved_lists").child(list_name).set(skus, token)

    return _db_request(user, operation) or {}


def delete_batch_list(user, list_name):
    if not user or not list_name: return
    uid = user['localId']

    def operation(token):
        db.child("user_data").child(uid).child("saved_lists").child(list_name).remove(token)

    _db_request(user, operation)
