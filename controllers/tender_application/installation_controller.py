import re
from collections import defaultdict
from math import sqrt

from config import COSNUS_PI, ETA
from controllers.tender_application.panel_controller import PanelController
from models.items.electrical_panel import get_electrical_panel_by_spec
from models.items.general import get_general_by_spec
from models.items.wire_cable import get_wire_cable_by_spec


class InstallationController(PanelController):
    """
    Specialized controller for bagfilter panel.
    """


    def __init__(self):
        super().__init__("installation")

    def build_panel(self):
        """
                Main controller for building installation from tender_application specifications.
        """

        instruments = self.electrical_specs["bagfilter"]["instruments"]
        for instrument_name, properties in instruments.items():
            qty = properties["qty"]
            if qty == 0:
                continue


        # calculate n_valves and n_airtanks
        result = []
        # Split string into parts inside and outside parentheses
        parts = re.split(r'(\(.*?\))', self.electrical_specs["bagfilter"]["order"])

        for part in parts:
            if part.startswith('(') and part.endswith(')'):
                # Inside parentheses - extract decimal numbers
                nums = re.findall(r'\d+\.\d+|\d+', part)
                result.extend(nums)
            else:
                # Outside parentheses - replace 'x' with '.' and remove non-digit/dot
                cleaned = part.replace('x', '.')
                cleaned = re.sub(r'[^\d\.]', '', cleaned)
                # split by dots
                nums = [p for p in cleaned.split('.') if p]
                result.extend(nums)

        self.n_valves = 0
        self.n_airtank = 0
        if self.electrical_specs["bagfilter"]["type"] == "Griin/China":  # EX: 8.96x5.(2.7m).10
            self.n_valves = int(result[2])  # ~ compartments ~ jacks
            bags = int(result[1])
            if bags >= 128:
                self.n_airtank = 2
            elif bags >= 64 and self.n_valves >= 6:
                self.n_airtank = 2
            elif bags <= 96 and self.n_valves <= 5:
                self.n_airtank = 1
            else:
                self.n_airtank = 0

        if self.electrical_specs["bagfilter"]["type"] == "BETH":  # 6.78x2.3.10
            n_valve_per_airtank = int(result[0])
            self.n_airtank = int(result[2])
            self.n_valves = n_valve_per_airtank * self.n_airtank

        # calculates n_motors
        self.total_motors_qty = 0
        self.total_instruments = 0
        for section in self.electrical_specs.values():
            motors = section.get("motors", {})
            instruments = section.get("instruments", {})
            for motor_name, motor_data in motors.items():
                try:
                    qty = motor_data.get("qty", 0)
                    self.total_motors_qty += qty
                except Exception:
                    pass
            for instrument_name, instrument_data in instruments.items():
                try:
                    if instrument_name == "ptc" or instrument_name == "vibration_transmitter":
                        continue # skip this 2 instruments
                    qty  = instrument_data.get("qty", 0)
                    self.total_instruments += qty
                except Exception:
                    pass

        if self.n_airtank <= 2:
            self.ladder_size = self.tray_size = 200  # mm
        elif self.n_airtank <= 4:
            self.ladder_size = self.tray_size = 300  # mm
        else:
            self.ladder_size = self.tray_size = 400  # mm

        self.ladder_length = round(self.electrical_specs["installation"]["height"] * 1.5, 2)  # ~ ladder_cover_length
        self.tray_length = round(self.electrical_specs["installation"]["width"] * 1.5, 2)

        self.choose_lcb()
        self.choose_jb()
        self.choose_gland_valvecable_flexible_conduit()
        self.choose_signal_cable_to_airtank()
        self.choose_signal_cable_to_motors()
        self.choose_power_cable_to_motors()
        self.choose_ladder_and_cover()
        self.choose_ladder_connector_and_screw()
        self.choose_tray_and_cover()
        self.choose_tray_connector_and_screw()
        self.choose_supports()
        self.choose_tray_riser()
        self.choose_cableshow_cabletrap_cabletag()
        return self.panel

    def choose_lcb(self):
        motors_lcb = {"Damper": 1 * self.electrical_specs["damper"]["motors"]["damper"]["qty"],
                      "Fan": 1 * self.electrical_specs["fan"]["motors"]["fan"]["qty"],
                      "Rotary": 1 * self.electrical_specs["transport"]["motors"]["rotary"]["qty"],
                      "Screw1": 1 * self.electrical_specs["transport"]["motors"]["screw1"]["qty"],
                      "Screw2": 1 * self.electrical_specs["transport"]["motors"]["screw2"]["qty"],
                      "Slide Gate": 1 * self.electrical_specs["transport"]["motors"]["slide_gate"]["qty"],
                      "Telescopic Chute": 1 * self.electrical_specs["transport"]["motors"]["telescopic_chute"]["qty"],
                      "Vibration": 0,
                      "Fresh Air": 1 * self.electrical_specs["fresh_air"]["motors"]["freshair_motor"]["qty"],
                      "Fresh Air Flap": 1 * self.electrical_specs["fresh_air"]["motors"]["fresh_air_flap"]["qty"],
                      "Emergency Air Flap": 1 * self.electrical_specs["fresh_air"]["motors"]["emergency_flap"]["qty"],
                      "Hopper Heater": 4 * self.electrical_specs["hopper_heater"]["motors"]["elements"]["qty"],
                      }

        total_lcb_for_speed_qty = sum(motors_lcb.values())
        notes = "\n".join(f"{qty}x{motor}" for motor, qty in motors_lcb.items() if qty > 0)

        success, lcb = get_electrical_panel_by_spec(type="Local Box")
        if success:
            self.add_to_panel(
                type="Local Box",
                brand=lcb['brand'],
                order_number=lcb["order_number"],
                specifications=f"{lcb['width']}mm x {lcb['height']}mm x {lcb['depth']}mm",
                quantity=total_lcb_for_speed_qty,
                price=lcb['price'],
                last_price_update=f"{lcb['supplier_name']}\n{lcb['date']}",
                note=notes
            )
        else:
            self.add_to_panel(
                type="Local Box",
                brand="",
                order_number="",
                specifications="",
                quantity=total_lcb_for_speed_qty,
                price=0,
                last_price_update="❌ Local Box not found",
                note=notes
            )

    def choose_jb(self):

        success, jb = get_electrical_panel_by_spec(type="Junction Box", width=200, height=200, depth=120)
        if success:
            self.add_to_panel(
                type="Junction Box",
                brand=jb['brand'],
                order_number=jb["order_number"],
                specifications=f"200mm x 200mm x 120mm",
                quantity=self.total_motors_qty,
                price=jb['price'],
                last_price_update=f"{jb['supplier_name']}\n{jb['date']}",
                note=""
            )
        else:
            self.add_to_panel(
                type="Junction Box",
                brand="",
                order_number="",
                specifications=f"200mm x 200mm x 120mm",
                quantity=self.total_motors_qty,
                price=0,
                last_price_update="❌ Junction Box not found",
                note=""
            )

        success, jb = get_electrical_panel_by_spec(type="Junction Box", width=100, height=100, depth=60)
        if success:
            self.add_to_panel(
                type="Junction Box",
                brand=jb['brand'],
                order_number=jb["order_number"],
                specifications=f"100mm x 100mm x 60mm",
                quantity=self.total_instruments,
                price=jb['price'],
                last_price_update=f"{jb['supplier_name']}\n{jb['date']}",
                note=""
            )
        else:
            self.add_to_panel(
                type="Junction Box",
                brand="",
                order_number="",
                specifications=f"100mm x 100mm x 60mm",
                quantity=self.total_instruments,
                price=0,
                last_price_update="❌ Junction Box not found",
                note=""
            )

    def choose_gland_valvecable_flexible_conduit(self):

        if self.n_valves == 0 or self.n_airtank == 0:
            return

        # choose gland for valves
        success, gland = get_general_by_spec("Gland", specification="PG16")
        if success:
            self.add_to_panel(
                type="Gland",
                brand=gland["brand"],
                order_number="",
                specifications="PG16",
                quantity=self.n_valves * 2 + self.total_instruments,
                price=gland["price"],
                last_price_update=f"{gland.get('supplier_name', '')}\n{gland.get('date', '')}",
                note=f"{self.n_valves} Valves and {self.total_instruments} Instruments"
            )
        else:
            self.add_to_panel(
                type="Gland",
                brand="",
                order_number="",
                specifications="PG16",
                quantity=self.n_valves * 2 + self.total_instruments,
                price=0,
                last_price_update=f"❌ Gland not found",
                note=f"{self.n_valves} Valves and {self.total_instruments} Instruments")

        # choose gland for airtank
        success, gland = get_general_by_spec("Gland", specification="PG21")
        if success:
            self.add_to_panel(
                type="Gland",
                brand=gland["brand"],
                order_number="",
                specifications="PG21",
                quantity=self.n_airtank * 2 + self.total_instruments * 4,
                price=gland["price"],
                last_price_update=f"{gland.get('supplier_name', '')}\n{gland.get('date', '')}",
                note=f"{self.n_airtank} Air Tank and {self.total_instruments} Instruments"
            )
        else:
            self.add_to_panel(
                type="Gland",
                brand="",
                order_number="",
                specifications="PG21",
                quantity=self.n_airtank * 2 + self.total_instruments * 4,
                price=0,
                last_price_update=f"❌ Gland not found",
                note=f"{self.n_airtank} Air Tank and {self.total_instruments} Instruments"
            )

        # choose cable 3x1.5 for valves
        success, cable = get_wire_cable_by_spec("Cable", 3, 1.5)
        if success:
            self.add_to_panel(
                type="Valve Cable",
                brand=cable["brand"],
                order_number="",
                specifications=f"{cable['l_number']}x{cable['l_size']}mm²",
                quantity=self.n_valves * 2,
                price=cable["price"],
                last_price_update=f"{cable.get('supplier_name', '')}\n{cable.get('date', '')}",
                note=f"{self.n_valves} Valves"
            )
        else:
            self.add_to_panel(
                type="Valve Cable",
                brand="",
                order_number="",
                specifications="",
                quantity=self.n_valves * 2,
                price=0,
                last_price_update=f"❌ Cable not found",
                note=f"{self.n_valves} Valves"
            )

        # flexible conduit
        success, conduit = get_wire_cable_by_spec("FlexibleConduit", 1)
        if success:
            self.add_to_panel(
                type="Flexible Conduit",
                brand=conduit["brand"],
                order_number="",
                specifications=f"{conduit['l_number']}x{conduit['l_size']}mm²",
                quantity=self.n_valves * 2 + self.total_instruments * 2,
                price=conduit["price"],
                last_price_update=f"{conduit.get('supplier_name', '')}\n{conduit.get('date', '')}",
                note=f"{self.n_valves} Valves  and {self.total_instruments} Instruments"
            )
        else:
            self.add_to_panel(
                type="Flexible Conduit",
                brand="",
                order_number="",
                specifications="",
                quantity=self.n_valves * 2 + self.total_instruments * 2,
                price=0,
                last_price_update=f"❌ Flexible Conduit not found",
                note=f"{self.n_valves} Valves  and {self.total_instruments} Instruments"
            )

        # flexible conduit Fixer
        success, conduit_fixer = get_general_by_spec("Flexible Conduit Fixer")
        if success:
            self.add_to_panel(
                type="Flexible Conduit Fixer",
                brand=conduit_fixer["brand"],
                order_number="",
                quantity= self.total_instruments * 2,
                price=conduit_fixer["price"],
                last_price_update=f"{conduit_fixer.get('supplier_name', '')}\n{conduit_fixer.get('date', '')}",
                note=f"For {self.total_instruments} Instruments"
            )
        else:
            self.add_to_panel(
                type="Flexible Conduit Fixer",
                brand="",
                order_number="",
                specifications="",
                quantity= self.total_instruments * 2,
                price=0,
                last_price_update=f"❌ Flexible Conduit Fixer not found",
                note=f"For {self.total_instruments} Instruments"
            )

    # signal cable to air tanks
    def choose_signal_cable_to_airtank(self):
        width = self.electrical_specs["installation"]["width"]
        height = self.electrical_specs["installation"]["height"]
        depth = self.electrical_specs["installation"]["depth"]
        ccr = self.electrical_specs["installation"]["ccr"]

        total_length = width + height + depth + ccr
        if total_length == 0 or width == 0 or height == 0 or depth == 0:
            return

        # choose cable
        success, cable = get_wire_cable_by_spec("Cable", 10, 1.5)
        if success:
            self.add_to_panel(
                type="Signal Cable To Airtanks",
                brand=cable["brand"],
                order_number="",
                specifications=f"{cable['l_number']}x{cable['l_size']}mm²",
                quantity=total_length,
                price=cable["price"],
                last_price_update=f"{cable.get('supplier_name', '')}\n{cable.get('date', '')}",
                note=f"Structure: {width}m x {height}m x {depth}m\nC.C.R: {ccr}m"
            )
        else:
            self.add_to_panel(
                type="Signal Cable To Airtanks",
                brand="",
                order_number="",
                specifications="",
                quantity=total_length,
                price=0,
                last_price_update=f"❌ Cable not found",
                note=f"Structure: {width}m x {height}m x {depth}m\nC.C.R: {ccr}m"
            )

    # signal cable to motors
    def choose_signal_cable_to_motors(self):
        """
        Adds signal cable entries based on motor usage and length.
        """

        length = self.electrical_specs["bagfilter"]["cable_dimension"]
        if length == 0:
            return

        total_length = self.total_motors_qty * length
        if total_length == 0:
            return

        success, cable = get_wire_cable_by_spec("Cable", 7, 1.5, brand=None, note=None)
        if success:
            self.add_to_panel(
                type=f"Signal Cable To Motors",
                brand=cable["brand"],
                order_number=cable["order_number"],
                specifications="7x1.5mm²",
                quantity=total_length,
                price=cable['price'],
                last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                note=f"For {self.total_motors_qty} Motors"
            )
        else:
            self.add_to_panel(
                type=f"Signal Cable To Motors",
                brand="",
                order_number="",
                specifications="7x1.5mm²",
                quantity=total_length,
                price=0,
                last_price_update="❌ Cable not found",
                note=f"For {self.total_motors_qty} Motors"
            )
            print(cable)

    # power cable to motors
    def choose_power_cable_to_motors(self):

        """
         Adds power cable entries with sizing based on current and motor demand.
        """
        volt = self.electrical_specs["project_info"]["l_voltage"]
        length = self.electrical_specs["bagfilter"]["cable_dimension"]
        if length == 0:
            return

        cable_grouping = defaultdict(lambda: {"total_length": 0, "notes": []})
        correction_factor = 1.6 / (sqrt(3) * volt * COSNUS_PI * ETA)

        motor_objects = []
        for section in self.electrical_specs.values():
            motors = section.get("motors", {})
            for motor_name, motor_data in motors.items():
                try:
                    qty = motor_data.get("qty", 0)
                    motor = motor_data.get("motor", 0)
                    motor_objects.append((motor, qty))
                except Exception:
                    pass

        for motor, qty in motor_objects:
            if qty > 0 and motor.power > 0:
                current = motor.power * correction_factor
                cable = cable_rating(cable_length_m=length, cable_current_a=current)
                if cable:
                    motor_length = length * motor.power_cable_cofactor * qty
                    cable_grouping[cable]["total_length"] += motor_length
                    cable_grouping[cable]["notes"].append(f"{motor_length:.1f} m for {motor.usage}")
                else:
                    self.add_to_panel(
                        type=f"Power Cable",
                        note="Power Cable For {motor.usage} Not Found"
                    )

        for size_mm, data in cable_grouping.items():
            total_len = round(data["total_length"], 2)
            if total_len == 0:
                continue

            success, cable = get_wire_cable_by_spec("Cable", 4, size_mm, brand=None, note=None)
            if success:
                self.add_to_panel(
                    type=f"Power Cable To Motors",
                    brand=cable["brand"],
                    order_number=cable["order_number"],
                    specifications=f"4x{size_mm}mm²",
                    quantity=total_len,
                    price=cable['price'],
                    last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                    note="\n".join(data["notes"])
                )
            else:
                self.add_to_panel(
                    type=f"Power Cable To Motors",
                    brand="",
                    order_number="",
                    specifications=f"4x{size_mm}mm²",
                    quantity=total_len,
                    price=0,
                    last_price_update="❌ Cable not found",
                    note="\n".join(data["notes"])
                )
                print(cable)

    """ ladder """

    def choose_ladder_and_cover(self):
        if self.n_airtank == 0 or self.electrical_specs["installation"]["height"] == 0:
            return

        success, ladder = get_wire_cable_by_spec("Ladder", l_number=1, l_size=self.ladder_size)
        if success:
            self.add_to_panel(
                type=f"Ladder",
                brand=ladder["brand"],
                order_number=ladder["order_number"],
                specifications=f"{self.ladder_size}mm²",
                quantity=self.ladder_length,
                price=ladder['price'],
                last_price_update=f"{ladder['supplier_name']}\n{ladder['date']}",
                note=f"For {self.n_airtank} Air Tanks")

        else:
            self.add_to_panel(
                type=f"Ladder",
                brand="",
                order_number="",
                specifications=f"{self.ladder_size}mm²",
                quantity=self.ladder_length,
                price=0,
                last_price_update="❌ Ladder not found",
                note=f"For {self.n_airtank} Air Tanks")

            print(ladder)

        success, ladder_cover = get_wire_cable_by_spec("LadderCover", l_number=1, l_size=self.ladder_size)
        if success:
            self.add_to_panel(
                type=f"Ladder Cover",
                brand=ladder_cover["brand"],
                order_number=ladder_cover["order_number"],
                specifications=f"{self.ladder_size}mm²",
                quantity=self.ladder_length,
                price=ladder_cover['price'],
                last_price_update=f"{ladder_cover['supplier_name']}\n{ladder_cover['date']}",
                note=f"For {self.n_airtank} Air Tanks")

        else:
            self.add_to_panel(
                type=f"Ladder Cover",
                brand="",
                order_number="",
                specifications=f"{self.ladder_size}mm²",
                quantity=self.ladder_length,
                price=0,
                last_price_update="❌ Ladder Cover not found",
                note=f"For {self.n_airtank} Air Tanks")

    def choose_ladder_connector_and_screw(self):
        if self.electrical_specs["installation"]["height"] == 0:
            return

        n_connectors = int(self.electrical_specs["installation"]["height"] * 1.5 / 2) * 2
        n_screw = n_connectors * 16

        success, connector = get_general_by_spec(type="Ladder Connector")
        if success:
            self.add_to_panel(
                type=f"Ladder Connector",
                brand=connector["brand"],
                order_number=connector["order_number"],
                specifications="",
                quantity=n_connectors,
                price=connector['price'],
                last_price_update=f"{connector['supplier_name']}\n{connector['date']}",
                note="")
        else:
            self.add_to_panel(
                type=f"Ladder Connector",
                brand="",
                order_number="",
                specifications="",
                quantity=n_connectors,
                price=0,
                last_price_update="❌ Ladder Connector not found",
                note=f"For {self.n_airtank} Air Tanks")

        success, screw = get_general_by_spec(type="Ladder Screw")
        if success:
            self.add_to_panel(
                type=f"Ladder Screw",
                brand=screw["brand"],
                order_number=screw["order_number"],
                specifications="",
                quantity=n_screw,
                price=screw['price'],
                last_price_update=f"{screw['supplier_name']}\n{screw['date']}",
                note=f"For {n_connectors} Ladder Connector")
        else:
            self.add_to_panel(
                type=f"Ladder Screw",
                brand="",
                order_number="",
                specifications="",
                quantity=n_screw,
                price=0,
                last_price_update="❌ Ladder Connector found",
                note=f"For {n_connectors} Ladder Connector")

    def choose_supports(self):
        if self.electrical_specs["installation"]["height"] == 0:
            return

        n_support_u = round(self.electrical_specs["installation"]["height"] * 1.3, 2)
        n_support_u += round(self.total_instruments * 2, 2)
        success, support_u = get_general_by_spec(type="Ladder Support U", specification="8")
        if success:
            self.add_to_panel(
                type=f"Ladder Support U8",
                brand=support_u["brand"],
                order_number=support_u["order_number"],
                specifications="",
                quantity=n_support_u,
                price=support_u['price'],
                last_price_update=f"{support_u['supplier_name']}\n{support_u['date']}",
                note=f"For {self.electrical_specs['installation']['height']} Height and {self.total_instruments} Instruments")
        else:
            self.add_to_panel(
                type=f"Ladder Support U8",
                brand="",
                order_number="",
                specifications="",
                quantity=n_support_u,
                price=0,
                last_price_update="❌ Ladder Support U not found",
                note=f"For {self.electrical_specs['installation']['height']} Height and {self.total_instruments} Instruments")

        n_support_l = round(self.electrical_specs["installation"]["height"] * 0.6, 2)
        n_support_l += round(self.total_instruments * 0.5, 2)
        success, support_l = get_general_by_spec(type="Ladder Support L", specification="5")
        if success:
            self.add_to_panel(
                type=f"Ladder Support L5",
                brand=support_l["brand"],
                order_number=support_l["order_number"],
                specifications="",
                quantity=n_support_l,
                price=support_l['price'],
                last_price_update=f"{support_l['supplier_name']}\n{support_l['date']}",
                note=f"For Ladder_Height/1.5 x 0.6 Height and {self.total_instruments} Instruments")
        else:
            self.add_to_panel(
                type=f"Ladder Support L5",
                brand="",
                order_number="",
                specifications="",
                quantity=n_support_l,
                price=0,
                last_price_update="❌ Ladder Support L not found",
                note=f"For Ladder_Height/1.5 x 0.6 Height and {self.total_instruments} Instruments")

        n_support_screw = self.electrical_specs["installation"]["height"] * 8
        n_support_screw += self.total_instruments * 8
        success, support_screw = get_general_by_spec(type="Ladder Support Screw", specification="8")
        if success:
            self.add_to_panel(
                type=f"Ladder Support Screw",
                brand=support_screw["brand"],
                order_number=support_screw["order_number"],
                specifications="",
                quantity=n_support_screw,
                price=support_screw['price'],
                last_price_update=f"{support_screw['supplier_name']}\n{support_screw['date']}",
                note=f"For Ladder_Height/1.5 x 8 and {self.total_instruments} Instruments")
        else:
            self.add_to_panel(
                type=f"Ladder Support Screw",
                brand="",
                order_number="",
                specifications="",
                quantity=n_support_screw,
                price=0,
                last_price_update="❌ Ladder Support Screw not found",
                note=f"For Ladder_Height/1.5 x 8 and {self.total_instruments} Instruments")

        n_riser = 2
        success, riser = get_wire_cable_by_spec("LadderRiser", l_number=1, l_size=self.ladder_size)
        if success:
            self.add_to_panel(
                type=f"Ladder Riser",
                brand=riser["brand"],
                order_number=riser["order_number"],
                specifications="",
                quantity=n_riser,
                price=riser['price'],
                last_price_update=f"{riser['supplier_name']}\n{riser['date']}",
                note=f"According to ladder size")
        else:
            self.add_to_panel(
                type=f"Ladder Riser",
                brand="",
                order_number="",
                specifications="",
                quantity=n_riser,
                price=0,
                last_price_update="❌ Riser not found",
                note=f"According to ladder size")

    """ tray """

    def choose_tray_and_cover(self):

        success, tray = get_wire_cable_by_spec("Tray", l_number=1, l_size=self.tray_size)
        if success:
            self.add_to_panel(
                type=f"Tray",
                brand=tray["brand"],
                order_number=tray["order_number"],
                specifications=f"{self.tray_length}mm²",
                quantity=self.tray_length,
                price=tray['price'],
                last_price_update=f"{tray['supplier_name']}\n{tray['date']}",
                note=f"For {self.n_airtank} Air Tanks")

        else:
            self.add_to_panel(
                type=f"Tray",
                brand="",
                order_number="",
                specifications=f"{self.tray_length}mm²",
                quantity=self.tray_length,
                price=0,
                last_price_update="❌ Tray not found",
                note=f"For {self.n_airtank} Air Tanks")

            print(tray)

        success, tray_cover = get_wire_cable_by_spec("TrayCover", l_number=1, l_size=self.ladder_size)
        if success:
            self.add_to_panel(
                type=f"Tray Cover",
                brand=tray_cover["brand"],
                order_number=tray_cover["order_number"],
                specifications=f"{self.tray_length}mm²",
                quantity=self.tray_length,
                price=tray_cover['price'],
                last_price_update=f"{tray_cover['supplier_name']}\n{tray_cover['date']}",
                note=f"For {self.n_airtank} Air Tanks")

        else:
            self.add_to_panel(
                type=f"Tray Cover",
                brand="",
                order_number="",
                specifications=f"{self.tray_length}mm²",
                quantity=self.tray_length,
                price=0,
                last_price_update="❌ Tray Cover not found",
                note=f"For {self.n_airtank} Air Tanks")

    def choose_tray_connector_and_screw(self):
        if self.electrical_specs["installation"]["width"] == 0:
            return

        n_connectors = int(self.electrical_specs["installation"]["width"] * 1.5 / 2) * 2
        n_screw = n_connectors * 16

        success, connector = get_general_by_spec(type="Tray Connector")
        if success:
            self.add_to_panel(
                type=f"Tray Connector",
                brand=connector["brand"],
                order_number=connector["order_number"],
                specifications="",
                quantity=n_connectors,
                price=connector['price'],
                last_price_update=f"{connector['supplier_name']}\n{connector['date']}",
                note="")
        else:
            self.add_to_panel(
                type=f"Tray Connector",
                brand="",
                order_number="",
                specifications="",
                quantity=n_connectors,
                price=0,
                last_price_update="❌ Tray Connector not found",
                note=f"For {self.n_airtank} Air Tanks")

        success, screw = get_general_by_spec(type="Tray Screw")
        if success:
            self.add_to_panel(
                type=f"Tray Screw",
                brand=screw["brand"],
                order_number=screw["order_number"],
                specifications="",
                quantity=n_screw,
                price=screw['price'],
                last_price_update=f"{screw['supplier_name']}\n{screw['date']}",
                note=f"For {n_connectors} Tray Connector")
        else:
            self.add_to_panel(
                type=f"Tray Screw",
                brand="",
                order_number="",
                specifications="",
                quantity=n_screw,
                price=0,
                last_price_update="❌ Tray Connector found",
                note=f"For {n_connectors} Tray Connector")

    def choose_tray_riser(self):
        if self.electrical_specs["installation"]["width"] == 0:
            return

        n_support_u = round(self.electrical_specs["installation"]["width"] * 1.3, 2)
        success, support_u = get_general_by_spec(type="Tray Support U", specification="8")
        if success:
            self.add_to_panel(
                type=f"Tray Support U8",
                brand=support_u["brand"],
                order_number=support_u["order_number"],
                specifications="",
                quantity=n_support_u,
                price=support_u['price'],
                last_price_update=f"{support_u['supplier_name']}\n{support_u['date']}",
                note=f"For {self.electrical_specs['installation']['width']} Width")
        else:
            self.add_to_panel(
                type=f"Tray Support U8",
                brand="",
                order_number="",
                specifications="",
                quantity=n_support_u,
                price=0,
                last_price_update="❌ Tray Support U not found",
                note=f"For {self.electrical_specs['installation']['width']} Width")

        n_support_l = round(self.electrical_specs["installation"]["width"] * 0.6, 2)
        success, support_l = get_general_by_spec(type="Tray Support L", specification="5")
        if success:
            self.add_to_panel(
                type=f"Tray Support L5",
                brand=support_l["brand"],
                order_number=support_l["order_number"],
                specifications="",
                quantity=n_support_l,
                price=support_l['price'],
                last_price_update=f"{support_l['supplier_name']}\n{support_l['date']}",
                note=f"For Ladder_Width/1.5 x 0.6 Width")
        else:
            self.add_to_panel(
                type=f"Tray Support L5",
                brand="",
                order_number="",
                specifications="",
                quantity=n_support_l,
                price=0,
                last_price_update="❌ Tray Support L not found",
                note=f"For Ladder_Width/1.5 x 0.6 Width")

        n_support_screw = self.electrical_specs["installation"]["width"] * 8
        success, support_screw = get_general_by_spec(type="Tray Support Screw", specification="8")
        if success:
            self.add_to_panel(
                type=f"Tray Support Screw",
                brand=support_screw["brand"],
                order_number=support_screw["order_number"],
                specifications="",
                quantity=n_support_screw,
                price=support_screw['price'],
                last_price_update=f"{support_screw['supplier_name']}\n{support_screw['date']}",
                note=f"For Ladder_Height/1.5 x 8")
        else:
            self.add_to_panel(
                type=f"Tray Support Screw",
                brand="",
                order_number="",
                specifications="",
                quantity=n_support_screw,
                price=0,
                last_price_update="❌ Tray Support Screw not found",
                note=f"For Ladder_Height/1.5 x 8")

        n_riser = 2
        success, riser = get_wire_cable_by_spec("LadderRiser", l_number=1, l_size=self.ladder_size)
        if success:
            self.add_to_panel(
                type=f"Tray Riser",
                brand=riser["brand"],
                order_number=riser["order_number"],
                specifications="",
                quantity=n_riser,
                price=riser['price'],
                last_price_update=f"{riser['supplier_name']}\n{riser['date']}",
                note=f"According to ladder size")
        else:
            self.add_to_panel(
                type=f"Tray Riser",
                brand="",
                order_number="",
                specifications="",
                quantity=n_riser,
                price=0,
                last_price_update="❌ Riser not found",
                note=f"According to ladder size")

    def choose_cableshow_cabletrap_cabletag(self):
        # Cable Shoe
        success, cable_show = get_general_by_spec("Cable Shoe")
        if success:
            self.add_to_panel(
                type="Cable Shoe",
                brand=cable_show["brand"],
                order_number="",
                quantity=self.total_instruments * 5,
                price=cable_show["price"],
                last_price_update=f"{cable_show.get('supplier_name', '')}\n{cable_show.get('date', '')}",
                note=f"For {self.total_instruments} Instruments"
            )
        else:
            self.add_to_panel(
                type="Cable Shoe",
                brand="",
                order_number="",
                specifications="",
                quantity=self.total_instruments * 5,
                price=0,
                last_price_update=f"❌ Cable Shoe not found",
                note=f"For {self.total_instruments} Instruments"
            )

        # Cable Trap
        success, cable_show = get_general_by_spec("Cable Trap")
        if success:
            self.add_to_panel(
                type="Cable Trap",
                brand=cable_show["brand"],
                order_number="",
                quantity=self.n_airtank,
                price=cable_show["price"],
                last_price_update=f"{cable_show.get('supplier_name', '')}\n{cable_show.get('date', '')}",
                note=f"For {self.n_airtank} AirTank"
            )
        else:
            self.add_to_panel(
                type="Cable Trap",
                brand="",
                order_number="",
                specifications="",
                quantity=self.n_airtank,
                price=0,
                last_price_update=f"❌ Cable Trap not found",
                note=f"For {self.n_airtank} AirTank"
            )

        # Cable Tag
        success, cable_tag = get_general_by_spec("Cable Tag")
        if success:
            self.add_to_panel(
                type="Cable Tag",
                brand=cable_tag["brand"],
                order_number="",
                quantity= self.n_airtank + self.total_instruments,
                price=cable_tag["price"],
                last_price_update=f"{cable_tag.get('supplier_name', '')}\n{cable_tag.get('date', '')}",
                note=f"For {self.n_airtank} and {self.total_instruments} Instruments"
            )
        else:
            self.add_to_panel(
                type="Cable Tag",
                brand="",
                order_number="",
                specifications="",
                quantity= self.n_airtank + self.total_instruments,
                price=0,
                last_price_update=f"❌ Cable Tag not found",
                note=f"For {self.n_airtank} and {self.total_instruments} Instruments"
            )


