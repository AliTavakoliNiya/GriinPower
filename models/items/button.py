from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentVendor
from utils.database import SessionLocal


class Button:
    def __init__(self, name, brand, model, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<Button(name={self.name})>"


def get_button():
    session = SessionLocal()
    try:
        button_type_obj = session.query(ComponentType).filter_by(name='Button').first()

        component = (
            session.query(Component)
            .filter(
                Component.type_id == button_type_obj.id,
            )
            .first()
        )

        if not component:
            return False, "❌ Button not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        button = Button(
            name=component.name,
            brand=component.brand,
            model=component.model,
            component_vendor=latest_vendor
        )

        return True, button

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Button:\n{str(e)}"

    finally:
        session.close()
