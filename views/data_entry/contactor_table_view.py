
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem

class TableWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("لیست کنتاکتورها")
        self.resize(800, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Order#", "Brand", "Amp", "Voltage", "Price"])

        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["order_number"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["brand"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(item["rated_current"])))
            self.table.setItem(row, 3, QTableWidgetItem(str(item["coil_voltage"])))
            self.table.setItem(row, 4, QTableWidgetItem(str(item["price"])))

        layout.addWidget(self.table)
        self.setLayout(layout)
