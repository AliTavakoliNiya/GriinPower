import os
import sys

import jdatetime
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from controllers.tender_application.project_session_controller import ProjectSession
from controllers.user_session_controller import UserSession
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

        # set styles
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

        # current user
        self.current_user = UserSession()
        self.user_details_field.setText(
            f"Welcome, {self.current_user.first_name.title()} {self.current_user.last_name.title()}\n{self.current_user.role}")

        # Connect buttons to their signals
        self.new_project_btn.clicked.connect(self.tender_application_func)
        self.open_project_btn.clicked.connect(lambda: self.tender_application_func(True))

        self.data_entry_btn.clicked.connect(self.data_entry_func)
        self.supplier_btn.clicked.connect(self.suppliers_func)

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

    def tender_application_func(self, load_proj=False):
        current_project = ProjectSession() # new empty project
        current_project.modified_by_id = self.current_user.id

        if load_proj:  # open existing project
            open_project_detail_window = OpenProjectView()
            result = open_project_detail_window.exec_()
            if result == QDialog.Accepted:
                current_project.id = open_project_detail_window.selected_project.id
                current_project.name = open_project_detail_window.selected_project.name
                current_project.code = open_project_detail_window.selected_project.code
                current_project.unique_no = open_project_detail_window.selected_project.unique_no
                current_project.revision = open_project_detail_window.selected_project.revision
                current_project.project_electrical_specs = json.loads(open_project_detail_window.selected_project.project_electrical_specs)
            else:
                return  # open project rejected by user

        else: # create new project
            # dont change id to update result ==> id = None
            current_project.revision = 0


        self.tender_application_window = TenderApplication(parent=self)

    def data_entry_func(self):
        self.data_entry_window = DataEntry(parent=self)

    def suppliers_func(self):
        self.venor_application_window = SupplierEntry(parent=self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize DB
    db_session = SessionLocal()

    # Show login dialog
    login = LoginView(db_session)
    if login.exec_() == QDialog.Accepted:
        #if True:
        session = QSettings("Griin", "GriinPower")
        username = session.value("last_username", "")

        window = GriinPower()
        window.show()
        sys.exit(app.exec_())
