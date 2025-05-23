import copy

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
        damper.current = self.calculate_motor_current(power=damper.power)
        self.project_details["damper"]["motors"]["damper"]["motor"] = damper

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
        fan = Motor(power=fan_config["power"], usage="Fan")
        if self.project_details["fan"]["motors"]["fan"]["voltage_type"] == "LV":
            fan_voltage = self.project_details["project_info"]["project_l_voltage"]
        else:
            fan_voltage = self.project_details["project_info"]["project_m_voltage"]
        fan.current = self.calculate_motor_current(power=fan.power, volt=fan_voltage)

        self.project_details["fan"]["motors"]["fan"]["motor"] = fan
        fan.start_type=fan_config["start_type"]
        if fan_config["start_type"] == "Delta/Star":
            fan.contactor_qty = 3
            fan.contactor_aux_contact_qty = 2
            fan.plc_di = 6
            fan.plc_do = 2
            fan.button_qty = 4
            fan.relay_1no_1nc_qty = 5
        elif fan_config["start_type"] == "VFD":
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

        # ----------------------- Add Components for Motors -----------------------
        self.choose_contactor(damper, damper_config["qty"])
        self.choose_contactor(fan, fan_config["qty"])

        self.choose_mpcb(damper, damper_config["qty"])
        self.choose_mpcb(fan, fan_config["qty"])

        self.choose_mccb(damper, damper_config["qty"])
        fan_with_half_power = copy.deepcopy(fan)
        fan_with_half_power.power = fan_with_half_power.power / 2 if fan_config["start_type"] == "Delta/Star" else fan_with_half_power.power
        self.choose_mccb(fan_with_half_power, fan_config["qty"])

        self.choose_bimetal(damper, damper_config["qty"])
        self.choose_bimetal(fan, fan_config["qty"])

        # ----------------------- Add BiMetal -----------------------


        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        fan_instruments = self.project_details["fan"]["instruments"]
        damper_instruments = self.project_details["damper"]["instruments"]
        instruments = {**fan_instruments, **damper_instruments}
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
        if total_motors != 0:
            self.choose_electrical_panel(total_motors)

        # ----------------------- Add instruments -----------------------
        self.choose_instruments(instruments)

        return self.panel
