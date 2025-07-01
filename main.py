import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
import firebase_handler
from auth_ui import LoginWindow
from app import RetailOperationsSuite
import updater  # Import the new updater module

# Define the current version of the application
# This should be updated for each new release and must match the version in updater.py and setup.py
APP_VERSION = "1.0.0"


def main():
    """Main function to run the application."""
    # Set the application version for cx_Freeze to pick up
    if getattr(sys, 'frozen', False):
        QApplication.setApplicationVersion(APP_VERSION)

    if not firebase_handler.initialize_firebase():
        QMessageBox.critical(None, "Firebase Error",
                             "Could not initialize Firebase. Please check your 'config.json' file and internet connection.")
        return -1

    app = QApplication(sys.argv)

    login_window = LoginWindow()

    # Keep the application running until the login window is closed
    if login_window.exec() == LoginWindow.DialogCode.Accepted:
        user = login_window.user
        main_window = RetailOperationsSuite(user)
        main_window.show()

        # --- Check for updates after the main window is shown ---
        # We pass the main_window as the parent for any message boxes.
        updater.check_for_updates(main_window)

        sys.exit(app.exec())
    else:
        # User closed the login window without logging in
        return 0


if __name__ == "__main__":
    sys.exit(main())
