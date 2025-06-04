from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased, joinedload
from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal

class ElectricalPanel:
    def __init__(self, brand, model, width, height, depth, ip_rating, component_supplier, order_number=""):
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.width = width
        self.height = height
        self.depth = depth
        self.ip_rating = ip_rating
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<ElectricalPanel(size={self.width}x{self.height}x{self.depth}, ip_rating={self.ip_rating})>"

def get_electrical_panel(width=None, height=None, depth=None, ip_rating=None):
    session = SessionLocal()
    try:
        panel_type = session.query(ComponentType).filter_by(name="Electrical Panel").first()

        width_attr = aliased(ComponentAttribute)
        height_attr = aliased(ComponentAttribute)
        depth_attr = aliased(ComponentAttribute)
        ip_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(width_attr, Component.attributes)
            .join(height_attr, Component.attributes)
            .join(depth_attr, Component.attributes)
            .join(ip_attr, Component.attributes)
            .filter(Component.type_id == panel_type.id)
            .filter(width_attr.key == "width")
            .filter(height_attr.key == "height")
            .filter(depth_attr.key == "depth")
            .filter(ip_attr.key == "ip_rating")
        )

        if width is not None:
            query = query.filter(cast(width_attr.value, Float) >= width)
        if height is not None:
            query = query.filter(cast(height_attr.value, Float) >= height)
        if depth is not None:
            query = query.filter(cast(depth_attr.value, Float) >= depth)
        if ip_rating is not None:
            query = query.filter(ip_attr.value == str(ip_rating))

        component = query.order_by(
            cast(width_attr.value, Float).asc(),
            cast(height_attr.value, Float).asc(),
            cast(depth_attr.value, Float).asc()
        ).first()

        if not component:
            return None, "❌ Electrical Panel not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        panel = ElectricalPanel(
            brand=component.brand,
            model=component.model,
            width=attrs.get("width"),
            height=attrs.get("height"),
            depth=attrs.get("depth"),
            ip_rating=attrs.get("ip_rating"),
            component_supplier=latest_supplier
        )

        return True, panel

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_electrical_panel:\n{str(e)}"

    finally:
        session.close()
