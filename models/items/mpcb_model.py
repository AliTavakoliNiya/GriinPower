from sqlalchemy import cast, Float, desc, and_, func
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models.items import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal



class MPCB:

    def __init__(self, name, brand, model, rated_current, breaking_capacity_ka, adjustment_range, poles, component_vendor):
        self.name = name
        self.brand = brand
        self.model = model
        self.rated_current = rated_current
        self.breaking_capacity_ka = breaking_capacity_ka
        self.adjustment_range = adjustment_range
        self.poles = poles
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<MPCB(name={self.name}, current={self.rated_current}A, adjustment_range={self.adjustment_range})>"

def get_mpcb_by_current(min_rated_current, min_breaking_capacity_ka=None, poles=None):
    session = SessionLocal()

    try:
        mpcb_type = session.query(ComponentType).filter_by(name='MPCB').first()
        if not mpcb_type:
            return None, "ComponentType 'MPCB' not found."

        rated_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(rated_attr, Component.attributes)
            .filter(
                Component.type_id == mpcb_type.id,
                rated_attr.key == 'rated_current',
                cast(func.replace(rated_attr.value, 'A', ''), Float) >= min_rated_current
            )
        )

        if min_breaking_capacity_ka:
            query = query.filter(
                Component.attributes.any(
                    and_(
                        ComponentAttribute.key == 'breaking_capacity_ka',
                        cast(func.replace(ComponentAttribute.value, 'kA', ''), Float) >= min_breaking_capacity_ka
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
            return None, f"No MPCB found with rated_current >= {min_rated_current} A."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}

        mpcb = MPCB(
            name=component.name,
            brand=component.brand,
            model=component.model,
            rated_current=attrs.get("rated_current"),
            breaking_capacity_ka=attrs.get("breaking_capacity_ka"),
            adjustment_range=attrs.get("adjustment_range"),
            poles=attrs.get("poles"),
            component_vendor=latest_vendor
        )

        return mpcb, f"{mpcb}"

    except Exception as e:
        session.rollback()
        return None, f"❌ Failed in get_mpcb_by_current:\n{str(e)}"

    finally:
        session.close()
