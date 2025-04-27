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

        # ------------------ Transport ------------------
        self.transport_checkbox.stateChanged.connect(self.transport_checkbox_handler)
        self.screw2_add_btn.clicked.connect(self.show_screw2)
        self.screw2_minuse_btn.clicked.connect(self.hide_screw2)
        self.hide_screw2()
        self.transport_checkbox.setChecked(False)

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
    def transport_zs_qty_handler(self):
        self.project_details["transport"]["instruments"]["proximity_switch"]["qty"] = self.transport_zs_qty.value()

    def transport_zs_kw_handler(self):
        self.project_details["transport"]["instruments"]["proximity_switch"][
            "brand"] = float(self.transport_zs_kw.currentText())
