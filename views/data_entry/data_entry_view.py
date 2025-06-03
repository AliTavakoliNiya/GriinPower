from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTableView

from controllers.user_session import UserSession
from views.data_entry.data_entry_electro_motor_view import ElectroMotorDataEntryView
from views.supplier_view import SupplierEntry


class DataEntry(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/data_entry/data_entry.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.user_logged = UserSession()

        self.item_list.currentRowChanged.connect(self.display_entry)  # this match QListWidget to QStackWidget
        self.motor_add_supplier_btn.clicked.connect(self.add_supplier)
        self.hide_show_motor_item_stack_btn.clicked.connect(self.hide_show_motor_item_stack_btn_func)

        self.history_list.setAlternatingRowColors(True)
        self.history_list.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.history_list.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.history_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.history_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.history_list.setWordWrap(True)
        self.history_list.setTextElideMode(Qt.ElideRight)
        self.history_list.verticalHeader().setVisible(False)
        self.history_list.setSelectionBehavior(QTableView.SelectRows)
        self.history_list.setSelectionMode(QTableView.SingleSelection)
        self.history_list.setSortingEnabled(True)

        self.history_table_headers = ["brand", "model", "order_number", "created_at",
                   "supplier_name", "price", "currency", "date"]

        self.display_entry(0)
        self.show()

    def display_entry(self, index):
        self.item_stack.setCurrentIndex(index)
        if index == 0:
            self.electro_motor_data_entry = ElectroMotorDataEntryView(self)


    def add_supplier(self):
        self.venor_application_window = SupplierEntry(parent=self)

    def hide_show_motor_item_stack_btn_func(self):
        # Toggle visibility of motor_list table view
        is_visible = self.item_stack.isVisible()
        self.item_stack.setVisible(not is_visible)

        # Optionally update the button text
        self.hide_show_motor_item_stack_btn.setText(
            "⏩" if is_visible else "⏪"
        )
