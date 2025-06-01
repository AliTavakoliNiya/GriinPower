from sqlalchemy import cast, Integer, desc
from sqlalchemy.orm import aliased, joinedload

from models import Component, ComponentType, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal


class Manifold:
    def __init__(self, name, brand, model, ways, component_supplier, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.ways = ways
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<Manifold(name={self.name} ways={self.ways})>"


def get_manifold(ways=None):
    session = SessionLocal()
    try:
        manifold_type = session.query(ComponentType).filter_by(name='Manifold').first()

        ways_attr = aliased(ComponentAttribute)

        query = (
            session.query(Component)
            .join(ways_attr, Component.attributes)
            .filter(Component.type_id == manifold_type.id)
            .filter(ways_attr.key == 'ways')
        )

        if ways is not None:
            query = query.filter(cast(ways_attr.value, Integer) >= ways)

        component = query.order_by(cast(ways_attr.value, Integer).asc()).first()

        if not component:
            return None, "❌ Manifold not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        attrs = {attr.key: attr.value for attr in component.attributes}
        manifold = Manifold(
            name=component.name,
            brand=component.brand,
            model=component.model,
            ways=attrs.get('ways'),
            component_supplier=latest_supplier
        )

        return True, manifold

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get Manifold:\n{str(e)}"

    finally:
        session.close()
