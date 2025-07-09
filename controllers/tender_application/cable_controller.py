import math
import re

from config import COSNUS_PI, ETA
from controllers.tender_application.panel_controller import PanelController
from models.items.wire_cable import get_wire_cable_by_spec


class CableController(PanelController):
    """
    Specialized controller for bagfilter panel.
    """

    def __init__(self):
        super().__init__("cable")

    def build_panel(self):
        """
                Main controller for building installation from tender_application specifications.
        """
        self.motors = []
        for section_name, section in self.electrical_specs.items():
            motor = section.get("motors", {})
            for motor_name, motor_data in motor.items():
                try:
                    # Skip "fan" motor if its voltage type is "MV"
                    if motor_name == "fan" and self.electrical_specs["fan"]["motors"]["voltage_type"] == "MV":
                        continue

                    qty = motor_data.get("qty", 0)
                    if qty:
                        volt = self.electrical_specs["project_info"]["l_voltage"]
                        power = motor_data.get("power", 0)  # Assuming 'power' is an attribute of motor
                        current = round(power / (math.sqrt(3) * volt * COSNUS_PI * ETA), 2)
                        self.motors.append({"motor": motor_name, "qty": qty, "power": power, "current": current})
                except Exception as e:
                    print(str(e))
                    continue

        self.length = self.electrical_specs["bagfilter"]["cable_dimension"]
        self.note_motors = ", ".join(f'{motor["motor"]} (x{motor["qty"]})' for motor in self.motors)


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

        # calculates n_instruments
        self.instruments = []
        for section in self.electrical_specs.values():
            instruments = section.get("instruments", {})
            for instrument_name, instrument_data in instruments.items():
                try:
                    if instrument_name == "ptc":
                        continue  # skip this instrument
                    qty = instrument_data.get("qty", 0)
                    if qty:
                        self.instruments.append({"instruments": instrument_name, "qty": qty})
                except Exception:
                    pass

        self.instrument_valve_cable()
        self.power_cable()
        self.signal_cable()

        return self.panel

    def instrument_valve_cable(self):
        shield_names = {"pt100", "bearing_vibration_transmitter"}

        # Separate lists
        flexible_instruments = []
        shield_instruments = []

        # Categorize instruments
        for item in self.instruments:
            if item["instruments"] in shield_names:
                shield_instruments.append(item)
            else:
                flexible_instruments.append(item)

        # Main report
        flexible_total_qty = sum(item["qty"] for item in flexible_instruments)
        flexible_total_qty += self.n_valves
        flexible_summary = ", ".join(f'{item["instruments"]} (x{item["qty"]})' for item in flexible_instruments)
        flexible_summary += f"\nValves (x{self.n_valves})"

        # shield reports
        shield_total_qty = sum(item["qty"] for item in shield_instruments)
        shield_summary = ", ".join(f'{item["instruments"]} (x{item["qty"]})' for item in shield_instruments)


        success, cable = get_wire_cable_by_spec(type="Cable", note="Shield", l_number=3, l_size=1.5)
        if success:
            self.add_to_panel(
                type=f"Cable 3x1.5",
                brand=cable["brand"],
                order_number=cable["order_number"],
                specifications=f"Shield 3x1.5mm",
                quantity=shield_total_qty * self.length,
                price=cable['price'],
                last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                note=shield_summary
            )
        else:
            self.add_to_panel(
                type=f"Cable 3x1.5",
                brand="",
                order_number="",
                specifications=f"Shield 3x1.5mm",
                quantity=shield_total_qty * self.length,
                price=0,
                last_price_update="❌ Cable not found",
                note=shield_summary
            )

        success, cable = get_wire_cable_by_spec(type="Cable", note="Flexible", l_number=3, l_size=1.5)
        if success:
            self.add_to_panel(
                type=f"Cable 3x1.5",
                brand=cable["brand"],
                order_number=cable["order_number"],
                specifications=f"Flexible 3x1.5mm",
                quantity=flexible_total_qty * self.length,
                price=cable['price'],
                last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                note=flexible_summary
            )
        else:
            self.add_to_panel(
                type=f"Cable 3x1.5",
                brand="",
                order_number="",
                specifications=f"Flexible 3x1.5mm",
                quantity=flexible_total_qty * self.length,
                price=0,
                last_price_update="❌ Cable not found",
                note=flexible_summary
            )



    def signal_cable(self):
        total_motors = sum(motor["qty"] for motor in self.motors)

        success, cable = get_wire_cable_by_spec(type="Cable", note="Flexible", l_number=7, l_size=1.5)
        if success:
            self.add_to_panel(
                type=f"Cable 7x1.5",
                brand=cable["brand"],
                order_number=cable["order_number"],
                specifications=f"7x1.5mm",
                quantity=self.length * total_motors,
                price=cable['price'],
                last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                note=self.note_motors
            )
        else:
            self.add_to_panel(
                type=f"Cable 7x1.5",
                brand="",
                order_number="",
                specifications=f"7x1.5mm",
                quantity=self.length * total_motors,
                price=0,
                last_price_update="❌ Cable not found",
                note=self.note_motors
            )

    def power_cable(self):
        # Step 1: Group motors by cable_size
        cable_group = {}

        for motor in self.motors:
            cable_size = cable_rating(cable_length_m=self.length, cable_current_a=motor["current"])

            if cable_size not in cable_group:
                cable_group[cable_size] = {
                    "length": 0,
                    "motors": []
                }

            cable_group[cable_size]["length"] += self.length
            cable_group[cable_size]["motors"].append(motor["motor"])

        # Step 2: Retrieve cable data for each cable_size (only once)
        cable_data = {}
        for cable_size in cable_group:
            success, cable = get_wire_cable_by_spec(type="Cable", note="Flexible", l_number=4, l_size=cable_size)
            cable_data[cable_size] = (success, cable)

        # Step 3: Add to panel
        for cable_size, data in cable_group.items():
            total_length = data["length"]
            success, cable = cable_data[cable_size]

            if success:
                self.add_to_panel(
                    type=f"Cable 4x{cable_size}",
                    brand=cable["brand"],
                    order_number=cable["order_number"],
                    specifications=f"4x{cable_size}mm",
                    quantity=total_length,
                    price=cable['price'],
                    last_price_update=f"{cable['supplier_name']}\n{cable['date']}",
                    note=self.note_motors
                )
            else:
                self.add_to_panel(
                    type=f"Cable 4x{cable_size}",
                    brand="",
                    order_number="",
                    specifications=f"4x{cable_size}mm",
                    quantity=total_length,
                    price=0,
                    last_price_update="❌ Cable not found",
                    note=self.note_motors
                )


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
