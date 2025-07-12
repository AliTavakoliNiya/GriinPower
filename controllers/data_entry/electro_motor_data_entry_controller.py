from models.component_suppliers import insert_component_suppliers_to_db
from models.items.electric_motor import get_all_motors, insert_motor_to_db
from models.suppliers import get_supplier_by_name


class ElectroMotorDataEntryController:

    def get_all_motors(self):
        motors = get_all_motors()
        return motors

    def save_motor(self, motor_details):

        success, motor_id = insert_motor_to_db(
            power=motor_details["power"],
            rpm=motor_details["rpm"],
            voltage=motor_details["voltage"],
            brand=motor_details["brand"],
            start_type=motor_details["start_type"],
            cooling_method=motor_details["cooling_method"],
            ip_rating=motor_details["ip_rating"],
            efficiency_class=motor_details["efficiency_class"],
            painting_ral=motor_details["painting_ral"],
            thermal_protection=motor_details["thermal_protection"],
            is_official=motor_details["is_official"],
            is_routine=motor_details["is_routine"]
        )
        if not success:
            return False, motor_id

        success, supplier_id = get_supplier_by_name(motor_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=motor_id, supplier_id=supplier_id, price=motor_details["price"], currency=motor_details["currency"]
        )
        if not success:
            return False, result

        return True, "✅ Electro Motor Saved successfully"

