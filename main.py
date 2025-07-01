# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
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
APP_VERSION = "1.0.0"


def global_exception_hook(exctype, value, tb):
    """
    Global exception handler to catch any uncaught exceptions
    and display them in a detailed message box. This is a safety net.
    """
    traceback_details = "".join(traceback.format_exception(exctype, value, tb))
    error_msg = f"An unexpected application error occurred:\n\n{traceback_details}"
    QMessageBox.critical(None, "Application Error", error_msg)
    sys.exit(1)


def main():
    """Main function to run the application."""
    # Set the global exception hook. This MUST be the first thing to run.
    sys.excepthook = global_exception_hook

    # We need a QApplication instance to show message boxes for the update check.
    # We create it early and use it throughout the application's lifecycle.
    app = QApplication(sys.argv)

    # Only check for updates if the application is frozen (i.e., running as an executable)
    if getattr(sys, 'frozen', False):
        QApplication.setApplicationVersion(APP_VERSION)

        # --- UPDATE CHECK ---
        print("Checking for updates...")
        latest_version, download_url = updater.check_for_updates(APP_VERSION)

        if latest_version and download_url:
            reply = QMessageBox.question(None, "Update Available",
                                         f"A new version ({latest_version}) is available.\n"
                                         f"You are currently on version {APP_VERSION}.\n\n"
                                         "Would you like to download and install it now?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Yes:
                # This function will download, launch the installer, and exit the app.
                updater.download_and_install_update(download_url)
                return 0  # Exit cleanly if update is started
        # If no update or user says no, the app continues.

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
