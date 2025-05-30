from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models.items import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class Contactor:

    def __init__(self, name, brand, model, rated_current, coil_voltage, power_cutting_kw, component_vendor):
        self.name = name
        self.brand = brand
        self.model = model
        self.rated_current = rated_current
        self.coil_voltage = coil_voltage
        self.power_cutting_kw = power_cutting_kw
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<Contactor(name={self.name} current_a={self.rated_current})>"


def get_contactor_by_current(rated_current, coil_voltage=None, power_cutting_kw=None):
    session = SessionLocal()

    try:

        contactor_type = session.query(ComponentType).filter_by(name='Contactor').first()
        rated_attr = aliased(ComponentAttribute)
        vendor_link = aliased(ComponentVendor)

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

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))  # load vendor in that query
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        contactor = Contactor(name=component.name,
                              brand=component.brand,
                              model=component.model,
                              rated_current=attrs.get("rated_current"),
                              coil_voltage=attrs.get("coil_voltage"),
                              power_cutting_kw=attrs.get("power_cutting_kw"),
                              component_vendor=latest_vendor
                              )
        return contactor, f"{contactor}"

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get contactor\n{str(e)}"

    finally:
        session.close()


