from controllers.project_details import ProjectDetails
from models.item_price_model import get_price
from models.items.electric_motor_model import get_electric_motor_by_specs


class ElectricMotorController():

    def __init__(self):
        self.project_details = ProjectDetails()

    def calculate_price(self):
        motor = self.project_details["fan"]["motors"]["fan"]
        voltage = self.project_details["project_info"]["project_l_voltage"]
        brand   = motor["brand"]
        electric_motor = get_electric_motor_by_specs(power=motor["power"],
                                                     rpm=motor["rpm"],
                                                     start_type=motor["start_type"],
                                                     cooling_method=motor["cooling_method"],
                                                     ip=motor["ip_rating"],
                                                     efficiency_class=motor["efficiency_class"],
                                                     voltage=voltage,
                                                     painting_ral=motor["painting_ral"],
                                                     thermal_protection=motor["thermal_protection"],
                                                     space_heater=motor["space_heater"])
        price_item = get_price(electric_motor.item_id, brand)
        price = price_item.price if price_item.price else 0
        effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
        return (price, effective_date)
