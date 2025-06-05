from models.component_suppliers import insert_component_suppliers_to_db
from models.items.instrument import get_all_instruments, insert_instrument_to_db
from models.supplier import get_supplier_by_name


class InstrumentDataEntryController:
    def get_all_instruments(self):
        instruments = get_all_instruments()
        return instruments

    def save_instrument(self, instrument_details):

        success, instrument_id = insert_instrument_to_db(
            brand=instrument_details["brand"],
            order_number=instrument_details["order_number"],
            type=instrument_details["type"],
            hart_comminucation=instrument_details["hart_comminucation"],
        )
        if not success:
            return False, instrument_id

        success, supplier_id = get_supplier_by_name(instrument_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=instrument_id, supplier_id=supplier_id, price=instrument_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ Instrument Saved successfully"
