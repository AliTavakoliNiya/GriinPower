from controllers.data_entry.general_data_entry_controller import GeneralDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message


class GeneralDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.general_data_entry_controller = GeneralDataEntryController()

        self.format_price_fields()
        self.ui.general_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.general_save_btn.clicked.connect(self.save_general_to_db_func)
        self.ui.general_type.currentTextChanged.connect(self.general_type_change_func)

        self.history_table_headers = (["type", "specification"] + self.ui.history_table_headers)

        self.refresh_page()

    def general_type_change_func(self):
        type_config = {
            'Signal Lamp': {
                'show': True,
                'label': "*Voltage",
                'entry': ""
            },
            'Terminal': {
                'show': True,
                'label': "*Current",
                'entry': ""
            },
            'Selector Switch': {
                'show': False,
                'label': "",
                'entry': "None"
            },
            'Button': {
                'show': False,
                'label': "",
                'entry': "None"
            },
            'Contactor Aux Contact': {
                'show': False,
                'label': "",
                'entry': "None"
            },
            'MCCB Aux Contact': {
                'show': False,
                'label': "",
                'entry': "None"
            },
            'MPCB Aux Contact': {
                'show': False,
                'label': "",
                'entry': "None"
            },
            'Relay': {
                'show': True,
                'label': "*NO/NC",
                'entry': ""
            },
        }

        current_type = self.ui.general_type.currentText()
        config = type_config.get(current_type, {'show': False, 'label': "", 'entry': ""})

        if config['show']:
            self.ui.general_spec_label.show()
            self.ui.general_spec_entry.show()
        else:
            self.ui.general_spec_label.hide()
            self.ui.general_spec_entry.hide()

        self.ui.general_spec_label.setText(config['label'])
        self.ui.general_spec_entry.setText(config['entry'])

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.general_price._last_text = ''
        self.ui.general_price.textChanged.connect(lambda: format_line_edit_text(self.ui.general_price))

    def refresh_page(self):
        self.clear_general_form()
        generals = self.general_data_entry_controller.get_all_generals()
        self.show_generals_in_table(generals)

    def clear_general_form(self):
        # Reset form fields to default
        self.ui.general_type.setCurrentIndex(0)
        self.ui.general_spec_entry.setText("")
        self.ui.general_spec_label.setText("*specification")
        self.ui.general_brand.setText("")
        self.ui.general_supplier.setCurrentIndex(0)
        self.ui.general_price.setText("0")

    def show_generals_in_table(self, generals_list):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        headers = self.history_table_headers

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(generals_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        # Create and set the model
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()

    def save_general_to_db_func(self):
        type = self.ui.general_type.currentText().strip() if self.ui.general_type.currentIndex() else None
        specification = self.ui.general_spec_entry.text().strip() if self.ui.general_spec_entry.text().strip() else None
        brand = self.ui.general_brand.text().strip() if self.ui.general_brand.text().strip() else None
        supplier = self.ui.general_supplier.currentText().strip() if self.ui.general_supplier.currentIndex() else None
        price = parse_price(self.ui.general_price.text())
        order_number = ""

        if not all([type, specification, brand, supplier, price]):
            show_message("Please fill in all required fields.", title="Error")
            return

        specification = "" if self.ui.general_spec_entry.text().strip() == "None" else specification

        general_details = {
            "type": type,
            "specification": specification,
            "brand": brand,
            "supplier": supplier,
            "price": price,
            "order_number": order_number,
        }

        success, msg = self.general_data_entry_controller.save_general(general_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")
