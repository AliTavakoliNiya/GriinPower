import pandas as pd
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableView, QHBoxLayout, QPushButton

from controllers.data_entry.mpcb_data_entry_controller import MPCBDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
from views.message_box_view import show_message, confirmation


class MPCBDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.mpcb_data_entry_controller = MPCBDataEntryController(self)

        self.format_price_fields()
        self.ui.mpcb_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.mpcb_save_btn.clicked.connect(self.save_mpcb_to_db_func)
        self.ui.update_mpcb_prices_btn.clicked.connect(self.update_mpcb_prices_btn_pressed)


        self.history_table_headers = (
                    ["min_current", "max_current", "breaking_capacity", "trip_class"] + self.ui.history_table_headers)

        self.refresh_page()

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.mpcb_price._last_text = ''
        self.ui.mpcb_price.textChanged.connect(lambda: format_line_edit_text(self.ui.mpcb_price))

    def refresh_page(self):
        self.clear_mpcb_form()
        all_items = self.mpcb_data_entry_controller.get_all_mpcbs()
        self.show_mpcbs_in_table(all_items)

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

    def show_table(self, data):
        self.table_window = TableWindow(data, on_save_callback=self.save_mpcbs_to_db_after_fetch, parent=self.ui)
        self.table_window.show()

    def save_mpcbs_to_db_after_fetch(self, data):
        success, msg = self.mpcb_data_entry_controller.save_mpcbs(data)
        if success:
            show_message(msg, title="Saved")
        else:
            show_message(msg, title="Failed")

        self.refresh_page()


    def update_mpcb_prices_btn_pressed(self):
        if not confirmation(f"You are about to update the Schneider Electric mpcb prices from:\n\n"
                            f"GV2 series: https://elicaelectric.com/انواع-کليد-حرارتی-مغناطيسی-سری-gv2\n"
                            f"GV2P series: https://elicaelectric.com/انواع-کليد-حرارتی-مغناطيسی-سری-gv2p\n"
                            f"GV3 series: https://elicaelectric.com/انواع-کليد-حرارتی-مغناطيسی-سری-gv3\n"
                            f"GV4 series: https://elicaelectric.com/کلید-حرارتی-مغناطیسی-سری-gv4-اشنایدر-الکتریک\n"
                            f"GV5 series: https://elicaelectric.com/کلید-حرارتی-مغناطیسی-سری-gv5-اشنایدر-الکتریک\n\n"
                            f"Are you sure?",
                            centeralize=False):
            return

        show_message("Fetching Datas...")
        self.mpcb_data_entry_controller.update_mpcbs_in_background()

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
        self.resize(880, 600)
        self.model = QStandardItemModel(len(data), 6)
        self.model.setHorizontalHeaderLabels(["Order Number", "Brand", "min_current", "max_current", "breaking_capacity", "Price"])

        for row, item in enumerate(data):
            self.model.setItem(row, 0, QStandardItem(str(item["order_number"])))
            self.model.setItem(row, 1, QStandardItem(item["brand"]))
            self.model.setItem(row, 2, QStandardItem(str(item["min_current"])))
            self.model.setItem(row, 3, QStandardItem(str(item["max_current"])))
            self.model.setItem(row, 4, QStandardItem(str(item["breaking_capacity"])))
            self.model.setItem(row, 5, QStandardItem(str(item["price"])))

        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.resizeColumnsToContents()

        layout.addWidget(self.table_view)

        self.table_view.setColumnWidth(0, 200)  # order_number
        self.table_view.setColumnWidth(1, 200)  # brand
        self.table_view.setColumnWidth(2, 100)  # min_current
        self.table_view.setColumnWidth(3, 100)  # max_current
        self.table_view.setColumnWidth(4, 100)  # breaking_capacity
        self.table_view.setColumnWidth(5, 100)  # price
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
