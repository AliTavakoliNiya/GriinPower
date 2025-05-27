from sqlalchemy import Column, Integer, String
from models import Base
from sqlalchemy.orm import Session
from utils.database import SessionLocal
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
    session: Session = SessionLocal()
    try:
        return session.query(Vendor).all()
    finally:
        session.close()

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

