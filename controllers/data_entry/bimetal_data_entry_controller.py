import re
import time

import requests
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
from bs4 import BeautifulSoup

from models.component_suppliers import insert_component_suppliers_to_db
from models.items.bimetal import get_all_bimetals, insert_bimetal_to_db
from models.suppliers import get_supplier_by_name


class BimetalUpdateWorkerSignals(QObject):
    """ define signals to tell main thread """
    finished = pyqtSignal(bool, object)  # success, data


class BimetalUpdateWorker(QRunnable):
    """ running Worker in seprate Thread """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.signals = BimetalUpdateWorkerSignals()

    def run(self):
        urls = [
            ("D", "https://elicaelectric.com/بیمتال-جهت-کنتاکتورهای-سری-d?page=1"),
            ("D", "https://elicaelectric.com/بیمتال-جهت-کنتاکتورهای-سری-d?page=2"),
        ]
        Bimetals = []
        for series, url in urls:
            success, data = self.controller._extract_product_info_from_elica(url)
            if not success:
                self.signals.finished.emit(False, data)
                return
            for Bimetal in data:
                Bimetal["series"] = series
                Bimetal["supplier_id"] = 9
                Bimetals.append(Bimetal)
        self.signals.finished.emit(True, Bimetals)


class BimetalDataEntryController:

    def __init__(self, view_ref):
        self.view = view_ref
        self.threadpool = QThreadPool()

    def get_all_bimetals(self):
        bimetals = get_all_bimetals()
        return bimetals

    def save_bimetal(self, bimetal_details):

        success, bimetal_id = insert_bimetal_to_db(
            brand=bimetal_details["brand"],
            order_number=bimetal_details["order_number"],
            min_current=bimetal_details["min_current"],
            max_current=bimetal_details["max_current"],
            _class=bimetal_details["class"],
            tripping_threshold=bimetal_details["tripping_threshold"]
        )
        if not success:
            return False, bimetal_id

        success, supplier_id = get_supplier_by_name(bimetal_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=bimetal_id, supplier_id=supplier_id, price=bimetal_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ Bimetal Saved successfully"

    def update_bimetals_in_background(self):
        self.view.ui.update_bimetal_prices_btn.setEnabled(False)
        worker = BimetalUpdateWorker(self)
        worker.signals.finished.connect(self.on_update_complete)
        self.threadpool.start(worker)

    def on_update_complete(self, success, data):
        if success:
            self.view.show_table(data)
        else:
            print("❌ Error:", data)
        self.view.ui.update_bimetal_prices_btn.setEnabled(True)

    def _extract_product_info_from_elica(self, url):
        time.sleep(2)
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
            })
            resp = session.get(url, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            products = soup.find_all('div', class_='product-thumb')
            out = []

            for p in products:
                order_number = None
                min_current = None
                max_current = None
                breaking_capacity = None
                price = None
                brand = None
                tripping_threshold = "-"  # Default as requested

                # Order number
                code_label = p.find('span', class_='stats-label', string='کد فنی:')
                if code_label:
                    order_number_span = code_label.find_next('span')
                    if order_number_span:
                        order_number = order_number_span.get_text(strip=True)

                # Brand
                brand_label = p.find('span', class_='stats-label', string='برند:')
                if brand_label:
                    brand_link = brand_label.find_next('a')
                    if brand_link:
                        brand = brand_link.get_text(strip=True)

                # Title
                title = ''
                name_div = p.find('div', class_='name')
                if name_div and name_div.a:
                    title = name_div.a.get_text(strip=True)

                # Description
                desc = ''
                desc_div = p.find('div', class_='description')
                if desc_div:
                    desc = desc_div.get_text(strip=True)

                # Extract min and max current
                range_match = re.search(r'(\d+)\s*الی\s*(\d+)\s*آمپر', title)
                if range_match:
                    min_current = float(range_match.group(1))
                    max_current = float(range_match.group(2))
                else:
                    amp_match = re.search(r'(\d+)\s*آمپر', desc)
                    if amp_match:
                        min_current = max_current = float(amp_match.group(1))

                if max_current is None:
                    continue  # Skip if we can't detect the current


                # Price
                price_span = p.find('span', class_='price-normal')
                if price_span:
                    price_text = price_span.get_text(strip=True)
                    price_digits = re.sub(r'[^\d]', '', price_text)
                    if price_digits.isdigit():
                        price = int(price_digits) * 10  # Convert Toman to Rial
                    else:
                        continue

                out.append({
                    'order_number': order_number,
                    'brand': "schneider electric",
                    'min_current': min_current,
                    'max_current': max_current,
                    'class': "D",
                    'tripping_threshold': "-",
                    'price': price
                })

            return (True, out) if out else (False, "No products found")
        except Exception as e:
            return False, str(e)

    def save_bimetals(self, bimetals_list):


        for bimetal in bimetals_list:
            success, bimetal_id = insert_bimetal_to_db(
                min_current=bimetal["min_current"],
                max_current=bimetal["max_current"],
                _class=bimetal["class"],
                tripping_threshold=bimetal["tripping_threshold"],
                brand=bimetal["brand"],
                order_number=bimetal["order_number"],
                created_by_id=2,  # System
            )
            if not success:
                return False, "Failed to save bimetal"

            success, result = insert_component_suppliers_to_db(
                component_id=bimetal_id,
                supplier_id=bimetal["supplier_id"],
                price=bimetal["price"],
                currency="IRR",
                created_by_id=2
            )
            if not success:
                return False, "Failed to save price"

        return True, "✅ Bimetal Saved successfully"



