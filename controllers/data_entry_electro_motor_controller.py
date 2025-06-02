from models.component_suppliers import insert_component_suppliers_to_db
from models.items.electric_motor import get_all_motors, insert_motor_to_db
from models.supplier import get_supplier_by_name
from utils.thousand_separator_line_edit import parse_price
from views.data_entry.data_entry_electro_motor_view import ElectroMotorDataEntryView
from views.message_box_view import show_message


class ElectroMotorDataEntryController:
    def __init__(self, ui):
        self.view = ElectroMotorDataEntryView(ui)
        self.ui = ui
        self.currency = "IRR"

        self.setup_ui()

    def refresh_table(self):
        motors, attr_keys = get_all_motors()
        headers = ["id", "name", "brand", "model", "order_number", "created_at",
                   "supplier_name", "price", "currency", "date"] + attr_keys
        self.view.show_motors_in_table(motors, headers)

    def setup_ui(self):
        self.view.format_price_fields()
        self.ui.motor_usd.toggled.connect(self.update_currency)
        self.ui.motor_eur.toggled.connect(self.update_currency)
        self.ui.motor_irr.toggled.connect(self.update_currency)
        self.ui.motor_save_btn.clicked.connect(self.save_motor)
        self.update_currency()
        self.refresh_table()


    def update_currency(self):
        if self.ui.motor_usd.isChecked():
            self.currency = "USD"
            self.ui.motor_convert_currency_field.setText("USD To Rial")
        elif self.ui.motor_eur.isChecked():
            self.currency = "EUR"
            self.ui.motor_convert_currency_field.setText("EUR To Rial")
        else:
            self.currency = "IRR"
        self.view.update_currency_fields(self.currency)

    def save_motor(self):
        power = self.ui.motor_power.value()
        rpm = self.ui.motor_rpm.value()
        voltage = self.ui.motor_voltage.value()
        brand = self.ui.motor_brand.currentText().strip() if self.ui.motor_brand.currentIndex() else None
        supplier = self.ui.motor_supplier.currentText().strip() if self.ui.motor_supplier.currentIndex() else None
        phone_email = self.ui.motor_phone_email.currentText().strip() if self.ui.motor_phone_email.currentIndex() else None
        special_routine = self.ui.motor_special_routine.currentText().strip() if self.ui.motor_special_routine.currentIndex() else None
        price = parse_price(self.ui.motor_price.text())
        currency_val = parse_price(self.ui.motor_convert_currency_entry.text())
        currency_converter = 1 if currency_val == 0 else currency_val

        if not all([power, rpm, voltage, brand, supplier, phone_email, special_routine, price]):
            show_message("Please fill in all required fields.", title="Error")
            return

        success, motor_id = insert_motor_to_db(
            power=power, rpm=rpm, voltage=voltage, brand=brand,
            start_type=self.optional_text(self.ui.motor_starting_method),
            cooling_method=self.optional_text(self.ui.motor_cooling_method),
            ip_rating=self.optional_text(self.ui.motor_ip),
            efficiency_class=self.optional_text(self.ui.motor_efficiency_class),
            painting_ral=self.optional_text(self.ui.motor_paiting_ral),
            thermal_protection=self.optional_text(self.ui.motor_thermal_protection),
            is_official=phone_email,
            is_routine=special_routine
        )
        if not success:
            show_message(motor_id, "Error")
            return

        final_price = price * currency_converter
        success, supplier_id = get_supplier_by_name(supplier)
        if not success:
            show_message(supplier_id, "Error")
            return

        success, result = insert_component_suppliers_to_db(
            component_id=motor_id, supplier_id=supplier_id, price=final_price, currency=self.currency
        )
        if not success:
            show_message(result, "Error")
            return

        show_message("✅ Electro Motor Saved successfully")
        self.view.clear_motor_form()
        self.refresh_table()


    def optional_text(self, widget):
        return None if widget.currentIndex() == 0 else widget.currentText().strip()
