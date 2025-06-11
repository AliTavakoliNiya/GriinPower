from math import ceil

from controllers.tender_application.panel_controller import PanelController
from models.abs_motor import Motor


class TransportController(PanelController):
    """
    Specialized controller for building a transport panel.
    """

    def __init__(self):
        super().__init__("transport")

    def build_panel(self):
        """
        Main controller for building a transport panel from tender_application specifications.
        """
        # ----------------------- Initialize Motors -----------------------
        motors_config = self.electrical_specs["transport"]["motors"]

        rotary = Motor(motors_config["rotary"]["power"], usage="Rotary")
        rotary.current = self.calculate_motor_current(power=rotary.power)
        self.electrical_specs["transport"]["motors"]["rotary"]["motor"] = rotary

        telescopic_chute = Motor(motors_config["telescopic_chute"]["power"],
                   usage="Telescopic Chute",
                   relay_1no_1nc_qty=5,
                   relay_2no_2nc_qty=2,
                   plc_di=7,
                   plc_do=2)
        telescopic_chute.current = self.calculate_motor_current(power=telescopic_chute.power)
        self.electrical_specs["transport"]["motors"]["telescopic_chute"]["motor"] = telescopic_chute

        slide_gate = Motor(motors_config["slide_gate"]["power"],
                   usage="Slide Gate",
                   relay_1no_1nc_qty=5,
                   relay_2no_2nc_qty=2,
                   plc_di=7,
                   plc_do=2)
        slide_gate.current = self.calculate_motor_current(power=slide_gate.power)
        self.electrical_specs["transport"]["motors"]["slide_gate"]["motor"] = slide_gate

        screw1 = Motor(motors_config["screw1"]["power"], usage="Screw1")
        screw1.current = self.calculate_motor_current(power=screw1.power)
        self.electrical_specs["transport"]["motors"]["screw1"]["motor"] = screw1

        screw2 = Motor(motors_config["screw2"]["power"], usage="Screw2")
        screw2.current = self.calculate_motor_current(power=screw2.power)
        self.electrical_specs["transport"]["motors"]["screw2"]["motor"] = screw2

        motor_objects = [
                            (rotary, motors_config["rotary"]["qty"]),
                            (telescopic_chute, motors_config["telescopic_chute"]["qty"]),
                            (slide_gate, motors_config["slide_gate"]["qty"]),
                            (screw1, motors_config["screw1"]["qty"]),
                            (screw2, motors_config["screw2"]["qty"])
                        ]

        # ----------------------- Add Components for Motors -----------------------
        for motor, qty in motor_objects:
            self.choose_contactor(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mpcb(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mccb(motor, qty)
        for motor, qty in motor_objects:
            self.choose_bimetal(motor, qty)

        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        instruments = self.electrical_specs["transport"]["instruments"]
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
        total_motors += sum(0.5 * qty for motor, qty in motor_objects if motor.usage == "Telescopic Chute")
        total_motors += sum(0.5 * qty for motor, qty in motor_objects if motor.usage == "Slide Gate")
        total_motors = ceil(total_motors)

        if total_motors != 0:
            self.choose_electrical_panel(total_motors)

        # ----------------------- Add instruments -----------------------
        self.choose_instruments(instruments)

        return self.panel

