import pandas as pd

from controllers.data_entry.data_entry_electro_motor_controller import ElectroMotorDataEntryController
from utils.pandas_model import PandasModel  # Ensure this exists and is imported
from utils.thousand_separator_line_edit import format_line_edit_text
from utils.thousand_separator_line_edit import parse_price
from views.message_box_view import show_message


class ElectroMotorDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.electro_motor_data_entry_controller = ElectroMotorDataEntryController()
        self.currency = "IRR"

        self.format_price_fields()
        self.ui.motor_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.motor_save_btn.clicked.connect(self.save_motor_to_db_func)

        self.history_table_headers = (["power", "rpm", "voltage", "start_type", "cooling_method", "ip_rating",
                                          "efficiency_class", "painting_ral", "thermal_protection", "is_official",
                                          "is_routine"] + self.ui.history_table_headers)
        self.refresh_page()

    def refresh_page(self):
        self.clear_motor_form()
        motors = self.electro_motor_data_entry_controller.get_all_motors()
        self.show_motors_in_table(motors)

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.motor_price._last_text = ''
        self.ui.motor_price.textChanged.connect(lambda: format_line_edit_text(self.ui.motor_price))

    def clear_motor_form(self):
        # Reset form fields to default
        for spin in [self.ui.motor_power, self.ui.motor_rpm, self.ui.motor_voltage]:
            spin.setValue(0)
        for combo in [self.ui.motor_brand, self.ui.motor_supplier, self.ui.motor_phone_email,
                      self.ui.motor_special_routine, self.ui.motor_starting_method,
                      self.ui.motor_cooling_method, self.ui.motor_ip, self.ui.motor_efficiency_class,
                      self.ui.motor_thermal_protection, self.ui.motor_paiting_ral]:
            combo.setCurrentIndex(0)
        self.ui.motor_price.setText("0")

    def show_motors_in_table(self, motor_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(motor_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()

    def save_motor_to_db_func(self):
        power = self.ui.motor_power.value()
        rpm = self.ui.motor_rpm.value()
        voltage = self.ui.motor_voltage.value()
        brand = self.ui.motor_brand.currentText().strip() if self.ui.motor_brand.currentIndex() else None
        supplier = self.ui.motor_supplier.currentText().strip() if self.ui.motor_supplier.currentIndex() else None
        phone_email = self.ui.motor_phone_email.currentText().strip() if self.ui.motor_phone_email.currentIndex() else None
        special_routine = self.ui.motor_special_routine.currentText().strip() if self.ui.motor_special_routine.currentIndex() else None
        price = parse_price(self.ui.motor_price.text())

        if not all([power, rpm, voltage, brand, supplier, phone_email, special_routine, price]):
            show_message("Please fill in all required fields.", title="Error")
            return

        start_type = self.optional_text(self.ui.motor_starting_method)
        cooling_method = self.optional_text(self.ui.motor_cooling_method)
        ip_rating = self.optional_text(self.ui.motor_ip)
        efficiency_class = self.optional_text(self.ui.motor_efficiency_class)
        painting_ral = self.optional_text(self.ui.motor_paiting_ral)
        thermal_protection = self.optional_text(self.ui.motor_thermal_protection)
        is_official = phone_email
        is_routine = special_routine
        if self.ui.motor_usd.isChecked():
            self.currency = "USD"
        elif self.ui.motor_eur.isChecked():
            self.currency = "EUR"
        else:
            self.currency = "IRR"

        motor_details = {"power": power,
                            "rpm": rpm,
                            "voltage": voltage,
                            "brand": brand,
                            "start_type": start_type,
                            "cooling_method": cooling_method,
                            "ip_rating": ip_rating,
                            "efficiency_class": efficiency_class,
                            "painting_ral": painting_ral,
                            "thermal_protection": thermal_protection,
                            "is_official": is_official,
                            "is_routine": is_routine,
                            "supplier": supplier,
                            "phone_email": phone_email,
                            "special_routine": special_routine,
                            "price": price,
                            "currency": self.currency,
                            }

        success, msg = self.electro_motor_data_entry_controller.save_motor(motor_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")

    def optional_text(self, widget):
        return None if widget.currentIndex() == 0 else widget.currentText().strip()
