from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from models import Base
from utils.database import SessionLocal


class Supplier(Base):
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    contact_info = Column(Text, nullable=True)
    website = Column(String, nullable=True)

    components = relationship('ComponentSupplier', back_populates='supplier', lazy="joined")

def get_all_suppliers():
    pass

def get_supplier_by_name(name):
    session = SessionLocal()
    try:
        supplier = session.query(Supplier).filter_by(name=name).first()
        return True, supplier.id
    except Exception as e:
        session.rollback()
        return False, f"❌ Error in get supplier: {str(e)}"
    finally:
        session.close()


def save_supplier_to_db():
    pass
