import math
from math import ceil

from controllers.panel_controller import PanelController
from controllers.project_details import ProjectDetails
from models.abs_motor import Motor
from models.item_price_model import get_price
from models.items.general_model import get_general_by_name
from models.items.mccb_model import get_mccb_by_motor_power


class BagfilterController(PanelController):
    """
    Specialized controller for bagfilter panel.
    """

    def __init__(self):
        super().__init__("bagfilter")
        self.project_details = ProjectDetails()
        self.panel = {
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

    def build_panel(self):
        """
        Main controller for building a bagfilter from project specifications.
        """

        # ----------------------- Add Components for Motors -----------------------
        self.choose_mccb()

        # ----------------------- Calculate and add PLC I/O requirements -----------------------
        self.calculate_plc_io_requirements()

        # # ----------------------- Add internal wiring -----------------------
        # self.choose_internal_signal_wire(motor_objects)
        # self.choose_internal_power_wire(motor_objects)
        #
        # # ----------------------- Add General Accessories -----------------------
        # self.choose_general(motor_objects)
        #
        # if self.project_details["bagfilter"]["touch_panel"] == "None":  # no touch panel required
        #     self.choose_general(motor_objects, ["signal_lamp_24v"])
        #
        # # ----------------------- Add Cables -----------------------
        # self.choose_signal_cable(motor_objects)
        # self.choose_power_cable(motor_objects)
        #
        # # ----------------------- Add Electrical Panel -----------------------
        # total_motors = sum(qty for _, qty in motor_objects)
        # total_motors += sum(0.5 * qty for motor, qty in motor_objects if motor.usage == "Telescopic Chute")
        # total_motors += sum(0.5 * qty for motor, qty in motor_objects if motor.usage == "Slide Gate")
        # total_motors = ceil(total_motors)
        #
        # if total_motors != 0:
        #     self.choose_electrical_panel(total_motors)
        #
        # # ----------------------- Add instruments -----------------------
        # self.choose_instruments(instruments)

        return self.panel

    def choose_mccb(self):

        # Calculate total power of all motors
        total_power = 0

        for section in self.project_details.values():
            motors = section.get("motors", {})
            for motor_name, motor_data in motors.items():
                try:
                    qty = motor_data.get("qty", 0)
                    power = motor_data.get("power", 0)
                    total_power += qty * power
                except:
                    pass

        if total_power == 0:
            return


        mccb = get_mccb_by_motor_power(total_power)
        if mccb.item_id:
            price_item = get_price(mccb.item_id, brand=False, item_brand=False)
            price = price_item.price if price_item.price else 0
            effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
            brand = price_item.brand
        else:
            price = 0
            effective_date = "Not Found"
            brand = ""

        self.add_to_panel(
            type=f"MCCB FOR BAGFILTER",
            brand=brand,
            reference_number=mccb.mccb_reference,
            specifications=f"For Total Power: {mccb.p_kw} KW\nCurrent: {mccb.i_a} A",
            quantity=1,
            price=price,
            last_price_update=effective_date,
            note=f"Total Power: {total_power} KW"
        )


    def calculate_plc_io_requirements(self):
        """
        Calculates total PLC I/O requirements and adds appropriate I/O cards
        """

        total_di, total_do, total_ai, total_ao,  io_notes = self.summarize_total_io()
        io_notes = "\n".join(io_notes)



        # Grouping totals
        total_digital = total_di + total_do
        total_analog = total_ai + total_ao

        # Calculate card requirements
        digital_16, digital_32 = self.calculate_card_distribution(total_digital)
        analog_16, analog_32 = self.calculate_card_distribution(total_analog)

        # Add digital 16-channel cards
        if digital_16 > 0:
            card = get_general_by_name("digital_16_channel")
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
                type="DIGITAL_CARD_16CH",
                brand=brand,  # Replace with actual brand logic if needed
                quantity=digital_16,
                price=price,  # Replace with pricing logic
                last_price_update=effective_date,
                note=io_notes
            )

        # Add digital 32-channel cards
        if digital_32 > 0:
            card = get_general_by_name("digital_32_channel")
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
                type="DIGITAL_CARD_32CH",
                brand=brand,
                quantity=digital_32,
                price=price,
                last_price_update=effective_date,
                note=io_notes
            )

        # Add analog 16-channel cards
        if analog_16 > 0:
            card = get_general_by_name("analog_16_channel")
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
                type="ANALOG_CARD_16CH",
                brand=brand,
                quantity=analog_16,
                price=price,
                last_price_update=effective_date,
                note=io_notes
            )

        # Add analog 32-channel cards
        if analog_32 > 0:
            card = get_general_by_name("analog_32_channel")
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
                type="ANALOG_CARD_32CH",
                brand=brand,
                specifications="32-channel Analog I/O card",
                quantity=analog_32,
                price=price,
                last_price_update=effective_date,
                note=io_notes
            )

        total_front_connector_20_pin = digital_16 + analog_16
        if total_front_connector_20_pin > 0:
            connector = get_general_by_name("front_connector_20_pin")
            if connector.item_id:
                price_item = get_price(connector.item_id, brand=False, item_brand=False)
                price = price_item.price if price_item.price else 0
                effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
                brand = price_item.brand
            else:
                price = 0
                effective_date = "Not Found"
                brand = ""
            self.add_to_panel(
                type="FRONT CONNECTOR 20 PIN",
                brand=brand,
                quantity=total_front_connector_20_pin,
                price=price,
                last_price_update=effective_date,
                note=f"{digital_16}Digital Card + {analog_16}Analog Card"
            )

        total_front_connector_40_pin = digital_32 + analog_32
        if total_front_connector_40_pin > 0:
            connector = get_general_by_name("front_connector_40_pin")
            if connector.item_id:
                price_item = get_price(connector.item_id, brand=False, item_brand=False)
                price = price_item.price if price_item.price else 0
                effective_date = price_item.effective_date if price_item.effective_date else "Not Found"
                brand = price_item.brand
            else:
                price = 0
                effective_date = "Not Found"
                brand = ""
            self.add_to_panel(
                type="FRONT CONNECTOR 40 PIN",
                brand=brand,
                quantity=total_front_connector_40_pin,
                price=price,
                last_price_update=effective_date,
                note=f"{digital_32}Digital Card + {analog_32}Analog Card"
            )


    def calculate_card_distribution(self, channel_total):
        cards_16 = math.ceil(channel_total / 16)
        if cards_16 <= 8:
            return cards_16, 0
        return 0, max(math.ceil(channel_total / 32), 1)

    def summarize_total_io(self):
        instruments_io_config = {
            'delta_pressure_transmitter': {'n_di': 0, 'n_ai': 1},
            'delta_pressure_switch': {'n_di': 1, 'n_ai': 0},
            'pressure_transmitter': {'n_di': 0, 'n_ai': 1},
            'pressure_switch': {'n_di': 1, 'n_ai': 0},
            'temperature_transmitter': {'n_di': 0, 'n_ai': 1},
            'proximity_switch': {'n_di': 1, 'n_ai': 0},
            'vibration_transmitter': {'n_di': 0, 'n_ai': 1},
            'speed_detector': {'n_di': 1, 'n_ai': 0},
            'level_switch': {'n_di': 1, 'n_ai': 0},
            'level_transmitter': {'n_di': 0, 'n_ai': 1},
            'bearing_temperature_transmitter': {'n_di': 0, 'n_ai': 1},
            'bearing_vibration_transmitter': {'n_di': 0, 'n_ai': 1},
            'inlet_temperature_transmitter': {'n_di': 0, 'n_ai': 1},
            'outlet_temperature_transmitter': {'n_di': 0, 'n_ai': 1},
            'pt100': {'n_di': 0, 'n_ai': 1},
        }

        total_di = total_do = total_ai = total_ao = 0
        io_notes = []

        for section, content in self.project_details.items():
            # --- Instruments ---
            instruments = content.get("instruments", {})
            for name, props in instruments.items():
                qty = props.get("qty", 0)
                if qty <= 0:
                    continue
                io_def = instruments_io_config.get(name, {"n_di": 0, "n_ai": 0})
                if io_def["n_di"] > 0:
                    total_di += qty * io_def["n_di"]
                    io_notes.append(f"{qty}×{name} → {qty * io_def['n_di']} DI")
                if io_def["n_ai"] > 0:
                    total_ai += qty * io_def["n_ai"]
                    io_notes.append(f"{qty}×{name} → {qty * io_def['n_ai']} AI")

            # --- Motors ---
            motors = content.get("motors", {})
            for m_name, m_props in motors.items():
                motor = m_props.get("motor")
                qty = m_props.get("qty", 0)
                if motor and qty > 0:
                    total_di += motor.plc_di * qty
                    total_do += motor.plc_do * qty
                    total_ai += motor.plc_ai * qty
                    total_ao += motor.plc_ao * qty
                    io_notes.append(f"{qty}×{m_name} motor(s)")

        return total_di, total_do, total_ai, total_ao, io_notes

