from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from models.items import Base

class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    contact_info = Column(Text, nullable=True)
    website = Column(String, nullable=True)

    components = relationship('ComponentVendor', back_populates='vendor')
