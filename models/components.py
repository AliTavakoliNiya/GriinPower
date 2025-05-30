import jdatetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from models.items import Base

today_shamsi = jdatetime.date.today().strftime("%Y/%m/%d %H:%M")


class Component(Base):
    __tablename__ = 'components'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type_id = Column(Integer, ForeignKey('component_types.id'))
    brand = Column(String)
    model = Column(String)
    created_at = Column(DateTime, default=today_shamsi)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    created_by = relationship('User')
    type = relationship('ComponentType', back_populates='components')
    attributes = relationship('ComponentAttribute', back_populates='component', cascade="all, delete-orphan")
    vendors = relationship('ComponentVendor', back_populates='component', cascade='all, delete-orphan')
