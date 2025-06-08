from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QComboBox, QSpinBox, QLineEdit, QCheckBox
from controllers.project_datas import ProjectDatas
from views.message_box_view import show_message


class ProjectInformationTab(QWidget):
    def __init__(self, main_view):
        super().__init__()
        uic.loadUi("ui/project/project_information_tab.ui", self)
        self.main_view = main_view

        self.electrical_specs = ProjectDatas().project_electrical_specs
        self._initialize_info()
        self.rev_hint_combo.currentIndexChanged.connect(self.on_selection_rev_hint_change)

    def on_selection_rev_hint_change(self, index):
        if index != 0: # rev 00 has no hint
            self.main_view.set_rev_hint(rev_specs=self.electrical_specs, rev_number=self.rev_hint_combo.currentText())

    def _initialize_info(self):
        """ --------------------------- Project Information --------------------------- """
        self.project_name.textChanged.connect(self._handle_project_name_changed)
        self.project_code.textChanged.connect(self._handle_project_code_changed)
        self.project_unique_code.textChanged.connect(self._handle_project_unique_code_changed)
        self.project_site_location.textChanged.connect(self._handle_project_site_location_changed)

        """ --------------------------- Site Condition --------------------------- """
        self.project_m_voltage.currentIndexChanged.connect(self._handle_m_voltage_changed)
        self.project_l_voltage.currentIndexChanged.connect(self._handle_l_voltage_changed)
        self.max_temprature.valueChanged.connect(self._handle_max_temperature_changed)
        self.min_temprature.valueChanged.connect(self._handle_min_temperature_changed)
        self.project_voltage_variation.currentIndexChanged.connect(self._handle_voltage_variation_changed)
        self.altitude_elevation.valueChanged.connect(self._handle_altitude_changed)
        self.humidity.valueChanged.connect(self._handle_humidity_changed)
        self.project_frequency.currentIndexChanged.connect(self._handle_frequency_changed)
        self.project_frequency_variation.currentIndexChanged.connect(self._handle_frequency_variation_changed)

        """ --------------------------- Owner --------------------------- """
        self.owner_name.textChanged.connect(self._handle_owner_changed)
        self.consultant_name.textChanged.connect(self._handle_consultant_name_changed)
        self.employer_name.textChanged.connect(self._handle_employer_name_changed)

        """ --------------------------- Electrical Contact Person --------------------------- """
        self.el_contact_name.textChanged.connect(self._handle_el_contact_name_changed)
        self.el_contact_position.textChanged.connect(self._handle_el_contact_position_changed)
        self.el_contact_phone.textChanged.connect(self._handle_el_contact_phone_changed)

        """ --------------------------- Mechanical Contact Person --------------------------- """
        self.me_contact_name.textChanged.connect(self._handle_me_contact_name_changed)
        self.me_contact_position.textChanged.connect(self._handle_me_contact_position_changed)
        self.me_contact_phone.textChanged.connect(self._handle_me_contact_phone_changed)

        """ --------------------------- Commercial Contact Person --------------------------- """
        self.co_contact_name.textChanged.connect(self._handle_co_contact_name_changed)
        self.co_contact_position.textChanged.connect(self._handle_co_contact_position_changed)
        self.co_contact_phone.textChanged.connect(self._handle_co_contact_phone_changed)


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
        target = self.electrical_specs
        for key in path_list[:-1]:
            target = target[key]

        # Set the value
        target[path_list[-1]] = value

    """ --------------------------- Project Information --------------------------- """
    def _handle_project_name_changed(self):
        self._update_project_value(["project_info", "project_name"], str(self.project_name.text()))

    def _handle_project_code_changed(self):
        self._update_project_value(["project_info", "project_code"], str(self.project_code.text()))

    def _handle_project_unique_code_changed(self):
        self._update_project_value(["project_info", "project_unique_code"], str(self.project_unique_code.text()))

    def _handle_project_site_location_changed(self):
        self._update_project_value(["project_info", "project_site_location"], str(self.project_site_location.toPlainText()))


    """ --------------------------- Site Condition --------------------------- """
    def _handle_m_voltage_changed(self):
        self._update_project_value(["project_info", "m_voltage"], float(self.project_m_voltage.currentText())*1000)

    def _handle_l_voltage_changed(self):
        self._update_project_value(["project_info", "l_voltage"], float(self.project_l_voltage.currentText()))

    def _handle_max_temperature_changed(self, value):
        self._update_project_value(["project_info", "maximum_temprature"], value)

    def _handle_min_temperature_changed(self, value):
        self._update_project_value(["project_info", "minimum_temprature"], value)

    def _handle_voltage_variation_changed(self):
        self._update_project_value(["project_info", "voltage_variation"], float(self.project_voltage_variation.currentText()))

    def _handle_altitude_changed(self, value):
        self._update_project_value(["project_info", "altitude_elevation"], value)

    def _handle_humidity_changed(self, value):
        self._update_project_value(["project_info", "humidity"], value)

    def _handle_frequency_changed(self):
        self._update_project_value(["project_info", "voltage_frequency"], float(self.project_frequency.currentText()))

    def _handle_frequency_variation_changed(self):
        self._update_project_value(["project_info", "frequency_variation"], float(self.project_frequency_variation.currentText()))

    """ --------------------------- Electrical Contact Person --------------------------- """
    def _handle_el_contact_name_changed(self):
        self._update_project_value(["project_info", "el_contact_name"], str(self.el_contact_name.text()))

    def _handle_el_contact_position_changed(self):
        self._update_project_value(["project_info", "el_contact_position"], str(self.el_contact_position.text()))

    def _handle_el_contact_phone_changed(self):
        self._update_project_value(["project_info", "el_contact_phone"], str(self.el_contact_phone.text()))

    """ --------------------------- Mechanical Contact Person --------------------------- """
    def _handle_me_contact_name_changed(self):
        self._update_project_value(["project_info", "me_contact_name"], str(self.me_contact_name.text()))

    def _handle_me_contact_position_changed(self):
        self._update_project_value(["project_info", "me_contact_position"], str(self.me_contact_position.text()))

    def _handle_me_contact_phone_changed(self):
        self._update_project_value(["project_info", "me_contact_phone"], str(self.me_contact_phone.text()))

    """ --------------------------- Commercial Contact Person --------------------------- """
    def _handle_co_contact_name_changed(self):
        self._update_project_value(["project_info", "co_contact_name"], str(self.co_contact_name.text()))

    def _handle_co_contact_position_changed(self):
        self._update_project_value(["project_info", "co_contact_position"],str(self.co_contact_position.text()))

    def _handle_co_contact_phone_changed(self):
        self._update_project_value(["project_info", "co_contact_phone"], str(self.co_contact_phone.text()))

    """ --------------------------- Owner --------------------------- """
    def _handle_owner_changed(self):
        self._update_project_value(["project_info", "owner_name"], str(self.owner_name.text()))

    def _handle_consultant_name_changed(self):
        self._update_project_value(["project_info", "consultant_name"], str(self.consultant_name.text()))

    def _handle_employer_name_changed(self):
        self._update_project_value(["project_info", "employer_name"], str(self.employer_name.text()))


    def check_info_tab_ui_rules(self):
        if self.project_m_voltage.currentIndex() == 0:
            show_message("Please Choose M Voltage", "Error")
            return False

        if self.project_l_voltage.currentIndex() == 0:
            show_message("Please Choose L Voltage", "Error")
            return False

        """ Project AVL"""
        proj_avl = self.electrical_specs["project_info"]["proj_avl"]
        for name, checkbox in [("Siemens", self.proj_avl_siemens), ("Schneider Electric", self.proj_avl_schneider), ("Hyundai", self.proj_avl_hyundai)]:
            if checkbox.isChecked() and name not in proj_avl:
                proj_avl.append(name)
            elif not checkbox.isChecked() and name in proj_avl:
                proj_avl.remove(name)

        return True