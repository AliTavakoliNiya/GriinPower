from controllers.data_entry.mpcb_data_entry_controller import MPCBDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


class MPCBDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.mpcb_data_entry_controller = MPCBDataEntryController()

        self.format_price_fields()
        self.ui.mpcb_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.mpcb_save_btn.clicked.connect(self.save_mpcb_to_db_func)

        self.history_table_headers = (
                    ["min_current", "max_current", "breaking_capacity", "trip_class"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.mpcb_price._last_text = ''
        self.ui.mpcb_price.textChanged.connect(lambda: format_line_edit_text(self.ui.mpcb_price))

    def refresh_page(self):
        self.clear_mpcb_form()
        motors = self.mpcb_data_entry_controller.get_all_mpcbs()
        self.show_mpcbs_in_table(motors)

    def clear_mpcb_form(self):
        # Reset form fields to default
        for spin in [self.ui.mpcb_min_current, self.ui.mpcb_max_current, self.ui.mpcb_breaking_capacity]:
            spin.setValue(0)
        for combo in [self.ui.mpcb_brand, self.ui.mpcb_supplier_list]:
            combo.setCurrentIndex(0)
        self.ui.mpcb_order_number.setText("")
        self.ui.trip_class.setText("")
        self.ui.mpcb_price.setText("0")

    def show_mpcbs_in_table(self, mpcbs_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(mpcbs_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()

    def save_mpcb_to_db_func(self):
        min_current = self.ui.mpcb_min_current.value()
        max_current = self.ui.mpcb_max_current.value()
        trip_class = self.ui.trip_class.text().strip() if self.ui.trip_class.text().strip() else None
        breaking_capacity = self.ui.mpcb_breaking_capacity.value() * 1000
        brand = self.ui.mpcb_brand.currentText().strip() if self.ui.mpcb_brand.currentIndex() else None
        supplier = self.ui.mpcb_supplier_list.currentText().strip() if self.ui.mpcb_supplier_list.currentIndex() else None
        price = parse_price(self.ui.mpcb_price.text())
        order_number = self.ui.mpcb_order_number.text().strip() if self.ui.mpcb_order_number.text().strip() else None

        if not all([min_current, max_current, trip_class, breaking_capacity, brand, supplier, price, order_number]):
            show_message("Please fill in all required fields.", title="Error")
            return

        mpcb_details = {
            "min_current": min_current,
            "max_current": max_current,
            "breaking_capacity": breaking_capacity,
            "trip_class": trip_class,
            "brand": brand,
            "supplier": supplier,
            "price": price,
            "order_number": order_number,
        }

        success, msg = self.mpcb_data_entry_controller.save_mpcb(mpcb_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")
