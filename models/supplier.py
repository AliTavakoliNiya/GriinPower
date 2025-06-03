from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from models import Base
from sqlalchemy.exc import SQLAlchemyError
from utils.database import SessionLocal


class Supplier(Base):
    __tablename__ = 'supplier'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    contact_person = Column(Text, nullable=True)
    phone1 = Column(Text, nullable=True)
    phone2 = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    address = Column(Text, nullable=True)

    components = relationship('ComponentSupplier', back_populates='supplier', lazy="joined")




def get_all_suppliers():
    session = SessionLocal()
    try:
        all_suppliers = session.query(Supplier).all()
        return True, all_suppliers
    except Exception as e:
        session.rollback()
        return False, f"❌ Error in get supplier: {str(e)}"
    finally:
        session.close()


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


def save_supplier_to_db(supplier: Supplier) -> bool:
    """
    Save a Supplier object to the database.

    Returns:
        True if successful, False otherwise.
    """
    session = SessionLocal()
    try:
        session.add(supplier)  # Add supplier to the session
        session.commit()  # Commit the transaction
        return True
    except SQLAlchemyError as e:
        session.rollback()  # Rollback in case of error
        print(f"Error saving supplier: {e}")  # Log the error
        return False
    finally:
        session.close()  # Ensure the session is closed

