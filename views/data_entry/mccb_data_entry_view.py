import pandas as pd
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QAbstractItemView
)
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableView, QHBoxLayout, QPushButton

from controllers.data_entry.mccb_data_entry_controller import MCCBDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
from views.message_box_view import show_message, confirmation


class MCCBDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.mccb_data_entry_controller = MCCBDataEntryController(self)

        self.format_price_fields()
        self.ui.mccb_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.mccb_save_btn.clicked.connect(self.save_mccb_to_db_func)
        self.ui.update_mccb_prices_btn.clicked.connect(self.update_mccb_prices_btn_pressed)

        self.history_table_headers = (
                ["rated_current", "breaking_capacity"] + self.ui.history_table_headers
        )

        self.refresh_page()

    def format_price_fields(self):
        self.ui.mccb_price._last_text = ''
        self.ui.mccb_price.textChanged.connect(lambda: format_line_edit_text(self.ui.mccb_price))

    def refresh_page(self):
        self.clear_mccb_form()
        all_items = self.mccb_data_entry_controller.get_all_mccbs()
        self.show_mccbs_in_table(all_items)

    def clear_mccb_form(self):
        for spin in [self.ui.mccb_current, self.ui.mccb_breaking_capacity]:
            spin.setValue(0)
        for combo in [self.ui.mccb_brand, self.ui.mccb_supplier_list]:
            combo.setCurrentIndex(0)
        self.ui.mccb_order_number.setText("")
        self.ui.mccb_price.setText("0")

    def show_mccbs_in_table(self, mccbs_list):
        headers = self.history_table_headers
        df = pd.DataFrame(mccbs_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)

        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()
        self.ui.history_list.setSortingEnabled(True)

    def save_mccb_to_db_func(self):
        rated_current = self.ui.mccb_current.value()
        breaking_capacity = self.ui.mccb_breaking_capacity.value() * 1000
        brand = self.ui.mccb_brand.currentText().strip() if self.ui.mccb_brand.currentIndex() else None
        supplier = self.ui.mccb_supplier_list.currentText().strip() if self.ui.mccb_supplier_list.currentIndex() else None
        price = parse_price(self.ui.mccb_price.text())
        order_number = self.ui.mccb_order_number.text().strip() if self.ui.mccb_order_number.text().strip() else None

        if not all([rated_current, breaking_capacity, brand, supplier, price, order_number]):
            show_message("Please fill in all required fields.", title="Error Saving MCCB")
            return

        mccb_details = {
            "rated_current": rated_current,
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

    def update_mccb_prices_btn_pressed(self):
        if not confirmation(f"You are about to update the Schneider Electric mccb prices from:\n\n"
                            f"nsx100 Series: https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سری-nsx100\n"
                            f"nsx160 Series: https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سه-پل-سری-nsx160\n"
                            f"nsx250 Series: https://elicaelectric.com/کلید-کمپکت-اتوماتیک-سری-nsx250\n"
                            f"nsx400 Series: https://elicaelectric.com/کلید-کمپکت-اتوماتیک-سری-nsx400\n"
                            f"nsx630 Series: https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سری-nsx630\n\n"
                            f"Are you sure?",
                            centeralize=False):
            return

        show_message("Fetching Datas...")
        self.mccb_data_entry_controller.update_mccbs_in_background()

    def show_table(self, data):
        self.table_window = TableWindow(data, on_save_callback=self.save_mccbs_to_db_after_fetch, parent=self.ui)
        self.table_window.show()

    def save_mccbs_to_db_after_fetch(self, data):
        success, msg = self.mccb_data_entry_controller.save_mccbs(data)
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

        self.setWindowTitle("MCCB List")
        self.resize(900, 600)

        self.data = data
        self.on_save_callback = on_save_callback

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.table_view = QTableView()
        layout.addWidget(self.table_view)

        # تعریف هدرها
        headers = [
            "Order Number",
            "Brand",
            "Min Current (A)",
            "Breaking Capacity (kA)",
            "Price (Rial)"
        ]

        # مدل جدول
        self.model = QStandardItemModel(len(data), len(headers))
        self.model.setHorizontalHeaderLabels(headers)

        # پر کردن جدول
        for row, item in enumerate(data):
            self.model.setItem(row, 0, QStandardItem(str(item.get("order_number", ""))))
            self.model.setItem(row, 1, QStandardItem(str(item.get("brand", ""))))
            self.model.setItem(row, 2, QStandardItem(str(item.get("rated_current", ""))))
            self.model.setItem(row, 3, QStandardItem(str(item.get("breaking_capacity", ""))))
            self.model.setItem(row, 4, QStandardItem(str(item.get("price", ""))))

        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setColumnWidth(0, 200)
        self.table_view.setColumnWidth(1, 200)
        self.table_view.setColumnWidth(2, 100)
        self.table_view.setColumnWidth(3, 140)
        self.table_view.setColumnWidth(4, 100)

        # دکمه ذخیره
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save To Database")
        self.save_button.setFixedSize(150, 30)
        self.save_button.clicked.connect(self.save_to_db)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
        self.setCentralWidget(central_widget)

    def save_to_db(self):
        self.close()
        self.on_save_callback(self.data)
