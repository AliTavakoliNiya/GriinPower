from controllers.data_entry.contactor_data_entry_controller import ContactorDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


class ContactorDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.contactor_data_entry_controller = ContactorDataEntryController()

        self.format_price_fields()
        self.ui.contactor_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.contactor_save_btn.clicked.connect(self.save_contactor_to_db_func)

        self.history_table_headers = (["rated_current", "coil_voltage"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.contactor_price._last_text = ''
        self.ui.contactor_price.textChanged.connect(lambda: format_line_edit_text(self.ui.contactor_price))

    def refresh_page(self):
        self.clear_contactor_form()
        motors = self.contactor_data_entry_controller.get_all_contactors()
        self.show_contactors_in_table(motors)

    def clear_contactor_form(self):
        # Reset form fields to default
        for spin in [self.ui.contactor_current, self.ui.contactor_coil_voltage]:
            spin.setValue(0)
        for combo in [self.ui.contactor_brand, self.ui.contactor_supplier_list]:
            combo.setCurrentIndex(0)
        self.ui.contactor_price.setText("0")

    def show_contactors_in_table(self, contactors_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(contactors_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()

    def save_contactor_to_db_func(self):

        current = self.ui.contactor_current.value()
        voltage = self.ui.contactor_coil_voltage.value()
        brand = self.ui.contactor_brand.currentText().strip() if self.ui.contactor_brand.currentIndex() else None
        supplier = self.ui.contactor_supplier_list.currentText().strip() if self.ui.contactor_supplier_list.currentIndex() else None
        price = parse_price(self.ui.contactor_price.text())

        if not all([voltage, brand, supplier, price]):
            show_message("Please fill in all required fields.", title="Error")
            return

        order_number = self.optional_text(self.ui.contactor_order_number)

        contactor_details = {"current": current,
                             "voltage": voltage,
                             "brand": brand,
                             "supplier": supplier,
                             "price": price,
                             "order_number": order_number,
                             }

        success, msg = self.contactor_data_entry_controller.save_contactor(contactor_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")

    def optional_text(self, widget):
        return None if widget.text() == 0 else widget.text().strip()
