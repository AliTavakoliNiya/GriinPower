from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal


class JunctionBox:
    def __init__(self, name, brand, model, width, height, depth, component_supplier, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.width=width,
        self.height=height,
        self.depth=depth,
        self.order_number = order_number
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<JunctionBox(name={self.name})>"


def get_junction_box(width=None, height=None, depth=None):
    session = SessionLocal()
    try:
        jb_type = session.query(ComponentType).filter_by(name='JunctionBoxForSpeed').first()

        width_attr = aliased(ComponentAttribute)
        height_attr = aliased(ComponentAttribute)
        depth_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(width_attr, Component.attributes)
            .join(height_attr, Component.attributes)
            .join(depth_attr, Component.attributes)
            .filter(Component.type_id == jb_type.id)
            .filter(width_attr.key == "width")
            .filter(height_attr.key == "height")
            .filter(depth_attr.key == "depth")
        )

        if width is not None:
            query = query.filter(cast(width_attr.value, Float) >= width)
        if height is not None:
            query = query.filter(cast(height_attr.value, Float) >= height)
        if depth is not None:
            query = query.filter(cast(depth_attr.value, Float) >= depth)

        component = query.order_by(
            cast(width_attr.value, Float).asc(),
            cast(height_attr.value, Float).asc(),
            cast(depth_attr.value, Float).asc()
        ).first()

        if not component:
            return None, "❌ Junction Box for Speed not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        junction_box = JunctionBox(
            name=component.name,
            brand=component.brand,
            model=component.model,
            component_supplier=latest_supplier
        )

        return True, junction_box

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Junction Box for Speed:\n{str(e)}"

    finally:
        session.close()
