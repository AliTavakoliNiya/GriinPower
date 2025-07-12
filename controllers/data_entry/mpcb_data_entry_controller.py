import re
import time

import requests
from bs4 import BeautifulSoup

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool


from models.component_suppliers import insert_component_suppliers_to_db
from models.items.mpcb import get_all_mpcbs, insert_mpcb_to_db
from models.suppliers import get_supplier_by_name


class MPCBUpdateWorkerSignals(QObject):
    """ define signals to tell main thread """
    finished = pyqtSignal(bool, object)  # success, data


class MPCBUpdateWorker(QRunnable):
    """ running Worker in seprate Thread """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.signals = MPCBUpdateWorkerSignals()

    def run(self):
        urls = [
            ("GV2", "https://elicaelectric.com/انواع-کليد-حرارتی-مغناطيسی-سری-gv2"),
            ("GV2P", "https://elicaelectric.com/انواع-کليد-حرارتی-مغناطيسی-سری-gv2p"),
            ("GV3", "https://elicaelectric.com/انواع-کليد-حرارتی-مغناطيسی-سری-gv3"),
            ("GV4", "https://elicaelectric.com/کلید-حرارتی-مغناطیسی-سری-gv4-اشنایدر-الکتریک"),
            ("GV5", "https://elicaelectric.com/کلید-حرارتی-مغناطیسی-سری-gv5-اشنایدر-الکتریک")
        ]
        MPCBs = []
        for series, url in urls:
            success, data = self.controller._extract_product_info_from_elica(url)
            if not success:
                self.signals.finished.emit(False, data)
                return
            for MPCB in data:
                MPCB["series"] = series
                MPCB["supplier_id"] = 9
                MPCBs.append(MPCB)
        self.signals.finished.emit(True, MPCBs)


class MPCBDataEntryController:
    def __init__(self, view_ref):
        self.view = view_ref
        self.threadpool = QThreadPool()


    def get_all_mpcbs(self):
        mpcbs = get_all_mpcbs()
        return mpcbs

    def save_mpcb(self, mpcb_details):

        success, mpcb_id = insert_mpcb_to_db(
            brand=mpcb_details["brand"],
            order_number=mpcb_details["order_number"],
            min_current=mpcb_details["min_current"],
            max_current=mpcb_details["max_current"],
            breaking_capacity=mpcb_details["breaking_capacity"],
            trip_class=mpcb_details["trip_class"]
        )
        if not success:
            return False, mpcb_id

        success, supplier_id = get_supplier_by_name(mpcb_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=mpcb_id, supplier_id=supplier_id, price=mpcb_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ MPCB Saved successfully"
    
    def update_mpcbs_in_background(self):
        self.view.ui.update_mpcb_prices_btn.setEnabled(False)
        worker = MPCBUpdateWorker(self)
        worker.signals.finished.connect(self.on_update_complete)
        self.threadpool.start(worker)

    # react to complete fetching data
    def on_update_complete(self, success, data):
        if success:
            self.view.show_table(data)
        else:
            print("❌ Error:", data)
        self.view.ui.update_mpcb_prices_btn.setEnabled(True)

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
                brand = None
                min_current = max_current = None
                breaking_capacity = None
                price = None

                # Order Number
                cs = p.find('span', class_='stats-label', string='کد فنی:')
                if cs:
                    order_number = cs.find_next('span').text.strip()


                # Title (for current and breaking)
                title = ''
                tn = p.find('div', class_='name')
                if tn:
                    title = tn.get_text(strip=True)

                # min/max current
                cm = re.search(r'(\d+(?:\.\d+)?)\s*(?:تا|الی|-)\s*(\d+(?:\.\d+)?)\s*آمپر', title)
                if cm:
                    min_current = float(cm.group(1))
                    max_current = float(cm.group(2))
                else:
                    continue

                # breaking capacity
                bm = re.search(r'قطع\s*(\d+)\s*کیلو\s*آمپر', title)
                if bm:
                    breaking_capacity = f"{bm.group(1)}"
                else:
                    breaking_capacity = max_current

                # Price
                ps = p.find('span', class_='price-normal')
                if ps:
                    txt = ps.get_text(strip=True)
                    # حذف تمام کاراکترهای غیر عددی (به‌جز ممیز)
                    txt_clean = re.sub(r'[^\d]', '', txt)
                    if txt_clean.isdigit():
                        price = int(txt_clean) * 10  # تبدیل به ریال
                    else:
                        continue


                out.append({
                    'order_number': order_number,
                    'brand': "schneider electric",
                    'min_current': min_current,
                    'max_current': max_current,
                    'breaking_capacity': breaking_capacity,
                    'trip_class': "",
                    'price': price
                })

            return (True, out) if out else (False, "No products found")
        except Exception as e:
            return False, str(e)

    def save_mpcbs(self, mpcbs_list):

        for mpcb in mpcbs_list:
            success, mpcb_id = insert_mpcb_to_db(
                min_current=mpcb["min_current"],
                max_current=mpcb["max_current"],
                breaking_capacity=mpcb["breaking_capacity"],
                trip_class=mpcb["trip_class"],
                brand=mpcb["brand"],
                order_number=mpcb["order_number"],
                created_by_id=2, # System
            )
            if not success:
                return False, "Failed to save mpcb"

            success, result = insert_component_suppliers_to_db(
                component_id=mpcb_id, supplier_id=mpcb["supplier_id"],
                price=mpcb["price"], currency="IRR", created_by_id=2
            )
            if not success:
                return False, "Failed to save price"

        return True, "✅ MPCB Saved successfully"
