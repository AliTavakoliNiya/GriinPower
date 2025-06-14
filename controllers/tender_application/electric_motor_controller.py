from controllers.tender_application.project_session_controller import ProjectSession
from models.items.electric_motor import get_motor_by_spec


class ElectricMotorController():

    def __init__(self):
        self.electrical_specs = ProjectSession().project_electrical_specs

    def calculate_price(self):
        motor = self.electrical_specs["fan"]["motors"]["fan"]
        voltage = self.electrical_specs["project_info"]["l_voltage"]
        brand = motor["brand"]

        success, electric_motor = get_motor_by_spec(
            power=motor["power"],
            rpm=motor["rpm"],
            brand=brand,
            start_type=motor["start_type"],
            cooling_method=motor["cooling_method"],
            ip_rating=motor["ip_rating"],
            efficiency_class=motor["efficiency_class"],
            voltage=voltage,
            painting_ral=motor["painting_ral"],
            thermal_protection=motor["thermal_protection"],
        )
        if success:
            return electric_motor.component_supplier.price, f"{electric_motor.component_supplier.supplier.name}\n{electric_motor.component_supplier.date}",
        elif success == False:
            # show_message(electric_motor, title="Error")
            return 0, ""


