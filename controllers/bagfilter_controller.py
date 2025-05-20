import math
from math import ceil

from controllers.panel_controller import PanelController
from controllers.project_details import ProjectDetails
from models.abs_motor import Motor
from models.item_price_model import get_price
from models.items.general_model import get_general_by_name
from models.items.mccb_model import get_mccb_by_motor_power


class BagfilterController(PanelController):
    """
    Specialized controller for bagfilter panel.
    """

    def __init__(self):
        super().__init__("bagfilter")
        self.project_details = ProjectDetails()
        self.panel = {
                    "type": [],
                    "brand": [],
                    "reference_number": [],
                    "specifications": [],
                    "quantity": [],
                    "price": [],
                    "total_price": [],
                    "last_price_update": [],
                    "note": []
                     }

    def build_panel(self):
        """
        Main controller for building a bagfilter from project specifications.
        """

        # ----------------------- Add Components for Motors -----------------------
        self.choose_mccb()

        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        # self.calculate_plc_io_requirements()

        # # ----------------------- Add internal wiring -----------------------
        # self.choose_internal_signal_wire(motor_objects)
        # self.choose_internal_power_wire(motor_objects)
        #
        # # ----------------------- Add General Accessories -----------------------
        # self.choose_general(motor_objects)
        #
        # if self.project_details["bagfilter"]["touch_panel"] == "None":  # no touch panel required
        #     self.choose_general(motor_objects, ["signal_lamp_24v"])
        #
        # # ----------------------- Add Cables -----------------------
        # self.choose_signal_cable(motor_objects)
        # self.choose_power_cable(motor_objects)
        #
        # # ----------------------- Add Electrical Panel -----------------------
        # total_motors = sum(qty for _, qty in motor_objects)
        # total_motors += sum(0.5 * qty for motor, qty in motor_objects if motor.usage == "Telescopic Chute")
        # total_motors += sum(0.5 * qty for motor, qty in motor_objects if motor.usage == "Slide Gate")
        # total_motors = ceil(total_motors)
        #
        # if total_motors != 0:
        #     self.choose_electrical_panel(total_motors)
        #
        # # ----------------------- Add instruments -----------------------
        # self.choose_instruments(instruments)

        return self.panel

    def choose_mccb(self):

        # Calculate total power of all motors
        total_power = 0

        for section in self.project_details.values():
            motors = section.get("motors", {})
            for motor_name, motor_data in motors.items():
                try:
                    qty = motor_data.get("qty", 0)
                    power = motor_data.get("power", 0)
                    total_power += qty * power
                except:
                    pass

        if total_power == 0:
            return


        mccb = get_mccb_by_motor_power(total_power)
        if mccb.item_id:
            price_item = get_price(mccb.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""

        self.add_to_panel(
            type=f"MCCB FOR BAGFILTER",
            brand=brand,
            reference_number=mccb.mccb_reference,
            specifications=f"For Total Power: {mccb.p_kw} KW\nCurrent: {mccb.i_a} A",
            quantity=1,
            price=price,
            last_price_update=effective_date,
            note=f"Total Power: {total_power} KW"
        )


