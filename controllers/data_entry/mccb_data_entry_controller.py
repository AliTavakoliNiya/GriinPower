from models.component_suppliers import insert_component_suppliers_to_db
from models.items.mccb import get_all_mccbs, insert_mccb_to_db
from models.supplier import get_supplier_by_name


class MCCBDataEntryController:
    def get_all_mccbs(self):
        mccbs = get_all_mccbs()
        return mccbs

    def save_mccb(self, mccb_details):

        success, mccb_id = insert_mccb_to_db(
            rated_current=mccb_details["current"],
            breaking_capacity=mccb_details["breaking_capacity"],
            brand=mccb_details["brand"],
            order_number=mccb_details["order_number"],
        )
        if not success:
            return False, mccb_id

        success, supplier_id = get_supplier_by_name(mccb_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=mccb_id, supplier_id=supplier_id, price=mccb_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ MCCB Saved successfully"
