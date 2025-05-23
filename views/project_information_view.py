from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QComboBox, QSpinBox, QLineEdit, QCheckBox
from controllers.project_details import ProjectDetails


class ProjectInformationTab(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/project_information_tab.ui", self)

        self.project_details = ProjectDetails()
        self._initialize_info()

    def _initialize_info(self):
        self.project_m_voltage.currentIndexChanged.connect(self._handle_project_m_voltage_changed)
        self.project_l_voltage.currentIndexChanged.connect(self._handle_project_l_voltage_changed)

    def _update_project_value(self, path_list, value=None):
        """Update project details dictionary value at the specified path

        Args:
            path_list: List of keys to navigate the nested dictionary
            value: Value to set (if None, gets from sender widget)
        """
        if value is None:
            # Get value from sender
            sender = self.sender()
            if isinstance(sender, QComboBox):
                value = sender.currentText()
            elif isinstance(sender, QSpinBox):
                value = sender.value()
            elif isinstance(sender, QLineEdit):
                value = sender.text()
            elif isinstance(sender, QCheckBox):
                value = sender.isChecked()
            else:
                return

        # Navigate to the right location in the dictionary
        target = self.project_details
        for key in path_list[:-1]:
            target = target[key]

        # Set the value
        target[path_list[-1]] = value


    def _handle_project_m_voltage_changed(self):
        self._update_project_value(["project_info", "project_m_voltage"], float(self.project_m_voltage.currentText())*1000)

    def _handle_project_l_voltage_changed(self):
        self._update_project_value(["project_info", "project_l_voltage"], float(self.project_l_voltage.currentText()))
