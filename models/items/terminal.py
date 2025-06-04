from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased, joinedload

from models import   ComponentAttribute, Component, ComponentSupplier
from utils.database import SessionLocal


class Terminal:
    def __init__(self, brand, model, current, component_supplier, order_number=""):
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.current = current
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<Terminal(current={self.current} A)>"


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

        if not component:
            return None, "❌ Button not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        terminal = Terminal(
                            brand=component.brand,
                            model=component.model,
                            current=attrs.get("current"),
                            component_supplier=latest_supplier)

        return True, terminal

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Terminal\n{str(e)}"

    finally:
        session.close()
