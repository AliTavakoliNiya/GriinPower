import math

from controllers.panel_controller import PanelController
from models.item_price_model import get_price
from models.items.general_model import get_general_by_name
from models.items.mccb_model import get_mccb_by_motor_current
from copy import deepcopy
import re


class BagfilterController(PanelController):
    """
    Specialized controller for bagfilter panel.
    """

    def __init__(self):
        super().__init__("bagfilter")

    def build_panel(self):
        """
        Main controller for building a bagfilter from project specifications.
        """

        n_valves = 0
        if self.project_details["bagfilter"]["type"] == "Griin/China":
            match = re.search(r"×(.*?)\.", self.project_details["bagfilter"]["order"])
            if match:
                n_valves = int(match.group(1))

        if self.project_details["bagfilter"]["type"] == "BETH":
            match = re.fullmatch(r"^(\d+)\.\d+x(\d+)\.\d+x\d+$", self.project_details["bagfilter"]["order"])
            if match:
                num1 = int(match.group(1))
                num2 = int(match.group(2))
                n_valves = num1 * num2

        bagfilter_general_items = {"relay_1no_1nc": 3,
                                   "relay_2no_2nc": 3,
                                   "terminal_4": n_valves * 2 + 20,
                                   "mpcb_mccb_aux_contact": 1,
                                   "duct_cover": round(n_valves * 0.1, 2),
                                   "miniatory_rail": round(n_valves * 0.3, 2),
                                   "power_outlet ": 1}

        total_do = 3
        total_di = 3
        total_ao = 0
        total_ai = 0

        n_bagfilter_cards = (n_valves + 15) // 16  # each card support 16 valves(round up)
        do_bagfilter_card = n_bagfilter_cards * 5
        if n_bagfilter_cards > 0:
            do_bagfilter_card += math.ceil(math.log2(n_bagfilter_cards))  # for address each card, digist use in binary
        total_do += do_bagfilter_card

        has_hmi = False if self.project_details["bagfilter"]["touch_panel"] == "None" else True
        if not has_hmi:
            total_di += 4
            total_do = 1
            bagfilter_general_items["button"] = 3
            bagfilter_general_items["selector_switch"] = 1
            bagfilter_general_items["signal_lamp_24v"] = 6
        else:
            hmi_type = self.project_details["bagfilter"]["touch_panel"]
            bagfilter_general_items[hmi_type] = 1

        bagfilter_general_items["olm"] = 1 if self.project_details["bagfilter"]["olm"] else 0

        # ----------------------- Add Components for Motors -----------------------
        self.choose_mccb()

        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        self.calculate_plc_io_requirements(total_do, total_di, total_ao, total_ai)

        # # ----------------------- Add internal wiring -----------------------
        # self.choose_internal_signal_wire(motor_objects)
        # self.choose_internal_power_wire(motor_objects)
        #
        # # ----------------------- Add General Accessories -----------------------
        self.choose_general(bagfilter_general_items)

        # # ----------------------- Add Cables -----------------------
        # self.choose_signal_cable(motor_objects)
        # self.choose_power_cable(motor_objects)
        #
        # # ----------------------- Add Electrical Panel -----------------------
        # self.choose_electrical_panel(total_motors)
        #
        # # ----------------------- Add instruments -----------------------
        self.choose_instruments(instruments=self.project_details["bagfilter"]["instruments"])

        return self.panel

    def choose_general(self, general_items):
        """
        Adds general accessories like terminals, buttons, etc. based on motor needs.
        """

        for item, qty in general_items.items():
            if qty == 0:
                continue

            general_item = get_general_by_name(item)
            if general_item.item_id:
                price_item = get_price(general_item.item_id, brand=False, item_brand=False)
                price = price_item.price if price_item.price else 0
                effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
                brand = price_item.brand
            else:
                price = 0
                effective_date = "Not Found"
                brand = ""

            formatted_name = item.upper()
            try:
                formatted_name = formatted_name.replace("_", " ")
            except:
                pass

            self.add_to_panel(
                type=formatted_name,
                brand=brand,
                quantity=qty,
                price=price,
                last_price_update=effective_date
            )

    def choose_mccb(self):
        """
    Adds an MCCB entry to the panel based on the total motor power in the project.
        """
        total_current = 0.0

        for section in self.project_details.values():
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


        mccb = get_mccb_by_motor_current(total_current)
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

        self.add_to_panel(
            type="MCCB INPUT PANEL",
            brand=brand,
            reference_number=reference,
            specifications=(
                f"Total Motor Current: {total_current:.2f} A\n"
            ),
            quantity=1,
            price=price,
            last_price_update=effective_date,
            note=""
        )

    def calculate_plc_io_requirements(self, total_do, total_di, total_ao, total_ai):
        instruments = deepcopy(self.project_details["bagfilter"]["instruments"])

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
                "label": "DI 16 CHANNEL",
                "general_name": "di_16_channel",
                "notes": di_notes
            },
            {
                "count": total_do,
                "label": "DO 16 CHANNEL",
                "general_name": "do_16_channel",
                "notes": do_notes
            },
            {
                "count": total_ai,
                "label": "AI 16 CHANNEL",
                "general_name": "ai_16_channel",
                "notes": ai_notes
            },
            {
                "count": total_ao,
                "label": "AO 16 CHANNEL",
                "general_name": "ao_16_channel",
                "notes": ao_notes
            }
        ]

        total_20pin = 0
        for io in io_config:
            if io["count"] > 0:
                cards = (io["count"] + 15) // 16
                total_20pin += cards
                self.add_io_card_to_panel(io["label"], io["general_name"], cards, io["count"], io["notes"])

        if total_20pin > 0:
            pin_card = get_general_by_name("front_connector_20_pin")
            if pin_card.item_id:
                price_item = get_price(pin_card.item_id, brand=False, item_brand=False)
                price = price_item.price or 0
                effective_date = price_item.effective_date or "Not Found"
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

    # def choose_instruments(self):
    #     """
    #     Adds instrument entries to panel.
    #     """
    #
    #     instruments = self.project_details["bagfilter"]["instruments"]
    #     for instrument_name, properties in instruments.items():
    #         # calibration fee
    #         # manifolds fee
    #
    #         instrument = get_instrument_by_type(instrument_name)
    #         price_item = get_price(instrument.item_id, properties["brand"])
    #
    #         price = price_item.price if price_item.price else 0
    #         effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
    #
    #         qty = properties["qty"]
    #         if qty > 0:
    #             self.add_to_panel(
    #                 type=instrument.type,
    #                 brand=properties["brand"],
    #                 specifications="",
    #                 quantity=qty,
    #                 price=price,
    #                 last_price_update=effective_date,
    #                 note=str(instrument.note) + " <calibration fee & manifolds fee>")
