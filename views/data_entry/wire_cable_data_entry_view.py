import pandas as pd
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableView, QHBoxLayout, QPushButton

from controllers.data_entry.wire_cable_data_entry_controller import WireCableDataEntryController
from utils.pandas_model import PandasModel
from utils.thousand_separator_line_edit import format_line_edit_text, parse_price
from views.message_box_view import show_message, confirmation


class WireCableDataEntryView:
    def __init__(self, ui):
        self.ui = ui
        self.wire_cable_data_entry_controller = WireCableDataEntryController(self)

        self.format_price_fields()
        self.ui.wire_cable_add_supplier_btn.clicked.connect(self.ui.add_supplier)
        self.ui.wire_cable_save_btn.clicked.connect(self.save_wire_cable_to_db_func)
        self.ui.update_wire_cable_prices_btn.clicked.connect(self.update_wire_cable_prices_btn_pressed)


        self.history_table_headers = (["type", "l_number", "l_size", "brand", "note"] + self.ui.history_table_headers)
        self.refresh_page()

    def format_price_fields(self):
        self.ui.wire_cable_price._last_text = ''
        self.ui.wire_cable_price.textChanged.connect(lambda: format_line_edit_text(self.ui.wire_cable_price))

    def refresh_page(self):
        self.clear_wire_cable_form()
        wire_cables = self.wire_cable_data_entry_controller.get_all_wire_cables()
        self.show_wire_cables_in_table(wire_cables)

    def clear_wire_cable_form(self):
        self.ui.wire_cable_type.setCurrentIndex(0)
        self.ui.wire_cable_supplier.setCurrentIndex(0)
        self.ui.wire_cable_brand.setText("")
        self.ui.wire_cable_l_number.setValue(0)
        self.ui.wire_cable_l_size.setValue(0)
        self.ui.wire_cable_note.setText("")
        self.ui.wire_cable_price.setText("0")

    def show_wire_cables_in_table(self, wire_cables_list):
        headers = self.history_table_headers
        df = pd.DataFrame(wire_cables_list, columns=headers)
        df.sort_values(by="date", ascending=False, inplace=True)
        model = PandasModel(df)
        self.ui.history_list.setModel(model)
        self.ui.history_list.resizeColumnsToContents()

    def save_wire_cable_to_db_func(self):
        type = self.ui.wire_cable_type.currentText().strip() if self.ui.wire_cable_type.currentIndex() else None
        brand = self.ui.wire_cable_brand.text().strip() or None
        l_number = self.ui.wire_cable_l_number.value() or None
        l_size = self.ui.wire_cable_l_size.value() or None
        note = self.ui.wire_cable_note.text().strip() or None
        supplier = self.ui.wire_cable_supplier.currentText().strip() if self.ui.wire_cable_supplier.currentIndex() else None
        price = parse_price(self.ui.wire_cable_price.text())

        if not all([type, brand, l_number, l_size, supplier, price]):
            show_message("Please fill in all required fields.", title="Error")
            return

        wire_cable_details = {
            "type": type,
            "brand": brand,
            "l_number": l_number,
            "l_size": l_size,
            "note": note,
            "supplier": supplier,
            "price": price,
            "order_number": "",
        }

        success, msg = self.wire_cable_data_entry_controller.save_wire_cable(wire_cable_details)
        if success:
            show_message(msg, "Saved")
            self.refresh_page()
        else:
            show_message(msg, "Error")

    def update_wire_cable_prices_btn_pressed(self):

        if not confirmation(f"You are about to update the Flexible Cables/Wires prices from:\n\n"
                            "https://www.barghsan.com/لیست-قیمت-سیم-و-کابل-خراسان-افشارنژاد/\n\n"
                            f"Are you sure?",
                            centeralize=False):
            return

        show_message("Fetching Datas...")
        self.wire_cable_data_entry_controller.update_wire_cables_in_background()

    def show_table(self, data):
        self.table_window = TableWindow(data, on_save_callback=self.save_wire_cables_to_db_after_fetch, parent=self.ui)
        self.table_window.show()

    def save_wire_cables_to_db_after_fetch(self, data):
        success, msg = self.wire_cable_data_entry_controller.save_wire_cables(data)
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

        self.setWindowTitle("wire_cable list")
        self.data = data
        self.on_save_callback = on_save_callback

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.table_view = QTableView()
        self.resize(780, 600)
        self.model = QStandardItemModel(len(data), 6)
        self.model.setHorizontalHeaderLabels(["Type", "L Number", "L Size", "Brand", "Note", "Price"])

        for row, item in enumerate(data):
            self.model.setItem(row, 0, QStandardItem(str(item["type"])))
            self.model.setItem(row, 1, QStandardItem(str(item["l_number"])))
            self.model.setItem(row, 2, QStandardItem(str(item["l_size"])))
            self.model.setItem(row, 3, QStandardItem(str(item["brand"])))
            self.model.setItem(row, 4, QStandardItem(str(item["note"])))
            self.model.setItem(row, 5, QStandardItem(str(item["price"])))

        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.resizeColumnsToContents()

        layout.addWidget(self.table_view)

        self.table_view.setColumnWidth(0, 200)  # type
        self.table_view.setColumnWidth(1, 100)  # l_number
        self.table_view.setColumnWidth(2, 100)  # l_size
        self.table_view.setColumnWidth(3, 100)  # brand
        self.table_view.setColumnWidth(4, 100)  # note
        self.table_view.setColumnWidth(5, 100)  # note
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

