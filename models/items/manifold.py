from sqlalchemy import cast, Integer, desc
from sqlalchemy.orm import joinedload

from models import Component, ComponentAttribute, ComponentSupplier
from utils.database import SessionLocal


class Manifold:
    def __init__(self, brand, model, ways, component_supplier, order_number=""):
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.ways = ways
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<Manifold(ways={self.ways})>"


def get_manifold(ways=None):
    session = SessionLocal()
    try:
        # Subquery to find ComponentAttribute with key='ways'
        ways_subquery = (
            session.query(ComponentAttribute.component_id, cast(ComponentAttribute.value, Integer).label("ways"))
            .filter(ComponentAttribute.key == "ways")
            .subquery()
        )

        # Join with Component and filter by type and optional 'ways' value
        query = (
            session.query(Component)
            .join(ways_subquery, Component.id == ways_subquery.c.component_id)
            .filter(Component.type == "Manifold")
            .options(
                joinedload(Component.attributes),
                joinedload(Component.suppliers).joinedload(ComponentSupplier.supplier)
            )
        )

        if ways is not None:
            query = query.filter(ways_subquery.c.ways >= ways)

        component = query.order_by(ways_subquery.c.ways.asc()).first()

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
            brand=component.brand,
            model=component.model,
            ways=attrs.get("ways"),
            component_supplier=latest_supplier
        )

        return True, manifold

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get_manifold:\n{str(e)}"

    finally:
        session.close()
