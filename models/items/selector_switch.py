from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentSupplier
from utils.database import SessionLocal


class SelectorSwitch:
    def __init__(self, name, brand, model, component_supplier, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<SelectorSwitch(name={self.name})>"


def get_selector_switch():
    session = SessionLocal()
    try:
        selector_switch_type = session.query(ComponentType).filter_by(name='SelectorSwitch').first()

        component = (
            session.query(Component)
            .filter(
                Component.type_id == selector_switch_type.id,
            )
            .first()
        )

        if not component:
            return None, "❌ Selector Switch not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        selector_switch = SelectorSwitch(
            name=component.name,
            brand=component.brand,
            model=component.model,
            component_supplier=latest_supplier
        )

        return True, selector_switch

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Selector Switch:\n{str(e)}"

    finally:
        session.close()
