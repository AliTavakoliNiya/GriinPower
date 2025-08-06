from controllers.data_entry.electrical_panel_data_entry_controller import ElectricalPanelDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


class ElectricalPanelDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.electrical_panel_data_entry_controller = ElectricalPanelDataEntryController()

        self.format_price_fields()
        self.ui.electrical_panel_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.electrical_panel_save_btn.clicked.connect(self.save_electrical_panel_to_db_func)

        self.history_table_headers = (["type", "width", "height", "depth", "ip_rating"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.electrical_panel_price._last_text = ''
        self.ui.electrical_panel_price.textChanged.connect(lambda: format_line_edit_text(self.ui.electrical_panel_price))

    def refresh_page(self):
        self.clear_electrical_panel_form()
        electrical_panels = self.electrical_panel_data_entry_controller.get_all_electrical_panels()
        self.show_electrical_panels_in_table(electrical_panels)

    def clear_electrical_panel_form(self):
        # Reset form fields to default
        self.ui.electrical_panel_type.setCurrentIndex(0)
        self.ui.electrical_panel_ip_rating.setCurrentIndex(0)
        self.ui.electrical_panel_supplier.setCurrentIndex(0)
        self.ui.electrical_panel_width.setValue(0)
        self.ui.electrical_panel_height.setValue(0)
        self.ui.electrical_panel_depth.setValue(0)
        self.ui.electrical_panel_price.setText("0")

    def show_electrical_panels_in_table(self, electrical_panels_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(electrical_panels_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()
        self.ui.history_list.setSortingEnabled(True)

    def save_electrical_panel_to_db_func(self):
        type = self.ui.electrical_panel_type.currentText().strip() if self.ui.electrical_panel_type.currentIndex() else None
        width = self.ui.electrical_panel_width.value() if self.ui.electrical_panel_width.value() else None
        height = self.ui.electrical_panel_width.value() if self.ui.electrical_panel_width.value() else None
        depth = self.ui.electrical_panel_width.value() if self.ui.electrical_panel_width.value() else None
        ip_rating = self.ui.electrical_panel_ip_rating.currentText().strip()if self.ui.electrical_panel_ip_rating.currentIndex() else None

        brand = self.ui.electrical_panel_brand.text().strip() if self.ui.electrical_panel_brand.text().strip() else None
        supplier = self.ui.electrical_panel_supplier.currentText().strip() if self.ui.electrical_panel_supplier.currentIndex() else None
        price = parse_price(self.ui.electrical_panel_price.text())

        if not all([type, width, height, depth, brand, supplier, price]):
            show_message("Please fill in all required fields.", title="Error Saving Electrical Panel")
            return

        electrical_panel_details = {
            "type": type,
            "width": width,
            "height": height,
            "depth": depth,
            "ip_rating": ip_rating,
            "brand": brand,
            "supplier": supplier,
            "price": price,
            "order_number": "",
        }

        success, msg = self.electrical_panel_data_entry_controller.save_electrical_panel(electrical_panel_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")
