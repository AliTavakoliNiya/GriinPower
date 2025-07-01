from models.component_suppliers import insert_component_suppliers_to_db
from models.items.bimetal import get_all_bimetals, insert_bimetal_to_db
from models.supplier import get_supplier_by_name


class BimetalDataEntryController:
    def get_all_bimetals(self):
        bimetals = get_all_bimetals()
        return bimetals

    def save_bimetal(self, bimetal_details):

        success, bimetal_id = insert_bimetal_to_db(
            brand=bimetal_details["brand"],
            order_number=bimetal_details["order_number"],
            min_current=bimetal_details["min_current"],
            max_current=bimetal_details["max_current"],
            _class=bimetal_details["class"],
            tripping_threshold=bimetal_details["tripping_threshold"]
        )
        if not success:
            return False, bimetal_id

        success, supplier_id = get_supplier_by_name(bimetal_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=bimetal_id, supplier_id=supplier_id, price=bimetal_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ Bimetal Saved successfully"
