from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased, joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class SignalLamp:
    def __init__(self, name, brand, model, voltage, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.voltage = voltage
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<SignalLamp24V(name={self.name} voltage={self.voltage}V)>"


def get_signal_lamp(voltage=None):
    session = SessionLocal()
    try:
        lamp_type = session.query(ComponentType).filter_by(name='SignalLamp').first()

        voltage_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(voltage_attr, Component.attributes)
            .filter(Component.type_id == lamp_type.id)
            .filter(voltage_attr.key == 'voltage')
        )

        if voltage is not None:
            query = query.filter(cast(voltage_attr.value, Float) == voltage)

        component = query.order_by(cast(voltage_attr.value, Float).asc()).first()

        if not component:
            return False, "❌ Signal Lamp not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        lamp = SignalLamp(
            name=component.name,
            brand=component.brand,
            model=component.model,
            voltage=attrs.get('voltage'),
            component_vendor=latest_vendor
        )

        return True, lamp

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Signal Lamp:\n{str(e)}"

    finally:
        session.close()
