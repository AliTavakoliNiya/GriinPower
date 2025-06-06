from controllers.data_entry.vfd_softstarter_data_entry_controller import VFDSoftStarterDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


class VFDSoftStarterDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.vfd_softstarter_data_entry_controller = VFDSoftStarterDataEntryController()

        self.format_price_fields()
        self.ui.vfd_softstarter_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.vfd_softstarter_save_btn.clicked.connect(self.save_vfd_softstarter_to_db_func)

        self.history_table_headers = (["type", "power"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.vfd_softstarter_price._last_text = ''
        self.ui.vfd_softstarter_price.textChanged.connect(lambda: format_line_edit_text(self.ui.vfd_softstarter_price))

    def refresh_page(self):
        self.clear_vfd_softstarter_form()
        vfd_softstarters = self.vfd_softstarter_data_entry_controller.get_all_vfd_softstarters()
        self.show_vfd_softstarters_in_table(vfd_softstarters)

    def clear_vfd_softstarter_form(self):
        # Reset form fields to default
        self.ui.vfd_softstarter_type.setCurrentIndex(0)
        self.ui.vfd_softstarter_power.setValue(0)
        self.ui.vfd_softstarter_brand.setCurrentIndex(0)
        self.ui.vfd_softstarter_supplier.setCurrentIndex(0)
        self.ui.vfd_softstarter_price.setText("0")
        self.ui.vfd_softstarter_order_number.setText("")

    def show_vfd_softstarters_in_table(self, vfd_softstarters_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(vfd_softstarters_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()

    def save_vfd_softstarter_to_db_func(self):
        type = self.ui.vfd_softstarter_type.currentText().strip() if self.ui.vfd_softstarter_type.currentIndex() else None
        power = self.ui.vfd_softstarter_power.value() * 1000
        brand = self.ui.vfd_softstarter_brand.currentText().strip()if self.ui.vfd_softstarter_brand.currentIndex() else None
        supplier = self.ui.vfd_softstarter_supplier.currentText().strip() if self.ui.vfd_softstarter_supplier.currentIndex() else None
        price = parse_price(self.ui.vfd_softstarter_price.text())
        order_number = self.ui.vfd_softstarter_order_number.text().strip() if self.ui.vfd_softstarter_order_number.text().strip() else None

        if not all([type, power, brand, order_number, supplier, price]):
            show_message("Please fill in all required fields.", title="Error")
            return

        vfd_softstarter_details = {
            "type": type,
            "power": power,
            "brand": brand,
            "supplier": supplier,
            "price": price,
            "order_number": order_number,
        }

        success, msg = self.vfd_softstarter_data_entry_controller.save_vfd_softstarter(vfd_softstarter_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")
