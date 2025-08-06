from controllers.data_entry.instrument_data_entry_controller import InstrumentDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


class InstrumentDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.instrument_data_entry_controller = InstrumentDataEntryController()

        self.format_price_fields()
        self.ui.instrument_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.instrument_save_btn.clicked.connect(self.save_instrument_to_db_func)
        self.ui.instrument_type.currentTextChanged.connect(self.instrument_type_change_func)

        self.history_table_headers = (["type", "hart_comminucation"] + self.ui.history_table_headers)

        self.refresh_page()

    def instrument_type_change_func(self):
        self.ui.instrument_has_hart.setChecked(False)
        instrument_type = self.ui.instrument_type.currentText()
        if "Calibration" in instrument_type:
            self.ui.instrument_has_hart.hide()
            self.ui.instrument_brand.hide()
        else:
            self.ui.instrument_has_hart.show()
            self.ui.instrument_brand.show()

        if "Manifold" in instrument_type:
            self.ui.instrument_has_hart.hide()
        else:
            self.ui.instrument_has_hart.show()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.instrument_price._last_text = ''
        self.ui.instrument_price.textChanged.connect(lambda: format_line_edit_text(self.ui.instrument_price))

    def refresh_page(self):
        self.clear_instrument_form()
        all_items = self.instrument_data_entry_controller.get_all_instruments()
        self.show_instruments_in_table(all_items)

    def clear_instrument_form(self):
        # Reset form fields to default
        for combo in [self.ui.instrument_type, self.ui.instrument_brand, self.ui.instrument_supplier_list]:
            combo.setCurrentIndex(0)
        self.ui.instrument_price.setText("0")
        self.ui.instrument_has_hart.setChecked(False)

    def show_instruments_in_table(self, instruments_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(instruments_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()
        self.ui.history_list.setSortingEnabled(True)

    def save_instrument_to_db_func(self):
        type = self.ui.instrument_type.currentText().strip() if self.ui.instrument_type.currentIndex() else None
        has_hart = True if self.ui.instrument_has_hart.isChecked() else False
        brand = self.ui.instrument_brand.currentText().strip() if self.ui.instrument_brand.currentIndex() else ""
        supplier = self.ui.instrument_supplier_list.currentText().strip() if self.ui.instrument_supplier_list.currentIndex() else None
        price = parse_price(self.ui.instrument_price.text())

        if not all([type, supplier, price]):
            show_message("Please fill in all required fields.", title="Error Saving Instrument")
            return

        instrument_details = {
            "type": type,
            "hart_comminucation": has_hart,
            "brand": brand,
            "supplier": supplier,
            "price": price,
            "order_number": "",
        }

        success, msg = self.instrument_data_entry_controller.save_instrument(instrument_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")
