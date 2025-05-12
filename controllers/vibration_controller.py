from math import ceil

from controllers.panel_controller import PanelController
from models.motor_model import Motor


class VibrationController(PanelController):
    """
    Specialized controller for building a vibration panel.
    """

    def __init__(self):
        super().__init__("vibration")

    def build_panel(self, project_details):
        """
        Main controller for building a vibration panel from project specifications.
        """
        # ----------------------- Initialize Motors -----------------------
        motors_config = project_details["vibration"]["motors"]
        motor_objects = [
            (Motor(motors_config["vibration"]["power"],
                   usage="Vibration Motor",
                   plc_di=4,
                   junction_box_for_speed_qty=0), motors_config["vibration"]["qty"])
        ]

        # ----------------------- Add Components for Motors -----------------------
        for motor, qty in motor_objects:
            self.choose_contactor(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mpcb(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mccb(motor, qty)  # Add MCCB selection

        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        instruments = project_details["vibration"]["instruments"]
        self.calculate_plc_io_requirements(motor_objects, instruments)

        # ----------------------- Add internal wiring -----------------------
        self.choose_internal_signal_wire(motor_objects)
        self.choose_internal_power_wire(motor_objects)

        # ----------------------- Add General Accessories -----------------------
        self.choose_general(motor_objects)

        if project_details["bagfilter"]["touch_panel"] == "None":  # no touch panel required
            self.choose_general(motor_objects, ["signal_lamp_24v"])

        # ----------------------- Add Cables -----------------------
        length = project_details["cable_dimension"]
        volt = project_details["volt"]

        if length > 0:
            self.choose_signal_cable(motor_objects, length)
            self.choose_power_cable(motor_objects, length, volt)

        # ----------------------- Add Electrical Panel -----------------------
        total_motors = sum(qty for _, qty in motor_objects)
        total_motors = ceil(total_motors)

        if total_motors != 0:
            self.choose_electrical_panel(total_motors)

        return self.panel

    def calculate_instruments_io(self, instruments, total_di, total_ai, di_notes, ai_notes):
        """
        Calculate I/O requirements specific to vibration instruments
        """
        # Vibration system currently has no specific instruments
        return total_di, total_ai

    def choose_instruments(self, instruments):
        """
        Adds instrument entries to the vibration panel.
        """
        # Currently no instruments for vibration system
        pass
