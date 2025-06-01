from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal


class MCCB:

    def __init__(self, name, brand, model, rated_current, breaking_capacity_ka, component_supplier, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.rated_current = rated_current
        self.breaking_capacity_ka = breaking_capacity_ka
        self.order_number = order_number,
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<MCCB(name={self.name}, rated_current={self.rated_current})>"


def get_mccb_by_current(min_rated_current):
    session = SessionLocal()

    try:
        mccb_type = session.query(ComponentType).filter_by(name='MCCB').first()

        rated_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(rated_attr, Component.attributes)
            .filter(
                Component.type_id == mccb_type.id,
                rated_attr.key == 'rated_current',
                cast(rated_attr.value, Float) >= min_rated_current
            )
        )

        component = query.order_by(cast(rated_attr.value, Float).asc()).first()

        if not component:
            return None, "❌ MCCB component not found for the specified current."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        mccb = MCCB(
            name=component.name,
            brand=component.brand,
            model=component.model,
            rated_current=attrs.get("rated_current"),
            breaking_capacity_ka=attrs.get("breaking_capacity_ka"),
            component_supplier=latest_supplier
        )

        return True, mccb, f"{mccb}"

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_mccb_by_current:\n{str(e)}"

    finally:
        session.close()
