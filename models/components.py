from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models import Base


class Component(Base):
    __tablename__ = 'components'
    id = Column(Integer, primary_key=True)
    type = Column(String)

    attributes = relationship('ComponentAttribute', back_populates='component', cascade="all, delete-orphan", lazy="joined")
    suppliers = relationship('ComponentSupplier', back_populates='component', cascade='all, delete-orphan', lazy="joined")
