from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased, joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal

class Relay:
    def __init__(self, name, brand, model, no_nc_contacts, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.no_nc_contacts = no_nc_contacts
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<Relay(name={self.name}, NO/NC={self.no_nc_contacts})>"

def get_relay_by_contacts(contacts=None):
    session = SessionLocal()
    try:
        relay_type = session.query(ComponentType).filter_by(name='Relay').first()

        contacts_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(contacts_attr, Component.attributes)
            .filter(Component.type_id == relay_type.id)
            .filter(contacts_attr.key == "no_nc_contacts")
        )

        if contacts is not None:
            query = query.filter(cast(contacts_attr.value, Float) >= contacts)

        component = query.order_by(
            cast(contacts_attr.value, Float).asc()
        ).first()

        if not component:
            return False, "❌ Relay not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        relay = Relay(
            name=component.name,
            brand=component.brand,
            model=component.model,
            no_nc_contacts=attrs.get("no_nc_contacts"),
            component_vendor=latest_vendor
        )

        return True, relay

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Relay:\n{str(e)}"

    finally:
        session.close()
