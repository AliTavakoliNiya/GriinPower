from models.items.electric_motor import insert_motor_to_db
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
from views.message_box_view import show_message


class ElectroMotorDataEntry:
    def __init__(self, ui_page):
        self.ui = ui_page

        # Format motor price with comma separator on typing
        self.ui.motor_price._last_text = ''
        self.ui.motor_price.textChanged.connect(
            lambda: format_line_edit_text(self.ui.motor_price)
        )
        self.ui.motor_convert_currency_entry._last_text = ''
        self.ui.motor_convert_currency_entry.textChanged.connect(
            lambda: format_line_edit_text(self.ui.motor_convert_currency_entry)
        )

        self.ui.motor_usd.toggled.connect(self.update_currency_entry_state)
        self.ui.motor_eur.toggled.connect(self.update_currency_entry_state)
        self.ui.motor_irr.toggled.connect(self.update_currency_entry_state)
        self.update_currency_entry_state()

        self.ui.motor_save_btn.clicked.connect(self.save_motor_to_db)

    def update_currency_entry_state(self):
        if self.ui.motor_usd.isChecked() or self.ui.motor_eur.isChecked():
            self.ui.motor_convert_currency_entry.show()
            self.ui.motor_convert_currency_field.show()
            self.ui.motor_convert_currency_entry.setText("0")

            if self.ui.motor_usd.isChecked():
                self.ui.motor_convert_currency_field.setText("USD To Rial")
            elif self.ui.motor_eur.isChecked():
                self.ui.motor_convert_currency_field.setText("EUR To Rial")

        else:
            self.ui.motor_convert_currency_entry.setText("0")
            self.ui.motor_convert_currency_entry.hide()
            self.ui.motor_convert_currency_field.hide()

    def load_values(self):
        self.power = self.ui.motor_power.value() #required
        self.rpm = self.ui.motor_rpm.value() #required
        self.voltage = self.ui.motor_voltage.value() #required

        self.start_type = None if self.ui.motor_starting_method.currentIndex() == 0 else self.ui.motor_starting_method.currentText().strip() #optional
        self.cooling_method = None if self.ui.motor_cooling_method.currentIndex() == 0 else self.ui.motor_cooling_method.currentText().strip() #optional
        self.ip_rating = None if self.ui.motor_ip.currentIndex() == 0 else self.ui.motor_ip.currentText().strip() #optional
        self.efficiency_class = None if self.ui.motor_efficiency_class.currentIndex() == 0 else self.ui.motor_efficiency_class.currentText().strip() #optional
        self.thermal_protection = None if self.ui.motor_thermal_protection.currentIndex() == 0 else self.ui.motor_thermal_protection.currentText().strip() #optional
        self.painting_ral = None if self.ui.motor_paiting_ral.currentIndex() == 0 else self.ui.motor_paiting_ral.currentText().strip() #optional

        self.brand = None if self.ui.motor_brand.currentIndex() == 0 else self.ui.motor_brand.currentText().strip() #required
        self.order_number = self.ui.motor_order_number.text() #optional
        self.supplier = None if self.ui.motor_supplier.currentIndex() == 0 else self.ui.motor_supplier.currentText().strip() #required
        self.price = parse_price(self.ui.motor_price.text()) #required
        self.motor_phone_email = None if self.ui.motor_phone_email.currentIndex() == 0 else self.ui.motor_phone_email.currentText().strip() #required
        self.motor_special_routine = None if self.ui.motor_special_routine.currentIndex() == 0 else self.ui.motor_special_routine.currentText().strip() #required
        currency_value = parse_price(self.ui.motor_convert_currency_entry.text())
        self.currency_converter = 1 if currency_value == 0 else currency_value #optional

    def validate_required_fields(self):
        if self.power == 0:
            return False, "Motor power must be more than zero."
        if self.rpm == 0:
            return False, "Motor RPM must be more than zero."
        if self.voltage == 0:
            return False, "Motor voltage must be more than zero."

        if not self.brand:
            return False, "Motor brand must be selected."
        if not self.supplier:
            return False, "Motor supplier must be selected."

        if self.price == 0:
            return False, "Motor price must be greater than zero."

        if not self.motor_phone_email:
            return False, "Motor phone/email must be selected."

        if not self.motor_special_routine:
            return False, "Motor special routine must be selected."

        return True, ""

    def save_motor_to_db(self):
        self.load_values()
        succuess, msg = self.validate_required_fields()
        if not succuess:
            show_message(msg, title="Error")
            return

        success, msg = insert_motor_to_db(power=self.power, rpm=self.rpm, voltage=self.voltage,)
        show_message(msg,"")
