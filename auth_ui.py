from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton,
                             QMessageBox, QFormLayout, QLabel, QDialogButtonBox)
import firebase_handler


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Price Tag Dashboard")
        self.setModal(True)
        self.user = None

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register New Account")

        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.handle_register)

        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return

        try:
            self.user = firebase_handler.login_user(email, password)
            if self.user:
                self.accept()
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid email or password.")
        except Exception as e:
            QMessageBox.critical(self, "Login Error", f"An error occurred during login: {e}")

    def handle_register(self):
        register_dialog = RegisterDialog(self)
        register_dialog.exec()


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Account")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.handle_registration)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def handle_registration(self):
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Email and password cannot be empty.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        try:
            is_first = firebase_handler.is_first_user()
            user = firebase_handler.register_user(email, password, is_first)
            if user:
                role = "Admin" if is_first else "User"
                QMessageBox.information(self, "Success",
                                        f"Account created successfully. You have been assigned the role: {role}")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Registration Failed", f"Could not create account: {e}")

