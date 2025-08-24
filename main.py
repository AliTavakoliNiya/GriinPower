import json
import os
import sys
import traceback

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import (
    QDialog, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy
)

from controllers.tender_application.project_session_controller import ProjectSession
from controllers.user_session_controller import UserSession
from utils.database import SessionLocal
from views.account_view import Account
from views.data_entry.data_entry_view import DataEntry
from views.login_view import LoginView
from views.message_box_view import show_message
from views.supplier_view import SupplierEntry
from views.tender_application.open_project_view import OpenProjectView
from views.tender_application.tender_application_view import TenderApplication


class GriinPower(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI and set window properties
        uic.loadUi("ui/main.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")

        # Initialize settings and apply saved theme
        self.settings = QSettings("Griin", "GriinPower")
        self.themes = {
            "dark": "styles/dark_style.qss",
            "coffee": "styles/coffee_style.qss",
            "light": "styles/light_style.qss"
        }
        self.theme_menu = self.menuBar().addMenu("🎨 Change Theme")

        # Populate theme menu and connect theme change signals
        for name, path in self.themes.items():
            action = QtWidgets.QAction(name, self)
            action.triggered.connect(lambda checked, p=path: self.change_theme(p))
            self.theme_menu.addAction(action)

        # Load last used theme
        last_theme = self.settings.value("theme_path", "styles/dark_style.qss")
        self.apply_stylesheet(last_theme)

        # Load current user session and update UI
        self.current_user = UserSession()
        self.user_details_field.setText(
            f"Welcome, {self.current_user.first_name.title()} {self.current_user.last_name.title()}\n{self.current_user.role}"
        )
        # ----------------------------------------------- Must Change!
        if self.current_user.username == "tavakoliniya":
            pixmap = QPixmap("assets/users/tavakoliniya.jpg")
            self.avatar_field.setPixmap(pixmap)

        elif self.current_user.username == "afshinnejad-m":
            pixmap = QPixmap("assets/users/afshinnejad.jpg")
            self.avatar_field.setPixmap(pixmap)

        else:
            pixmap = QPixmap("assets/users/user.png")
            self.avatar_field.setPixmap(pixmap)

        if self.current_user.role != "admin":
            self.account_btn.setText("My Account")

        # Connect main UI buttons to their respective functions
        self.new_project_btn.clicked.connect(self.tender_application_func)
        self.open_project_btn.clicked.connect(lambda: self.tender_application_func(True))
        self.data_entry_btn.clicked.connect(self.data_entry_func)
        self.supplier_btn.clicked.connect(self.suppliers_func)
        self.account_btn.clicked.connect(self.account_func)

        self.show()

    def change_theme(self, path):
        """Change theme and save selected theme path in settings."""
        self.apply_stylesheet(path)
        self.settings.setValue("theme_path", path)

    def apply_stylesheet(self, path):
        """Load and apply the QSS stylesheet."""
        if os.path.exists(path):
            with open(path, "r") as f:
                self.setStyleSheet(f.read())
        else:
            show_message(f"file {path} not found.", "Details")

    def tender_application_func(self, open_project_clicked=False):
        """Create a new project or open an existing one, then launch tender application UI."""

        # Select Electrical or Mechanical App
        El_app_selected = El_App_selected()
        if El_app_selected.exec_() == QDialog.Rejected:
            return

        current_project = ProjectSession()
        current_project.reset()  # Always start with a clean project session

        if open_project_clicked:
            # If user wants to open an existing project
            dialog = OpenProjectView()
            if dialog.exec_() != QDialog.Accepted:
                return  # User cancelled the dialog, exit function

            # Populate current project with selected project details
            selected = dialog.selected_project
            current_project.id = selected.id
            current_project.name = selected.name
            current_project.code = selected.code
            current_project.unique_no = selected.unique_no
            current_project.revision = selected.revision
            current_project.project_electrical_specs = json.loads(selected.project_electrical_specs)

        # Assign the currently logged-in user as the modifier
        current_project.modified_by_id = self.current_user.id


        # Launch the tender application window
        self.tender_application_window = TenderApplication(parent=self)

    def data_entry_func(self):
        """Open the data entry form."""
        self.data_entry_window = DataEntry(parent=self)

    def suppliers_func(self):
        """Open the supplier entry form."""
        self.venor_application_window = SupplierEntry(parent=self)

    def account_func(self):
        self.account_window = Account(parent=self)

class El_App_selected(QDialog):
    def __init__(self):
        super().__init__()

        # Set up dialog window
        self.setWindowTitle("Select")
        self.setWindowIcon(QIcon('assets/Logo.ico'))


        self.de_button = QPushButton("Mechanical and Basic Design")
        self.el_button = QPushButton("Electrical")
        self.el_button.clicked.connect(self.el_login_func)

        # Form layout (right side)
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.de_button)
        form_layout.addWidget(self.el_button)
        form_layout.addStretch()
        form_widget.setLayout(form_layout)

        # Allow form to expand vertically
        form_widget.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding))

        # Combine logo and form
        main_layout = QHBoxLayout()
        main_layout.addWidget(form_widget)
        self.setLayout(main_layout)

        # Apply default stylesheet
        self.apply_stylesheet("styles/dark_style.qss")

    def apply_stylesheet(self, path):
        """Apply QSS stylesheet to the dialog."""
        if os.path.exists(path):
            with open(path, "r") as f:
                self.setStyleSheet(f.read())
        else:
            show_message(f"file {path} not found.", "Details")

    def el_login_func(self):
        self.accept()  # Close dialog with Accepted resul



def main() -> int:
    app = QApplication(sys.argv)

    db_session = SessionLocal()
    try:
        # Login
        login = LoginView(db_session)
        accepted = (login.exec_() == QDialog.Accepted)  # PyQt6: login.exec()

        if not accepted:
            return 0  # user cancelled login

        # Load last user (optional – you don’t use it yet)
        session = QSettings("Griin", "GriinPower")
        username = session.value("last_username", "")

        # Main window
        window = GriinPower()
        window.show()

        # Run event loop and return its exit code
        return app.exec_()  # PyQt6/PySide6: app.exec()

    except Exception:
        error_message = traceback.format_exc()

        # Keep history of failures
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write("\n" + "="*60 + "\n" + error_message)

        # Try to show a GUI error if possible, else print to stderr
        try:
            show_message(error_message, "Error")
        except Exception:
            sys.stderr.write("An error occurred; see 'error_log.txt'.\n")
            sys.stderr.write(error_message + "\n")

        return 1  # non-zero exit for failure

    finally:
        try:
            db_session.close()
        except Exception:
            pass

if __name__ == "__main__":
    sys.exit(main())

