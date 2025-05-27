import os
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from controllers.user_session import UserSession
from utils.database import SessionLocal
from views.data_entry_view import DataEntry
from views.login_view import LoginView
from views.message_box_view import show_message
from views.tender_application_view import TenderApplication
from views.vendor_view import VendorEntry


class GriinPower(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/GrrinPower.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.new_project_btn.clicked.connect(self.open_new_project_func)
        self.data_entry_btn.clicked.connect(self.open_data_entry_func)
        self.vendor_btn.clicked.connect(self.open_vendors_func)

        self.themes = {
            "dark": "styles/dark_style.qss",
            "coffee": "styles/coffee_style.qss",
            "light": "styles/light_style.qss"
        }
        self.theme_menu = self.menuBar().addMenu("Change Theme")
        for name, path in self.themes.items():
            action = QtWidgets.QAction(name, self)
            action.triggered.connect(lambda checked, p=path: self.change_theme(p))
            self.theme_menu.addAction(action)

        last_theme = self.settings.value("theme_path", "styles/dark_style.qss")
        self.apply_stylesheet(last_theme)

        self.show()

    def change_theme(self, path):
        self.apply_stylesheet(path)
        self.settings.setValue("theme_path", path)

    def apply_stylesheet(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        else:
            show_message(f"file {path} not found.", "Details")

    def open_new_project_func(self):
        self.tender_application_window = TenderApplication(parent=self)

    def open_data_entry_func(self):
        self.data_entry_window = DataEntry(parent=self)

    def open_vendors_func(self):
        self.venor_application_window = VendorEntry(parent=self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize DB
    db_session = SessionLocal()

    # Show login dialog
    login = LoginView(db_session)
    if login.exec_() == QDialog.Accepted:
        session = QSettings("Griin", "GriinPower")
        username = session.value("last_username", "")
        current_user = UserSession()

        window = GriinPower()
        window.show()
        sys.exit(app.exec_())
