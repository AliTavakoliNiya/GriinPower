from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.items import Base


class ComponentAttribute(Base):
    __tablename__ = 'component_attributes'
    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('components.id'))
    key = Column(String)
    value = Column(String)

    component = relationship('Component', back_populates='attributes')
