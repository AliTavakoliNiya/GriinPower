from controllers.tender_application.panel_controller import PanelController
from models.items.electrical_panel import get_electrical_panel_by_spec


class InstallationController(PanelController):
    """
    Specialized controller for bagfilter panel.
    """

    def __init__(self):
        super().__init__("installation")


    def build_panel(self):
        """
                Main controller for building installation from tender_application specifications.
        """
        self.choose_jb_lcb()
        return self.panel

    def choose_jb_lcb(self):

        total_motors_qty = 0
        for section in self.electrical_specs.values():
            motors = section.get("motors", {})
            for motor_name, motor_data in motors.items():
                try:
                    qty = motor_data.get("qty", 0)
                    total_motors_qty += qty
                except Exception:
                    pass

        success, jb = get_electrical_panel_by_spec(type="Junction Box", width=200, height=200, depth=120)
        if success:
            self.add_to_panel(
                type="Junction Box",
                brand=jb['brand'],
                order_number=jb["order_number"],
                specifications=f"200mm x 200mm x 120mm",
                quantity=total_motors_qty,
                price=jb['price'],
                last_price_update=f"{jb['supplier_name']}\n{jb['date']}",
                note=""
            )
        else:
            self.add_to_panel(
                type="Junction Box",
                brand="",
                order_number="",
                specifications=f"200mm x 200mm x 120mm",
                quantity=total_motors_qty,
                price=0,
                last_price_update="❌ Junction Box not found",
                note=""
            )

