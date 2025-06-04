from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased, joinedload

from models import Component,   ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal


class SignalLamp:
    def __init__(self, brand, model, voltage, component_supplier, order_number=""):
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.voltage = voltage
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<SignalLamp24V(voltage={self.voltage}V)>"


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
            return None, "❌ Signal Lamp not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        lamp = SignalLamp(
            brand=component.brand,
            model=component.model,
            voltage=attrs.get('voltage'),
            component_supplier=latest_supplier
        )

        return True, lamp

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Signal Lamp:\n{str(e)}"

    finally:
        session.close()