def cable_rating(cable_length_m, cable_current_a):
    cable_rating = \
        [{'cable_size_mm': 1.5, 'cable_length_m': 10, 'cable_current_a': 27.0},
         {'cable_size_mm': 1.5, 'cable_length_m': 50, 'cable_current_a': 15.0},
         {'cable_size_mm': 1.5, 'cable_length_m': 100, 'cable_current_a': 7.0},
         {'cable_size_mm': 1.5, 'cable_length_m': 150, 'cable_current_a': 5.0},
         {'cable_size_mm': 2.5, 'cable_length_m': 10, 'cable_current_a': 36.0},
         {'cable_size_mm': 2.5, 'cable_length_m': 50, 'cable_current_a': 25.0},
         {'cable_size_mm': 2.5, 'cable_length_m': 100, 'cable_current_a': 12.0},
         {'cable_size_mm': 2.5, 'cable_length_m': 150, 'cable_current_a': 8.0},
         {'cable_size_mm': 2.5, 'cable_length_m': 200, 'cable_current_a': 6.0},
         {'cable_size_mm': 4.0, 'cable_length_m': 10, 'cable_current_a': 46.0},
         {'cable_size_mm': 4.0, 'cable_length_m': 50, 'cable_current_a': 40.0},
         {'cable_size_mm': 4.0, 'cable_length_m': 100, 'cable_current_a': 20.0},
         {'cable_size_mm': 4.0, 'cable_length_m': 150, 'cable_current_a': 13.0},
         {'cable_size_mm': 4.0, 'cable_length_m': 200, 'cable_current_a': 10.0},
         {'cable_size_mm': 4.0, 'cable_length_m': 250, 'cable_current_a': 8.0},
         {'cable_size_mm': 4.0, 'cable_length_m': 300, 'cable_current_a': 6.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 10, 'cable_current_a': 58.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 50, 'cable_current_a': 58.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 100, 'cable_current_a': 30.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 150, 'cable_current_a': 20.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 200, 'cable_current_a': 15.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 250, 'cable_current_a': 12.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 300, 'cable_current_a': 10.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 350, 'cable_current_a': 8.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 400, 'cable_current_a': 7.0},
         {'cable_size_mm': 6.0, 'cable_length_m': 450, 'cable_current_a': 6.5},
         {'cable_size_mm': 6.0, 'cable_length_m': 500, 'cable_current_a': 6.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 10, 'cable_current_a': 77.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 50, 'cable_current_a': 77.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 100, 'cable_current_a': 50.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 150, 'cable_current_a': 33.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 200, 'cable_current_a': 25.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 250, 'cable_current_a': 20.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 300, 'cable_current_a': 16.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 350, 'cable_current_a': 14.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 400, 'cable_current_a': 12.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 450, 'cable_current_a': 11.0},
         {'cable_size_mm': 10.0, 'cable_length_m': 500, 'cable_current_a': 10.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 10, 'cable_current_a': 100.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 50, 'cable_current_a': 100.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 100, 'cable_current_a': 80.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 150, 'cable_current_a': 63.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 200, 'cable_current_a': 40.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 250, 'cable_current_a': 32.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 300, 'cable_current_a': 26.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 350, 'cable_current_a': 22.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 400, 'cable_current_a': 20.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 450, 'cable_current_a': 17.0},
         {'cable_size_mm': 16.0, 'cable_length_m': 500, 'cable_current_a': 16.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 10, 'cable_current_a': 130.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 50, 'cable_current_a': 130.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 100, 'cable_current_a': 125.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 150, 'cable_current_a': 83.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 200, 'cable_current_a': 62.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 250, 'cable_current_a': 50.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 300, 'cable_current_a': 41.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 350, 'cable_current_a': 35.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 400, 'cable_current_a': 31.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 450, 'cable_current_a': 27.0},
         {'cable_size_mm': 25.0, 'cable_length_m': 500, 'cable_current_a': 25.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 10, 'cable_current_a': 155.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 50, 'cable_current_a': 155.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 100, 'cable_current_a': 155.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 150, 'cable_current_a': 115.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 200, 'cable_current_a': 86.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 250, 'cable_current_a': 69.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 300, 'cable_current_a': 57.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 350, 'cable_current_a': 49.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 400, 'cable_current_a': 43.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 450, 'cable_current_a': 38.0},
         {'cable_size_mm': 35.0, 'cable_length_m': 500, 'cable_current_a': 34.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 10, 'cable_current_a': 185.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 50, 'cable_current_a': 185.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 100, 'cable_current_a': 185.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 150, 'cable_current_a': 156.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 200, 'cable_current_a': 117.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 250, 'cable_current_a': 93.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 300, 'cable_current_a': 78.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 350, 'cable_current_a': 66.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 400, 'cable_current_a': 58.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 450, 'cable_current_a': 52.0},
         {'cable_size_mm': 50.0, 'cable_length_m': 500, 'cable_current_a': 46.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 10, 'cable_current_a': 230.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 50, 'cable_current_a': 230.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 100, 'cable_current_a': 230.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 150, 'cable_current_a': 222.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 200, 'cable_current_a': 166.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 250, 'cable_current_a': 133.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 300, 'cable_current_a': 111.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 350, 'cable_current_a': 95.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 400, 'cable_current_a': 83.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 450, 'cable_current_a': 74.0},
         {'cable_size_mm': 70.0, 'cable_length_m': 500, 'cable_current_a': 66.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 10, 'cable_current_a': 275.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 50, 'cable_current_a': 275.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 100, 'cable_current_a': 275.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 150, 'cable_current_a': 275.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 200, 'cable_current_a': 225.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 250, 'cable_current_a': 180.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 300, 'cable_current_a': 150.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 350, 'cable_current_a': 129.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 400, 'cable_current_a': 112.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 450, 'cable_current_a': 100.0},
         {'cable_size_mm': 95.0, 'cable_length_m': 500, 'cable_current_a': 90.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 10, 'cable_current_a': 315.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 50, 'cable_current_a': 315.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 100, 'cable_current_a': 315.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 150, 'cable_current_a': 315.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 200, 'cable_current_a': 278.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 250, 'cable_current_a': 222.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 300, 'cable_current_a': 185.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 350, 'cable_current_a': 159.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 400, 'cable_current_a': 139.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 450, 'cable_current_a': 123.0},
         {'cable_size_mm': 120.0, 'cable_length_m': 500, 'cable_current_a': 111.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 10, 'cable_current_a': 355.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 50, 'cable_current_a': 355.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 100, 'cable_current_a': 355.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 150, 'cable_current_a': 355.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 200, 'cable_current_a': 330.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 250, 'cable_current_a': 264.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 300, 'cable_current_a': 220.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 350, 'cable_current_a': 189.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 400, 'cable_current_a': 165.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 450, 'cable_current_a': 147.0},
         {'cable_size_mm': 150.0, 'cable_length_m': 500, 'cable_current_a': 132.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 10, 'cable_current_a': 400.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 50, 'cable_current_a': 400.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 100, 'cable_current_a': 400.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 150, 'cable_current_a': 400.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 200, 'cable_current_a': 393.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 250, 'cable_current_a': 314.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 300, 'cable_current_a': 267.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 350, 'cable_current_a': 224.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 400, 'cable_current_a': 196.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 450, 'cable_current_a': 174.0},
         {'cable_size_mm': 185.0, 'cable_length_m': 500, 'cable_current_a': 157.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 10, 'cable_current_a': 465.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 50, 'cable_current_a': 465.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 100, 'cable_current_a': 465.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 150, 'cable_current_a': 465.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 200, 'cable_current_a': 437.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 250, 'cable_current_a': 349.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 300, 'cable_current_a': 291.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 350, 'cable_current_a': 249.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 400, 'cable_current_a': 218.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 450, 'cable_current_a': 194.0},
         {'cable_size_mm': 240.0, 'cable_length_m': 500, 'cable_current_a': 174.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 10, 'cable_current_a': 550.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 50, 'cable_current_a': 550.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 100, 'cable_current_a': 550.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 150, 'cable_current_a': 550.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 200, 'cable_current_a': 496.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 250, 'cable_current_a': 397.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 300, 'cable_current_a': 331.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 350, 'cable_current_a': 283.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 400, 'cable_current_a': 248.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 450, 'cable_current_a': 220.0},
         {'cable_size_mm': 300.0, 'cable_length_m': 500, 'cable_current_a': 198.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 10, 'cable_current_a': 745.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 50, 'cable_current_a': 745.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 100, 'cable_current_a': 745.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 150, 'cable_current_a': 745.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 200, 'cable_current_a': 559.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 250, 'cable_current_a': 447.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 300, 'cable_current_a': 373.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 350, 'cable_current_a': 319.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 400, 'cable_current_a': 279.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 450, 'cable_current_a': 248.0},
         {'cable_size_mm': 400.0, 'cable_length_m': 500, 'cable_current_a': 224.0}]

    # Filter entries with cable_length >= input
    filtered = [
        r for r in cable_rating
        if r['cable_length_m'] >= cable_length_m and r['cable_current_a'] >= cable_current_a
    ]

    # Sort by cable_length_m then cable_current_a
    filtered.sort(key=lambda x: (x['cable_length_m'], x['cable_current_a']))

    # Return the first matching cable_size_mm
    if filtered:
        return filtered[0]['cable_size_mm']
    else:
        return None  # or raise an exception / return default
