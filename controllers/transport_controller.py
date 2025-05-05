from math import ceil

from controllers.panel_controller import PanelController
from models.motor_model import Motor


class TransportController(PanelController):
    """
    Specialized controller for building a transport panel.
    """

    def __init__(self):
        super().__init__("transport")

    def build_panel(self, project_details):
        """
        Main controller for building a transport panel from project specifications.
        """
        # ----------------------- Initialize Motors -----------------------
        motors_config = project_details["transport"]["motors"]
        motor_objects = [
            (Motor(motors_config["rotary"]["power"], usage="Rotary"),
             motors_config["rotary"]["qty"]),
            (Motor(motors_config["telescopic_chute"]["power"],
                   usage="Telescopic Chute",
                   relay_1no_1nc_qty=5,
                   relay_2no_2nc_qty=2,
                   plc_di=7,
                   plc_do=2),
             motors_config["telescopic_chute"]["qty"]),
            (Motor(motors_config["slide_gate"]["power"],
                   usage="Slide Gate",
                   relay_1no_1nc_qty=5,
                   relay_2no_2nc_qty=2,
                   plc_di=7,
                   plc_do=2),
             motors_config["slide_gate"]["qty"]),
            (Motor(motors_config["screw1"]["power"], usage="Screw1"),
             motors_config["screw1"]["qty"]),
            (Motor(motors_config["screw2"]["power"], usage="Screw2"),
             motors_config["screw2"]["qty"])
        ]

        # ----------------------- Add Components for Motors -----------------------
        for motor, qty in motor_objects:
            self.choose_contactor(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mpcb(motor, qty)

        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        instruments = project_details["transport"]["instruments"]
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
        total_motors += sum(0.5 * qty for motor, qty in motor_objects if motor.usage == "Telescopic Chute")
        total_motors += sum(0.5 * qty for motor, qty in motor_objects if motor.usage == "Slide Gate")
        total_motors = ceil(total_motors)

        if total_motors != 0:
            self.choose_electrical_panel(total_motors)

        # ----------------------- Add instruments -----------------------
        self.choose_instruments(instruments)

        return self.panel

    def choose_instruments(self, instruments):
        """
        Adds instrument entries to the transport panel.
        """
        instrument_specs = {
            "speed_detector": {
                "type": "SPEED DETECTOR",
                "specifications": "",
                "price": 2_000_000,
                "usage": ""
            },
            "proximity_switch": {
                "type": "PROXIMITY SWITCH",
                "specifications": "",
                "price": 1_500_000,
                "usage": ""
            },
            "level_switch_bin": {
                "type": "LEVEL SWITCH BIN",
                "specifications": "",
                "price": 1_800_000,
                "usage": ""
            },
            "level_transmitter": {
                "type": "LEVEL TRANSMITTER",
                "specifications": "",
                "price": 5_000_000,
                "usage": ""
            }
        }

        for instrument_name, specs in instrument_specs.items():
            qty = instruments[instrument_name]["qty"]
            brand = instruments[instrument_name]["brand"]
            if qty > 0:
                self.add_to_panel(
                    type_=specs["type"],
                    brand=brand if brand else "-",
                    specifications=f"Instrument: {specs['specifications']}",
                    quantity=qty,
                    price=specs["price"],
                    note=f"Usage: {specs['usage']}\nQuantity: {qty}"
                )
