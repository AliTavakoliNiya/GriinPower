from sqlalchemy import cast, Float, desc, and_
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class SoftStarter:

    def __init__(self, name, brand, model, rated_voltage, rated_current,
                 starting_current_limit, power_rating_kw, component_vendor):
        self.name = name
        self.brand = brand
        self.model = model
        self.rated_voltage = rated_voltage
        self.rated_current = rated_current
        self.starting_current_limit = starting_current_limit
        self.power_rating_kw = power_rating_kw
        self.component_vendor = component_vendor

    def __repr__(self):
        return (f"<SoftStarter(name={self.name}, voltage={self.rated_voltage}V, "
                f"current={self.rated_current}A, power={self.power_rating_kw}kW)>")


def get_softstarter_by_power_and_current(min_power_kw, max_starting_current=None):
    session = SessionLocal()

    try:
        softstarter_type = session.query(ComponentType).filter_by(name='SoftStarter').first()
        if not softstarter_type:
            return None, "ComponentType 'SoftStarter' not found."

        power_attr = aliased(ComponentAttribute)
        current_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(power_attr, Component.attributes)
            .filter(
                Component.type_id == softstarter_type.id,
                power_attr.key == 'power_rating_kw',
                cast(power_attr.value, Float) >= min_power_kw
            )
        )

        if max_starting_current is not None:
            query = query.join(current_attr, Component.attributes).filter(
                and_(
                    current_attr.key == 'starting_current_limit',
                    cast(current_attr.value, Float) <= max_starting_current
                )
            )

        component = query.order_by(cast(power_attr.value, Float).asc()).first()

        if not component:
            return None, "No SoftStarter found matching criteria."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        softstarter = SoftStarter(
            name=component.name,
            brand=component.brand,
            model=component.model,
            rated_voltage=attrs.get("rated_voltage"),
            rated_current=attrs.get("rated_current"),
            starting_current_limit=attrs.get("starting_current_limit"),
            power_rating_kw=attrs.get("power_rating_kw"),
            component_vendor=latest_vendor
        )

        return softstarter, f"{softstarter}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_softstarter_by_power_and_current:\n{str(e)}"

    finally:
        session.close()
