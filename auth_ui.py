from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton,
                             QMessageBox, QFormLayout, QLabel, QDialogButtonBox)
import firebase_handler
from translations import Translator


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()  # Assuming default language is fine for login
        self.setWindowTitle(self.translator.get("login_window_title"))
        self.setModal(True)
        self.user = None

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.identifier_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_login)

        form_layout.addRow(self.translator.get("login_identifier_label"), self.identifier_input)
        form_layout.addRow(self.translator.get("login_password_label"), self.password_input)

        layout.addLayout(form_layout)

        self.login_button = QPushButton(self.translator.get("login_button"))
        self.register_button = QPushButton(self.translator.get("register_button"))

        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.handle_register)

        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

    def handle_login(self):
        identifier = self.identifier_input.text()
        password = self.password_input.text()

        if not identifier or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both identifier and password.")
            return

        try:
            self.user = firebase_handler.login_user(identifier, password)
            if self.user:
                self.accept()
            else:
                # The specific error is now handled inside firebase_handler
                pass  # QMessageBox is shown in the handler
        except Exception as e:
            QMessageBox.critical(self, "Login Error", f"An error occurred during login: {e}")

    def handle_register(self):
        register_dialog = RegisterDialog(self)
        register_dialog.exec()


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self.setWindowTitle(self.translator.get("register_window_title"))
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow(self.translator.get("register_username_label"), self.username_input)
        form_layout.addRow(self.translator.get("register_email_label"), self.email_input)
        form_layout.addRow(self.translator.get("register_password_label"), self.password_input)
        form_layout.addRow(self.translator.get("register_confirm_password_label"), self.confirm_password_input)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.handle_registration)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def handle_registration(self):
        username = self.username_input.text().strip().lower()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not email or not password:
            QMessageBox.warning(self, "Input Error", "Username, email and password cannot be empty.")
            return

        if " " in username:
            QMessageBox.warning(self, "Input Error", "Username cannot contain spaces.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        try:
            is_first = firebase_handler.is_first_user()
            user, error = firebase_handler.register_user(email, password, username, is_first)
            if user:
                role = "Admin" if is_first else "User"
                QMessageBox.information(self, "Success",
                                        f"Account created successfully for {username}. You have been assigned the role: {role}")
                self.accept()
            else:
                QMessageBox.critical(self, "Registration Failed", f"Could not create account: {error}")

        except Exception as e:
            QMessageBox.critical(self, "Registration Failed", f"An unexpected error occurred: {e}")
