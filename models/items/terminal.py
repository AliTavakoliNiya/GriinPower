from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased, joinedload

from models import ComponentType, ComponentAttribute, Component, ComponentVendor
from utils.database import SessionLocal


class Terminal:
    def __init__(self, name, brand, model, current, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.current = current
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<Terminal(name={self.name} current={self.current} A)>"


def get_terminal_by_current(rated_current):
    session = SessionLocal()
    try:
        terminal_type = session.query(ComponentType).filter_by(name='Terminal').first()
        rated_attr = aliased(ComponentAttribute)

        component = (
            session.query(Component)
            .join(rated_attr, Component.attributes)
            .filter(
                Component.type_id == terminal_type.id,
                rated_attr.key == 'current',
                cast(rated_attr.value, Float) > rated_current
            )
            .order_by(cast(rated_attr.value, Float).asc())
            .first()
        )

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        terminal = Terminal(name=component.name,
                            brand=component.brand,
                            model=component.model,
                            current=attrs.get("current"),
                            component_vendor=latest_vendor)

        return True, terminal

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Terminal\n{str(e)}"

    finally:
        session.close()
