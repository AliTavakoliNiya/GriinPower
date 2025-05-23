from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from models import Base
from utils.database import SessionLocal
from views.message_box_view import show_message


class MCCB(Base):
    __tablename__ = 'mccb'

    mccb_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False, unique=True)
    rated_current = Column(Float, nullable=False)
    breaking_capacity = Column(Float, nullable=False)
    modified_by = Column(String, ForeignKey('users.username'), nullable=False)
    modified_at = Column(String, nullable=False)

    # Relationships
    item = relationship("Item", back_populates="mccb", uselist=False)
    modified_user = relationship("User", back_populates="mccbs_modified")

    def __repr__(self):
        return f"<MCCB(rated_current={self.rated_current}A, breaking_capacity={self.breaking_capacity}kA)>"


def get_mccb_by_motor_current(current_value):
    session = SessionLocal()
    try:
        mccb = (
            session.query(MCCB)
            .filter(MCCB.rated_current >= current_value)
            .order_by(MCCB.rated_current.asc())
            .first()
        )
        return mccb or MCCB()
    except Exception as e:
        session.rollback()
        show_message("mccb_model\n" + str(e) + "\n")
        return MCCB()
    finally:
        session.close()

# def get_mccbs_by_motor_current(current_value: float, limit: int = 5):
#     session = SessionLocal()
#     try:
#         mccbs = (
#             session.query(MCCB)
#             .filter(MCCB.rated_current >= current_value)
#             .order_by(MCCB.rated_current.asc())
#             .limit(limit)
#             .all()
#         )
#         return mccbs
#     except Exception as e:
#         session.rollback()
#         show_message("mccb_model\n" + str(e) + "\n")
#         return []
#     finally:
#         session.close()
