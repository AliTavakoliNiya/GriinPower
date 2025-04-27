from PyQt5 import uic
from PyQt5.QtWidgets import QWidget



class ProjectInformationTab(QWidget):
    def __init__(self, project_details):
        super().__init__()
        uic.loadUi("ui/project_information_tab.ui", self)

        self.project_details = project_details

        self.show()


