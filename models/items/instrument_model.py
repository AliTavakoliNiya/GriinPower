from sqlalchemy import desc, and_
from sqlalchemy.orm import joinedload

from models.items import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class Instrument:

    def __init__(self, name, brand, model, instrument_type, measuring_range,
                 signal_output, accuracy, component_vendor):
        self.name = name
        self.brand = brand
        self.model = model
        self.instrument_type = instrument_type
        self.measuring_range = measuring_range
        self.signal_output = signal_output
        self.accuracy = accuracy
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<Instrument(name={self.name}, type={self.instrument_type}, range={self.measuring_range})>"


def get_instrument_by_type(instrument_type=None, signal_output=None):
    session = SessionLocal()

    try:
        instr_type = session.query(ComponentType).filter_by(name='Instrument').first()
        if not instr_type:
            return None, "ComponentType 'Instrument' not found."

        query = session.query(Component).filter(Component.type_id == instr_type.id)

        if instrument_type:
            query = query.filter(
                Component.attributes.any(
                    and_(
                        ComponentAttribute.key == 'instrument_type',
                        ComponentAttribute.value == instrument_type
                    )
                )
            )

        if signal_output:
            query = query.filter(
                Component.attributes.any(
                    and_(
                        ComponentAttribute.key == 'signal_output',
                        ComponentAttribute.value == signal_output
                    )
                )
            )

        component = query.first()

        if not component:
            return None, "No Instrument found with the specified filters."

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
            measuring_range=attrs.get("measuring_range"),
            signal_output=attrs.get("signal_output"),
            accuracy=attrs.get("accuracy"),
            component_vendor=latest_vendor
        )

        return instrument, f"{instrument}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_instrument_by_type:\n{str(e)}"

    finally:
        session.close()
