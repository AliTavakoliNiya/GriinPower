from controllers.panel_controller import PanelController
from models.abs_motor import Motor


class HopperHeaterController(PanelController):
    """Controller for hopper heater panel components."""

    def __init__(self):
        super().__init__("hopper_heater")

    def build_panel(self):
        """
        Main controller for building a hopper heater panel from project specifications.
        """
        # ----------------------- Initialize Motors -----------------------
        motors_config = self.project_details["hopper_heater"]["motors"]
        hopper_heater = Motor(motors_config["elements"]["power"],
                   usage="Hopper Heater",
                   plc_di=4,
                   junction_box_for_speed_qty=4,
                   terminal_4_qty=4 * 8,
                   terminal_6_qty=4 * 10,
                   relay_1no_1nc_qty=2,
                   mpcb_qty=0,
                   mccb_qty=1,
                   button_qty=0,
                   selector_switch_qty=0,
                   signal_lamp_24v_qty=0)
        self.project_details["hopper_heater"]["motors"]["elements"]["motor"] = hopper_heater
        motor_objects = [(hopper_heater, motors_config["elements"]["qty"])]
        motor_objects[0][0].temperature_meter = 2

        # ----------------------- Add Components for Motors -----------------------
        for motor, qty in motor_objects:
            self.choose_contactor(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mccb(motor, qty)

        # ----------------------- Calculate and add PLC I/O requirements -----------------------

        # ----------------------- Add internal wiring -----------------------
        self.choose_internal_signal_wire(motor_objects)
        self.choose_internal_power_wire(motor_objects)

        # ----------------------- Add General Accessories -----------------------
        self.choose_general(motor_objects)

        # ----------------------- Add Cables -----------------------
        self.choose_signal_cable(motor_objects)
        self.choose_power_cable(motor_objects)

        # ----------------------- Add Electrical Panel -----------------------
        total_motors = sum(qty for _, qty in motor_objects)
        if total_motors != 0:
            self.choose_electrical_panel(total_motors)

        # ----------------------- Add instruments -----------------------
        instruments = self.project_details["hopper_heater"]["instruments"]
        self.choose_instruments(instruments)

        return self.panel
