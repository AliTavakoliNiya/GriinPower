from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models import Base


class Item(Base):
    __tablename__ = 'items'

    item_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=False)

    contactor = relationship("Contactor", back_populates="item", uselist=False)
    mpcb = relationship("MPCB", back_populates="item", uselist=False)
    mccb = relationship("MCCB", back_populates="item", uselist=False)
    general = relationship("General", back_populates="item", uselist=False)
    electric_motor = relationship("ElectricMotor", back_populates="item", uselist=False)
    instrument = relationship("Instrument", back_populates="item", uselist=False)
    plc = relationship("PLC", back_populates="item", uselist=False)
    prices = relationship("ItemPrice", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Item(item_id={self.item_id}, name='{self.name}')>"
