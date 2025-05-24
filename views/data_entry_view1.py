from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QGroupBox, QStackedWidget, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
import sys


class StyledEntry(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid gray; border-radius: 8px; margin-top: 10px; } "
                           "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        self.setLayout(QVBoxLayout())


class ContactorForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        form = StyledEntry("Contactor Information")
        self.item_id = QLineEdit()
        self.current_a = QLineEdit()
        self.modified_by = QLineEdit()
        self.modified_at = QLineEdit()

        for label, field in [("Item ID", self.item_id), ("Current (A)", self.current_a),
                             ("Modified By", self.modified_by), ("Modified At", self.modified_at)]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label), 1)
            row.addWidget(field, 3)
            form.layout().addLayout(row)

        self.save_button = QPushButton("💾 Save Contactor")
        self.save_button.clicked.connect(self.save_data)
        layout.addWidget(form)
        layout.addStretch()
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)

    def save_data(self):
        QMessageBox.information(self, "Saved", "Contactor data saved.")


class BimetalForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        form = StyledEntry("Bimetal Information")
        self.item_id = QLineEdit()
        self.current_min = QLineEdit()
        self.current_max = QLineEdit()
        self.trip_time = QLineEdit()
        self.modified_by = QLineEdit()
        self.modified_at = QLineEdit()

        for label, field in [("Item ID", self.item_id), ("Min Current (A)", self.current_min),
                             ("Max Current (A)", self.current_max), ("Trip Time (s)", self.trip_time),
                             ("Modified By", self.modified_by), ("Modified At", self.modified_at)]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label), 1)
            row.addWidget(field, 3)
            form.layout().addLayout(row)

        self.save_button = QPushButton("💾 Save Bimetal")
        self.save_button.clicked.connect(self.save_data)
        layout.addWidget(form)
        layout.addStretch()
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)

    def save_data(self):
        QMessageBox.information(self, "Saved", "Bimetal data saved.")


class DataEntryUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧾 Equipment Data Entry")
        self.setMinimumSize(500, 400)

        main_layout = QHBoxLayout()
        self.menu = QListWidget()
        self.menu.setFixedWidth(150)
        self.menu.addItem(QListWidgetItem("Contactor"))
        self.menu.addItem(QListWidgetItem("Bimetal"))
        self.menu.currentRowChanged.connect(self.display_form)

        self.stack = QStackedWidget()
        self.stack.addWidget(ContactorForm())
        self.stack.addWidget(BimetalForm())

        main_layout.addWidget(self.menu)
        main_layout.addWidget(self.stack, 1)

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2e86de;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1b4f72;
            }
            QLineEdit {
                padding: 4px;
                border-radius: 4px;
                border: 1px solid #ccc;
            }
        """)

        self.setLayout(main_layout)

    def display_form(self, index):
        self.stack.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataEntryUI()
    window.show()
    sys.exit(app.exec_())
