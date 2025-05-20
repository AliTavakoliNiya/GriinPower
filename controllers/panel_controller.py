from collections import defaultdict
from math import sqrt

from config import COSNUS_PI, ETA
from models.items.cable_rating_model import get_cable_by_dimension_current
from models.items.contactor_model import get_contactor_by_motor_power
from models.items.general_model import get_general_by_name
from models.items.instrument_model import get_instrument_by_type
from models.items.mpcb_model import get_mpcb_by_motor_power
from models.items.mccb_model import get_mccb_by_motor_power
from models.item_price_model import get_price

from controllers.project_details import ProjectDetails


class PanelController:
    """
    Base controller class for building electrical panels from project specifications.
    """

    def __init__(self, panel_type):
        """
        Initialize the panel controller with a specific panel type.
        """
        self.panel_type = panel_type
        self.panel = self._create_empty_panel()
        self.project_details = ProjectDetails()

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

    def add_to_panel(self, *, type, brand, reference_number="-", specifications="-",
                     quantity=1, price=0, last_price_update="", note=""):
        """
        Adds a new entry to the panel dictionary.
        All parameters must be passed by keyword for clarity.
        """
        total_price = quantity * price

        self.panel["type"].append(type)
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
        if mpcb.item_id:
            price_item = get_price(mpcb.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""
        total_qty = qty * motor.mpcb_qty

        self.add_to_panel(
            type=f"MPCB FOR {motor.usage.upper()}",
            brand=brand,
            reference_number=mpcb.mpcb_reference,
            specifications=f"Motor Power: {mpcb.p_kw} KW\nIe: {mpcb.ie_a} A",
            quantity=total_qty,
            price=price,
            last_price_update=effective_date,
            note=f"{total_qty} x Motor Power: {motor.power_kw} KW {motor.usage}"
        )

    def choose_contactor(self, motor, qty):
        """
        Adds a contactor entry to the panel based on motor specifications.
        """
        if qty == 0 or motor.power_kw == 0 or motor.contactor_qty == 0:
            return

        contactor = get_contactor_by_motor_power(motor.power_kw)
        if contactor.item_id:
            price_item = get_price(contactor.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""

        total_qty = qty * motor.contactor_qty

        self.add_to_panel(
            type=f"CONTACTOR FOR {motor.usage}",
            brand=brand,
            reference_number=contactor.contactor_reference,
            specifications=f"Motor Power: {contactor.p_kw} KW",
            quantity=total_qty,
            price=price,
            last_price_update=effective_date,
            note=f"{total_qty} x Motor Power: {motor.power_kw} KW {motor.usage}"
        )

    def choose_mccb(self, motor, qty):
        """
        Adds an MCCB entry to the panel based on motor specifications.
        """
        if qty == 0 or motor.power_kw == 0 or motor.mccb_qty == 0:
            return

        mccb = get_mccb_by_motor_power(motor.power_kw)
        if mccb.item_id:
            price_item = get_price(mccb.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""
        total_qty = qty * motor.mpcb_qty

        self.add_to_panel(
            type=f"MCCB FOR {motor.usage.upper()}",
            brand=brand,
            reference_number=mccb.mccb_reference,
            specifications=f"For Motor Power: {mccb.p_kw} KW\nCurrent: {mccb.i_a} A",
            quantity=total_qty,
            price=price,
            last_price_update=effective_date,
            note=f"{total_qty} x Motor Power: {motor.power_kw} KW {motor.usage}"
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
            type="INTERNAL SIGNAL PANEL WIRE 1x1.5",
            brand="check this out",
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
                type="INTERNAL POWER PANEL WIRE 1x1.6",
                brand="check this out",
                specifications="Size: 1x1.6 mm²",
                quantity=wire_length,
                price=60_000,
                note="\n".join(wire_notes)
            )

        if busbar_length > 0:
            self.add_to_panel(
                type="POWER BUSBAR",
                brand="check this out",
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
            if general_item.item_id:
                price_item = get_price(general_item.item_id, brand=False, item_brand=False)
                price = price_item.price if price_item.price else 0
                effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
                brand = price_item.brand
            else:
                price = 0
                effective_date = "Not Found"
                brand = ""

            formatted_name = item_name.upper().replace("_", " ")
            total_qty = round(total_qty, 1)

            self.add_to_panel(
                type=formatted_name,
                brand=brand,
                quantity=total_qty,
                price=price,
                last_price_update=effective_date,
                note="\n".join(notes)
            )

    def choose_signal_cable(self, motor_objects):
        """
        Adds signal cable entries based on motor usage and length.
        """

        length = self.project_details["bagfilter"]["cable_dimension"]
        if length == 0:
            return

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
            type="SIGNAL CABLE 7x1.5",
            brand="check this out",
            quantity=total_length,
            price=400_000,
            note="\n".join(notes)
        )

    def choose_power_cable(self, motor_objects):
        """
        Adds power cable entries with sizing based on current and motor demand.
        """
        volt = self.project_details["project_info"]["project_l_voltage"]
        length = self.project_details["bagfilter"]["cable_dimension"]
        if length == 0:
            return

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
                type=f"POWER CABLE SIZE {size_mm}mm",
                brand="check this out",
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
        if panel.item_id:
            price_item = get_price(panel.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""

        self.add_to_panel(
            type=f"ELECTRICAL PANEL {label}",
            brand=brand,
            quantity=qty,
            price=price,
            last_price_update=effective_date,
            note="")

    def choose_instruments(self, instruments):
        """
        Adds instrument entries to panel.
        """
        for instrument_name, properties in instruments.items():
            # calibration fee
            # manifolds fee

            instrument = get_instrument_by_type(instrument_name)
            price_item = get_price(instrument.item_id, properties["brand"])

            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"

            qty = properties["qty"]
            if qty > 0:
                self.add_to_panel(
                    type=instrument.type,
                    brand=properties["brand"],
                    specifications="",
                    quantity=qty,
                    price=price,
                    last_price_update=effective_date,
                    note=str(instrument.note) + " <calibration fee & manifolds fee>")
