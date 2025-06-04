from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal

class LCB:
    def __init__(self, brand, model, width, height, depth, component_supplier, order_number=""):
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.width = width
        self.height = height
        self.depth = depth
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<LCB(size={self.width}x{self.height}x{self.depth})>"

def get_lcb(width=None, height=None, depth=None):
    session = SessionLocal()
    try:
        lcb_type = session.query(ComponentType).filter_by(name='LCB').first()

        width_attr = aliased(ComponentAttribute)
        height_attr = aliased(ComponentAttribute)
        depth_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(width_attr, Component.attributes)
            .join(height_attr, Component.attributes)
            .join(depth_attr, Component.attributes)
            .filter(Component.type_id == lcb_type.id)
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
            return None, "❌ LCB not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        lcb = LCB(
            brand=component.brand,
            model=component.model,
            width=attrs.get("width"),
            height=attrs.get("height"),
            depth=attrs.get("depth"),
            component_supplier=latest_supplier
        )

        return True, lcb

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get LCB:\n{str(e)}"

    finally:
        session.close()


