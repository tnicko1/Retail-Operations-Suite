# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი). All Rights Reserved.
#
# This file is part of the Retail Operations Suite.
# This software is proprietary and confidential.
#
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.

import json
import pyrebase
import os
import csv
import re
from datetime import datetime
import pytz
from data_handler import extract_part_number, extract_specifications, sanitize_for_indexing
from PyQt6.QtWidgets import QMessageBox

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
    """
    email = None
    identifier = identifier.strip()
    if '@' in identifier:
        email = identifier
    else:
        email = get_email_for_username(identifier.lower())
        if not email:
            QMessageBox.critical(None, "Login Failed", f"Username '{identifier}' not found.")
            return None

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_profile = db.child("users").child(user['localId']).get(user['idToken']).val()

        if user_profile:
            user['role'] = user_profile.get('role', 'User')
            user['username'] = user_profile.get('username', 'N/A')
        else:  # Should not happen for a valid user, but as a fallback
            user['role'] = 'User'
            user['username'] = 'N/A'

        log_activity(user.get('idToken'), f"User {user['username']} ({email}) logged in.")
        return user
    except Exception as e:
        # Parse the error message from Firebase
        try:
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            if error_message == "INVALID_PASSWORD" or error_message == "EMAIL_NOT_FOUND":
                QMessageBox.critical(None, "Login Failed", "Invalid identifier or password.")
            else:
                QMessageBox.critical(None, "Login Failed", f"Firebase error: {error_message}")
        except (IndexError, KeyError, json.JSONDecodeError):
            QMessageBox.critical(None, "Login Failed", f"An unexpected error occurred: {e}")
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
            error_json = e.args[1]
            error_message = json.loads(error_json)['error']['message']
            return None, error_message
        except (IndexError, KeyError, json.JSONDecodeError):
            return None, str(e)


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
        # Define keys that should NOT be treated as attributes and should remain at the top level of the item.
        known_top_level_keys = [
            "SKU", "Name", "Short description", "Description", "Stock", "Stock Vaja", "Stock Marj", "Stock Gldan",
            "Regular price", "Sale price", "Categories", "Image", "category_sanitized"
        ]

        file_skus = set()
        file_items = {}
        with open(filepath, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                sku = row.get("SKU")
                if not sku:
                    continue

                new_item = {'attributes': {}}

                # Iterate through all columns in the row from the CSV
                for key, value in row.items():
                    if not key or value is None or value.strip() in ['', '-']:
                        continue  # Skip empty keys or values

                    # If the key is a known top-level field, add it directly to the item.
                    if key in known_top_level_keys:
                        new_item[key] = value
                    # Otherwise, treat it as a specification and add it to the 'attributes' dictionary.
                    else:
                        new_item['attributes'][key.strip()] = value.strip()

                # Add the sanitized category for indexing
                category = new_item.get("Categories")
                new_item["category_sanitized"] = sanitize_for_indexing(category)

                file_skus.add(sku)
                file_items[sku] = new_item

        firebase_items = db.child("items").get(admin_token).val() or {}
        firebase_skus = set(firebase_items.keys())

        price_history_payload = {}
        tbilisi_tz = pytz.timezone('Asia/Tbilisi')
        timestamp = datetime.now(tbilisi_tz).strftime('%Y-%m-%d %H:%M:%S')

        for sku, new_item_data in file_items.items():
            old_item_data = firebase_items.get(sku)
            if old_item_data:
                old_price = old_item_data.get("Regular price", "N/A")
                new_price = new_item_data.get("Regular price", "N/A")
                if old_price != new_price:
                    history_entry = {
                        "timestamp": timestamp,
                        "old_price": old_price,
                        "new_price": new_price
                    }
                    price_history_payload[f"price_history/{sku}/{timestamp.replace('.', ':')}"] = history_entry

        skus_to_delete = firebase_skus - file_skus

        update_payload = {}
        for sku in skus_to_delete:
            update_payload[f"items/{sku}"] = None

        for sku, item_data in file_items.items():
            update_payload[f"items/{sku}"] = item_data

        update_payload.update(price_history_payload)

        if update_payload:
            db.update(update_payload, admin_token)

        num_synced = len(file_items)
        num_deleted = len(skus_to_delete)

        log_activity(admin_token,
                     f"Admin performed database sync. Updated/Added: {num_synced}, Removed: {num_deleted}.")
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
        QMessageBox.critical(None, "Database Query Error",
                             f"Could not search for category: {category}\n\n"
                             "Please ensure your database rules include an index for 'category_sanitized' on the 'items' node. "
                             "You may also need to re-sync your product list to create the index field.")
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
def get_print_queue(uid, token):
    if not uid or not token: return []
    queue = db.child("user_data").child(uid).child("print_queue").get(token).val()
    return queue if isinstance(queue, list) else []


def save_print_queue(uid, token, queue_data):
    if not uid or not token: return
    db.child("user_data").child(uid).child("print_queue").set(queue_data, token)


def get_saved_batch_lists(uid, token):
    if not uid or not token: return {}
    lists = db.child("user_data").child(uid).child("saved_lists").get(token).val()
    return lists if lists else {}


def save_batch_list(uid, token, list_name, skus):
    if not uid or not token or not list_name: return
    db.child("user_data").child(uid).child("saved_lists").child(list_name).set(skus, token)


def delete_batch_list(uid, token, list_name):
    if not uid or not token or not list_name: return
    db.child("user_data").child(uid).child("saved_lists").child(list_name).remove(token)
