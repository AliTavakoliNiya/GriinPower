from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSpinBox


class ElectricalTab(QWidget):
    def __init__(self, project_details):
        super().__init__()
        uic.loadUi("ui/electrical_tab.ui", self)

        self.project_details = project_details

        # ------------------ Bagfilter ------------------
        self.cable_length.valueChanged.connect(self.cable_length_handler)
        self.touch_panel_model.currentTextChanged.connect(self.touch_panel_model_handler)

        # ------------------ Transport ------------------
        self.transport_checkbox.stateChanged.connect(self.transport_checkbox_handler)
        self.screw2_add_btn.clicked.connect(self.show_screw2)
        self.screw2_minuse_btn.clicked.connect(self.hide_screw2)
        self.hide_screw2()
        self.transport_checkbox.setChecked(False)

        # motors
        self.rotary_qty.valueChanged.connect(self.rotary_qty_handler)
        self.rotary_kw.currentIndexChanged.connect(self.rotary_kw_handler)
        self.telescopic_chute_qty.valueChanged.connect(self.telescopic_chute_qty_handler)
        self.telescopic_chute_kw.currentIndexChanged.connect(self.telescopic_chute_kw_handler)
        self.slide_gate_qty.valueChanged.connect(self.slide_gate_qty_handler)
        self.slide_gate_kw.currentIndexChanged.connect(self.slide_gate_kw_handler)
        self.screw1_qty.valueChanged.connect(self.screw1_qty_handler)
        self.screw1_kw.currentIndexChanged.connect(self.screw1_kw_handler)
        self.screw2_qty.valueChanged.connect(self.screw2_qty_handler)
        self.screw2_kw.currentIndexChanged.connect(self.screw2_kw_handler)

        # instruments
        self.transport_spd_qty.valueChanged.connect(self.transport_spd_qty_handler)
        self.transport_spd_brand.currentIndexChanged.connect(self.transport_spd_brand_handler)

        self.transport_zs_qty.valueChanged.connect(self.transport_zs_qty_handler)
        self.transport_zs_brand.currentIndexChanged.connect(self.transport_zs_brand_handler)

        self.transport_ls_bin_qty.valueChanged.connect(self.transport_ls_bin_qty_handler)
        self.transport_ls_bin_brand.currentIndexChanged.connect(self.transport_ls_bin_brand_handler)

        self.transport_lt_qty.valueChanged.connect(self.transport_lt_qty_handler)
        self.transport_lt_brand.currentIndexChanged.connect(self.transport_lt_brand_handler)

        # ------------------ Vibration ------------------
        self.vibration_checkbox.stateChanged.connect(self.vibration_checkbox_handler)
        self.vibration_checkbox.setChecked(False)

        # motors
        self.vibration_motor_qty.valueChanged.connect(self.vibration_motor_qty_handler)
        self.vibration_motor_kw.currentIndexChanged.connect(self.vibration_motor_kw_handler)

        # ------------------ Fresh Air ------------------
        self.freshair_checkbox.stateChanged.connect(self.freshair_checkbox_handler)
        self.freshair_checkbox.setChecked(False)

        # motors
        self.freshair_motor_qty.valueChanged.connect(self.freshair_motor_qty_handler)
        self.freshair_motor_kw.currentIndexChanged.connect(self.freshair_motor_kw_handler)
        self.freshair_motor_start_type.currentIndexChanged.connect(self.freshair_motor_start_type_handler)

        self.freshair_flap_motor_qty.valueChanged.connect(self.freshair_flap_motor_qty_handler)
        self.freshair_flap_motor_kw.currentIndexChanged.connect(self.freshair_flap_motor_kw_handler)
        self.freshair_flap_motor_start_type.currentIndexChanged.connect(self.freshair_flap_motor_start_type_handler)

        self.emergency_flap_motor_kw.currentIndexChanged.connect(self.emergency_flap_motor_kw_handler)
        self.emergency_flap_start_type.currentIndexChanged.connect(self.emergency_flap_start_type_handler)

        # instruments
        self.freshair_tt_qty.valueChanged.connect(self.freshair_tt_qty_handler)
        self.freshair_tt_brand.currentIndexChanged.connect(self.freshair_tt_brand_handler)

        self.freshair_zs_qty.valueChanged.connect(self.freshair_zs_qty_handler)
        self.freshair_zs_brand.currentIndexChanged.connect(self.freshair_zs_brand_handler)

        # ------------------ Heater Hopper ------------------
        self.hopper_heater_checkbox.stateChanged.connect(self.hopper_heater_checkbox_handler)
        self.hopper_heater_checkbox.setChecked(False)

        self.hopper_heater_qty.valueChanged.connect(self.hopper_heater_qty_handler)
        self.hopper_heater_kw.currentIndexChanged.connect(self.hopper_heater_kw_handler)

        # PTC heaters
        self.hopper_heater_ptc_brand.currentIndexChanged.connect(self.hopper_heater_ptc_brand_handler)

        self.show()

    def cable_length_handler(self):
        self.project_details["cable_dimension"] = self.cable_length.value()

    # ------------------ reset_qtys ------------------
    def reset_qtys(self, d):
        for key, value in d.items():
            if isinstance(value, dict):
                self.reset_qtys(value)
            elif key == "qty":
                d[key] = 0

    # ------------------ Transport ------------------
    def transport_checkbox_handler(self, state):
        self.project_details["transport"]["status"] = state == Qt.Checked
        self.reset_qtys(self.project_details["transport"])

        for child in self.transport_gbox.findChildren(QSpinBox):
            child.setValue(0)

        for child in self.transport_gbox.findChildren(QWidget):
            child.setEnabled(state == Qt.Checked)
        self.transport_checkbox.setEnabled(True)  # Except This one

    def show_screw2(self):
        self.screw2_minuse_btn.show()
        self.screw2_label.show()

        self.screw2_qty.show()
        self.screw2_qty.setValue(0)

        self.screw2_kw.show()
        self.screw2_kw.setCurrentIndex(0)

    def hide_screw2(self):
        self.screw2_minuse_btn.hide()
        self.screw2_label.hide()

        self.screw2_qty.hide()
        self.screw2_qty.setValue(0)

        self.screw2_kw.hide()
        self.screw2_kw.setCurrentIndex(0)

    ###### rotary
    def rotary_qty_handler(self):
        self.project_details["transport"]["motors"]["rotary"]["qty"] = self.rotary_qty.value()
        # rotary affect speed detector
        if self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value() == 0:
            self.transport_spd_qty.setValue(0)
            self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = 0
        elif self.transport_spd_qty.value() < self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value():
            spd_qty = self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value()
            self.transport_spd_qty.setValue(spd_qty)
            self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = spd_qty

    def rotary_kw_handler(self):
        self.project_details["transport"]["motors"]["rotary"]["power"] = float(self.rotary_kw.currentText())

    ###### telescopic_chute
    def telescopic_chute_qty_handler(self):
        self.project_details["transport"]["motors"]["telescopic_chute"]["qty"] = self.telescopic_chute_qty.value()

    def telescopic_chute_kw_handler(self):
        self.project_details["transport"]["motors"]["telescopic_chute"][
            "power"] = float(self.telescopic_chute_kw.currentText())

    ###### slide_gate
    def slide_gate_qty_handler(self):
        self.project_details["transport"]["motors"]["slide_gate"]["qty"] = self.slide_gate_qty.value()
        # slide gate affect proximity switch
        if self.slide_gate_qty.value() != 0:
            if self.transport_zs_qty.value() < self.slide_gate_qty.value() * 2:
                self.transport_zs_qty.setValue(self.slide_gate_qty.value() * 2)
                self.project_details["transport"]["instruments"]["proximity_switch"] \
                    ["qty"] = self.slide_gate_qty.value() * 2
        else:
            self.transport_zs_qty.setValue(0)
            self.project_details["transport"]["instruments"]["proximity_switch"]["qty"] = 0

    def slide_gate_kw_handler(self):
        self.project_details["transport"]["motors"]["slide_gate"]["power"] = float(self.slide_gate_kw.currentText())

    ###### screw1_qty
    def screw1_qty_handler(self):
        self.project_details["transport"]["motors"]["screw1"]["qty"] = self.screw1_qty.value()
        # screw affect speed detector
        if self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value() == 0:
            self.transport_spd_qty.setValue(0)
            self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = 0
        elif self.transport_spd_qty.value() < self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value():
            spd_qty = self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value()
            self.transport_spd_qty.setValue(spd_qty)
            self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = spd_qty

    def screw1_kw_handler(self):
        self.project_details["transport"]["motors"]["screw1"]["power"] = float(self.screw1_kw.currentText())

    ###### screw2_qty
    def screw2_qty_handler(self):
        self.project_details["transport"]["motors"]["screw2"]["qty"] = self.screw2_qty.value()
        # screw affect speed detector
        if self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value() == 0:
            self.transport_spd_qty.setValue(0)
            self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = 0
        elif self.transport_spd_qty.value() < self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value():
            spd_qty = self.rotary_qty.value() + self.screw1_qty.value() + self.screw2_qty.value()
            self.transport_spd_qty.setValue(spd_qty)
            self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = spd_qty

    def screw2_kw_handler(self):
        self.project_details["transport"]["motors"]["screw2"]["power"] = float(self.screw2_kw.currentText())

    ###### proximity switch for slide gate
    def transport_zs_qty_handler_legacy(self):
        self.project_details["transport"]["instruments"]["proximity_switch"]["qty"] = self.transport_zs_qty.value()

    def transport_zs_kw_handler(self):
        self.project_details["transport"]["instruments"]["proximity_switch"][
            "brand"] = float(self.transport_zs_kw.currentText())

    def touch_panel_model_handler(self, text):
        self.project_details["bagfilter"]["touch_panel"] = text

    ###### Instrument handlers
    def transport_spd_qty_handler(self):
        """Speed detector quantity handler"""
        self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = self.transport_spd_qty.value()

    def transport_spd_brand_handler(self):
        """Speed detector brand handler"""
        self.project_details["transport"]["instruments"]["speed_detector"][
            "brand"] = self.transport_spd_brand.currentText()

    def transport_zs_qty_handler(self):
        """Proximity switch quantity handler"""
        self.project_details["transport"]["instruments"]["proximity_switch"]["qty"] = self.transport_zs_qty.value()

    def transport_zs_brand_handler(self):
        """Proximity switch brand handler"""
        self.project_details["transport"]["instruments"]["proximity_switch"][
            "brand"] = self.transport_zs_brand.currentText()

    def transport_ls_bin_qty_handler(self):
        """Level switch bin quantity handler"""
        self.project_details["transport"]["instruments"]["level_switch_bin"]["qty"] = self.transport_ls_bin_qty.value()

    def transport_ls_bin_brand_handler(self):
        """Level switch bin brand handler"""
        self.project_details["transport"]["instruments"]["level_switch_bin"][
            "brand"] = self.transport_ls_bin_brand.currentText()

    def transport_lt_qty_handler(self):
        """Level transmitter quantity handler"""
        self.project_details["transport"]["instruments"]["level_transmitter"]["qty"] = self.transport_lt_qty.value()

    def transport_lt_brand_handler(self):
        """Level transmitter bin brand handler"""
        self.project_details["transport"]["instruments"]["level_transmitter"][
            "brand"] = self.transport_lt_brand.currentText()

    # ------------------ Vibration ------------------

    def vibration_checkbox_handler(self, state):
        self.project_details["vibration"]["status"] = state == Qt.Checked
        self.reset_qtys(self.project_details["vibration"])

        for child in self.vibration_gbox.findChildren(QSpinBox):
            child.setValue(0)

        for child in self.vibration_gbox.findChildren(QWidget):
            child.setEnabled(state == Qt.Checked)
        self.vibration_checkbox.setEnabled(True)  # Except This one

    def vibration_motor_qty_handler(self):
        self.project_details["vibration"]["motors"]["vibration"]["qty"] = self.vibration_motor_qty.value()

    def vibration_motor_kw_handler(self):
        self.project_details["vibration"]["motors"]["vibration"]["power"] = float(self.vibration_motor_kw.currentText())

    # ------------------ Fresh Air ------------------
    def freshair_checkbox_handler(self, state):
        self.project_details["fresh_air"]["status"] = state == Qt.Checked
        self.reset_qtys(self.project_details["fresh_air"])

        for child in self.freshair_gbox.findChildren(QSpinBox):
            child.setValue(0)

        for child in self.freshair_gbox.findChildren(QWidget):
            child.setEnabled(state == Qt.Checked)
        self.freshair_checkbox.setEnabled(True)

    ###### Fresh Air Motor
    def freshair_motor_qty_handler(self):
        self.project_details["fresh_air"]["motors"]["freshair_motor"]["qty"] = self.freshair_motor_qty.value()
        # Affect proximity switch quantity
        if self.freshair_motor_qty.value() != 0:
            if self.freshair_zs_qty.value() < self.freshair_motor_qty.value() * 2:
                self.freshair_zs_qty.setValue(self.freshair_motor_qty.value() * 2)
                self.project_details["fresh_air"]["instruments"]["proximity_switch"]["qty"] = self.freshair_motor_qty.value() * 2

    def freshair_motor_kw_handler(self):
        self.project_details["fresh_air"]["motors"]["freshair_motor"]["power"] = float(self.freshair_motor_kw.currentText())

    def freshair_motor_start_type_handler(self):
        self.project_details["fresh_air"]["motors"]["freshair_motor"]["start_type"] = self.freshair_motor_start_type.currentText()

    ###### Fresh Air Flap Motor
    def freshair_flap_motor_qty_handler(self):
        self.project_details["fresh_air"]["motors"]["fresh_air_flap"]["qty"] = self.freshair_flap_motor_qty.value()

    def freshair_flap_motor_kw_handler(self):
        self.project_details["fresh_air"]["motors"]["fresh_air_flap"]["power"] = float(self.freshair_flap_motor_kw.currentText())

    def freshair_flap_motor_start_type_handler(self):
        self.project_details["fresh_air"]["motors"]["fresh_air_flap"]["start_type"] = self.freshair_flap_motor_start_type.currentText()

    ###### Emergency Flap Motor
    def emergency_flap_motor_kw_handler(self):
        self.project_details["fresh_air"]["motors"]["emergency_flap"]["power"] = float(self.emergency_flap_motor_kw.currentText())

    def emergency_flap_start_type_handler(self):
        self.project_details["fresh_air"]["motors"]["emergency_flap"]["start_type"] = self.emergency_flap_start_type.currentText()

    ###### Fresh Air Instruments
    def freshair_tt_qty_handler(self):
        """Temperature transmitter quantity handler"""
        self.project_details["fresh_air"]["instruments"]["temperature_transmitter"]["qty"] = self.freshair_tt_qty.value()

    def freshair_tt_brand_handler(self):
        """Temperature transmitter brand handler"""
        self.project_details["fresh_air"]["instruments"]["temperature_transmitter"]["brand"] = self.freshair_tt_brand.currentText()

    def freshair_zs_qty_handler(self):
        """Proximity switch quantity handler"""
        self.project_details["fresh_air"]["instruments"]["proximity_switch"]["qty"] = self.freshair_zs_qty.value()

    def freshair_zs_brand_handler(self):
        """Proximity switch brand handler"""
        self.project_details["fresh_air"]["instruments"]["proximity_switch"]["brand"] = self.freshair_zs_brand.currentText()

    # ------------------ Heater Hopper ------------------
    def hopper_heater_checkbox_handler(self, state):
        self.project_details["hopper_heater"]["status"] = state == Qt.Checked
        self.reset_qtys(self.project_details["hopper_heater"])

        for child in self.hopper_heater_gbox.findChildren(QSpinBox):
            child.setValue(0)

        for child in self.hopper_heater_gbox.findChildren(QWidget):
            child.setEnabled(state == Qt.Checked)
        self.hopper_heater_checkbox.setEnabled(True)
        self.hopper_heater_ptc_qty.setEnabled(False) # user always not allowed to change PTC Quantity

    ###### Elements
    def hopper_heater_qty_handler(self):
        """heater quantity handler"""
        self.project_details["hopper_heater"]["motors"]["elements"]["qty"] = self.hopper_heater_qty.value()
        self.project_details["hopper_heater"]["instruments"]["ptc"]["qty"] = self.hopper_heater_qty.value() * 2
        self.hopper_heater_ptc_qty.setText(f"Qty: {str(self.hopper_heater_qty.value() * 2)}")

    def hopper_heater_kw_handler(self):
        self.project_details["hopper_heater"]["motors"]["elements"]["power"] = float(self.hopper_heater_kw.currentText())

    ######  Instruments

    def hopper_heater_ptc_brand_handler(self):
        """PTC heater brand handler"""
        self.project_details["hopper_heater"]["instruments"]["ptc"]["brand"] = self.hopper_heater_ptc_brand.currentText()

