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

        if not success or not electric_motor:
            return [{"Title": "Electric Motor", "Price": 0, "Note": "Not Found", "brands": {}}]
        else:
            return electric_motor

