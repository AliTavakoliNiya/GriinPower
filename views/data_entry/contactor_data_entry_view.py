from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableView, QHBoxLayout, QPushButton

from controllers.data_entry.contactor_data_entry_controller import ContactorDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
import pandas as pd

from views.message_box_view import show_message, confirmation


class ContactorDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.contactor_data_entry_controller = ContactorDataEntryController(self)

        self.format_price_fields()
        self.ui.contactor_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.contactor_save_btn.clicked.connect(self.save_contactor_to_db_func)
        self.ui.update_contactor_prices_btn.clicked.connect(self.update_contactor_prices_btn_pressed)

        self.history_table_headers = (["rated_current", "coil_voltage"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.contactor_price._last_text = ''
        self.ui.contactor_price.textChanged.connect(lambda: format_line_edit_text(self.ui.contactor_price))

    def refresh_page(self):
        self.clear_contactor_form()
        all_items = self.contactor_data_entry_controller.get_all_contactors()
        self.show_contactors_in_table(all_items)

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
        order_number = self.ui.contactor_order_number.text().strip() if self.ui.contactor_order_number.text().strip() else None

        if not all([current, voltage, brand, supplier, price, order_number]):
            show_message("Please fill in all required fields.", title="Error")
            return

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

    def update_contactor_prices_btn_pressed(self):

        if not confirmation(f"You are about to update the Schneider Electric contactor prices from:\n\n"
                            f"D series: https://elicaelectric.com/کنتاکتور-220-ولت-ac-سری-d-اشنایدر-contactor-220-v-ac-coil\n"
                            f"G series: https://elicaelectric.com/contactor-tesys-giga\n\n"
                            f"Are you sure?",
                            centeralize=False):
            return

        show_message("Fetching Datas...")
        self.contactor_data_entry_controller.update_contactors_in_background()

    def show_table(self, data):
        self.table_window = TableWindow(data, on_save_callback=self.save_contactors_to_db_after_fetch, parent=self.ui)
        self.table_window.show()

    def save_contactors_to_db_after_fetch(self, data):
        success, msg = self.contactor_data_entry_controller.save_contactors(data)
        if success:
            show_message(msg, title="Saved")
        else:
            show_message(msg, title="Failed")

        self.refresh_page()


class TableWindow(QMainWindow):
    def __init__(self, data, on_save_callback, parent=None):
        super().__init__(parent)
        if parent:
            self.setStyleSheet(parent.styleSheet())

        self.setWindowTitle("contactor list")
        self.data = data
        self.on_save_callback = on_save_callback

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.table_view = QTableView()
        self.resize(780, 600)
        self.model = QStandardItemModel(len(data), 5)
        self.model.setHorizontalHeaderLabels(["Order Number", "Brand", "Amper", "Voltage", "Price"])

        for row, item in enumerate(data):
            self.model.setItem(row, 0, QStandardItem(str(item["order_number"])))
            self.model.setItem(row, 1, QStandardItem(item["brand"]))
            self.model.setItem(row, 2, QStandardItem(str(item["rated_current"])))
            self.model.setItem(row, 3, QStandardItem(str(item["coil_voltage"])))
            self.model.setItem(row, 4, QStandardItem(str(item["price"])))

        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.resizeColumnsToContents()

        layout.addWidget(self.table_view)

        self.table_view.setColumnWidth(0, 200)  # order_number
        self.table_view.setColumnWidth(1, 200)  # brand
        self.table_view.setColumnWidth(2, 100)  # rated_current
        self.table_view.setColumnWidth(3, 100)  # coil_voltage
        self.table_view.setColumnWidth(4, 100)  # price
        self.setCentralWidget(central_widget)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save To Database")
        self.save_button.setFixedSize(150, 30)
        self.save_button.clicked.connect(self.save_to_db)

        button_layout.addStretch()  # Pushes the button to the right
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)


    def save_to_db(self):
        self.close()
        self.on_save_callback(self.data)
