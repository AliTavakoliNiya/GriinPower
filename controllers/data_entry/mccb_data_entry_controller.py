import re
import time

import requests
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from bs4 import BeautifulSoup

from models.component_suppliers import insert_component_suppliers_to_db
from models.items.mccb import get_all_mccbs, insert_mccb_to_db
from models.suppliers import get_supplier_by_name


class MCCBUpdateWorkerSignals(QObject):
    """ define signals to tell main thread """
    finished = pyqtSignal(bool, object)  # success, data


class MCCBUpdateWorker(QRunnable):
    """ running Worker in seprate Thread """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.signals = MCCBUpdateWorkerSignals()

    def run(self):
        urls = [
            ("nsx100", "https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سری-nsx100?page=1"),
            ("nsx100", "https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سری-nsx100?page=2"),
            ("nsx100", "https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سری-nsx100?page=3"),
            ("nsx100", "https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سری-nsx100?page=4"),
            ("nsx160", "https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سه-پل-سری-nsx160?page=1"),
            ("nsx250", "https://elicaelectric.com/کلید-کمپکت-اتوماتیک-سری-nsx250?page=1"),
            ("nsx250", "https://elicaelectric.com/کلید-کمپکت-اتوماتیک-سری-nsx250?page=2"),
            ("nsx400", "https://elicaelectric.com/کلید-کمپکت-اتوماتیک-سری-nsx400?page=1"),
            ("nsx630", "https://elicaelectric.com/کلید-اتوماتیک-کمپکت-سری-nsx630?page=1"),
        ]
        MCCBs = []
        for series, url in urls:
            success, data = self.controller._extract_product_info_from_elica(url)
            if not success:
                self.signals.finished.emit(False, data)
                return
            for MCCB in data:
                MCCB["series"] = series
                MCCB["supplier_id"] = 9
                MCCBs.append(MCCB)
        self.signals.finished.emit(True, MCCBs)


class MCCBDataEntryController:
    def __init__(self, view_ref):
        self.view = view_ref
        self.threadpool = QThreadPool()

    def get_all_mccbs(self):
        mccbs = get_all_mccbs()
        return mccbs

    def save_mccb(self, mccb_details):

        success, mccb_id = insert_mccb_to_db(
            rated_current=mccb_details["current"],
            breaking_capacity=mccb_details["breaking_capacity"],
            brand=mccb_details["brand"],
            order_number=mccb_details["order_number"],
        )
        if not success:
            return False, mccb_id

        success, supplier_id = get_supplier_by_name(mccb_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=mccb_id, supplier_id=supplier_id, price=mccb_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ MCCB Saved successfully"


    def update_mccbs_in_background(self):
        self.view.ui.update_mccb_prices_btn.setEnabled(False)
        worker = MCCBUpdateWorker(self)
        worker.signals.finished.connect(self.on_update_complete)
        self.threadpool.start(worker)

    # react to complete fetching data
    def on_update_complete(self, success, data):
        if success:
            self.view.show_table(data)
        else:
            print("❌ Error:", data)
        self.view.ui.update_mccb_prices_btn.setEnabled(True)


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
                rated_current = None
                price = None

                code_span = p.find('span', class_='stats-label', string='کد فنی:')
                if code_span:
                    order_number_span = code_span.find_next('span')
                    if order_number_span:
                        order_number = order_number_span.get_text(strip=True)

                title = ''
                tn = p.find('div', class_='name')
                if tn:
                    title = tn.get_text(strip=True)

                desc = ''
                desc_div = p.find('div', class_='description')
                if desc_div:
                    desc = desc_div.get_text(strip=True)

                amp_match = re.search(r'(\d+)\s*آمپر', title)
                if amp_match:
                    rated_current = float(amp_match.group(1))
                else:
                    amp_match = re.search(r'(\d+)\s*آمپر', desc)
                    if amp_match:
                        rated_current = float(amp_match.group(1))

                if rated_current is None:
                    continue

                bc_match = re.search(r'(\d+)\s*[kK]A|(\d+)\s*کیلو\s*آمپر', title + " " + desc)
                if bc_match:
                    breaking_capacity = bc_match.group(1) or bc_match.group(2)
                else:
                    breaking_capacity = rated_current

                price_span = p.find('span', class_='price-normal')
                if price_span:
                    price_text = price_span.get_text(strip=True)
                    price_clean = re.sub(r'[^\d]', '', price_text)
                    if price_clean.isdigit():
                        price = int(price_clean) * 10
                    else:
                        continue

                out.append({
                    'order_number': order_number,
                    'brand': "schneider electric",
                    'rated_current': rated_current,
                    'breaking_capacity': breaking_capacity,
                    'price': price
                })

            return (True, out) if out else (False, "No products found")
        except Exception as e:
            return False, str(e)

    def save_mccbs(self, mccbs_list):

        for mccb in mccbs_list:
            success, mccb_id = insert_mccb_to_db(
                rated_current=mccb["rated_current"],
                breaking_capacity=mccb["breaking_capacity"],
                brand=mccb["brand"],
                order_number=mccb["order_number"],
                created_by_id=2,  # System
            )
            if not success:
                return False, "Failed to save mccb"

            success, result = insert_component_suppliers_to_db(
                component_id=mccb_id,
                supplier_id=mccb["supplier_id"],
                price=mccb["price"],
                currency="IRR",
                created_by_id=2
            )
            if not success:
                return False, "Failed to save price"

        return True, "✅ MCCB Saved successfully"
