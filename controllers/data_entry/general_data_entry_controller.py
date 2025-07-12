from models.component_suppliers import insert_component_suppliers_to_db
from models.items.general import get_all_generals, insert_general_to_db
from models.suppliers import get_supplier_by_name


class GeneralDataEntryController:
    def get_all_generals(self):
        generals = get_all_generals()
        return generals

    def save_general(self, general_details):

        success, general_id = insert_general_to_db(
            brand=general_details["brand"],
            order_number=general_details["order_number"],
            type=general_details["type"],
            specification=general_details["specification"]
        )
        if not success:
            return False, general_id

        success, supplier_id = get_supplier_by_name(general_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=general_id, supplier_id=supplier_id, price=general_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ General Saved successfully"
