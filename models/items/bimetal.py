from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class Bimetal:

    def __init__(self, name, brand, model, min_current, max_current, trip_time, class_type, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.min_current = min_current
        self.max_current = max_current
        self.trip_time = trip_time
        self.class_type = class_type
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<Bimetal(name={self.name}, current= {self.min_current}A - {self.max_current}A)>"


def get_bimetal_by_current(min_rated_current):
    session = SessionLocal()

    try:
        bimetal_type = session.query(ComponentType).filter_by(name='Bimetal').first()
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
            return None, "❌ Bimetal not found."

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
            min_current=attrs.get("min_current"),
            max_current=attrs.get("max_current"),
            trip_time=attrs.get("trip_time"),
            class_type=attrs.get("class_type"),
            component_vendor=latest_vendor
        )

        return True, bimetal

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_bimetal_by_current:\n{str(e)}"

    finally:
        session.close()

