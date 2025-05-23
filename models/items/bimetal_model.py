from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from models import Base
from utils.database import SessionLocal
from views.message_box_view import show_message


class Bimetal(Base):
    __tablename__ = 'bimetal'

    bimetal_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False, unique=True)

    current_setting_min = Column(Float, nullable=False)
    current_setting_max = Column(Float, nullable=False)
    trip_time = Column(Float, nullable=False)

    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=False)
    modified_at = Column(String, nullable=False)

    # Relationships
    item = relationship("Item", back_populates="bimetal", uselist=False)
    modified_user = relationship("User", back_populates="bimetals_modified")

    def __repr__(self):
        return (f"<Bimetal(current_setting_min={self.current_setting_min}, "
                f"current_setting_max={self.current_setting_max}, trip_time={self.trip_time})>")



def get_bimetal_by_motor_current(current_value: float):
    session = SessionLocal()
    try:
        bimetal = (
            session.query(Bimetal)
            .filter(Bimetal.current_setting_min <= current_value,
                    Bimetal.current_setting_max >= current_value)
            .order_by(Bimetal.current_setting_max.asc())
            .first()
        )
        return bimetal or Bimetal()
    except Exception as e:
        session.rollback()
        show_message("bimetal_model\n" + str(e) + "\n")
        return Bimetal()
    finally:
        session.close()

