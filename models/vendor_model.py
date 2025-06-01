from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import Base
from utils.database import SessionLocal
from views.message_box_view import show_message


class Supplier(Base):
    __tablename__ = 'suppliers'

    supplier_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    phone1 = Column(String, nullable=True)
    phone2 = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)

    def __repr__(self):
        return f"<Supplier(id={self.supplier_id}, name='{self.name}')>"


def get_all_suppliers():

    session = SessionLocal()
    try:
        supplier = session.query(Supplier).all()
        return supplier or []
    except Exception as e:
        session.rollback()
        show_message(f"supplier_model\n{str(e)}\n")
        return []
    finally:
        session.close()


def save_supplier_to_db(supplier: Supplier):
    """
    Insert or update a supplier in the database based on normalized name.
    """
    session: Session = SessionLocal()

    try:
        # Query existing supplier in the current session
        existing_supplier = session.query(Supplier).filter(Supplier.name == supplier.name).first()

        if existing_supplier:
            # Update fields of the existing supplier
            existing_supplier.contact_person = supplier.contact_person
            existing_supplier.phone1 = supplier.phone1
            existing_supplier.phone2 = supplier.phone2
            existing_supplier.email = supplier.email
            existing_supplier.address = supplier.address

            session.commit()
            return True

        # No existing supplier found: insert new supplier
        session.add(supplier)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        show_message(f"Database error while saving supplier:\n{str(e)}", "Error")
        return False

    finally:
        session.close()
