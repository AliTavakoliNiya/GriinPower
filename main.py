import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from views.electrical_tab_view import ElectricalTab
from views.result_tab_view import ResultTab
from views.project_information_view import ProjectInformationTab
from PyQt5.QtCore import QSettings

from views.message_box_view import show_message


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/main_window.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        # store all data of project as dictionary
        self.project_details = {"volt": 220,
                                "rev":0,
                                "bagfilter": {"touch_panel": "None"},
                                "vibration": {"status": False,
                                              "motors": {
                                                          "vibration": {"qty": 0, "power": 0}
                                              },
                                              "instruments": {},
                                },
                                "transport": {"status": False,
                                              "motors": {
                                                          "rotary": {"qty": 0, "power": 0},
                                                          "telescopic_chute": {"qty": 0, "power": 0},
                                                          "slide_gate": {"qty": 0, "power": 0},
                                                          "screw1": {"qty": 0, "power": 0},
                                                          "screw2": {"qty": 0, "power": 0}
                                              },
                                              "instruments": {
                                                          "proximity_switch": {"qty": 0, "brand": ""},
                                                          "speed_detector": {"qty": 0, "brand": ""},
                                                          "level_switch_bin": {"qty": 0, "brand": ""},
                                                          "level_transmitter": {"qty": 0, "brand": ""}
                                              }},
                                "fresh_air": {"status": False,
                                              "motors": {
                                                          "freshair_motor": {"qty": 0, "power": 0, "start_type":""},
                                                          "fresh_air_flap": {"qty": 0, "power": 0, "start_type":""},
                                                          "emergency_flap": {"qty": 0, "power": 0, "start_type":""}
                                              },
                                              "instruments": {
                                                          "proximity_switch": {"qty": 0, "brand": ""},
                                                          "temperature_transmitter": {"qty": 0, "brand": ""}
                                              }},
                                "hopper_heater": {"status": False,
                                              "motors": {
                                                          "elements": {"qty": 0, "power": 0}
                                                        },
                                              "instruments": {
                                                          "ptc": {"qty": 0, "power": 0}
                                                            }
                                                  },
                                "cable_dimension": 0
                                }

        self.project_information_tab = ProjectInformationTab(self.project_details)
        self.tabWidget.addTab(self.project_information_tab, "Project Information")

        self.electrical_tab = ElectricalTab(self.project_details)
        self.tabWidget.addTab(self.electrical_tab, "Electrical")

        self.result_tab = ResultTab(self, self.project_details)
        self.tabWidget.addTab(self.result_tab, "Result")

        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.tabWidget.setCurrentIndex(1)  # temprory

        self.themes = {
            "dark": "styles/dark_style.qss",
            "coffee": "styles/coffee_style.qss",
            "light": "styles/light_style.qss"
        }
        self.theme_menu = self.menuBar().addMenu("Change Theme")
        for name, path in self.themes.items():
            action = QtWidgets.QAction(name, self)
            action.triggered.connect(lambda checked, p=path: self.change_theme(p))
            self.theme_menu.addAction(action)
        last_theme = self.settings.value("theme_path", "styles/app_style.qss")
        self.apply_stylesheet(last_theme)

        self.showMaximized()

    def on_tab_changed(self, index):
        tab_text = self.tabWidget.tabText(index)
        if tab_text == "Result":
            self.result_tab.generate_panels()

    def apply_stylesheet(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        else:
            show_message(f"فایل {path} پیدا نشد.", "Details")

    def change_theme(self, path):
        self.apply_stylesheet(path)
        self.settings.setValue("theme_path", path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    view = MainView()

    sys.exit(app.exec_())
