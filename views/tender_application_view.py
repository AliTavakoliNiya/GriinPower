import os

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from controllers.project_details import ProjectDetails
from views.electrical_tab_view import ElectricalTab
from views.message_box_view import show_message
from views.project_information_view import ProjectInformationTab
from views.result_tab_view import ResultTab


class TenderApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/tender_application.ui", self)
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

        self.tabWidget.setCurrentIndex(0)  # Start at first tab

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
        if index == 1: # Electrical
            if not self.result_tab.check_info_tab_ui_rules():
                self.tabWidget.setCurrentIndex(0)

        if index == 2 : # Result
            if not self.result_tab.check_electrical_tab_ui_rules():
                self.tabWidget.setCurrentIndex(1)
            else:
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
