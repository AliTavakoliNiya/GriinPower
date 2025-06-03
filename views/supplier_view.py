import re

from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from controllers.supplier_controller import SupplierController
from models import Supplier
from views.message_box_view import show_message, confirmation


class SupplierEntry(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/supplier_view.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.controller = SupplierController()
        self.selected_supplier = Supplier()

        # Connect signals
        self.search_supplier_field.textChanged.connect(self.on_search_text_changed)
        self.suppliers_list.itemClicked.connect(self.on_supplier_selected)
        self.clear_form.clicked.connect(self.clear_form_btn)
        self.save_supplier.clicked.connect(self.insert_or_update_supplier)

        self.refresh_data()
        self.show()

    def clear_form_btn(self):
        self.selected_supplier = Supplier()
        self.supplier_gp_box.setTitle("New Supplier")
        self.name.clear()
        self.contact_person.clear()
        self.phone1.clear()
        self.phone2.clear()
        self.email.clear()
        self.address.clear()
        self.search_supplier_field.clear()
        self.suppliers_list.clearSelection()

    def refresh_data(self):
        self.clear_form_btn()
        self.suppliers_list.clear()

        success, msg = self.controller.load_suppliers()
        if not success:
            show_message(msg, title="Error")
        for supplier in self.controller.suppliers:
            self.suppliers_list.addItem(supplier.name_c_to_del)

    def on_supplier_selected(self, item):
        supplier = self.controller.select_supplier_by_name(item.text())
        if supplier:
            self.selected_supplier = supplier
            self.supplier_gp_box.setTitle(supplier.name_c_to_del)
            self.name.setText(supplier.name_c_to_del or "")
            self.contact_person.setText(supplier.contact_person or "")
            self.phone1.setText(supplier.phone1 or "")
            self.phone2.setText(supplier.phone2 or "")
            self.email.setText(supplier.email or "")
            self.address.setPlainText(supplier.address or "")

    def insert_or_update_supplier(self):
        supplier = self.selected_supplier
        supplier.name = normalize_string(self.name.text())
        supplier.contact_person = normalize_string(self.contact_person.text())
        supplier.phone1 = normalize_string(self.phone1.text())
        supplier.phone2 = normalize_string(self.phone2.text())
        supplier.email = normalize_string(self.email.text())
        supplier.address = normalize_string(self.address.toPlainText())

        if not confirmation(f"You are about to save the {supplier.name}. Are you sure?"):
            return

        success, message = self.controller.save_supplier(supplier)
        show_message(message, "Success" if success else "Error")
        if success:
            self.refresh_data()

    def on_search_text_changed(self, text):
        self.suppliers_list.clear()
        filtered_names = self.controller.filter_supplier_names(self.controller.suppliers, text)
        for name in filtered_names:
            self.suppliers_list.addItem(name)


def normalize_string(s: str) -> str:
    """Normalize a string for comparison: lowercase, trimmed, collapsed spaces."""
    if not s:
        return ''
    s = re.sub(r'\s+', ' ', s.strip())
    return s[0].upper() + s[1:].lower() if len(s) > 0 else ''
