import os
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from utils.database import SessionLocal
from views.login_view import LoginView

from views.electrical_tab_view import ElectricalTab
from views.message_box_view import show_message
from views.project_information_view import ProjectInformationTab
from views.result_tab_view import ResultTab

from controllers.user_session import UserSession
from controllers.project_details import ProjectDetails


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/main_window.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.project_details = ProjectDetails()

        self.project_information_tab = ProjectInformationTab()
        self.tabWidget.addTab(self.project_information_tab, "Project Information")

        self.electrical_tab = ElectricalTab()
        self.tabWidget.addTab(self.electrical_tab, "Electrical")

        self.result_tab = ResultTab(self)
        self.tabWidget.addTab(self.result_tab, "Result")

        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.tabWidget.setCurrentIndex(1)  # temprory

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

        # try - except here
        last_theme = self.settings.value("theme_path", "styles/dark_style.qss")
        self.apply_stylesheet(last_theme)

        self.showMaximized()

    def on_tab_changed(self, index):
        tab_text = self.tabWidget.tabText(index)
        if tab_text == "Result":
            self.result_tab.generate_panels()

    def apply_stylesheet(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        else:
            show_message(f"file {path} not found.", "Details")

    def change_theme(self, path):
        self.apply_stylesheet(path)
        self.settings.setValue("theme_path", path)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize DB
    db_session = SessionLocal()

    # Show login dialog
    login = LoginView(db_session)
    if login.exec_() == QDialog.Accepted:
        session = QSettings("Griin", "GriinPower")
        username = session.value("last_username", "Unknown")
        current_user = UserSession()

        show_message(f"Welcome back, {current_user.first_name} {current_user.last_name}", title="Welcome")

        window = MainView()
        window.show()
        sys.exit(app.exec_())
