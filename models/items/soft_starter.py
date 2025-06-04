from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component,   ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal


class SoftStarter:

    def __init__(self, brand, model, rated_voltage, power_rating_kw, component_supplier, order_number):
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.rated_voltage = rated_voltage
        self.power_rating_kw = power_rating_kw
        self.component_supplier = component_supplier

    def __repr__(self):
        return (f"<SoftStarter(voltage={self.rated_voltage}V, "
                f"power={self.power_rating_kw}kW)>")


def get_softstarter_by_power(min_power_kw):
    session = SessionLocal()

    try:
        softstarter_type = session.query(ComponentType).filter_by(name='SoftStarter').first()
        if not softstarter_type:
            return None, "ComponentType 'SoftStarter' not found."

        power_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(power_attr, Component.attributes)
            .filter(
                Component.type_id == softstarter_type.id,
                power_attr.key == 'power_rating_kw',
                cast(power_attr.value, Float) >= min_power_kw
            )
        )


        component = query.order_by(cast(power_attr.value, Float).asc()).first()

        if not component:
            return None, "No SoftStarter found matching criteria."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        softstarter = SoftStarter(
            brand=component.brand,
            model=component.model,
            order_number=component.order_number,
            rated_voltage=attrs.get("rated_voltage"),
            power_rating_kw=attrs.get("power_rating_kw"),
            component_supplier=latest_supplier
        )

        return softstarter, f"{softstarter}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_softstarter_by_power_and_current:\n{str(e)}"

    finally:
        session.close()
