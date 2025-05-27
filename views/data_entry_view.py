from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from views.vendor_view import VendorEntry


class DataEntry(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/data_entry.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.item_list.currentRowChanged.connect(self.display_entry)  # this match QListWidget to QStackWidget

        self.add_vendor_btn1.clicked.connect(self.add_vendor)
        self.add_vendor_btn2.clicked.connect(self.add_vendor)
        self.add_vendor_btn3.clicked.connect(self.add_vendor)
        self.add_vendor_btn4.clicked.connect(self.add_vendor)
        self.add_vendor_btn5.clicked.connect(self.add_vendor)
        self.add_vendor_btn6.clicked.connect(self.add_vendor)
        self.add_vendor_btn7.clicked.connect(self.add_vendor)

        self.show()

    def display_entry(self, index):
        self.item_stack.setCurrentIndex(index)

    def add_vendor(self):
        self.venor_application_window = VendorEntry(parent=self)
