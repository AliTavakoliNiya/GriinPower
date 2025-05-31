from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from controllers.user_session import UserSession
from views.data_entry.data_entry_electro_motor import ElectroMotorDataEntry
from views.vendor_view import VendorEntry


class DataEntry(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/data_entry.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.user_logged = UserSession()

        self.item_list.currentRowChanged.connect(self.display_entry)  # this match QListWidget to QStackWidget

        self.electro_motor_controller = ElectroMotorDataEntry(self)

        self.refresh_data()
        self.show()

    def refresh_data(self):
        pass


    def display_entry(self, index):
        self.item_stack.setCurrentIndex(index)

    def add_vendor(self):
        self.venor_application_window = VendorEntry(parent=self)





