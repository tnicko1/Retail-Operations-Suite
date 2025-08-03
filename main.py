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


import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
import firebase_handler
from auth_ui import LoginWindow
from app import RetailOperationsSuite
import updater  # Import the new updater module

# Define the current version of the application
# This should be updated for each new release and must match the version in setup.py
# The 'v' prefix on GitHub tags is handled by the updater, so just use the number.
APP_VERSION = "2.2.0"


def global_exception_hook(exctype, value, tb):
    """
    Global exception handler to catch any uncaught exceptions
    and display them in a detailed message box. This is a safety net.
    """
    traceback_details = "".join(traceback.format_exception(exctype, value, tb))
    error_msg = f"An unexpected application error occurred:\n\n{traceback_details}"
    QMessageBox.critical(None, "Application Error", error_msg)
    sys.exit(1)


def run_update_check(app_version):
    """
    Checks for updates and prompts the user to install if a new version is found.
    This function contains the logic that was previously at the start of main().
    It requires a QApplication instance to be running to show message boxes.
    """
    # Only check for updates if the application is frozen (i.e., running as an executable)
    if not getattr(sys, 'frozen', False):
        return True  # Continue normal execution if not frozen

    QApplication.setApplicationVersion(app_version)

    # --- UPDATE CHECK ---
    print("Checking for updates...")
    latest_version, download_url = updater.check_for_updates(app_version)

    if latest_version and download_url:
        reply = QMessageBox.question(None, "Update Available",
                                     f"A new version ({latest_version}) is available.\n"
                                     f"You are currently on version {app_version}.\n\n"
                                     "Would you like to download and install it now?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.Yes)
        if reply == QMessageBox.StandardButton.Yes:
            # This function will download, launch the installer, and exit the app.
            # We pass `None` as the parent for the dialogs.
            updater.download_and_install_update(download_url, parent=None)
            return False  # Signal to exit the application
            
    return True # Signal to continue execution


def main():
    """Main function to run the application."""
    # Set the global exception hook. This MUST be the first thing to run.
    sys.excepthook = global_exception_hook

    app = QApplication(sys.argv)

    # --- Run Update Check ---
    # The application will proceed only if the update check completes
    # without initiating an update.
    if not run_update_check(APP_VERSION):
        return 0  # Exit cleanly if an update is started

    # --- APPLICATION STARTUP ---
    if not firebase_handler.initialize_firebase():
        # This error is already handled with a QMessageBox in the function, so we can just exit.
        return -1

    login_window = LoginWindow()

    # Keep the application running until the login window is closed
    if login_window.exec() == LoginWindow.DialogCode.Accepted:
        user = login_window.user
        main_window = RetailOperationsSuite(user)
        main_window.show()
        sys.exit(app.exec())
    else:
        # User closed the login window without logging in
        return 0


if __name__ == "__main__":
    # A final try-except block for any errors that might occur even before the hook is set.
    try:
        sys.exit(main())
    except SystemExit:
        pass  # Ignore SystemExit exceptions from sys.exit()
    except Exception:
        # The global hook should catch this, but this is an absolute fallback.
        error_msg = f"A critical error occurred on startup:\n\n{traceback.format_exc()}"
        QMessageBox.critical(None, "Startup Error", error_msg)
        sys.exit(1)
