from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentSupplier
from utils.database import SessionLocal


class MiniatoryRail:
    def __init__(self, brand, model, component_supplier, order_number=""):
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<MiniatoryRail>"


def get_miniatory_rail():
    session = SessionLocal()
    try:
        rail_type = session.query(ComponentType).filter_by(name='MiniatoryRail').first()

        component = (
            session.query(Component)
            .filter(
                Component.type_id == rail_type.id,
            )
            .first()
        )

        if not component:
            return None, "❌ Miniatory Rail not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        rail = MiniatoryRail(
            brand=component.brand,
            model=component.model,
            component_supplier=latest_supplier
        )

        return True, rail

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Miniatory Rail:\n{str(e)}"

    finally:
        session.close()
