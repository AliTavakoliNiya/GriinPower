from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentVendor, ComponentAttribute
from utils.database import SessionLocal


class IOCard:
    def __init__(self, name, io_type, brand, model, channels, component_vendor, order_number=""):
        self.name = name
        self.io_type = io_type  # DI, DO, AI, AO
        self.brand = brand
        self.model = model
        self.channels = channels
        self.component_vendor = component_vendor
        self.order_number = order_number

    def __repr__(self):
        return f"<IOCard(name={self.name}, type={self.io_type}, channels={self.channels})>"


def get_io_card(io_type: str, min_channels: int = 0):
    """
    Fetches an IO card of type `io_type` (e.g., 'DI', 'DO', 'AI', 'AO') with at least `min_channels`.
    """
    session = SessionLocal()
    try:
        io_type_obj = session.query(ComponentType).filter_by(name='IOCard').first()
        if not io_type_obj:
            return False, "❌ IOCard component type not found."

        components = (
            session.query(Component)
            .filter(Component.type_id == io_type_obj.id)
            .join(Component.attributes)
            .filter(ComponentAttribute.key == "io_type", ComponentAttribute.value == io_type.upper())
            .all()
        )

        selected_component = None
        for comp in components:
            attrs = {attr.key: attr.value for attr in comp.attributes}
            channels = int(attrs.get("channels", 0))
            if channels >= min_channels:
                if not selected_component or channels < int(selected_component[1].get("channels", 999)):
                    selected_component = (comp, attrs)

        if not selected_component:
            return None, f"❌ No matching IOCard found for type={io_type} and min_channels={min_channels}"

        component, attrs = selected_component
        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        card = IOCard(
            name=component.name,
            io_type=attrs.get("io_type"),
            brand=component.brand,
            model=component.model,
            channels=int(attrs.get("channels", 0)),
            component_vendor=latest_vendor
        )

        return True, card

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_io_card: {str(e)}"

    finally:
        session.close()
