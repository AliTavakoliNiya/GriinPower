import re

from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from controllers.vendor_controller import VendorController
from models.vendor_model import Vendor
from views.message_box_view import show_message, confirmation


class VendorEntry(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/vendor_view.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.controller = VendorController()
        self.selected_vendor = Vendor()

        # Connect signals
        self.search_vendor_field.textChanged.connect(self.on_search_text_changed)
        self.vendors_list.itemClicked.connect(self.on_vendor_selected)
        self.clear_form.clicked.connect(self.clear_form_btn)
        self.save_vendor.clicked.connect(self.insert_or_update_vendor)

        self.refresh_data()
        self.show()

    def clear_form_btn(self):
        self.selected_vendor = Vendor()
        self.vendor_gp_box.setTitle("New Vendor")
        self.name.clear()
        self.contact_person.clear()
        self.phone1.clear()
        self.phone2.clear()
        self.email.clear()
        self.address.clear()
        self.search_vendor_field.clear()
        self.vendors_list.clearSelection()

    def refresh_data(self):
        self.clear_form_btn()
        self.vendors_list.clear()

        self.controller.load_vendors()
        for vendor in self.controller.vendors:
            self.vendors_list.addItem(vendor.name)

    def on_vendor_selected(self, item):
        vendor = self.controller.select_vendor_by_name(item.text())
        if vendor:
            self.selected_vendor = vendor
            self.vendor_gp_box.setTitle(vendor.name)
            self.name.setText(vendor.name or "")
            self.contact_person.setText(vendor.contact_person or "")
            self.phone1.setText(vendor.phone1 or "")
            self.phone2.setText(vendor.phone2 or "")
            self.email.setText(vendor.email or "")
            self.address.setPlainText(vendor.address or "")

    def insert_or_update_vendor(self):
        vendor = self.selected_vendor
        vendor.name = normalize_string(self.name.text())
        vendor.contact_person = normalize_string(self.contact_person.text())
        vendor.phone1 = normalize_string(self.phone1.text())
        vendor.phone2 = normalize_string(self.phone2.text())
        vendor.email = normalize_string(self.email.text())
        vendor.address = normalize_string(self.address.toPlainText())

        if not confirmation(f"You are about to save the {vendor.name}. Are you sure?"):
            return

        success, message = self.controller.save_vendor(vendor)
        show_message(message, "Success" if success else "Error")
        if success:
            self.refresh_data()

    def on_search_text_changed(self, text):
        self.vendors_list.clear()
        filtered_names = self.controller.filter_vendor_names(self.controller.vendors, text)
        for name in filtered_names:
            self.vendors_list.addItem(name)


def normalize_string(s: str) -> str:
    """Normalize a string for comparison: lowercase, trimmed, collapsed spaces."""
    if not s:
        return ''
    s = re.sub(r'\s+', ' ', s.strip())
    return s[0].upper() + s[1:].lower() if len(s) > 0 else ''
