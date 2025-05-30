from sqlalchemy import cast, Float, desc, and_, func
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal


class MCB:

    def __init__(self, name, brand, model, rated_current, breaking_capacity, curve_type, poles, component_vendor):
        self.name = name
        self.brand = brand
        self.model = model
        self.rated_current = rated_current
        self.breaking_capacity = breaking_capacity
        self.curve_type = curve_type
        self.poles = poles
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<MCB(name={self.name}, current={self.rated_current}A, curve={self.curve_type})>"


def get_mcb_by_current(min_rated_current, curve_type=None, poles=None):
    session = SessionLocal()

    try:
        mcb_type = session.query(ComponentType).filter_by(name='MCB').first()
        if not mcb_type:
            return None, "ComponentType 'MCB' not found."

        rated_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(rated_attr, Component.attributes)
            .filter(
                Component.type_id == mcb_type.id,
                rated_attr.key == 'rated_current',
                cast(func.replace(rated_attr.value, 'A', ''), Float) >= min_rated_current
            )
        )

        if curve_type:
            query = query.filter(
                Component.attributes.any(
                    and_(
                        ComponentAttribute.key == 'curve_type',
                        ComponentAttribute.value == curve_type
                    )
                )
            )

        if poles:
            query = query.filter(
                Component.attributes.any(
                    and_(
                        ComponentAttribute.key == 'poles',
                        ComponentAttribute.value == str(poles)
                    )
                )
            )

        component = query.order_by(cast(rated_attr.value, Float).asc()).first()

        if not component:
            return None, "No MCB found matching the given criteria."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        mcb = MCB(
            name=component.name,
            brand=component.brand,
            model=component.model,
            rated_current=attrs.get("rated_current"),
            breaking_capacity=attrs.get("breaking_capacity"),
            curve_type=attrs.get("curve_type"),
            poles=attrs.get("poles"),
            component_vendor=latest_vendor
        )

        return mcb, f"{mcb}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_mcb_by_current:\n{str(e)}"

    finally:
        session.close()
