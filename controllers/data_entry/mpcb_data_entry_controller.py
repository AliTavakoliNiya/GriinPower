from models.component_suppliers import insert_component_suppliers_to_db
from models.items.mpcb import get_all_mpcbs, insert_mpcb_to_db
from models.supplier import get_supplier_by_name


class MPCBDataEntryController:
    def get_all_mpcbs(self):
        mpcbs = get_all_mpcbs()
        return mpcbs

    def save_mpcb(self, mpcb_details):

        success, mpcb_id = insert_mpcb_to_db(
            brand=mpcb_details["brand"],
            order_number=mpcb_details["order_number"],
            min_current=mpcb_details["min_current"],
            max_current=mpcb_details["max_current"],
            breaking_capacity=mpcb_details["breaking_capacity"],
            trip_class=mpcb_details["trip_class"]
        )
        if not success:
            return False, mpcb_id

        success, supplier_id = get_supplier_by_name(mpcb_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=mpcb_id, supplier_id=supplier_id, price=mpcb_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ MPCB Saved successfully"
