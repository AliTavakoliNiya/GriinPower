from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentSupplier
from utils.database import SessionLocal


class Button:
    def __init__(self, name, brand, model, component_supplier, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.component_supplier = component_supplier

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
            return None, "❌ Button not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        button = Button(
            name=component.name,
            brand=component.brand,
            model=component.model,
            component_supplier=latest_supplier
        )

        return True, button

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Button:\n{str(e)}"

    finally:
        session.close()
