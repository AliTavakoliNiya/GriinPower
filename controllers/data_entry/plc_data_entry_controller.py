from models.component_suppliers import insert_component_suppliers_to_db
from models.items.plc import get_all_plcs, insert_plc_to_db
from models.supplier import get_supplier_by_name


class PLCDataEntryController:
    def get_all_plcs(self):
        plcs = get_all_plcs()
        return plcs

    def save_plc(self, plc_details):

        success, plc_id = insert_plc_to_db(
            series=plc_details["series"],
            model=plc_details["model"],
            di_pins=plc_details["di_pins"],
            do_pins=plc_details["do_pins"],
            ai_pins=plc_details["ai_pins"],
            ao_pins=plc_details["ao_pins"],
            has_profinet=plc_details["has_profinet"],
            has_profibus=plc_details["has_profibus"],
            has_hard_wire=plc_details["has_hard_wire"],
            has_mpi=plc_details["has_mpi"],
            brand=plc_details["brand"],
            order_number=plc_details["order_number"],
        )
        if not success:
            return False, plc_id

        success, supplier_id = get_supplier_by_name(plc_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=plc_id, supplier_id=supplier_id, price=plc_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ PLC Saved successfully"
