from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentType, ComponentVendor
from utils.database import SessionLocal


class DuctCover:
    def __init__(self, name, brand, model, component_vendor, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.component_vendor = component_vendor

    def __repr__(self):
        return f"<DuctCover(name={self.name})>"


def get_duct_cover():
    session = SessionLocal()
    try:
        duct_cover_type = session.query(ComponentType).filter_by(name='DuctCover').first()

        component = (
            session.query(Component)
            .filter(
                Component.type_id == duct_cover_type.id,
            )
            .first()
        )

        if not component:
            return None, "❌ Duct Cover not found."

        latest_vendor = (
            session.query(ComponentVendor)
            .options(joinedload(ComponentVendor.vendor))
            .filter(ComponentVendor.component_id == component.id)
            .order_by(desc(ComponentVendor.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        duct_cover = DuctCover(
            name=component.name,
            brand=component.brand,
            model=component.model,
            component_vendor=latest_vendor
        )

        return True, duct_cover

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Duct Cover:\n{str(e)}"

    finally:
        session.close()
