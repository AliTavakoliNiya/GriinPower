import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtWidgets import QMessageBox


def show_message(message: str, title: str = ""):
    msg = QMessageBox()
    msg.setWindowIcon(QIcon('assets/Logo.ico'))
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok)

    apply_stylesheet(msg, "styles/dark_style.qss")  # <- Apply to the message box

    msg.exec_()


def confirmation(text):
    dialog = QDialog()
    dialog.setWindowTitle(" ")
    apply_stylesheet(dialog, "styles/dark_style.qss")
    dialog.setWindowIcon(QIcon('assets/Logo.ico'))
    dialog.setWindowModality(Qt.ApplicationModal)

    layout = QVBoxLayout()
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    button_layout = QHBoxLayout()
    yes_button = QPushButton("Yes")
    no_button = QPushButton("No")
    yes_button.clicked.connect(dialog.accept)
    no_button.clicked.connect(dialog.reject)
    button_layout.addStretch()
    button_layout.addWidget(yes_button)
    button_layout.addWidget(no_button)
    button_layout.addStretch()

    layout.addLayout(button_layout)
    dialog.setLayout(layout)

    return dialog.exec_()


def apply_stylesheet(widget, path: str):
    if os.path.exists(path):
        with open(path, "r") as f:
            style = f.read()
            widget.setStyleSheet(style)
    else:
        # Warning: Avoid recursive call to `show_message` if it fails again!
        print(f"[ERROR] Stylesheet file '{path}' not found.")
