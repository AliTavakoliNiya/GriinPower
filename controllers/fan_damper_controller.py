from math import ceil

from controllers.panel_controller import PanelController
from models.motor_model import Motor


class FanDamperController(PanelController):
    """
    Specialized controller for building a fan_damper panel.
    """

    def __init__(self):
        super().__init__("fan_damper")

    def build_panel(self, project_details):
        """
        Main controller for building a fan_damper panel from project specifications.
        """
        # ----------------------- Initialize Motors -----------------------
        damper_config = project_details["damper"]["motors"]["damper"]
        motor_objects = [(Motor(damper_config["power"], usage="Damper"), damper_config["qty"])]

        fan_config = project_details["fan"]["motors"]["fan"]
        fan = Motor(power_kw=fan_config["power"], usage="Fan")
        fan.rpm=fan_config["rpm"]
        fan.brand=fan_config["brand"]
        fan.cooling_method=fan_config["cooling_method"]
        fan.ip_rating=fan_config["ip_rating"]
        fan.efficiency_class=fan_config["efficiency_class"]
        fan.voltage_type=fan_config["voltage_type"]
        fan.thermal_protection=fan_config["thermal_protection"]
        fan.space_heater=fan_config["space_heater"]
        fan.mpcb_qty=0
        fan.mccb_qty=1

        motor_objects.append((fan, fan_config["qty"]))




    # ----------------------- choose electro motor ----------------------------
        # ----------------------- choose electro motor ----------------------------
        # ----------------------- choose electro motor ----------------------------
        # ----------------------- choose electro motor ----------------------------

        # ----------------------- Add Components for Motors -----------------------
        for motor, qty in motor_objects:
            self.choose_contactor(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mpcb(motor, qty)
        for motor, qty in motor_objects:
            self.choose_mccb(motor, qty)

        # ----------------------- Add BiMetal -----------------------


        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        fan_instruments = project_details["fan"]["instruments"]
        damper_instruments = project_details["damper"]["instruments"]
        instruments = {**fan_instruments, **damper_instruments}
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
        if total_motors != 0:
            self.choose_electrical_panel(total_motors)

        # ----------------------- Add instruments -----------------------
        self.choose_instruments(instruments)

        return self.panel

    def choose_instruments(self, instruments):
        """
        Adds instrument entries to the fan_damper panel.
        """
        instrument_specs = {
            "pressure_transmitter": {
                "type": "Pressure Transmitter",
                "specifications": "",
                "price": 2_000_000,
                "usage": ""
            },
            "temperature_transmitter": {
                "type": "Temperature Transmitter",
                "specifications": "",
                "price": 1_800_000,
                "usage": ""
            },
            "bearing_temperature_transmitter": {
                "type": "Bearing Temperature Transmitter",
                "specifications": "",
                "price": 2_000_000,
                "usage": ""
            },
            "bearing_vibration_transmitter": {
                "type": "Bearing Vibration Transmitter",
                "specifications": "",
                "price": 2_000_000,
                "usage": ""
            },
            "proximity_switch": {
                "type": "PROXIMITY SWITCH",
                "specifications": "",
                "price": 1_500_000,
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

    def calculate_instruments_io(self, instruments, total_di, total_ai, di_notes, ai_notes):
        """
        Calculate I/O requirements specific to fan damper instruments
        """
        di_instruments = ["proximity_switch", "bearing_temperature_transmitter", "bearing_vibration_transmitter",
                          "pressure_transmitter", "temperature_transmitter"]
        for instrument in di_instruments:
            qty = instruments[instrument]["qty"]
            if qty > 0:
                total_di += qty  # Each instrument has 1 DI
                di_notes.append(f"{instrument}: {qty} DI")

        return total_di, total_ai
