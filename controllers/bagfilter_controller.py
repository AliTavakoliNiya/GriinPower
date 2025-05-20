from math import ceil

from controllers.panel_controller import PanelController
from controllers.project_details import ProjectDetails
from models.abs_motor import Motor
from models.item_price_model import get_price
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
        # self.calculate_plc_io_requirements()

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

        total_di, total_ai, di_notes, ai_notes = self.summarize_total_io()



        """          

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
            card = get_general_by_name("digital_input_16_channel")
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
                type="DIGITAL INPUT 16 CHANNEL",
                brand=brand,
                specifications=f"Total DI: {total_di}",
                quantity=di_16ch,
                price=price,
                last_price_update=effective_date,
                note="\n".join(di_notes)
            )
        elif di_32ch > 0:
            card = get_general_by_name("digital_input_32_channel")
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
                type="DIGITAL INPUT 32 CHANNEL",
                brand=brand,
                specifications=f"Total DI: {total_di}",
                quantity=di_32ch,
                price=price,
                last_price_update=effective_date,
                note="\n".join(di_notes)
            )

        # Similar pattern for DO cards
        if do_16ch > 0:
            card = get_general_by_name("digital_output_16_channel")
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
                type="DIGITAL OUTPUT 16 CHANNEL",
                brand=brand,
                specifications=f"Total DO: {total_do}",
                quantity=do_16ch,
                price=price,
                last_price_update=effective_date,
                note="\n".join(do_notes)
            )
        elif do_32ch > 0:
            card = get_general_by_name("digital_output_32_channel")
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
                type="DIGITAL OUTPUT 32 CHANNEL",
                brand=brand,
                specifications=f"Total DO: {total_do}",
                quantity=do_32ch,
                price=price,
                last_price_update=effective_date,
                note="\n".join(do_notes)
            )

        # Add AI cards if needed
        if ai_16ch > 0:
            card = get_general_by_name("analog_input_16_channel")
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
                type="ANALOG INPUT 16 CHANNEL",
                brand=brand,
                specifications=f"Total AI: {total_ai}",
                quantity=ai_16ch,
                price=price,
                last_price_update=effective_date,
                note="\n".join(ai_notes)
            )
        elif ai_32ch > 0:
            card = get_general_by_name("analog_input_32_channel")
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
                type="ANALOG INPUT 32 CHANNEL",
                brand=brand,
                specifications=f"Total AI: {total_ai}",
                quantity=ai_32ch,
                price=price,
                last_price_update=effective_date,
                note="\n".join(ai_notes)
            )

        # Add AO cards if needed
        if ao_16ch > 0:
            card = get_general_by_name("analog_output_16_channel")
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
                type="ANALOG OUTPUT 16 CHANNEL",
                brand=brand,
                specifications=f"Total AO: {total_ao}",
                quantity=ao_16ch,
                price=price,
                last_price_update=effective_date,
                note="\n".join(ao_notes)
            )
        elif ao_32ch > 0:
            card = get_general_by_name("analog_output_32_channel")
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
                type="ANALOG OUTPUT 32 CHANNEL",
                brand=brand,
                specifications=f"Total AO: {total_ao}",
                quantity=ao_32ch,
                price=price,
                last_price_update=effective_date,
                note="\n".join(ao_notes)
            )

        # Calculate and add total connectors
        total_20pin = di_16ch + do_16ch + ai_16ch + ao_16ch
        total_40pin = di_32ch + do_32ch + ai_32ch + ao_32ch

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
                specifications="Total 20PIN connectors needed",
                quantity=total_20pin,
                price=price,
                last_price_update=effective_date,
                note=f"Total connectors for all 16CH cards"
            )

        if total_40pin > 0:
            pin_card = get_general_by_name("front_connector_40_pin")
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
                type="FRONT CONNECTOR 40PIN",
                brand=brand,
                specifications="Total 40PIN connectors needed",
                quantity=total_40pin,
                price=price,
                last_price_update=effective_date,
                note=f"Total connectors for all 32CH cards"
            )


        """

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
                    io_notes.append(f"{name}: {qty} × {io_def['n_di']} DI")
                if io_def["n_ai"] > 0:
                    total_ai += qty * io_def["n_ai"]
                    io_notes.append(f"{name}: {qty} × {io_def['n_ai']} AI")

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
                    io_notes.append(f"{section} → {m_name}: {qty} motor(s) × "
                                    f"{motor.plc_di} DI, {motor.plc_do} DO, "
                                    f"{motor.plc_ai} AI, {motor.plc_ao} AO")

        return {
            "total_di": total_di,
            "total_do": total_do,
            "total_ai": total_ai,
            "total_ao": total_ao,
            "notes": io_notes
        }

