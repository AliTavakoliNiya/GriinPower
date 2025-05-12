from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models import Base

class ElectricMotor(Base):
    __tablename__ = 'electric_motor'

    motor_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False, unique=True)

    power = Column(Float, nullable=False)
    rpm = Column(Integer, nullable=False)
    brand = Column(String, nullable=False)
    cooling_method = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    efficiency_class = Column(String, nullable=False)
    voltage_type = Column(Integer, nullable=False)
    thermal_protection = Column(String, nullable=False)
    space_heater = Column(Boolean, nullable=False)

    # Relationship to the item
    item = relationship("Item", back_populates="electric_motor", uselist=False)

    def __repr__(self):
        return f"<ElectricMotor(power={self.power}, rpm={self.rpm}, brand='{self.brand}')>"
