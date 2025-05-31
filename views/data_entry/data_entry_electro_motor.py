from utils.thousand_separator_line_edit import format_line_edit_text

class ElectroMotorDataEntry:
    def __init__(self, ui_page):
        self.ui = ui_page

        # Format motor price with comma separator on typing
        self.ui.motor_price._last_text = ''
        self.ui.motor_price.textChanged.connect(
            lambda: format_line_edit_text(self.ui.motor_price)
        )

        self.ui.motor_save_btn.clicked.connect(self.save_motor_to_db)

    def validate_required_fields(self):
        if self.ui.motor_power.value() == 0:
            return False, "Motor power must be more than zero."
        if self.ui.motor_rpm.value() == 0:
            return False, "Motor RPM must be more than zero."
        if self.ui.motor_voltage.value() == 0:
            return False, "Motor voltage must be more than zero."

        if not self.ui.motor_brand.currentText().strip():
            return False, "Motor brand must be selected."
        if not self.ui.motor_supplier.currentText().strip():
            return False, "Motor supplier must be selected."

        self.starting_method = self.ui.motor_starting_method.currentText().strip() or None
        self.cooling_method = self.ui.motor_cooling_method.currentText().strip() or None
        self.ip_rating = self.ui.motor_ip.currentText().strip() or None
        self.efficiency_class = self.ui.motor_efficiency_class.currentText().strip() or None
        self.thermal_protection = self.ui.motor_thermal_protection.currentText().strip() or None
        self.painting_ral = self.ui.motor_paiting_ral.currentText().strip() or None

        return True, ""

    def save_motor_to_db(self):
        self.load_values()
        self.validate_required_fields()




    def load_values(self):
        self.groupbox_checked = self.ui.motor_gp_box.isChecked()
        self.power = self.ui.motor_power.value()
        self.rpm = self.ui.motor_rpm.value()
        self.voltage = self.ui.motor_voltage.value()

        self.starting_method = self.ui.motor_starting_method.currentText()
        self.cooling_method = self.ui.motor_cooling_method.currentText()
        self.ip_rating = self.ui.motor_ip.currentText()
        self.efficiency_class = self.ui.motor_efficiency_class.currentText()
        self.thermal_protection = self.ui.motor_thermal_protection.currentText()
        self.painting_ral = self.ui.motor_paiting_ral.currentText()
        self.brand = self.ui.motor_brand.currentText()
        self.order_number = self.ui.motor_order_number.text()
        self.supplier = self.ui.motor_supplier.currentText()
        self.price = self._parse_price(self.ui.motor_price.text())

        selected_item = self.ui.motor_list.currentItem()
        self.selected_list_item = selected_item.text() if selected_item else None

    def _parse_price(self, price_text):
        """Removes comma separators and converts price to int if valid"""
        try:
            clean_text = price_text.replace(',', '')
            return int(clean_text)
        except ValueError:
            return None


