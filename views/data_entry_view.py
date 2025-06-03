from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from controllers.data_entry_electro_motor_controller import ElectroMotorDataEntryController
from controllers.user_session import UserSession
from views.supplier_view import SupplierEntry


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

        self.electro_motor_data_entry = ElectroMotorDataEntryController(self)

        self.motor_add_supplier_btn.clicked.connect(self.add_supplier)

        self.hide_show_motor_gp_box_btn.clicked.connect(self.hide_show_motor_gp_box_btn_func)


        self.show()


    def display_entry(self, index):
        self.item_stack.setCurrentIndex(index)

    def add_supplier(self):
        self.venor_application_window = SupplierEntry(parent=self)

    def hide_show_motor_gp_box_btn_func(self):
        # Toggle visibility of motor_list table view
        is_visible = self.motor_gp_box.isVisible()
        self.motor_gp_box.setVisible(not is_visible)

        # Optionally update the button text
        self.hide_show_motor_gp_box_btn.setText(
            "⏩" if is_visible else "⏪"
        )





