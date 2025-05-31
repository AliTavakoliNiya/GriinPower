from sqlalchemy import desc, and_
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class Instrument:

    def __init__(self, name, brand, model, instrument_type, hart_support, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number,
        self.instrument_type = instrument_type
        self.hart_support
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<Instrument(name={self.name}, type={self.instrument_type}, hart support={self.hart_support})>"


def get_instrument_by_type(instrument_type):
    session = SessionLocal()

    try:
        instr_type = session.query(ComponentType).filter_by(name='Instrument').first()
        query = session.query(Component).filter(Component.type_id == instr_type.id)

        query = query.filter(
            Component.attributes.any(
                and_(
                    ComponentAttribute.key == 'instrument_type',
                    ComponentAttribute.value == instrument_type
                )
            )
        )
        component = query.first()

        if not component:
            return None, "❌ Instrument not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        instrument = Instrument(
            name=component.name,
            brand=component.brand,
            model=component.model,
            instrument_type=attrs.get("instrument_type"),
            hart_support=attrs.get("hart_support"),
            component_vendor=latest_vendor
        )

        return True, instrument

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_instrument_by_type:\n{str(e)}"

    finally:
        session.close()
