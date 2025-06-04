from controllers.data_entry.mccb_data_entry_controller import MCCBDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


class MCCBDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.mccb_data_entry_controller = MCCBDataEntryController()

        self.format_price_fields()
        self.ui.mccb_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.mccb_save_btn.clicked.connect(self.save_mccb_to_db_func)

        self.history_table_headers = (["rated_current", "breaking_capacity"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.mccb_price._last_text = ''
        self.ui.mccb_price.textChanged.connect(lambda: format_line_edit_text(self.ui.mccb_price))

    def refresh_page(self):
        self.clear_mccb_form()
        motors = self.mccb_data_entry_controller.get_all_mccbs()
        self.show_mccbs_in_table(motors)

    def clear_mccb_form(self):
        # Reset form fields to default
        for spin in [self.ui.mccb_current, self.ui.mccb_breaking_capacity]:
            spin.setValue(0)
        for combo in [self.ui.mccb_brand, self.ui.mccb_supplier_list]:
            combo.setCurrentIndex(0)
        self.ui.mccb_order_number.setText("")
        self.ui.mccb_price.setText("0")

    def show_mccbs_in_table(self, mccbs_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(mccbs_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()

    def save_mccb_to_db_func(self):

        current = self.ui.mccb_current.value()
        breaking_capacity = self.ui.mccb_breaking_capacity.value() * 1000
        brand = self.ui.mccb_brand.currentText().strip() if self.ui.mccb_brand.currentIndex() else None
        supplier = self.ui.mccb_supplier_list.currentText().strip() if self.ui.mccb_supplier_list.currentIndex() else None
        price = parse_price(self.ui.mccb_price.text())
        order_number = self.ui.mccb_order_number.text().strip() if self.ui.mccb_order_number.text().strip() else None

        if not all([current, breaking_capacity, brand, supplier, price, order_number]):
            show_message("Please fill in all required fields.", title="Error")
            return

        mccb_details = {"current": current,
                        "breaking_capacity": breaking_capacity,
                        "brand": brand,
                        "supplier": supplier,
                        "price": price,
                        "order_number": order_number,
                        }

        success, msg = self.mccb_data_entry_controller.save_mccb(mccb_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")


