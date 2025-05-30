import jdatetime


from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship

from models.items import Base

today_shamsi = jdatetime.date.today().strftime("%Y/%m/%d %H:%M")


class ComponentVendor(Base):
    __tablename__ = 'component_vendors'
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('components.id'))
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    price = Column(Float)
    currency = Column(String, default='IRR')
    date = Column(Date, default=today_shamsi)

    vendor = relationship('Vendor', back_populates='components')
    component = relationship('Component', back_populates='vendors')
