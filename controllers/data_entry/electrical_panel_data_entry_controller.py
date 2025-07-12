from models.component_suppliers import insert_component_suppliers_to_db
from models.items.electrical_panel import get_all_electrical_panel, insert_electrical_panel_to_db
from models.suppliers import get_supplier_by_name


class ElectricalPanelDataEntryController:
    def get_all_electrical_panels(self):
        electrical_panels = get_all_electrical_panel()
        return electrical_panels

    def save_electrical_panel(self, electrical_panel_details):

        success, electrical_panel_id = insert_electrical_panel_to_db(
            brand=electrical_panel_details["brand"],
            order_number=electrical_panel_details["order_number"],
            type=electrical_panel_details["type"],
            width=electrical_panel_details["width"],
            height=electrical_panel_details["height"],
            depth=electrical_panel_details["depth"],
            ip_rating=electrical_panel_details["ip_rating"],
        )
        if not success:
            return False, electrical_panel_id

        success, supplier_id = get_supplier_by_name(electrical_panel_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=electrical_panel_id, supplier_id=supplier_id, price=electrical_panel_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ Saved successfully"
