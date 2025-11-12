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


import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")
import sys
import os
import traceback

if hasattr(sys, '_MEIPASS'):
    # PyInstaller-specific: Add the bundled DLLs to the PATH
    os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']
else:
    # Development environment: Add the project root to the PATH
    os.environ['PATH'] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + os.environ['PATH']
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox
import firebase_handler
from auth_ui import LoginWindow
from main_window import RetailOperationsSuite
import updater
import data_handler

APP_VERSION = "3.0.2"


def global_exception_hook(exctype, value, tb):
    traceback_details = "".join(traceback.format_exception(exctype, value, tb))
    error_msg = f"An unexpected application error occurred:\n\n{traceback_details}"
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText(error_msg)
    msg.setWindowTitle("Application Error")
    msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    msg.exec()
    sys.exit(1)


def run_update_check(app_version):
    if not getattr(sys, 'frozen', False):
        return True

    QApplication.setApplicationVersion(app_version)
    print("Checking for updates...")
    latest_version, download_url = updater.check_for_updates(app_version)

    if latest_version and download_url:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(f"A new version ({latest_version}) is available.\n"
                    f"You are currently on version {app_version}.\n\n"
                    "Would you like to download and install it now?")
        msg.setWindowTitle("Update Available")
        msg.addButton(QMessageBox.StandardButton.Yes)
        msg.addButton(QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        reply = msg.exec()
        if reply == QMessageBox.StandardButton.Yes:
            updater.download_and_install_update(download_url, parent=None)
            return False
    return True


def main():
    # --- SSL Certificate Fix for PyInstaller ---
    try:
        import ssl
        import certifi
        ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        # This will only fail if certifi is not installed, which shouldn't happen
        # with the updated requirements.txt.
        pass
    # -----------------------------------------

    sys.excepthook = global_exception_hook
    app = QApplication(sys.argv)

    if not run_update_check(APP_VERSION):
        return 0

    if not firebase_handler.initialize_firebase():
        return -1

    while True:
        user = None
        if not user:
            login_window = LoginWindow()
            if login_window.exec() == LoginWindow.DialogCode.Accepted:
                user = login_window.user
            else:
                return 0  # Exit if login is cancelled

        main_window = RetailOperationsSuite(user)
        main_window.showMaximized()

        result = app.exec()
        if result == 0:  # Normal exit
            break
        # If app.exec() returns a specific value for logout, we'll re-enter the loop
        # This requires a signal from the main_window on logout.

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        pass
    except Exception:
        error_msg = f"A critical error occurred on startup:\n\n{traceback.format_exc()}"
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(error_msg)
        msg.setWindowTitle("Startup Error")
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        msg.exec()
        sys.exit(1)
