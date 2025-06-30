import json
import pyrebase
import os
import csv
from datetime import datetime
import pytz
from collections import deque
from data_handler import extract_part_number, extract_specifications

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
        log_activity(user.get('idToken'), f"User {email} logged in.")
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
            log_activity(user.get('idToken'), f"New user registered: {email}")
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


def get_replacement_suggestions(category, branch_db_key, branch_stock_col, token):
    if not category or not branch_stock_col or not token:
        return []

    try:
        results = db.child("items").order_by_child("Categories").equal_to(category).get(token).val()
        category_items = list(results.values()) if results else []
    except Exception as e:
        print(f"Warning: Query on category failed. Error: {e}")
        category_items = []

    status_dict = get_display_status(token)
    on_display_skus = set(status_dict.get(branch_db_key, []))
    suggestions = []

    for item in category_items:
        stock_str = str(item.get(branch_stock_col, '0')).replace(',', '')
        is_in_stock = int(stock_str) > 0 if stock_str.isdigit() else False

        if is_in_stock and item.get('SKU') not in on_display_skus:
            suggestions.append(item)

    return suggestions


# --- Display Status ---
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

    display_set = set(status_dict[branch_db_key])
    if sku not in display_set:
        status_dict[branch_db_key].append(sku)
        save_display_status(status_dict, token)


def remove_item_from_display(sku, branch_db_key, token):
    if not sku or not branch_db_key or not token: return
    status_dict = get_display_status(token)
    if branch_db_key in status_dict and sku in status_dict[branch_db_key]:
        status_dict[branch_db_key].remove(sku)
        save_display_status(status_dict, token)


def is_item_on_display(sku, branch_db_key, token):
    if not token or not branch_db_key: return False
    status_dict = get_display_status(token)
    return sku in status_dict.get(branch_db_key, [])


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


def get_recently_printed(uid, token):
    if not uid or not token: return []
    recent_skus = db.child("user_data").child(uid).child("recently_printed").get(token).val()
    return recent_skus if isinstance(recent_skus, list) else []


def add_to_recently_printed(uid, token, sku):
    if not uid or not token or not sku: return
    try:
        current_list = get_recently_printed(uid, token)

        # Use a deque for efficient adding and trimming
        d = deque(current_list, maxlen=10)

        # If sku is already in the list, remove it to re-add it at the front
        if sku in d:
            d.remove(sku)

        d.appendleft(sku)

        db.child("user_data").child(uid).child("recently_printed").set(list(d), token)
    except Exception as e:
        print(f"Error updating recently printed list: {e}")


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
