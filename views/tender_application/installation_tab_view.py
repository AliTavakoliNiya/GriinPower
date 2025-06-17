from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from controllers.tender_application.project_session_controller import ProjectSession


class InstallationTab(QWidget):
    def __init__(self, main_view):
        super().__init__()
        uic.loadUi("ui/tender_application/installation_tab.ui", self)
        self.main_view = main_view

        self.current_project = ProjectSession()
        self.electrical_specs = self.current_project.project_electrical_specs


