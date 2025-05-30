import re

from models import Vendor
from models.vendor import get_all_vendors, save_vendor_to_db


class VendorController:
    def __init__(self):
        self.vendors = []  # list of Vendor objects
        self.selected_vendor = None

    def load_vendors(self):
        self.vendors = get_all_vendors()
        return self.vendors

    def select_vendor_by_name(self, name):
        self.selected_vendor = next((v for v in self.vendors if v.name == name), None)
        return self.selected_vendor

    def save_vendor(self, vendor: Vendor):
        # Validate
        if not vendor.name:
            return False, "Name is required"
        if (vendor.phone1 and not vendor.phone1.isdigit()) or (vendor.phone2 and not vendor.phone2.isdigit()):
            return False, "Phone Number is incorrect"
        if vendor.email and not re.match(r"^[\w.-]+@[\w.-]+\.\w+$", vendor.email):
            return False, "Email is incorrect"

        # Save
        if save_vendor_to_db(vendor):
            return True, f"Vendor '{vendor.name}' saved successfully."
        else:
            return False, "Failed to save vendor."

    def filter_vendor_names(self, vendors, filter_text):
        text = filter_text.lower().strip()
        return [v.name for v in vendors if text in v.name.lower()]
