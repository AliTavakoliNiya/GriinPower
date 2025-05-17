from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from models import Base
from utils.database import SessionLocal
from views.message_box_view import show_message


class ElectricMotor(Base):
    __tablename__ = 'electric_motor'

    motor_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False, unique=True)

    power = Column(Float, nullable=False)
    rpm = Column(Integer, nullable=False)
    starting_method = Column(String, nullable=False)
    cooling_method = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    efficiency_class = Column(String, nullable=False)
    voltage = Column(Integer, nullable=False)
    painting_ral = Column(String, nullable=False)
    thermal_protection = Column(String, nullable=False)
    space_heater = Column(Boolean, nullable=False)

    # Relationship to the item
    item = relationship("Item", back_populates="electric_motor", uselist=False)

    def __repr__(self):
        return f"<ElectricMotor(power={self.power}, rpm={self.rpm}')>"


def get_electric_motor_by_specs(*, power, rpm, starting_method, cooling_method, ip, efficiency_class,
                                voltage, painting_ral, thermal_protection, space_heater):
    session = SessionLocal()
    try:
        return session.query(ElectricMotor).filter_by(
            power=power,
            rpm=rpm,
            starting_method=starting_method,
            cooling_method=cooling_method,
            ip=ip,
            efficiency_class=efficiency_class,
            voltage=voltage,
            painting_ral=painting_ral,
            thermal_protection=thermal_protection,
            space_heater=space_heater
        ).first() or ElectricMotor()
    except Exception as e:
        session.rollback()
        show_message("electric_motor_model\n" + str(e) + "\n")
        return ElectricMotor()
    finally:
        session.close()
