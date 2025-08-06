import math
from math import sqrt
from collections import defaultdict
from config import COSNUS_PI, ETA
from controllers.tender_application.project_session_controller import ProjectSession
from models.items.bimetal import get_bimetal_by_current
from models.items.contactor import get_contactor_by_current
from models.items.electrical_panel import get_electrical_panel_by_spec
from models.items.general import get_general_by_spec
from models.items.instrument import get_instrument_by_spec
from models.items.mccb import get_mccb_by_current
from models.items.mpcb import get_mpcb_by_current
from models.items.vfd_softstarter import get_vfd_softstarter_by_power
from models.items.wire_cable import get_wire_cable_by_spec


class PanelController:
    """
    Base controller class for building electrical panels from tender_application specifications.
    """

    def __init__(self, panel_type):
        """
        Initialize the panel controller with a specific panel type.
        """
        self.panel_type = panel_type
        self.panel = self._create_empty_panel()
        self.electrical_specs = ProjectSession().project_electrical_specs

    def _create_empty_panel(self):
        """
        Initializes and returns an empty panel dictionary to collect all components.
        """
        return {
            "type": [],
            "brand": [],
            "order_number": [],
            "specifications": [],
            "quantity": [],
            "price": [],
            "total_price": [],
            "last_price_update": [],
            "note": []
        }

    def add_to_panel(self, *, type, brand="", order_number="", specifications="",
                     quantity=0, price=0, last_price_update="", note=""):
        """
        Adds a new entry to the panel dictionary.
        All parameters must be passed by keyword for clarity.
        """
        total_price = quantity * price

        self.panel["type"].append(type)
        self.panel["brand"].append(brand)
        self.panel["specifications"].append(specifications)
        self.panel["quantity"].append(quantity)
        self.panel["price"].append(price)
        self.panel["total_price"].append(total_price)
        self.panel["last_price_update"].append(last_price_update)
        self.panel["note"].append(note)
        self.panel["order_number"].append(order_number)

    """ ------------------------------------- Contactor/MPCB/MCCB/BiMetal ------------------------------------- """

    def choose_contactor(self, motor, qty):
        """
        Adds a contactor entry to the panel based on motor current specifications.
        """
        if qty == 0 or motor.current == 0 or motor.contactor_qty == 0:
            return
        total_qty = qty * motor.contactor_qty

        success, contactor = get_contactor_by_current(rated_current=motor.current * 1.25,
                                                      brands=self.electrical_specs["project_info"]["proj_avl"])
        if success:
            self.add_to_panel(
                type=f"Contactor",
                brand=contactor["brand"],
                order_number=contactor["order_number"],
                specifications=f"Current: {contactor['rated_current']}A",
                quantity=total_qty,
                price=contactor['price'],
                last_price_update=f"{contactor['supplier_name']}\n{contactor['date']}",
                note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
            )
        else:
            self.add_to_panel(
                type=f"Contactor",
                brand="",
                order_number="",
                specifications=f"At Least: {motor.current * 1.25:.2f}A",
                quantity=total_qty,
                price=0,
                last_price_update="❌ Contactor not found",
                note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
            )

    def choose_mpcb(self, motor, qty):
        """
        Adds an MPCB entry to the panel based on motor current specifications.
        """
        if qty == 0 or motor.current == 0 or motor.mpcb_qty == 0:
            return
        total_qty = qty * motor.mpcb_qty

        success, mpcb = get_mpcb_by_current(rated_current=motor.current * 1.25,
                                            brands=self.electrical_specs["project_info"]["proj_avl"])
        if success:
            self.add_to_panel(
                type=f"MPCB",
                brand=mpcb["brand"],
                order_number=mpcb["order_number"],
                specifications=f"Current: {mpcb['min_current']}A ~ {mpcb['max_current']}A\n"
                               f"Breaking Capacity: {mpcb['breaking_capacity']}, Trip Class: {mpcb['trip_class']}",
                quantity=total_qty,
                price=mpcb['price'],
                last_price_update=f"{mpcb['supplier_name']}\n{mpcb['date']}",
                note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
            )
        else:
            self.add_to_panel(
                type=f"MPCB",
                brand="",
                order_number="",
                specifications=f"At Least: {motor.current * 1.25:.2f}A",
                quantity=total_qty,
                price=0,
                last_price_update="❌ MPCB not found",
                note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
            )

    def choose_mccb(self, motor, qty):
        """
        Adds an MCCB entry to the panel based on motor current specifications.
        """

        if qty == 0 or motor.current == 0 or motor.mccb_qty == 0:
            return
        total_qty = qty * motor.mccb_qty

        success, mccb = get_mccb_by_current(rated_current=motor.current * 1.25,
                                            brands=self.electrical_specs["project_info"]["proj_avl"])
        if success:
            self.add_to_panel(
                type=f"MCCB",
                brand=mccb["brand"],
                order_number=mccb["order_number"],
                specifications=f"Current: {mccb['rated_current']}A\nBreaking Capacity:{mccb['breaking_capacity']}KA",
                quantity=total_qty,
                price=mccb['price'],
                last_price_update=f"{mccb['supplier_name']}\n{mccb['date']}",
                note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
            )
        else:
            self.add_to_panel(
                type=f"MCCB",
                brand="",
                order_number="",
                specifications=f"At Least: {motor.current * 1.25:.2f}A",
                quantity=total_qty,
                price=0,
                last_price_update="❌ MCCB not found",
                note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
            )

    def choose_bimetal(self, motor, qty):
        """
        Adds a bimetal entry to the panel based on motor current specifications.
        """
        if qty == 0 or motor.current == 0 or motor.bimetal_qty == 0:
            return
        total_qty = qty * motor.bimetal_qty

        success, bimetal = get_bimetal_by_current(rated_current=motor.current * 1.25,
                                                  brands=self.electrical_specs["project_info"]["proj_avl"])

        if success:
            self.add_to_panel(
                type=f"Bimetal",
                brand=bimetal["brand"],
                order_number=bimetal["order_number"],
                specifications=(
                    f"Current: {bimetal['min_current']}A ~ {bimetal['max_current''']}A\n"
                    f"Tripping Threshold: {bimetal['tripping_threshold']} A"),
                quantity=total_qty,
                price=bimetal['price'],
                last_price_update=f"{bimetal['supplier_name']}\n{bimetal['date']}",
                note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
            )
        else:
            self.add_to_panel(
                type=f"Bimetal",
                brand="",
                order_number="",
                specifications=f"At Least: {motor.current * 1.25:.2f}A",
                quantity=total_qty,
                price=0,
                last_price_update="❌ BIMETAL not found",
                note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
            )

    def choose_vfd(self, motor, total_qty):
        """
        Adds a VFD to the panel based on motor current specifications.
        """
        if total_qty == 0:
            return

        success, vfd = get_vfd_softstarter_by_power(type="VFD", power=motor.power,
                                                    brands=self.electrical_specs["project_info"]["proj_avl"])

        if success:
            if success:
                self.add_to_panel(
                    type=f"VFD",
                    brand=vfd["brand"],
                    order_number=vfd["order_number"],
                    specifications=f"Power: {vfd['power']}",
                    quantity=total_qty,
                    price=vfd['price'],
                    last_price_update=f"{vfd['supplier_name']}\n{vfd['date']}",
                    note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
                )
            else:
                self.add_to_panel(
                    type=f"VFD",
                    brand="",
                    order_number="",
                    specifications=f"At Least: {motor.power / 1000}KW",
                    quantity=total_qty,
                    price=0,
                    last_price_update="❌ VFD not found",
                    note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
                )

    def choose_soft_starter(self, motor, total_qty):
        """
        Adds a Soft Starter to the panel based on motor current specifications.
        """
        if total_qty == 0:
            return

        success, soft_starter = get_vfd_softstarter_by_power(type="SoftStarter", power=motor.power,
                                                             brands=self.electrical_specs["project_info"]["proj_avl"])
        if success:
            if success:
                self.add_to_panel(
                    type=f"SoftStarter",
                    brand=soft_starter["brand"],
                    order_number=soft_starter["order_number"],
                    specifications=f"Power: {soft_starter['power']}",
                    quantity=total_qty,
                    price=soft_starter['price'],
                    last_price_update=f"{soft_starter['supplier_name']}\n{soft_starter['date']}",
                    note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
                )
            else:
                self.add_to_panel(
                    type=f"SoftStarter",
                    brand="",
                    order_number="",
                    specifications=f"At Least: {motor.power / 1000}KW",
                    quantity=total_qty,
                    price=0,
                    last_price_update="❌ VFD not found",
                    note=f"{total_qty} x Motor Current: {motor.current}A {motor.usage}"
                )

    """ ------------------------------------- Generals ------------------------------------- """

    def process_item(self, motor_objects, attr_name, comp_type, specification=""):
        success, item = get_general_by_spec(comp_type, specification)

        total_qty = 0
        notes = []
        for motor, qty in motor_objects:
            if qty > 0:
                item_qty = getattr(motor, attr_name, 0)
                total_qty += qty * item_qty
                notes.append(f"{qty}x{item_qty} for {motor.usage}")

        if total_qty > 0:
            if success:
                self.add_to_panel(
                    type=f"{comp_type} {specification}",
                    brand=item.get("brand", ""),
                    order_number=item.get("order_number", ""),
                    specifications=item.get("specification", ""),
                    quantity=round(total_qty, 2),
                    price=item.get("price", 0),
                    last_price_update=f"{item.get('supplier_name', '')}\n{item.get('date', '')}",
                    note="\n".join(notes)
                )
            else:
                self.add_to_panel(
                    type=f"{comp_type} {specification}",
                    brand="",
                    order_number="",
                    specifications=specification,
                    quantity=round(total_qty, 2),
                    price=0,
                    last_price_update=f"❌ {comp_type} not found",
                    note="\n".join(notes)
                )

    def choose_general(self, motor_objects):
        """
        Adds general accessories like terminals, buttons, etc. based on motor needs.
        """

        self.process_item(motor_objects=motor_objects, attr_name="terminal_4_qty", comp_type="Terminal",
                          specification="4")
        self.process_item(motor_objects=motor_objects, attr_name="terminal_6_qty", comp_type="Terminal",
                          specification="6")
        self.process_item(motor_objects=motor_objects, attr_name="contactor_aux_contact_qty",
                          comp_type="Contactor Aux Contact")
        self.process_item(motor_objects=motor_objects, attr_name="mccb_aux_contact_qty",
                          comp_type="MCCB Aux Contact")
        self.process_item(motor_objects=motor_objects, attr_name="mpcb_aux_contact_qty",
                          comp_type="MPCB Aux Contact")
        self.process_item(motor_objects=motor_objects, attr_name="relay_1no_1nc_qty", comp_type="Relay",
                          specification="1")
        self.process_item(motor_objects=motor_objects, attr_name="relay_2no_2nc_qty", comp_type="Relay",
                          specification="2")
        self.process_item(motor_objects=motor_objects, attr_name="button_qty", comp_type="Button")
        self.process_item(motor_objects=motor_objects, attr_name="selector_switch_qty", comp_type="Selector Switch")

        self.choose_duct_cover(motor_objects)
        self.choose_miniatory_rail(motor_objects)

        has_hmi = True if self.electrical_specs["bagfilter"]["touch_panel"] else False
        if not has_hmi:
            self.process_item(motor_objects=motor_objects, attr_name="signal_lamp_24v_qty", comp_type="Signal Lamp",
                              specification="24")

    def choose_electrical_panel(self, total_motors):
        """
        Chooses electrical panel size based on number of motors and retrieves real component data.
        """
        if total_motors == 0:
            return
        elif total_motors < 3:
            width, height, depth = 800, 1000, 300
            qty = 1
        elif total_motors < 4:
            width, height, depth = 800, 1600, 300
            qty = 1
        elif total_motors < 8:
            width, height, depth = 1200, 2200, 600
            qty = 1
        else:
            width, height, depth = 1200, 2000, 600
            qty = 2

        success, electrical_panel = get_electrical_panel_by_spec(type="Electrical Panel", width=width, height=height, depth=depth)
        if success:
            self.add_to_panel(
                type="Electrical Panel",
                brand=electrical_panel.get("brand", ""),
                order_number="",
                specifications=f"{width}mm x {height}mm x {depth}mm",
                quantity=qty,
                price=electrical_panel.get("price", 0),
                last_price_update=f"{electrical_panel.get('supplier_name', '')}\n{electrical_panel.get('date', '')}",
                note=f"total motors: {total_motors}"
            )
        else:
            self.add_to_panel(
                type="Electrical Panel",
                brand="",
                order_number="",
                specifications=f"{width}mm x {height}mm x {depth}mm",
                quantity=qty,
                price=0,
                last_price_update="❌ Electrical Panel not found",
                note=f"total motors: {total_motors}"
            )

    """ ------------------------------------- Instrument ------------------------------------- """

    def choose_instruments(self, instruments):
        """
        Adds instrument entries to panel.
        """
        for instrument_name, properties in instruments.items():
            qty = properties["qty"]
            if qty == 0:
                continue

            name = "temperature_transmitter" if instrument_name == "inlet_temperature_transmitter" \
                                                or instrument_name == "outlet_temperature_transmitter" \
                                                or instrument_name == "bearing_temperature_transmitter" \
                                                or instrument_name == "pt100" \
                else instrument_name
            name = "vibration_transmitter" if name == "bearing_vibration_transmitter" else name

            success, instrument = get_instrument_by_spec(name.replace('_', ' ').title(), brand=properties["brand"])

            if success:
                self.add_to_panel(
                    type=instrument_name.title().replace("_", " "),
                    brand=instrument["brand"],
                    order_number=instrument["order_number"],
                    specifications="",
                    quantity=qty,
                    price=instrument["price"],
                    last_price_update=f"{instrument['supplier_name']}\n{instrument['date']}",
                )
            else:
                self.add_to_panel(
                    type=instrument_name.title().replace("_", " "),
                    brand="",
                    order_number="",
                    specifications="",
                    quantity=qty,
                    price=0,
                    last_price_update=f"❌ Instrument not found",
                )

            # ------------ Choose Manifold ------------
            manifold_qty = 0
            manifold_ways = None
            if "delta" in name.lower():
                manifold_ways = "3 Ways Manifold"
                manifold_qty = qty
            elif "pressure" in name.lower():
                manifold_ways = "2 Ways Manifold"
                manifold_qty = qty

            if manifold_qty > 0 and manifold_ways:
                formatted_name = f"{manifold_ways} WAYS MANIFOLD"

                success, manifold_obj = get_instrument_by_spec(type=manifold_ways)
                if success:
                    self.add_to_panel(
                        type=formatted_name,
                        brand=manifold_obj['brand'],
                        order_number=manifold_obj['order_number'],
                        quantity=qty,
                        price=manifold_obj['price'],
                        last_price_update=f"{manifold_obj['supplier_name']}\n{manifold_obj['date']}",
                        note=f"Manifold for {instrument_name.replace('_', ' ').title()}")
                else:
                    self.add_to_panel(
                        type=formatted_name,
                        brand="",
                        order_number="",
                        quantity=qty,
                        price=0,
                        last_price_update=f"❌Manifold not found",
                        note=f"Manifold for {instrument_name.replace('_', ' ').title()}")

            # ------------ Calibration ------------
            if "proximity_switch" != name and "speed_detector" != name and "ptc" != name and qty != 0:
                calibration_name = instrument_name.title().replace("_", " ") + " Calibration"
                success, calibration = get_instrument_by_spec(type=calibration_name)
                if success:
                    self.add_to_panel(
                        type=calibration_name,
                        brand=calibration['brand'],
                        quantity=qty,
                        price=calibration['price'],
                        last_price_update=f"{calibration['supplier_name']}\n{calibration['date']}",
                        note=f"Calibration for {instrument_name.replace('_', ' ').title()}"
                    )
                else:
                    self.add_to_panel(
                        type=calibration_name,
                        brand="",
                        quantity=qty,
                        price=0,
                        last_price_update=f"❌ Calibration not found",
                        note=f"Calibration for {instrument_name.replace('_', ' ').title()}"

                    )

    def calculate_plc_io_requirements(self, motor_objects, instruments=None):
        total_di = total_do = total_ai = total_ao = 0
        di_notes, do_notes, ai_notes, ao_notes = [], [], [], []

        for motor, qty in motor_objects:
            if qty <= 0:
                continue
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

        # Cards calculation
        di_cards = self.calculate_and_add_io("DI", total_di, di_notes)
        do_cards = self.calculate_and_add_io("DO", total_do, do_notes)
        ai_cards = self.calculate_and_add_io("AI", total_ai, ai_notes)
        ao_cards = self.calculate_and_add_io("AO", total_ao, ao_notes)

        total_20pin = di_cards + do_cards + ai_cards + ao_cards
        if total_20pin > 0 and self.electrical_specs["bagfilter"]["plc_series"]=="S7-300 Series":
            success, pin_card = get_general_by_spec(type="Front Connector", specification="20")
            if success:
                self.add_to_panel(
                    type=f"Front Connector 20Pins",
                    brand=pin_card["brand"],
                    order_number=pin_card["order_number"],
                    quantity=total_20pin,
                    price=pin_card['price'],
                    last_price_update=f"{pin_card['supplier_name']}\n{pin_card['date']}",
                    note="Total connectors for all 16CH cards"
                )
            else:
                self.add_to_panel(
                    type=f"Front Connector 20Pins",
                    brand="",
                    order_number="",
                    specifications="",
                    quantity=total_20pin,
                    price=0,
                    last_price_update="❌ Front Connector not found",
                    note="Total connectors for all 16CH cards"
                )

    def calculate_and_add_io(self, io_type, total, notes):
        if total <= 0:
            return 0

        cards = max(1, (total + 15) // 16)  # 16-channel cards
        if io_type == "DI":
            success, card = get_general_by_spec(type="DI Module", specification="16")
        elif io_type == "DO":
            success, card = get_general_by_spec(type="DO Module", specification="16")
        elif io_type == "AI":
            success, card = get_general_by_spec(type="AI Module", specification="16")
        elif io_type == "AO":
            success, card = get_general_by_spec(type="AO Module", specification="16")

        if success:
            price = card["price"] or 0
            effective_date = f"{card['supplier_name']}\n{card['date']}" or "Not Found"
            brand = card["brand"]
        else:
            price = 0
            effective_date = f"❌ Channel card not found"
            brand = ""

        self.add_to_panel(
            type=f"{io_type} 16 Channel",
            brand=brand,
            specifications=f"Total: {total} {io_type}s",
            quantity=cards,
            price=price,
            last_price_update=effective_date,
            note="\n".join(notes)
        )
        return cards

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

    def choose_miniatory_rail(self, motor_objects):

        rail_length = 0
        rail_notes = []

        for motor, qty in motor_objects:
            if qty > 0:
                motor_wire_length = qty * motor.miniatory_rail_qty
                rail_length += motor_wire_length
                rail_notes.append(f"{motor_wire_length} m for {motor.usage}")

        if rail_length > 0:
            success, rail = get_wire_cable_by_spec("MiniatoryRail", 1)
            if success:
                self.add_to_panel(
                    type="Miniatory Rail",
                    brand=rail["brand"],
                    order_number=rail["order_number"],
                    specifications=rail["note"],
                    quantity=rail_length,
                    price=rail['price'],
                    last_price_update=f"{rail['supplier_name']}\n{rail['date']}",
                    note="\n".join(rail_notes)
                )
            else:
                self.add_to_panel(
                    type="Miniatory Rail",
                    brand="",
                    order_number="",
                    specifications="",
                    quantity=rail_length,
                    price=0,
                    last_price_update="❌ Miniatory Rail not found",
                    note="\n".join(rail_notes)
                )

    def choose_duct_cover(self, motor_objects):
        duct_length = 0
        duct_notes = []

        for motor, qty in motor_objects:
            if qty > 0:
                motor_wire_length = qty * motor.duct_cover_qty
                duct_length += motor_wire_length
                duct_notes.append(f"{motor_wire_length} m for {motor.usage}")

        if duct_length > 0:
            success, duct = get_wire_cable_by_spec("DuctCover", 1)
            if success:
                self.add_to_panel(
                    type="Duct & Cover",
                    brand=duct["brand"],
                    order_number=duct["order_number"],
                    specifications=duct["note"],
                    quantity=duct_length,
                    price=duct['price'],
                    last_price_update=f"{duct['supplier_name']}\n{duct['date']}",
                    note="\n".join(duct_notes)
                )
            else:
                self.add_to_panel(
                    type="Duct & Cover",
                    brand="",
                    order_number="",
                    specifications="",
                    quantity=duct_length,
                    price=0,
                    last_price_update="❌ Duct not found",
                    note="\n".join(duct_notes)
                )

    def choose_internal_power_wire(self, motor_objects):
        """
        Adds internal power panel wire or busbar based on motor power:
        - For motors <= 45kW: 4 meters of 1x6 wire per motor
        - For motors > 45kW: 5 meters of busbar per motor
        """
        wire_length = 0
        busbar_length = 0
        wire_notes = []
        busbar_notes = []

        for motor, qty in motor_objects:
            if qty > 0:
                if motor.power < 45000:
                    motor_wire_length = 4 * qty
                    wire_length += motor_wire_length
                    wire_notes.append(f"{motor_wire_length} m for {motor.usage}")
                else:
                    motor_busbar_length = 5 * qty
                    busbar_length += motor_busbar_length
                    busbar_notes.append(f"{motor_busbar_length} m for {motor.usage}")

        if wire_length > 0:
            success, cable = get_wire_cable_by_spec("Wire", 1, 6, brand=None, note=None)
            if success:
                self.add_to_panel(
                    type="Internal Power Panel Wire",
                    brand=cable["brand"],
                    order_number=cable["order_number"],
                    specifications="(3x) Size: 1x6 mm²",
                    quantity=wire_length*3,
                    price=cable['price'],
                    last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                    note="\n".join(wire_notes)
                )
            else:
                self.add_to_panel(
                    type="Internal Power Panel Wire",
                    brand="",
                    order_number="",
                    specifications="(3x) Size: 1x6 mm²",
                    quantity=wire_length*3,
                    price=0,
                    last_price_update="❌ Wire not found",
                    note="\n".join(wire_notes)
                )

        if busbar_length > 0:

            success, cable = get_wire_cable_by_spec("Busbar", 1)
            if success:
                self.add_to_panel(
                    type="Internal Power Busbar",
                    brand=cable["brand"],
                    order_number=cable["order_number"],
                    specifications="(3x) For motors > 45kW",
                    quantity=busbar_length*3,
                    price=cable['price'],
                    last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                    note="\n".join(busbar_notes))
            else:
                self.add_to_panel(
                    type="Internal Power Busbar",
                    brand="",
                    order_number="",
                    specifications="(3x) For motors > 45kW",
                    quantity=busbar_length*3,
                    price=0,
                    last_price_update="❌ Busbar not found",
                    note="\n".join(busbar_notes))


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

        success, cable = get_wire_cable_by_spec("Wire", 1, 1.5, brand=None, note=None)
        if success:
            self.add_to_panel(
                type=f"Internal Signal Panel Wire",
                brand=cable["brand"],
                order_number=cable["order_number"],
                specifications="Size: 1x1.5 mm²",
                quantity=total_length,
                price=cable['price'],
                last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                note="\n".join(notes)
            )
        else:
            self.add_to_panel(
                type=f"Internal Signal Panel Wire",
                brand="",
                order_number="",
                specifications="Size: 1x1.5 mm²",
                quantity=total_length,
                price=0,
                last_price_update="❌ Wire not found",
                note="\n".join(notes)
            )

    """ ------------------------------------- Calculate Motor Current ------------------------------------- """

    def calculate_motor_current(self, power, volt=False):
        if not volt:
            volt = self.electrical_specs["project_info"]["l_voltage"]

        return round(power / (sqrt(3) * volt * COSNUS_PI * ETA), 2)
