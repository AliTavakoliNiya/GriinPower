from controllers.data_entry.bimetal_data_entry_controller import BimetalDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


class BimetalDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.bimetal_data_entry_controller = BimetalDataEntryController()

        self.format_price_fields()
        self.ui.bimetal_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.bimetal_save_btn.clicked.connect(self.save_bimetal_to_db_func)

        self.history_table_headers = (
                ["min_current", "max_current", "trip_time", "class"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.bimetal_price._last_text = ''
        self.ui.bimetal_price.textChanged.connect(lambda: format_line_edit_text(self.ui.bimetal_price))

    def refresh_page(self):
        self.clear_bimetal_form()
        all_items = self.bimetal_data_entry_controller.get_all_bimetals()
        self.show_bimetals_in_table(all_items)

    def clear_bimetal_form(self):
        # Reset form fields to default
        for spin in [self.ui.bimetal_min_current, self.ui.bimetal_max_current, self.ui.bimetal_trip_time]:
            spin.setValue(0)
        for combo in [self.ui.bimetal_brand, self.ui.bimetal_supplier_list]:
            combo.setCurrentIndex(0)
        self.ui.bimetal_order_number.setText("")
        self.ui.bimetal_class.setText("")
        self.ui.bimetal_price.setText("0")

    def show_bimetals_in_table(self, bimetals_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(bimetals_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()
        self.ui.history_list.setSortingEnabled(True)

    def save_bimetal_to_db_func(self):
        min_current = self.ui.bimetal_min_current.value()
        max_current = self.ui.bimetal_max_current.value()
        bimetal_class = self.ui.bimetal_class.text().strip() if self.ui.bimetal_class.text().strip() else None
        trip_time = self.ui.bimetal_trip_time.value()
        brand = self.ui.bimetal_brand.currentText().strip() if self.ui.bimetal_brand.currentIndex() else None
        supplier = self.ui.bimetal_supplier_list.currentText().strip() if self.ui.bimetal_supplier_list.currentIndex() else None
        price = parse_price(self.ui.bimetal_price.text())
        order_number = self.ui.bimetal_order_number.text().strip() if self.ui.bimetal_order_number.text().strip() else None
        if not all([min_current, max_current, bimetal_class, trip_time, brand, supplier, price, order_number]):
            show_message("Please fill in all required fields.", title="Error")
            return

        bimetal_details = {
            "min_current": min_current,
            "max_current": max_current,
            "trip_time": trip_time,
            "class": bimetal_class,
            "brand": brand,
            "supplier": supplier,
            "price": price,
            "order_number": order_number,
        }

        success, msg = self.bimetal_data_entry_controller.save_bimetal(bimetal_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")
