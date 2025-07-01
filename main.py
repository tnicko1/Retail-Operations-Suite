import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
import firebase_handler
from auth_ui import LoginWindow
from app import RetailOperationsSuite
import updater

# Define the current version of the application
# This should be updated for each new release and must match the version in updater.py and setup.py
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

    if getattr(sys, 'frozen', False):
        QApplication.setApplicationVersion(APP_VERSION)

    if not firebase_handler.initialize_firebase():
        # This error is already handled with a QMessageBox, so we can just exit.
        return -1

    app = QApplication(sys.argv)

    login_window = LoginWindow()

    # Keep the application running until the login window is closed
    if login_window.exec() == LoginWindow.DialogCode.Accepted:
        user = login_window.user
        main_window = RetailOperationsSuite(user)
        main_window.show()

        # Check for updates after the main window is shown
        updater.check_for_updates(main_window)

        sys.exit(app.exec())
    else:
        # User closed the login window without logging in
        return 0


if __name__ == "__main__":
    # A final try-except block for any errors that might occur even before the hook is set.
    try:
        sys.exit(main())
    except Exception:
        # The global hook should catch this, but this is an absolute fallback.
        error_msg = f"A critical error occurred on startup:\n\n{traceback.format_exc()}"
        QMessageBox.critical(None, "Startup Error", error_msg)
        sys.exit(1)
