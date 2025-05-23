from collections import defaultdict
from math import sqrt

from config import COSNUS_PI, ETA
from controllers.project_details import ProjectDetails
from models.item_price_model import get_price
from models.items.bimetal_model import get_bimetal_by_motor_current
from models.items.contactor_model import get_contactor_by_current
from models.items.general_model import get_general_by_name
from models.items.instrument_model import get_instrument_by_type
from models.items.mccb_model import get_mccb_by_motor_current
from models.items.mpcb_model import get_mpcb_by_motor_current


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

    def add_to_panel(self, *, type, brand="", reference_number="", specifications="",
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

    """ ------------------------------------- Contactor/MPCB/MCCB/BiMetal ------------------------------------- """

    def choose_contactor(self, motor, qty):
        """
        Adds a contactor entry to the panel based on motor current specifications.
        """
        if qty == 0 or motor.current == 0 or motor.contactor_qty == 0:
            return

        contactor = get_contactor_by_current(motor.current)
        if contactor.item_id:
            price_item = get_price(contactor.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
            reference = price_item.reference
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""
            reference = ""

        total_qty = qty * motor.contactor_qty

        self.add_to_panel(
            type=f"CONTACTOR FOR {motor.usage.upper()}",
            brand=brand,
            reference_number=reference,
            specifications=f"Current: {contactor.current_a} A",
            quantity=total_qty,
            price=price,
            last_price_update=effective_date,
            note=f"{total_qty} x Motor Current: {motor.current} A {motor.usage}"
        )

    def choose_mpcb(self, motor, qty):
        """
        Adds an MPCB entry to the panel based on motor current specifications.
        """
        if qty == 0 or motor.current == 0 or motor.mpcb_qty == 0:
            return

        mpcb = get_mpcb_by_motor_current(motor.current)
        if mpcb.item_id:
            price_item = get_price(mpcb.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
            reference = price_item.reference
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""
            reference = ""

        total_qty = qty * motor.mpcb_qty

        self.add_to_panel(
            type=f"MPCB FOR {motor.usage.upper()}",
            brand=brand,
            reference_number=reference,
            specifications=(
                f"Current Range: {mpcb.min_current}A - {mpcb.max_current}A\n"
                f"Breaking Capacity: {mpcb.breaking_capacity} A\n"
                f"Trip Class: {mpcb.trip_class}"
            ),
            quantity=total_qty,
            price=price,
            last_price_update=effective_date,
            note=f"{total_qty} x Motor Current: {motor.current} A {motor.usage}"
        )

    def choose_mccb(self, motor, qty):
        """
        Adds an MCCB entry to the panel based on motor current specifications.
        """
        if qty == 0 or motor.current == 0 or motor.mccb_qty == 0:
            return

        mccb = get_mccb_by_motor_current(motor.current)
        if mccb.item_id:
            price_item = get_price(mccb.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
            reference = price_item.reference
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""
            reference = ""

        total_qty = qty * motor.mccb_qty

        self.add_to_panel(
            type=f"MCCB FOR {motor.usage.upper()}",
            brand=brand,
            reference_number=reference,
            specifications=(
                f"Breaking Capacity: {mccb.breaking_capacity} A\n"
                f"Rated Current: {mccb.rated_current} A"
            ),
            quantity=total_qty,
            price=price,
            last_price_update=effective_date,
            note=f"{total_qty} x Motor Current: {motor.current} A {motor.usage}"
        )

    def choose_bimetal(self, motor, qty):
        """
        Adds a bimetal entry to the panel based on motor current specifications.
        """
        if qty == 0 or motor.current == 0 or motor.bimetal_qty == 0:
            return

        bimetal = get_bimetal_by_motor_current(motor.current)

        if bimetal.item_id:
            price_item = get_price(bimetal.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
            reference = price_item.reference
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""
            reference = ""

        total_qty = qty * motor.bimetal_qty

        self.add_to_panel(
            type=f"BIMETAL FOR {motor.usage.upper()}",
            brand=brand,
            reference_number=reference,
            specifications=(
                f"Current Setting: {bimetal.current_setting_min} A - {bimetal.current_setting_max} A\n"
                f"Trip Time: {bimetal.trip_time} sec"
            ),
            quantity=total_qty,
            price=price,
            last_price_update=effective_date,
            note=f"{total_qty} x Motor Current: {motor.current} A {motor.usage}"
        )

    """ ------------------------------------- Generals ------------------------------------- """

    def choose_general(self, motor_objects):
        """
        Adds general accessories like terminals, buttons, etc. based on motor needs.
        """
        general_items = [
            "lcb", "terminal_4", "terminal_6",
            "contactor_aux_contact", "mpcb_mccb_aux_contact",
            "relay_1no_1nc", "relay_2no_2nc",
            "button", "selector_switch",
            "duct_cover", "miniatory_rail", "junction_box_for_speed"
        ]
        has_hmi = False if self.project_details["bagfilter"]["touch_panel"] == "None" else True
        if not has_hmi:
            general_items.append("signal_lamp_24v")

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

    """ ------------------------------------- Instrument ------------------------------------- """

    def choose_instruments(self, instruments):
        """
        Adds instrument entries to panel.
        """
        for instrument_name, properties in instruments.items():
            qty = properties["qty"]
            if qty == 0:
                continue

            # calibration fee
            # manifolds fee

            name = "temperature_transmitter" if instrument_name == "inlet_temperature_transmitter" \
                                                or instrument_name == "outlet_temperature_transmitter" \
                                                or instrument_name == "bearing_temperature_transmitter" \
                                                or instrument_name == "pt100" \
                else instrument_name
            name = "vibration_transmitter" if name == "bearing_vibration_transmitter" else name

            instrument = get_instrument_by_type(name)
            price_item = get_price(instrument.item_id, properties["brand"])

            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"

            self.add_to_panel(
                type=instrument_name.upper().replace("_", " "),
                brand=properties["brand"],
                specifications="",
                quantity=qty,
                price=price,
                last_price_update=effective_date)

            # ------------ Choose Manifold ------------
            manifold_qty = 0
            if "delta" in name:
                manifold = "3ways_manifold"
                manifold_qty = qty
            elif "pressure" in name:
                manifold = "2ways_manifold"
                manifold_qty = qty

            if manifold_qty > 0:
                general_item = get_general_by_name(manifold)
                if general_item.item_id:
                    price_item = get_price(general_item.item_id, brand=False, item_brand=False)
                    price = price_item.price if price_item.price else 0
                    effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
                    brand = price_item.brand
                else:
                    price = 0
                    effective_date = "Not Found"
                    brand = ""

                formatted_name = manifold.upper().replace("_", " ")

                self.add_to_panel(
                    type=formatted_name,
                    brand=brand,
                    quantity=qty,
                    price=price,
                    last_price_update=effective_date,
                    note=f"manifold for {instrument_name}"
                )

            # ------------ Calibration ------------
            if "transmitter" in name and qty != 0:
                general_item = get_general_by_name("calibration")
                if general_item.item_id:
                    price_item = get_price(general_item.item_id, brand=False, item_brand=False)
                    price = price_item.price if price_item.price else 0
                    effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
                    brand = price_item.brand
                else:
                    price = 0
                    effective_date = "Not Found"
                    brand = ""

                self.add_to_panel(
                    type="CALIBRATION",
                    brand=brand,
                    quantity=qty,
                    price=price,
                    last_price_update=effective_date,
                    note=f"calibration for {instrument_name}"
                )

    def calculate_plc_io_requirements(self, motor_objects, instruments=None):
        total_di = total_do = total_ai = total_ao = 0
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

        if instruments:
            total_di, total_ai = self.calculate_instruments_io(instruments, total_di, total_ai, di_notes, ai_notes)

        # Calculate DI cards
        if total_di > 0:
            di_cards = max(1, (total_di + 15) // 16)
            self.add_io_card_to_panel("DI 16 CHANNEL", "di_16_channel", di_cards, total_di, di_notes)
        else:
            di_cards = 0

        # Calculate DO cards
        if total_do > 0:
            do_cards = max(1, (total_do + 15) // 16)
            self.add_io_card_to_panel("DO 16 CHANNEL", "do_16_channel", do_cards, total_do, do_notes)
        else:
            do_cards = 0

        # Calculate AI cards
        if total_ai > 0:
            ai_cards = max(1, (total_ai + 15) // 16)
            self.add_io_card_to_panel("AI 16 CHANNEL", "ai_16_channel", ai_cards, total_ai, ai_notes)
        else:
            ai_cards = 0

        # Calculate AO cards
        if total_ao > 0:
            ao_cards = max(1, (total_ao + 15) // 16)
            self.add_io_card_to_panel("AO 16 CHANNEL", "ao_16_channel", ao_cards, total_ao, ao_notes)
        else:
            ao_cards = 0

        total_20pin = di_cards + do_cards + ai_cards + ao_cards
        if total_20pin > 0:
            pin_card = get_general_by_name("front_connector_20_pin")
            if pin_card.item_id:
                price_item = get_price(pin_card.item_id, brand=False, item_brand=False)
                price = price_item.price if price_item.price else 0
                effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
                brand = price_item.brand
            else:
                price = 0
                effective_date = "Not Found"
                brand = ""
            self.add_to_panel(
                type="FRONT CONNECTOR 20PIN",
                brand=brand,
                quantity=total_20pin,
                price=price,
                last_price_update=effective_date,
                note="Total connectors for all 16CH cards"
            )

    def add_io_card_to_panel(self, label, general_name, qty, total, notes):
        card = get_general_by_name(general_name)
        if card.item_id:
            price_item = get_price(card.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""
        self.add_to_panel(
            type=label,
            brand=brand,
            specifications=f"Total: {total}",
            quantity=qty,
            price=price,
            last_price_update=effective_date,
            note="\n".join(notes)
        )

    def calculate_instruments_io(self, instruments, total_di, total_ai, di_notes, ai_notes):
        instruments_pins = {
            'delta_pressure_transmitter': {'n_di': 0, 'n_ai': 1},
            'delta_pressure_switch': {'n_di': 1, 'n_ai': 0},
            'pressure_transmitter': {'n_di': 0, 'n_ai': 1},
            'pressure_switch': {'n_di': 1, 'n_ai': 0},
            'pressure_gauge': {'n_di': 0, 'n_ai': 0},
            'temperature_transmitter': {'n_di': 0, 'n_ai': 1},
            'proximity_switch': {'n_di': 1, 'n_ai': 0},
            'vibration_transmitter': {'n_di': 0, 'n_ai': 1},
            'speed_detector': {'n_di': 1, 'n_ai': 0},
            'level_switch': {'n_di': 1, 'n_ai': 0},
            'level_transmitter': {'n_di': 0, 'n_ai': 1},
            'ptc': {'n_di': 0, 'n_ai': 0}
        }

        for instrument_name, properties in instruments.items():

            name = "temperature_transmitter" if instrument_name == "inlet_temperature_transmitter" \
                                                or instrument_name == "outlet_temperature_transmitter" \
                                                or instrument_name == "bearing_temperature_transmitter" \
                                                or instrument_name == "pt100" \
                else instrument_name
            name = "vibration_transmitter" if name == "bearing_vibration_transmitter" else name

            n_di = instruments_pins[name]["n_di"]
            n_ai = instruments_pins[name]["n_ai"]
            if properties["qty"] > 0:
                if n_di > 0:
                    total_di += n_di * properties["qty"]
                    di_notes.append(f"{instrument_name}: {properties['qty']}*{n_di} DI")
                if n_ai > 0:
                    total_ai += n_ai * properties["qty"]
                    ai_notes.append(f"{instrument_name}: {properties['qty']}*{n_ai} AI")

        return total_di, total_ai

    """ ------------------------------------- Wire and Cable ------------------------------------- """

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

        total_length = round(total_length, 1)  # round to 1 point float
        if total_length == 0:
            return

        cable = get_general_by_name("cable_7x1p5")
        price_item = get_price(cable.item_id, brand="", item_brand=False)  # brand doent matter in this stage

        price = price_item.price if price_item.price else 0
        effective_date = price_item.effective_date if price_item.effective_date else "Not Found"

        self.add_to_panel(
            type="SIGNAL CABLE 7x1.5",
            quantity=total_length,
            price=price,
            last_price_update=effective_date,
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
            if qty > 0 and motor.power > 0:
                current = motor.power * correction_factor
                cable = cable_rating(cable_length_m=length, cable_current_a=current)
                if cable:
                    motor_length = length * motor.power_cable_cofactor * qty
                    cable_grouping[cable]["total_length"] += motor_length
                    cable_grouping[cable]["notes"].append(f"{motor_length:.1f} m for {motor.usage}")
                else:
                    self.add_to_panel(
                        type=f"POWER CABLE",
                        note="POWER CABLE For {motor.usage} Not Found"
                    )

        for size_mm, data in cable_grouping.items():
            total_len = round(data["total_length"], 1)
            if total_len == 0:
                continue

            cable_name = "cable_4x" + str(size_mm).replace(".", "p")
            cable = get_general_by_name(cable_name)
            price_item = get_price(cable.item_id, brand="", item_brand=False)  # brand doesnt matter in this stage

            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"

            self.add_to_panel(
                type=f"POWER CABLE SIZE 4x{size_mm}mm²",
                quantity=total_len,
                price=price,
                last_price_update=effective_date,
                note="\n".join(data["notes"])
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

        cable = get_general_by_name("cable_1x1p5")
        price_item = get_price(cable.item_id, brand="", item_brand=False)  # brand doesnt matter in this stage

        price = price_item.price if price_item.price else 0
        effective_date = price_item.effective_date if price_item.effective_date else "Not Found"

        self.add_to_panel(
            type="INTERNAL SIGNAL PANEL WIRE 1x1.5",
            specifications="Size: 1x1.5 mm²",
            quantity=total_length,
            price=price,
            last_price_update=effective_date,
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
                if motor.power <= 45:
                    motor_wire_length = 4 * qty
                    wire_length += motor_wire_length
                    wire_notes.append(f"{motor_wire_length} m for {motor.usage}")
                else:
                    motor_busbar_length = 5 * qty
                    busbar_length += motor_busbar_length
                    busbar_notes.append(f"{motor_busbar_length} m for {motor.usage}")

        if wire_length > 0:
            cable = get_general_by_name("cable_1x1p6")
            price_item = get_price(cable.item_id, brand="", item_brand=False)  # brand doesnt matter in this stage

            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"

            self.add_to_panel(
                type="INTERNAL POWER PANEL WIRE 1x1.6mm²",
                specifications="Size: 1x1.6 mm²",
                quantity=wire_length,
                price=price,
                last_price_update=effective_date,
                note="\n".join(wire_notes)
            )

        if busbar_length > 0:
            cable = get_general_by_name("busbar")
            price_item = get_price(cable.item_id, brand="", item_brand=False)  # brand doesnt matter in this stage

            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"

            self.add_to_panel(
                type="INTERNAL POWER BUSBAR",
                specifications="For motors > 45kW",
                quantity=busbar_length,
                price=price,
                last_price_update=effective_date,
                note="\n".join(busbar_notes))

    """ ------------------------------------- Calculate Motor Current ------------------------------------- """

    def calculate_motor_current(self, power, volt=None):
        if volt is None:
            volt = self.project_details["project_info"]["project_l_voltage"]

        return round(power / (sqrt(3) * volt * COSNUS_PI * ETA), 2)


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
