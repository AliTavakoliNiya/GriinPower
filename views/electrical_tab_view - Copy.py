from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSpinBox, QComboBox, QLineEdit, QCheckBox


class ElectricalTab(QWidget):
    def __init__(self, project_details):
        super().__init__()
        uic.loadUi("ui/electrical_tab.ui", self)

        self.project_details = project_details

        # Initialize all UI components with event handlers
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all UI components with their event handlers"""
        # ------------ Bagfilter ------------
        self._connect_handlers([
            (self.cable_length, "valueChanged", self._update_project_value,
             ["cable_dimension"]),
            (self.touch_panel_model, "currentTextChanged", self._update_project_value,
             ["bagfilter", "touch_panel"]),
        ])

        # ------------ Transport ------------
        self.transport_checkbox.stateChanged.connect(self.transport_checkbox_handler)
        self.screw2_add_btn.clicked.connect(self.show_screw2)
        self.screw2_minuse_btn.clicked.connect(self.hide_screw2)
        self.hide_screw2()
        self.transport_checkbox.setChecked(False)

        # Transport motors
        self._connect_motor_handlers("transport", [
            (self.rotary_qty, self.rotary_kw, "rotary", self._handle_rotary_screw_qty),
            (self.telescopic_chute_qty, self.telescopic_chute_kw, "telescopic_chute", None),
            (self.slide_gate_qty, self.slide_gate_kw, "slide_gate", self._handle_slide_gate_qty),
            (self.screw1_qty, self.screw1_kw, "screw1", self._handle_rotary_screw_qty),
            (self.screw2_qty, self.screw2_kw, "screw2", self._handle_rotary_screw_qty),
        ])

        # Transport instruments
        self._connect_instrument_handlers("transport", [
            (self.transport_spd_qty, self.transport_spd_brand, "speed_detector"),
            (self.transport_zs_qty, self.transport_zs_brand, "proximity_switch"),
            (self.transport_ls_bin_qty, self.transport_ls_bin_brand, "level_switch"),
            (self.transport_lt_qty, self.transport_lt_brand, "level_transmitter"),
        ])

        # ------------ Vibration ------------
        self.vibration_checkbox.stateChanged.connect(self.vibration_checkbox_handler)
        self.vibration_checkbox.setChecked(False)

        # Vibration motors
        self._connect_motor_handlers("vibration", [
            (self.vibration_motor_qty, self.vibration_motor_kw, "vibration", None),
        ])

        # ------------ Fresh Air ------------
        self.freshair_checkbox.stateChanged.connect(self.freshair_checkbox_handler)
        self.freshair_checkbox.setChecked(False)

        # Fresh air motors
        self._connect_handlers([
            (self.freshair_motor_qty, "valueChanged", self.freshair_motor_qty_handler),
            (self.freshair_motor_kw, "currentIndexChanged", self._handle_combobox_float,
             ["fresh_air", "motors", "freshair_motor", "power"]),
            (self.freshair_motor_start_type, "currentIndexChanged", self._update_project_value,
             ["fresh_air", "motors", "freshair_motor", "start_type"]),

            (self.freshair_flap_motor_qty, "valueChanged", self._update_project_value,
             ["fresh_air", "motors", "fresh_air_flap", "qty"]),
            (self.freshair_flap_motor_kw, "currentIndexChanged", self._handle_combobox_float,
             ["fresh_air", "motors", "fresh_air_flap", "power"]),
            (self.freshair_flap_motor_start_type, "currentIndexChanged", self._update_project_value,
             ["fresh_air", "motors", "fresh_air_flap", "start_type"]),

            (self.emergency_flap_motor_kw, "currentIndexChanged", self._handle_combobox_float,
             ["fresh_air", "motors", "emergency_flap", "power"]),
            (self.emergency_flap_start_type, "currentIndexChanged", self._update_project_value,
             ["fresh_air", "motors", "emergency_flap", "start_type"]),
        ])

        # Fresh air instruments
        self._connect_instrument_handlers("fresh_air", [
            (self.freshair_tt_qty, self.freshair_tt_brand, "temperature_transmitter"),
            (self.freshair_zs_qty, self.freshair_zs_brand, "proximity_switch"),
        ])

        # ------------ Heater Hopper ------------
        self.hopper_heater_checkbox.stateChanged.connect(self.hopper_heater_checkbox_handler)
        self.hopper_heater_checkbox.setChecked(False)

        self._connect_handlers([
            (self.hopper_heater_qty, "valueChanged", self.hopper_heater_qty_handler),
            (self.hopper_heater_kw, "currentIndexChanged", self._handle_combobox_float,
             ["hopper_heater", "motors", "elements", "power"]),
            (self.hopper_heater_ptc_brand, "currentIndexChanged", self._update_project_value,
             ["hopper_heater", "instruments", "ptc", "brand"]),
        ])

        # ------------ Damper ------------
        self.damper_checkbox.stateChanged.connect(self.damper_checkbox_handler)
        self.damper_checkbox.setChecked(False)

        self._connect_handlers([
            (self.damper_kw, "currentIndexChanged", self._handle_combobox_float,
             ["damper", "motors", "damper", "power"]),
            (self.damper_brand, "currentIndexChanged", self._update_project_value,
             ["damper", "motors", "damper", "brand"]),
            (self.damper_start_type, "currentIndexChanged", self._update_project_value,
             ["damper", "motors", "damper", "start_type"]),
        ])

        self._connect_instrument_handlers("damper", [
            (self.damper_zs_qty, self.damper_zs_brand, "proximity_switch"),
        ])

        # ------------ Fan ------------
        self.fan_checkbox.stateChanged.connect(self.fan_checkbox_handler)
        self.fan_checkbox.setChecked(False)

        # Fan motor properties
        self._connect_handlers([
            (self.fan_kw, "currentIndexChanged", self._handle_combobox_float,
             ["fan", "motors", "fan", "power"]),
            (self.fan_rpm, "textChanged", self._update_project_value,
             ["fan", "motors", "fan", "rpm"]),
            (self.fan_start_type, "currentIndexChanged", self._update_project_value,
             ["fan", "motors", "fan", "start_type"]),
            (self.fan_brand, "currentIndexChanged", self._update_project_value,
             ["fan", "motors", "fan", "brand"]),
            (self.fan_cooling_method, "currentIndexChanged", self._update_project_value,
             ["fan", "motors", "fan", "cooling_method"]),
            (self.fan_ip, "currentIndexChanged", self._update_project_value,
             ["fan", "motors", "fan", "ip_rating"]),
            (self.fan_efficiency_class, "currentIndexChanged", self._update_project_value,
             ["fan", "motors", "fan", "efficiency_class"]),
            (self.fan_voltage_type, "currentIndexChanged", self._update_project_value,
             ["fan", "motors", "fan", "voltage_type"]),
            (self.fan_painting_ral, "currentIndexChanged", self._update_project_value,
             ["fan", "motors", "fan", "painting_ral"]),
            (self.fan_thermal_protection, "currentIndexChanged", self._update_project_value,
             ["fan", "motors", "fan", "thermal_protection"]),
            (self.fan_space_heater, "stateChanged", self._handle_checkbox,
             ["fan", "motors", "fan", "space_heater"]),
        ])

        # Fan instruments
        self._connect_instrument_handlers("fan", [
            (self.fan_bearing_tt_qty, self.fan_bearing_tt_brand, "bearing_temperature_transmitter"),
            (self.fan_bearing_vt_qty, self.fan_bearing_vt_brand, "bearing_vibration_transmitter"),
            (self.fan_pt_qty, self.fan_pt_brand, "pressure_transmitter"),
            (self.fan_tt_qty, self.fan_tt_brand, "temperature_transmitter"),
        ])

    def _connect_handlers(self, connections):
        """Connect multiple widget signals to handlers

        Args:
            connections: List of tuples (widget, signal_name, handler, optional_args)
        """
        for conn in connections:
            widget = conn[0]
            signal_name = conn[1]
            handler = conn[2]
            args = conn[3] if len(conn) > 3 else None

            signal = getattr(widget, signal_name)
            if args:
                signal.connect(lambda *_, h=handler, a=args: h(a))
            else:
                signal.connect(handler)

    def _connect_motor_handlers(self, section, motor_configs):
        """Connect motor quantity and power handlers

        Args:
            section: Project section name (e.g., "transport", "vibration")
            motor_configs: List of tuples (qty_widget, kw_widget, motor_name, custom_qty_handler)
        """
        for config in motor_configs:
            qty_widget, kw_widget, motor_name, custom_qty_handler = config

            # Connect quantity handler
            if custom_qty_handler:
                qty_widget.valueChanged.connect(
                    lambda val, w=qty_widget, h=custom_qty_handler: h(w))
            else:
                qty_widget.valueChanged.connect(
                    lambda val, s=section, m=motor_name: self._update_project_value(
                        [s, "motors", m, "qty"]))

            # Connect power handler
            kw_widget.currentIndexChanged.connect(
                lambda val, s=section, m=motor_name: self._handle_combobox_float(
                    [s, "motors", m, "power"]))

    def _connect_instrument_handlers(self, section, instrument_configs):
        """Connect instrument quantity and brand handlers

        Args:
            section: Project section name (e.g., "transport", "vibration")
            instrument_configs: List of tuples (qty_widget, brand_widget, instrument_name)
        """
        for config in instrument_configs:
            qty_widget, brand_widget, instrument_name = config

            # Connect quantity handler
            qty_widget.valueChanged.connect(
                lambda val, s=section, i=instrument_name: self._update_project_value(
                    [s, "instruments", i, "qty"]))

            # Connect brand handler
            brand_widget.currentIndexChanged.connect(
                lambda val, s=section, i=instrument_name: self._update_project_value(
                    [s, "instruments", i, "brand"]))

    def _update_project_value(self, path_list, value=None):
        """Update project details dictionary value at the specified path

        Args:
            path_list: List of keys to navigate the nested dictionary
            value: Value to set (if None, gets from sender widget)
        """
        if value is None:
            # Get value from sender
            sender = self.sender()
            if isinstance(sender, QComboBox):
                value = sender.currentText()
            elif isinstance(sender, QSpinBox):
                value = sender.value()
            elif isinstance(sender, QLineEdit):
                value = sender.text()
            elif isinstance(sender, QCheckBox):
                value = sender.isChecked()
            else:
                return

        # Navigate to the right location in the dictionary
        target = self.project_details
        for key in path_list[:-1]:
            target = target[key]

        # Set the value
        target[path_list[-1]] = value

    def _handle_combobox_float(self, path_list):
        """Handle conversion of combobox text to float value

        Args:
            path_list: List of keys to navigate the nested dictionary
        """
        sender = self.sender()
        text = sender.currentText()
        try:
            value = float(text)
        except ValueError:
            value = 0.0

        self._update_project_value(path_list, value)

    def _handle_checkbox(self, path_list):
        """Handle checkbox state change

        Args:
            path_list: List of keys to navigate the nested dictionary
        """
        sender = self.sender()
        state = sender.isChecked()
        self._update_project_value(path_list, state)

    def reset_qtys(self, d):
        """Reset all quantity values in a dictionary to zero

        Args:
            d: Dictionary to process
        """
        for key, value in d.items():
            if isinstance(value, dict):
                self.reset_qtys(value)
            elif key == "qty":
                d[key] = 0

    def _reset_section_widgets(self, parent_widget, enabled=True):
        """Reset and enable/disable all widgets in a section

        Args:
            parent_widget: Parent widget containing child widgets to reset
            enabled: Whether to enable or disable the widgets
        """
        for child in parent_widget.findChildren(QWidget):
            # Skip the checkbox itself
            if isinstance(child, QCheckBox) and child.parent() == parent_widget:
                continue

            # Reset values if disabling
            if not enabled:
                if isinstance(child, QSpinBox):
                    child.setValue(0)
                elif isinstance(child, QComboBox):
                    child.setCurrentIndex(0)
                elif isinstance(child, QLineEdit):
                    child.setText("")
                elif isinstance(child, QCheckBox):
                    child.setChecked(False)

            # Set enabled state
            child.setEnabled(enabled)

    # ------ Special Case Handlers ------

    def _handle_rotary_screw_qty(self, widget):
        """Special handler for rotary and screw qty fields that affect speed detector"""
        motor_type = None
        if widget == self.rotary_qty:
            motor_type = "rotary"
        elif widget == self.screw1_qty:
            motor_type = "screw1"
        elif widget == self.screw2_qty:
            motor_type = "screw2"

        if not motor_type:
            return

        # Update the project details
        self.project_details["transport"]["motors"][motor_type]["qty"] = widget.value()

        # Calculate total rotary/screw motors
        total_motors = (self.rotary_qty.value() +
                        self.screw1_qty.value() +
                        self.screw2_qty.value())

        # Update speed detector quantity based on total motors
        if total_motors == 0:
            self.transport_spd_qty.setValue(0)
            self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = 0
        elif self.transport_spd_qty.value() < total_motors:
            self.transport_spd_qty.setValue(total_motors)
            self.project_details["transport"]["instruments"]["speed_detector"]["qty"] = total_motors

    def _handle_slide_gate_qty(self, widget):
        """Special handler for slide gate qty that affects proximity switch"""
        # Update the project details
        self.project_details["transport"]["motors"]["slide_gate"]["qty"] = widget.value()

        # Update proximity switch quantity based on slide gate qty
        if widget.value() != 0:
            required_switches = widget.value() * 2
            if self.transport_zs_qty.value() < required_switches:
                self.transport_zs_qty.setValue(required_switches)
                self.project_details["transport"]["instruments"]["proximity_switch"]["qty"] = required_switches
        else:
            self.transport_zs_qty.setValue(0)
            self.project_details["transport"]["instruments"]["proximity_switch"]["qty"] = 0

    def freshair_motor_qty_handler(self):
        """Special handler for fresh air motor qty that affects proximity switch"""
        # Update the project details
        self.project_details["fresh_air"]["motors"]["freshair_motor"]["qty"] = self.freshair_motor_qty.value()

        # Update proximity switch quantity based on motor qty
        if self.freshair_motor_qty.value() != 0:
            required_switches = self.freshair_motor_qty.value() * 2
            if self.freshair_zs_qty.value() < required_switches:
                self.freshair_zs_qty.setValue(required_switches)
                self.project_details["fresh_air"]["instruments"]["proximity_switch"]["qty"] = required_switches

    def hopper_heater_qty_handler(self):
        """Special handler for hopper heater qty that affects PTC qty"""
        # Update the project details
        qty = self.hopper_heater_qty.value()
        self.project_details["hopper_heater"]["motors"]["elements"]["qty"] = qty

        # Update PTC qty based on heater qty
        ptc_qty = qty * 2
        self.project_details["hopper_heater"]["instruments"]["ptc"]["qty"] = ptc_qty
        self.hopper_heater_ptc_qty.setText(f"Qty: {ptc_qty}")

    # ------ Section Handlers ------

    def transport_checkbox_handler(self, state):
        """Handle transport section enabling/disabling"""
        enabled = state == Qt.Checked
        self.project_details["transport"]["status"] = enabled

        if not enabled:
            self.reset_qtys(self.project_details["transport"])

        self._reset_section_widgets(self.transport_gbox, enabled)
        self.transport_checkbox.setEnabled(True)

    def vibration_checkbox_handler(self, state):
        """Handle vibration section enabling/disabling"""
        enabled = state == Qt.Checked
        self.project_details["vibration"]["status"] = enabled

        if not enabled:
            self.reset_qtys(self.project_details["vibration"])

        self._reset_section_widgets(self.vibration_gbox, enabled)
        self.vibration_checkbox.setEnabled(True)

    def freshair_checkbox_handler(self, state):
        """Handle fresh air section enabling/disabling"""
        enabled = state == Qt.Checked
        self.project_details["fresh_air"]["status"] = enabled

        if not enabled:
            self.reset_qtys(self.project_details["fresh_air"])

        self._reset_section_widgets(self.freshair_gbox, enabled)
        self.freshair_checkbox.setEnabled(True)

    def hopper_heater_checkbox_handler(self, state):
        """Handle hopper heater section enabling/disabling"""
        enabled = state == Qt.Checked
        self.project_details["hopper_heater"]["status"] = enabled

        if not enabled:
            self.reset_qtys(self.project_details["hopper_heater"])

        self._reset_section_widgets(self.hopper_heater_gbox, enabled)
        self.hopper_heater_checkbox.setEnabled(True)
        self.hopper_heater_ptc_qty.setEnabled(False)  # Always keep disabled

    def damper_checkbox_handler(self, state):
        """Handle damper section enabling/disabling"""
        enabled = state == Qt.Checked
        self.project_details["damper"]["status"] = enabled
        self.project_details["damper"]["motors"]["damper"]["qty"] = 1 if enabled else 0

        if not enabled:
            self.reset_qtys(self.project_details["damper"])

        # Access direct UI elements for damper section since there's no damper_gbox
        damper_ui_elements = [
            self.damper_kw,
            self.damper_brand,
            self.damper_start_type,
            self.damper_zs_qty,
            self.damper_zs_brand
        ]

        for element in damper_ui_elements:
            if not enabled:
                if isinstance(element, QSpinBox):
                    element.setValue(0)
                elif isinstance(element, QComboBox):
                    element.setCurrentIndex(0)
                elif isinstance(element, QLineEdit):
                    element.setText("")
                elif isinstance(element, QCheckBox):
                    element.setChecked(False)

            element.setEnabled(enabled)

        self.damper_checkbox.setEnabled(True)

    def fan_checkbox_handler(self, state):
        """Handle fan section enabling/disabling"""
        enabled = state == Qt.Checked
        self.project_details["fan"]["status"] = enabled

        # Set fan motor quantity based on checkbox state
        self.project_details["fan"]["motors"]["fan"]["qty"] = 1 if enabled else 0

        if not enabled:
            self.reset_qtys(self.project_details["fan"])

        # Access direct UI elements for fan section since there's no fan_gbox
        fan_ui_elements = [
            self.fan_kw,
            self.fan_rpm,
            self.fan_start_type,
            self.fan_brand,
            self.fan_cooling_method,
            self.fan_ip,
            self.fan_efficiency_class,
            self.fan_voltage_type,
            self.fan_painting_ral,
            self.fan_thermal_protection,
            self.fan_space_heater,
            self.fan_bearing_tt_qty,
            self.fan_bearing_tt_brand,
            self.fan_bearing_vt_qty,
            self.fan_bearing_vt_brand,
            self.fan_pt_qty,
            self.fan_pt_brand,
            self.fan_tt_qty,
            self.fan_tt_brand
        ]

        for element in fan_ui_elements:
            if not enabled:
                if isinstance(element, QSpinBox):
                    element.setValue(0)
                elif isinstance(element, QComboBox):
                    element.setCurrentIndex(0)
                elif isinstance(element, QLineEdit):
                    element.setText("")
                elif isinstance(element, QCheckBox):
                    element.setChecked(False)

            element.setEnabled(enabled)

        self.fan_checkbox.setEnabled(True)

    # ------ Screw UI Controls ------

    def show_screw2(self):
        """Show screw2 UI components"""
        self.screw2_minuse_btn.show()
        self.screw2_label.show()
        self.screw2_qty.show()
        self.screw2_qty.setValue(0)
        self.screw2_kw.show()
        self.screw2_kw.setCurrentIndex(0)

    def hide_screw2(self):
        """Hide screw2 UI components"""
        self.screw2_minuse_btn.hide()
        self.screw2_label.hide()
        self.screw2_qty.hide()
        self.screw2_qty.setValue(0)
        self.screw2_kw.hide()
        self.screw2_kw.setCurrentIndex(0)
