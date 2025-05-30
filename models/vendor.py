from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from models import Base

class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    contact_info = Column(Text, nullable=True)
    website = Column(String, nullable=True)

    components = relationship('ComponentVendor', back_populates='vendor')

def get_all_vendors():
    pass

def save_vendor_to_db():
    pass
