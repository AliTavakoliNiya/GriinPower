from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from models import Base
from utils.database import SessionLocal
from views.message_box_view import show_message


class MPCB(Base):
    __tablename__ = 'mpcb'

    mpcb_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False, unique=True)

    min_current = Column(Float, nullable=False)
    max_current = Column(Float, nullable=False)
    breaking_capacity = Column(Float, nullable=False)
    trip_class = Column(Integer, nullable=False)

    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=False)
    modified_at = Column(String, nullable=False)

    # Relationships
    item = relationship("Item", back_populates="mpcb", uselist=False)
    modified_user = relationship("User", back_populates="mpcbs_modified")

    def __repr__(self):
        return (f"<MPCB(min_current={self.min_current}, max_current={self.max_current}, "
                f"trip_class={self.trip_class}, breaking_capacity={self.breaking_capacity})>")


def get_mpcb_by_motor_current(current_value: float):
    session = SessionLocal()
    try:
        mpcb = (
            session.query(MPCB)
            .filter(MPCB.min_current <= current_value, MPCB.max_current >= current_value)
            .order_by(MPCB.max_current.asc())
            .first()
        )
        return mpcb or MPCB()
    except Exception as e:
        session.rollback()
        show_message("mpcb_model\n" + str(e) + "\n")
        return MPCB()
    finally:
        session.close()

