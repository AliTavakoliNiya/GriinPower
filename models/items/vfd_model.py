from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class VFD:

    def __init__(self, name, brand, model, output_power_kw, input_voltage, component_vendor):
        self.name = name
        self.brand = brand
        self.model = model
        self.output_power_kw = output_power_kw
        self.input_voltage = input_voltage
        self.component_vendor = component_vendor

    def __repr__(self):
        return (f"<VFD(name={self.name}, power={self.output_power_kw}kW, voltage={self.input_voltage}V)>")


def get_vfd_by_power(min_power_kw):
    session = SessionLocal()

    try:
        vfd_type = session.query(ComponentType).filter_by(name='VFD').first()
        if not vfd_type:
            return None, "ComponentType 'VFD' not found."

        power_attr = aliased(ComponentAttribute)

        component = (
            session.query(Component)
            .join(power_attr, Component.attributes)
            .filter(
                Component.type_id == vfd_type.id,
                power_attr.key == 'output_power_kw',
                cast(power_attr.value, Float) >= min_power_kw
            )
            .order_by(cast(power_attr.value, Float).asc())
            .first()
        )

        if not component:
            return None, "No VFD found with sufficient output power."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        vfd = VFD(
            name=component.name,
            brand=component.brand,
            model=component.model,
            output_power_kw=attrs.get("output_power_kw"),
            input_voltage=attrs.get("input_voltage"),
            rated_current=attrs.get("rated_current"),
            component_vendor=latest_vendor
        )

        return vfd, f"{vfd}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_vfd_by_power:\n{str(e)}"

    finally:
        session.close()
