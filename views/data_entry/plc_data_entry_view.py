from controllers.data_entry.plc_data_entry_controller import PLCDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


"""
attribute_keys:
    series --> required
    model --> required
    di_pins --> required
    do_pins --> required
    ai_pins --> required
    ao_pins --> required
    comminucation_type:has_profinet --> required
    comminucation_type:has_profibus --> required
    comminucation_type:has_hart --> required
    has_mpi --> required
    brand --> required
    order_number --> required
    created_by_id --> required
"""

class PLCDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.plc_data_entry_controller = PLCDataEntryController()

        self.format_price_fields()
        self.ui.plc_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.plc_save_btn.clicked.connect(self.save_plc_to_db_func)

        self.history_table_headers = (
                    ["series", "model", "di_pins", "do_pins", "ai_pins", "ao_pins",
                     "has_profinet", "has_profibus", "has_hart", "has_mpi"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.plc_price._last_text = ''
        self.ui.plc_price.textChanged.connect(lambda: format_line_edit_text(self.ui.plc_price))

    def refresh_page(self):
        self.clear_plc_form()
        all_items = self.plc_data_entry_controller.get_all_plcs()
        self.show_plcs_in_table(all_items)

    def clear_plc_form(self):
        # Reset form fields to default
        for spin in [self.ui.plc_di_pins, self.ui.plc_do_pins, self.ui.plc_ai_pins, self.ui.plc_ao_pins]:
            spin.setValue(0)
        for combo in [self.ui.plc_series, self.ui.plc_supplier_list]:
            combo.setCurrentIndex(0)
        for checkbox in [self.ui.has_profinet, self.ui.has_profibus, self.ui.has_mpi, self.ui.has_hart]:
            checkbox.setChecked(False)

        self.ui.plc_order_number.setText("")
        self.ui.plc_model.setText("")
        self.ui.plc_price.setText("0")

    def show_plcs_in_table(self, plcs_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(plcs_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()
        self.ui.history_list.setSortingEnabled(True)

    def save_plc_to_db_func(self):
        series = self.ui.plc_series.currentText().strip() if self.ui.plc_series.currentIndex() else None
        model = self.ui.plc_model.text().strip() if self.ui.plc_model.text().strip() else None

        di_pins = self.ui.plc_di_pins.value()
        do_pins = self.ui.plc_do_pins.value()
        ai_pins = self.ui.plc_ai_pins.value()
        ao_pins = self.ui.plc_ao_pins.value()

        has_profinet = True if self.ui.has_profinet.isChecked() else False
        has_profibus = True if self.ui.has_profibus.isChecked() else False
        has_hart = True if self.ui.has_hart.isChecked() else False
        has_mpi = True if self.ui.has_mpi.isChecked() else False

        brand = self.ui.plc_brand.currentText().strip() if self.ui.plc_brand.currentIndex() else None
        supplier = self.ui.plc_supplier_list.currentText().strip() if self.ui.plc_supplier_list.currentIndex() else None
        price = parse_price(self.ui.plc_price.text())
        order_number = self.ui.plc_order_number.text().strip() if self.ui.plc_order_number.text().strip() else None

        if not all([series, model, brand, supplier, price, order_number]):
            show_message("Please fill in all required fields.", title="Error Saving PLC")
            return

        plc_details = {
            "series": series,
            "model": model,
            "di_pins": di_pins,
            "do_pins": do_pins,
            "ai_pins": ai_pins,
            "ao_pins": ao_pins,
            "has_profinet": has_profinet,
            "has_profibus": has_profibus,
            "has_hart": has_hart,
            "has_mpi": has_mpi,
            "brand": brand,
            "supplier": supplier,
            "price": price,
            "order_number": order_number

        }

        success, msg = self.plc_data_entry_controller.save_plc(plc_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")
