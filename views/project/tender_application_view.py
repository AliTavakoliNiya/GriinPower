from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from controllers.project_datas import ProjectDatas
from views.project.electrical_tab_view import ElectricalTab
from views.project.project_information_view import ProjectInformationTab
from views.project.result_tab_view import ResultTab


class TenderApplication(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/project/tender_application.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.electrical_specs = ProjectDatas().project_electrical_specs

        self.project_information_tab = ProjectInformationTab(self)
        self.tabWidget.addTab(self.project_information_tab, "Project Information")

        self.electrical_tab = ElectricalTab()
        self.tabWidget.addTab(self.electrical_tab, "Electrical")

        self.result_tab = ResultTab(self)
        self.tabWidget.addTab(self.result_tab, "Result")

        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.tabWidget.setCurrentIndex(0)  # Start at first tab

        self.showMaximized()

    def on_tab_changed(self, index):
        if index == 1:  # Electrical
            if not self.project_information_tab.check_info_tab_ui_rules():
                self.tabWidget.setCurrentIndex(0)

        if index == 2:  # Result
            if not self.electrical_tab.check_electrical_tab_ui_rules():
                self.tabWidget.setCurrentIndex(1)
            elif not self.project_information_tab.check_info_tab_ui_rules():
                self.tabWidget.setCurrentIndex(0)
            else:
                self.result_tab.generate_panels()

    def set_rev_hint(self, rev_specs, rev_number):
        """----------------------project_information_tab----------------------"""
        info_tab = self.project_information_tab
        info_tab.max_temprature.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['maximum_temprature']}</b>℃")
        info_tab.min_temprature.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['minimum_temprature']}</b>℃")
        info_tab.project_m_voltage.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['m_voltage']}</b>KV")
        info_tab.project_l_voltage.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['l_voltage']}</b>V")
        info_tab.project_voltage_variation.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['voltage_variation']}</b>%")
        info_tab.altitude_elevation.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['altitude_elevation']}</b>m")
        info_tab.humidity.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['humidity']}</b>%")
        info_tab.project_frequency.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['voltage_frequency']}</b>Hz")
        info_tab.project_frequency_variation.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['frequency_variation']}</b>%")






