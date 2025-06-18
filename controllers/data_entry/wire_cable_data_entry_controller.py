from models.component_suppliers import insert_component_suppliers_to_db
from models.items.wire_cable import get_all_wire_cable, insert_wire_cable_to_db
from models.supplier import get_supplier_by_name
import re
import time

import requests
from bs4 import BeautifulSoup

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

from models.component_suppliers import insert_component_suppliers_to_db
from models.items.wire_cable import insert_wire_cable_to_db
from models.supplier import get_supplier_by_name


class WireCableUpdateWorkerSignals(QObject):
    """ define signals to tell main thread """
    finished = pyqtSignal(bool, object)  # success, data


class WireCableUpdateWorker(QRunnable):
    """ running Worker in seprate Thread """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.signals = WireCableUpdateWorkerSignals()

    def run(self):
        urls = [
            ("Flexible Cables or Wires", "https://www.barghsan.com/لیست-قیمت-سیم-و-کابل-خراسان-افشارنژاد/")
        ]
        wire_cables = []
        for series, url in urls:
            success, data = self.controller._extract_product_info_from_barghsan(url)
            if not success:
                self.signals.finished.emit(False, data)
                return
            for wire_cable in data:
                wire_cable["series"] = series
                wire_cable["supplier_id"] = 15
                wire_cables.append(wire_cable)
        self.signals.finished.emit(True, wire_cables)


class WireCableDataEntryController:
    def __init__(self, view_ref):
        self.view = view_ref
        self.threadpool = QThreadPool()

    def get_all_wire_cables(self):
        return get_all_wire_cable()

    def save_wire_cable(self, wire_cable_details):
        success, wire_cable_id = insert_wire_cable_to_db(
            type=wire_cable_details["type"],
            l_number=wire_cable_details["l_number"],
            l_size=wire_cable_details["l_size"],
            brand=wire_cable_details["brand"],
            note=wire_cable_details.get("note")
        )
        if not success:
            return False, wire_cable_id

        success, supplier_id = get_supplier_by_name(wire_cable_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=wire_cable_id,
            supplier_id=supplier_id,
            price=wire_cable_details["price"],
            currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ Saved successfully"

    def update_wire_cables_in_background(self):
        self.view.ui.update_wire_cable_prices_btn.setEnabled(False)
        worker = WireCableUpdateWorker(self)
        worker.signals.finished.connect(self.on_update_complete)
        self.threadpool.start(worker)

    # react to complete fetching data
    def on_update_complete(self, success, data):
        if success:
            self.view.show_table(data)
        else:
            print("❌ Error:", data)
        self.view.ui.update_wire_cable_prices_btn.setEnabled(True)

    def _extract_product_info_from_barghsan(self, url):
        time.sleep(2)  # Delay to avoid getting blocked by the website

        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
            })
            response = session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            cable_rows = soup.find_all('tr')
            results = []

            for row in cable_rows:
                product_td = row.find('td')  # Get product information
                price_td = row.find('td', class_='wy-price-sep')  # Get price information

                if product_td and price_td:
                    product_text = product_td.get_text(strip=True)  # Extract full product name
                    size_match = product_td.find('strong')  # Extract cable size

                    # Validate product type: must contain "کابل افشان" or "سیم افشان"
                    if "کابل افشان" in product_text:
                        product_type = "Cable"
                    elif "سیم افشان" in product_text:
                        product_type = "Wire"
                    else:
                        continue  # Skip unrelated products

                    # Extract size information if found
                    size = size_match.get_text(strip=True) if size_match else None
                    if size and '+' in size:
                        continue  # Skip sizes with "+" (combined sizes)

                    # Extract price and convert it to an integer
                    price_text = price_td.get_text(strip=True)
                    try:
                        price = int(price_text.replace(',', '').strip())
                    except ValueError:
                        price = None  # Handle cases where price conversion fails

                    # Extract brand name (assuming the brand is "Khorasan Afsharnejad")
                    brand_match = re.search(r'خراسان افشارنژاد', product_text)
                    brand = "Khorasan" if brand_match else None

                    # Format size for structured output
                    if size:
                        size = size.replace('/', '.')  # Standardize size format
                        if '×' in size:
                            l_number = int(size.split('×')[0])
                            l_size = float(size.split('×')[1])
                        else:
                            l_number = 1
                            l_size = float(size)
                    else:
                        l_number, l_size = None, None  # Handle missing size

                    results.append({
                        'l_number': l_number,
                        'l_size': l_size,
                        'brand': brand,
                        'type': product_type,
                        'note': "Flexible",
                        'price': price
                    })

            # Return results or an error message if no relevant products are found
            if not results:
                return False, "No matching cables or wires found"
            return True, results

        except Exception as e:
            return False, f"Error while fetching: {e}"

    def save_wire_cables(self, wire_cables_list):

        for wire_cable in wire_cables_list:
            success, wire_cable_id = insert_wire_cable_to_db(type=wire_cable['type'],
                                                             l_number=wire_cable['l_number'],
                                                             l_size=wire_cable['l_size'],
                                                             brand=wire_cable['brand'],
                                                             note=wire_cable['note'],
                                                             created_by_id=2,  # System
                                                             )
            if not success:
                return False, "Failed to save wire_cable"

            success, result = insert_component_suppliers_to_db(
                component_id=wire_cable_id, supplier_id=wire_cable["supplier_id"],
                price=wire_cable["price"], currency="IRR", created_by_id=2
            )
            if not success:
                return False, "Failed to save price"

        return True, "✅ WireCable Saved successfully"