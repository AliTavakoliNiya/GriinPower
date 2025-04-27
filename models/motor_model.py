class Motor:
    def __init__(self, power_kw, usage="", brand=""):

        self.usage = usage
        self.power_kw = power_kw
        self.brand = brand
        self.lcb_qty = 1
        self.terminal_4_qty = 4
        self.terminal_6_qty = 10
        self.relay_1no_1nc_qty = 4
        self.relay_2no_2nc_qty = 1
        self.button_qty = 3
        self.selector_switch_qty = 1
        self.signal_lamp_24v_qty = 2
        self.signal_cable_7x1p5_l_cofactor = 1
        self.power_cable_cofactor = 1
        self.duct_cover_qty = 0.5
        self.miniatory_rail_qty = 0.3
        self.panel_wire_qty = 5

    def __repr__(self):
        return (
            f"Motor Power(KW)={self.power_kw}, "
            f"Usage={self.usage}', "
            f"Brand={self.brand}"
        )






