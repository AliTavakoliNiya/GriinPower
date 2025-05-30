from sqlalchemy import cast, Float, desc, and_, func
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal



class MPCB:

    def __init__(self, name, brand, model, min_current, max_current, breaking_capacity_ka, trip_class, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.min_current = min_current
        self.max_current = max_current
        self.breaking_capacity_ka = breaking_capacity_ka
        self.trip_class = trip_class
        self.component_vendor = component_vendor


    def __repr__(self):
        return f"<MPCB(name={self.name}, current={self.min_current}A - {self.max_current}A)"

def get_mpcb_by_current(current):
    session = SessionLocal()

    try:
        mpcb_type = session.query(ComponentType).filter_by(name='MPCB').first()
        if not mpcb_type:
            return False, "❌ MPCB type not found."

        min_attr = aliased(ComponentAttribute)
        max_attr = aliased(ComponentAttribute)

        component = (
            session.query(Component)
            .join(min_attr, Component.attributes)
            .join(max_attr, Component.attributes)
            .filter(
                Component.type_id == mpcb_type.id,
                min_attr.key == 'min_current',
                max_attr.key == 'max_current',
                cast(min_attr.value, Float) <= current,
                cast(max_attr.value, Float) >= current
            )
            .order_by(cast(min_attr.value, Float).asc())
            .first()
        )

        if not component:
            return False, "❌ MPCB component not found for this current."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        mpcb = MPCB(
            name=component.name,
            brand=component.brand,
            model=component.model,
            min_current=attrs.get("min_current"),
            max_current=attrs.get("max_current"),
            breaking_capacity_ka=attrs.get("breaking_capacity_ka"),
            trip_class=attrs.get("trip_class"),  # اصلاح نام کلید
            component_vendor=latest_vendor
        )

        return True, mpcb
    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_mpcb_by_current:\n{str(e)}"
    finally:
        session.close()
