
from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from controllers.project_details import ProjectDetails
from views.electrical_tab_view import ElectricalTab
from views.project_information_view import ProjectInformationTab
from views.result_tab_view import ResultTab


class TenderApplication(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

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


        self.showMaximized()

    def on_tab_changed(self, index):
        if index == 1: # Electrical
            if not self.project_information_tab.check_info_tab_ui_rules():
                self.tabWidget.setCurrentIndex(0)

        if index == 2 : # Result
            if not self.electrical_tab.check_electrical_tab_ui_rules():
                self.tabWidget.setCurrentIndex(1)
            else:
                self.result_tab.generate_panels()




