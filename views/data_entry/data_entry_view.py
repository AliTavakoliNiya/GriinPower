from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTableView

from controllers.user_session import UserSession
from views.data_entry.bimetal_data_entry_view import BimetalDataEntryView
from views.data_entry.contactor_data_entry_view import ContactorDataEntryView
from views.data_entry.electro_motor_data_entry_view import ElectroMotorDataEntryView
from views.data_entry.general_data_entry_view import GeneralDataEntryView
from views.data_entry.instrument_data_entry_view import InstrumentDataEntryView
from views.data_entry.mccb_data_entry_view import MCCBDataEntryView
from views.data_entry.mpcb_data_entry_view import MPCBDataEntryView
from views.data_entry.plc_data_entry_view import PLCDataEntryView
from views.data_entry.vfd_softstarter_data_entry_view import VFDSoftStarterDataEntryView
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
        self.hide_show_item_stack_btn.clicked.connect(self.hide_show_item_stack_btn_func)

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

        self.history_table_headers = ["brand", "order_number", "supplier_name","price", "currency", "date", "created_by"]

        self.load_suppliers()

        self.display_entry(0)
        self.show()

    def display_entry(self, index):

        empty_model = QStandardItemModel()
        self.history_list.setModel(empty_model)

        self.item_stack.setCurrentIndex(index)
        if index == 0:
            ElectroMotorDataEntryView(self)
        elif index == 1:
            PLCDataEntryView(self)
        elif index == 2:
            InstrumentDataEntryView(self)
        elif index == 3:
            ContactorDataEntryView(self)
        elif index == 4:
            MPCBDataEntryView(self)
        elif index == 5:
            MCCBDataEntryView(self)
        elif index == 6:
            BimetalDataEntryView(self)
        elif index == 7:
            VFDSoftStarterDataEntryView(self)
        elif index == 8:
            GeneralDataEntryView(self)


    def add_supplier(self):
        self.venor_application_window = SupplierEntry(parent=self)

    def load_suppliers(self):
        suppliers = ["--------", "Elica electric", "Asam kala"]
        self.plc_supplier_list.addItems(suppliers)
        self.instrument_supplier_list.addItems(suppliers)
        self.contactor_supplier_list.addItems(suppliers)
        self.mccb_supplier_list.addItems(suppliers)
        self.mpcb_supplier_list.addItems(suppliers)
        self.bimetal_supplier_list.addItems(suppliers)
        self.general_supplier.addItems(suppliers)
        self.vfd_softstarter_supplier.addItems(suppliers)

    def hide_show_item_stack_btn_func(self):
        # Toggle visibility of motor_list table view
        is_visible = self.item_stack.isVisible()
        self.item_stack.setVisible(not is_visible)

        # Optionally update the button text
        self.hide_show_item_stack_btn.setText(
            "⏩" if is_visible else "⏪"
        )
