from sqlalchemy import cast, Integer, desc
from sqlalchemy.orm import joinedload
from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal

class FrontConnector:
    def __init__(self, name, brand, model, pin_count, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.pin_count = pin_count
        self.component_vendor = component_vendor
        self.order_number = order_number

    def __repr__(self):
        return f"<FrontConnector(name={self.name}, pins={self.pin_count})>"

def get_front_connector(pin_count):
    session = SessionLocal()
    try:
        type_obj = session.query(ComponentType).filter_by(name='FrontConnector').first()
        if not type_obj:
            return False, "❌ ComponentType 'FrontConnector' not found."

        attr_alias = ComponentAttribute.__table__.alias('attr')
        component = (
            session.query(Component)
            .join(Component.attributes)
            .filter(Component.type_id == type_obj.id)
            .filter(ComponentAttribute.key == 'pin_count')
            .filter(cast(ComponentAttribute.value, Integer) >= pin_count)
            .order_by(cast(ComponentAttribute.value, Integer).asc())
            .first()
        )

        if not component:
            return False, f"❌ No front connector found for pin count ≥ {pin_count}"

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter_by(component_id=component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        connector = FrontConnector(
            name=component.name,
            brand=component.brand,
            model=component.model,
            pin_count=attrs.get("pin_count"),
            component_vendor=latest_vendor
        )

        return True, connector

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_front_connector: {str(e)}"

    finally:
        session.close()
