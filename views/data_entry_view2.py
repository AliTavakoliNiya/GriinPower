from PyQt5.QtWidgets import QApplication
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow



class DataEntryUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("data_entry_view.ui", self)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataEntryUI()
    window.show()
    sys.exit(app.exec_())
