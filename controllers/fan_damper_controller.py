from math import ceil

from controllers.panel_controller import PanelController
from models.abs_motor import Motor


class FanDamperController(PanelController):
    """
    Specialized controller for building a fan_damper panel.
    """

    def __init__(self):
        super().__init__("fan_damper")

    def build_panel(self):
        """
        Main controller for building a fan_damper panel from project specifications.
        """
        # ----------------------- Initialize Motors -----------------------
        damper_config = self.project_details["damper"]["motors"]["damper"]
        damper = Motor(damper_config["power"], usage="Damper")
        if damper_config["start_type"] == "Pneumatic":
            damper.mpcb_qty = 0
            damper.mccb_qty = 1
            damper.relay_1no_1nc_qty = 6
            damper.plc_do = 2
        elif damper_config["start_type"] == "Motorized On/Off":
            damper.contactor_qty = 2
            damper.contactor_aux_contact_qty = 2
            damper.plc_di = 6
            damper.plc_do = 2
            damper.button_qty = 4
            damper.relay_1no_1nc_qty = 5
        elif damper_config["start_type"] == "Motorized Gradual ":
            damper.contactor_qty = 2
            damper.contactor_aux_contact_qty = 2
            damper.plc_di = 6
            damper.plc_do = 2
            damper.plc_ai = 1
            damper.plc_ao = 1
            damper.button_qty = 4
            damper.relay_1no_1nc_qty = 5
        motor_objects = [(damper, damper_config["qty"])]

        fan_config = self.project_details["fan"]["motors"]["fan"]
        fan = Motor(power_kw=fan_config["power"], usage="Fan")
        fan.starting_method=fan_config["starting_method"]
        if fan_config["starting_method"] == "Delta/Star":
            fan.contactor_qty = 2
            fan.contactor_aux_contact_qty = 2
            fan.plc_di = 6
            fan.plc_do = 2
            fan.button_qty = 4
            fan.relay_1no_1nc_qty = 5
        elif fan_config["starting_method"] == "VFD":
            fan.plc_ai = 1
            fan.plc_ao = 1


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
        fan_instruments = self.project_details["fan"]["instruments"]
        damper_instruments = self.project_details["damper"]["instruments"]
        instruments = {**fan_instruments, **damper_instruments}
        # Create a copy with "bearing_" removed from keys
        instruments_cloned = {
            key.replace("bearing_", ""): value for key, value in instruments.items()
        }
        self.calculate_plc_io_requirements(motor_objects, instruments_cloned)

        # ----------------------- Add internal wiring -----------------------
        self.choose_internal_signal_wire(motor_objects)
        self.choose_internal_power_wire(motor_objects)

        # ----------------------- Add General Accessories -----------------------
        self.choose_general(motor_objects)

        if self.project_details["bagfilter"]["touch_panel"] == "None":  # no touch panel required
            self.choose_general(motor_objects, ["signal_lamp_24v"])

        # ----------------------- Add Cables -----------------------
        self.choose_signal_cable(motor_objects)
        self.choose_power_cable(motor_objects)

        # ----------------------- Add Electrical Panel -----------------------
        total_motors = sum(qty for _, qty in motor_objects)
        if total_motors != 0:
            self.choose_electrical_panel(total_motors)

        # ----------------------- Add instruments -----------------------
        self.choose_instruments(instruments)

        return self.panel
