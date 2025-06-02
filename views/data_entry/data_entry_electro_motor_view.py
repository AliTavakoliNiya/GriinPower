from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView

from utils.thousand_separator_line_edit import format_line_edit_text
from utils.pandas_model import PandasModel  # Ensure this exists and is imported

import pandas as pd


class ElectroMotorDataEntryView:
    def __init__(self, ui):
        self.ui = ui

        self.ui.hide_show_motor_gp_box_btn.clicked.connect(self.hide_show_motor_gp_box_btn_func)

        self.ui.motor_list.setAlternatingRowColors(True)
        self.ui.motor_list.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.ui.motor_list.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.ui.motor_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.motor_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.motor_list.setWordWrap(True)
        self.ui.motor_list.setTextElideMode(Qt.ElideRight)
        self.ui.motor_list.verticalHeader().setVisible(False)
        self.ui.motor_list.setSelectionBehavior(QTableView.SelectRows)
        self.ui.motor_list.setSelectionMode(QTableView.SingleSelection)
        self.ui.motor_list.setSortingEnabled(True)

    def hide_show_motor_gp_box_btn_func(self):
        # Toggle visibility of motor_list table view
        is_visible = self.ui.motor_gp_box.isVisible()
        self.ui.motor_gp_box.setVisible(not is_visible)

        # Optionally update the button text
        self.ui.hide_show_motor_gp_box_btn.setText(
            "⏩" if is_visible else "⏪"
        )

    def format_price_fields(self):
        # Format price fields with thousand separator on text change
        self.ui.motor_price._last_text = ''
        self.ui.motor_price.textChanged.connect(lambda: format_line_edit_text(self.ui.motor_price))
        self.ui.motor_convert_currency_entry._last_text = ''
        self.ui.motor_convert_currency_entry.textChanged.connect(lambda: format_line_edit_text(self.ui.motor_convert_currency_entry))

    def update_currency_fields(self, currency):
        # Show/hide currency conversion field based on currency type
        if currency in ["USD", "EUR"]:
            self.ui.motor_convert_currency_entry.show()
            self.ui.motor_convert_currency_field.show()
        else:
            self.ui.motor_convert_currency_entry.setText("0")
            self.ui.motor_convert_currency_entry.hide()
            self.ui.motor_convert_currency_field.hide()

    def clear_motor_form(self):
        # Reset form fields to default
        for spin in [self.ui.motor_power, self.ui.motor_rpm, self.ui.motor_voltage]:
            spin.setValue(0)
        for combo in [self.ui.motor_brand, self.ui.motor_supplier, self.ui.motor_phone_email,
                      self.ui.motor_special_routine, self.ui.motor_starting_method,
                      self.ui.motor_cooling_method, self.ui.motor_ip, self.ui.motor_efficiency_class,
                      self.ui.motor_thermal_protection, self.ui.motor_paiting_ral]:
            combo.setCurrentIndex(0)
        self.ui.motor_price.setText("0")
        self.ui.motor_convert_currency_entry.setText("0")

    def show_motors_in_table(self, motor_list, headers):
        """
        Populate QTableView with motor data using a Pandas DataFrame and PandasModel.
        """
        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(motor_list, columns=headers)

        # Create and set the model
        model = PandasModel(df)
        self.ui.motor_list.setModel(model)
        self.ui.motor_list.resizeColumnsToContents()
