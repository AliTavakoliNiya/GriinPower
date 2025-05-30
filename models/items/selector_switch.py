from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentVendor
from utils.database import SessionLocal


class SelectorSwitch:
    def __init__(self, name, brand, model, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.component_vendor = component_vendor

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
            return False, "❌ Selector Switch not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        selector_switch = SelectorSwitch(
            name=component.name,
            brand=component.brand,
            model=component.model,
            component_vendor=latest_vendor
        )

        return True, selector_switch

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Selector Switch:\n{str(e)}"

    finally:
        session.close()
