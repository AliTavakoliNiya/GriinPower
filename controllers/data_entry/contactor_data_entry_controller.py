from models.component_suppliers import insert_component_suppliers_to_db
from models.items.contactor import get_all_contactors, insert_contactor_to_db
from models.supplier import get_supplier_by_name


class ContactorDataEntryController:
    def get_all_contactors(self):
        contactors = get_all_contactors()
        return contactors

    def save_contactor(self, contactor_details):

        success, contactor_id = insert_contactor_to_db(
            rated_current=contactor_details["current"],
            coil_voltage=contactor_details["voltage"],
            brand=contactor_details["brand"],
            order_number=contactor_details["order_number"],
        )
        if not success:
            return False, contactor_id

        success, supplier_id = get_supplier_by_name(contactor_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=contactor_id, supplier_id=supplier_id, price=contactor_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ Contactor Saved successfully"
