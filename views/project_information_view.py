from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from controllers.project_details import ProjectDetails



class ProjectInformationTab(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/project_information_tab.ui", self)

        self.project_details = ProjectDetails()

        self.show()


