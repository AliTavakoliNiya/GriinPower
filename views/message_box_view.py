import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox


def show_message(message: str, title: str = ""):
    msg = QMessageBox()
    msg.setWindowIcon(QIcon('assets/Logo.ico'))
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok)

    apply_stylesheet(msg, "styles/dark_style.qss")  # <- Apply to the message box

    msg.exec_()


def apply_stylesheet(widget, path: str):
    if os.path.exists(path):
        with open(path, "r") as f:
            style = f.read()
            widget.setStyleSheet(style)
    else:
        # Warning: Avoid recursive call to `show_message` if it fails again!
        print(f"[ERROR] Stylesheet file '{path}' not found.")
