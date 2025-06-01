from sqlalchemy import desc
from sqlalchemy.orm import aliased, joinedload

from models import ComponentType, ComponentAttribute, Component, ComponentSupplier
from utils.database import SessionLocal


class ContactorAuxContact:
    def __init__(self, name, brand, model, component_supplier, order_number=""):
        self.name = name
        self.brand = brand
        self.model = model
        self.order_number = order_number
        self.component_supplier = component_supplier

    def __repr__(self):
        return f"<ContactorAuxContact(name={self.name})>"


def get_contactor_aux_contact():
    session = SessionLocal()
    try:
        comp_type = session.query(ComponentType).filter_by(name='Contactor Auxiliary Contact').first()

        component = (
            session.query(Component)
            .filter(
                Component.type_id == comp_type.id,
            )
            .first()
        )
        if not component:
            return None, "❌ Contactor Auxiliary Contact not found."

        latest_supplier = (
            session.query(ComponentSupplier)
            .options(joinedload(ComponentSupplier.supplier))
            .filter(ComponentSupplier.component_id == component.id)
            .order_by(desc(ComponentSupplier.date))
            .first()
        )

        aux_contact = ContactorAuxContact(name=component.name,
                                          brand=component.brand,
                                          model=component.model,
                                          component_supplier=latest_supplier)

        return True, aux_contact

    except Exception as e:
        session.rollback()
        return False, f"❌ Failed in get ContactorAuxContact\n{str(e)}"

    finally:
        session.close()
