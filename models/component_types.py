
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.items import Base


class ComponentType(Base):
    __tablename__ = 'component_types'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    components = relationship('Component', back_populates='type')
    created_by = relationship('User')