from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
import jdatetime

from models import Contactor
from models.item_price_model import insert_price
from models.items.contactor_model import insert_contactor
from models.vendor_model import get_all_vendors, Vendor
from views.message_box_view import show_message
from views.vendor_view import VendorEntry

from controllers.user_session import UserSession


class DataEntry(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/data_entry.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.user_logged = UserSession()

        self.item_list.currentRowChanged.connect(self.display_entry)  # this match QListWidget to QStackWidget

        self.contactor_save_btn.clicked.connect(self.contactor_save_func)

        self.add_vendor_btn1.clicked.connect(self.add_vendor)
        self.add_vendor_btn2.clicked.connect(self.add_vendor)
        self.add_vendor_btn3.clicked.connect(self.add_vendor)
        self.add_vendor_btn4.clicked.connect(self.add_vendor)
        self.add_vendor_btn5.clicked.connect(self.add_vendor)
        self.add_vendor_btn6.clicked.connect(self.add_vendor)
        self.contactor_add_vendor_btn7.clicked.connect(self.add_vendor)

        self.refresh_data()
        self.show()

    def refresh_data(self):
        self.vendors = [Vendor()] + get_all_vendors()

        # Clear the combo box first (optional, in case you're repopulating)
        self.contactor_vendor_list.clear()

        # Populate the combo box with vendor names
        for vendor in self.vendors:
            self.contactor_vendor_list.addItem(vendor.name)


    def contactor_save_func(self):
        contactor = Contactor()
        contactor.current_a = self.contactor_current.value()
        contactor_brand = self.contactor_brand.text() #??????????????????
        contactor_order_number = self.contactor_order_number.text() #?????????????????
        contactor_vendor = self.vendors[self.contactor_vendor_list.currentIndex()] #??????????????
        contactor_price = self.contactor_price.text() #????????????????????
        contactor.modified_by = f"{self.user_logged.first_name} {self.user_logged.last_name}"
        contactor.modified_at = jdatetime.date.today().strftime("%Y/%m/%d %H:%M")

        if contactor.current_a == 0:
            show_message("Contactor Current cant be 0", "Error")
            return

        if contactor_brand == "":
            show_message("Contactor Brand cant be empty", "Error")
            return

        if not contactor_vendor.vendor_id:
            show_message("Select Vendor", "Error")
            return

        if not contactor_price.isdigit():
            show_message("Please Enter correct price value", "Error")
            return
        else:
            contactor_price =int(contactor_price)

        if contactor_price == 0:
            show_message("Price cant be 0", "Error")
            return

        if insert_contactor( contactor):
            success = insert_price(
                item_id=contactor.item_id,
                price=contactor_price,
                brand=contactor_brand,
                order_number=contactor_order_number,
                created_by=contactor.modified_by
            )
            if success:
                show_message(f"Inserted Contactor and Price for item_id={contactor.item_id}", "")
            else:
                show_message("Contactor saved, but failed to insert price", "Warning")
        else:
            show_message("Error inserting Contactor", "Error")

    def display_entry(self, index):
        self.item_stack.setCurrentIndex(index)

    def add_vendor(self):
        self.venor_application_window = VendorEntry(parent=self)
