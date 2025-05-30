from sqlalchemy import cast, Float, desc
from sqlalchemy.orm import aliased, joinedload
from models import Component, ComponentType, ComponentAttribute, ComponentVendor
from utils.database import SessionLocal

class ElectricalPanel:
    def __init__(self, name, brand, model, width, height, depth, ip, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.width = width
        self.height = height
        self.depth = depth
        self.ip = ip
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<ElectricalPanel(name={self.name}, size={self.width}x{self.height}x{self.depth}, ip={self.ip})>"

def get_electrical_panel(width=None, height=None, depth=None, ip=None):
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
            .filter(ip_attr.key == "ip")
        )

        if width is not None:
            query = query.filter(cast(width_attr.value, Float) >= width)
        if height is not None:
            query = query.filter(cast(height_attr.value, Float) >= height)
        if depth is not None:
            query = query.filter(cast(depth_attr.value, Float) >= depth)
        if ip is not None:
            query = query.filter(ip_attr.value == str(ip))

        component = query.order_by(
            cast(width_attr.value, Float).asc(),
            cast(height_attr.value, Float).asc(),
            cast(depth_attr.value, Float).asc()
        ).first()

        if not component:
            return False, "❌ Electrical Panel not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        panel = ElectricalPanel(
            name=component.name,
            brand=component.brand,
            model=component.model,
            width=attrs.get("width"),
            height=attrs.get("height"),
            depth=attrs.get("depth"),
            ip=attrs.get("ip"),
            component_vendor=latest_vendor
        )

        return True, panel

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_electrical_panel:\n{str(e)}"

    finally:
        session.close()
