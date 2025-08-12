import re

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
                        continue  # skip this 2 instruments
                    qty = instrument_data.get("qty", 0)
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
        self.choose_gland_flexible_conduit_cableTray()
        self.choose_ladder_and_cover()
        self.choose_ladder_connector_and_screw()
        self.choose_tray_and_cover()
        self.choose_supports()
        self.choose_tray_riser()
        self.choose_cableshoe_cableTyRap_cableMetalTag()
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
                quantity=self.total_motors_qty + self.n_airtank,
                price=jb['price'],
                last_price_update=f"{jb['supplier_name']}\n{jb['date']}",
                note=f"{self.total_motors_qty}xMotors\n{self.n_airtank}xAirTanks"
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
                note=f"{self.total_motors_qty}xMotors\n{self.n_airtank}xAirTanks"
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
                note=f"For {self.total_instruments} Instruments"
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
                note=f"For {self.total_instruments} Instruments"
            )

    def choose_gland_flexible_conduit_cableTray(self):

        if self.n_valves == 0 or self.n_airtank == 0:
            return

        # conduit pipe
        success, conduit = get_wire_cable_by_spec("Conduit", 1)
        if success:
            self.add_to_panel(
                type="Conduit",
                brand=conduit["brand"],
                order_number="",
                specifications=f"{conduit['l_number']}x{conduit['l_size']}mm²",
                quantity=self.total_motors_qty * 3 + self.total_instruments * 2 + self.ladder_length,
                price=conduit["price"],
                last_price_update=f"{conduit.get('supplier_name', '')}\n{conduit.get('date', '')}",
                note=f"{self.total_motors_qty}x2x1.5m Motors\n"
                     f"Height({self.ladder_length}) x AirTank\n"
                     f"{self.total_instruments}x2m Instruments"
            )
        else:
            self.add_to_panel(
                type="Conduit",
                brand="",
                order_number="",
                specifications="",
                quantity=self.total_motors_qty * 3 + self.total_instruments * 2 + self.ladder_length,
                price=0,
                last_price_update=f"❌ Flexible Conduit not found",
                note=f"{self.total_motors_qty}x2x1.5m Motors\n"
                     f"Height({self.ladder_length}) x AirTank\n"
                     f"{self.total_instruments}x2m Instruments"
            )

        # flexible conduit
        success, flexible_conduit = get_wire_cable_by_spec("FlexibleConduit", 1)
        if success:
            self.add_to_panel(
                type="Flexible Conduit",
                brand=flexible_conduit["brand"],
                order_number="",
                specifications=f"{flexible_conduit['l_number']}x{flexible_conduit['l_size']}mm²",
                quantity=self.n_valves * 2 + self.n_airtank * 2 + self.total_instruments * 2 + self.total_motors_qty * 4,
                price=flexible_conduit["price"],
                last_price_update=f"{flexible_conduit.get('supplier_name', '')}\n{flexible_conduit.get('date', '')}",
                note=f"{self.total_motors_qty}x4 Motors\n"
                     f"{self.n_valves}x2 Valves\n"
                     f"{self.n_airtank}x2 Air Tank\n"
                     f"{self.total_instruments}x2 Instruments"
            )
        else:
            self.add_to_panel(
                type="Flexible Conduit",
                brand="",
                order_number="",
                specifications="",
                quantity=self.n_valves * 2 + self.n_airtank * 2 + self.total_instruments * 2 + self.total_motors_qty * 4,
                price=0,
                last_price_update=f"❌ Flexible Conduit not found",
                note=f"{self.total_motors_qty}x4 Motors\n"
                     f"{self.n_valves}x2 Valves\n"
                     f"{self.n_airtank}x2 Air Tank\n"
                     f"{self.total_instruments}x2 Instruments"
            )

        # choose gland for valves
        success, gland = get_general_by_spec("Gland", specification="PG16")
        if success:
            self.add_to_panel(
                type="Gland",
                brand=gland["brand"],
                order_number="",
                specifications="PG16",
                quantity=self.n_valves * 2 + self.total_instruments + self.total_motors_qty * 10,
                price=gland["price"],
                last_price_update=f"{gland.get('supplier_name', '')}\n{gland.get('date', '')}",
                note=f"{self.total_motors_qty}x10 Motors\n{self.n_valves}x2 Valves\n{self.total_instruments} Instruments"
            )
        else:
            self.add_to_panel(
                type="Gland",
                brand="",
                order_number="",
                specifications="PG16",
                quantity=self.n_valves * 2 + self.total_instruments + self.total_motors_qty * 10,
                price=0,
                last_price_update=f"❌ Gland not found",
                note=f"{self.total_motors_qty}x10 Motors\n{self.n_valves}x2 Valves\n{self.total_instruments} Instruments"
            )

        # choose Gland-G21 for airtank
        success, gland = get_general_by_spec("Gland", specification="PG21")
        if success:
            self.add_to_panel(
                type="Gland",
                brand=gland["brand"],
                order_number="",
                specifications="PG21",
                quantity=self.n_airtank * 1 + self.total_motors_qty * 6,
                price=gland["price"],
                last_price_update=f"{gland.get('supplier_name', '')}\n{gland.get('date', '')}",
                note=f"{self.n_airtank}x1 Air Tank\n{self.total_motors_qty}x6 Motors"
            )
        else:
            self.add_to_panel(
                type="Gland",
                brand="",
                order_number="",
                specifications="PG21",
                quantity=self.n_airtank * 1 + self.total_motors_qty * 6,
                price=0,
                last_price_update=f"❌ Gland not found",
                note=f"{self.n_airtank}x1 Air Tank\n{self.total_motors_qty}x6 Motors"
            )

        # conduit Fixer
        success, conduit_fixer = get_general_by_spec("Conduit Fixer")
        if success:
            self.add_to_panel(
                type="Conduit Fixer",
                brand=conduit_fixer["brand"],
                order_number="",
                quantity=self.total_instruments * 2,
                price=conduit_fixer["price"],
                last_price_update=f"{conduit_fixer.get('supplier_name', '')}\n{conduit_fixer.get('date', '')}",
                note=f"{self.total_instruments}x2 Instruments"
            )
        else:
            self.add_to_panel(
                type="Conduit Fixer",
                brand="",
                order_number="",
                specifications="",
                quantity=self.total_instruments * 2,
                price=0,
                last_price_update=f"❌ Flexible Conduit Fixer not found",
                note=f"{self.total_instruments}x2 Instruments"
            )

        # Cable Tray 20
        success, cable_tray = get_wire_cable_by_spec("Cable Tray", 1 , l_size=20 )
        if success:
            self.add_to_panel(
                type="Cable Tray",
                brand=flexible_conduit["brand"],
                order_number="",
                specifications=f"200m",
                quantity=self.total_motors_qty * self.electrical_specs['bagfilter']['cable_dimension'] * 0.2,
                price=flexible_conduit["price"],
                last_price_update=f"{flexible_conduit.get('supplier_name', '')}\n{flexible_conduit.get('date', '')}",
                note=f"{self.total_motors_qty}x Motors x 20% of Distance({self.electrical_specs['bagfilter']['cable_dimension']}m)"
            )
        else:
            self.add_to_panel(
                type="Cable Tray",
                brand="",
                order_number="",
                specifications=f"200m",
                quantity=self.total_motors_qty * self.electrical_specs['bagfilter']['cable_dimension'] * 0.2,
                price=0,
                last_price_update=f"❌ Cable Tray not found",
                note=f"{self.total_motors_qty}x Motors x 20% of Distance({self.electrical_specs['bagfilter']['cable_dimension']}m)"
            )

        # Cable Tray 20 - Cover
        success, cable_tray = get_wire_cable_by_spec("Cable Tray Cover", 1, l_size=20)
        if success:
            self.add_to_panel(
                type="Cable Tray Cover",
                brand=flexible_conduit["brand"],
                order_number="",
                specifications=f"200m",
                quantity=self.total_motors_qty * self.electrical_specs['bagfilter']['cable_dimension'] * 0.2,
                price=flexible_conduit["price"],
                last_price_update=f"{flexible_conduit.get('supplier_name', '')}\n{flexible_conduit.get('date', '')}",
                note=f"{self.total_motors_qty}x Motors x 20% of Distance({self.electrical_specs['bagfilter']['cable_dimension']}m)"
            )
        else:
            self.add_to_panel(
                type="Cable Tray Cover",
                brand="",
                order_number="",
                specifications=f"200m",
                quantity=self.total_motors_qty * self.electrical_specs['bagfilter']['cable_dimension'] * 0.2,
                price=0,
                last_price_update=f"❌ Cable Tray not found",
                note=f"{self.total_motors_qty}x Motors x 20% of Distance({self.electrical_specs['bagfilter']['cable_dimension']}m)"
            )

        # Cable Tray 30
        success, cable_tray = get_wire_cable_by_spec("Cable Tray", 1, l_size=30)
        if success:
            self.add_to_panel(
                type="Cable Tray",
                brand=flexible_conduit["brand"],
                order_number="",
                specifications=f"300m",
                quantity=self.total_motors_qty * self.electrical_specs['bagfilter']['cable_dimension'] * 0.2,
                price=flexible_conduit["price"],
                last_price_update=f"{flexible_conduit.get('supplier_name', '')}\n{flexible_conduit.get('date', '')}",
                note=f"{self.total_motors_qty}x Motors x 20% of Distance({self.electrical_specs['bagfilter']['cable_dimension']}m)"
            )
        else:
            self.add_to_panel(
                type="Cable Tray",
                brand="",
                order_number="",
                specifications=f"300m",
                quantity=self.total_motors_qty * self.electrical_specs['bagfilter']['cable_dimension'] * 0.2,
                price=0,
                last_price_update=f"❌ Cable Tray not found",
                note=f"{self.total_motors_qty}x Motors x 20% of Distance({self.electrical_specs['bagfilter']['cable_dimension']}m)"
            )

        # Cable Tray 30 - Cover
        success, cable_tray = get_wire_cable_by_spec("Cable Tray Cover", 1, l_size=30)
        if success:
            self.add_to_panel(
                type="Cable Tray Cover",
                brand=flexible_conduit["brand"],
                order_number="",
                specifications=f"300m",
                quantity=self.total_motors_qty * self.electrical_specs['bagfilter']['cable_dimension'] * 0.2,
                price=flexible_conduit["price"],
                last_price_update=f"{flexible_conduit.get('supplier_name', '')}\n{flexible_conduit.get('date', '')}",
                note=f"{self.total_motors_qty}x Motors x 20% of Distance({self.electrical_specs['bagfilter']['cable_dimension']}m)"
            )
        else:
            self.add_to_panel(
                type="Cable Tray Cover",
                brand="",
                order_number="",
                specifications=f"300m",
                quantity=self.total_motors_qty * self.electrical_specs['bagfilter']['cable_dimension'] * 0.2,
                price=0,
                last_price_update=f"❌ Cable Tray not found",
                note=f"{self.total_motors_qty}x Motors x 20% of Distance({self.electrical_specs['bagfilter']['cable_dimension']}m)"
            )

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

        n_connectors = int(self.ladder_length / 2) * 2
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
                note=f"Height({self.electrical_specs['installation']['height']})*1.5/2)*2"
            )
        else:
            self.add_to_panel(
                type=f"Ladder Connector",
                brand="",
                order_number="",
                specifications="",
                quantity=n_connectors,
                price=0,
                last_price_update="❌ Ladder Connector not found",
                note=f"Height({self.electrical_specs['installation']['height']})*1.5/2)*2"
            )

        n_screw = n_connectors * 16 + int(self.ladder_length / 1.5) * 8 + self.tray_length * 16 + int(
            self.tray_length / 1.5) * 8 + self.total_instruments * 8 + self.total_instruments * 2
        success, screw = get_general_by_spec(type="Ladder Screw")
        if success:
            self.add_to_panel(
                type=f"Screw",
                brand=screw["brand"],
                order_number=screw["order_number"],
                specifications="",
                quantity=n_screw,
                price=screw['price'],
                last_price_update=f"{screw['supplier_name']}\n{screw['date']}",
                note=f"Ladder Connector({n_connectors})x16\n"
                     f"Ladder Support({int(self.ladder_length / 1.5)})x8\n"
                     f"Tray Connector({self.tray_length})x16\n"
                     f"Tray Support({int(self.tray_length / 1.5)})x8\n"
                     f"Instruments Support({self.total_instruments})x8\n"
                     f"Instruments Fix Elements({self.total_instruments})x2")
        else:
            self.add_to_panel(
                type=f"Screw",
                brand="",
                order_number="",
                specifications="",
                quantity=n_screw,
                price=0,
                last_price_update="❌ Ladder Connector found",
                note=f"Ladder Connector({n_connectors})x16\n"
                     f"Ladder Support({int(self.ladder_length / 1.5)})x8\n"
                     f"Tray Connector({self.tray_length})x16\n"
                     f"Tray Support({int(self.tray_length / 1.5)})x8\n"
                     f"Instruments Support({self.total_instruments})x8\n"
                     f"Instruments Fix Elements({self.total_instruments})x2"
            )

    def choose_supports(self):
        if self.electrical_specs["installation"]["height"] == 0:
            return

        n_support_u = round(self.electrical_specs["installation"]["height"] / 1.5 * 2, 2)
        n_support_u += round(self.electrical_specs["installation"]["width"] / 1.5 * 2, 2)
        n_support_u += round(self.total_instruments * 2, 2)
        success, support_u = get_general_by_spec(type="Support U", specification="8")
        if success:
            self.add_to_panel(
                type=f"Support U8",
                brand=support_u["brand"],
                order_number=support_u["order_number"],
                specifications="",
                quantity=n_support_u,
                price=support_u['price'],
                last_price_update=f"{support_u['supplier_name']}\n{support_u['date']}",
                note=f"Height({self.electrical_specs['installation']['height']})/1.5*2 \n"
                     f"Width({self.electrical_specs['installation']['width']})/1.5*2 \n"
                     f"{self.total_instruments} Instruments")
        else:
            self.add_to_panel(
                type=f"Support U8",
                brand="",
                order_number="",
                specifications="",
                quantity=n_support_u,
                price=0,
                last_price_update="❌ Support U not found",
                note=f"Height({self.electrical_specs['installation']['height']})/1.5*2 \n"
                     f"Width({self.electrical_specs['installation']['width']})/1.5*2 \n"
                     f"{self.total_instruments} Instruments")

        n_support_l = round(self.electrical_specs["installation"]["height"] / 1.5 * 0.6, 2)
        n_support_l += round(self.electrical_specs["installation"]["width"] / 1.5 * 0.6, 2)
        n_support_l += round(self.total_instruments * 0.5, 2)
        success, support_l = get_general_by_spec(type="Support L", specification="5")
        if success:
            self.add_to_panel(
                type=f"Support L5",
                brand=support_l["brand"],
                order_number=support_l["order_number"],
                specifications="",
                quantity=n_support_l,
                price=support_l['price'],
                last_price_update=f"{support_l['supplier_name']}\n{support_l['date']}",
                note=f"Height({self.electrical_specs['installation']['height']})/1.5*0.5 \n"
                     f"Width({self.electrical_specs['installation']['width']})/1.5*0.5 \n"
                     f"{self.total_instruments} Instruments")
        else:
            self.add_to_panel(
                type=f"Support L5",
                brand="",
                order_number="",
                specifications="",
                quantity=n_support_l,
                price=0,
                last_price_update="❌ Support L not found",
                note=f"Height({self.electrical_specs['installation']['height']})/1.5*0.5 \n"
                     f"Width({self.electrical_specs['installation']['width']})/1.5*0.5 \n"
                     f"{self.total_instruments} Instruments")

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
                note=f"According to ladder size {self.ladder_size}")
        else:
            self.add_to_panel(
                type=f"Ladder Riser",
                brand="",
                order_number="",
                specifications="",
                quantity=n_riser,
                price=0,
                last_price_update=f"❌ Ladder Riser not found",
                note=f"According to ladder size {self.ladder_size}")

    """ tray """

    def choose_tray_and_cover(self):

        success, tray = get_wire_cable_by_spec("Tray", l_number=1, l_size=self.tray_size)
        if success:
            self.add_to_panel(
                type=f"Tray",
                brand=tray["brand"],
                order_number=tray["order_number"],
                specifications=f"{self.tray_size}mm²",
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

        success, tray_cover = get_wire_cable_by_spec("TrayCover", l_number=1, l_size=self.ladder_size)
        if success:
            self.add_to_panel(
                type=f"Tray Cover",
                brand=tray_cover["brand"],
                order_number=tray_cover["order_number"],
                specifications=f"{self.tray_size}mm²",
                quantity=self.tray_length,
                price=tray_cover['price'],
                last_price_update=f"{tray_cover['supplier_name']}\n{tray_cover['date']}",
                note=f"For {self.n_airtank} Air Tanks")

        else:
            self.add_to_panel(
                type=f"Tray Cover",
                brand="",
                order_number="",
                specifications=f"{self.tray_size}mm²",
                quantity=self.tray_length,
                price=0,
                last_price_update="❌ Tray Cover not found",
                note=f"For {self.n_airtank} Air Tanks")

    def choose_tray_riser(self):
        if self.electrical_specs["installation"]["width"] == 0:
            return

        n_riser = 2
        success, riser = get_wire_cable_by_spec("TrayRiser", l_number=1, l_size=self.ladder_size)
        if success:
            self.add_to_panel(
                type=f"Tray Riser",
                brand=riser["brand"],
                order_number=riser["order_number"],
                specifications="",
                quantity=n_riser,
                price=riser['price'],
                last_price_update=f"{riser['supplier_name']}\n{riser['date']}",
                note=f"According to ladder size {self.ladder_size}")
        else:
            self.add_to_panel(
                type=f"Tray Riser",
                brand="",
                order_number="",
                specifications="",
                quantity=n_riser,
                price=0,
                last_price_update=f"❌ Tray Riser not found",
                note=f"According to ladder size {self.ladder_size}")

    def choose_cableshoe_cableTyRap_cableMetalTag(self):
        # Cable Shoe
        success, cable_shoe = get_general_by_spec("Cable Shoe")
        if success:
            self.add_to_panel(
                type="Cable Shoe",
                brand=cable_shoe["brand"],
                order_number="",
                quantity=self.total_instruments * 5 + self.total_motors_qty * 10,
                price=cable_shoe["price"],
                last_price_update=f"{cable_shoe.get('supplier_name', '')}\n{cable_shoe.get('date', '')}",
                note=f"{self.total_motors_qty}x10 Motors\n{self.total_instruments}x5 Instruments"
            )
        else:
            self.add_to_panel(
                type="Cable Shoe",
                brand="",
                order_number="",
                specifications="",
                quantity=self.total_instruments * 5 + self.total_motors_qty * 10,
                price=0,
                last_price_update=f"❌ Cable Shoe not found",
                note=f"{self.total_motors_qty}x10 Motors\n{self.total_instruments}x5 Instruments"
            )

        # Cable Tyap
        success, cable_shoe = get_general_by_spec("Cable Tyrap")
        if success:
            self.add_to_panel(
                type="Cable Tyrap",
                brand=cable_shoe["brand"],
                order_number="",
                quantity=self.n_airtank,
                price=cable_shoe["price"],
                last_price_update=f"{cable_shoe.get('supplier_name', '')}\n{cable_shoe.get('date', '')}",
                note=f"{self.n_airtank} AirTank"
            )
        else:
            self.add_to_panel(
                type="Cable Tyrap",
                brand="",
                order_number="",
                specifications="",
                quantity=self.n_airtank,
                price=0,
                last_price_update=f"❌ Cable Tyrap not found",
                note=f"{self.n_airtank} AirTank"
            )

        # Cable Tag
        success, cable_tag = get_general_by_spec("Cable MetalTag")
        if success:
            self.add_to_panel(
                type="Cable Tag",
                brand=cable_tag["brand"],
                order_number="",
                quantity=self.n_airtank + self.total_instruments,
                price=cable_tag["price"],
                last_price_update=f"{cable_tag.get('supplier_name', '')}\n{cable_tag.get('date', '')}",
                note=f"{self.n_airtank} AirTank\n{self.total_instruments} Intstrument"
            )
        else:
            self.add_to_panel(
                type="Cable Tag",
                brand="",
                order_number="",
                specifications="",
                quantity=self.n_airtank + self.total_instruments,
                price=0,
                last_price_update=f"❌ Cable MetalTag not found",
                note=f"{self.n_airtank} AirTank\n{self.total_instruments} Intstrument"
            )
