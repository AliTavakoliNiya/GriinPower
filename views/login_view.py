import os

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QDialog, QLineEdit, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy
)

from controllers.user_session import authenticate
from views.message_box_view import show_message


class LoginView(QDialog):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon('assets/Logo.ico'))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.status_label = QLabel()

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)

        # Logo on the left
        self.logo_label = QLabel()
        pixmap = QPixmap("assets/Logo.png")
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setFixedSize(128, 128)
        self.logo_label.setScaledContents(True)

        # Right side form in its own widget for control
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.status_label)
        form_layout.addStretch()  # Pushes everything to the top
        form_widget.setLayout(form_layout)

        # Let the form expand vertically
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        form_widget.setSizePolicy(size_policy)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.logo_label)
        main_layout.addWidget(form_widget)

        self.setLayout(main_layout)

        # Try loading the last username from QSettings
        settings = QSettings("Griin", "GriinPower")
        last_user = settings.value("last_username")
        if last_user:
            self.username_input.setText(last_user)
            self.password_input.setFocus()
        else:
            self.username_input.setFocus()

        self.apply_stylesheet("styles/dark_style.qss")

    def apply_stylesheet(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        else:
            show_message(f"file {path} not found.", "Details")

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if authenticate(username, password):
            # Save username to settings
            settings = QSettings("Griin", "GriinPower")
            settings.setValue("last_username", username)

            self.accept()
        else:
            self.status_label.setText("login failed.")
