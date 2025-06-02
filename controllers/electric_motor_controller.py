from controllers.project_details import ProjectDetails
from models.items.electric_motor import get_motor
from views.message_box_view import show_message


class ElectricMotorController():

    def __init__(self):
        self.project_details = ProjectDetails()

    def calculate_price(self):
        motor = self.project_details["fan"]["motors"]["fan"]
        voltage = self.project_details["project_info"]["l_voltage"]
        brand = motor["brand"]

        success, electric_motor = get_motor(
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
            show_message(electric_motor, title="Error")
            return 0, ""


