import re
import time

import requests
from bs4 import BeautifulSoup

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

from models.component_suppliers import insert_component_suppliers_to_db
from models.items.contactor import get_all_contactors, insert_contactor_to_db
from models.suppliers import get_supplier_by_name


class ContactorUpdateWorkerSignals(QObject):
    """ define signals to tell main thread """
    finished = pyqtSignal(bool, object)  # success, data


class ContactorUpdateWorker(QRunnable):
    """ running Worker in seprate Thread """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.signals = ContactorUpdateWorkerSignals()

    def run(self):
        urls = [
            ("G", "https://elicaelectric.com/contactor-tesys-giga"),
            ("D", "https://elicaelectric.com/کنتاکتور-220-ولت-ac-سری-d-اشنایدر-contactor-220-v-ac-coil")
        ]
        contactors = []
        for series, url in urls:
            success, data = self.controller._extract_product_info_from_elica(url)
            if not success:
                self.signals.finished.emit(False, data)
                return
            for contactor in data:
                contactor["series"] = series
                contactor["supplier_id"] = 9
                contactors.append(contactor)
        self.signals.finished.emit(True, contactors)


class ContactorDataEntryController:
    def __init__(self, view_ref):
        self.view = view_ref
        self.threadpool = QThreadPool()

    def get_all_contactors(self):
        contactors = get_all_contactors()
        return contactors

    def save_contactor(self, contactor_details):

        success, contactor_id = insert_contactor_to_db(
            rated_current=contactor_details["current"],
            coil_voltage=contactor_details["voltage"],
            brand=contactor_details["brand"],
            order_number=contactor_details["order_number"],
        )
        if not success:
            return False, contactor_id

        success, supplier_id = get_supplier_by_name(contactor_details["supplier"])
        if not success:
            return False, supplier_id

        success, result = insert_component_suppliers_to_db(
            component_id=contactor_id, supplier_id=supplier_id, price=contactor_details["price"], currency="IRR"
        )
        if not success:
            return False, result

        return True, "✅ Contactor Saved successfully"

    def update_contactors_in_background(self):
        self.view.ui.update_contactor_prices_btn.setEnabled(False)
        worker = ContactorUpdateWorker(self)
        worker.signals.finished.connect(self.on_update_complete)
        self.threadpool.start(worker)

    # react to complete fetching data
    def on_update_complete(self, success, data):
        if success:
            self.view.show_table(data)
        else:
            print("❌ Error:", data)
        self.view.ui.update_contactor_prices_btn.setEnabled(True)

    def _extract_product_info_from_elica(self, url):
        time.sleep(2)
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
            })
            response = session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            product_divs = soup.find_all('div', class_='product-thumb')
            results = []

            for product in product_divs:
                title_tag = product.find('div', class_='name')
                title = title_tag.get_text(strip=True) if title_tag else ''
                amp_match = re.search(r'(\d+)\s*آمپر', title)
                amp = int(amp_match.group(1)) if amp_match else None

                code_span = product.find('span', class_='stats-label', string='کد فنی:')
                order_number = code_span.find_next('span').text.strip() if code_span else None

                price_span = product.find('span', class_='price-normal')
                price_text = price_span.get_text(strip=True) if price_span else None
                if price_text:
                    try:
                        price_text = price_text.replace(',', '').replace('تومان', '').strip()
                        price = int(price_text) * 10
                        results.append({
                            'order_number': order_number,
                            'brand': "schneider electric",
                            'rated_current': amp,
                            'coil_voltage': 220,
                            'price': price
                        })
                    except:
                        print("قیمت قابل تبدیل نبود")

            if not results:
                return False, "No products found or invalid page structure"
            return True, results

        except Exception as e:
            return False, f"Error while fetching: {e}"

    def save_contactors(self, contactors_list):

        for contactor in contactors_list:
            success, contactor_id = insert_contactor_to_db(
                rated_current=contactor["rated_current"],
                coil_voltage=contactor["coil_voltage"],
                brand=contactor["brand"],
                order_number=contactor["order_number"],
                created_by_id=2, # System
            )
            if not success:
                return False, "Failed to save contactor"

            success, result = insert_component_suppliers_to_db(
                component_id=contactor_id, supplier_id=contactor["supplier_id"],
                price=contactor["price"], currency="IRR", created_by_id=2
            )
            if not success:
                return False, "Failed to save price"

        return True, "✅ Contactor Saved successfully"