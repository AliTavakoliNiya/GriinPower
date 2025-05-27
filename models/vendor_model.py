from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import Base
from utils.database import SessionLocal
from views.message_box_view import show_message


class Vendor(Base):
    __tablename__ = 'vendors'

    vendor_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    phone1 = Column(String, nullable=True)
    phone2 = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)

    def __repr__(self):
        return f"<Vendor(id={self.vendor_id}, name='{self.name}')>"


def get_all_vendors():

    session = SessionLocal()
    try:
        vendor = session.query(Vendor).all()
        return vendor or []
    except Exception as e:
        session.rollback()
        show_message(f"vendor_model\n{str(e)}\n")
        return []
    finally:
        session.close()


def save_vendor_to_db(vendor: Vendor):
    """
    Insert or update a vendor in the database based on normalized name.
    """
    session: Session = SessionLocal()

    try:
        # Query existing vendor in the current session
        existing_vendor = session.query(Vendor).filter(Vendor.name == vendor.name).first()

        if existing_vendor:
            # Update fields of the existing vendor
            existing_vendor.contact_person = vendor.contact_person
            existing_vendor.phone1 = vendor.phone1
            existing_vendor.phone2 = vendor.phone2
            existing_vendor.email = vendor.email
            existing_vendor.address = vendor.address

            session.commit()
            return True

        # No existing vendor found: insert new vendor
        session.add(vendor)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        show_message(f"Database error while saving vendor:\n{str(e)}", "Error")
        return False

    finally:
        session.close()
