from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import SessionLocal
from views.message_box_view import show_message
from models import Base

class Bimetal(Base):
    __tablename__ = 'bimetal'

    bimetal_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False)
    bimetal_reference = Column(String, nullable=False, unique=True)
    min_current_range_a = Column(Float, nullable=False)
    max_current_range_a = Column(Float, nullable=False)
    trip_class = Column(String, nullable=True)  # Optional: trip class like 10A, 10, 20

    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=True)
    modified_at = Column(String, nullable=False)

    item = relationship("Item", back_populates="bimetal", uselist=False)
    modified_user = relationship("User", back_populates="bimetals_modified")

    def __repr__(self):
        return (
            f"Bimetal Reference={self.bimetal_reference}, "
            f"Minimum Current(A)={self.min_current_range_a}, "
            f"Maximum Current(A)={self.max_current_range_a}, "
            f"Trip Class={self.trip_class}, "
        )


def get_bimetal_by_current_range(min_current):
    session = SessionLocal()
    try:
        return session.query(Bimetal).filter(Bimetal.min_current_range_a >= min_current).order_by(Bimetal.min_current_range_a.asc()).first() or Bimetal()
    except Exception as e:
        session.rollback()
        show_message(f"bimetal_mode\n{str(e)}\n", "Error")
        return Bimetal()
    finally:
        session.close()
