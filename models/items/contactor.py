from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal


class Contactor:

    def __init__(self, name, brand, model, rated_current, coil_voltage, power_cutting_kw, component_supplier, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.rated_current = rated_current
        self.coil_voltage = coil_voltage
        self.power_cutting_kw = power_cutting_kw
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<Contactor(name={self.name} current_a={self.rated_current})>"


def get_contactor_by_current(rated_current):
    session = SessionLocal()

    try:

        contactor_type = session.query(ComponentType).filter_by(name='Contactor').first()
        rated_attr = aliased(ComponentAttribute)

        component = (
            session.query(Component)
            .join(rated_attr, Component.attributes)
            .filter(
                Component.type_id == contactor_type.id,
                rated_attr.key == 'rated_current',
                cast(rated_attr.value, Float) > rated_current
            )
            .order_by(cast(rated_attr.value, Float).asc())
            .first()
        )

        if not component:
            return None, "❌ Contactor not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))  # load supplier in that query
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        contactor = Contactor(name=component.name,
                              brand=component.brand,
                              model=component.model,
                              rated_current=attrs.get("rated_current"),
                              coil_voltage=attrs.get("coil_voltage"),
                              power_cutting_kw=attrs.get("power_cutting_kw"),
                              component_supplier=latest_supplier
                              )
        return True, contactor

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get contactor\n{str(e)}"

    finally:
        session.close()

def insert_contactor(contactor):
    pass
