from models.component_suppliers import insert_component_suppliers_to_db
from models.items.vfd_softstarter import get_all_vfds_softstarters, insert_vfd_softstarter_to_db
from models.supplier import get_supplier_by_name


class VFDSoftStarterDataEntryController:
    def get_all_vfd_softstarters(self):
        vfd_softstarters = get_all_vfds_softstarters()
        return vfd_softstarters

    def save_vfd_softstarter(self, vfd_softstarter_details):

        success, vfd_softstarter_id = insert_vfd_softstarter_to_db(
            brand=vfd_softstarter_details["brand"],
            order_number=vfd_softstarter_details["order_number"],
            type=vfd_softstarter_details["type"],
            power=vfd_softstarter_details["power"]
        )
        if not success:
            return False, vfd_softstarter_id

        success, supplier_id = get_supplier_by_name(vfd_softstarter_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=vfd_softstarter_id, supplier_id=supplier_id, price=vfd_softstarter_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ VFD Or SoftStarter Saved successfully"
