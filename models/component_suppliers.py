import jdatetime


from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from models import Base, Component
from utils.database import SessionLocal

today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")


class ComponentSupplier(Base):
    __tablename__ = 'component_supplier'
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('components.id'))
    supplier_id = Column(Integer, ForeignKey('supplier.id'))
    price = Column(Float)
    currency = Column(String, default='IRR')
    date = Column(String, default=today_shamsi)

    supplier = relationship('Supplier', back_populates='components', lazy="joined")
    component = relationship('Component', back_populates='suppliers', lazy="joined")


def insert_component_suppliers_to_db(component_id, supplier_id, price, currency):
    session = SessionLocal()
    try:
        component = session.get(Component, component_id)
        supplier_link = ComponentSupplier(
            supplier_id=supplier_id,
            component_id=component_id,
            price=price,
            currency=currency,
        )

        component.suppliers.append(supplier_link)

        session.commit()
        return True, None

    except Exception as e:
        session.rollback()
        return False, f"❌ Error saving supplier price: {str(e)}"

    finally:
        session.close()


