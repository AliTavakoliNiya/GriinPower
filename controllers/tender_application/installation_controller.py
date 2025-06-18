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
        self.choose_lcb()
        self.choose_jb()
        self.chosse_gland_valvecable_flexible_conduit()
        self.chosse_signal_cable()
        return self.panel

    def choose_lcb(self):
        motors_lcb = {"Damper":1 * self.electrical_specs["damper"]["motors"]["damper"]["qty"],
                       "Fan":1 * self.electrical_specs["fan"]["motors"]["fan"]["qty"],
                       "Rotary":1 * self.electrical_specs["transport"]["motors"]["rotary"]["qty"],
                       "Screw1":1 * self.electrical_specs["transport"]["motors"]["screw1"]["qty"],
                       "Screw2":1 * self.electrical_specs["transport"]["motors"]["screw2"]["qty"],
                       "Slide Gate":1 * self.electrical_specs["transport"]["motors"]["slide_gate"]["qty"],
                       "Telescopic Chute":1 * self.electrical_specs["transport"]["motors"]["telescopic_chute"]["qty"],
                       "Vibration":0,
                       "Fresh Air":1 * self.electrical_specs["fresh_air"]["motors"]["freshair_motor"]["qty"],
                       "Fresh Air Flap":1 * self.electrical_specs["fresh_air"]["motors"]["fresh_air_flap"]["qty"],
                       "Emergency Air Flap":1 * self.electrical_specs["fresh_air"]["motors"]["emergency_flap"]["qty"],
                       "Hopper Heater":4 * self.electrical_specs["hopper_heater"]["motors"]["elements"]["qty"],
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
                last_price_update="❌ Junction Box not found",
                note=notes
            )


    def choose_jb(self):

        total_motors_qty = 0
        for section in self.electrical_specs.values():
            motors = section.get("motors", {})
            for motor_name, motor_data in motors.items():
                try:
                    qty = motor_data.get("qty", 0)
                    total_motors_qty += qty
                except Exception:
                    pass

        success, jb = get_electrical_panel_by_spec(type="Junction Box", width=200, height=200, depth=120)
        if success:
            self.add_to_panel(
                type="Junction Box",
                brand=jb['brand'],
                order_number=jb["order_number"],
                specifications=f"200mm x 200mm x 120mm",
                quantity=total_motors_qty,
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
                quantity=total_motors_qty,
                price=0,
                last_price_update="❌ Junction Box not found",
                note=""
            )


    def chosse_gland_valvecable_flexible_conduit(self):
        n_valves = 0
        if self.electrical_specs["bagfilter"]["type"] == "Griin/China":
            match = re.search(r"×(.*?)\.", self.electrical_specs["bagfilter"]["order"])
            if match:
                n_valves = int(match.group(1))

        if self.electrical_specs["bagfilter"]["type"] == "BETH":
            match = re.fullmatch(r"^(\d+)\.\d+x(\d+)\.\d+x\d+$", self.electrical_specs["bagfilter"]["order"])
            if match:
                num1 = int(match.group(1))
                num2 = int(match.group(2))
                n_valves = num1 * num2

        if n_valves == 0:
            return

        # choose gland
        success, gland = get_general_by_spec("Gland")
        if success:
            self.add_to_panel(
                type="Gland",
                brand=gland["brand"],
                order_number="",
                specifications=gland["specification"],
                quantity=n_valves*2,
                price=gland["price"],
                last_price_update=f"{gland.get('supplier_name', '')}\n{gland.get('date', '')}",
                note=f"{n_valves} Valves"
            )
        else:
            self.add_to_panel(
                type="Gland",
                brand="",
                order_number="",
                specifications="",
                quantity=n_valves*2,
                price=0,
                last_price_update=f"❌ Gland not found",
                note=f"{n_valves} Valves"
            )

        # choose cable
        success, cable = get_wire_cable_by_spec("Cable", 3, 1.5)
        if success:
            self.add_to_panel(
                type="Valve Cable",
                brand=cable["brand"],
                order_number="",
                specifications=f"{cable['l_number']}x{cable['l_size']}mm²",
                quantity=n_valves*2,
                price=cable["price"],
                last_price_update=f"{cable.get('supplier_name', '')}\n{cable.get('date', '')}",
                note=f"{n_valves} Valves"
            )
        else:
            self.add_to_panel(
                type="Valve Cable",
                brand="",
                order_number="",
                specifications="",
                quantity=n_valves*2,
                price=0,
                last_price_update=f"❌ Cable not found",
                note=f"{n_valves} Valves"
            )

        # flexible conduit
        success, conduit = get_wire_cable_by_spec("FlexibleConduit", 1)
        if success:
            self.add_to_panel(
                type="Flexible Conduit",
                brand=conduit["brand"],
                order_number="",
                specifications=f"{conduit['l_number']}x{conduit['l_size']}mm²",
                quantity=n_valves*2,
                price=conduit["price"],
                last_price_update=f"{conduit.get('supplier_name', '')}\n{conduit.get('date', '')}",
                note=f"{n_valves} Valves"
            )
        else:
            self.add_to_panel(
                type="Flexible Conduit",
                brand="",
                order_number="",
                specifications="",
                quantity=n_valves*2,
                price=0,
                last_price_update=f"❌ Flexible Conduit not found",
                note=f"{n_valves} Valves"
            )


    def chosse_signal_cable(self):
        width  = self.electrical_specs["installation"]["width"]
        height = self.electrical_specs["installation"]["height"]
        depth  = self.electrical_specs["installation"]["depth"]
        ccr    = self.electrical_specs["installation"]["ccr"]

        total_length = width + height + depth + ccr
        if total_length == 0 or width == 0 or height == 0 or depth == 0:
            return


        # choose cable
        success, cable = get_wire_cable_by_spec("Cable", 10, 1.5)
        if success:
            self.add_to_panel(
                type="Signal Cable",
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
                type="Signal Cable",
                brand="",
                order_number="",
                specifications="",
                quantity=total_length,
                price=0,
                last_price_update=f"❌ Cable not found",
                note=f"Structure: {width}m x {height}m x {depth}m\nC.C.R: {ccr}m"
            )
