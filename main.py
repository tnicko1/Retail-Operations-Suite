import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
import firebase_handler
from auth_ui import LoginWindow
from app import PriceTagDashboard


def main():
    """Main function to run the application."""
    if not firebase_handler.initialize_firebase():
        QMessageBox.critical(None, "Firebase Error",
                             "Could not initialize Firebase. Please check your 'config.json' file and internet connection.")
        return -1

    app = QApplication(sys.argv)

    login_window = LoginWindow()

    # Keep the application running until the login window is closed
    if login_window.exec() == LoginWindow.DialogCode.Accepted:
        user = login_window.user
        dashboard = PriceTagDashboard(user)
        dashboard.show()
        sys.exit(app.exec())
    else:
        # User closed the login window without logging in
        return 0


if __name__ == "__main__":
    sys.exit(main())
