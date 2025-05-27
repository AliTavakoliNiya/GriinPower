from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from models.vendor_model import get_all_vendors


class VendorEntry(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/vendor_view.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")


        self.vendors_list.itemClicked.connect(self.on_vendor_selected)
        self.clear_form.clicked.connect(self.clear_form_btn)

        self.vendors = []  # List of Vendor objects
        self.refresh_data()

        self.show()

    def clear_form_btn(self):
        self.name.clear()
        self.contact_person.clear()
        self.phone1.clear()
        self.phone2.clear()
        self.email.clear()
        self.address.clear()
        self.vendors_list.clearSelection()

    def refresh_data(self):
        self.vendors = get_all_vendors()

        self.vendors_list.clear()
        for vendor in self.vendors:
            self.vendors_list.addItem(vendor.name)

    def on_vendor_selected(self, item):
        selected_name = item.text()
        selected_vendor = next((v for v in self.vendors if v.name == selected_name), None)

        if selected_vendor:
            self.name.setText(selected_vendor.name or "")
            self.contact_person.setText(selected_vendor.contact_person or "")
            self.phone1.setText(selected_vendor.phone1 or "")
            self.phone2.setText(selected_vendor.phone2 or "")
            self.email.setText(selected_vendor.email or "")
            self.address.setPlainText(selected_vendor.address or "")



