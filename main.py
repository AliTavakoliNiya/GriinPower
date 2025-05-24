import sys

from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from utils.database import SessionLocal
from views.login_view import LoginView

from views.message_box_view import show_message

from controllers.user_session import UserSession
from views.tender_application_view import TenderApplication
from views.data_entry_view import DataEntry


class GriinPower(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/GrrinPower.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.new_project_btn.clicked.connect(self.open_new_project_func)
        self.data_entry_btn.clicked.connect(self.open_data_entry_func)

        self.showMaximized()

    def open_new_project_func(self):
        self.tender_application_window = TenderApplication()

    def open_data_entry_func(self):
        self.data_entry_window = DataEntry()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize DB
    db_session = SessionLocal()

    # Show login dialog
    login = LoginView(db_session)
    if login.exec_() == QDialog.Accepted:
        session = QSettings("Griin", "GriinPower")
        username = session.value("last_username", "")
        current_user = UserSession()

        # show_message(f"Welcome back, {current_user.first_name} {current_user.last_name}", title="Welcome")

        window = GriinPower()
        window.show()
        sys.exit(app.exec_())
