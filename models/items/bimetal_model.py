from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models.items import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class Bimetal:

    def __init__(self, name, brand, model, rated_current, operating_range, reset_type, component_vendor):
        self.name = name
        self.brand = brand
        self.model = model
        self.rated_current = rated_current
        self.operating_range = operating_range
        self.reset_type = reset_type
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<Bimetal(name={self.name}, current={self.rated_current}A, range={self.operating_range})>"


def get_bimetal_by_current(min_rated_current):
    session = SessionLocal()

    try:
        bimetal_type = session.query(ComponentType).filter_by(name='Bimetal').first()
        if not bimetal_type:
            return None, "ComponentType 'Bimetal' not found."

        rated_attr = aliased(ComponentAttribute)

        component = (
            session.query(Component)
            .join(rated_attr, Component.attributes)
            .filter(
                Component.type_id == bimetal_type.id,
                rated_attr.key == 'rated_current',
                cast(rated_attr.value, Float) >= min_rated_current
            )
            .order_by(cast(rated_attr.value, Float).asc())
            .first()
        )

        if not component:
            return None, "No Bimetal found with sufficient rated current."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        bimetal = Bimetal(
            name=component.name,
            brand=component.brand,
            model=component.model,
            rated_current=attrs.get("rated_current"),
            operating_range=attrs.get("operating_range"),
            reset_type=attrs.get("reset_type"),
            component_vendor=latest_vendor
        )

        return bimetal, f"{bimetal}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_bimetal_by_current:\n{str(e)}"

    finally:
        session.close()

