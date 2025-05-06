from controllers.panel_controller import PanelController
from models.motor_model import Motor


class FreshAirController(PanelController):
    """
    Specialized controller for building a fresh air panel.
    """

    def __init__(self):
        super().__init__("fresh_air")

    def build_panel(self, project_details):
        """
        Main controller for building a fresh air panel from project specifications.
        """
        # ----------------------- Initialize Motors -----------------------
        motors_config = project_details["fresh_air"]["motors"]
        motor_objects = []

        freshair_motor = Motor(motors_config["freshair_motor"]["power"], usage="Fresh Air Motor")
        if motors_config["freshair_motor"]["start_type"] == "VFD":
            # Rules for choosing vfd
            freshair_motor.plc_ai = 1
            freshair_motor.plc_ao = 1
        elif motors_config["freshair_motor"]["start_type"] == "Pneumatic":
            freshair_motor.mpcb_qty = 0
            freshair_motor.mccb_qty = 1
            freshair_motor.relay_1no_1nc_qty = 6
            freshair_motor.plc_do = 2
        motor_objects.append((freshair_motor, motors_config["freshair_motor"]["qty"]))

        fresh_air_flap = Motor(motors_config["fresh_air_flap"]["power"], usage="Fresh Air Flap")
        if motors_config["fresh_air_flap"]["start_type"] == "Pneumatic":
            fresh_air_flap.mpcb_qty = 0
            fresh_air_flap.mccb_qty = 1
            fresh_air_flap.relay_1no_1nc_qty = 6
            fresh_air_flap.plc_do = 2
        elif motors_config["fresh_air_flap"]["start_type"] == "Motorized On/Off":
            fresh_air_flap.contactor_qty = 2
            fresh_air_flap.contactor_aux_contact_qty = 2
            fresh_air_flap.plc_di = 6
            fresh_air_flap.plc_do = 2
            fresh_air_flap.button_qty = 4
            fresh_air_flap.relay_1no_1nc_qty = 5
        elif motors_config["fresh_air_flap"]["start_type"] == "Motorized Gradual ":
            fresh_air_flap.contactor_qty = 2
            fresh_air_flap.contactor_aux_contact_qty = 2
            fresh_air_flap.plc_di = 6
            fresh_air_flap.plc_do = 2
            fresh_air_flap.plc_ai = 1
            fresh_air_flap.plc_ao = 1
            fresh_air_flap.button_qty = 4
            fresh_air_flap.relay_1no_1nc_qty = 5
        motor_objects.append((fresh_air_flap, motors_config["fresh_air_flap"]["qty"]))

        emergency_flap = Motor(motors_config["emergency_flap"]["power"], usage="Emergency Flap")
        if motors_config["fresh_air_flap"]["start_type"] == "Pneumatic":
            emergency_flap.mpcb_qty = 0
            emergency_flap.mccb_qty = 1
            emergency_flap.relay_1no_1nc_qty = 6
            emergency_flap.plc_do = 2
        elif motors_config["fresh_air_flap"]["start_type"] == "Motorized On/Off":
            emergency_flap.contactor_qty = 2
            emergency_flap.contactor_aux_contact_qty = 2
            emergency_flap.plc_di = 6
            emergency_flap.plc_do = 2
            emergency_flap.button_qty = 4
            emergency_flap.relay_1no_1nc_qty = 5
        elif motors_config["fresh_air_flap"]["start_type"] == "Motorized Gradual ":
            emergency_flap.contactor_qty = 2
            emergency_flap.contactor_aux_contact_qty = 2
            emergency_flap.plc_di = 6
            emergency_flap.plc_do = 2
            emergency_flap.plc_ai = 1
            emergency_flap.plc_ao = 1
            emergency_flap.button_qty = 4
            emergency_flap.relay_1no_1nc_qty = 5
        motor_objects.append((emergency_flap, motors_config["emergency_flap"]["qty"]))

        # ----------------------- Add Components for Motors -----------------------
        for motor, qty in motor_objects:
            self.choose_contactor(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mpcb(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mccb(motor, qty)

        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        instruments = project_details["fresh_air"]["instruments"]
        self.calculate_plc_io_requirements(motor_objects, instruments)

        # ----------------------- Add internal wiring -----------------------
        self.choose_internal_signal_wire(motor_objects)
        self.choose_internal_power_wire(motor_objects)

        # ----------------------- Add General Accessories -----------------------
        self.choose_general(motor_objects)

        if project_details["bagfilter"]["touch_panel"] == "None":
            self.choose_general(motor_objects, ["signal_lamp_24v"])

        # ----------------------- Add Cables -----------------------
        length = project_details["cable_dimension"]
        volt = project_details["volt"]

        if length > 0:
            self.choose_signal_cable(motor_objects, length)
            self.choose_power_cable(motor_objects, length, volt)

        # ----------------------- Add Electrical Panel -----------------------
        total_motors = sum(qty for _, qty in motor_objects)
        self.choose_electrical_panel(total_motors)

        # ----------------------- Add instruments -----------------------
        self.choose_instruments(instruments)

        return self.panel

    def choose_instruments(self, instruments):
        """
        Adds instrument entries to the fresh air panel.
        """
        instrument_specs = {
            "proximity_switch": {
                "type": "PROXIMITY SWITCH",
                "specifications": "For flap position detection",
                "price": 1_500_000,
                "usage": "Flap position monitoring"
            },
            "temperature_transmitter": {
                "type": "TEMPERATURE TRANSMITTER",
                "specifications": "For air temperature measurement",
                "price": 3_000_000,
                "usage": "Air temperature monitoring"
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
                    note=f"Usage: {specs['usage']}\nQuantity: {qty}")

    def calculate_instruments_io(self, instruments, total_di, total_ai, di_notes, ai_notes):
        """
        Calculate I/O requirements specific to fresh air instruments
        """
        # Proximity switches use DI
        prox_qty = instruments["proximity_switch"]["qty"]
        if prox_qty > 0:
            total_di += prox_qty
            di_notes.append(f"proximity_switch: {prox_qty} DI")

        # Temperature transmitters use AI
        temp_qty = instruments["temperature_transmitter"]["qty"]
        if temp_qty > 0:
            total_ai += temp_qty
            ai_notes.append(f"temperature_transmitter: {temp_qty} AI")

        return total_di, total_ai
