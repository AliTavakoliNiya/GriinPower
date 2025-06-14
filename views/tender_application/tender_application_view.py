from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow

from controllers.tender_application.project_session_controller import ProjectSession
from views.tender_application.electrical_tab_view import ElectricalTab
from views.tender_application.project_information_view import ProjectInformationTab
from views.tender_application.result_tab_view import ResultTab


class TenderApplication(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load the main window UI (with the QTabWidget)
        uic.loadUi("ui/tender_application/tender_application.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.electrical_specs = ProjectSession().project_electrical_specs

        self.project_information_tab = ProjectInformationTab(self)
        self.tabWidget.addTab(self.project_information_tab, "Project Information")

        self.electrical_tab = ElectricalTab(self)
        self.tabWidget.addTab(self.electrical_tab, "Electrical")

        self.result_tab = ResultTab(self)
        self.tabWidget.addTab(self.result_tab, "Result")

        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.tabWidget.setCurrentIndex(0)  # Start at first tab

        self.showMaximized()

    def on_tab_changed(self, index):
        if index == 1:  # Electrical
            if not self.project_information_tab.check_info_tab_ui_rules():
                self.tabWidget.setCurrentIndex(0)

        if index == 2:  # Result
            if not self.electrical_tab.check_electrical_tab_ui_rules():
                self.tabWidget.setCurrentIndex(1)
            elif not self.project_information_tab.check_info_tab_ui_rules():
                self.tabWidget.setCurrentIndex(0)
            else:
                self.result_tab.generate_panels()

    def set_rev_hint(self, rev_number):
        rev_specs = self.electrical_specs
        rev_number = "00"
        """----------------------project_information_tab----------------------"""
        info_tab = self.project_information_tab
        info_tab.max_temprature.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['maximum_temprature']}</b>℃")
        info_tab.min_temprature.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['minimum_temprature']}</b>℃")
        info_tab.project_m_voltage.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['m_voltage']/1000}</b>KV")
        info_tab.project_l_voltage.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['l_voltage']}</b>V")
        info_tab.project_voltage_variation.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['voltage_variation']}</b>%")
        info_tab.altitude_elevation.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['altitude_elevation']}</b>m")
        info_tab.humidity.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['humidity']}</b>%")
        info_tab.project_frequency.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['voltage_frequency']}</b>Hz")
        info_tab.project_frequency_variation.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['project_info']['frequency_variation']}</b>%")
        info_tab.proj_avl_siemens.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{'siemens' in rev_specs['project_info']['proj_avl']}</b>")
        info_tab.proj_avl_schneider.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{'Schneider Electric' in rev_specs['project_info']['proj_avl']}</b>")
        info_tab.proj_avl_hyundai.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{'Hyundai' in rev_specs['project_info']['proj_avl']}</b>")

        """----------------------project_electrical_tab----------------------"""

        # ----------------Bagfilter/Baghouse ----------------
        el_tab = self.electrical_tab
        el_tab.bagfilter_type.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['type']}</b>")
        el_tab.bagfilter_order.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['order']}</b>")
        el_tab.plc_series.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['plc_series']}</b>")
        el_tab.plc_protocol.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['plc_protocol']}</b>")
        el_tab.olm.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['olm']}</b>")
        el_tab.touch_panel_model.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['touch_panel']}</b>")
        el_tab.ee.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['ee']}</b>")
        el_tab.me.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['me']}</b>")
        el_tab.cable_supply.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['cable_supply']}</b>")
        el_tab.cable_length.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['cable_dimension']}</b>m")

        el_tab.bagfilter_dpt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['delta_pressure_transmitter']['qty']}</b> QTY")
        el_tab.bagfilter_dpt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['delta_pressure_transmitter']['brand']}</b>")

        el_tab.bagfilter_dps_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['delta_pressure_switch']['qty']}</b> QTY")
        el_tab.bagfilter_dps_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['delta_pressure_switch']['brand']}</b>")

        el_tab.bagfilter_pt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['pressure_transmitter']['qty']}</b> QTY")
        el_tab.bagfilter_pt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['pressure_transmitter']['brand']}</b>")

        el_tab.bagfilter_ps_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['pressure_switch']['qty']}</b> QTY")
        el_tab.bagfilter_ps_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['pressure_switch']['brand']}</b>")

        el_tab.bagfilter_pg_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['pressure_gauge']['qty']}</b> QTY")
        el_tab.bagfilter_pg_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['pressure_gauge']['brand']}</b>")

        el_tab.bagfilter_inlet_tt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['inlet_temperature_transmitter']['qty']}</b> QTY")
        el_tab.bagfilter_inlet_tt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['inlet_temperature_transmitter']['brand']}</b>")

        el_tab.bagfilter_outlet_tt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['outlet_temperature_transmitter']['qty']}</b> QTY")
        el_tab.bagfilter_outlet_tt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['bagfilter']['instruments']['outlet_temperature_transmitter']['brand']}</b>")

        # ---------------- Fan - Damper ----------------
        el_tab.damper_checkbox.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['damper']['status']}</b>")
        el_tab.damper_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['damper']['motors']['damper']['power']}</b>KW")
        el_tab.damper_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['damper']['motors']['damper']['brand']}</b>")
        el_tab.damper_start_type.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['damper']['motors']['damper']['start_type']}</b>")

        el_tab.damper_zs_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['damper']['instruments']['proximity_switch']['qty']}</b> QTY")
        el_tab.damper_zs_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['damper']['instruments']['proximity_switch']['brand']}</b>")

        el_tab.fan_checkbox.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['status']}</b>")
        el_tab.fan_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['power']/1000}</b> KW")
        el_tab.fan_rpm.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['rpm']}</b> R.P.M.")
        el_tab.fan_start_type.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['start_type']}</b>")
        el_tab.fan_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['brand']}</b>")
        el_tab.fan_cooling_method.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['cooling_method']}</b>")
        el_tab.fan_ip.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['ip_rating']}</b>")
        el_tab.fan_efficiency_class.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['efficiency_class']}</b>")
        el_tab.fan_voltage_type.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['voltage_type']}</b>")
        el_tab.fan_painting_ral.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['painting_ral']}</b>")
        el_tab.fan_thermal_protection.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['thermal_protection']}</b>")
        el_tab.fan_de_nde.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['de_nde']}</b>")
        el_tab.fan_space_heater.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['motors']['fan']['space_heater']}</b>")

        el_tab.fan_bearing_tt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['bearing_temperature_transmitter']['qty']}</b> QTY")
        el_tab.fan_bearing_tt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['bearing_temperature_transmitter']['brand']}</b>")

        el_tab.fan_bearing_vt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['bearing_vibration_transmitter']['qty']}</b> QTY")
        el_tab.fan_bearing_vt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['bearing_vibration_transmitter']['brand']}</b>")

        el_tab.fan_pt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['pressure_transmitter']['qty']}</b> QTY")
        el_tab.fan_pt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['pressure_transmitter']['brand']}</b>")

        el_tab.fan_tt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['temperature_transmitter']['qty']}</b> QTY")
        el_tab.fan_tt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['temperature_transmitter']['brand']}</b>")

        el_tab.pt100_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['pt100']['qty']}</b> QTY")
        el_tab.pt100_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fan']['instruments']['pt100']['brand']}</b>")

        # ---------------- Transport ----------------
        el_tab.transport_checkbox.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['status']}</b>")

        el_tab.rotary_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['rotary']['qty']}</b> QTY")
        el_tab.rotary_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['rotary']['power']/1000}</b>KW")

        el_tab.screw1_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['screw1']['qty']}</b> QTY")
        el_tab.screw1_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['screw1']['power']/1000}</b>KW")

        el_tab.screw2_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['screw2']['qty']}</b> QTY")
        el_tab.screw2_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['screw2']['power']/1000}</b>KW")

        el_tab.slide_gate_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['slide_gate']['qty']}</b> QTY")
        el_tab.slide_gate_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['slide_gate']['power']/1000}</b>KW")

        el_tab.telescopic_chute_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['telescopic_chute']['qty']}</b> QTY")
        el_tab.telescopic_chute_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['motors']['telescopic_chute']['power']/1000}</b>KW")

        el_tab.transport_zs_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['instruments']['proximity_switch']['qty']}</b> QTY")
        el_tab.transport_zs_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['instruments']['proximity_switch']['brand']}</b>")

        el_tab.transport_spd_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['instruments']['speed_detector']['qty']}</b> QTY")
        el_tab.transport_spd_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['instruments']['speed_detector']['brand']}</b>")

        el_tab.transport_ls_bin_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['instruments']['level_switch']['qty']}</b> QTY")
        el_tab.transport_ls_bin_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['instruments']['level_switch']['brand']}</b>")

        el_tab.transport_lt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['instruments']['level_transmitter']['qty']}</b> QTY")
        el_tab.transport_lt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['transport']['instruments']['level_transmitter']['brand']}</b>")

        # ---------------- Vibration ----------------
        el_tab.vibration_checkbox.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['vibration']['status']}</b>")
        el_tab.vibration_motor_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['vibration']['motors']['vibration']['qty']}</b> QTY")
        el_tab.vibration_motor_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['vibration']['motors']['vibration']['power'] / 1000}</b>KW")

        # ---------------- Fresh Air ----------------
        el_tab.freshair_checkbox.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['status']}</b>")
        el_tab.freshair_motor_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['freshair_motor']['qty']}</b> QTY")
        el_tab.freshair_motor_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['freshair_motor']['power'] / 1000}</b>KW")
        el_tab.freshair_motor_start_type.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['freshair_motor']['start_type']}</b>")

        el_tab.freshair_flap_motor_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['fresh_air_flap']['qty']}</b> QTY")
        el_tab.freshair_flap_motor_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['fresh_air_flap']['power'] / 1000}</b>KW")
        el_tab.freshair_flap_motor_start_type.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['fresh_air_flap']['start_type']}</b>")

        el_tab.emergency_flap_motor_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['emergency_flap']['qty']}</b> QTY")
        el_tab.emergency_flap_motor_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['emergency_flap']['power'] / 1000}</b>KW")
        el_tab.emergency_flap_motor_start_type.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['motors']['emergency_flap']['start_type']}</b>")

        el_tab.freshair_tt_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['instruments']['temperature_transmitter']['qty']}</b> QTY")
        el_tab.freshair_tt_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['instruments']['temperature_transmitter']['brand']}</b>")

        el_tab.freshair_zs_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['instruments']['proximity_switch']['qty']}</b> QTY")
        el_tab.freshair_zs_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['fresh_air']['instruments']['proximity_switch']['brand']}</b>")

        # ---------------- Hopper Heater ----------------
        el_tab.hopper_heater_checkbox.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['hopper_heater']['status']}</b>")
        el_tab.hopper_heater_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['hopper_heater']['motors']['elements']['qty']}</b> QTY")
        el_tab.hopper_heater_kw.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['hopper_heater']['motors']['elements']['power'] / 1000}</b>KW")

        el_tab.hopper_heater_ptc_qty.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['hopper_heater']['instruments']['ptc']['qty']}</b> QTY")
        el_tab.hopper_heater_ptc_brand.setToolTip(f"Rev:<b>{rev_number}</b><br><b>{rev_specs['hopper_heater']['instruments']['ptc']['brand']}</b>")











