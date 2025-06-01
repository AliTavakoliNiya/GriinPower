from PyQt5.QtWidgets import QTableWidgetItem

from models.component_suppliers import insert_component_suppliers_to_db
from models.items.electric_motor import insert_motor_to_db, get_all_motor
from models.supplier import get_supplier_by_name
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

        # ui rules
        self.currency = "IRR"
        self.ui.motor_usd.toggled.connect(self.update_currency_entry_state)
        self.ui.motor_eur.toggled.connect(self.update_currency_entry_state)
        self.ui.motor_irr.toggled.connect(self.update_currency_entry_state)
        self.update_currency_entry_state()

        self.ui.motor_save_btn.clicked.connect(self.save_motor_to_db)

        self.show_motors_in_table()

    def update_currency_entry_state(self):
        if self.ui.motor_usd.isChecked() or self.ui.motor_eur.isChecked():
            self.ui.motor_convert_currency_entry.show()
            self.ui.motor_convert_currency_field.show()
            self.ui.motor_convert_currency_entry.setText("0")

            self.currency = "IRR"
            if self.ui.motor_usd.isChecked():
                self.ui.motor_convert_currency_field.setText("USD To Rial")
                self.currency = "USD"
            elif self.ui.motor_eur.isChecked():
                self.ui.motor_convert_currency_field.setText("EUR To Rial")
                self.currency = "EUR"

        else:
            self.ui.motor_convert_currency_entry.setText("0")
            self.ui.motor_convert_currency_entry.hide()
            self.ui.motor_convert_currency_field.hide()

    def clear_motor_form(self):
        # Reset required spin boxes
        self.ui.motor_power.setValue(0)
        self.ui.motor_rpm.setValue(0)
        self.ui.motor_voltage.setValue(0)

        # Reset combo boxes to first index
        self.ui.motor_brand.setCurrentIndex(0)
        self.ui.motor_supplier.setCurrentIndex(0)
        self.ui.motor_phone_email.setCurrentIndex(0)
        self.ui.motor_special_routine.setCurrentIndex(0)
        self.ui.motor_starting_method.setCurrentIndex(0)
        self.ui.motor_cooling_method.setCurrentIndex(0)
        self.ui.motor_ip.setCurrentIndex(0)
        self.ui.motor_efficiency_class.setCurrentIndex(0)
        self.ui.motor_thermal_protection.setCurrentIndex(0)
        self.ui.motor_paiting_ral.setCurrentIndex(0)

        # Reset required price field
        self.ui.motor_price.setText("0")

        # Reset optional currency conversion field
        self.ui.motor_convert_currency_entry.setText("0")


    def load_values(self):
        self.power = self.ui.motor_power.value() #required
        self.rpm = self.ui.motor_rpm.value() #required
        self.voltage = self.ui.motor_voltage.value() #required
        self.brand = None if self.ui.motor_brand.currentIndex() == 0 else self.ui.motor_brand.currentText().strip() #required

        self.start_type = None if self.ui.motor_starting_method.currentIndex() == 0 else self.ui.motor_starting_method.currentText().strip() #optional
        self.cooling_method = None if self.ui.motor_cooling_method.currentIndex() == 0 else self.ui.motor_cooling_method.currentText().strip() #optional
        self.ip_rating = None if self.ui.motor_ip.currentIndex() == 0 else self.ui.motor_ip.currentText().strip() #optional
        self.efficiency_class = None if self.ui.motor_efficiency_class.currentIndex() == 0 else self.ui.motor_efficiency_class.currentText().strip() #optional
        self.thermal_protection = None if self.ui.motor_thermal_protection.currentIndex() == 0 else self.ui.motor_thermal_protection.currentText().strip() #optional
        self.painting_ral = None if self.ui.motor_paiting_ral.currentIndex() == 0 else self.ui.motor_paiting_ral.currentText().strip() #optional

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

        success, electro_motor_id = insert_motor_to_db(power=self.power,
                                          rpm=self.rpm,
                                          voltage=self.voltage,
                                          brand=self.brand,
                                          start_type=self.start_type,
                                          cooling_method=self.cooling_method,
                                          ip_rating=self.ip_rating,
                                          efficiency_class=self.efficiency_class,
                                          painting_ral=self.painting_ral,
                                          thermal_protection=self.thermal_protection,
                                          is_official=self.motor_phone_email,
                                          is_routine=self.motor_special_routine,
                                          )
        if not success:
            show_message(electro_motor_id, "Error")
            return

        # add price
        self.price *= self.currency_converter
        success, supplier_id = get_supplier_by_name(self.supplier)
        if not success:
            show_message(supplier_id, "Error")
            return

        success, component_suppliers = insert_component_suppliers_to_db(component_id=electro_motor_id, supplier_id=supplier_id, price=self.price, currency=self.currency)
        if not success:
            show_message(component_suppliers, "Error")
            return

        show_message("✅ Electro Motor Saved successfully")
        self.clear_motor_form()

    from PyQt5.QtWidgets import QTableWidgetItem

    def show_motors_in_table(self):
        motors = get_all_motor()  # list of motor objects

        headers = [
            'Power (kW)', 'RPM', 'Voltage', 'Brand', 'Start Type', 'Cooling Method',
            'IP Rating', 'Efficiency Class', 'Painting RAL', 'Thermal Protection',
            'Is Official', 'Is Routine'
        ]

        table = self.ui.motor_list  # This must be a QTableWidget

        table.clear()  # Clear previous content (headers + cells)
        table.setColumnCount(len(headers))
        table.setRowCount(len(motors))
        table.setHorizontalHeaderLabels(headers)

        for row, motor in enumerate(motors):
            table.setItem(row, 0, QTableWidgetItem(str(motor.power)))
            table.setItem(row, 1, QTableWidgetItem(str(motor.rpm)))
            table.setItem(row, 2, QTableWidgetItem(str(motor.voltage)))
            table.setItem(row, 3, QTableWidgetItem(str(motor.brand or '')))
            table.setItem(row, 4, QTableWidgetItem(str(motor.start_type or '')))
            table.setItem(row, 5, QTableWidgetItem(str(motor.cooling_method or '')))
            table.setItem(row, 6, QTableWidgetItem(str(motor.ip_rating or '')))
            table.setItem(row, 7, QTableWidgetItem(str(motor.efficiency_class or '')))
            table.setItem(row, 8, QTableWidgetItem(str(motor.painting_ral or '')))
            table.setItem(row, 9, QTableWidgetItem(str(motor.thermal_protection or '')))
            table.setItem(row, 10, QTableWidgetItem('Yes' if motor.is_official else 'No'))
            table.setItem(row, 11, QTableWidgetItem('Yes' if motor.is_routine else 'No'))

        table.resizeColumnsToContents()

