import math
import re
from copy import deepcopy

from controllers.tender_application.panel_controller import PanelController

from models.items.electrical_panel import get_electrical_panel_by_spec
from models.items.general import get_general_by_spec
from models.items.instrument import get_instrument_by_spec
from models.items.mccb import get_mccb_by_current
from models.items.plc import get_plc_by_spec


class BagfilterController(PanelController):
    """
    Specialized controller for bagfilter panel.
    """

    def __init__(self):
        super().__init__("bagfilter")

    def build_panel(self):
        """
        Main controller for building a bagfilter from tender_application specifications.
        """

        n_valves = 0
        if self.electrical_specs["bagfilter"]["type"] == "Griin/China":  # EX: 8.96x5.(2.7m).10
            pattern = r'(\d+)\.(\d+)x(\d+)\.\((\d+(?:\.\d+)?)m\)\.(\d+)'
            match = re.match(pattern, self.electrical_specs["bagfilter"]["order"])
            if match:
                n_valves = int(match.group(1))  # ~ compartments ~ jacks

        if self.electrical_specs["bagfilter"]["type"] == "BETH":  # 6.78x2.3.10
            match = re.match(r'(\d+)\.(\d+)x(\d+)\.(\d+)\.(\d+)', self.electrical_specs["bagfilter"]["order"])
            if match:
                n_valve_per_airtank = int(match.group(1))
                n_airtank = int(match.group(3))
                n_valves = n_valve_per_airtank * n_airtank

        self.bagfilter_general_items = {
            "touch_panel": 0,
            "relay_1no_1nc": 3,
            "relay_2no_2nc": 3,
            "terminal_4": n_valves * 2 + 20,
            "mpcb_mccb_aux_contact": 1,
            "duct_cover": round(n_valves * 0.1, 2),
            "miniatory_rail": round(n_valves * 0.3, 2),
            "power_outlet": 1,
            "mcb_4DC": 2,
            "mcb_2AC": 1,
        }

        total_do = 3
        total_di = 3
        total_ao = 0
        total_ai = 0

        n_bagfilter_cards = (n_valves + 15) // 16  # each card support 16 valves(round up)
        self.bagfilter_general_items["bagfilter_cards"] = n_bagfilter_cards

        do_bagfilter_card = n_bagfilter_cards * 5
        if n_bagfilter_cards > 0:
            do_bagfilter_card += math.ceil(math.log2(n_bagfilter_cards))  # for address each card, digist use in binary
        total_do += do_bagfilter_card

        has_hmi = True if self.electrical_specs["bagfilter"]["touch_panel"] else False
        if has_hmi:
            self.bagfilter_general_items["touch_panel"] = 1
        else:
            total_di += 4
            total_do = 1
            self.bagfilter_general_items["button"] = 3
            self.bagfilter_general_items["selector_switch"] = 1
            self.bagfilter_general_items["signal_lamp_24v"] = 6

        self.bagfilter_general_items["olm"] = 1 if self.electrical_specs["bagfilter"]["olm"] else 0

        """ ----------------------- Add plc ----------------------- """
        self.choose_plc()

        """ ----------------------- Add Components for Motors ----------------------- """
        self.choose_mccb()

        """ ----------------------- Calculate and add PLC I/O requirements ----------------------- """
        self.calculate_plc_io_requirements(total_do, total_di, total_ao, total_ai)

        # # ----------------------- Add internal wiring -----------------------
        # self.choose_internal_signal_wire(motor_objects)
        # self.choose_internal_power_wire(motor_objects)
        #
        # # ----------------------- Add General Accessories -----------------------
        self.choose_general(self.bagfilter_general_items)


        # # ----------------------- Add Electrical Panel -----------------------
        # self.choose_electrical_panel()

        # # ----------------------- Add instruments -----------------------
        self.choose_instruments()

        return self.panel

    def choose_electrical_panel(self):

        success, electrical_panel = get_electrical_panel_by_spec(type="Electrical Panel")
        if success:
            self.add_to_panel(
                type="Electrical Panel",
                brand=electrical_panel.get("brand", ""),
                order_number="",
                specifications=f"{electrical_panel.width}mm x {electrical_panel.height}mm x {electrical_panel.depth}mm",
                quantity=1,
                price=electrical_panel.get("price", 0),
                last_price_update=f"{electrical_panel.get('supplier_name', '')}\n{electrical_panel.get('date', '')}",
                note=""
            )
        else:
            self.add_to_panel(
                type="Electrical Panel",
                brand="",
                order_number="",
                specifications="",
                quantity=1,
                price=0,
                last_price_update="❌ Electrical Panel not found",
                note=""
            )

    def process_item(self, comp_type, qty, specification=""):
        if qty <= 0:
            return

        success, item = get_general_by_spec(comp_type, specification)
        display_type = f"{comp_type} {specification}".strip()

        if success:
            self.add_to_panel(
                type=display_type,
                brand=item.get("brand", ""),
                order_number="",
                specifications=item.get("specification", ""),
                quantity=qty,
                price=item.get("price", 0),
                last_price_update=f"{item.get('supplier_name', '')}\n{item.get('date', '')}",
                note=""
            )
        else:
            self.add_to_panel(
                type=display_type,
                brand="",
                order_number="",
                specifications=specification,
                quantity=qty,
                price=0,
                last_price_update=f"❌ {display_type} not found",
                note=""
            )

    def choose_general(self, general_items):
        self.process_item(comp_type="Griin Bagfilter Cards", qty=general_items.get("bagfilter_cards", 0))
        self.process_item(comp_type="Terminal", specification="4", qty=general_items.get("terminal_4", 0))
        self.process_item(comp_type="Relay", specification="1", qty=general_items.get("relay_1no_1nc", 0))
        self.process_item(comp_type="Relay", specification="2", qty=general_items.get("relay_2no_2nc", 0))
        self.process_item(comp_type="Button", qty=general_items.get("button", 0))
        self.process_item(comp_type="Selector Switch", qty=general_items.get("selector_switch", 0))
        self.process_item(comp_type="Power Outlet", qty=general_items.get("power_outlet", 0))
        self.process_item(comp_type="MCB", specification="4DC", qty=general_items.get("mcb_4DC", 0))
        self.process_item(comp_type="MCB", specification="2AC", qty=general_items.get("mcb_2AC", 0))
        self.process_item(comp_type="Touch Panel", specification=self.electrical_specs["bagfilter"]["touch_panel"],
                          qty=general_items.get("touch_panel", 0))
        self.process_item(comp_type="Signal Lamp", specification="24", qty=general_items.get("signal_lamp_24v", 0))

        # Optional OLM
        if "olm" in general_items:
            self.process_item(comp_type="OLM", qty=self.bagfilter_general_items["olm"])

    def choose_mccb(self):
        """
        Adds an MCCB entry to the panel based on the total motor power in the tender_application.
        """
        total_current = 0.0

        for section in self.electrical_specs.values():
            motors = section.get("motors", {})
            for motor_name, motor_data in motors.items():
                try:
                    qty = motor_data.get("qty", 0)
                    current = motor_data.get("motor", 0).current
                    total_current += qty * current
                except Exception:
                    pass

        if total_current == 0:
            return

        success, mccb = get_mccb_by_current(rated_current=total_current,
                                            brands=self.electrical_specs["project_info"]["proj_avl"])
        if success:
            self.add_to_panel(
                type="MCCB INPUT PANEL",
                brand=mccb['brand'],
                order_number=mccb["order_number"],
                specifications=(
                    f"Total Motor Current: {total_current:.2f}A"
                ),
                quantity=1,
                price=mccb['price'],
                last_price_update=f"{mccb['supplier_name']}\n{mccb['date']}",
                note=""
            )
        else:
            self.add_to_panel(
                type="MCCB INPUT PANEL",
                brand="",
                order_number="",
                specifications=(
                    f"At Least: {total_current * 1.25:.2f}A"
                ),
                quantity=1,
                price=0,
                last_price_update="❌ MCCB not found",
                note=""
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
            specifications=f"Total: {total}",
            quantity=cards,
            price=price,
            last_price_update=effective_date,
            note="\n".join(notes)
        )
        return cards

    def calculate_plc_io_requirements(self, total_do, total_di, total_ao, total_ai):
        instruments = deepcopy(self.electrical_specs["bagfilter"]["instruments"])

        di_notes = [f"Initial DI: {total_di}"] if total_di else []
        ai_notes = [f"Initial AI: {total_ai}"] if total_ai else []
        do_notes = [f"Initial DO: {total_do}"] if total_do else []
        ao_notes = [f"Initial AO: {total_ao}"] if total_ao else []

        if instruments:
            total_di, total_ai = self.calculate_instruments_io(
                instruments, total_di, total_ai, di_notes, ai_notes
            )

        io_config = [
            {
                "count": total_di,
                "general_name": "DI",
                "notes": di_notes
            },
            {
                "count": total_do,
                "general_name": "DO",
                "notes": do_notes
            },
            {
                "count": total_ai,
                "general_name": "AI",
                "notes": ai_notes
            },
            {
                "count": total_ao,
                "general_name": "AO",
                "notes": ao_notes
            }
        ]

        total_20pin = 0
        for io in io_config:
            if io["count"] > 0:
                cards = (io["count"] + 15) // 16
                total_20pin += cards
                self.calculate_and_add_io(io["general_name"], io["count"], io["notes"])

        if total_20pin > 0:
            success, pin_card = get_general_by_spec(type="Front Connector", specification="20")
            if success:
                self.add_to_panel(
                    type="Front Connector 20Pin",
                    brand=pin_card["brand"],
                    order_number=pin_card["order_number"],
                    quantity=total_20pin,
                    price=pin_card['price'],
                    last_price_update=f"{pin_card['supplier_name']}\n{pin_card['date']}",
                    note="Total connectors for all 16CH cards"
                )
            else:
                self.add_to_panel(
                    type="Front Connector 20Pin",
                    brand="",
                    order_number="",
                    specifications="",
                    quantity=total_20pin,
                    price=0,
                    last_price_update="❌ Front Connector not found",
                    note="Total connectors for all 16CH cards"
                )

    def choose_instruments(self):
        """
        Adds instrument entries to panel.
        """

        instruments = self.electrical_specs["bagfilter"]["instruments"]
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

            success, instrument = get_instrument_by_spec(name.replace('_', ' ').title())

            if success:
                self.add_to_panel(
                    type=instrument_name.upper().replace("_", " "),
                    brand=instrument["brand"],
                    order_number=instrument["order_number"],
                    specifications="",
                    quantity=qty,
                    price=instrument["price"],
                    last_price_update=f"{instrument['supplier_name']}\n{instrument['date']}",
                )
            else:
                self.add_to_panel(
                    type=instrument_name.upper().replace("_", " "),
                    brand="",
                    order_number="",
                    specifications="",
                    quantity=qty,
                    price=0,
                    last_price_update=f"❌ Instrument not found",
                )
                print(instrument)

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

                success, manifold_obj = get_instrument_by_spec(type=manifold_ways)
                if success:
                    self.add_to_panel(
                        type=manifold_ways,
                        brand=manifold_obj['brand'],
                        order_number=manifold_obj['order_number'],
                        quantity=qty,
                        price=manifold_obj['price'],
                        last_price_update=f"{manifold_obj['supplier_name']}\n{manifold_obj['date']}",
                        note=f"manifold for {instrument_name.replace('_', ' ').title()}")
                else:
                    self.add_to_panel(
                        type=manifold_ways,
                        brand="",
                        order_number="",
                        quantity=qty,
                        price=0,
                        last_price_update=f"❌Manifold not found",
                        note=f"manifold for {instrument_name.replace('_', ' ').title()}")
                    print(manifold_obj)

            # ------------ Calibration ------------
            if "transmitter" in name and qty != 0:
                success, calibration = get_instrument_by_spec(type="Calibration")
                if success:
                    self.add_to_panel(
                        type="CALIBRATION",
                        brand=calibration['brand'],
                        quantity=qty,
                        price=calibration['price'],
                        last_price_update=f"{calibration['supplier_name']}\n{calibration['date']}",
                        note=f"calibration for {instrument_name.replace('_', ' ').title()}"
                    )
                else:
                    self.add_to_panel(
                        type="CALIBRATION",
                        brand="",
                        quantity=qty,
                        price=0,
                        last_price_update=f"❌ Calibration not found",
                        note=f"calibration for {instrument_name.replace('_', ' ').title()}"
                    )
                    print(calibration)

    def choose_plc(self):
        """
        Adds a PLC entry to the panel based on electrical specs.
        """
        plc_series_spec = self.electrical_specs["bagfilter"]["plc_series"]

        series = None
        if "S7-1200 Series" in plc_series_spec:
            series = "S7-1200"
        elif "S7-300 Series" in plc_series_spec:
            series = "S7-300"
        elif "LOGO!" in plc_series_spec:
            series = "LOGO!"

        if not series:
            self.add_to_panel(
                type="PLC",
                brand="",
                order_number="",
                specifications=f"{series}",
                quantity=0,
                price=0,
                last_price_update="❌ PLC series missing",
                note=""
            )
            return

        plc_protocol = (self.electrical_specs.get("bagfilter", {}).get("plc_protocol") or "").lower()
        protocol_filters = {}
        if plc_protocol == "profinet":
            protocol_filters["has_profinet"] = True
        elif plc_protocol == "profibus":
            protocol_filters["has_profibus"] = True
        elif plc_protocol == "hart":
            protocol_filters["has_hart"] = True
        # else no protocol filters added, so these are optional

        success, plc = get_plc_by_spec(
            series=series,
            **protocol_filters
        )

        if success:
            self.add_to_panel(
                type="PLC",
                brand=plc.get('brand', ''),
                order_number=plc.get('order_number', ''),
                specifications="",
                quantity=1,
                price=float(plc.get('price', 0)),
                last_price_update=f"{plc.get('supplier_name', '')}\n{plc.get('date', '')}",
                note=(
                    f"Series: {plc.get('series', '')}, "
                    f"Model: {plc.get('model', '')}, "
                    f"DI pins: {plc.get('di_pins', '')}, "
                    f"DO pins: {plc.get('do_pins', '')}, "
                    f"AI pins: {plc.get('ai_pins', '')}, "
                    f"AO pins: {plc.get('ao_pins', '')}"
                )
            )
        else:
            self.add_to_panel(
                type="PLC",
                brand="",
                order_number="",
                specifications="No matching PLC found for selected specs.",
                quantity=1,
                price=0,
                last_price_update="❌ PLC not found",
                note=""
            )
