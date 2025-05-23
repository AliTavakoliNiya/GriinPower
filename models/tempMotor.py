class Motor:
    def __init__(

    ):
        self.power = power_kw
        self.usage = usage
        self.brand = brand
        self.lcb_qty = lcb_qty
        self.contactor_qty = contactor_qty
        self.mpcb_qty = mpcb_qty
        self.mccb_qty = mccb_qty
        self.contactor_aux_contact_qty = contactor_aux_contact_qty
        self.mpcb_mccb_aux_contact_qty = mpcb_mccb_aux_contact_qty
        self.terminal_4_qty = terminal_4_qty
        self.terminal_6_qty = terminal_6_qty
        self.relay_1no_1nc_qty = relay_1no_1nc_qty
        self.relay_2no_2nc_qty = relay_2no_2nc_qty
        self.button_qty = button_qty
        self.selector_switch_qty = selector_switch_qty
        self.signal_lamp_24v_qty = signal_lamp_24v_qty
        self.signal_cable_7x1p5_l_cofactor = signal_cable_7x1p5_l_cofactor
        self.power_cable_cofactor = power_cable_cofactor
        self.duct_cover_qty = duct_cover_qty
        self.miniatory_rail_qty = miniatory_rail_qty
        self.panel_wire_qty = panel_wire_qty
        self.junction_box_for_speed_qty = junction_box_for_speed_qty
        self.plc_di = plc_di
        self.plc_do = plc_do
        self.plc_ai = plc_ai
        self.plc_ao = plc_ao
        self.plc_front_input_connector = self.plc_di + self.plc_ai
        self.plc_front_output_connector = self.plc_do + self.plc_ao

    def __repr__(self):
        return (
            f"Motor Power(KW)={self.power_kw}, "
            f"Usage={self.usage}', "
            f"Brand={self.brand}"
        )
