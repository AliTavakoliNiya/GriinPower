import re

from models import Supplier
from models.supplier import get_all_suppliers, save_supplier_to_db


class SupplierController:
    def __init__(self):
        self.suppliers = []  # list of Supplier objects
        self.selected_supplier = None

    def load_suppliers(self):
        success, suppliers = get_all_suppliers()
        if success:
            self.suppliers = suppliers
            return True, ""
        else:
            return False, suppliers

    def select_supplier_by_name(self, name):
        self.selected_supplier = next((v for v in self.suppliers if v.name_c_to_del == name), None)
        return self.selected_supplier

    def save_supplier(self, supplier: Supplier):
        # Validate
        if not supplier.name:
            return False, "Name is required"
        if (supplier.phone1 and not supplier.phone1.isdigit()) or (supplier.phone2 and not supplier.phone2.isdigit()):
            return False, "Phone Number is incorrect"
        if supplier.email and not re.match(r"^[\w.-]+@[\w.-]+\.\w+$", supplier.email):
            return False, "Email is incorrect"

        # Save
        if save_supplier_to_db(supplier):
            return True, f"Supplier '{supplier.name}' saved successfully."
        else:
            return False, "Failed to save supplier."

    def filter_supplier_names(self, suppliers, filter_text):
        text = filter_text.lower().strip()
        return [v.name_c_to_del for v in suppliers if text in v.name_c_to_del.lower()]
