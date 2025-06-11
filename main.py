import os
import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from controllers.tender_application.project_datas_controller import ProjectDatasController
from controllers.user_session import UserSession
import json
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

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/main.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.new_project_btn.clicked.connect(self.open_project_func)
        self.open_project_btn.clicked.connect(lambda: self.open_project_func(True))
        self.data_entry_btn.clicked.connect(self.open_data_entry_func)
        self.supplier_btn.clicked.connect(self.open_suppliers_func)

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

    def open_project_func(self, load_proj=False):
        if load_proj: # open existing project
            open_project_detail_window = OpenProjectView()
            result = open_project_detail_window.exec_()
            if result == QDialog.Accepted:
                project_datas = ProjectDatasController()
                project_datas.load_data(json.loads(open_project_detail_window.selected_project.datas))
            else:
                return # open project rejected by user

        self.tender_application_window = TenderApplication(parent=self)

    def open_data_entry_func(self):
        self.data_entry_window = DataEntry(parent=self)

    def open_suppliers_func(self):
        self.venor_application_window = SupplierEntry(parent=self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize DB
    db_session = SessionLocal()

    # Show login dialog
    login = LoginView(db_session)
    #if login.exec_() == QDialog.Accepted:
    if True:
        session = QSettings("Griin", "GriinPower")
        username = session.value("last_username", "")
        current_user = UserSession()

        window = GriinPower()
        window.show()
        sys.exit(app.exec_())
