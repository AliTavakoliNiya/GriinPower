import pandas as pd
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QHBoxLayout, QMainWindow, QPushButton, QTableView, QVBoxLayout, QWidget

from controllers.data_entry.bimetal_data_entry_controller import BimetalDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
from views.message_box_view import confirmation, show_message


class BimetalDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.bimetal_data_entry_controller = BimetalDataEntryController(self)

        self.format_price_fields()
        self.ui.bimetal_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.bimetal_save_btn.clicked.connect(self.save_bimetal_to_db_func)
        self.ui.update_bimetal_prices_btn.clicked.connect(self.update_bimetal_prices_btn_pressed)

        self.history_table_headers = (
                ["min_current", "max_current", "tripping_threshold", "class"] + self.ui.history_table_headers)

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
        for spin in [self.ui.bimetal_min_current, self.ui.bimetal_max_current, self.ui.bimetal_tripping_threshold]:
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
        tripping_threshold = self.ui.bimetal_tripping_threshold.value()
        brand = self.ui.bimetal_brand.currentText().strip() if self.ui.bimetal_brand.currentIndex() else None
        supplier = self.ui.bimetal_supplier_list.currentText().strip() if self.ui.bimetal_supplier_list.currentIndex() else None
        price = parse_price(self.ui.bimetal_price.text())
        order_number = self.ui.bimetal_order_number.text().strip() if self.ui.bimetal_order_number.text().strip() else None
        if not all([min_current, max_current, bimetal_class, tripping_threshold, brand, supplier, price, order_number]):
            show_message("Please fill in all required fields.", title="Error")
            return

        bimetal_details = {
            "min_current": min_current,
            "max_current": max_current,
            "tripping_threshold": tripping_threshold,
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

    def update_bimetal_prices_btn_pressed(self):
        if not confirmation(f"You are about to update the Schneider Electric bimetal prices from:\n\n"
                            f"D Series: https://elicaelectric.com/بیمتال-جهت-کنتاکتورهای-سری-d\n\n"
                            f"Are you sure?",
                            centeralize=False):
            return

        show_message("Fetching Datas...")
        self.bimetal_data_entry_controller.update_bimetals_in_background()

    def show_table(self, data):
        self.table_window = TableWindow(data, on_save_callback=self.save_bimetals_to_db_after_fetch, parent=self.ui)
        self.table_window.show()

    def save_bimetals_to_db_after_fetch(self, data):
        success, msg = self.bimetal_data_entry_controller.save_bimetals(data)
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

        self.setWindowTitle("Bimetal List")
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
            "Max Current (A)",
            "Tripping Threshold",
            "Price (Rial)"
        ]

        # مدل جدول
        self.model = QStandardItemModel(len(data), len(headers))
        self.model.setHorizontalHeaderLabels(headers)

        # پر کردن جدول
        for row, item in enumerate(data):
            self.model.setItem(row, 0, QStandardItem(str(item.get("order_number", ""))))
            self.model.setItem(row, 1, QStandardItem(str(item.get("brand", ""))))
            self.model.setItem(row, 2, QStandardItem(str(item.get("min_current", ""))))
            self.model.setItem(row, 3, QStandardItem(str(item.get("max_current", ""))))
            self.model.setItem(row, 4, QStandardItem(str(item.get("tripping_threshold", ""))))
            self.model.setItem(row, 5, QStandardItem(str(item.get("price", ""))))

        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setColumnWidth(0, 100)
        self.table_view.setColumnWidth(1, 150)
        self.table_view.setColumnWidth(2, 100)
        self.table_view.setColumnWidth(3, 100)
        self.table_view.setColumnWidth(4, 120)
        self.table_view.setColumnWidth(5, 100)

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
