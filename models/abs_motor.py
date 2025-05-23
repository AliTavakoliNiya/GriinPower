class Motor:
    def __init__(
            self,
            power,
            current=0,
            usage=None,
            brand=None,
            lcb_qty=1,
            terminal_4_qty=4,
            terminal_6_qty=10,
            relay_1no_1nc_qty=4,
            relay_2no_2nc_qty=1,
            contactor_qty=1,
            mpcb_qty=1,
            mccb_qty=0,
            bimetal_qty=0,
            contactor_aux_contact_qty=1,
            mpcb_mccb_aux_contact_qty=1,
            button_qty=3,
            selector_switch_qty=1,
            signal_lamp_24v_qty=2,
            signal_cable_7x1p5_l_cofactor=1,
            power_cable_cofactor=1,
            duct_cover_qty=0.5,
            miniatory_rail_qty=0.3,
            junction_box_for_speed_qty=1,
            panel_wire_qty=5,
            plc_di=5,
            plc_do=1,
            plc_ai=0,
            plc_ao=0
    ):
        self.power = power
        self.current = current
        self.usage = usage
        self.brand = brand
        self.lcb_qty = lcb_qty
        self.contactor_qty = contactor_qty
        self.mpcb_qty = mpcb_qty
        self.mccb_qty = mccb_qty
        self.bimetal_qty = bimetal_qty
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
            f"Power={self.power}, "
            f"Current={self.current}, "
            f"Usage={self.usage}"
        )
