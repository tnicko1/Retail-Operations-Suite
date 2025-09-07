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


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton,
                             QMessageBox, QFormLayout, QLabel, QDialogButtonBox, QCheckBox)
import firebase_handler
from translations import Translator
import data_handler


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

        form_layout.addRow(self.translator.get("login_identifier_label"), self.identifier_input)
        form_layout.addRow(self.translator.get("login_password_label"), self.password_input)
        layout.addLayout(form_layout)

        self.login_button = QPushButton(self.translator.get("login_button"))
        self.register_button = QPushButton(self.translator.get("register_button"))

        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setDefault(True)
        self.register_button.clicked.connect(self.handle_register)

        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

    def handle_login(self):
        identifier = self.identifier_input.text()
        password = self.password_input.text()

        if not identifier or not password:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Please enter both identifier and password.")
            msg.setWindowTitle("Input Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        try:
            self.user, error = firebase_handler.login_user(identifier, password)
            if error:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(error)
                msg.setWindowTitle("Login Failed")
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()
            elif self.user:
                self.accept()
        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(f"An unexpected error occurred during login: {e}")
            msg.setWindowTitle("Login Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()

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
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Username, email and password cannot be empty.")
            msg.setWindowTitle("Input Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        if " " in username:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Username cannot contain spaces.")
            msg.setWindowTitle("Input Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        if password != confirm_password:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Passwords do not match.")
            msg.setWindowTitle("Input Error")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
            return

        try:
            is_first = firebase_handler.is_first_user()
            user, error = firebase_handler.register_user(email, password, username, is_first)
            if user:
                role = "Admin" if is_first else "User"
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText(f"Account created successfully for {username}. You have been assigned the role: {role}")
                msg.setWindowTitle("Success")
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()
                self.accept()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText(f"Could not create account: {error}")
                msg.setWindowTitle("Registration Failed")
                msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                msg.exec()

        except Exception as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(f"An unexpected error occurred: {e}")
            msg.setWindowTitle("Registration Failed")
            msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            msg.exec()
