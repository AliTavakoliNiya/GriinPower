import os
import sys
import json
import jdatetime

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

# Import application modules
from controllers.tender_application.project_session_controller import ProjectSession
from controllers.user_session_controller import UserSession
from utils.database import SessionLocal
from views.data_entry.data_entry_view import DataEntry
from views.login_view import LoginView
from views.message_box_view import show_message
from views.tender_application.open_project_view import OpenProjectView
from views.tender_application.tender_application_view import TenderApplication
from views.supplier_view import SupplierEntry


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
        self.theme_menu = self.menuBar().addMenu("Change Theme")

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

        if self.current_user.role != "admin":
            self.account_btn.hide()

        # Connect main UI buttons to their respective functions
        self.new_project_btn.clicked.connect(self.tender_application_func)
        self.open_project_btn.clicked.connect(lambda: self.tender_application_func(True))
        self.data_entry_btn.clicked.connect(self.data_entry_func)
        self.supplier_btn.clicked.connect(self.suppliers_func)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize the database session
    db_session = SessionLocal()

    # Launch login window
    login = LoginView(db_session)
    if login.exec_() == QDialog.Accepted:
        # Load last logged-in username (for possible future use)
        session = QSettings("Griin", "GriinPower")
        username = session.value("last_username", "")

        # Launch the main application window
        window = GriinPower()
        window.show()
        sys.exit(app.exec_())
