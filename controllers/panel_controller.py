from collections import defaultdict
from math import sqrt

from config import COSNUS_PI, ETA
from models.cable_rating_model import get_cable_by_dimension_current
from models.contactor_model import get_contactor_by_motor_power
from models.general_model import get_general_by_name
from models.mpcb_model import get_mpcb_by_motor_power
from models.mccb_model import get_mccb_by_motor_power


class PanelController:
    """
    Base controller class for building electrical panels from project specifications.
    """

    def __init__(self, panel_type):
        """
        Initialize the panel controller with a specific panel type.

        Args:
            panel_type (str): Type of panel being constructed (e.g., 'transport', 'vibration')
        """
        self.panel_type = panel_type
        self.panel = self._create_empty_panel()

    def _create_empty_panel(self):
        """
        Initializes and returns an empty panel dictionary to collect all components.
        """
        return {
            "type": [],
            "brand": [],
            "reference_number": [],
            "specifications": [],
            "quantity": [],
            "price": [],
            "total_price": [],
            "last_price_update": [],
            "note": []
        }

    def add_to_panel(self, *, type_, brand, reference_number="-", specifications="-",
                     quantity=1, price=0, last_price_update="", note=""):
        """
        Adds a new entry to the panel dictionary.
        All parameters must be passed by keyword for clarity.
        """
        total_price = quantity * price

        self.panel["type"].append(type_)
        self.panel["brand"].append(brand)
        self.panel["reference_number"].append(reference_number)
        self.panel["specifications"].append(specifications)
        self.panel["quantity"].append(quantity)
        self.panel["price"].append(price)
        self.panel["total_price"].append(total_price)
        self.panel["last_price_update"].append(last_price_update)
        self.panel["note"].append(note)

    def choose_mpcb(self, motor, qty):
        """
        Adds an MPCB entry to the panel based on motor specifications.
        """
        if qty == 0 or motor.power_kw == 0 or motor.mpcb_qty == 0:
            return

        mpcb = get_mpcb_by_motor_power(motor.power_kw)
        total_qty = qty * motor.mpcb_qty

        self.add_to_panel(
            type_=f"MPCB FOR {motor.usage.upper()}",
            brand=mpcb.brand,
            reference_number=mpcb.mpcb_reference,
            specifications=f"Motor Power: {mpcb.p_kw} KW\nIe: {mpcb.ie_a} A",
            quantity=total_qty,
            price=12_000_000,
            note=f"{total_qty} x Motor Power: {motor.power_kw} KW"
        )

    def choose_contactor(self, motor, qty):
        """
        Adds a contactor entry to the panel based on motor specifications.
        """
        if qty == 0 or motor.power_kw == 0 or motor.contactor_qty == 0:
            return

        contactor = get_contactor_by_motor_power(motor.power_kw)
        total_qty = qty * motor.contactor_qty

        self.add_to_panel(
            type_=f"CONTACTOR FOR {motor.usage}",
            brand=contactor.brand,
            reference_number=contactor.contactor_reference,
            specifications=f"Motor Power: {contactor.p_kw} KW",
            quantity=total_qty,
            price=50_000_000,
            note=f"{total_qty} x Motor Power: {motor.power_kw} KW"
        )

    def choose_mccb(self, motor, qty):
        """
        Adds an MCCB entry to the panel based on motor specifications.
        """
        if qty == 0 or motor.power_kw == 0 or motor.mccb_qty == 0:
            return

        mccb = get_mccb_by_motor_power(motor.power_kw)
        total_qty = qty * motor.mccb_qty

        self.add_to_panel(
            type_=f"MCCB FOR {motor.usage.upper()}",
            brand=mccb.brand,
            reference_number=mccb.mccb_reference,
            specifications=f"Motor Power: {mccb.p_kw} KW\nCurrent: {mccb.i_a} A",
            quantity=total_qty,
            price=15_000_000,
            note=f"{total_qty} x Motor Power: {motor.power_kw} KW"
        )

    def calculate_plc_io_requirements(self, motor_objects, instruments=None):
        """
        Calculates total PLC I/O requirements and adds appropriate I/O cards
        """
        # Initialize all counters
        total_di = 0
        total_do = 0
        total_ai = 0
        total_ao = 0

        # Calculate I/O for motors
        di_notes = []
        do_notes = []
        ai_notes = []
        ao_notes = []
        
        for motor, qty in motor_objects:
            if qty > 0:
                motor_di = motor.plc_di * qty
                motor_do = motor.plc_do * qty
                motor_ai = motor.plc_ai * qty
                motor_ao = motor.plc_ao * qty
                total_di += motor_di
                total_do += motor_do
                total_ai += motor_ai
                total_ao += motor_ao
                if motor_di > 0:
                    di_notes.append(f"{motor.usage}: {motor_di} DI")
                if motor_do > 0:
                    do_notes.append(f"{motor.usage}: {motor_do} DO")
                if motor_ai > 0:
                    ai_notes.append(f"{motor.usage}: {motor_ai} AI")
                if motor_ao > 0:
                    ao_notes.append(f"{motor.usage}: {motor_ao} AO")

        # Calculate I/O for instruments if provided
        if instruments:
            total_di, total_ai = self.calculate_instruments_io(instruments, total_di, total_ai, di_notes, ai_notes)

        # Rest of the method remains the same...
        di_16ch = (total_di + 15) // 16  # Round up to full 16-channel cards
        do_16ch = (total_do + 15) // 16
        ai_16ch = (total_ai + 15) // 16
        ao_16ch = (total_ao + 15) // 16

        total_cards = di_16ch + do_16ch + ai_16ch + ao_16ch
        if total_cards > 8:
            # If exceeding 8 cards, switch to 32-channel cards as needed
            di_32ch = (total_di + 31) // 32
            di_16ch = 0
            remaining = 8 - di_32ch

            do_32ch = (total_do + 31) // 32 if remaining > 0 else 0
            do_16ch = 0
            remaining -= do_32ch

            ai_32ch = (total_ai + 31) // 32 if remaining > 0 else 0
            ai_16ch = 0
            remaining -= ai_32ch

            ao_32ch = (total_ao + 31) // 32 if remaining > 0 else 0
            ao_16ch = 0
        else:
            di_32ch = do_32ch = ai_32ch = ao_32ch = 0

        # Add card entries and their corresponding connectors
        if di_16ch > 0:
            self.add_to_panel(
                type_="DIGITAL INPUT 16 CHANNEL",
                brand="-",
                specifications=f"Total DI: {total_di}",
                quantity=di_16ch,
                price=0,
                note="\n".join(di_notes)
            )
        elif di_32ch > 0:
            self.add_to_panel(
                type_="DIGITAL INPUT 32 CHANNEL",
                brand="-",
                specifications=f"Total DI: {total_di}",
                quantity=di_32ch,
                price=0,
                note="\n".join(di_notes)
            )

        # Similar pattern for DO cards
        if do_16ch > 0:
            self.add_to_panel(
                type_="DIGITAL OUTPUT 16 CHANNEL",
                brand="-",
                specifications=f"Total DO: {total_do}",
                quantity=do_16ch,
                price=0,
                note="\n".join(do_notes)
            )
        elif do_32ch > 0:
            self.add_to_panel(
                type_="DIGITAL OUTPUT 32 CHANNEL",
                brand="-",
                specifications=f"Total DO: {total_do}",
                quantity=do_32ch,
                price=0,
                note="\n".join(do_notes)
            )

        # Add AI cards if needed
        if ai_16ch > 0:
            self.add_to_panel(
                type_="ANALOG INPUT 16 CHANNEL",
                brand="-",
                specifications=f"Total AI: {total_ai}",
                quantity=ai_16ch,
                price=0,
                note="\n".join(ai_notes)
            )
        elif ai_32ch > 0:
            self.add_to_panel(
                type_="ANALOG INPUT 32 CHANNEL",
                brand="-",
                specifications=f"Total AI: {total_ai}",
                quantity=ai_32ch,
                price=0,
                note="\n".join(ai_notes)
            )

        # Add AO cards if needed
        if ao_16ch > 0:
            self.add_to_panel(
                type_="ANALOG OUTPUT 16 CHANNEL",
                brand="-",
                specifications=f"Total AO: {total_ao}",
                quantity=ao_16ch,
                price=0,
                note="\n".join(ao_notes)
            )
        elif ao_32ch > 0:
            self.add_to_panel(
                type_="ANALOG OUTPUT 32 CHANNEL",
                brand="-",
                specifications=f"Total AO: {total_ao}",
                quantity=ao_32ch,
                price=0,
                note="\n".join(ao_notes)
            )

        # Calculate and add total connectors
        total_20pin = di_16ch + do_16ch + ai_16ch + ao_16ch
        total_40pin = di_32ch + do_32ch + ai_32ch + ao_32ch

        if total_20pin > 0:
            self.add_to_panel(
                type_="FRONT CONNECTOR 20PIN",
                brand="-",
                specifications="Total 20PIN connectors needed",
                quantity=total_20pin,
                price=0,
                note=f"Total connectors for all 16CH cards"
            )

        if total_40pin > 0:
            self.add_to_panel(
                type_="FRONT CONNECTOR 40PIN",
                brand="-",
                specifications="Total 40PIN connectors needed",
                quantity=total_40pin,
                price=0,
                note=f"Total connectors for all 32CH cards"
            )

    def choose_internal_signal_wire(self, motor_objects):
        """
        Adds internal signal panel wire (1x1.5) entries for each motor.
        Each motor gets 4 meters of wire if its quantity isn't 0.
        """
        total_length = 0
        notes = []

        for motor, qty in motor_objects:
            if qty > 0:
                wire_length = 4 * qty  # 4 meters per motor
                total_length += wire_length
                notes.append(f"{wire_length} m for {motor.usage}")

        if total_length == 0:
            return

        self.add_to_panel(
            type_="INTERNAL SIGNAL PANEL WIRE 1x1.5",
            brand="-",
            specifications="Size: 1x1.5 mm²",
            quantity=total_length,
            price=50_000,
            note="\n".join(notes))

    def choose_internal_power_wire(self, motor_objects):
        """
        Adds internal power panel wire or busbar based on motor power:
        - For motors <= 45kW: 4 meters of 1x1.6 wire per motor
        - For motors > 45kW: 5 meters of busbar per motor
        """
        wire_length = 0
        busbar_length = 0
        wire_notes = []
        busbar_notes = []

        for motor, qty in motor_objects:
            if qty > 0:
                if motor.power_kw <= 45:
                    motor_wire_length = 4 * qty
                    wire_length += motor_wire_length
                    wire_notes.append(f"{motor_wire_length} m for {motor.usage}")
                else:
                    motor_busbar_length = 5 * qty
                    busbar_length += motor_busbar_length
                    busbar_notes.append(f"{motor_busbar_length} m for {motor.usage}")

        if wire_length > 0:
            self.add_to_panel(
                type_="INTERNAL POWER PANEL WIRE 1x1.6",
                brand="-",
                specifications="Size: 1x1.6 mm²",
                quantity=wire_length,
                price=60_000,
                note="\n".join(wire_notes)
            )

        if busbar_length > 0:
            self.add_to_panel(
                type_="POWER BUSBAR",
                brand="-",
                specifications="For motors > 45kW",
                quantity=busbar_length,
                price=250_000,
                note="\n".join(busbar_notes))

    def choose_general(self, motor_objects, general_items=[]):
        """
        Adds general accessories like terminals, buttons, etc. based on motor needs.
        """
        if not general_items:
            general_items = [
                "lcb", "terminal_4", "terminal_6",
                "contactor_aux_contact", "mpcb_mccb_aux_contact",
                "relay_1no_1nc", "relay_2no_2nc",
                "button", "selector_switch",
                "duct_cover", "miniatory_rail", "junction_box_for_speed"
            ]
        for item_name in general_items:
            total_qty = 0
            notes = []

            for motor, qty in motor_objects:
                if qty > 0:
                    item_qty = getattr(motor, f"{item_name}_qty")
                    total_qty += qty * item_qty
                    notes.append(f"{qty}x{item_qty} for {motor.usage}")

            if total_qty == 0:
                return

            general_item = get_general_by_name(item_name)

            formatted_name = item_name.upper().replace("_", " ")
            total_qty = round(total_qty, 1)

            self.add_to_panel(
                type_=formatted_name,
                brand=general_item.brand,
                quantity=total_qty,
                price=1_000_000,
                note="\n".join(notes)
            )

    def choose_signal_cable(self, motor_objects, length):
        """
        Adds signal cable entries based on motor usage and length.
        """
        total_length = 0
        notes = []

        for motor, qty in motor_objects:
            if qty > 0:
                seg_length = length * motor.signal_cable_7x1p5_l_cofactor * qty
                total_length += seg_length
                notes.append(f"{seg_length:.1f} m for {motor.usage}")

        if total_length == 0:
            return

        cable = get_general_by_name("signal_cable_7x1p5")
        total_length = round(total_length, 1)

        self.add_to_panel(
            type_="SIGNAL CABLE 7x1.5",
            brand=cable.brand,
            quantity=total_length,
            price=400_000,
            note="\n".join(notes)
        )

    def choose_power_cable(self, motor_objects, length, volt):
        """
        Adds power cable entries with sizing based on current and motor demand.
        """
        cable_grouping = defaultdict(lambda: {"total_length": 0, "notes": []})
        correction_factor = 1.6 / (sqrt(3) * volt * COSNUS_PI * ETA)

        for motor, qty in motor_objects:
            if qty > 0 and motor.power_kw > 0:
                current = motor.power_kw * 1000 * correction_factor
                cable = get_cable_by_dimension_current(length=length, current=current)
                motor_length = length * motor.power_cable_cofactor * qty

                key = cable.cable_size_mm
                cable_grouping[key]["total_length"] += motor_length
                cable_grouping[key]["notes"].append(f"{motor_length:.1f} m for {motor.usage}")

        for size_mm, data in cable_grouping.items():
            total_len = round(data["total_length"], 1)
            if total_len == 0:
                continue

            self.add_to_panel(
                type_=f"POWER CABLE SIZE {size_mm}mm",
                brand="-",
                quantity=total_len,
                price=850_000,
                note="\n".join(data["notes"])
            )

    def choose_electrical_panel(self, total_motors):
        """
        Chooses electrical panel size based on number of motors.
        """
        if total_motors == 0:
            return
        elif total_motors < 3:
            panel_name, label = "electrical_panel_0p8x1", "0.8x1"
            qty = 1
        elif total_motors < 4:
            panel_name, label = "electrical_panel_0p8x1p6", "0.8x1.6"
            qty = 1
        elif total_motors < 8:
            panel_name, label = "electrical_panel_1p2x2p2", "1.2x2.2"
            qty = 1
        else:
            panel_name, label = "electrical_panel_1p2x2", "1.2x2"
            qty = 2

        panel = get_general_by_name(panel_name)

        self.add_to_panel(
            type_=f"ELECTRICAL PANEL {label}",
            brand=panel.brand,
            quantity=qty,
            price=1_000_000,
            note="")
