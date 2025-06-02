import jdatetime

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models import Base

today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")


class Component(Base):
    __tablename__ = 'components'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type_id = Column(Integer, ForeignKey('component_types.id'))
    brand = Column(String)
    model = Column(String, default="")
    order_number = Column(String, default="")
    created_at = Column(String, default=today_shamsi)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    created_by = relationship('User')
    type = relationship('ComponentType', back_populates='components', lazy="joined")
    attributes = relationship('ComponentAttribute', back_populates='component', cascade="all, delete-orphan", lazy="joined")
    suppliers = relationship('ComponentSupplier', back_populates='component', cascade='all, delete-orphan', lazy="joined")
