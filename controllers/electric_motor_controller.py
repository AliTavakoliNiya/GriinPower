from controllers.project_details import ProjectDetails
from models.items.electric_motor_model import get_motor_by_power
from views.message_box_view import show_message


class ElectricMotorController():

    def __init__(self):
        self.project_details = ProjectDetails()

    def calculate_price(self):
        motor = self.project_details["fan"]["motors"]["fan"]
        voltage = self.project_details["project_info"]["l_voltage"]
        brand = motor["brand"]

        success, electric_motor = get_motor_by_power(
            power=motor["power"],
            rpm=motor["rpm"],
            start_type=motor["start_type"],
            cooling_method=motor["cooling_method"],
            ip=motor["ip_rating"],
            efficiency_class=motor["efficiency_class"],
            voltage=voltage,
            painting_ral=motor["painting_ral"],
            thermal_protection=motor["thermal_protection"],
            space_heater=motor["space_heater"]
        )
        if success:
            return electric_motor.component_vendor.price, f"{electric_motor.component_vendor.vendor.name}\n{electric_motor.component_vendor.date}",
        else:
            show_message(electric_motor, title="Error")
            return 0, ""


