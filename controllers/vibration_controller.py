from math import ceil

from controllers.panel_controller import PanelController
from models.abs_motor import Motor

class VibrationController(PanelController):
    """
    Specialized controller for building a vibration panel.
    """

    def __init__(self):
        super().__init__("vibration")

    def build_panel(self):
        """
        Main controller for building a vibration panel from project specifications.
        """
        # ----------------------- Initialize Motors -----------------------
        motors_config = self.project_details["vibration"]["motors"]
        vibration = Motor(motors_config["vibration"]["power"],
                   usage="Vibration Motor",
                   plc_di=4,
                   junction_box_for_speed_qty=0)
        self.project_details["vibration"]["motors"]["vibration"]["motor"] = vibration
        motor_objects = [(vibration, motors_config["vibration"]["qty"])]

        # ----------------------- Add Components for Motors -----------------------
        for motor, qty in motor_objects:
            self.choose_contactor(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mpcb(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mccb(motor, qty)  # Add MCCB selection

        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        instruments = self.project_details["vibration"]["instruments"]
        self.calculate_plc_io_requirements(motor_objects, instruments)


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
        total_motors = ceil(total_motors)

        if total_motors != 0:
            self.choose_electrical_panel(total_motors)

        return self.panel

